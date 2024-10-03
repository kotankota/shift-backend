import os
import time
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

# 環境変数からデータベースURLを取得
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# PostgreSQL用のエンジン作成（リトライ機能を追加）
retries = 5
while retries > 0:
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        engine.connect()  # 接続を試みる
        print("Database connected successfully!")
        break
    except OperationalError:
        retries -= 1
        print(f"Database connection failed, retrying... ({5-retries}/5)")
        time.sleep(5)

    if retries == 0:
        raise Exception("Database connection failed after multiple attempts.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()