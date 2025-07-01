from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import cv2
import asyncio
import base64
import numpy as np
from ultralytics import YOLO

app = FastAPI()

# Configure CORS to allow requests from Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = YOLO('models/best.pt')

def draw_detections(frame, results):
    """Draw bounding boxes and labels on the frame"""
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                # Get coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                
                # Get confidence and class
                confidence = box.conf[0].cpu().numpy()
                class_id = int(box.cls[0].cpu().numpy())
                
                # Get class name
                class_name = model.names[class_id]
                
                # Only draw if confidence is above threshold
                if confidence > 0.5:
                    # Draw bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Create label with class name and confidence
                    label = f"{class_name}: {confidence:.2f}"
                    
                    # Get text size for background rectangle
                    (text_width, text_height), _ = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1
                    )
                    
                    # Draw background rectangle for text
                    cv2.rectangle(
                        frame, 
                        (x1, y1 - text_height - 10), 
                        (x1 + text_width, y1), 
                        (0, 255, 0), 
                        -1
                    )
                    
                    # Draw text
                    cv2.putText(
                        frame,
                        label,
                        (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 0, 0),  # Black text
                        1,
                        cv2.LINE_AA
                    )
    return frame

@app.websocket("/ws/video")
async def video_websocket(websocket: WebSocket):
    await websocket.accept()
    cap = cv2.VideoCapture(0)  # or video source
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    try:
        while True:
            ret, frame = cap.read()

            if ret:
                # Run YOLO inference
                results = model(frame, verbose=False, device='cuda')
                
                # Draw detections on frame
                frame_with_detections = draw_detections(frame, results)
                
                # Optional: Add frame info
                cv2.putText(
                    frame_with_detections,
                    f"Objects detected: {len(results[0].boxes) if results[0].boxes is not None else 0}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )
                
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame_with_detections, [cv2.IMWRITE_JPEG_QUALITY, 80])
                
                # Convert to base64
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                await websocket.send_text(f"data:image/jpeg;base64,{frame_base64}")
                
            await asyncio.sleep(0.033)  # ~30 FPS
    except Exception as e:
        print(f"Error in video stream: {e}")
    finally:
        cap.release()

# Optional: Add endpoint to get detection data separately
@app.websocket("/ws/detections")
async def detections_websocket(websocket: WebSocket):
    await websocket.accept()
    cap = cv2.VideoCapture(0)
    
    try:
        while True:
            ret, frame = cap.read()
            
            if ret:
                # Run YOLO inference
                results = model(frame, verbose=False)
                
                # Extract detection data
                detections = []
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            confidence = float(box.conf[0].cpu().numpy())
                            class_id = int(box.cls[0].cpu().numpy())
                            class_name = model.names[class_id]
                            
                            if confidence > 0.5:
                                detections.append({
                                    "class_name": class_name,
                                    "confidence": confidence,
                                    "bbox": [float(x1), float(y1), float(x2), float(y2)]
                                })
                
                # Send detection data as JSON
                await websocket.send_json({
                    "detections": detections,
                    "timestamp": asyncio.get_event_loop().time()
                })
                
            await asyncio.sleep(0.1)  # 10 FPS for detection data
            
    except Exception as e:
        print(f"Error in detection stream: {e}")
    finally:
        cap.release()
