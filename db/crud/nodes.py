from sqlalchemy.orm import Session

from db.schemas.nodes import NodeCreate, NodeModify, NodeStatusUpdate
from db.models.nodes import Node


def get_nodes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Node).offset(skip).limit(limit).all()

def get_nodes_by_status(db: Session, node_status: int, skip: int = 0, limit: int = 100):
    return db.query(Node).filter(Node.status == node_status).order_by(Node.update_time.desc()).offset(skip).limit(limit).all()

def get_nodes_type(db: Session, node_type: str, skip: int = 0, limit: int = 100):
    return db.query(Node).filter(Node.type == node_type).offset(skip).limit(limit).all()

def get_nodes_by_name(db: Session, node_name: str):
    return db.query(Node).filter(Node.name == node_name).first()

def get_node(db: Session, node_id: int):
    return db.query(Node).filter(Node.id == node_id).first()

def create_node(db: Session, node: NodeCreate):
    db_node = Node(**node.dict())
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node

def modify_node(db: Session, node: NodeModify):
    db_node = get_node(db, node_id=node.id)
    db_node.status = node.status
    db_node.type = node.type
    db_node.name = node.name
    db_node.update_time = node.update_time
    db_node.update_by = node.update_by
    db.commit()
    db.refresh(db_node)
    return db_node

def update_node_by_status(db: Session, node: NodeStatusUpdate):
    db_node = get_node(db, node_id=node.id)
    db_node.status = node.status
    db_node.update_time = node.update_time
    db_node.update_by = node.update_by
    db.commit()
    db.refresh(db_node)
    return db_node

def delete_node_by_id(db: Session, id: int):
    db_node = get_node(db, id)
    db.delete(db_node)
    db.commit()
