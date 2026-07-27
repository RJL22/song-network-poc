from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
 
from app.core.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserOut
 
router = APIRouter(prefix="/auth", tags=["auth"])
 
 
@router.post("/signup", response_model=UserOut)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already taken")
 
    user = User(
        username=payload.username,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
 
 
@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
 
    # Deliberately the same error for "no such user" and "wrong password" —
    # distinguishing them lets an attacker enumerate valid usernames.
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
 
    token = create_access_token(user_id=user.id)
    return Token(access_token=token)