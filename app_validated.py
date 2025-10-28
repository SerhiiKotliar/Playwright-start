from flask import Flask, request, render_template_string, redirect, url_for, session
import re

app = Flask(__name__)
app.secret_key = "dev-key"

# Простая in-memory "база"
USERS = {}

REGISTER_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Register</title>
</head>
<body>
  <h2>Register</h2>
  <form method="post" action="/register">
    <label for="username">Username</label><br>
    <input id="username" name="username" type="text" value="{{ username or '' }}" required><br>
    {% if errors.get('username') %}
      <p style="color:red">{{ errors['username'] }}</p>
    {% endif %}

    <label for="password">Password</label><br>
    <input id="password" name="password" type="password" required><br>
    {% if errors.get('password') %}
      <p style="color:red">{{ errors['password'] }}</p>
    {% endif %}

    <button type="submit">Register</button>
  </form>

  <p><a href="/login">Already registered? Login</a></p>
</body>
</html>
"""

LOGIN_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Login</title>
</head>
<body>
  <h2>Login</h2>
  <form method="post" action="/login">
    <label for="username">Username</label><br>
    <input id="username" name="username" type="text" value="{{ username or '' }}" required><br>
    {% if errors.get('username') %}
      <p style="color:red">{{ errors['username'] }}</p>
    {% endif %}

    <label for="password">Password</label><br>
    <input id="password" name="password" type="password" required><br>
    {% if errors.get('password') %}
      <p style="color:red">{{ errors['password'] }}</p>
    {% endif %}

    <button type="submit">Login</button>
  </form>

  <p><a href="/register">Create new account</a></p>
</body>
</html>
"""

PROFILE_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Profile</title>
</head>
<body>
  <h2>Welcome, {{ username }}!</h2>
  <p><a href="/logout">Logout</a></p>
</body>
</html>
"""


# --- Проверки ---
def validate_username(username):
    """4–12 символов, только латиница и цифры, хотя бы 1 буква"""
    return bool(re.fullmatch(r"(?=.*[A-Za-z])[A-Za-z0-9]{4,12}", username))


def validate_password(password):
    """8–25 символов, хотя бы 1 буква и 1 цифра"""
    return bool(re.fullmatch(r"(?=.*[A-Za-z])(?=.*\\d)[A-Za-z0-9]{8,25}", password))


# --- Маршруты ---
@app.route("/")
def index():
    return '<p><a href="/register">Register</a> | <a href="/login">Login</a></p>'


@app.route("/register", methods=["GET", "POST"])
def register():
    errors = {}
    username = ""

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        # Проверка ошибок
        if username in USERS:
            errors["username"] = "User exists"
        elif not validate_username(username):
            errors["username"] = "Invalid username (4–12 latin letters/numbers, no Cyrillic, no spaces)"
        elif not validate_password(password):
            errors["password"] = "Invalid password (8–25 chars, must have letters & digits, no Cyrillic, no spaces)"
        else:
            # Успешная регистрация
            USERS[username] = password
            session["username"] = username
            session.pop("last_error", None)
            return redirect(url_for("profile"))

        # Сохраняем ошибки в сессию и делаем redirect
        session["last_error"] = errors
        session["last_username"] = username
        return redirect(url_for("register"))

    # --- GET ---
    errors = session.pop("last_error", {})
    username = session.pop("last_username", "")
    return render_template_string(REGISTER_HTML, errors=errors, username=username)


@app.route("/login", methods=["GET", "POST"])
def login():
    errors = {}
    username = ""

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if username not in USERS:
            errors["username"] = "User does not exist"
        elif USERS.get(username) != password:
            errors["password"] = "Invalid password"

        if not errors:
            session["username"] = username
            return redirect(url_for("profile"))

    return render_template_string(LOGIN_HTML, errors=errors, username=username)


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
