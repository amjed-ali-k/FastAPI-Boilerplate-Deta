from datetime import datetime, timedelta
from typing import Optional

import deta, hashlib, uuid
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from starlette import status

from models.user import UserInDB, User, UserCreate, UserActionsHistory, AccountDetails, UserEdit
from services.db.userDB import get_user_from_username_db, create_new_user_to_db, update_user_to_db, \
    get_user_from_id, update_password_to_db
from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY: str = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
EMAIL_RESET_TOKEN_EXPIRE_HOURS = settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(username: str) -> Optional[UserInDB]:
    user = await get_user_from_username_db(username)
    if user:
        return UserInDB(**user.dict())
    else:
        return None


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return User(**user.dict())


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = User(**payload)
        if user.username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def create_new_user(user: UserCreate) -> UserInDB:
    hashed_password = get_password_hash(user.password)
    user_in = UserInDB(hashed_password=hashed_password, **user.dict())
    user_in.key = str(uuid.uuid4())
    created_user = await create_new_user_to_db(user_in)

    return created_user


async def update_user_fields(updateuser: UserEdit, user: User) -> Optional[UserInDB]:
    userindb = await get_user_from_id(user.key)
    userindb.accounts.updatedAt = datetime.now().isoformat()
    useroutdb = await update_user_to_db(User(**updateuser.dict()), userindb)

    return useroutdb


async def update_user_password(new_password: str, user: User):
    hashed_password = get_password_hash(new_password)
    await update_password_to_db(hashed_password, user)
    return True


async def check_password_and_username(userinput, user: User):
    user_db = await get_user_from_id(user.key)
    if user.username != userinput.username:
        return False
    v = verify_password(userinput.password, user_db.hashed_password)
    return v if v else False


def send_email(email: str, subject: str, message: str):
    # TODO : Send Email
    deta.send_email(to=email, subject=subject, message=message)
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)


def generate_password_reset_token(username):
    delta = timedelta(hours=EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {
            "exp": exp,
            "nbf": now,
            "sub": 'reset',
            "username": username,
        },
        SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        assert decoded_token["sub"] == 'reset'
        return decoded_token["username"]
    except JWTError:
        return None


def reset_password(username: str, new_password: str):
    pass


# def send_reset_password_email(email_to: str, username: str, token: str):
#     project_name = config.PROJECT_NAME
#     subject = f"{project_name} - Password recovery for user {username}"
#     with open(Path(config.EMAIL_TEMPLATES_DIR) / "reset_password.html") as f:
#         template_str = f.read()
#     if hasattr(token, "decode"):
#         use_token = token.decode()
#     else:
#         use_token = token
#     server_host = config.SERVER_HOST
#     link = f"{server_host}/reset-password?token={use_token}"
#     send_email(
#         email_to=email_to,
#         subject_template=subject,
#         html_template=template_str,
#         environment={
#             "project_name": config.PROJECT_NAME,
#             "username": username,
#             "email": email_to,
#             "valid_hours": config.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
#             "link": link,
#         },
#     )
#
#
# def send_new_account_email(email_to: str, username: str, password: str):
#     project_name = config.PROJECT_NAME
#     subject = f"{project_name} - New account for user {username}"
#     with open(Path(config.EMAIL_TEMPLATES_DIR) / "new_account.html") as f:
#         template_str = f.read()
#     link = config.SERVER_HOST
#     send_email(
#         email_to=email_to,
#         subject_template=subject,
#         html_template=template_str,
#         environment={
#             "project_name": config.PROJECT_NAME,
#             "username": username,
#             "password": password,
#             "email": email_to,
#             "link": link,
#         },
#     )
# def send_email(email_to: str, subject_template="", html_template="", environment={}):
#     assert config.EMAILS_ENABLED, "no provided configuration for email variables"
#     message = emails.Message(
#         subject=JinjaTemplate(subject_template),
#         html=JinjaTemplate(html_template),
#         mail_from=(config.EMAILS_FROM_NAME, config.EMAILS_FROM_EMAIL),
#     )
#     smtp_options = {"host": config.SMTP_HOST, "port": config.SMTP_PORT}
#     if config.SMTP_TLS:
#         smtp_options["tls"] = True
#     if config.SMTP_USER:
#         smtp_options["user"] = config.SMTP_USER
#     if config.SMTP_PASSWORD:
#         smtp_options["password"] = config.SMTP_PASSWORD
#     response = message.send(to=email_to, render=environment, smtp=smtp_options)
#     logging.info(f"send email result: {response}")

def populate_fields(user: UserCreate) -> UserCreate:
    if not user.avatar:
        email = user.email.lower().strip()
        hash_object = hashlib.md5(email.encode())
        md5_hash = hash_object.hexdigest()
        user.avatar = f'https://www.gravatar.com/avatar/{md5_hash}?s=400&d=robohash'
    user.accounts = AccountDetails(createdAt=datetime.now().isoformat(), updatedAt=datetime.now().isoformat())
    return user
