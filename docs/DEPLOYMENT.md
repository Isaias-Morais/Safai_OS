# SafaiOS Deployment & Optimization Guide

This guide details best practices for deploying SafaiOS YOLO11s models on edge computing devices and centralized inference servers.

## Hardware Targets

1. **NVIDIA Jetson Orin / AGX**:
   - Recommended resolution: 768px FP16 TensorRT engine.
   - Expected latency: 8–15 ms per frame.
2. **Centralized Cloud Server (NVIDIA T4 / L4 / RTX 4060+)**:
   - Recommended resolution: 768px PyTorch or ONNX Runtime with CUDA execution provider.
   - Batch size: 8 to 16 for streaming camera pipelines.

## Export Pipeline

```bash
python -m src.export.exporter --weights best.pt --format onnx --imgsz 768 --half
```
