## セットアップ方法
```
docker-compose up -d
docker-compose up --build
```
## APIルート
### /admin
admin画面の提供

### /docs
openapiのドキュメントの提供

## 認証認可について
https://zenn.dev/tnakano/articles/a2245ec1b55c63

## db変更時
マイグレーションファイルの作成
```
alembic revision --autogenerate -m "Initial migration"
```
マイグレーションの実行
```
alembic upgrade head
```

## 初期データを入れたい時
マイグレーションファイルの生成
```
alembic revision --autogenerate -m "add initial items data"
```
データ挿入コードの追加
```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.models import Item  # 必要に応じてItemモデルをインポート

# revision identifiers, used by Alembic.
revision = 'your_revision_id'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None

def upgrade():
    # データベース接続のためのバインドを取得し、セッションを作成
    bind = op.get_bind()
    session = Session(bind=bind)

    # Itemの初期データを定義
    items = [
        Item(name="Water", description="Essential for survival", tag="basic"),
        Item(name="Canned Food", description="Long-lasting food", tag="food"),
        Item(name="First Aid Kit", description="Contains basic medical supplies", tag="medical"),
        # 他のアイテムをここに追加
    ]
    
    # 初期データをセッションに追加
    session.add_all(items)
    
    # データベースにコミット
    session.commit()

def downgrade():
    # ダウングレード時の処理（初期データの削除）
    bind = op.get_bind()
    session = Session(bind=bind)

    # 必要に応じて削除処理を追加
    session.query(Item).delete()
    session.commit()

```

## 新テーブル＆エンドポイント作成したい時
- models.pyに記述
- schemas/[].pyにスキーマ記述
- crud/[].pyにcrud操作記述
- main.pyにルーティング作成


## TODO:
- listで数を表示
- デフォルト値の設定