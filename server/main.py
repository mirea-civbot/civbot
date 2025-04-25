from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session
from typing import List, AsyncGenerator
import crud, schemas, models, auth
from jose import JWTError, jwt
from config import settings

app = FastAPI(debug=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Dependency: асинхронная сессия БД
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if not email:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await crud.get_user_by_email(db, email)
    if not user:
        raise credentials_exception
    return user

# Регистрация
@app.post("/register", response_model=schemas.UserResponse)
async def register(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    existing = await crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(400, "Email already registered")
    return await crud.create_user(db, user)

# Логин -> выдача JWT
@app.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await crud.get_user_by_name(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    token = auth.create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

# Создать диалог (авторизованный пользователь)
@app.post(
    "/dialogs",
    response_model=schemas.DialogResponse,
)
async def create_dialog(
    payload: schemas.DialogCreate,
    current_user: models.User = Security(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await crud.create_dialog(db, current_user.user_id, payload.name)

# Добавить сообщение к диалогу
@app.post(
    "/dialogs/{dialog_id}/messages",
    response_model=schemas.MessageResponse,
)
async def create_message_in_dialog(
    dialog_id: int,
    payload: schemas.MessageCreate,
    current_user: models.User = Security(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if payload.dialog_id != dialog_id:
        raise HTTPException(400, "dialog_id mismatch")
    # можно проверить, что dialog.user_id == current_user.user_id
    return await crud.create_message(db, payload)

# Получить все сообщения в диалоге
@app.get(
    "/dialogs/{dialog_id}/messages",
    response_model=List[schemas.MessageResponse],
)
async def read_messages_in_dialog(
    dialog_id: int,
    current_user: models.User = Security(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_messages_by_dialog(db, dialog_id)

# Получить все диалоги пользователя
@app.get(
    "/dialogs",
    response_model=List[schemas.DialogResponse],
)
async def read_dialogs_for_user(
    current_user: models.User = Security(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_dialogs_by_user(db, current_user.user_id)

# Получить все сообщения пользователя
@app.get(
    "/users/me/messages",
    response_model=List[schemas.MessageResponse],
    tags=["messages"]
)
async def read_messages_for_current_user(
    current_user: models.User = Security(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_messages_by_user(db, current_user.user_id)
