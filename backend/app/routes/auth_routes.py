from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.auth_bearer import get_current_user, require_admin
from app.auth.jwt_handler import create_access_token
from app.auth.password_handler import hash_password, verify_password
from app.database.connection import get_db
from app.models.user import User
from app.schemas.user_schema import LoginRequest, TokenResponse, UserCreate, UserResponse, ChangePasswordRequest

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
	user = db.query(User).filter(User.email == data.email).first()

	if not user or not user.is_active or not verify_password(data.password, user.hashed_password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid email or password",
		)

	access_token = create_access_token(
		{
			"sub": user.email,
			"user_id": user.id,
			"role": user.role.value if hasattr(user.role, "value") else str(user.role),
			"full_name": user.full_name,
		}
	)

	return TokenResponse(
		access_token=access_token,
		user=UserResponse.model_validate(user),
	)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
	return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
	existing_user = db.query(User).filter(User.email == data.email).first()
	if existing_user:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="A user with this email already exists",
		)

	user = User(
		email=data.email,
		hashed_password=hash_password(data.password),
		full_name=data.full_name,
		role=data.role,
		is_active=True,
	)

	db.add(user)
	db.commit()
	db.refresh(user)
	return user


@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
	return db.query(User).order_by(User.id).all()


@router.post("/change-password")
def change_password(data: ChangePasswordRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
	if not verify_password(data.old_password, current_user.hashed_password):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect old password")
	
	current_user.hashed_password = hash_password(data.new_password)
	db.commit()
	return {"message": "Password updated successfully"}


@router.patch("/users/{id}/deactivate")
def deactivate_user(id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
	if id == current_user.id:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate your own account")
	user = db.query(User).filter(User.id == id).first()
	if not user:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
	
	user.is_active = False
	db.commit()
	return {"message": f"User {id} deactivated"}
