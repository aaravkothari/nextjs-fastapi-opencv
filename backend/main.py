from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import cv2
import numpy as np
import os
import tempfile
from datetime import datetime
import shutil

app = FastAPI()

@app.post("/process-video/")
async def process_video(file: UploadFile = File(...)):
    # Create temporary files for input and output
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_input:
        # Save uploaded video to temporary file
        shutil.copyfileobj(file.file, temp_input)
        input_path = temp_input.name

    output_path = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

    # Process video with OpenCV
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        return {"error": "Could not open video file"}

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define codec and create VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    start_time = datetime.now()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Calculate elapsed time for stopwatch
        elapsed = (datetime.now() - start_time).total_seconds()
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        stopwatch_text = f"{minutes:02d}:{seconds:02d}"

        # Overlay stopwatch in top-right corner
        cv2.putText(
            frame,
            stopwatch_text,
            (width - 150, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        out.write(frame)

    # Release resources
    cap.release()
    out.release()

    # Remove temporary input file
    os.remove(input_path)

    # Return the processed video
    return FileResponse(output_path, media_type="video/mp4", filename="processed_video.mp4")