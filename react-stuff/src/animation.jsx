//CREDITS TO https://ascii-motion.app/ FOR WRITING THIS AMAZING REACT COMPONENT!
import react, { useCallback, useRef, useEffect, useState } from 'react';
import AsciiMotionAnimation from './ascii-motion-animation.jsx';

export default function MyPage() {
  const playbackRef = useRef(null);
  const handleReady = useCallback((api) => {
    playbackRef.current = api;
    api.play()
  }, []);

  return (
    <div className = "animation">
      <AsciiMotionAnimation 
        showControls={false}
        autoPlay={false}
        onReady={handleReady}
      />
    </div>
  );
}