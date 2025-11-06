# Helpdesk Backend API

FastAPI ベースのヘルプデスク・チケット管理システムのバックエンドAPIです。

## 技術スタック

- **Framework**: FastAPI 0.115.0
- **ORM**: SQLAlchemy 2.0.35
- **Database**: SQLite (開発用)
- **Migration**: Alembic 1.13.3
- **Authentication**: JWT (python-jose)
- **Password**: Bcrypt 5.0.0
- **Testing**: pytest 8.3.3 + pytest-xdist

## セットアップ

### ローカル環境

```bash
# 仮想環境作成
python -m venv .venv

# 仮想環境を有効化
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (cmd)
.venv\Scripts\activate.bat
# macOS/Linux
source .venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt

# マイグレーション
alembic upgrade head

# シードデータ投入
python seed.py

# サーバー起動
python -m uvicorn app.main:app --reload
```

サーバーが起動したら:
- **API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

### Docker環境

```bash
# Docker Composeで起動（推奨）
docker-compose up -d

# ログ確認
docker-compose logs -f backend

# コンテナに入ってマイグレーション実行（初回のみ）
docker-compose exec backend alembic upgrade head

# シードデータ投入（初回のみ）
docker-compose exec backend python seed.py

# コンテナ停止
docker-compose down

# コンテナ停止してボリュームも削除
docker-compose down -v
```

サーバーが起動したら:
- **API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

## 開発

### データベースマイグレーション

```bash
# マイグレーション作成
alembic revision --autogenerate -m "description"

# マイグレーション適用
alembic upgrade head

# ロールバック
alembic downgrade -1

# マイグレーション履歴
alembic history
```

### テスト

```bash
# 全テスト実行（高速・並列）
pytest

# カバレッジ付き実行
pytest --cov=app --cov-report=html

# 特定のテストファイル
pytest tests/test_auth.py -v

# 詳細出力
pytest -vv
```

テストカバレッジレポート: `htmlcov/index.html`

### コードフォーマット

```bash
# Black（フォーマッター）
black app tests

# Flake8（リンター）
flake8 app tests

# isort（import整理）
isort app tests
```

## API エンドポイント

### 認証
- `POST /api/auth/login` - ログイン（JWT発行）
- `POST /api/auth/logout` - ログアウト
- `GET /api/auth/me` - 現在のユーザー情報取得

### チケット
- `POST /api/tickets` - チケット作成
- `GET /api/tickets` - チケット一覧
- `GET /api/tickets/{id}` - チケット詳細
- `PATCH /api/tickets/{id}` - チケット更新
- `POST /api/tickets/{id}/transition` - ステータス遷移
- `POST /api/tickets/{id}/assign` - 担当者割り当て
- `POST /api/tickets/{id}/comments` - コメント追加
- `GET /api/tickets/{id}/comments` - コメント一覧

### ナレッジベース
- `POST /api/articles` - 記事作成
- `GET /api/articles` - 記事一覧
- `GET /api/articles/{id}` - 記事詳細
- `PATCH /api/articles/{id}` - 記事更新
- `POST /api/articles/{id}/publish` - 記事公開
- `POST /api/articles/{id}/unpublish` - 記事非公開
- `DELETE /api/articles/{id}` - 記事アーカイブ

### 管理機能
- `GET /api/admin/users` - ユーザー一覧
- `POST /api/admin/users` - ユーザー作成
- `PATCH /api/admin/users/{id}` - ユーザー更新
- `GET /api/admin/teams` - チーム一覧
- `POST /api/admin/teams` - チーム作成
- `PATCH /api/admin/teams/{id}` - チーム更新
- `GET /api/admin/categories` - カテゴリ一覧
- `POST /api/admin/categories` - カテゴリ作成
- `GET /api/admin/tags` - タグ一覧
- `POST /api/admin/tags` - タグ作成
- `GET /api/admin/sla-settings` - SLA設定一覧
- `POST /api/admin/sla-settings` - SLA設定作成
- `PATCH /api/admin/sla-settings/{id}` - SLA設定更新
- `GET /api/admin/audit-logs` - 監査ログ閲覧

## 環境変数

`.env`ファイルを作成して設定:

```env
DATABASE_URL=sqlite:///./helpdesk.db
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## プロジェクト構造

```
backend/
├── app/
│   ├── core/           # 認証・セキュリティ・設定
│   │   ├── auth.py
│   │   ├── security.py
│   │   ├── config.py
│   │   └── deps.py
│   ├── models/         # SQLAlchemyモデル
│   │   ├── user.py
│   │   ├── team.py
│   │   ├── ticket.py
│   │   ├── comment.py
│   │   ├── knowledge_article.py
│   │   ├── category.py
│   │   ├── tag.py
│   │   ├── audit_log.py
│   │   └── sla_settings.py
│   ├── schemas/        # Pydanticスキーマ
│   ├── routers/        # APIエンドポイント
│   │   ├── auth.py
│   │   ├── tickets.py
│   │   ├── articles.py
│   │   └── admin.py
│   ├── services/       # ビジネスロジック
│   ├── db/            # データベース設定
│   │   ├── base.py
│   │   └── session.py
│   └── main.py        # FastAPIアプリケーション
├── alembic/           # マイグレーション
├── tests/             # テストコード
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_tickets.py
│   ├── test_articles.py
│   └── test_admin.py
├── Dockerfile
├── requirements.txt
├── pytest.ini
├── seed.py           # 初期データ投入
└── README.md
```

## 初期データ

`seed.py`を実行すると以下のテストデータが投入されます:

### ユーザー

| ロール | メール | パスワード |
|--------|--------|-----------|
| Admin | admin@example.com | testpass123 |
| Operator | operator@example.com | testpass123 |
| Requester | user@example.com | testpass123 |

### その他
- チーム: 2件
- カテゴリ: 5件（チケット/記事/両方）
- タグ: 7件
- SLA設定: 4件（LOW/MEDIUM/HIGH/URGENT）

## デプロイ

### 本番環境設定

1. **環境変数を設定**
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=<strong-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

2. **PostgreSQLに移行**
```bash
pip install psycopg2-binary
alembic upgrade head
```

3. **Uvicornで起動（本番）**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

4. **Dockerで起動（本番）**
```dockerfile
# Dockerfile.prod
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## トラブルシューティング

### データベースをリセット

```bash
rm helpdesk.db
alembic upgrade head
python seed.py
```

### マイグレーションエラー

```bash
# マイグレーション履歴を確認
alembic history

# 最新に戻す
alembic upgrade head

# 1つ戻る
alembic downgrade -1
```

### テストが失敗する

```bash
# 依存関係を再インストール
pip install -r requirements.txt

# キャッシュをクリア
pytest --cache-clear

# 詳細出力で実行
pytest -vv
```

## ライセンス

MIT
