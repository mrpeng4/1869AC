// USE THIS TO PROTECT A PATH BY SURROUNDING IT
import {Navigate} from 'react-router-dom';
import {useEffect} from 'react'
import {get_login_status} from './data.jsx'


export default function Protected({children}){
    const isAuthenticated = get_login_status()
    if(!isAuthenticated){
        return <Navigate to =  "/login" />
    }
    return children 
}