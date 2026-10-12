"""Device selection and hardware accelerator inspection."""
from typing import Dict, Any

def get_optimal_device() -> str:
    """Returns optimal compute device ('0' for CUDA or 'cpu')."""
    try:
        import torch
        return "0" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"

def get_device_summary() -> Dict[str, Any]:
    """Inspects available hardware and memory resources."""
    try:
        import torch
        cuda_avail = torch.cuda.is_available()
        summary = {
            "cuda_available": cuda_avail,
            "device_count": torch.cuda.device_count() if cuda_avail else 0,
            "current_device": get_optimal_device(),
        }
        if cuda_avail:
            summary["device_name"] = torch.cuda.get_device_name(0)
            props = torch.cuda.get_device_properties(0)
            summary["total_memory_mb"] = props.total_memory / (1024 * 1024)
            summary["allocated_memory_mb"] = torch.cuda.memory_allocated(0) / (1024 * 1024)
        return summary
    except Exception as e:
        return {
            "cuda_available": False,
            "device_count": 0,
            "current_device": "cpu",
            "note": str(e)
        }
