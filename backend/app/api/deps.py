import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models.farm import Farm
from app.models.field import Field
from app.models.rover import Rover
from app.models.user import Farmer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
device_bearer = HTTPBearer(auto_error=False)


def get_current_farmer(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Farmer:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exception
        farmer_id = payload.get("sub")
    except JWTError:
        raise credentials_exception

    farmer = db.get(Farmer, uuid.UUID(farmer_id))
    if farmer is None:
        raise credentials_exception
    return farmer


def get_current_rover(
    creds: HTTPAuthorizationCredentials | None = Depends(device_bearer),
    db: Session = Depends(get_db),
) -> Rover:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid device credentials"
    )
    if creds is None:
        raise unauthorized
    try:
        payload = decode_token(creds.credentials)
        if payload.get("type") != "device":
            raise unauthorized
        device_id = payload.get("sub")
    except JWTError:
        raise unauthorized

    rover = db.query(Rover).filter(Rover.device_id == device_id).first()
    if rover is None:
        raise unauthorized
    return rover


def get_owned_farm(farm_id: uuid.UUID, farmer: Farmer = Depends(get_current_farmer), db: Session = Depends(get_db)) -> Farm:
    farm = db.get(Farm, farm_id)
    if farm is None or farm.farmer_id != farmer.id:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm


def get_owned_field(field_id: uuid.UUID, farmer: Farmer = Depends(get_current_farmer), db: Session = Depends(get_db)) -> Field:
    field = db.get(Field, field_id)
    if field is None:
        raise HTTPException(status_code=404, detail="Field not found")
    farm = db.get(Farm, field.farm_id)
    if farm is None or farm.farmer_id != farmer.id:
        raise HTTPException(status_code=404, detail="Field not found")
    return field
