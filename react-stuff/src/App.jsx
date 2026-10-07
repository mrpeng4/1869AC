import {BrowserRouter, Routes, Route, useLocation} from 'react-router-dom'
import { useState , useEffect, useRef} from 'react'
import './index.css'
import Home from './home.jsx'
import Features from './features.jsx'
import Navbar from './navbar.jsx'
import Login from './login.jsx'
//import Navbar from './navbar.jsx'
//ALL PAGES!
function Topset(){
  const path = useLocation();
  const target = useRef(null);
    useEffect(() => {
      if(target.current){
        target.current.scrollIntoView({ //special to start where i want
          behavior: "instant",  //smooth auto
          block: "start" //alligns to the top!
    })
    }
  }, [path])
  return (
    <div ref = {target}>
      <Routes>
        <Route path = "/" element = {<Home/>}/>
        <Route path = "/features" element = {<Features/>}/>
        <Route path = "/login" element = {<Login/>}/>
      </Routes>
    </div>
  ); 
}
export default function App() {
  return(
    <BrowserRouter>
      <Navbar/>
      <Topset/>
    </BrowserRouter>
  );
}