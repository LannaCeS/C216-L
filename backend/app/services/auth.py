import secrets


def credentials_match(
    email: str, password: str, expected_email: str, expected_password: str
) -> bool:
    return secrets.compare_digest(email, expected_email) and secrets.compare_digest(
        password, expected_password
    )
