from fastapi import HTTPException
from sqlalchemy.orm import Session

from db.models.dictionary import Dictionary
from db.schemas.dictionary import DictionaryModify, DictionaryCreate

def get_dictionary(db: Session, dictionary_id: int):
    return db.query(Dictionary).filter(Dictionary.id == dictionary_id).first()

def get_dictionary_by_name(db: Session, dictionary_name: str):
    return db.query(Dictionary).filter(Dictionary.name == dictionary_name).first()

def get_dictionarys(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Dictionary).order_by(Dictionary.name.asc()).offset(skip).limit(limit).all()

def get_dictionarys_by_type(db: Session, dict_type:str, skip: int = 0, limit: int = 100):
    return db.query(Dictionary).filter(Dictionary.type == dict_type).order_by(Dictionary.name.asc()).offset(skip).limit(limit).all()

def modify_dictionary(db: Session, dictionary: DictionaryModify):
    db_dictionary = get_dictionary(db, dictionary.id)
    db_dictionary.name = dictionary.name
    db_dictionary.value = dictionary.value
    db_dictionary.type = dictionary.type

    db.commit()
    db.refresh(db_dictionary)
    return db_dictionary

def create_dictionary(db: Session, dictionary: DictionaryCreate):
    db_dictionary = Dictionary(**dictionary.dict())
    db.add(db_dictionary)
    db.commit()
    db.refresh(db_dictionary)
    return db_dictionary

def delete_dictionary_by_id(db: Session, id: int):
    db_dictionary = get_dictionary(db, id)
    db.delete(db_dictionary)
    db.commit()