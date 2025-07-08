"use client";
import { createClient } from "@/utils/supabase/client";
import React, { useEffect, useState } from "react";

const UserGreetText = () => {
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
    if (user !== null) {
      return (
        <div className="flex font-bold left-0 top-0 w-full justify-center m-2">
          Welcome&nbsp;
          <div className="font-bold">{user.user_metadata.full_name ?? "user"}!</div>
        </div>
      );
    }
  return (
    <div className="flex font-bold left-0 top-0 w-full justify-center m-2">
      Sign-in to get started
    </div>
  );
};

export default UserGreetText;
