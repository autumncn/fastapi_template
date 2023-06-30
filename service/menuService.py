from typing import List

from db.crud.menus import get_menus, get_menu_by_name, get_menu, get_menu_by_title, get_menu_by_path, get_menus_by_ids
from db.crud.permissions import get_permission
from db.crud.users import get_user_by_email
from db.database import get_db, async_db_session
from libs.fastapi_babel import _


class MenuService:
    async def get_menu_list(self, skip: int = 0, limit: int = 100):
        async with async_db_session() as db:
            menus = await get_menus(db, skip=skip, limit=limit)

            menu_level_1_list = []
            menu_level_2_list = []
            menu_level_3_list = []
            menu_level_4_list = []
            for menu in menus:
                menu_dict = {
                    'id': menu.id,
                    'name': menu.name,
                    'path': menu.path,
                    'parent_id': menu.parent_id,
                    'icon': menu.icon,
                    'redirect': menu.redirect,
                    'title': _(menu.title),
                    'hidden': menu.hidden,
                    'type': menu.type,
                    'component': menu.component,
                    'sort': menu.sort,
                    'level': menu.level,
                    'status': menu.status
                }
                if menu.level < 10:
                    menu_level_1_list.append(menu_dict)
                elif menu.level < 100 and menu.level >= 10:
                    menu_level_2_list.append(menu_dict)
                elif menu.level < 1000 and menu.level >= 100:
                    menu_level_3_list.append(menu_dict)
                elif menu.level < 10000 and menu.level >= 1000:
                    menu_level_4_list.append(menu_dict)

            new_menu_level_3_list = []
            for menu_level_3 in menu_level_3_list:
                menu_level_4_list_temp = []
                for menu_level_4 in menu_level_4_list:
                    if menu_level_4['parent_id'] == menu_level_3['id']:
                        menu_level_4_list_temp.append(menu_level_4)
                menu_level_3['children'] = menu_level_4_list_temp
                new_menu_level_3_list.append(menu_level_3)

            new_menu_level_2_list = []
            # new_menu_level_2_dict = {}
            for menu_level_2 in menu_level_2_list:
                menu_level_3_list_temp = []
                for menu_level_3 in menu_level_3_list:
                    if menu_level_3['parent_id'] == menu_level_2['id']:
                        menu_level_3_list_temp.append(menu_level_3)
                menu_level_2['children'] = menu_level_3_list_temp
                new_menu_level_2_list.append(menu_level_2)
            # print(new_menu_level_2_list)

            new_menu_level_1_list = []
            for menu_level_1 in menu_level_1_list:
                menu_level_2_list_temp = []
                for menu_level_2 in new_menu_level_2_list:
                    if menu_level_2['parent_id'] == menu_level_1['id']:
                        menu_level_2_list_temp.append(menu_level_2)
                menu_level_1['children'] = menu_level_2_list_temp
                new_menu_level_1_list.append(menu_level_1)
            # print(new_menu_level_1_list)

            return new_menu_level_1_list


    async def get_menu_list_by_user_permission(self, user_login_email: str, skip: int = 0, limit: int = 100):
        async with async_db_session() as db:
            login_user = get_user_by_email(user_login_email, db)
            user_role_id = login_user.user_role_id
            user_permission = get_permission(db, user_role_id)
            user_menu_ids = (user_permission.menu_ids).split(',')
            menus = get_menus_by_ids(db, user_menu_ids)
            # menus = get_menus(db, skip=skip, limit=limit)

            menu_level_1_list = []
            menu_level_2_list = []
            menu_level_3_list = []
            menu_level_4_list = []
            for menu in menus:
                # print(_(menu.title))
                menu_dict = {
                    'id': menu.id,
                    'name': menu.name,
                    'path': menu.path,
                    'parent_id': menu.parent_id,
                    'icon': menu.icon,
                    'redirect': menu.redirect,
                    'title': _(menu.title),
                    'hidden': menu.hidden,
                    'type': menu.type,
                    'component': menu.component,
                    'sort': menu.sort,
                    'level': menu.level,
                    'status': menu.status
                }
                if menu.level < 10:
                    menu_level_1_list.append(menu_dict)
                elif menu.level < 100 and menu.level >= 10:
                    menu_level_2_list.append(menu_dict)
                elif menu.level < 1000 and menu.level >= 100:
                    menu_level_3_list.append(menu_dict)
                elif menu.level < 10000 and menu.level >= 1000:
                    menu_level_4_list.append(menu_dict)

            new_menu_level_3_list = []
            for menu_level_3 in menu_level_3_list:
                menu_level_4_list_temp = []
                for menu_level_4 in menu_level_4_list:
                    if menu_level_4['parent_id'] == menu_level_3['id']:
                        menu_level_4_list_temp.append(menu_level_4)
                menu_level_3['children'] = menu_level_4_list_temp
                new_menu_level_3_list.append(menu_level_3)

            new_menu_level_2_list = []
            # new_menu_level_2_dict = {}
            for menu_level_2 in menu_level_2_list:
                menu_level_3_list_temp = []
                for menu_level_3 in menu_level_3_list:
                    if menu_level_3['parent_id'] == menu_level_2['id']:
                        menu_level_3_list_temp.append(menu_level_3)
                menu_level_2['children'] = menu_level_3_list_temp
                new_menu_level_2_list.append(menu_level_2)
            # print(new_menu_level_2_list)

            new_menu_level_1_list = []
            for menu_level_1 in menu_level_1_list:
                menu_level_2_list_temp = []
                for menu_level_2 in new_menu_level_2_list:
                    if menu_level_2['parent_id'] == menu_level_1['id']:
                        menu_level_2_list_temp.append(menu_level_2)
                menu_level_1['children'] = menu_level_2_list_temp
                new_menu_level_1_list.append(menu_level_1)
            # print(new_menu_level_1_list)

            return new_menu_level_1_list

    async def get_menu_path_by_user_permission(self, user_login_email: str):
        async with async_db_session() as db:
            login_user = get_user_by_email(user_login_email, db)
            user_role_id = login_user.user_role_id
            user_permission = get_permission(db, user_role_id)
            user_menu_ids = (user_permission.menu_ids).split(',')
            menus = get_menus_by_ids(db, user_menu_ids)
            menu_path_list = []
            for menu in menus:
                menu_path_list.append(menu.path)

            return menu_path_list


    async def find_parent_menu(self, menu_path: str):
        async with async_db_session() as db:
            menu_dict = {}
            find_menu = get_menu_by_path(db, menu_path)
            # print(find_menu)
            try:
                menu_level = find_menu.level
                if menu_level < 10:
                    menu_dict['top_menu'] = find_menu.path
                    return menu_dict
                elif menu_level < 100 and menu_level >= 10:
                    menu_parent_id = find_menu.parent_id
                    menu_dict['grand_parent_menu'] = find_menu.path
                    parent_menu = get_menu(db, menu_parent_id)
                    menu_dict['top_menu'] = parent_menu.path
                    return menu_dict
                elif menu_level < 1000 and menu_level >= 100:
                    menu_parent_id = find_menu.parent_id
                    menu_dict['parent_menu'] = find_menu.path
                    parent_menu = get_menu(db, menu_parent_id)
                    menu_dict['grand_parent_menu'] = parent_menu.path
                    grand_parent_menu_id = parent_menu.parent_id
                    grand_parent_menu = get_menu(db, grand_parent_menu_id)
                    menu_dict['top_menu'] = grand_parent_menu.path
                    return menu_dict
                elif menu_level < 10000 and menu_level >= 1000:
                    menu_parent_id = find_menu.parent_id
                    menu_dict['menu'] = find_menu.path
                    parent_menu = get_menu(db, menu_parent_id)
                    menu_dict['parent_menu'] = parent_menu.path
                    grand_parent_menu_id = parent_menu.parent_id
                    grand_parent_menu = get_menu(db, grand_parent_menu_id)
                    menu_dict['grand_parent_menu'] = grand_parent_menu.path
                    top_menu_id = grand_parent_menu.parent_id
                    top_menu = get_menu(db, top_menu_id)
                    menu_dict['top_menu'] = top_menu.path
                    return menu_dict
                else:
                    return menu_dict
            except Exception as e:
                return menu_dict


    async def menu_list_id_name(self, skip: int = 0, limit: int = 100):
        async with async_db_session() as db:
            menus = get_menus(db, skip=skip, limit=limit)
            menu_list = []
            for menu in menus:
                menu_dict = {
                    'id': menu.id,
                    'name': menu.name,
                    'title': _(menu.title)
                }
                menu_list.append(menu_dict)

            return menu_list

    async def get_menu_name_by_id_list(self, menu_ids=List[int]):
        async with async_db_session() as db:
            menus = get_menus_by_ids(menu_ids=menu_ids, db=db)
            # print(users)
            menu_name_list = []
            for menu in menus:
                # user_list.append(
                #     {"id": user.id, "email": user.email}
                # )
                menu_name_list.append(_(menu.title))
            return menu_name_list