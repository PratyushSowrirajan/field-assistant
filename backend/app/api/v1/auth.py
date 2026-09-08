from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_farmer
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import Farmer
from app.schemas.auth import FarmerOut, RegisterRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Farmer).filter(Farmer.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    farmer = Farmer(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
    )
    db.add(farmer)
    db.commit()
    db.refresh(farmer)

    token = create_access_token(str(farmer.id))
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    farmer = db.query(Farmer).filter(Farmer.email == form_data.username).first()
    if not farmer or not verify_password(form_data.password, farmer.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
        )
    token = create_access_token(str(farmer.id))
    return TokenResponse(access_token=token)


@router.get("/me", response_model=FarmerOut)
def me(farmer: Farmer = Depends(get_current_farmer)):
    return farmer
