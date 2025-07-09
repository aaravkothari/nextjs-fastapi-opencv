"use client";

import LoginButton from "@/components/LoginLogoutButton";
import UserGreetText from "@/components/UserGreetText";
import { createClient } from "@/utils/supabase/client";
import { BsRecordBtnFill, BsRecordBtn } from "react-icons/bs";

// components/VideoStream.js

import { useEffect, useRef, useState } from "react";

const VideoStream = () => {
  const imgRef = useRef<HTMLImageElement | null>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [user, setUser] = useState<any>(null);
  const [recording, setRecording] = useState<boolean>(false);
  const supabase = createClient();
  const [juggles, setJuggles] = useState<number>(0);
  const [subJug, setSubJug] = useState<number>(0);

  useEffect(() => {
    const fetchUser = async () => {
      const {
        data: { user },
      } = await supabase.auth.getUser();
      setUser(user);
    };
    fetchUser();
  }, []);

  useEffect(() => {
    if (user !== null && recording) {
      const websocket = new WebSocket("ws://localhost:8000/ws/video");

      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (imgRef.current && data.frame) {
            imgRef.current.src = data.frame;
          }
          if (typeof data.juggles === "number") {
            setJuggles(data.juggles);
          }
        } catch (e) {
          // fallback for non-JSON or error
          console.error("WebSocket message error:", e);
        }
      };

      setWs(websocket);

      return () => websocket.close();
    }
  }, [user, recording]);

  if (user !== null) {
    return (
      <>
        <div className="flex justify-center text-6xl m-6">Juggles: {juggles - subJug}</div>

        {recording ? (
          <div className="flex justify-center mx-12">
            <div className="flex justify-center">
              <img
                ref={imgRef}
                className="border-lime-500 border-4 rounded-2xl w-max"
                alt="Starting..."
              />
            </div>
          </div>
        ) : (
          <div className="flex justify-center mx-12">
            <div className="flex justify-center">
              <div className="border-lime-500 border-4 rounded-2xl w-max p-12">
                Not Recording
              </div>
            </div>
          </div>
        )}

        {!recording ? (
          <div
            onClick={() => {
              setRecording(true);
            }}
            className="flex items-center justify-center"
          >
            <BsRecordBtnFill
              className="text-lime-500 hover:cursor-pointer"
              size="50"
            />
          </div>
        ) : (
          <div
            
            className="flex items-center justify-center text-lime-500 hover:cursor-pointer"
          >
            <div className="border-black border-2 text-lime-500 px-2 py-1 font-semibold bg-black rounded">Save Juggles</div>
            <BsRecordBtn onClick={() => { setRecording(false)}} className="mx-10" size="50" />
            <div className="border-black border-2 text-red-500 px-2 py-1 font-semibold bg-black rounded" onClick={() => {setSubJug(juggles)}}>Reset Juggles</div>
          </div>

          
        )}
      </>
    );
  }
};

export default VideoStream;
