DEMO_USERNAME = "professor"
DEMO_PASSWORD = "password"


def authenticate(username: str, password: str) -> bool:
    """Validate the demo user's credentials."""
    return username == DEMO_USERNAME and password == DEMO_PASSWORD
