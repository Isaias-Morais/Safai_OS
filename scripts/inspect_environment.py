import sys
import os
import platform
import shutil
import json

def get_size(bytes_val, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes_val < factor:
            return f"{bytes_val:.2f} {unit}{suffix}"
        bytes_val /= factor
    return f"{bytes_val:.2f} Y{suffix}"

def inspect_environment():
    report = {}

    # Operating System
    report["os"] = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "architecture": platform.architecture()[0],
        "machine": platform.machine(),
        "processor": platform.processor()
    }

    # Python & Pip
    report["python"] = {
        "version": sys.version,
        "executable": sys.executable
    }

    try:
        import pip
        report["pip"] = {"version": pip.__version__}
    except ImportError:
        report["pip"] = {"version": "Not installed"}

    # CPU & RAM
    try:
        import psutil
        cpu_count_logical = psutil.cpu_count(logical=True)
        cpu_count_physical = psutil.cpu_count(logical=False)
        ram = psutil.virtual_memory()
        report["cpu_ram"] = {
            "logical_cpus": cpu_count_logical,
            "physical_cpus": cpu_count_physical,
            "total_ram": get_size(ram.total),
            "available_ram": get_size(ram.available),
            "ram_usage_percent": f"{ram.percent}%"
        }
    except ImportError:
        report["cpu_ram"] = {
            "logical_cpus": os.cpu_count(),
            "total_ram": "psutil not installed"
        }

    # Disk Space
    usage = shutil.disk_usage(os.getcwd())
    report["disk_space"] = {
        "total": get_size(usage.total),
        "used": get_size(usage.used),
        "free": get_size(usage.free)
    }

    # PyTorch & CUDA
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        report["pytorch_cuda"] = {
            "pytorch_version": torch.__version__,
            "cuda_available": cuda_available,
            "cuda_version": torch.version.cuda if cuda_available else None,
            "cudnn_version": torch.backends.cudnn.version() if cuda_available and torch.backends.cudnn.is_available() else None,
            "device_count": torch.cuda.device_count() if cuda_available else 0
        }
        if cuda_available:
            gpus = []
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                total_mem = props.total_memory
                allocated = torch.cuda.memory_allocated(i)
                reserved = torch.cuda.memory_reserved(i)
                gpus.append({
                    "id": i,
                    "name": props.name,
                    "total_vram": get_size(total_mem),
                    "allocated_vram": get_size(allocated),
                    "free_vram_est": get_size(total_mem - reserved),
                    "compute_capability": f"{props.major}.{props.minor}"
                })
            report["pytorch_cuda"]["gpus"] = gpus
    except ImportError:
        report["pytorch_cuda"] = {
            "pytorch_version": "Not installed",
            "cuda_available": False
        }

    # OpenCV
    try:
        import cv2
        report["opencv"] = {
            "version": cv2.__version__,
            "installed": True
        }
        # Webcam check
        webcams = []
        for index in range(4):
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW if platform.system() == "Windows" else cv2.CAP_ANY)
            if cap.isOpened():
                ret, _ = cap.read()
                webcams.append({"index": index, "working": ret})
                cap.release()
        report["opencv"]["webcams_detected"] = webcams
    except ImportError:
        report["opencv"] = {
            "version": "Not installed",
            "installed": False,
            "webcams_detected": []
        }

    # Ultralytics / YOLO
    try:
        import ultralytics
        report["ultralytics"] = {
            "version": ultralytics.__version__,
            "installed": True
        }
    except ImportError:
        report["ultralytics"] = {
            "version": "Not installed",
            "installed": False
        }

    return report

if __name__ == "__main__":
    env_data = inspect_environment()
    print(json.dumps(env_data, indent=2))
