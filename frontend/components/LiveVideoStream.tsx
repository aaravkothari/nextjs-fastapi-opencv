"use client";

import LoginButton from "@/components/LoginLogoutButton";
import UserGreetText from "@/components/UserGreetText";
import { createClient } from "@/utils/supabase/client";

// components/VideoStream.js

import { useEffect, useRef, useState } from "react";

const VideoStream = () => {
    const imgRef = useRef<HTMLImageElement | null>(null);
    const [ws, setWs] = useState<WebSocket | null>(null);
    const [user, setUser] = useState<any>(null);
    const supabase = createClient();




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
        if (user !== null) {
        const websocket = new WebSocket("ws://localhost:8000/ws/video");

        websocket.onmessage = (event) => {
        if (imgRef.current) {
            imgRef.current.src = event.data;
        }
        };

        setWs(websocket);

        return () => websocket.close();
        }
        

    }, [user])

    if (user !== null) {
    return (
        <>
        
        
        <div className="flex justify-center mx-12">
            <img ref={imgRef} className="border-lime-500 border-4 rounded-2xl w-max" alt="Live Video Stream" />
        </div>
        </>
    );
    }
}

export default VideoStream
