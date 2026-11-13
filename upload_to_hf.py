"""Upload ./processed (train.csv, validation.csv, test.csv, README.md) to a Hugging Face dataset repo.

Log in first:   hf auth login
Then run:       python upload_to_hf.py <your-username>/<dataset-name> [--private]
"""

import sys
from pathlib import Path

from huggingface_hub import HfApi

FOLDER = Path(__file__).resolve().parent / "processed"


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    repo_id = sys.argv[1]
    private = "--private" in sys.argv[2:]

    api = HfApi()
    print(f"Logged in as: {api.whoami()['name']}")
    api.create_repo(repo_id, repo_type="dataset", private=private, exist_ok=True)
    api.upload_folder(
        folder_path=FOLDER,
        repo_id=repo_id,
        repo_type="dataset",
        allow_patterns=["train.csv", "validation.csv", "test.csv", "README.md"],
        commit_message="Add cleaned WMT14 en-de TRAIN/VALIDATE/TEST splits",
    )
    print(f"Done: https://huggingface.co/datasets/{repo_id}")


if __name__ == "__main__":
    main()
