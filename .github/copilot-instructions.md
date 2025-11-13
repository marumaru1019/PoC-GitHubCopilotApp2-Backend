# 社内ヘルプアプリ - バックエンド

チケット管理システムのバックエンドAPI。企業内のサポートチケット、ナレッジベース、ユーザー管理を提供するREST APIです。FastAPIを使用し、JWT認証、PostgreSQLデータベース、Alembicマイグレーションを実装しています。

## 技術スタック

### バックエンドフレームワーク
- **FastAPI** - 高速なWeb APIフレームワーク
- **Python 3.11+** - プログラミング言語
- **Pydantic** - データバリデーションとスキーマ定義
- **SQLAlchemy 2.0** - ORMとデータベース操作

### データベース
- **PostgreSQL** - メインデータベース
- **Alembic** - データベースマイグレーションツール

### 認証・セキュリティ
- **JWT (JSON Web Tokens)** - トークンベース認証
- **bcrypt** - パスワードハッシュ化
- **python-jose** - JWTエンコード/デコード

### テスト
- **pytest** - テストフレームワーク
- **pytest-asyncio** - 非同期テスト
- **httpx** - HTTPクライアント（テスト用）

### フロントエンド連携
- **Next.js フロントエンド** - `../helpdesk-frontend`
- **REST API** - JSONベースのデータ通信
- **CORS** - クロスオリジンリクエスト対応

## コーディングガイドライン

### 全般的な原則
- **一貫性**: プロジェクト全体で統一されたコーディングスタイルを維持
- **可読性**: 将来の自分や他の開発者が理解しやすいコードを書く
- **保守性**: 変更や拡張が容易な構造を心がける

### コミットとドキュメント
- コミットメッセージは変更内容を明確に記述
- 複雑なロジックにはコメントを追加
- READMEやドキュメントは常に最新の状態を保つ

### セキュリティとパフォーマンス
- 機密情報（APIキー、パスワード等）をコードに含めない
- パフォーマンスに影響する処理は最適化を検討
- ユーザー入力は必ずバリデーションを行う

### テストとデプロイ
- 新機能には必ずテストを追加
- 本番環境へのデプロイ前にローカルとステージング環境で動作確認
- CI/CDパイプラインを活用して品質を担保

## プロジェクト構造

- `app/` - アプリケーションのメインコード
  - `main.py` - FastAPIアプリケーションのエントリーポイント
  - `routers/` - APIエンドポイント定義
    - `auth.py` - 認証関連エンドポイント
    - `tickets.py` - チケット管理エンドポイント
    - `articles.py` - ナレッジ記事エンドポイント
    - `admin.py` - 管理機能エンドポイント
  - `models/` - SQLAlchemyモデル定義
  - `schemas/` - Pydanticスキーマ定義
  - `services/` - ビジネスロジック
  - `core/` - コア機能（認証、設定、依存性注入）
  - `db/` - データベース接続設定
- `alembic/` - データベースマイグレーション
- `tests/` - pytestテストコード
- `docs/` - API仕様書とドキュメント

## 利用可能なリソース

### スクリプト
- `uvicorn app.main:app --reload` - 開発サーバー起動
- `pytest` - テスト実行
- `alembic upgrade head` - マイグレーション適用
- `alembic revision --autogenerate -m "message"` - マイグレーション生成

### 重要な設定ファイル
- `requirements.txt` - Python依存関係
- `alembic.ini` - Alembic設定
- `pytest.ini` - pytest設定

### API仕様書
API仕様の詳細は `#file:docs/api-specification.md` を参照してください。

### フロントエンド型定義
フロントエンドのTypeScript型定義は `#file:../helpdesk-frontend/lib/types.ts` を参照してください。
