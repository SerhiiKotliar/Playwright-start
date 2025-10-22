# app_validated.py
from flask import Flask, request, render_template_string, redirect, url_for, session
import re

app = Flask(__name__)
app.secret_key = "dev-key"

# Простая in-memory "база"
USERS = {}

REGISTER_HTML = """
<!doctype html>
<title>Register</title>
<h2>Register</h2>
<form method="post" action="/register">
  <label>Username <input name="username" required></label><br>
  <label>Password <input name="password" type="password" required></label><br>
  <button type="submit">Register</button>
</form>
{% if error %}<p style="color:red">{{ error }}</p>{% endif %}
"""

LOGIN_HTML = """
<!doctype html>
<title>Login</title>
<h2>Login</h2>
<form method="post" action="/login">
  <label>Username <input name="username" required></label><br>
  <label>Password <input name="password" type="password" required></label><br>
  <button type="submit">Login</button>
</form>
{% if error %}<p style="color:red">{{ error }}</p>{% endif %}
"""

PROFILE_HTML = """
<!doctype html>
<title>Profile</title>
<h2>Profile</h2>
<p>Welcome {{ username }}!</p>
<a href="/logout">Logout</a>
"""

def validate_username(username):
    """Только буквы и цифры, длина 4–12"""
    if not re.match(r"^[A-Za-z0-9]{4,12}$", username):
        return False
    return True

def validate_password(password):
    """Минимум 8 символов, хотя бы одна буква и одна цифра"""
    if len(password) < 8:
        return False
    if not re.search(r"[A-Za-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True

@app.route("/")
def index():
    return '<p><a href="/register">Register</a> | <a href="/login">Login</a></p>'

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        u = request.form["username"].strip()
        p = request.form["password"]

        if u in USERS:
            error = "User exists"
        elif not validate_username(u):
            error = "Invalid username (4-12 letters/numbers)"
        elif not validate_password(p):
            error = "Invalid password (min 8 chars, at least 1 letter and 1 digit)"
        else:
            USERS[u] = p
            session["username"] = u
            return redirect(url_for("profile"))

    return render_template_string(REGISTER_HTML, error=error)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form["username"].strip()
        p = request.form["password"]
        if USERS.get(u) == p:
            session["username"] = u
            return redirect(url_for("profile"))
        error = "Invalid username or password"
    return render_template_string(LOGIN_HTML, error=error)

@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template_string(PROFILE_HTML, username=session["username"])

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
