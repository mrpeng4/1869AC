import { useState } from 'react'
import Features from './features.jsx'
import {Routes, Route, useNavigate} from 'react-router-dom'
//IMAGES
import left from "./assets/left.PNG"
import right from "./assets/right.PNG"
import cd from "./assets/cd.PNG"
import chest from "./assets/chest.PNG"
import couch from "./assets/couch.PNG"
import cover from "./assets/cover.PNG"
import fish3 from "./assets/fish-3.PNG"
import fish from "./assets/fish.PNG"
import floor1 from "./assets/floor-1.PNG"
import floor2 from "./assets/floor-2.PNG"
import floor3 from "./assets/floor-3.PNG"
import floor4 from "./assets/floor-4.PNG"
import grate1 from "./assets/grate-1.PNG"
import grate2 from "./assets/grate-2.PNG"
import grate3 from "./assets/grate-3.PNG"
import grate4 from "./assets/grate-4.PNG"
import greyfloor1 from "./assets/grey-floor-1.PNG"
import greyfloor3 from "./assets/grey-floor-3.PNG"
import greywall2 from "./assets/grey-wall-2.PNG"
import human2 from "./assets/human-2.PNG"
import human from "./assets/human.PNG"
import locker from "./assets/locker.PNG"
import tank from "./assets/tank.PNG"
import wall2 from "./assets/wall-2.PNG"
import wall3 from "./assets/wall-3.PNG"
import wallblank from "./assets/wall-blank.PNG"
import wallclosed from "./assets/wall-closed.PNG"
import wallcloser from "./assets/wall-closer.PNG"
import wall from "./assets/wall.PNG"

const all = [wall,wallcloser,wallclosed,wallblank,wall3,wall2,greywall2,greyfloor3,greyfloor1,floor4,floor3,floor2,floor1,grate4,grate3,grate2,grate1,tank,locker,human,human2,fish,fish3,cover, couch, chest]

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
export default function Home() {
  const Navigate = useNavigate()
  return (
    <>
      <motion.div id = "column" {...mainSettings}>
        <div className = "row">
          <h2> Welcome to 1869 AC </h2>
          <img id = "bounce" src = {cd} />
        </div>
        <p style = {{paddingLeft: "20%", fontSize: "2vw"}}> The offline and online music player! </p>
        <button style = {{marginLeft: "20%", fontSize: "2vw"}} onClick = {() => Navigate("/features")}> View All Current Features </button>
      </motion.div>

      <motion.div className = "biggie" {...scrollSettings}>
        <div className = "row reverse">
          <div>
            <h2 className = "stack"> Currently a work in progress! </h2>
          </div>
            <img className = "ugh"  src = {left} />
        </div>
      </motion.div>

      <motion.div className = "biggie" {...scrollSettings}>
        <div className = "row">
          <div>
            <h2 className = "stack"> Right now the app is only avaiable offline on your terminal! It's compatible with Mac, Linux, and Windows!</h2>
          </div>
          <img className = "ugh" src = {right} />
        </div>
      </motion.div>

      <motion.div className = "biggie" {...scrollSettings}>
        <div className = "row reverse">
          <div>
            <h2 className = "stack"> You can install the application by going to this <a href = "https://github.com/mrpeng4/1869AC">repository</a> and cloning it!</h2>
          </div>
          <img className = "ugh"  src = {left} />
        </div>
      </motion.div>

      <motion.div className = "biggie" {...scrollSettings}>
        <div className = "row">
          <div>
            <h2 className = "stack"> You also need to have python and VLC media player installed!</h2>
          </div>
          <img className = "ugh"  src = {right} />
        </div>
      </motion.div>

      <div>
        {[...all].sort(() => Math.random() - 0.5)
        .map((img,index) => (
          <img
            className = "small"
            key = {index}
            src = {img}
          />
        ))}
      </div>
    </>
  )
}

