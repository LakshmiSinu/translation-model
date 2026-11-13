# translation-model

English → German machine translation project using the WMT 2014 English–German dataset.

## Dataset

Processed TRAIN / VALIDATE / TEST splits are on Hugging Face:
**https://huggingface.co/datasets/lakshmi-sinu/wmt14-en-de-cleaned**

| Split | File | Rows | Source |
|---|---|---|---|
| Train | `train.csv` | 100,000 | Random sample (seed 42) of the cleaned WMT14 training data |
| Validation | `validation.csv` | 2,996 | newstest2013 |
| Test | `test.csv` | 3,003 | newstest2014 |

Columns: `en` (English), `de` (German).

Original data: [Kaggle – WMT 2014 English-German](https://www.kaggle.com/datasets/mohamedlotfy50/wmt-2014-english-german), downloaded through the Hugging Face mirror `wmt/wmt14` (config `de-en`).

## Processing

All splits: Unicode NFC normalization, whitespace cleanup, empty and duplicate pairs removed.

Training data only:
- untranslated pairs (English = German) removed
- 1–100 words per side
- length ratio between sides at most 2.5
- pairs with no letters removed
- sentences that also appear in validation/test removed (no leakage)

4,508,785 raw pairs → 4,330,486 cleaned → 100,000 sampled.

## Reproduce

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python prepare_wmt14.py          # downloads ~820 MB, writes processed/*.csv
python upload_to_hf.py <user>/<dataset-name>   # after: hf auth login
```

## Files

- `prepare_wmt14.py` – download, clean, split and save the data
- `upload_to_hf.py` – upload the processed splits to Hugging Face
- `processed/README.md` – dataset card used on Hugging Face

## Reference

Sai et al., 2023. *IndicMT Eval: A Dataset to Meta-Evaluate Machine Translation Metrics for Indian Languages.* ACL 2023.
