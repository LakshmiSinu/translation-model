---
language:
- en
- de
task_categories:
- translation
size_categories:
- 100K<n<1M
configs:
- config_name: default
  data_files:
  - split: train
    path: train.csv
  - split: validation
    path: validation.csv
  - split: test
    path: test.csv
---

# WMT14 English–German (cleaned, 100k training subset)

A processed version of the WMT 2014 English–German parallel corpus, with TRAIN, VALIDATE and TEST splits.

## Files

| Split | File | Rows | Source |
|---|---|---|---|
| Train | `train.csv` | 100,000 | Random sample (seed 42) of the cleaned WMT14 training data (Europarl, Common Crawl, News Commentary) |
| Validation | `validation.csv` | 2,996 | newstest2013 |
| Test | `test.csv` | 3,003 | newstest2014 |

Each file has two columns: `en` (English) and `de` (German).

## Processing

Applied to all splits:
- Unicode NFC normalization; repeated whitespace collapsed; leading and trailing spaces removed
- Pairs with an empty side removed
- Exact duplicate pairs removed

Applied to the training data only:
- Pairs where the English and German text are identical (untranslated) removed
- Each side must have 1–100 words
- Word-length ratio between the two sides must be at most 2.5
- Pairs with no letters (only numbers or symbols) removed
- Pairs whose English sentence appears in the validation or test set removed, to avoid leakage
- Training data went from 4,508,785 raw pairs to 4,330,486 cleaned pairs; 100,000 were then sampled at random

## Source

Original data comes from the WMT 2014 shared task (https://www.statmt.org/wmt14/translation-task.html), downloaded through the Hugging Face dataset `wmt/wmt14` (config `de-en`). The same data is available on Kaggle as `mohamedlotfy50/wmt-2014-english-german`. Use is subject to the terms of the original corpora.
