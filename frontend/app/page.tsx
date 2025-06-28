'use client';

import { useState, useRef } from 'react';
import axios from 'axios';

export default function Home() {
  const [recording, setRecording] = useState(false);
  const [videoBlob, setVideoBlob] = useState(null);
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      streamRef.current = stream;
      videoRef.current.srcObject = stream;
      videoRef.current.play();

      const recorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
      mediaRecorderRef.current = recorder;
      const chunks = [];

      recorder.ondataavailable = (e) => chunks.push(e.data);
      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'video/webm' });
        setVideoBlob(blob);
      };

      recorder.start();
      setRecording(true);
    } catch (err) {
      console.error('Error starting recording:', err);
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current.stop();
    streamRef.current.getTracks().forEach((track) => track.stop());
    setRecording(false);
  };

  const uploadVideo = async () => {
    if (!videoBlob) return;

    const formData = new FormData();
    formData.append('file', videoBlob, 'recorded_video.webm');

    try {
      const response = await axios.post('http://localhost:8000/process-video/', formData, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'processed_video.mp4');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Error uploading video:', err);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <h1 className="text-3xl font-bold mb-6">Webcam Recorder with Stopwatch</h1>
      <video
        ref={videoRef}
        className="w-[640px] h-[480px] bg-black rounded-lg shadow-lg"
        muted
      />
      <div className="mt-6 space-x-4">
        {!recording ? (
          <button
            onClick={startRecording}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
          >
            Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
          >
            Stop Recording
          </button>
        )}
        {videoBlob && (
          <button
            onClick={uploadVideo}
            className="px-6 py-2 bg-green-500 text-white rounded-lg hover-bg-green-600 transition"
          >
            Upload Video
          </button>
        )}
      </div>
    </div>
  );
}