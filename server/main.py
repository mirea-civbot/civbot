from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session
from typing import List, AsyncGenerator
import crud
import schemas
import models
from fastapi import status
import auth
from jose import JWTError, jwt
from app_config import settings
from LLM_model import LLMService

app = FastAPI(debug=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


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


@app.post("/register", response_model=schemas.UserResponse)
async def register(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    existing = await crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(400, "Email already registered")
    return await crud.create_user(db, user)



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
    # 1. Проверка совпадения dialog_id
    if payload.dialog_id != dialog_id:
        raise HTTPException(400, "dialog_id mismatch")

    # 2. Проверка прав доступа к диалогу
    dialog = await crud.get_dialog_by_id(db, dialog_id)
    if not dialog:
        raise HTTPException(404, "Dialog not found")
    if dialog.user_id != current_user.user_id:
        raise HTTPException(403, "Access denied")

    # 3. Сохраняем сообщение пользователя
    user_message = await crud.create_message(
        db, 
        msg_in=payload, 
        is_bot=False
    )

    # 4. Генерируем ответ бота
    model = LLMService()
    bot_response_text = await model.generate_response(
        user_input=user_message.text,
        history=await crud.get_messages_by_dialog(db, dialog_id)
    )

    # 5. Сохраняем ответ бота
    bot_message = await crud.create_message(
        db,
        msg_in=schemas.MessageCreate(
            text=bot_response_text,
            dialog_id=dialog_id
        ),
        is_bot=True
    )

    return bot_message


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


@app.put(
    "/dialogs/{dialog_id}/messages/{message_id}",
    response_model=schemas.MessageResponse
)
async def edit_message(
    dialog_id: int,
    message_id: int,
    payload: schemas.MessageCreate,
    current_user: models.User = Security(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if payload.dialog_id != dialog_id:
        raise HTTPException(status_code=400, detail="dialog_id mismatch")
    return await crud.update_message_text(
        db,
        message_id=message_id,
        new_text=payload.text,
        current_user_id=current_user.user_id
    )


@app.delete(
    "/dialogs/{dialog_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Not Found"}, 403: {"description": "Forbidden"}}
)
async def remove_dialog(
    dialog_id: int,
    current_user: models.User = Security(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await crud.delete_dialog(db, dialog_id, current_user.user_id)


@app.delete(
    "/dialogs/{dialogs_id}/messages/{messages_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Not Found"}, 403: {"description": "Forbidden"}}
)
async def delete_message(
    message_id: int,
    current_user: models.User = Security(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await crud.delete_message(message_id=message_id, db=db, current_user_id=current_user.user_id)
