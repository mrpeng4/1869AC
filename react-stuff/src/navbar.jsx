import { Link } from 'react-router-dom'
import './index.css'
import cover from "./assets/cover.PNG"

export default function NavBar() {
    return (
        <nav className="nav">
            <div className="logo">
                <img className="small" src={cover} alt="logo" />
                <p> meow </p>
            </div>

            <ul className="list">
                <li> <Link to="/"> Home </Link> </li>
                <li> <Link to="/features"> Features </Link> </li>
            </ul>
        </nav>
    );
}