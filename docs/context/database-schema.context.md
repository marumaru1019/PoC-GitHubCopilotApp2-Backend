# データベーススキーマドキュメント

<!-- Created by Copilot2 -->

このドキュメントは、社内ヘルプアプリのデータベーススキーマ、テーブル構造、リレーションシップについて詳細に説明します。

## 目次

- [ER図](#er図)
- [テーブル一覧](#テーブル一覧)
- [テーブル詳細](#テーブル詳細)
  - [users（ユーザー）](#usersユーザー)
  - [tickets（チケット）](#ticketsチケット)
  - [comments（コメント）](#commentsコメント)
  - [teams（チーム）](#teamsチーム)
  - [categories（カテゴリ）](#categoriesカテゴリ)
  - [tags（タグ）](#tagsタグ)
  - [knowledge_articles（ナレッジ記事）](#knowledge_articlesナレッジ記事)
  - [sla_settings（SLA設定）](#sla_settingssla設定)
  - [audit_logs（監査ログ）](#audit_logs監査ログ)
- [関連テーブル（多対多）](#関連テーブル多対多)
- [リレーションシップ](#リレーションシップ)
- [マイグレーション](#マイグレーション)
- [インデックス戦略](#インデックス戦略)

---

## ER図

```mermaid
erDiagram
    users ||--o{ tickets : "requester"
    users ||--o{ tickets : "assignee"
    users ||--o{ comments : "author"
    users ||--o{ knowledge_articles : "author"
    users ||--o{ audit_logs : "creates"

    teams ||--o{ tickets : "assigned_to"

    categories ||--o{ tickets : "categorizes"
    categories ||--o{ knowledge_articles : "categorizes"

    tickets ||--o{ comments : "has"
    tickets }o--o{ tags : "tagged_with"

    knowledge_articles }o--o{ tags : "tagged_with"

    sla_settings ||--|| tickets : "applies_to (via priority)"

    users {
        string id PK
        string email UK
        string name
        string role
        string team_id FK
        string password_hash
        datetime created_at
        datetime updated_at
    }

    tickets {
        string id PK
        string ticket_number UK
        string title
        string description
        string status
        string priority
        string category_id FK
        string requester_id FK
        string assignee_id FK
        string assigned_team_id FK
        datetime first_response_at
        datetime resolved_at
        datetime closed_at
        datetime waiting_customer_started_at
        integer total_waiting_customer_duration
        datetime created_at
        datetime updated_at
    }

    comments {
        string id PK
        string ticket_id FK
        string author_id FK
        text content
        boolean is_internal
        datetime created_at
        datetime updated_at
    }

    teams {
        string id PK
        string name
        string description
        datetime created_at
        datetime updated_at
    }

    categories {
        string id PK
        string name
        string type
        string description
        datetime created_at
    }

    tags {
        string id PK
        string name UK
        datetime created_at
    }

    knowledge_articles {
        string id PK
        string title
        text content
        string status
        string category_id FK
        string author_id FK
        integer view_count
        datetime created_at
        datetime updated_at
        datetime published_at
    }

    sla_settings {
        string id PK
        string priority UK
        integer first_response_target_minutes
        integer resolution_target_minutes
        boolean pause_on_waiting_customer
        string timezone
        datetime created_at
        datetime updated_at
    }

    audit_logs {
        string id PK
        string user_id FK
        string action
        string entity_type
        string entity_id
        json meta_data
        string ip_address
        string user_agent
        datetime created_at
    }
```

---

## テーブル一覧

| テーブル名 | 説明 | 実装ファイル |
|-----------|------|-------------|
| `users` | ユーザー情報 | `app/models/user.py` |
| `tickets` | チケット情報 | `app/models/ticket.py` |
| `comments` | チケットコメント | `app/models/comment.py` |
| `teams` | チーム情報 | `app/models/team.py` |
| `categories` | カテゴリ情報 | `app/models/category.py` |
| `tags` | タグ情報 | `app/models/tag.py` |
| `knowledge_articles` | ナレッジ記事 | `app/models/knowledge_article.py` |
| `sla_settings` | SLA設定 | `app/models/sla_settings.py` |
| `audit_logs` | 監査ログ | `app/models/audit_log.py` |
| `ticket_tags` | チケットとタグの関連（多対多） | `app/models/tag.py` |
| `article_tags` | 記事とタグの関連（多対多） | `app/models/tag.py` |

---

## テーブル詳細

### users（ユーザー）

システムのユーザーを管理するテーブル。

**実装ファイル**: `app/models/user.py`

#### カラム定義

| カラム名 | 型 | NULL | デフォルト | 制約 | 説明 |
|---------|-----|------|-----------|------|------|
| `id` | String | NO | - | PRIMARY KEY | ユーザーID（UUID） |
| `email` | String | NO | - | UNIQUE, INDEX | メールアドレス（ログインID） |
| `name` | String | NO | - | - | ユーザー名 |
| `role` | String | NO | - | - | ロール（requester, operator, admin） |
| `team_id` | String | YES | NULL | FOREIGN KEY | 所属チームID |
| `password_hash` | String | NO | - | - | ハッシュ化されたパスワード（bcrypt） |
| `created_at` | DateTime | NO | utcnow() | - | 作成日時 |
| `updated_at` | DateTime | NO | utcnow() | ON UPDATE | 更新日時 |

#### インデックス

```sql
CREATE UNIQUE INDEX ix_users_email ON users (email);
```

#### ロール値

- `requester`: 一般ユーザー（チケット作成・閲覧）
- `operator`: オペレーター（チケット管理、記事作成）
- `admin`: 管理者（すべての機能）

#### リレーションシップ

- **1対多**: 1人のユーザーは複数のチケットを作成（`requester`）
- **1対多**: 1人のユーザーは複数のチケットを担当（`assignee`）
- **1対多**: 1人のユーザーは複数のコメントを作成
- **1対多**: 1人のユーザーは複数のナレッジ記事を作成
- **多対1**: 複数のユーザーは1つのチームに所属

#### SQLAlchemyモデル

```python
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # requester, operator, admin
    team_id = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

---

### tickets（チケット）

サポートチケットを管理するテーブル。

**実装ファイル**: `app/models/ticket.py`

#### カラム定義

| カラム名 | 型 | NULL | デフォルト | 制約 | 説明 |
|---------|-----|------|-----------|------|------|
| `id` | String | NO | - | PRIMARY KEY | チケットID（UUID） |
| `ticket_number` | String | NO | - | UNIQUE, INDEX | チケット番号（TKT-00001形式） |
| `title` | String | NO | - | - | タイトル |
| `description` | String | NO | - | - | 詳細説明 |
| `status` | String | NO | - | - | ステータス |
| `priority` | String | NO | - | - | 優先度 |
| `category_id` | String | YES | NULL | FOREIGN KEY | カテゴリID |
| `requester_id` | String | NO | - | FOREIGN KEY | 依頼者ID（users.id） |
| `assignee_id` | String | YES | NULL | FOREIGN KEY | 担当者ID（users.id） |
| `assigned_team_id` | String | YES | NULL | FOREIGN KEY | 担当チームID |
| `first_response_at` | DateTime | YES | NULL | - | 初回応答日時（SLA追跡） |
| `resolved_at` | DateTime | YES | NULL | - | 解決日時 |
| `closed_at` | DateTime | YES | NULL | - | 完了日時 |
| `waiting_customer_started_at` | DateTime | YES | NULL | - | 顧客待ち開始日時 |
| `total_waiting_customer_duration` | Integer | NO | 0 | - | 顧客待ち累計時間（秒） |
| `created_at` | DateTime | NO | utcnow() | - | 作成日時 |
| `updated_at` | DateTime | NO | utcnow() | ON UPDATE | 更新日時 |

#### インデックス

```sql
CREATE UNIQUE INDEX ix_tickets_ticket_number ON tickets (ticket_number);
```

#### ステータス値

- `OPEN`: 新規
- `IN_PROGRESS`: 対応中
- `WAITING_CUSTOMER`: 顧客待ち
- `RESOLVED`: 解決済み
- `CLOSED`: 完了
- `CANCELED`: キャンセル

#### 優先度値

- `LOW`: 低
- `MEDIUM`: 中
- `HIGH`: 高
- `URGENT`: 緊急

#### リレーションシップ

- **多対1**: 複数のチケットは1人の依頼者を持つ（`requester`）
- **多対1**: 複数のチケットは1人の担当者を持つ（`assignee`）
- **多対1**: 複数のチケットは1つのチームに割り当て
- **多対1**: 複数のチケットは1つのカテゴリに属する
- **1対多**: 1つのチケットは複数のコメントを持つ
- **多対多**: チケットとタグ（`ticket_tags`テーブル経由）

#### SQLAlchemyモデル

```python
class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True)
    ticket_number = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    category_id = Column(String, ForeignKey("categories.id"), nullable=True)
    requester_id = Column(String, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(String, ForeignKey("users.id"), nullable=True)
    assigned_team_id = Column(String, ForeignKey("teams.id"), nullable=True)

    # SLA tracking
    first_response_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    waiting_customer_started_at = Column(DateTime, nullable=True)
    total_waiting_customer_duration = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    category = relationship("Category", foreign_keys=[category_id])
    requester = relationship("User", foreign_keys=[requester_id])
    assignee = relationship("User", foreign_keys=[assignee_id])
    assigned_team = relationship("Team", foreign_keys=[assigned_team_id])
    tags = relationship("Tag", secondary="ticket_tags", back_populates="tickets")
    comments = relationship("Comment", back_populates="ticket")
```

---

### comments（コメント）

チケットに対するコメントを管理するテーブル。

**実装ファイル**: `app/models/comment.py`

#### カラム定義

| カラム名 | 型 | NULL | デフォルト | 制約 | 説明 |
|---------|-----|------|-----------|------|------|
| `id` | String | NO | - | PRIMARY KEY | コメントID（UUID） |
| `ticket_id` | String | NO | - | FOREIGN KEY | チケットID |
| `author_id` | String | NO | - | FOREIGN KEY | 作成者ID（users.id） |
| `content` | Text | NO | - | - | コメント内容 |
| `is_internal` | Boolean | NO | False | - | 内部コメントフラグ |
| `created_at` | DateTime | NO | utcnow() | - | 作成日時 |
| `updated_at` | DateTime | NO | utcnow() | ON UPDATE | 更新日時 |

#### 内部コメント（is_internal）

- `False`: 顧客にも表示される公開コメント
- `True`: オペレーター/管理者のみ閲覧可能な内部コメント

#### リレーションシップ

- **多対1**: 複数のコメントは1つのチケットに属する
- **多対1**: 複数のコメントは1人の作成者を持つ

#### SQLAlchemyモデル

```python
class Comment(Base):
    __tablename__ = "comments"

    id = Column(String, primary_key=True)
    ticket_id = Column(String, ForeignKey("tickets.id"), nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    ticket = relationship("Ticket", back_populates="comments")
    author = relationship("User", foreign_keys=[author_id])
```

---

### teams（チーム）

オペレーターや管理者のチームを管理するテーブル。

**実装ファイル**: `app/models/team.py`

#### カラム定義

| カラム名 | 型 | NULL | デフォルト | 制約 | 説明 |
|---------|-----|------|-----------|------|------|
| `id` | String | NO | - | PRIMARY KEY | チームID（UUID） |
| `name` | String | NO | - | - | チーム名 |
| `description` | String | YES | NULL | - | チームの説明 |
| `created_at` | DateTime | NO | utcnow() | - | 作成日時 |
| `updated_at` | DateTime | NO | utcnow() | ON UPDATE | 更新日時 |

#### リレーションシップ

- **1対多**: 1つのチームは複数のユーザーを持つ（`users.team_id`）
- **1対多**: 1つのチームは複数のチケットに割り当てられる

#### SQLAlchemyモデル

```python
class Team(Base):
    __tablename__ = "teams"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

---

### categories（カテゴリ）

チケットやナレッジ記事のカテゴリを管理するテーブル。

**実装ファイル**: `app/models/category.py`

#### カラム定義

| カラム名 | 型 | NULL | デフォルト | 制約 | 説明 |
|---------|-----|------|-----------|------|------|
| `id` | String | NO | - | PRIMARY KEY | カテゴリID（UUID） |
| `name` | String | NO | - | - | カテゴリ名 |
| `type` | String | NO | - | - | カテゴリタイプ |
| `description` | String | YES | NULL | - | カテゴリの説明 |
| `created_at` | DateTime | NO | utcnow() | - | 作成日時 |

#### カテゴリタイプ値

- `TICKET`: チケット専用
- `ARTICLE`: ナレッジ記事専用
- `BOTH`: チケットと記事の両方に使用可能

#### リレーションシップ

- **1対多**: 1つのカテゴリは複数のチケットを持つ
- **1対多**: 1つのカテゴリは複数のナレッジ記事を持つ

#### SQLAlchemyモデル

```python
class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # TICKET, ARTICLE, BOTH
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

---

### tags（タグ）

チケットやナレッジ記事に付与するタグを管理するテーブル。

**実装ファイル**: `app/models/tag.py`

#### カラム定義

| カラム名 | 型 | NULL | デフォルト | 制約 | 説明 |
|---------|-----|------|-----------|------|------|
| `id` | String | NO | - | PRIMARY KEY | タグID（UUID） |
| `name` | String | NO | - | UNIQUE, INDEX | タグ名 |
| `created_at` | DateTime | NO | utcnow() | - | 作成日時 |

#### インデックス

```sql
CREATE UNIQUE INDEX ix_tags_name ON tags (name);
```

#### リレーションシップ

- **多対多**: タグとチケット（`ticket_tags`テーブル経由）
- **多対多**: タグとナレッジ記事（`article_tags`テーブル経由）

#### SQLAlchemyモデル

```python
class Tag(Base):
    __tablename__ = "tags"

    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    tickets = relationship("Ticket", secondary="ticket_tags", back_populates="tags")
    articles = relationship("KnowledgeArticle", secondary="article_tags", back_populates="tags")
```

---

### knowledge_articles（ナレッジ記事）

ナレッジベースの記事を管理するテーブル。

**実装ファイル**: `app/models/knowledge_article.py`

#### カラム定義

| カラム名 | 型 | NULL | デフォルト | 制約 | 説明 |
|---------|-----|------|-----------|------|------|
| `id` | String | NO | - | PRIMARY KEY | 記事ID（UUID） |
| `title` | String | NO | - | - | 記事タイトル |
| `content` | Text | NO | - | - | 記事内容（Markdown対応） |
| `status` | String | NO | - | - | 公開ステータス |
| `category_id` | String | YES | NULL | FOREIGN KEY | カテゴリID |
| `author_id` | String | NO | - | FOREIGN KEY | 作成者ID（users.id） |
| `view_count` | Integer | NO | 0 | - | 閲覧数 |
| `created_at` | DateTime | NO | utcnow() | - | 作成日時 |
| `updated_at` | DateTime | NO | utcnow() | ON UPDATE | 更新日時 |
| `published_at` | DateTime | YES | NULL | - | 公開日時 |

#### ステータス値

- `DRAFT`: 下書き（作成者と管理者のみ閲覧可能）
- `PUBLISHED`: 公開済み（全ユーザーが閲覧可能）
- `ARCHIVED`: アーカイブ（論理削除）

#### リレーションシップ

- **多対1**: 複数の記事は1つのカテゴリに属する
- **多対1**: 複数の記事は1人の作成者を持つ
- **多対多**: 記事とタグ（`article_tags`テーブル経由）

#### SQLAlchemyモデル

```python
class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String, nullable=False)  # DRAFT, PUBLISHED, ARCHIVED
    category_id = Column(String, ForeignKey("categories.id"), nullable=True)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    published_at = Column(DateTime, nullable=True)

    # Relationships
    category = relationship("Category", foreign_keys=[category_id])
    author = relationship("User", foreign_keys=[author_id])
    tags = relationship("Tag", secondary="article_tags", back_populates="articles")
```

---

### sla_settings（SLA設定）

優先度ごとのSLA（Service Level Agreement）設定を管理するテーブル。

**実装ファイル**: `app/models/sla_settings.py`

#### カラム定義

| カラム名 | 型 | NULL | デフォルト | 制約 | 説明 |
|---------|-----|------|-----------|------|------|
| `id` | String | NO | - | PRIMARY KEY | 設定ID（UUID） |
| `priority` | String | NO | - | UNIQUE | 優先度（LOW, MEDIUM, HIGH, URGENT） |
| `first_response_target_minutes` | Integer | NO | - | - | 初回応答目標時間（分） |
| `resolution_target_minutes` | Integer | NO | - | - | 解決目標時間（分） |
| `pause_on_waiting_customer` | Boolean | NO | True | - | 顧客待ち時に計測を一時停止するか |
| `timezone` | String | NO | "Asia/Tokyo" | - | タイムゾーン |
| `created_at` | DateTime | NO | utcnow() | - | 作成日時 |
| `updated_at` | DateTime | NO | utcnow() | ON UPDATE | 更新日時 |

#### 制約

```sql
UNIQUE (priority)
```

各優先度に対して1つのSLA設定のみ存在可能。

#### SLA計測

- **first_response_target_minutes**: チケット作成から初回応答までの目標時間
- **resolution_target_minutes**: チケット作成から解決までの目標時間
- **pause_on_waiting_customer**: `True`の場合、`WAITING_CUSTOMER`ステータス中は計測を一時停止

#### SQLAlchemyモデル

```python
class SLASettings(Base):
    __tablename__ = "sla_settings"

    id = Column(String, primary_key=True)
    priority = Column(String, unique=True, nullable=False)
    first_response_target_minutes = Column(Integer, nullable=False)
    resolution_target_minutes = Column(Integer, nullable=False)
    pause_on_waiting_customer = Column(Boolean, default=True, nullable=False)
    timezone = Column(String, default="Asia/Tokyo", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

---

### audit_logs（監査ログ）

システム内のすべての重要な操作を記録する監査ログテーブル。

**実装ファイル**: `app/models/audit_log.py`

#### カラム定義

| カラム名 | 型 | NULL | デフォルト | 制約 | 説明 |
|---------|-----|------|-----------|------|------|
| `id` | String | NO | - | PRIMARY KEY | ログID（UUID） |
| `user_id` | String | NO | - | FOREIGN KEY | 操作ユーザーID |
| `action` | String | NO | - | - | アクション名 |
| `entity_type` | String | NO | - | - | エンティティタイプ |
| `entity_id` | String | NO | - | - | エンティティID |
| `meta_data` | JSON | YES | NULL | - | メタデータ（JSON形式） |
| `ip_address` | String | YES | NULL | - | IPアドレス |
| `user_agent` | String | YES | NULL | - | ユーザーエージェント |
| `created_at` | DateTime | NO | utcnow() | - | 作成日時 |

#### アクション値の例

- `TICKET_CREATED`: チケット作成
- `TICKET_UPDATED`: チケット更新
- `STATUS_CHANGED`: ステータス変更
- `TICKET_ASSIGNED`: チケット割り当て
- `COMMENT_ADDED`: コメント追加
- `ARTICLE_CREATED`: 記事作成
- `ARTICLE_PUBLISHED`: 記事公開

#### エンティティタイプ値

- `TICKET`: チケット
- `ARTICLE`: ナレッジ記事
- `USER`: ユーザー
- `CATEGORY`: カテゴリ
- `TAG`: タグ

#### メタデータ例

```json
{
  "old_status": "OPEN",
  "new_status": "IN_PROGRESS",
  "ticket_number": "TKT-00042"
}
```

#### リレーションシップ

- **多対1**: 複数のログは1人のユーザーによって作成される

#### SQLAlchemyモデル

```python
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    meta_data = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

---

## 関連テーブル（多対多）

### ticket_tags（チケット-タグ関連）

チケットとタグの多対多リレーションシップを管理する関連テーブル。

**実装ファイル**: `app/models/tag.py`

#### カラム定義

| カラム名 | 型 | NULL | 制約 | 説明 |
|---------|-----|------|------|------|
| `ticket_id` | String | NO | PRIMARY KEY, FOREIGN KEY | チケットID |
| `tag_id` | String | NO | PRIMARY KEY, FOREIGN KEY | タグID |

#### 複合主キー

```sql
PRIMARY KEY (ticket_id, tag_id)
```

#### 外部キー制約

```sql
FOREIGN KEY (ticket_id) REFERENCES tickets(id)
FOREIGN KEY (tag_id) REFERENCES tags(id)
```

#### SQLAlchemy定義

```python
ticket_tags = Table(
    "ticket_tags",
    Base.metadata,
    Column("ticket_id", String, ForeignKey("tickets.id"), primary_key=True),
    Column("tag_id", String, ForeignKey("tags.id"), primary_key=True),
)
```

---

### article_tags（記事-タグ関連）

ナレッジ記事とタグの多対多リレーションシップを管理する関連テーブル。

**実装ファイル**: `app/models/tag.py`

#### カラム定義

| カラム名 | 型 | NULL | 制約 | 説明 |
|---------|-----|------|------|------|
| `article_id` | String | NO | PRIMARY KEY, FOREIGN KEY | 記事ID |
| `tag_id` | String | NO | PRIMARY KEY, FOREIGN KEY | タグID |

#### 複合主キー

```sql
PRIMARY KEY (article_id, tag_id)
```

#### 外部キー制約

```sql
FOREIGN KEY (article_id) REFERENCES knowledge_articles(id)
FOREIGN KEY (tag_id) REFERENCES tags(id)
```

#### SQLAlchemy定義

```python
article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", String, ForeignKey("knowledge_articles.id"), primary_key=True),
    Column("tag_id", String, ForeignKey("tags.id"), primary_key=True),
)
```

---

## リレーションシップ

### 1対多（One-to-Many）リレーションシップ

| 親テーブル | 子テーブル | 外部キー | 説明 |
|-----------|-----------|---------|------|
| `users` | `tickets` | `requester_id` | ユーザーは複数のチケットを作成 |
| `users` | `tickets` | `assignee_id` | ユーザーは複数のチケットを担当 |
| `users` | `comments` | `author_id` | ユーザーは複数のコメントを作成 |
| `users` | `knowledge_articles` | `author_id` | ユーザーは複数の記事を作成 |
| `users` | `audit_logs` | `user_id` | ユーザーは複数のログを生成 |
| `teams` | `tickets` | `assigned_team_id` | チームは複数のチケットに割り当て |
| `categories` | `tickets` | `category_id` | カテゴリは複数のチケットを持つ |
| `categories` | `knowledge_articles` | `category_id` | カテゴリは複数の記事を持つ |
| `tickets` | `comments` | `ticket_id` | チケットは複数のコメントを持つ |

### 多対多（Many-to-Many）リレーションシップ

| テーブル1 | テーブル2 | 関連テーブル | 説明 |
|----------|----------|------------|------|
| `tickets` | `tags` | `ticket_tags` | チケットは複数のタグを持ち、タグは複数のチケットに付与 |
| `knowledge_articles` | `tags` | `article_tags` | 記事は複数のタグを持ち、タグは複数の記事に付与 |

### SQLAlchemyでのリレーションシップ定義例

#### 1対多（tickets.requester → users）

```python
# Ticket側
requester = relationship("User", foreign_keys=[requester_id])

# 使用例
ticket = session.query(Ticket).first()
print(ticket.requester.name)  # "山田太郎"
```

#### 多対多（tickets ↔ tags）

```python
# Ticket側
tags = relationship("Tag", secondary="ticket_tags", back_populates="tickets")

# Tag側
tickets = relationship("Ticket", secondary="ticket_tags", back_populates="tags")

# 使用例
ticket = session.query(Ticket).first()
for tag in ticket.tags:
    print(tag.name)  # "urgent", "login", etc.
```

---

## マイグレーション

このプロジェクトは**Alembic**を使用してデータベースマイグレーションを管理しています。

### Alembic設定

**設定ファイル**: `alembic.ini`
**マイグレーションディレクトリ**: `alembic/versions/`

### 初回マイグレーション

初回マイグレーションファイル: `alembic/versions/a6a51f800395_initial_migration.py`

このマイグレーションで以下のテーブルが作成されます:
1. `categories`
2. `sla_settings`
3. `tags`
4. `teams`
5. `users`
6. `audit_logs`
7. `knowledge_articles`
8. `tickets`
9. `article_tags`
10. `comments`
11. `ticket_tags`

### マイグレーション手順

#### 1. データベース接続設定

```bash
# .env ファイルに設定
DATABASE_URL=postgresql://user:password@localhost:5432/helpdesk
```

または

```bash
# SQLite（開発環境）
DATABASE_URL=sqlite:///./helpdesk.db
```

#### 2. 最新のマイグレーションを適用

```bash
alembic upgrade head
```

**実行されるSQL例**:
```sql
CREATE TABLE categories (
    id VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    description VARCHAR,
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE users (
    id VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    role VARCHAR NOT NULL,
    team_id VARCHAR,
    password_hash VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_users_email ON users (email);

-- 他のテーブルも同様に作成...
```

#### 3. 現在のマイグレーションバージョンを確認

```bash
alembic current
```

**出力例**:
```
a6a51f800395 (head)
```

#### 4. マイグレーション履歴を表示

```bash
alembic history
```

**出力例**:
```
a6a51f800395 -> head, Initial migration
```

### 新しいマイグレーションの作成

#### モデルを変更した後、自動生成

```bash
alembic revision --autogenerate -m "Add email_verified column to users"
```

**生成されるファイル例**: `alembic/versions/xxxxx_add_email_verified_column_to_users.py`

```python
def upgrade() -> None:
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))

def downgrade() -> None:
    op.drop_column('users', 'email_verified')
```

#### マイグレーションを適用

```bash
alembic upgrade head
```

#### マイグレーションをロールバック

```bash
# 1つ前に戻る
alembic downgrade -1

# 特定のリビジョンに戻る
alembic downgrade a6a51f800395
```

### マイグレーションのベストプラクティス

1. **本番環境にデプロイする前に必ずテスト環境で検証**
   ```bash
   # テスト環境で実行
   alembic upgrade head
   # 問題がなければロールバック
   alembic downgrade -1
   # 再度適用して確認
   alembic upgrade head
   ```

2. **データ損失のリスクがある変更は慎重に**
   - カラム削除
   - テーブル削除
   - NOT NULL制約の追加（既存データがある場合）

3. **`--autogenerate`の結果は必ず確認**
   - 自動生成されたマイグレーションが意図通りか確認
   - 不要な変更が含まれていないか確認

4. **本番環境では必ずバックアップを取得**
   ```bash
   # PostgreSQLの例
   pg_dump -U user -d helpdesk > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

---

## インデックス戦略

### 既存のインデックス

| テーブル | カラム | インデックスタイプ | 目的 |
|---------|-------|-----------------|------|
| `users` | `email` | UNIQUE INDEX | ログイン時の高速検索、重複防止 |
| `tickets` | `ticket_number` | UNIQUE INDEX | チケット番号での高速検索、重複防止 |
| `tags` | `name` | UNIQUE INDEX | タグ名での高速検索、重複防止 |

### 追加推奨インデックス（パフォーマンス改善）

#### チケットテーブル

```sql
-- ステータスでのフィルタリングが頻繁
CREATE INDEX idx_tickets_status ON tickets (status);

-- 優先度でのフィルタリングが頻繁
CREATE INDEX idx_tickets_priority ON tickets (priority);

-- 依頼者IDでの検索（ユーザーが自分のチケットを確認）
CREATE INDEX idx_tickets_requester_id ON tickets (requester_id);

-- 担当者IDでの検索（担当チケットの確認）
CREATE INDEX idx_tickets_assignee_id ON tickets (assignee_id);

-- 作成日時での並び替え
CREATE INDEX idx_tickets_created_at ON tickets (created_at DESC);

-- 複合インデックス（ステータスと作成日時）
CREATE INDEX idx_tickets_status_created ON tickets (status, created_at DESC);

-- タイトル検索の最適化（部分一致検索）
-- Note: ILIKEによる前方一致・部分一致検索を高速化
-- PostgreSQLの場合、pg_trgm拡張を使用するとさらに高速化可能
CREATE INDEX idx_tickets_title ON tickets (title);

-- または、PostgreSQLでpg_trgm拡張を使用する場合:
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- CREATE INDEX idx_tickets_title_trgm ON tickets USING gin (title gin_trgm_ops);
```

#### ナレッジ記事テーブル

```sql
-- ステータスでのフィルタリング（公開記事のみ表示）
CREATE INDEX idx_articles_status ON knowledge_articles (status);

-- 作成日時での並び替え
CREATE INDEX idx_articles_created_at ON knowledge_articles (created_at DESC);

-- 閲覧数での並び替え（人気記事）
CREATE INDEX idx_articles_view_count ON knowledge_articles (view_count DESC);
```

#### コメントテーブル

```sql
-- チケットIDでの検索（チケットのコメント一覧）
CREATE INDEX idx_comments_ticket_id ON comments (ticket_id);

-- 作成日時での並び替え
CREATE INDEX idx_comments_created_at ON comments (created_at ASC);
```

#### 監査ログテーブル

```sql
-- ユーザーIDでの検索
CREATE INDEX idx_audit_logs_user_id ON audit_logs (user_id);

-- エンティティタイプとIDでの検索
CREATE INDEX idx_audit_logs_entity ON audit_logs (entity_type, entity_id);

-- 作成日時での並び替え
CREATE INDEX idx_audit_logs_created_at ON audit_logs (created_at DESC);
```

### インデックス作成時の注意点

1. **書き込みパフォーマンスへの影響**
   - インデックスが多いと INSERT/UPDATE が遅くなる
   - 必要なインデックスのみ作成

2. **ディスクスペースの使用**
   - インデックスはディスクスペースを消費
   - 大きなテーブルでは注意が必要

3. **定期的なメンテナンス**
   ```sql
   -- PostgreSQLの例
   REINDEX TABLE tickets;
   VACUUM ANALYZE tickets;
   ```

---

## データ型とUUID

### UUID（Universally Unique Identifier）の使用

すべての主キー（`id`）はUUID形式の文字列を使用しています。

**メリット**:
- グローバルに一意
- シーケンシャルIDよりも予測困難（セキュリティ向上）
- 分散システムでの衝突リスクが低い

**Python実装**:
```python
import uuid

ticket_id = str(uuid.uuid4())
# 例: "12345678-1234-1234-1234-1234567890ab"
```

### 日時型

すべての日時は`DateTime`型でUTCとして保存されます。

```python
from datetime import datetime

created_at = datetime.utcnow()
# 例: 2025-11-13 10:30:45.123456
```

### JSON型

`audit_logs.meta_data`はJSON型を使用し、柔軟なメタデータを保存できます。

```python
meta_data = {
    "old_status": "OPEN",
    "new_status": "IN_PROGRESS",
    "changed_fields": ["status", "assignee_id"]
}
```

---

## まとめ

### データベース設計の特徴

- ✅ **正規化**: 適切に正規化されたスキーマ
- ✅ **リレーションシップ**: 1対多、多対多を適切に実装
- ✅ **制約**: 外部キー、UNIQUE、NOT NULLで整合性を保証
- ✅ **インデックス**: 頻繁なクエリに対応したインデックス
- ✅ **監査ログ**: すべての重要な操作を記録
- ✅ **SLA追跡**: チケットのSLA計測をサポート
- ✅ **柔軟性**: タグやカテゴリで柔軟な分類が可能

### パフォーマンス考慮事項

- **Eager Loading**: SQLAlchemyの`joinedload`で N+1 問題を回避
- **インデックス**: 頻繁なクエリにインデックスを追加
- **ページネーション**: 大量データの取得にオフセット・リミットを使用

---

## 関連ドキュメント

- [API仕様書](./api-specification.context.md) - APIエンドポイントの詳細
- [認証フロー](./auth-flow.context.md) - 認証の実装詳細
- [README.md](../../README.md) - プロジェクト全体の説明

---

**ドキュメント更新日**: 2025年11月13日
