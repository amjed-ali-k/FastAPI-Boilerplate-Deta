from typing import Optional, List

from deta import Deta
from config import settings

from models.user import User, UserInDB

# configure your Deta project
deta = Deta(settings.DETA_BASE_KEY if 'DETA_BASE_KEY' in settings else None)
users_db = deta.Base('users')


async def get_user_from_id(key: str) -> Optional[UserInDB]:
    user = users_db.get(str(key))
    if user:
        return UserInDB(**user)
    else:
        return None


async def get_user_from_username_db(username: str) -> Optional[UserInDB]:
    fetch = users_db.fetch({'username': username}, limit=1)
    if fetch.count > 0:
        user = fetch.items[0]
        return UserInDB(**user)
    else:
        return None


async def create_new_user_to_db(user: UserInDB) -> UserInDB:
    user = users_db.insert(user.dict())
    return UserInDB(**user)


async def update_user_to_db(user: User, userindb: UserInDB) -> Optional[UserInDB]:
    var = userindb.dict()
    var.update(**{k: v for k, v in user.dict().items() if v is not None})
    var1 = UserInDB(**var)
    userdb = users_db.put(var1.dict())
    if userdb:
        return UserInDB(**userdb)
    else:
        return None


async def update_password_to_db(hashed_password, userindb: User) -> UserInDB:
    v = userindb.dict()
    v['hashed_password'] = hashed_password
    return users_db.put(v, key=userindb.key)
