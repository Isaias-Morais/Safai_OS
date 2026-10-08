"""
SafaiOS Real-time OpenCV Webcam Inference Application
Captures webcam frames, runs inference using the trained SafaiOS YOLO checkpoint,
and displays real-time bounding boxes, waste classes, and confidence scores.
"""
import argparse
import time
from pathlib import Path

def run_webcam_inference(weights_path="models/checkpoints/safaios_baseline/weights/best.pt", camera_idx=0, conf=0.3):
    print("=== SafaiOS Real-time Webcam Waste Detector ===")
    print(f"Loading trained weights: {weights_path}")
    
    try:
        import cv2
        from ultralytics import YOLO
    except ImportError:
        print("Required dependencies (opencv-python, ultralytics) are missing.")
        return

    weights = Path(weights_path)
    if not weights.exists():
        print(f"ERROR: Trained checkpoint not found at '{weights_path}'.")
        print("Webcam demo must run using a trained SafaiOS checkpoint, not a generic COCO model.")
        return

    model = YOLO(weights_path)
    cap = cv2.VideoCapture(camera_idx)
    
    if not cap.isOpened():
        print(f"Failed to open webcam index {camera_idx}")
        return

    print("Webcam stream started. Press 'q' or ESC to exit.")
    
    prev_time = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame from webcam.")
            break

        results = model.predict(source=frame, conf=conf, verbose=False)
        annotated_frame = results[0].plot()

        # FPS calculation
        curr_time = time.time()
        fps = 1.0 / (curr_time - prev_time + 1e-6)
        prev_time = curr_time

        cv2.putText(
            annotated_frame,
            f"SafaiOS Realtime | FPS: {fps:.1f}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.imshow("SafaiOS - Waste Detection Live Stream", annotated_frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Webcam session closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SafaiOS Live Webcam Inference")
    parser.add_argument("--weights", default="models/checkpoints/safaios_baseline/weights/best.pt")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--conf", type=float, default=0.3)
    args = parser.parse_args()

    run_webcam_inference(args.weights, args.camera, args.conf)
