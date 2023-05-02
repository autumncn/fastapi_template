from typing import List

from db.crud.menus import get_menus, get_menu_by_name, get_menu, get_menu_by_title, get_menu_by_path
from db.crud.users import get_users, get_users_by_ids
from db.database import get_db
from libs.fastapi_babel import _

def get_user_list(skip: int = 0, limit: int = 100, db=next(get_db())):
    users = get_users(db, skip=skip, limit=limit)
    user_list = []
    for user in users:
        user_list.append(
            {"id": user.id, "email": user.email}
        )
    return user_list

def get_user_name_by_id_list(user_ids=List[int], db=next(get_db())):
    users = get_users_by_ids(user_ids=user_ids, db=db)
    # print(users)
    user_name_list = []
    for user in users:
        # user_list.append(
        #     {"id": user.id, "email": user.email}
        # )
        user_name_list.append(user.email)
    return user_name_list

def get_user_email_id_map():
    users = get_users(db=next(get_db()))
    user_email_id_map = {}
    for user in users:
        user_email_id_map[user.id] = user.email
    return user_email_id_map

if __name__ == '__main__':
    # get_user_name_by_id_list([1,])
    users = get_user_email_id_map()
    # print(users.get(1))
