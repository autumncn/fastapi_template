# -*- coding: utf-8 -*-
from fastapi import FastAPI, Security
from apis import api
from apis.common import home, items, users, login, ws, stables, tasks, nodes, menus, dictionary, permissions, userLoginLogs, tools


def register_router(app: FastAPI):
    """ 注册路由 """
    app.include_router(home.router, tags=["home"], prefix="")
    app.include_router(items.router, tags=["items"], prefix="/items")
    app.include_router(users.router, tags=["users"], prefix="/users")
    app.include_router(login.router, tags=["login"], prefix="")
    app.include_router(ws.router, tags=["ws"], prefix="/ws")
    app.include_router(stables.router, tags=["stables"], prefix="/stables")
    app.include_router(tasks.router, tags=["tasks"], prefix="/tasks")
    app.include_router(nodes.router, tags=["nodes"], prefix="/nodes")
    app.include_router(menus.router, tags=["menus"], prefix="/menus")
    app.include_router(dictionary.router, tags=["dictionary"], prefix="/dictionary")
    app.include_router(permissions.router, tags=["permissions"], prefix="/permissions")
    app.include_router(userLoginLogs.router, tags=["access"], prefix="/access")
    app.include_router(tools.router, tags=["tools"], prefix="/tools")

    # 权限(权限在每个接口上)
    app.include_router(api.router, tags=["api"], prefix="/api")
