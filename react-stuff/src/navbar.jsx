import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import {Link} from 'react-router-dom'
import './index.css'
import cover from "./assets/cover.PNG"

export default function NavBar () {
    return(
    <nav className = "nav">
        <div className = "logo">
            <img className = "small" src = {cover} />
            <h1> meow </h1>
        </div>

        {/* THE ACTUAL LIST! */}

        <ul>
            <li> <Link to = "/"> Home </Link> </li>
            <li> <Link to = "/features"> Features </Link> </li>
            <li> <Link to = "/"> Authenticate </Link> </li>

        </ul>
    </nav>
    );
}