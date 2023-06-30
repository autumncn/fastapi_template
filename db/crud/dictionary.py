from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from db.models.dictionary import Dictionary
from db.schemas.dictionary import DictionaryModify, DictionaryCreate

async def get_dictionary(db: AsyncSession, dictionary_id: int):
    return db.query(Dictionary).filter(Dictionary.id == dictionary_id).first()

async def get_dictionary_by_name(db: AsyncSession, dictionary_name: str):
    return db.query(Dictionary).filter(Dictionary.name == dictionary_name).first()

async def get_dictionarys(db: AsyncSession, skip: int = 0, limit: int = 100):
    return db.query(Dictionary).order_by(Dictionary.name.asc()).offset(skip).limit(limit).all()

async def get_dictionarys_by_type(db: AsyncSession, dict_type:str, skip: int = 0, limit: int = 100):
    return db.query(Dictionary).filter(Dictionary.type == dict_type).order_by(Dictionary.name.asc()).offset(skip).limit(limit).all()

async def modify_dictionary(db: AsyncSession, dictionary: DictionaryModify):
    db_dictionary = get_dictionary(db, dictionary.id)
    db_dictionary.name = dictionary.name
    db_dictionary.value = dictionary.value
    db_dictionary.type = dictionary.type

    db.commit()
    db.refresh(db_dictionary)
    return db_dictionary

async def create_dictionary(db: AsyncSession, dictionary: DictionaryCreate):
    db_dictionary = Dictionary(**dictionary.dict())
    db.add(db_dictionary)
    db.commit()
    db.refresh(db_dictionary)
    return db_dictionary

async def delete_dictionary_by_id(db: AsyncSession, id: int):
    db_dictionary = get_dictionary(db, id)
    db.delete(db_dictionary)
    db.commit()