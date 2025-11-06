# pytest導入完了しました

## 📦 インストールされたパッケージ

- pytest==8.3.3
- pytest-asyncio==0.24.0
- pytest-cov==5.0.0
- httpx==0.27.2

## 📝 作成したテストファイル

1. **pytest.ini** - pytest設定ファイル
2. **tests/conftest.py** - テストフィクスチャ（共通設定）
3. **tests/test_auth.py** - 認証APIのテスト
4. **tests/test_tickets.py** - チケットAPIのテスト
5. **tests/test_articles.py** - ナレッジベースAPIのテスト
6. **tests/test_admin.py** - 管理APIのテスト

## 🚀 テストの実行方法

```bash
cd backend

# 依存関係をインストール
pip install -r requirements.txt

# すべてのテストを実行
pytest

# カバレッジ付きで実行
pytest --cov=app --cov-report=html

# 特定のテストファイルのみ実行
pytest tests/test_auth.py

# 詳細な出力
pytest -v

# 失敗したテストのみ再実行
pytest --lf
```

## 📊 テストカバレッジの確認

```bash
# テスト実行後、カバレッジレポートが生成されます
# htmlcov/index.html をブラウザで開いて確認
```

## 🧪 テスト内容

### test_auth.py
- ログイン成功/失敗
- 現在のユーザー情報取得
- 認証なしでのアクセス拒否
- ログアウト

### test_tickets.py
- チケットCRUD操作
- ロール別の権限チェック
- ステータス遷移
- 担当者割り当て
- コメント追加/取得

### test_articles.py
- 記事CRUD操作
- 公開/非公開管理
- 閲覧数カウント
- ロール別の権限チェック

### test_admin.py
- ユーザー管理
- チーム管理
- カテゴリ/タグ管理
- SLA設定管理
- 監査ログ取得とフィルタリング

## 💡 Tips

- テストはインメモリSQLiteを使用（高速＆クリーンな環境）
- 各テスト実行後にDBは自動クリーンアップ
- フィクスチャで認証済みヘッダーを簡単に取得可能
- カバレッジレポートでテストされていないコードを特定可能
