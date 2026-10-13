
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    make_response,
    flash
)
import sqlite3
import json
import os

app = Flask(__name__)
app.secret_key = "lab4-demo-secret-key"

DATABASE = "users.db"
USERS_FILE = "users.json"


# Database connection
def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# Create database and table
def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        # Import existing users from users.json
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, "r", encoding="utf-8") as file:
                    users = json.load(file)

                for user in users:
                    db.execute(
                        """
                        INSERT OR IGNORE INTO users (email, password)
                        VALUES (?, ?)
                        """,
                        (user["email"], user["password"])
                    )
            except (json.JSONDecodeError, KeyError, TypeError):
                pass


init_db()


# Profile page
@app.route("/")
def instagram():
    email = request.cookies.get("email")

    if not email:
        return redirect(url_for("login"))

    with get_db() as db:
        user = db.execute(
            "SELECT id, email FROM users WHERE email = ?",
            (email,)
        ).fetchone()

    if user is None:
        response = make_response(redirect(url_for("login")))
        response.delete_cookie("email")
        flash("Please log in to continue.", "error")
        return response

    email = user["email"]
    name = email.split("@")[0]
    username = name.lower().replace(" ", "_")
    letters = name[:2].upper()

    profile = {
        "name": name,
        "username": username,
        "letters": letters,
        "email": email
    }

    return render_template("profile.html", profile=profile)


# Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not email or not password or not confirm_password:
            flash("Please fill in all fields.", "error")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash(
                "Password must contain at least 6 characters.",
                "error"
            )
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))

        try:
            with get_db() as db:
                db.execute(
                    """
                    INSERT INTO users (email, password)
                    VALUES (?, ?)
                    """,
                    (email, password)
                )
        except sqlite3.IntegrityError:
            flash("This email is already registered.", "error")
            return redirect(url_for("register"))

        flash(
            "Registration successful! You can now log in.",
            "success"
        )
        return redirect(url_for("login"))

    return render_template("register.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please fill in all fields.", "error")
            return redirect(url_for("login"))

        with get_db() as db:
            user = db.execute(
                """
                SELECT id, email FROM users
                WHERE email = ? AND password = ?
                """,
                (email, password)
            ).fetchone()

        if user:
            response = make_response(
                redirect(url_for("instagram"))
            )
            response.set_cookie("email", email)
            flash("Login successful!", "success")
            return response

        flash("Incorrect email or password.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


# Logout
@app.route("/logout")
def logout():
    response = make_response(redirect(url_for("login")))
    response.delete_cookie("email")
    flash("You have successfully logged out.", "success")
    return response


if __name__ == "__main__":
    app.run(debug=True)
