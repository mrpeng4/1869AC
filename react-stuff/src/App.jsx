import {BrowserRouter, Routes, Route, useLocation} from 'react-router-dom'
import './index.css'
import Home from './home.jsx'
import Features from './features.jsx'
import Navbar from './navbar.jsx'
//ALL PAGES!

export default function App() {
  return(
    <BrowserRouter>
      <Navbar/>
      <Routes>
        <Route path = "/" element = {<Home/>}/>
        <Route path = "/features" element = {<Features/>}/>
      </Routes>
    </BrowserRouter>
  );
}