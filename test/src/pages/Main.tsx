import React from 'react';
import { Link } from 'react-router-dom';

export const Main: React.FC = () => {
  
  return (
    <div className="text-3xl font-sans bg-gradient-to-b from-slate-800 to-cyan-800 w-screen h-screen flex flex-col text-white text-center">
      <div className='font-extralight mt-auto'>
        Vioke
      </div>
      <Link to="/app" className='font-light text-xl border mx-auto px-2 py-1 mb-auto mt-3 hover:text-white hover:no-underline'>
          Get Started
      </Link>
    </div>
  )
};

export default Main;
