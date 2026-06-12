import jwt
from jose import jwt as jose_jwt

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

# Paste a token here from previous output if needed, or I'll just use a command to pass it
import sys
token = sys.argv[1]

try:
    payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print(payload)
except Exception as e:
    print(f"Error: {e}")
