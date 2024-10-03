from typing import Generic, Type, TypeVar, Optional, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import Base

# モデルとスキーマ用のTypeVarを定義
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUDオブジェクトは、特定のSQLAlchemyモデルを操作するために使用されます。
        :param model: SQLAlchemyモデルクラス
        """
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """
        IDに基づいて1つのオブジェクトを取得します。
        :param db: データベースセッション
        :param id: オブジェクトのID
        :return: モデルオブジェクト
        """
        return db.query(self.model).filter(self.model.id == id).first()
    
    def list(self, db: Session) -> List[ModelType]:
        """
        全てのオブジェクトを取得します。
        :param db: データベースセッション
        :return: モデルオブジェクトのリスト
        """
        return db.query(self.model).all()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        複数のオブジェクトを取得します。
        :param db: データベースセッション
        :param skip: 取得開始位置
        :param limit: 取得する最大件数
        :return: モデルオブジェクトのリスト
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """
        新しいオブジェクトを作成します。
        :param db: データベースセッション
        :param obj_in: 作成するオブジェクトのデータ
        :return: 作成されたモデルオブジェクト
        """
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        """
        既存のオブジェクトを更新します。
        :param db: データベースセッション
        :param db_obj: 更新対象のモデルオブジェクト
        :param obj_in: 更新するデータ
        :return: 更新されたモデルオブジェクト
        """
        obj_data = db_obj.__dict__
        update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: int) -> ModelType:
        """
        オブジェクトを削除します。
        :param db: データベースセッション
        :param id: 削除対象のオブジェクトのID
        :return: 削除されたモデルオブジェクト
        """
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj