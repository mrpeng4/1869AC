import {BrowserRouter, Routes, Route, useLocation} from 'react-router-dom'
import './index.css'
import Home from './home.jsx'
import Features from './features.jsx'
//ALL PAGES!

export default function App() {
  return(
    <BrowserRouter>
      <Routes>
        <Route path = "/" element = {<Home/>}/>
        <Route path = "/features" element = {<Features/>}/>
      </Routes>
    </BrowserRouter>
  );
}