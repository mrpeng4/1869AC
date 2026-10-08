///STORES PLAYER DATA

export function get_login_status(){
    return localStorage.getItem('login-status') === 'true';//ONLY STRINGS ALLOWED
}
export function set_login_status(new_status){ 
    return localStorage.setItem('login-status', String(new_status));//ONLY STRINGS ALLOWED
}

//use local storage!! to keep data there a while :3