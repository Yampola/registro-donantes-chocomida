from typing import Optional

from sqlalchemy.orm import Session

from . import auth, models, schemas


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(
    db: Session, user: schemas.UserCreate, role: models.RoleEnum = models.RoleEnum.usuario
) -> models.User:
    db_user = models.User(
        username=user.username,
        hashed_password=auth.hash_password(user.password),
        role=role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_donor(db: Session, donor: schemas.DonorCreate, created_by: int) -> models.Donor:
    db_donor = models.Donor(**donor.model_dump(), created_by=created_by)
    db.add(db_donor)
    db.commit()
    db.refresh(db_donor)
    return db_donor


def get_donors(db: Session, skip: int = 0, limit: int = 100) -> list[models.Donor]:
    return db.query(models.Donor).offset(skip).limit(limit).all()


def get_donor(db: Session, donor_id: int) -> Optional[models.Donor]:
    return db.query(models.Donor).filter(models.Donor.id == donor_id).first()


def delete_donor(db: Session, donor_id: int) -> bool:
    donor = get_donor(db, donor_id)
    if not donor:
        return False
    db.delete(donor)
    db.commit()
    return True
