from fastapi import APIRouter, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.schemas.grade import GradeSettings
from app.schemas.user import LoginRequest
from app.services import grades as grade_service
from app.services import user as user_service

router = APIRouter()


@router.get("/home")
def home() -> HTMLResponse:
    return HTMLResponse(
        """
        <!doctype html>
        <html lang="en">
          <head><title>Home</title></head>
          <body>
            <h1>Welcome, """
        + user_service.DEMO_USERNAME
        + """</h1>
            <form id="grade-form">
              <label for="name">Name</label>
              <input id="name" name="name" type="text" required>
              <label for="grade">Grade</label>
              <input id="grade" name="grade" type="text" required>
              <button type="submit" name="method" value="POST">Add</button>
              <button type="submit" name="method" value="PATCH">Alter grade
              (PATCH)</button>
              <button type="submit" name="method" value="PUT">Replace grade
              (PUT)</button>
              <button id="find-grade" type="button">Find grade</button>
            </form>
            <button id="delete-grades" type="button">Delete all grades</button>
            <pre id="result"></pre>
            <form action="/logout" method="post">
              <button type="submit">Logout</button>
            </form>
            <script>
              document.getElementById("grade-form").addEventListener(
                "submit", async (event) => {
                event.preventDefault();
                const name = document.getElementById("name").value;
                const grade = document.getElementById("grade").value;
                const method = event.submitter.value;
                const response = await fetch("/settings/grade", {
                  method,
                  headers: {"Content-Type": "application/json"},
                  body: JSON.stringify({name, grade}),
                });
                const result = await response.json();
                document.getElementById("result").textContent = response.ok
                  ? JSON.stringify(result, null, 2)
                  : result.detail;
                }
              );

              document.getElementById("find-grade").addEventListener(
                "click", async () => {
                  const name = document.getElementById("name").value.trim();
                  const resultElement = document.getElementById("result");
                  if (!name) {
                    resultElement.textContent = "Enter a name first.";
                    return;
                  }

                  const response = await fetch(
                    "/settings/grade/" + encodeURIComponent(name)
                  );
                  const result = await response.json();
                  resultElement.textContent = response.ok
                    ? JSON.stringify(result, null, 2)
                    : result.detail;
                }
              );

              document.getElementById("delete-grades").addEventListener(
                "click", async () => {
                  const response = await fetch("/settings/grade", {
                    method: "DELETE",
                  });
                  const result = await response.json();
                  document.getElementById("result").textContent = result.message;
                }
              );
            </script>
          </body>
        </html>
        """
    )


@router.post("/")
def login(credentials: LoginRequest):
    """Demo-only login with hard-coded credentials."""
    if not user_service.authenticate(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    return {"message": "Login successful!", "username": credentials.username}


@router.get("/")
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


@router.post("/settings/grade")
def save_grade(settings: GradeSettings):
    """Create a new grade record."""
    try:
        return grade_service.create_grade(settings.name, settings.grade)
    except grade_service.GradeAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"A grade for {settings.name} already exists. "
                "Use PATCH or PUT to change it."
            ),
        ) from None


@router.get("/settings/grade")
def list_grades():
    """Return all grades saved in the JSON file."""
    return grade_service.list_grades()


@router.get("/settings/grade/{name}")
def get_grade(name: str):
    """Return the grade for the first matching name."""
    try:
        return grade_service.get_grade(name)
    except grade_service.GradeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grade for {name} not found.",
        ) from None


@router.delete("/settings/grade")
def delete_grades():
    """Delete all grades saved in the JSON file."""
    grade_service.delete_all_grades()
    return {"message": "All grades deleted."}


@router.patch("/settings/grade")
def update_grade(settings: GradeSettings):
    """Update only the grade for the first matching name."""
    try:
        return grade_service.update_grade(settings.name, settings.grade)
    except grade_service.GradeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grade for {settings.name} not found.",
        ) from None


@router.put("/settings/grade")
def replace_grade(settings: GradeSettings):
    """Replace the full record for the first matching name."""
    try:
        return grade_service.replace_grade(settings.name, settings.grade)
    except grade_service.GradeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grade for {settings.name} not found.",
        ) from None


@router.post("/logout")
def logout() -> RedirectResponse:
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
