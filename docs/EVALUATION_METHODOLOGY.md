# SafaiOS Evaluation Methodology

## 1. Operating Metrics vs Summary Metrics

- **Summary Precision / Recall (`box.mp` / `box.mr`)**: Calculated across the confidence sweep curve at peak F1 threshold.
- **Operational Precision / Recall**: Evaluated strictly at the fixed operational operating point (`conf = 0.25`, `iou = 0.60`).

## 2. Stratification Dimensions

- **Overlap Stratum**: Ground truth boxes with pairwise IoU $\ge 0.10$ with any other box in the image.
- **Relative Scale Stratum**:
  - Small: Normalized area $< 0.025$.
  - Medium: Normalized area between $0.025$ and $0.050$.
  - Large: Normalized area $> 0.050$.
