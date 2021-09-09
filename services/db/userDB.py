from typing import Optional, List

from deta import Deta
from config import settings

from models.user import User, UserInDB, UserActionsHistory

deta = Deta(settings.DETA_BASE_KEY)  # configure your Deta project
users_db = deta.Base('users')
user_history_db = deta.Base('UserHistory')


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


async def get_user_history(username: str, all: bool = False) -> Optional[List[UserActionsHistory]]:
    if all:
        v = user_history_db.fetch()
    else:
        v = user_history_db.fetch({'username': username})
    if v.count == 0:
        return None
    r: List = []
    for k in v.items:
        r.append(UserActionsHistory(**k))
    return r


async def create_user_history(user_history: UserActionsHistory) -> UserActionsHistory:
    return user_history_db.insert(user_history.dict())
