from typing import List

from db.crud.menus import get_menus, get_menu_by_name, get_menu, get_menu_by_title, get_menu_by_path
from db.crud.users import get_users, get_users_by_ids
from db.database import get_db, async_db_session
from libs.fastapi_babel import _

class UserService:
    async def get_user_list(self, skip: int = 0, limit: int = 100):
        async with async_db_session() as db:
            users = get_users(db, skip=skip, limit=limit)
            user_list = []
            for user in users:
                user_list.append(
                    {"id": user.id, "email": user.email}
                )
            return user_list

    async def get_user_name_by_id_list(self, user_ids=List[int]):
        async with async_db_session() as db:
            users = get_users_by_ids(user_ids=user_ids, db=db)
            # print(users)
            user_name_list = []
            for user in users:
                # user_list.append(
                #     {"id": user.id, "email": user.email}
                # )
                user_name_list.append(user.email)
            return user_name_list

    async def get_user_email_id_map(self):
        async with async_db_session() as db:
            users = get_users(db=db)
            user_email_id_map = {}
            for user in users:
                user_email_id_map[user.id] = user.email
            return user_email_id_map

