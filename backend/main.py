from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import cv2
import asyncio
import base64
import numpy as np
from ultralytics import YOLO
import time
from collections import defaultdict, deque

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

BALL_CLASS_ID = 0  # update if different
FOOT_CLASS_ID = 1

def draw_detections(frame, results, juggle_count, is_below):
    """Draw bounding boxes and labels on the frame"""

    
    was_above = True # old algorithm
    was_below = False
    foot_top_y = None
    ball_bottom_y = None
    
    print('funciton called')

    for result in results:
        # print(f"top of is below: {is_below}")
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                cls_id = int(box.cls[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                

                # Draw bounding boxes
                label = "Foot" if cls_id == FOOT_CLASS_ID else "Ball" if cls_id == BALL_CLASS_ID else str(cls_id)
                
                
                if cls_id == FOOT_CLASS_ID:
                    color = (0, 255, 0) 
                elif cls_id == BALL_CLASS_ID:
                    color = (0, 0, 255)
                else:
                    color = (255, 0, 0) 
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f'{label}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                # print('Label', label, '| box_id', box_id)

                if cls_id == FOOT_CLASS_ID:
                    if foot_top_y == None:
                        foot_top_y = y1  # top of foot bounding box
                        # print('Found Foot')
                    else:
                        if foot_top_y > y1:
                            # print('Lower Foot:', foot_top_y)
                            foot_top_y = y1
                            # print('Higher Foot:', foot_top_y)

                elif cls_id == BALL_CLASS_ID:
                    ball_bottom_y = y2  # bottom of ball bounding box

        if foot_top_y is not None and ball_bottom_y is not None:
            # print(f'ball_bottom_y: {ball_bottom_y} and foot_top_y: {foot_top_y}')
            # print(f'is_below: {is_below}')
            # print(f"juggle_count: {juggle_count}")

            if not is_below and ball_bottom_y > (foot_top_y - 100):
                is_below = True
                # print('is_below now true')
            elif is_below and ball_bottom_y < (foot_top_y - 100):
                is_below = False
                juggle_count += 1

        # Overlay juggle count on frame
        cv2.putText(frame, f'Juggles: {juggle_count}', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

        # Write frame to output
        # cv2.imshow("Juggle Counter", frame)

    return frame, juggle_count, is_below

@app.websocket("/ws/video")
async def video_websocket(websocket: WebSocket):
    await websocket.accept()
    cap = cv2.VideoCapture(0)  # or video source
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
    cap.set(cv2.CAP_PROP_FPS, 100)

    juggle_count = 0
    is_below = False
    
    try:
        while True:
            ret, frame = cap.read()

            if ret:
                frame = cv2.flip(frame, 1)

                # Run YOLO inference
                results = model(frame, verbose=False, device='cuda')
                
                # Draw detections on frame
                frame_with_detections, juggle_count, is_below = draw_detections(frame, results, juggle_count, is_below)

                # frame_with_detections = cv2.flip(frame_with_detections, 1)
                
                # Optional: Add frame info
                # cv2.putText(
                #     frame_with_detections,
                #     f"Objects detected: {len(results[0].boxes) if results[0].boxes is not None else 0}",
                #     (10, 30),
                #     cv2.FONT_HERSHEY_SIMPLEX,
                #     0.7,
                #     (255, 255, 255),
                #     2,
                #     cv2.LINE_AA
                # )
                
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
                results = model(frame, verbose=False, device='cuda')
                
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
