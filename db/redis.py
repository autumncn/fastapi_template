# redis 链接
import asyncio
import json
from typing import Union
from aioredis import Redis
from starlette.requests import Request
from core.config import settings


class MyRedis(Redis):
    """ 继承Redis,并添加自己的方法 """
    # async def get_keys(self):
    #     """ 获取所有的key """
    #     return await self.keys("*")

    async def get_keys(self, pattern: str):
        """ 获取所有关于pattern的key """
        return await self.keys(pattern)

    async def get_values(self):
        """ 获取所有的value """
        return await self.mget(await self.get_keys())

    async def get_all(self):
        """ 获取所有的key和value """
        return await self.mget(await self.get_keys(), await self.get_values())

    async def get_value_by_key(self, key: str):
        """ 根据key获取value """
        return await self.get(key)

    async def save_value_by_key(self, key: str, value: str):
        """ 根据key保存value """
        return await self.set(key, value)

    async def list_loads(self, key: str, num: int = -1) -> list:
        """
        将列表字符串转为对象

        :param key: 列表的key
        :param num: 最大长度(默认值 0-全部)
        :return: 列表对象
        """
        todo_list = await self.lrange(key, 0, (num - 1) if num > -1 else num)
        return [json.loads(todo) for todo in todo_list]

    async def cus_lpush(self, key: str, value: Union[str, list, dict]):
        """
        向列表右侧插入数据

        :param key: 列表的key
        :param value: 插入的值
        """
        text = json.dumps(value)
        await self.lpush(key, text)

    async def get_list_by_index(self, key: str, id: int) -> object:
        """
        根据索引得到列表值

        :param key: 列表的值
        :param id: 索引值
        :return:
        """
        value = await self.lindex(key, id)
        return json.loads(value)


# 参考: https://github.com/grillazz/fastapi-redis/tree/main/app
async def init_redis_pool() -> MyRedis:
    """ 连接redis """
    redis = await MyRedis.from_url(url=settings.REDIS_URI, encoding=settings.GLOBAL_ENCODING, decode_responses=True)
    print(redis)
    print("redis 连接成功")
    return redis

async def get_redis(request: Request) -> MyRedis:
    """ redis连接对象 """
    return await request.app.state.redis

#Redis 操作：
#     get_user = await request.app.state.redis.get(token)
# await request.app.state.redis.set(access_token, obj_as_json(user), access_token_expires)


if __name__ == '__main__':
    import tracemalloc

    tracemalloc.start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_redis(Request))

    print(get_redis(Request))


'''
redis 设置
安装：pip install aioredis
安装 apt install redis-server
设置端口和访问来源：nano /etc/redis/redis.conf
port=49999
bind=127.0.0.1

m1: /usr/local/redis-7.0.10/src/redis-server redis.conf
macbook: /usr/local/greycdn/redis/redis-server redis.conf
'''