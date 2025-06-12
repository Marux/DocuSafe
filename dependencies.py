from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from fastapi import Depends, HTTPException, status
from auth import SECRET_KEY, ALGORITHM  # Asegúrate de que estos estén definidos en auth.py

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        raise credentials_exception