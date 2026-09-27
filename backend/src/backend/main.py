from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

app = FastAPI()


DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo-password"


class LoginRequest(BaseModel):
    username: str
    password: str


class EmailSettings(BaseModel):
    email: str


@app.get("/home")
def home() -> HTMLResponse:
    return HTMLResponse(
        """
        <!doctype html>
        <html lang="en">
          <head><title>Home</title></head>
          <body>
            <h1>Welcome, """
        + DEMO_USERNAME
        + """</h1>
            <form id="email-form">
              <label for="email">Email</label>
              <input id="email" name="email" type="email" required>
              <button type="submit">Save email</button>
            </form>
            <pre id="result"></pre>
            <form action="/logout" method="post">
              <button type="submit">Logout</button>
            </form>
            <script>
              document.getElementById("email-form").addEventListener(
                "submit", async (event) => {
                event.preventDefault();
                const email = document.getElementById("email").value;
                const response = await fetch("/settings/email", {
                  method: "POST",
                  headers: {"Content-Type": "application/json"},
                  body: JSON.stringify({email}),
                });
                document.getElementById("result").textContent = JSON.stringify(
                  await response.json(), null, 2
                );
                }
              );
            </script>
          </body>
        </html>
        """
    )


@app.post("/")
def login(credentials: LoginRequest):
    """Demo-only login with hard-coded credentials."""
    if credentials.username != DEMO_USERNAME or credentials.password != DEMO_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    return {"message": "Login successful!", "username": credentials.username}


@app.get("/")
def login_page() -> HTMLResponse:
    return HTMLResponse(
        """
       <form id="login-form">
            <label for="username">Username</label>
            <input id="username" type="text" required>

            <label for="password">Password</label>
            <input id="password" type="password" required>

            <button type="submit">Login</button>
        </form>

        <p id="error"></p>

        <script>
        document.getElementById("login-form").addEventListener(
            "submit",
            async (event) => {
            event.preventDefault();

            const response = await fetch("/", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                username: document.getElementById("username").value,
                password: document.getElementById("password").value,
                }),
            });

            if (response.ok) {
                window.location.href = "/home";
                return;
            }

            const error = await response.json();
            document.getElementById("error").textContent = error.detail;
            }
        );
        </script>
"""
    )


@app.post("/settings/email")
def save_email(settings: EmailSettings):
    """Demo-only endpoint: echoes the fixed user and submitted email."""
    return {"username": DEMO_USERNAME, "email": settings.email}


@app.post("/logout")
def logout() -> RedirectResponse:
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
