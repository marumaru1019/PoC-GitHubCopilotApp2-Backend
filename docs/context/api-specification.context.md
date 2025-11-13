# チケット管理API仕様書

<!-- Created by Copilot -->

このドキュメントは、チケット管理機能の詳細なAPI仕様を記載しています。

## 目次

- [認証エンドポイント](#認証エンドポイント)
  - [POST /api/auth/login](#post-apiauthlogin)
  - [GET /api/auth/me](#get-apiauthme)
- [チケットエンドポイント](#チケットエンドポイント)
  - [GET /api/tickets](#get-apitickets)
  - [POST /api/tickets](#post-apitickets)
  - [PATCH /api/tickets/{ticket_id}](#patch-apiticketsticket_id)

---

## 認証エンドポイント

### POST /api/auth/login

ユーザー認証を行い、JWTアクセストークンを発行します。

#### 実装ファイル

- **Router**: `app/routers/auth.py`
- **Schema**: `app/schemas/user.py` (LoginRequest, Token)
- **Logic**: `app/core/deps.py` (authenticate_user)
- **Security**: `app/core/security.py` (create_access_token, verify_password)

#### リクエスト

**HTTPメソッド**: `POST`
**URL**: `/api/auth/login`
**認証**: 不要
**Content-Type**: `application/json`

##### リクエストボディスキーマ

```python
# app/schemas/user.py
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
```

##### リクエスト例

```json
{
  "email": "operator@example.com",
  "password": "operator123"
}
```

##### バリデーションルール

| フィールド | 型 | 必須 | バリデーション |
|-----------|-----|------|---------------|
| `email` | EmailStr | ✅ | Pydanticの`EmailStr`による検証（RFC 5322準拠） |
| `password` | string | ✅ | 空文字列不可 |

#### レスポンス

##### 成功レスポンス (200 OK)

**スキーマ**:
```python
# app/schemas/user.py
class Token(BaseModel):
    access_token: str
    token_type: str
```

**例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzY4NTg0MDAsInN1YiI6IjEyMzQ1Njc4LTEyMzQtMTIzNC0xMjM0LTEyMzQ1Njc4OTBhYiJ9.signature",
  "token_type": "bearer"
}
```

**フィールド説明**:
- `access_token`: JWT形式のアクセストークン（有効期限: 24時間）
- `token_type`: トークンタイプ（常に "bearer"）

##### エラーレスポンス

###### 401 Unauthorized - 認証失敗

```json
{
  "detail": "Incorrect email or password"
}
```

**発生条件**:
- メールアドレスが存在しない
- パスワードが一致しない

**ヘッダー**:
```
WWW-Authenticate: Bearer
```

###### 422 Unprocessable Entity - バリデーションエラー

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "input": "invalid-email"
    }
  ]
}
```

**発生条件**:
- メールアドレス形式が不正
- 必須フィールドが欠落

#### 実装詳細

##### パスワード検証処理

```python
# app/core/deps.py
def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user by email and password."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
```

##### トークン生成処理

```python
# app/core/security.py
def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

##### JWT設定

```python
# app/core/config.py
class Settings(BaseSettings):
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
```

---

### GET /api/auth/me

現在認証されているユーザーの情報を取得します。

#### 実装ファイル

- **Router**: `app/routers/auth.py`
- **Schema**: `app/schemas/user.py` (UserResponse)
- **Logic**: `app/core/deps.py` (get_current_user)
- **Model**: `app/models/user.py` (User)

#### リクエスト

**HTTPメソッド**: `GET`
**URL**: `/api/auth/me`
**認証**: 必須（Bearer Token）

##### ヘッダー

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### レスポンス

##### 成功レスポンス (200 OK)

**スキーマ**:
```python
# app/schemas/user.py
class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str
    team_id: Optional[str] = None
```

**例**:
```json
{
  "id": "12345678-1234-1234-1234-1234567890ab",
  "email": "operator@example.com",
  "name": "オペレーター太郎",
  "role": "operator",
  "team_id": "team-uuid-1234",
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-10T15:30:00"
}
```

**フィールド説明**:
- `id`: ユーザーの一意識別子（UUID）
- `email`: メールアドレス
- `name`: ユーザー名
- `role`: ユーザーロール（`requester`, `operator`, `admin`）
- `team_id`: 所属チームID（オプショナル）
- `created_at`: アカウント作成日時（ISO 8601形式）
- `updated_at`: 最終更新日時（ISO 8601形式）

##### エラーレスポンス

###### 401 Unauthorized - 認証エラー

```json
{
  "detail": "Could not validate credentials"
}
```

**発生条件**:
- トークンが無効
- トークンの有効期限切れ
- トークンの署名が不正
- Authorizationヘッダーがない

**ヘッダー**:
```
WWW-Authenticate: Bearer
```

#### 実装詳細

##### トークン検証処理

```python
# app/core/deps.py
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    return user
```

---

## チケットエンドポイント

### GET /api/tickets

チケット一覧を取得します。フィルタリングとページネーションをサポートしています。

#### 実装ファイル

- **Router**: `app/routers/tickets.py`
- **Schema**: `app/schemas/ticket.py` (PaginatedTicketResponse, TicketResponse)
- **Service**: `app/services/ticket_service.py` (get_tickets, count_tickets)
- **Model**: `app/models/ticket.py` (Ticket)

#### リクエスト

**HTTPメソッド**: `GET`
**URL**: `/api/tickets`
**認証**: 必須（Bearer Token）

##### クエリパラメータ

| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|-----|------|-----------|------|
| `status` | string | - | なし | ステータスでフィルタ |
| `priority` | string | - | なし | 優先度でフィルタ |
| `assignee_id` | string | - | なし | 担当者IDでフィルタ |
| `category_id` | string | - | なし | カテゴリIDでフィルタ |
| `search` | string | - | なし | チケットタイトルで部分一致検索（大文字小文字を区別しない） |
| `skip` | integer | - | 0 | スキップする件数（オフセット） |
| `limit` | integer | - | 25 | 取得する最大件数（1〜100） |

##### クエリパラメータの値

**status** の有効な値:
- `OPEN` - 新規
- `IN_PROGRESS` - 対応中
- `WAITING_CUSTOMER` - 顧客待ち
- `RESOLVED` - 解決済み
- `CLOSED` - 完了
- `CANCELED` - キャンセル

**priority** の有効な値:
- `LOW` - 低
- `MEDIUM` - 中
- `HIGH` - 高
- `URGENT` - 緊急

##### リクエスト例

```
GET /api/tickets?status=OPEN&priority=HIGH&skip=0&limit=25
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### レスポンス

##### 成功レスポンス (200 OK)

**スキーマ**:
```python
# app/schemas/ticket.py
class PaginatedTicketResponse(BaseModel):
    items: List[TicketResponse]
    total: int
    skip: int
    limit: int

class TicketResponse(BaseModel):
    id: str
    ticket_number: str
    title: str
    description: str
    status: str
    priority: str
    category_id: Optional[str] = None
    category: Optional[CategoryResponse] = None
    requester_id: str
    requester: UserBasicResponse
    assignee_id: Optional[str] = None
    assignee: Optional[UserBasicResponse] = None
    assigned_team_id: Optional[str] = None
    first_response_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    waiting_customer_started_at: Optional[datetime] = None
    total_waiting_customer_duration: int = 0
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True
```

**例**:
```json
{
  "items": [
    {
      "id": "ticket-uuid-1234",
      "ticket_number": "TKT-00042",
      "title": "ログインができない",
      "description": "パスワードを入力しても「認証エラー」が表示されます",
      "status": "OPEN",
      "priority": "HIGH",
      "category_id": "category-uuid-5678",
      "category": {
        "id": "category-uuid-5678",
        "name": "ログイン問題",
        "type": "TICKET"
      },
      "requester_id": "user-uuid-1111",
      "requester": {
        "id": "user-uuid-1111",
        "name": "山田太郎",
        "email": "yamada@example.com",
        "role": "requester"
      },
      "assignee_id": "user-uuid-2222",
      "assignee": {
        "id": "user-uuid-2222",
        "name": "佐藤花子",
        "email": "sato@example.com",
        "role": "operator"
      },
      "assigned_team_id": "team-uuid-3333",
      "first_response_at": "2025-01-15T10:30:00",
      "resolved_at": null,
      "closed_at": null,
      "waiting_customer_started_at": null,
      "total_waiting_customer_duration": 0,
      "created_at": "2025-01-15T10:00:00",
      "updated_at": "2025-01-15T10:30:00",
      "tags": [
        {
          "id": "tag-uuid-1",
          "name": "login"
        },
        {
          "id": "tag-uuid-2",
          "name": "urgent"
        }
      ]
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 25
}
```

**フィールド説明**:
- `items`: チケットオブジェクトの配列
- `total`: フィルタ条件に一致するチケットの総数
- `skip`: 現在のオフセット
- `limit`: 1ページあたりの件数
- `ticket_number`: チケット番号（TKT-00001形式）
- `total_waiting_customer_duration`: 顧客待ち状態の累計時間（秒）
- `tags`: チケットに付与されたタグの配列

##### エラーレスポンス

###### 401 Unauthorized - 認証エラー

```json
{
  "detail": "Could not validate credentials"
}
```

###### 422 Unprocessable Entity - バリデーションエラー

```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["query", "limit"],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "input": "abc"
    }
  ]
}
```

**発生条件**:
- `skip`や`limit`に数値以外を指定
- `limit`が範囲外（1〜100以外）

#### 権限による動作の違い

##### requester ロール
- **自分が作成したチケットのみ**取得可能
- `requester_id`フィルタは自動的に現在のユーザーIDに設定される

##### operator / admin ロール
- **すべてのチケット**を取得可能
- すべてのフィルタパラメータを使用可能

#### 実装詳細

##### ルーター実装

```python
# app/routers/tickets.py
@router.get("", response_model=PaginatedTicketResponse)
def list_tickets(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assignee_id: Optional[str] = Query(None),
    category_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of tickets with filters."""
    # Requesters can only see their own tickets
    requester_id = None if current_user.role in ["operator", "admin"] else current_user.id

    tickets = ticket_service.get_tickets(
        db=db,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        requester_id=requester_id,
        category_id=category_id,
        skip=skip,
        limit=limit,
    )

    # Get total count
    total = ticket_service.count_tickets(
        db=db,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        requester_id=requester_id,
        category_id=category_id,
    )

    return {
        "items": tickets,
        "total": total,
        "skip": skip,
        "limit": limit,
    }
```

##### サービス実装

```python
# app/services/ticket_service.py
def get_tickets(
    db: Session,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[str] = None,
    requester_id: Optional[str] = None,
    category_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 25,
) -> List[Ticket]:
    """Get tickets with filters."""
    query = db.query(Ticket).options(
        joinedload(Ticket.category),
        joinedload(Ticket.requester),
        joinedload(Ticket.assignee),
        joinedload(Ticket.assigned_team),
        joinedload(Ticket.tags),
    )

    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if assignee_id:
        query = query.filter(Ticket.assignee_id == assignee_id)
    if requester_id:
        query = query.filter(Ticket.requester_id == requester_id)
    if category_id:
        query = query.filter(Ticket.category_id == category_id)

    return query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
```

---

### POST /api/tickets

新しいチケットを作成します。

#### 実装ファイル

- **Router**: `app/routers/tickets.py`
- **Schema**: `app/schemas/ticket.py` (TicketCreate, TicketResponse)
- **Service**: `app/services/ticket_service.py` (create_ticket)
- **Model**: `app/models/ticket.py` (Ticket)

#### リクエスト

**HTTPメソッド**: `POST`
**URL**: `/api/tickets`
**認証**: 必須（Bearer Token）
**Content-Type**: `application/json`

##### リクエストボディスキーマ

```python
# app/schemas/ticket.py
class TicketBase(BaseModel):
    title: str
    description: str
    priority: str  # LOW, MEDIUM, HIGH, URGENT
    category_id: Optional[str] = None

class TicketCreate(TicketBase):
    tags: Optional[List[str]] = []
```

##### リクエスト例

```json
{
  "title": "ログインができない",
  "description": "パスワードを入力しても「認証エラー」が表示されます。昨日までは正常にログインできていました。",
  "priority": "HIGH",
  "category_id": "category-uuid-5678",
  "tags": ["login", "urgent", "password"]
}
```

##### バリデーションルール

| フィールド | 型 | 必須 | バリデーション | 説明 |
|-----------|-----|------|---------------|------|
| `title` | string | ✅ | 空文字列不可 | チケットのタイトル |
| `description` | string | ✅ | 空文字列不可 | チケットの詳細説明 |
| `priority` | string | ✅ | `LOW`, `MEDIUM`, `HIGH`, `URGENT` のいずれか | 優先度 |
| `category_id` | string | - | 存在するカテゴリIDであること | カテゴリID |
| `tags` | array[string] | - | - | タグ名の配列（存在しないタグは自動作成） |

#### レスポンス

##### 成功レスポンス (201 Created)

**スキーマ**: `TicketResponse`（GET /api/ticketsと同じ）

**例**:
```json
{
  "id": "ticket-uuid-1234",
  "ticket_number": "TKT-00042",
  "title": "ログインができない",
  "description": "パスワードを入力しても「認証エラー」が表示されます。昨日までは正常にログインできていました。",
  "status": "OPEN",
  "priority": "HIGH",
  "category_id": "category-uuid-5678",
  "category": {
    "id": "category-uuid-5678",
    "name": "ログイン問題",
    "type": "TICKET"
  },
  "requester_id": "user-uuid-1111",
  "requester": {
    "id": "user-uuid-1111",
    "name": "山田太郎",
    "email": "yamada@example.com",
    "role": "requester"
  },
  "assignee_id": null,
  "assignee": null,
  "assigned_team_id": null,
  "first_response_at": null,
  "resolved_at": null,
  "closed_at": null,
  "waiting_customer_started_at": null,
  "total_waiting_customer_duration": 0,
  "created_at": "2025-01-15T10:00:00",
  "updated_at": "2025-01-15T10:00:00",
  "tags": [
    {
      "id": "tag-uuid-1",
      "name": "login"
    },
    {
      "id": "tag-uuid-2",
      "name": "urgent"
    },
    {
      "id": "tag-uuid-3",
      "name": "password"
    }
  ]
}
```

**自動設定される値**:
- `id`: UUID v4形式の一意識別子
- `ticket_number`: 連番形式（TKT-00001〜）
- `status`: 常に `OPEN`
- `requester_id`: 現在のユーザーID
- `created_at`, `updated_at`: 現在時刻（UTC）

##### エラーレスポンス

###### 401 Unauthorized - 認証エラー

```json
{
  "detail": "Could not validate credentials"
}
```

###### 422 Unprocessable Entity - バリデーションエラー

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "input": ""
    },
    {
      "type": "enum",
      "loc": ["body", "priority"],
      "msg": "Input should be 'LOW', 'MEDIUM', 'HIGH' or 'URGENT'",
      "input": "INVALID_PRIORITY"
    }
  ]
}
```

**発生条件**:
- 必須フィールドが欠落
- `title`または`description`が空文字列
- `priority`が有効な値でない
- `category_id`が存在しないID

#### 実装詳細

##### ルーター実装

```python
# app/routers/tickets.py
@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new ticket."""
    ticket = ticket_service.create_ticket(
        db=db,
        title=ticket_data.title,
        description=ticket_data.description,
        priority=ticket_data.priority,
        requester_id=current_user.id,
        category_id=ticket_data.category_id,
        tag_names=ticket_data.tags,
    )
    return ticket
```

##### サービス実装

```python
# app/services/ticket_service.py
def create_ticket(
    db: Session,
    title: str,
    description: str,
    priority: str,
    requester_id: str,
    category_id: Optional[str] = None,
    tag_names: Optional[List[str]] = None,
) -> Ticket:
    """Create a new ticket."""
    ticket_id = str(uuid.uuid4())
    ticket_number = generate_ticket_number(db)

    ticket = Ticket(
        id=ticket_id,
        ticket_number=ticket_number,
        title=title,
        description=description,
        status="OPEN",
        priority=priority,
        category_id=category_id,
        requester_id=requester_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    # Add tags if provided
    if tag_names:
        for tag_name in tag_names:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(id=str(uuid.uuid4()), name=tag_name, created_at=datetime.utcnow())
                db.add(tag)
            ticket.tags.append(tag)

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # Reload ticket with relationships
    ticket = get_ticket(db, ticket.id)

    # Create audit log
    create_audit_log(
        db,
        user_id=requester_id,
        action="TICKET_CREATED",
        entity_type="TICKET",
        entity_id=ticket.id,
        metadata={"ticket_number": ticket.ticket_number, "title": title},
    )

    return ticket
```

##### チケット番号生成

```python
# app/services/ticket_service.py
def generate_ticket_number(db: Session) -> str:
    """Generate unique ticket number in format TKT-00001."""
    last_ticket = db.query(Ticket).order_by(Ticket.created_at.desc()).first()
    if not last_ticket:
        return "TKT-00001"

    # Extract number from last ticket
    last_number = int(last_ticket.ticket_number.split("-")[1])
    new_number = last_number + 1
    return f"TKT-{new_number:05d}"
```

---

### PATCH /api/tickets/{ticket_id}

既存のチケット情報を更新します。

#### 実装ファイル

- **Router**: `app/routers/tickets.py`
- **Schema**: `app/schemas/ticket.py` (TicketUpdate, TicketResponse)
- **Service**: `app/services/ticket_service.py` (update_ticket)
- **Model**: `app/models/ticket.py` (Ticket)

#### リクエスト

**HTTPメソッド**: `PATCH`
**URL**: `/api/tickets/{ticket_id}`
**認証**: 必須（Bearer Token、operator/admin ロールのみ）
**Content-Type**: `application/json`

##### パスパラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `ticket_id` | string | ✅ | 更新対象のチケットID（UUID） |

##### リクエストボディスキーマ

```python
# app/schemas/ticket.py
class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    category_id: Optional[str] = None
    assignee_id: Optional[str] = None
    assigned_team_id: Optional[str] = None
    tags: Optional[List[str]] = None
```

> **Note**: すべてのフィールドはオプショナルです。指定されたフィールドのみが更新されます。

##### リクエスト例

```json
{
  "title": "ログインができない（パスワードリセット済み）",
  "priority": "MEDIUM",
  "assignee_id": "operator-uuid-5678",
  "tags": ["login", "password", "resolved"]
}
```

##### バリデーションルール

| フィールド | 型 | 必須 | バリデーション | 説明 |
|-----------|-----|------|---------------|------|
| `title` | string | - | 空文字列不可 | チケットのタイトル |
| `description` | string | - | 空文字列不可 | チケットの詳細説明 |
| `priority` | string | - | `LOW`, `MEDIUM`, `HIGH`, `URGENT` のいずれか | 優先度 |
| `category_id` | string | - | 存在するカテゴリIDであること | カテゴリID |
| `assignee_id` | string | - | 存在するユーザーIDであること | 担当者ID |
| `assigned_team_id` | string | - | 存在するチームIDであること | 担当チームID |
| `tags` | array[string] | - | - | タグ名の配列（既存タグは全て置き換え） |

#### レスポンス

##### 成功レスポンス (200 OK)

**スキーマ**: `TicketResponse`（GET /api/ticketsと同じ）

**例**:
```json
{
  "id": "ticket-uuid-1234",
  "ticket_number": "TKT-00042",
  "title": "ログインができない（パスワードリセット済み）",
  "description": "パスワードを入力しても「認証エラー」が表示されます。昨日までは正常にログインできていました。",
  "status": "OPEN",
  "priority": "MEDIUM",
  "category_id": "category-uuid-5678",
  "category": {
    "id": "category-uuid-5678",
    "name": "ログイン問題",
    "type": "TICKET"
  },
  "requester_id": "user-uuid-1111",
  "requester": {
    "id": "user-uuid-1111",
    "name": "山田太郎",
    "email": "yamada@example.com",
    "role": "requester"
  },
  "assignee_id": "operator-uuid-5678",
  "assignee": {
    "id": "operator-uuid-5678",
    "name": "佐藤花子",
    "email": "sato@example.com",
    "role": "operator"
  },
  "assigned_team_id": null,
  "first_response_at": "2025-01-15T10:30:00",
  "resolved_at": null,
  "closed_at": null,
  "waiting_customer_started_at": null,
  "total_waiting_customer_duration": 0,
  "created_at": "2025-01-15T10:00:00",
  "updated_at": "2025-01-15T11:00:00",
  "tags": [
    {
      "id": "tag-uuid-1",
      "name": "login"
    },
    {
      "id": "tag-uuid-2",
      "name": "password"
    },
    {
      "id": "tag-uuid-3",
      "name": "resolved"
    }
  ]
}
```

##### エラーレスポンス

###### 401 Unauthorized - 認証エラー

```json
{
  "detail": "Could not validate credentials"
}
```

###### 403 Forbidden - 権限エラー

```json
{
  "detail": "User role 'requester' not authorized. Required: ('operator', 'admin')"
}
```

**発生条件**:
- requester ロールのユーザーがアクセス
- operator または admin ロールのみ実行可能

###### 404 Not Found - チケットが見つからない

```json
{
  "detail": "Ticket not found"
}
```

**発生条件**:
- 指定された `ticket_id` が存在しない

###### 422 Unprocessable Entity - バリデーションエラー

```json
{
  "detail": [
    {
      "type": "enum",
      "loc": ["body", "priority"],
      "msg": "Input should be 'LOW', 'MEDIUM', 'HIGH' or 'URGENT'",
      "input": "INVALID"
    }
  ]
}
```

**発生条件**:
- `priority` が有効な値でない
- `category_id`, `assignee_id`, `assigned_team_id` が存在しないID

#### 実装詳細

##### ルーター実装

```python
# app/routers/tickets.py
@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: str,
    ticket_data: TicketUpdate,
    current_user: User = Depends(get_current_operator),
    db: Session = Depends(get_db),
):
    """Update ticket fields (operator/admin only)."""
    ticket = ticket_service.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Prepare update data
    updates = ticket_data.model_dump(exclude_unset=True)

    # Handle tags separately
    if "tags" in updates:
        tag_names = updates.pop("tags")
        # Clear existing tags and add new ones
        ticket.tags.clear()
        if tag_names:
            from app.models.tag import Tag
            import uuid
            from datetime import datetime
            for tag_name in tag_names:
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(id=str(uuid.uuid4()), name=tag_name, created_at=datetime.utcnow())
                    db.add(tag)
                ticket.tags.append(tag)

    return ticket_service.update_ticket(db, ticket, current_user.id, **updates)
```

##### サービス実装

```python
# app/services/ticket_service.py
def update_ticket(
    db: Session,
    ticket: Ticket,
    user_id: str,
    **updates,
) -> Ticket:
    """Update ticket fields."""
    old_values = {}

    for key, value in updates.items():
        if value is not None and hasattr(ticket, key):
            old_values[key] = getattr(ticket, key)
            setattr(ticket, key, value)

    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)

    # Create audit log
    if old_values:
        create_audit_log(
            db,
            user_id=user_id,
            action="TICKET_UPDATED",
            entity_type="TICKET",
            entity_id=ticket.id,
            metadata={"old": old_values, "new": updates},
        )

    return ticket
```

#### 権限要件

- **operator**: チケットの更新が可能
- **admin**: チケットの更新が可能
- **requester**: チケットの更新は**不可**（403 Forbiddenエラー）

#### タグの更新動作

`tags` フィールドを指定した場合:
1. 既存のタグは**すべて削除**される
2. 指定されたタグが新しく設定される
3. 存在しないタグ名は自動的に作成される

**例**:
```json
// 既存のタグ: ["login", "urgent"]
// リクエスト:
{
  "tags": ["login", "resolved"]
}
// 結果: ["login", "resolved"] （"urgent"は削除され、"resolved"が追加）
```

#### 監査ログ

更新が成功すると、以下の情報が監査ログに記録されます:
- アクション: `TICKET_UPDATED`
- ユーザーID: 更新を実行したユーザー
- エンティティ: 更新されたチケット
- メタデータ: 変更前の値（old）と変更後の値（new）

---

## 共通仕様

### データモデル

#### Ticketモデル

```python
# app/models/ticket.py
class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True)
    ticket_number = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False)  # OPEN, IN_PROGRESS, WAITING_CUSTOMER, RESOLVED, CLOSED, CANCELED
    priority = Column(String, nullable=False)  # LOW, MEDIUM, HIGH, URGENT
    category_id = Column(String, ForeignKey("categories.id"), nullable=True)
    requester_id = Column(String, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(String, ForeignKey("users.id"), nullable=True)
    assigned_team_id = Column(String, ForeignKey("teams.id"), nullable=True)

    # SLA tracking
    first_response_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    waiting_customer_started_at = Column(DateTime, nullable=True)
    total_waiting_customer_duration = Column(Integer, default=0, nullable=False)  # seconds

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

#### Userモデル

```python
# app/models/user.py
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

### 認証と権限

#### ロール一覧

| ロール | 説明 | 権限 |
|--------|------|------|
| `requester` | 一般ユーザー | 自分のチケット作成・閲覧、公開ナレッジ記事閲覧 |
| `operator` | オペレーター | すべてのチケット管理、ナレッジ記事作成・管理 |
| `admin` | 管理者 | すべての機能にアクセス可能 |

#### 権限チェック実装

```python
# app/core/deps.py
def get_current_operator(current_user: User = Depends(require_role("operator", "admin"))) -> User:
    """Require operator or admin role."""
    return current_user

def get_current_admin(current_user: User = Depends(require_role("admin"))) -> User:
    """Require admin role."""
    return current_user
```

### エラーハンドリング

#### 標準エラーレスポンス形式

```json
{
  "detail": "エラーメッセージ"
}
```

または

```json
{
  "detail": [
    {
      "type": "エラータイプ",
      "loc": ["エラー位置", "フィールド名"],
      "msg": "エラーメッセージ",
      "input": "入力値"
    }
  ]
}
```

### 日時形式

- すべての日時は**UTC**で保存
- レスポンスはISO 8601形式（`YYYY-MM-DDTHH:mm:ss`）
- タイムゾーン情報は含まない（暗黙的にUTC）

### ページネーション

- `skip`: オフセット（デフォルト: 0、最小: 0）
- `limit`: 取得件数（デフォルト: 25、範囲: 1〜100）

### 監査ログ

すべての重要な操作（作成、更新、削除、ステータス変更等）は自動的に監査ログに記録されます。

**ログに記録される情報**:
- ユーザーID
- アクション（TICKET_CREATED, TICKET_UPDATED, STATUS_CHANGED等）
- エンティティタイプとID
- メタデータ（変更内容の詳細）
- タイムスタンプ（UTC）

---

## 関連ドキュメント

- [API概要ドキュメント](./api-overview.context.md) - APIの全体像と使用方法
- [README.md](../../README.md) - プロジェクト全体の説明
- [USAGE.md](../../USAGE.md) - システムの使用方法

---

**ドキュメント更新日**: 2025年11月13日
