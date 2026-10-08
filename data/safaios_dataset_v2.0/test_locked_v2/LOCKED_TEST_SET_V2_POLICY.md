# SafaiOS Dataset v2.0 — Locked Test Set Governance Policy

**Project:** SafaiOS  
**Dataset Version:** safaios_dataset_v2.0  
**Test Set Version:** Locked Test Set v2.0 (`data/safaios_dataset_v2.0/test_locked_v2/`)  
**Status:** FROZEN & LOCKED  

---

## Strict Protection Rules
1. **NO HYPERPARAMETER TUNING:** Never use this test set to select learning rates, batch sizes, or augmentations.
2. **NO MODEL SELECTION:** Never select model checkpoints based on performance on this test set.
3. **NO THRESHOLD OPTIMIZATION:** Never tune confidence or IoU thresholds against this test set.
4. **NO AGGREGATION LEAKAGE:** Test set images must remain strictly isolated from all training and validation data.
