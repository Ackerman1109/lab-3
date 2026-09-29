from flask import Flask, render_template, request, redirect, url_for, make_response
import json

app = Flask(__name__)

USERS_FILE = "users.json"



def load_users():
    with open(USERS_FILE, "r") as file:
        return json.load(file)



def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)



def create_profile(email):

    
    username = email.split("@")[0]

   
    name = username.replace(".", " ").replace("_", " ")

   
    name = name.title()

    
    letters = ""

    for word in name.split():
        if word:
            letters += word[0]

  
    letters = letters[:2].upper()

   
    if len(letters) == 1:
        letters = letters * 2

    return {
        "email": email,
        "username": username,
        "name": name,
        "letters": letters
    }



@app.route("/")
def home():

    email = request.cookies.get("email")

    if not email:
        return redirect(url_for("login"))

    return redirect(url_for("profile"))



@app.route("/profile")
def profile():

    email = request.cookies.get("email")

    
    if not email:
        return redirect(url_for("login"))

    
    profile = create_profile(email)

    return render_template(
        "profile.html",
        profile=profile
    )



@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        
        if not email or not password or not confirm_password:

            return render_template(
                "register.html",
                error="Please fill in all fields"
            )

        if len(password) < 6:

            return render_template(
                "register.html",
                error="Password must contain at least 6 characters"
            )

        
        if password != confirm_password:

            return render_template(
                "register.html",
                error="Passwords do not match"
            )

     
        users = load_users()

        for user in users:

            if user["email"] == email:

                return render_template(
                    "register.html",
                    error="This email is already registered"
                )

      
        users.append({
            "email": email,
            "password": password
        })

      
        save_users(users)

     
        response = make_response(
            redirect(url_for("profile"))
        )

        response.set_cookie("email", email)

        return response

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

   
        if not email or not password:

            return render_template(
                "login.html",
                error="Please fill in all fields"
            )

        users = load_users()

        
        for user in users:

            if user["email"] == email and user["password"] == password:

                
                response = make_response(
                    redirect(url_for("profile"))
                )

                response.set_cookie("email", email)

                return response

       
        return render_template(
            "login.html",
            error="Incorrect email or password"
        )

    return render_template("login.html")

@app.route("/logout")
def logout():

   
    response = make_response(
        redirect(url_for("login"))
    )

    response.delete_cookie("email")

    return response


if __name__ == "__main__":
    app.run(debug=True)