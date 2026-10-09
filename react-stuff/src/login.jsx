import { useState , useEffect, useRef} from 'react'
import { useNavigate} from 'react-router-dom'
import {set_login_status} from './data.jsx'

//MY BELOVED TOASTER
import toast from 'react-hot-toast';

export default function login(){
    const Navigate = useNavigate()
    const [name, setName] = useState("")
    const [password, setPassword] = useState("")
    async function submit(e) { 
        e.preventDefault(); 
        // DB CODE
        const real_username = name + "@gmail.com"
        try{
            const {data,error} = supabase.auth.signUp(
                {
                    "email": real_username, 
                    "password": password
                }
            )
            toast.success("Sucessfully logged in!")
            set_login_status(true)
            console.log("ERM WHAT THE SIGMA")
            setTimeout(()=>{Navigate("/dashboard")},[1000])
        }catch(e){
            toast.error(e.message)
        }
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

