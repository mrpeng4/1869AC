import { useState } from 'react'
import heroImg from './assets/hero.png'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import cover from "./assets/hero.png"
import './index.css'
import { motion } from 'framer-motion'

const mainSettings = {
  initial: {opacity: 1, y: 200}, 
  whileInView: {opacity: 1, y: 0}, 
  viewport: {once: true, amount: 0.1}, //how much before
  transition: {duration: 0.8, ease: "ease-in-out"}
}
const scrollSettings = {
  initial: {opacity: 0, y: 20}, 
  whileInView: {opacity: 1, y: 0}, 
  viewport: {once: false, amount: 0.2}, //how much before
  transition: {duration: 0.8, ease: "ease-in-out"}
}
function App() {
  const [count, setCount] = useState(0)

  return (
    <>
    <motion.div id = "column" {...mainSettings}>
      <div className = "row">
        <h2> Welcome to 1869 AC </h2>
        <img id = "bounce" src = {cover} />
      </div>
      <p style = {{paddingLeft: "20%", fontSize: "2vw"}}> The offline and online music player! </p>
    </motion.div>

    <motion.div className = "biggie" {...scrollSettings}>
      <div className = "row reverse">
        <div>
          <h2 className = "stack"> Currently a work in progress! </h2>
        </div>
          <img src = {cover} />
      </div>
    </motion.div>

    <motion.div className = "biggie" {...scrollSettings}>
      <div className = "row">
        <div>
          <h2 className = "stack"> Right now the app is only avaiable offline on your terminal! It's compatible with Mac, Linux, and Windows!</h2>
        </div>
        <img src = {cover} />
      </div>
    </motion.div>

    <motion.div className = "biggie" {...scrollSettings}>
      <div className = "row reverse">
        <div>
          <h2 className = "stack"> You can install the application by going to this <a href = "https://github.com/mrpeng4/1869AC">repository</a> and cloning it!</h2>
        </div>
        <img src = {cover} />
      </div>
    </motion.div>

    <motion.div className = "biggie" {...scrollSettings}>
      <div className = "row">
        <div>
          <h2 className = "stack"> You also need to have python and VLC media player installed!</h2>
        </div>
        <img src = {cover} />
      </div>
    </motion.div>

    <div>
      
    </div>
    </>
  )
}

export default App
