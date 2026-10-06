//CREDITS TO https://ascii-motion.app/ FOR WRITING THIS AMAZING REACT COMPONENT!
import { useCallback, useRef, useEffect } from 'react';
import AsciiMotionAnimation from './ascii-motion-animation.jsx';

export default function MyPage() {
  const playbackRef = useRef(null);
  const handleReady = useCallback((api) => {
    playbackRef.current = api;
  }, []);
  useEffect(() => {
      playbackRef.current?.play()
    },[])
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