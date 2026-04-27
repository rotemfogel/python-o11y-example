import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas import user_schemas
from app.db import models
from app.db.database import get_db

router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=user_schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: user_schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.user_name == payload.user_name).first():
        logger.warning("create_user failed: username already exists", extra={"user_name": payload.user_name})
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    user = models.User(user_name=payload.user_name, password=payload.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("create_user succeeded", extra={"user_name": user.user_name, "user_id": user.id})
    return user


@router.delete("/{user_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_name: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_name == user_name).first()
    if not user:
        logger.warning("delete_user failed: user not found", extra={"user_name": user_name})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    logger.info("delete_user succeeded", extra={"user_name": user_name})


@router.post("/authenticate", status_code=status.HTTP_200_OK)
def authenticate(payload: user_schemas.AuthRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_name == payload.user_name).first()
    if not user or user.password != payload.password:
        logger.warning("authenticate failed: invalid credentials", extra={"user_name": payload.user_name})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    logger.info("authenticate succeeded", extra={"user_name": payload.user_name})
    return {"authenticated": True}


@router.put("/{user_name}/password", status_code=status.HTTP_200_OK)
def change_password(user_name: str, payload: user_schemas.ChangePasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_name == user_name).first()
    if not user:
        logger.warning("change_password failed: user not found", extra={"user_name": user_name})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if payload.current_password != user.password:
        logger.warning("change_password failed: current password incorrect", extra={"user_name": user_name})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")
    user.password = payload.new_password
    db.commit()
    logger.info("change_password succeeded", extra={"user_name": user_name})
    return {"message": "Password updated"}
