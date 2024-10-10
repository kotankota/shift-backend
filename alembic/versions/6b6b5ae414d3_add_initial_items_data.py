"""add initial items data

Revision ID: 6b6b5ae414d3
Revises: 71bc91cb9747
Create Date: 2024-10-08 07:03:45.179814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.models import User, DailyConstraint, Availability
import uuid
import datetime

# revision identifiers, used by Alembic.
revision: str = '6b6b5ae414d3'
down_revision: Union[str, None] = '71bc91cb9747'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # データベース接続のためのバインドを取得し、セッションを作成
    bind = op.get_bind()
    session = Session(bind=bind)

    # 初期データの削除
    session.query(Availability).delete()
    session.query(User).delete()
    session.commit()

    # 初期データの挿入

    # ユーザーの初期データを定義
    users = [
        User(id="1", name="Admin User", email="admin@example.com", hashed_password="$2b$12$QU4phCxcPsAksVLHap3JveJrK1HJ0aqhiDC7PnLPs6BpmTW0Bm/ta", role="admin"),
        User(id="2", name="Employee User", email="employee@example.com", hashed_password="$2b$12$QU4phCxcPsAksVLHap3JveJrK1HJ0aqhiDC7PnLPs6BpmTW0Bm/ta", role="employee")
    ]

    # 提出されたシフト
    submitted_shift = {
        'a': [1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1],
        'b': [0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1],
        'c': [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        'd': [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
        'e': [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1],
        'f': [0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1],
        'g': [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        'h': [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
        'i': [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
        'j': [0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1]
    }

    # 提出されたシフトに基づいてユーザーを追加
    for emp in submitted_shift.keys():
        users.append(User(id=str(uuid.uuid4()), name=f"Employee {emp.upper()}", email=f"{emp}@example.com", hashed_password="$2b$12$QU4phCxcPsAksVLHap3JveJrK1HJ0aqhiDC7PnLPs6BpmTW0Bm/ta", role="employee"))

    # 初期データをセッションに追加
    session.add_all(users)
    
    # シフト希望の初期データを定義
    availabilities = []
    for emp, shifts in submitted_shift.items():
        user_id = next(user.id for user in users if user.email == f"{emp}@example.com")
        for day, is_available in enumerate(shifts, start=1):
            availabilities.append(Availability(id=str(uuid.uuid4()), user_id=user_id, date=datetime.date(2024, 10, day), is_available=bool(is_available)))

    # シフト希望の初期データをセッションに追加
    session.add_all(availabilities)

    # データベースにコミット
    session.commit()

def downgrade() -> None:
    # データベース接続のためのバインドを取得し、セッションを作成
    bind = op.get_bind()
    session = Session(bind=bind)

    # 初期データの削除
    session.query(Availability).delete()
    session.query(User).delete()
    session.commit()
