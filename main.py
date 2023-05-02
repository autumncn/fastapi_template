import os

from fastapi import FastAPI
import uvicorn

from core.config import settings
from core.i18n import configs, babel
from db.redis import init_redis_pool
from logs.logger import logger
from register.cors import register_cors
from register.exception import register_exception
from register.middleware import register_middleware
from register.mount import register_mount
from register.routers import register_router
from service.menuService import get_menu_list

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

register_mount(app)  # 挂载静态文件
register_exception(app)  # 注册捕获全局异常
register_router(app)  # 注册路由
register_middleware(app)  # 注册请求响应拦截
register_cors(app)  # 注册跨域请求

@app.on_event("startup")
async def startup():
    babel.locale = 'en'
    app.state.redis = await init_redis_pool()  # redis

@app.on_event("shutdown")
async def shutdown():
    await app.state.redis.close()  # 关闭 redis

if __name__ == '__main__':
    os.system(f"figlet -f slant {settings.PROJECT_NAME}")
    uvicorn.run(app='main:app', host="0.0.0.0", port=8080, reload=True, workers=5, lifespan="on")




