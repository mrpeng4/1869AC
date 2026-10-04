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
  viewPort: {once: true, amount: 0.5}, //how much before
  transition: {duration: 0.8, ease: "ease-in-out"}
}
const scrollSettings = {
  initial: {opacity: 0, y: 50}, 
  whileInView: {opacity: 1, y: 0}, 
  viewPort: {once: false, amount: 0.2}, //how much before
  transition: {duration: 0.8, ease: "ease-in-out"}
}
function App() {
  const [count, setCount] = useState(0)

  return (
    <>
    <motion.div id = "column" {...mainSettings}>
      <div id = "row">
        <h1> Welcome to 1869 AC </h1>
        <img id = "bounce" src = {cover} />
      </div>
      <p style = {{paddingLeft: "20%", fontSize: "2vw"}}> The offline and online music player! </p>
    </motion.div>
    
    <div class = "biggie">
      <p> intro</p>
    </div>

    <motion.div class = "biggie" {...scrollSettings}>
      <p> smth </p>
    </motion.div>

    </>
  )
}

export default App
