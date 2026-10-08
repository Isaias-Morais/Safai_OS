# SAFAIOS LOCKED TEST SET POLICY

**STATUS: STRICTLY LOCKED**

This dataset directory (`data/test_locked/`) contains the locked benchmark test set for SafaiOS.

## ISOLATION RULES
1. **NEVER** use any image or label in this directory for training.
2. **NEVER** use any image or label in this directory for data augmentation.
3. **NEVER** use any image or label in this directory for hyperparameter tuning.
4. **NEVER** overwrite or modify any file in this directory based on model results.
5. Ingestion and processing scripts MUST NOT automatically clean or overwrite this directory.

This dataset must remain untouched to evaluate real-world generalization performance.
