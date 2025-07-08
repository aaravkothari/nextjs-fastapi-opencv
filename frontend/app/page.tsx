  "use client";

import LoginButton from "@/components/LoginLogoutButton";
  // components/VideoStream.js

  import { useEffect, useRef, useState } from "react";

  export default function VideoStream() {
    const imgRef = useRef<HTMLImageElement | null>(null);
    const [ws, setWs] = useState<WebSocket | null>(null);

    useEffect(() => {
      const websocket = new WebSocket("ws://localhost:8000/ws/video");

      websocket.onmessage = (event) => {
        if (imgRef.current) {
          imgRef.current.src = event.data;
        }
      };

      setWs(websocket);

      return () => websocket.close();
    }, []);

    return (
      <>
        <div className="flex justify-center my-8">
          
          <div className="m-6 flex justify-between items-center w-5/6 h-16 rounded-2xl px-7 bg-gray-100">
            <img src="footyup-logo.png" className="h-48 mb-1"></img>
            <button className="border-2 border-black bg-black text-lime-500 rounded-3xl px-4 py-1 font-semibold">Yo</button>
            <LoginButton />
          </div>
        </div>
        
        <div className="flex justify-center">
          <img ref={imgRef} className="border-lime-500 border-4 rounded-2xl w-140" alt="Live Video Stream" />
        </div>
      </>
    );
  }
