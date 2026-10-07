import { useState , useEffect, useRef} from 'react'
import { useNavigate} from 'react-router-dom'

export default function login(){
    const Navigate = useNavigate()
    const [name, setName] = useState("")
    const [password, setPassword] = useState("")
    function submit(e) { 
        e.preventDefault(); 
        // DB CODE
        Navigate("/dashboard")
    }
    return(
        <div className = "container">
            <p> Login/Signup </p>
            <form className = "form" onSubmit = {submit}>
                <input 
                placeholder = "name"
                maxLength = "18"
                minLength = "6"
                onChange =  {(e) => {setName(e.target.value)}}
                />
                <input 
                placeholder = "password"
                maxLength = "18"
                minLength = "6"
                type = "password"
                onChange = {(e) => {setPassword(e.target.value)}}
                />
                <button type = "submit"> Submit! </button>
            </form>
            <p> {`Name ${name} Password ${password}`}</p>
        </div>
    );
}
