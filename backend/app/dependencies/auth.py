from fastapi import Cookie, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
 
from app.core.security import decode_access_token
from app.database import get_db
from app.models import User

# tokenUrl just tells FastAPI's auto-docs where to send the login form;
# it doesn't affect how this dependency verifies tokens.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    user_id = decode_access_token(access_token or token) if (access_token or token) else None
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
 
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
 
    return user
