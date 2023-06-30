from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator, Annotated
from core.config import settings

import sys
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from logs.logger import logger


def create_engine_and_session(url: str | URL):
    try:
        # 数据库引擎
        engine = create_async_engine(
            url,
            echo=False,
            pool_recycle=1800,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            pool_timeout=86400,
            pool_use_lifo=True,
            future=True
        )
        # log.success('数据库连接成功')
    except Exception as e:
        logger.error('❌ 数据库链接失败 {}', e)
        sys.exit()
    else:
        db_session = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
        return engine, db_session


async_engine, async_db_session = create_engine_and_session(settings.SQL_SYNC_DATABASE_URL)


async def get_db() -> AsyncSession:
    """session 生成器"""
    session = async_db_session()
    try:
        yield session
    except Exception as se:
        await session.rollback()
        raise se
    finally:
        await session.close()


Base = declarative_base()

# Session Annotated
CurrentSession = Annotated[AsyncSession, Depends(get_db)]