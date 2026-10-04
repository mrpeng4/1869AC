from supabase import create_client
import re
supabaseUsernameRegex = re.compile(
    r"^[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*$"
)

VITE_SUPABASE_URL = "https://qzqhzwsfubazirdzxnse.supabase.co"
VITE_SUPABASE_PUBLISHABLE_KEY = "sb_publishable_9mpzUg4eXNLneiT-3O65VA_IhjFNt8E"
supabase = create_client(VITE_SUPABASE_URL, VITE_SUPABASE_PUBLISHABLE_KEY)
while True:
    print("login, signup, or continue as a guest?")
    print("(l/s/g): ")
    yor = input("").strip()
    if yor.lower() == "l":
        while True:
            print("+====================================================+")
            print("Username:")
            username = input("").strip()
            print("Password: ")
            password = input("").strip()
            real_username = username + "@gmail.com"
            try:
                response = supabase.auth.sign_in_with_password(
                    {"email": real_username, 
                    "password": password,}
                )
                print("Welcome back " + username)
                break
            except Exception as e:
                print("Login failed:", e)
    elif yor.lower() == "s":
        print("+====================================================+")
        while True:
            print("Username: ")
            username = input("").strip()
            real_username = username + "@gmail.com"
            if not supabaseUsernameRegex.match(username):
                print("Sorry. No spaces, '@' or leading/trailing periods allowed")
                continue
            ##check for duplicates
            valid = supabase.rpc("check_username", {
                "user_name":username
            }).execute()
            if valid.data is True:
                print("sorry. that username is already taken!")
                continue
            else:
                break
        while True:
            print("Password: ")
            password = input("").strip()
            if len(password) < 6:
                print("Passwords must be atleast 6 characters long!")
                continue
            try:
                response = supabase.auth.sign_up(
                {
                    "email": real_username, 
                    "password": password
                }
                )
                print("Account created! Logging you in...")
                break
            except Exception as e:
                print("Signup error:", e)

    elif yor.lower() == "g":
        print("Continuing as a guest!")
    else:
        print("Invalid option.")
