"""Dataset class distribution and imbalance analysis."""
from typing import List, Dict, Any
from collections import Counter

def compute_class_distribution(annotations: List[int], num_classes: int = 5) -> Dict[str, Any]:
    """Computes count, proportion, and imbalance metrics across class IDs."""
    total = len(annotations)
    counts = Counter(annotations)
    distribution = {}

    for c in range(num_classes):
        cnt = counts.get(c, 0)
        prop = cnt / total if total > 0 else 0.0
        distribution[c] = {"count": cnt, "proportion": prop}

    max_cnt = max(counts.values()) if counts else 0
    min_cnt = min(counts.values()) if counts else 0
    imbalance_ratio = max_cnt / min_cnt if min_cnt > 0 else 0.0

    return {
        "total_instances": total,
        "per_class": distribution,
        "imbalance_ratio": imbalance_ratio
    }
