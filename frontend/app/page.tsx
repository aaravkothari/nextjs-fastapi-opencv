"use client"

// components/VideoStream.js

import { useEffect, useRef, useState } from 'react';

export default function VideoStream() {
  const imgRef = useRef(null);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    const websocket = new WebSocket('ws://localhost:8000/ws/video');
    
    websocket.onmessage = (event) => {
      if (imgRef.current) {
        imgRef.current.src = event.data;
      }
    };

    setWs(websocket);

    return () => websocket.close();
  }, []);

  return <img ref={imgRef} alt="Live Video Stream" />;
}