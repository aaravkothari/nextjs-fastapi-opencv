import VideoStream from '@/components/LiveVideoStream'
import LoginButton from '@/components/LoginLogoutButton'
import UserGreetText from '@/components/UserGreetText'
import React from 'react'

const Home = () => {
  return (
    <div>
      <div className="flex justify-center mt-8">
            
            <div className="m-6 flex justify-between items-center w-5/6 h-16 rounded-2xl px-7 bg-gray-100">
            <img src="Footy (1).png" className="h-52 mb-1"></img>
            <LoginButton />
            </div>
        </div>
        <div><UserGreetText/></div>
      <VideoStream />
    </div>
  )
}

export default Home