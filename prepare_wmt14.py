"""Build cleaned TRAIN / VALIDATE / TEST CSV files from WMT14 English-German.

Source: Hugging Face dataset wmt/wmt14 (config de-en), which holds the same data
as the Kaggle dataset mohamedlotfy50/wmt-2014-english-german.

Output (in ./processed): train.csv, validation.csv, test.csv with columns en, de.
"""

import re
import unicodedata
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "processed"

REPO = "wmt/wmt14"
TRAIN_FILES = [f"de-en/train-0000{i}-of-00003.parquet" for i in range(3)]
VAL_FILE = "de-en/validation-00000-of-00001.parquet"
TEST_FILE = "de-en/test-00000-of-00001.parquet"

TRAIN_SAMPLE = 100_000
SEED = 42
MIN_WORDS, MAX_WORDS = 1, 100
MAX_LEN_RATIO = 2.5

_ws = re.compile(r"\s+")


def download(filename: str) -> Path:
    return Path(hf_hub_download(REPO, filename, repo_type="dataset", local_dir=RAW_DIR))


def load(path: Path) -> pd.DataFrame:
    table = pq.read_table(path).flatten()  # struct column -> translation.de / translation.en
    df = table.to_pandas()
    return pd.DataFrame({"en": df["translation.en"], "de": df["translation.de"]})


def normalize(s: pd.Series) -> pd.Series:
    return s.fillna("").map(lambda t: _ws.sub(" ", unicodedata.normalize("NFC", t)).strip())


def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Light cleaning used for every split."""
    df = df.assign(en=normalize(df["en"]), de=normalize(df["de"]))
    df = df[(df["en"] != "") & (df["de"] != "")]
    return df.drop_duplicates(subset=["en", "de"])


def train_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Extra filters for the noisy training data."""
    df = df[df["en"] != df["de"]]  # untranslated copies
    en_len = df["en"].str.split().str.len()
    de_len = df["de"].str.split().str.len()
    keep = en_len.between(MIN_WORDS, MAX_WORDS) & de_len.between(MIN_WORDS, MAX_WORDS)
    ratio = en_len.clip(lower=1) / de_len.clip(lower=1)
    keep &= ratio.between(1 / MAX_LEN_RATIO, MAX_LEN_RATIO)
    df = df[keep]
    # drop lines with no letters at all (numbers / symbols only)
    letters = df["en"].str.contains(r"[A-Za-z]") & df["de"].str.contains(r"[A-Za-zÄÖÜäöüß]")
    return df[letters]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stats = []

    val = load(download(VAL_FILE))
    test = load(download(TEST_FILE))
    stats += [("validation raw", len(val)), ("test raw", len(test))]
    val, test = basic_clean(val), basic_clean(test)
    stats += [("validation cleaned", len(val)), ("test cleaned", len(test))]
    held_out_en = set(val["en"]) | set(test["en"])

    parts, raw_total = [], 0
    for f in TRAIN_FILES:
        df = load(download(f))
        raw_total += len(df)
        parts.append(train_clean(basic_clean(df)))
        print(f"{f}: {len(df):,} raw -> {len(parts[-1]):,} kept")
    train = pd.concat(parts, ignore_index=True).drop_duplicates(subset=["en", "de"])
    train = train[~train["en"].isin(held_out_en)]  # no overlap with val/test
    stats += [("train raw", raw_total), ("train cleaned", len(train))]

    train = train.sample(n=min(TRAIN_SAMPLE, len(train)), random_state=SEED)
    stats.append(("train sampled", len(train)))

    for name, df in [("train", train), ("validation", val), ("test", test)]:
        df.reset_index(drop=True).to_csv(OUT_DIR / f"{name}.csv", index=False, encoding="utf-8")

    print("\nRow counts:")
    for label, n in stats:
        print(f"  {label:<20} {n:>10,}")


if __name__ == "__main__":
    main()
