import os

# Secret key for signing tokens (Store securely in environment variables in production)
SECRET_KEY = os.getenv("SECRET_KEY", "my-super-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Mock user database (Replace or connect to your database/env variables)
USERS = {
    "admin": {
        "username": os.getenv("ADMIN_USER", "admin"),
        "password": os.getenv("ADMIN_PW", "admin"),
    }
}
