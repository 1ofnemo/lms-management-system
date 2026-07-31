from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try: 
        payload = decode_access_token(token)
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")
    return {"id": int(payload["sub"]), "role": payload["role"]}

def require_roles(*roles: str):
    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] not in roles:
            raise HTTPException(403, "Not authorized")
        return user
    return checker

def ensure_can_view_student(user: dict, student_id: int) -> None:
    if user["role"] == "student" and user["id"] != student_id:
        raise HTTPException(403, "Not authorized")

