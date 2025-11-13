---
applyTo: "**/*.py"
description: "Python/FastAPI開発ガイドライン"
---

# Python/FastAPI 開発ガイドライン

## Context Loading
実装前に以下を確認してください:
- [APIルーターパターン](../../app/routers/)
- [データモデル](../../docs/context/database-schema.context.md)
- [API仕様書](../../docs/context/api-specification.context.md)

## Deterministic Requirements
- PEP 8 に準拠し、型ヒント（Type Hints）を必ず使用
- Pydantic スキーマでリクエスト/レスポンスを定義
- フロントエンドのTypeScript型（`lib/types.ts`）と一致させる
- JWT認証とSQLAlchemy ORMを使用

## Structured Output
コード生成時に以下を含める:
- [ ] Docstring（Args, Returns, Raises）
- [ ] FastAPI依存性注入（`Depends`）
- [ ] pytest テストケース（`tests/test_*.py`）
- [ ] Alembicマイグレーション（スキーマ変更時）
