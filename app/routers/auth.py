from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token, get_current_user
from app.services.user import authenticate_user, create_user
from app.schemas.user import UserCreate, Token, UserResponse, UserLogin

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db=db, user=user)

@router.post("/login", response_model=Token)
def login(form_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(response: Response, current_user: UserResponse= Depends(get_current_user)):
    # In a real implementation, you might want to blacklist the token
    # For a simple implementation, we'll just clear the cookie
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: UserResponse = Depends(get_current_user)):
    return current_user