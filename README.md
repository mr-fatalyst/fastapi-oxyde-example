# Blog API with FastAPI + Oxyde ORM

> Step-by-step tutorial for building a complete REST API for a blog

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Oxyde ORM](https://img.shields.io/badge/Oxyde-ORM-orange.svg)](https://github.com/mr-fatalyst/oxyde)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## What We'll Build

REST API for a blog with:
- Users (post authors)
- Posts (blog articles)
- Comments on posts
- Tags (many-to-many relationship)
- Search and filtering
- Transactions for atomic operations

## What You'll Learn

| Topic | Description |
|-------|-------------|
| Models | Defining tables with `OxydeModel` and `Field` |
| Migrations | Auto-generating and applying schema changes |
| Stub files | Auto-generating `.pyi` for typing and IDE support |
| CRUD | Create, Read, Update, Delete |
| Foreign Keys | One-to-many relationships with cascade deletion |
| Many-to-Many | Relationships through junction tables |
| Joins & Prefetch | Efficient loading of related data |
| Q expressions | Complex search conditions (OR, AND, NOT) |
| Pagination | Paginated output with metadata |
| Transactions | Atomic operations with auto-rollback |

## Requirements

- Python 3.10+
- SQLite 3.35+ (built into Python)

---

## Table of Contents

- [Part 1: Project Setup](#part-1-project-setup)
- [Part 2: Users](#part-2-users-user)
- [Part 3: Posts](#part-3-posts-post)
- [Part 4: Comments](#part-4-comments-comment)
- [Part 5: Tags (M2M)](#part-5-tags-tag--posttag)
- [Part 6: Search and Filtering](#part-6-search-and-filtering)
- [Part 7: Transactions](#part-7-transactions-and-final-touches)
- [Summary](#summary)

---

# Part 1: Project Setup

## 1.1 Creating Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

## 1.2 Installing Dependencies

```bash
pip install oxyde fastapi uvicorn email-validator
```

## 1.3 Project Structure

Create the following structure:

```
project/
├── main.py              # FastAPI application + entry point
├── models.py            # Oxyde models
├── routes/
│   ├── __init__.py
│   └── users.py         # User routes
├── migrations/          # Will be created automatically
└── oxyde_config.py      # Will be created via oxyde init
```

Create folders and empty files:

```bash
mkdir -p routes
touch main.py models.py
touch routes/__init__.py routes/users.py
```

## 1.4 Initializing Oxyde

Run the interactive setup:

```bash
oxyde init
```

Answer the questions:
- **Models module(s):** `models`
- **Dialect:** `sqlite`
- **Database URL:** `sqlite:///blog.db`
- **Migrations directory:** `migrations`

This will create the file `oxyde_config.py`:

```python
"""Oxyde ORM configuration."""

MODELS = ["models"]
DIALECT = "sqlite"
MIGRATIONS_DIR = "migrations"
DATABASES = {
    "default": f"sqlite:///blog.db",
}
```

Since we want to use the database next to our application, according to the documentation, we modify it slightly:

```python
"""Oxyde ORM configuration."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MODELS = ["models"]
DIALECT = "sqlite"
MIGRATIONS_DIR = "migrations"
DATABASES = {
    "default": f"sqlite:///{BASE_DIR}/blog.db",
}
```

## 1.5 Basic FastAPI Application

Open `main.py` and add:

```python
import uvicorn
from fastapi import FastAPI
from oxyde import db

from oxyde_config import DATABASES

app = FastAPI(
    title="Blog API",
    description="REST API for blog with Oxyde ORM",
    version="0.1.0",
    lifespan=db.lifespan(**DATABASES)
)


@app.get("/")
async def root():
    return {"message": "Blog API is running!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
```

**What's happening here:**

- `db.lifespan(**DATABASES)` — FastAPI lifecycle context manager. It automatically:
  - Opens database connection on application startup
  - Closes connection on shutdown
- `**DATABASES` unpacks the dictionary from config as `default="sqlite:///..."`

## 1.6 Verification

Start the server:

```bash
python main.py
```

Open in browser: http://localhost:8000

Expected result:
```json
{"message": "Blog API is running!"}
```

Swagger UI is available at: http://localhost:8000/docs

---

# Part 2: Users (User)

## 2.1 Creating User Model

Open `models.py` and add:

```python
from datetime import datetime
from oxyde import OxydeModel, Field


class User(OxydeModel):
    """Blog user."""

    id: int | None = Field(default=None, db_pk=True)
    username: str = Field(db_unique=True, db_index=True)
    email: str = Field(db_unique=True)
    created_at: datetime | None = Field(default=None, db_default="CURRENT_TIMESTAMP")

    class Meta:
        is_table = True
        table_name = "users"
```

**Code breakdown:**

| Element | Description |
|---------|-------------|
| `OxydeModel` | Base class for all Oxyde models. Inherits from Pydantic BaseModel |
| `Field(db_pk=True)` | Primary key. `id` will be auto-incrementing |
| `Field(db_unique=True)` | Creates UNIQUE constraint in database |
| `Field(db_index=True)` | Creates index for fast lookup |
| `Field(db_default="CURRENT_TIMESTAMP")` | Default value at database level |
| `int \| None = Field(default=None)` | Nullable field. None means the database will assign the value |
| `class Meta: is_table = True` | Required! Indicates this is a database table |
| `table_name = "users"` | Table name. If not specified — class name will be used |

## 2.2 Creating Migration

```bash
oxyde makemigrations
```

Output:
```
📝 Creating migrations...

0️⃣  Loading models...
   ✅ Imported 1 module(s)

1️⃣  Extracting schema from models...
   ✅ Found 1 table(s): users

2️⃣  Replaying existing migrations...
   📁 Creating migrations directory: /path/migrations
   ✅ Replayed 0 migration(s)

3️⃣  Computing diff...
   ✅ Found 1 operation(s):
      - Create table: users

4️⃣  Generating migration file...

   ✅ Created: migrations/0001_create_users_table.py

5️⃣  Generating type stubs...
Generated stub: /path/models.pyi
   ✅ Generated 1 stub file(s)

```

Check the created file `migrations/0001_create_users_table.py` — it contains SQL for creating the table.

### Stub Files (.pyi)

Besides the migration, Oxyde creates a `models.pyi` file — this is a stub file with types for your IDE:

```
models.pyi
```

Contents:
```python
from datetime import datetime

class User:
    id: int | None
    username: str
    email: str
    created_at: datetime | None
    ...
```

**Why this is useful:**
- Autocompletion in IDE (PyCharm, VS Code)
- Hints for FK fields (e.g., `post.author_id` for FK `author`)
- Static type checking (mypy, pyright)

Stub files are updated automatically with each `oxyde makemigrations`.

## 2.3 Applying Migration

```bash
oxyde migrate
```

Output:
```
⏳ Applying migrations...

Found 1 pending migration(s):
  - 0001_create_users_table

Migrating to latest...

✅ Applied 1 migration(s)
   - 0001_create_users_table
```

The `users` table is now created in `blog.db`.

## 2.4 User Routes

Open `routes/users.py`:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from models import User

router = APIRouter(prefix="/users", tags=["users"])


# --- Request Schemas ---

class UserCreate(BaseModel):
    """Schema for creating a user."""
    username: str
    email: EmailStr


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    username: str | None = None
    email: EmailStr | None = None


# --- Endpoints ---

@router.get("")
async def list_users():
    """Get list of all users."""
    return await User.objects.all()


@router.get("/{user_id}")
async def get_user(user_id: int):
    """Get user by ID."""
    user = await User.objects.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", status_code=201)
async def create_user(data: UserCreate):
    """Create a new user."""
    # Check username uniqueness
    if await User.objects.filter(username=data.username).exists():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Check email uniqueness
    if await User.objects.filter(email=data.email).exists():
        raise HTTPException(status_code=400, detail="Email already taken")

    return await User.objects.create(**data.model_dump())


@router.patch("/{user_id}")
async def update_user(user_id: int, data: UserUpdate):
    """Update user."""
    user = await User.objects.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update only provided fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await user.save()
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int):
    """Delete user."""
    count = await User.objects.filter(id=user_id).delete()
    if not count:
        raise HTTPException(status_code=404, detail="User not found")
```

**Key Oxyde methods:**

| Method | Description |
|--------|-------------|
| `User.objects.all()` | Get all records |
| `User.objects.get_or_none(id=1)` | Get by ID or None |
| `User.objects.filter(username="john")` | Filtering (returns QuerySet) |
| `User.objects.filter(...).exists()` | Check existence |
| `User.objects.create(**data)` | Create record |
| `user.save()` | Save changes |
| `User.objects.filter(...).delete()` | Delete records (returns count) |

## 2.5 Connecting the Router

Update `main.py`:

```python
import uvicorn
from fastapi import FastAPI
from oxyde import db

from oxyde_config import DATABASES
from routes import users

app = FastAPI(
    title="Blog API",
    description="REST API for blog with Oxyde ORM",
    version="0.1.0",
    lifespan=db.lifespan(**DATABASES)
)

app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "Blog API is running!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
```

## 2.6 Verification

Restart the server (or it will restart automatically with `--reload`).

Open Swagger UI: http://localhost:8000/docs

### Test 1: Creating Users

**POST /users** with body:
```json
{"username": "alice", "email": "alice@example.com"}
```

Expected response (201):
```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "created_at": "2024-01-15T10:30:00.123456"
}
```

Create another one:
```json
{"username": "bob", "email": "bob@example.com"}
```

### Test 2: Getting List

**GET /users**

Expected response:
```json
[
  {"id": 1, "username": "alice", "email": "alice@example.com", "created_at": "..."},
  {"id": 2, "username": "bob", "email": "bob@example.com", "created_at": "..."}
]
```

### Test 3: Getting by ID

**GET /users/1**

Expected response:
```json
{"id": 1, "username": "alice", "email": "alice@example.com", "created_at": "..."}
```

### Test 4: Updating

**PATCH /users/1** with body:
```json
{"username": "alice_updated"}
```

### Test 5: Uniqueness Check

**POST /users** with body:
```json
{"username": "alice_updated", "email": "new@example.com"}
```

Expected response (400):
```json
{"detail": "Username already taken"}
```

---

# Part 3: Posts (Post)

## 3.1 Adding Post Model

Update `models.py`:

```python
from datetime import datetime
from oxyde import OxydeModel, Field


class User(OxydeModel):
    """Blog user."""

    id: int | None = Field(default=None, db_pk=True)
    username: str = Field(db_unique=True, db_index=True)
    email: str = Field(db_unique=True)
    created_at: datetime | None = Field(default=None, db_default="CURRENT_TIMESTAMP")

    class Meta:
        is_table = True
        table_name = "users"


class Post(OxydeModel):
    """Blog post."""

    id: int | None = Field(default=None, db_pk=True)
    title: str
    content: str
    published: bool = Field(default=False)
    created_at: datetime | None = Field(default=None, db_default="CURRENT_TIMESTAMP")
    updated_at: datetime | None = Field(default=None, db_default="CURRENT_TIMESTAMP")

    # Foreign Key to User
    author: User | None = Field(default=None, db_on_delete="CASCADE")

    class Meta:
        is_table = True
        table_name = "posts"
```

**New concepts:**

| Element | Description |
|---------|-------------|
| `author: User \| None` | Foreign Key to User model |
| `db_on_delete="CASCADE"` | When User is deleted, all their Posts are deleted |
| `Field(default=False)` | Default value at Python level |

**How FK works in Oxyde:**

- A column `author_id` is created in the database (field name + `_id`)
- When creating a post, pass `author_id=1`, not `author=user`
- When loading with `join("author")` — the `author` field is populated with a User object

## 3.2 Migration

```bash
oxyde makemigrations
```

Output:
```
📝 Creating migrations...

0️⃣  Loading models...
   ✅ Imported 1 module(s)

1️⃣  Extracting schema from models...
   ✅ Found 2 table(s): users, posts

2️⃣  Replaying existing migrations...
   ✅ Replayed 1 migration(s)

3️⃣  Computing diff...
   ✅ Found 1 operation(s):
      - Create table: posts

4️⃣  Generating migration file...

   ✅ Created: migrations/0002_create_posts_table.py

5️⃣  Generating type stubs...
Generated stub: /path/models.pyi
   ✅ Generated 1 stub file(s)
```

```bash
oxyde migrate
```

## 3.3 Post Routes

Create `routes/posts.py`:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models import Post

router = APIRouter(prefix="/posts", tags=["posts"])


# --- Schemas ---

class PostCreate(BaseModel):
    title: str
    content: str
    author_id: int
    published: bool = False


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    published: bool | None = None


# --- Endpoints ---

@router.get("")
async def list_posts(published: bool | None = None, author_id: int | None = None):
    """Get list of posts."""
    query = Post.objects

    if published is not None:
        query = query.filter(published=published)

    if author_id is not None:
        query = query.filter(author_id=author_id)

    return await query.all()


@router.get("/{post_id}")
async def get_post(post_id: int):
    """Get post by ID."""
    post = await Post.objects.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("", status_code=201)
async def create_post(data: PostCreate):
    """Create a new post."""
    return await Post.objects.create(**data.model_dump())


@router.patch("/{post_id}")
async def update_post(post_id: int, data: PostUpdate):
    """Update post."""
    post = await Post.objects.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(post, field, value)

    await post.save()
    return post


@router.delete("/{post_id}", status_code=204)
async def delete_post(post_id: int):
    """Delete post."""
    count = await Post.objects.filter(id=post_id).delete()
    if not count:
        raise HTTPException(status_code=404, detail="Post not found")
```

**Key methods:**

| Method | Description |
|--------|-------------|
| `.all()` | All records |
| `.filter(field=value)` | Filtering |
| `.get_or_none(id=...)` | Single record or None |
| `.create(**data)` | Create record |
| `.save()` | Save changes |
| `.delete()` | Delete (returns count) |

## 3.4 User's Posts

Add to `routes/users.py`:

```python
from models import User, Post

# ... existing code ...

@router.get("/{user_id}/posts")
async def list_user_posts(user_id: int):
    """Get all posts by user."""
    if not await User.objects.filter(id=user_id).exists():
        raise HTTPException(status_code=404, detail="User not found")

    return await Post.objects.filter(author_id=user_id).order_by("-created_at").all()
```

## 3.5 Connecting the Router

Update `main.py`:

```python
import uvicorn
from fastapi import FastAPI
from oxyde import db

from oxyde_config import DATABASES
from routes import users, posts

app = FastAPI(
    title="Blog API",
    description="REST API for blog with Oxyde ORM",
    version="0.1.0",
    lifespan=db.lifespan(**DATABASES)
)

app.include_router(users.router)
app.include_router(posts.router)


@app.get("/")
async def root():
    return {"message": "Blog API is running!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
```

## 3.6 Verification

### Test 1: Creating a Post

**POST /posts** with body:
```json
{
  "title": "My first post",
  "content": "Hello, this is my first blog post!",
  "author_id": 1,
  "published": true
}
```

Expected response (201):
```json
{
  "id": 1,
  "title": "My first post",
  "content": "Hello, this is my first blog post!",
  "published": true,
  "created_at": "...",
  "updated_at": "...",
  "author_id": 1,
  "author": null
}
```

### Test 2: List of Posts

**GET /posts**

### Test 3: Filtering

**GET /posts?published=true**

**GET /posts?author_id=1**

### Test 4: User's Posts

**GET /users/1/posts**

All posts by user with id=1.

---

# Part 4: Comments (Comment)

## 4.1 Adding Comment Model

Add to `models.py`:

```python
class Comment(OxydeModel):
    """Comment on a post."""

    id: int | None = Field(default=None, db_pk=True)
    content: str
    created_at: datetime | None = Field(default=None, db_default="CURRENT_TIMESTAMP")

    # FK to post
    post: Post | None = Field(default=None, db_on_delete="CASCADE")
    # FK to comment author
    author: User | None = Field(default=None, db_on_delete="CASCADE")

    class Meta:
        is_table = True
        table_name = "comments"
```

## 4.2 Adding Reverse FK to Post

To load comments together with a post, add to the `Post` model:

```python
class Post(OxydeModel):
    """Blog post."""

    id: int | None = Field(default=None, db_pk=True)
    title: str
    content: str
    published: bool = Field(default=False)
    created_at: datetime | None = Field(default=None, db_default="CURRENT_TIMESTAMP")
    updated_at: datetime | None = Field(default=None, db_default="CURRENT_TIMESTAMP")

    author: User | None = Field(default=None, db_on_delete="CASCADE")

    # Reverse relationship — list of comments
    comments: list["Comment"] = Field(default=[], db_reverse_fk="post")

    class Meta:
        is_table = True
        table_name = "posts"
```

**What is `db_reverse_fk`:**

- This is a virtual field, it doesn't create a column in the database
- `db_reverse_fk="post"` points to the `post` field in the `Comment` model
- Used with `prefetch("comments")` to load related records

## 4.3 Migration

```bash
oxyde makemigrations
oxyde migrate
```

## 4.4 Comment Routes

Create `routes/comments.py`:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models import Comment, Post, User

router = APIRouter(tags=["comments"])


class CommentCreate(BaseModel):
    content: str
    author_id: int


class CommentUpdate(BaseModel):
    content: str


# --- Comments on a Post ---

@router.get("/posts/{post_id}/comments")
async def list_post_comments(post_id: int):
    """Get comments on a post."""
    if not await Post.objects.filter(id=post_id).exists():
        raise HTTPException(status_code=404, detail="Post not found")

    return await Comment.objects.filter(post_id=post_id).join("author").order_by("created_at").all()


@router.post("/posts/{post_id}/comments", status_code=201)
async def create_comment(post_id: int, data: CommentCreate):
    """Add comment to a post."""
    if not await Post.objects.filter(id=post_id).exists():
        raise HTTPException(status_code=404, detail="Post not found")

    if not await User.objects.filter(id=data.author_id).exists():
        raise HTTPException(status_code=400, detail="Author not found")

    return await Comment.objects.create(
        content=data.content,
        post_id=post_id,
        author_id=data.author_id
    )


# --- Operations on Specific Comment ---

@router.get("/comments/{comment_id}")
async def get_comment(comment_id: int):
    """Get comment by ID."""
    comment = await Comment.objects.filter(id=comment_id).join("author", "post").first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.patch("/comments/{comment_id}")
async def update_comment(comment_id: int, data: CommentUpdate):
    """Update comment."""
    comment = await Comment.objects.get_or_none(id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.content = data.content
    await comment.save()
    return comment


@router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(comment_id: int):
    """Delete comment."""
    count = await Comment.objects.filter(id=comment_id).delete()
    if not count:
        raise HTTPException(status_code=404, detail="Comment not found")
```

**New features:**

| Method | Description |
|--------|-------------|
| `.join("author", "post")` | Multiple JOIN — loads both author and post |
| `Comment.objects.create(post_id=..., author_id=...)` | Creating with FK using `_id` suffix |

## 4.5 Post with Comments (prefetch)

Add a new endpoint to `routes/posts.py`:

```python
@router.get("/{post_id}/full")
async def get_post_full(post_id: int):
    """Get post with all comments."""
    post = await Post.objects.filter(id=post_id).join("author").prefetch("comments").first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
```

**How `prefetch()` works:**

1. Main query is executed (SELECT * FROM posts WHERE id=...)
2. Second query is executed (SELECT * FROM comments WHERE post_id IN (...))
3. Results are combined in Python

**Difference between join and prefetch:**

| Method | How it works | When to use |
|--------|--------------|-------------|
| `join()` | LEFT JOIN in one query | FK (single object) |
| `prefetch()` | Separate query + Python merge | Reverse FK, M2M (list of objects) |

## 4.6 Connecting the Router

Update `main.py`:

```python
import uvicorn
from fastapi import FastAPI
from oxyde import db

from oxyde_config import DATABASES
from routes import users, posts, comments

app = FastAPI(
    title="Blog API",
    description="REST API for blog with Oxyde ORM",
    version="0.1.0",
    lifespan=db.lifespan(**DATABASES)
)

app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)


@app.get("/")
async def root():
    return {"message": "Blog API is running!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
```

## 4.7 Verification

### Test 1: Adding a Comment

**POST /posts/1/comments** with body:
```json
{"content": "Great post!", "author_id": 2}
```

Expected response (201):
```json
{
  "id": 1,
  "content": "Great post!",
  "created_at": "...",
  "post_id": 1,
  "author_id": 2,
  "post": null,
  "author": null
}
```

Add a few more comments.

### Test 2: List of Comments

**GET /posts/1/comments**

All comments on the post with authors.

### Test 3: Post with Comments (prefetch)

**GET /posts/1/full**

Expected response:
```json
{
  "id": 1,
  "title": "My first post",
  "content": "...",
  "published": true,
  "created_at": "...",
  "updated_at": "...",
  "author_id": 1,
  "author": {"id": 1, "username": "alice_updated", ...},
  "comments": [
    {"id": 1, "content": "Great post!", "author_id": 2, ...},
    {"id": 2, "content": "I agree!", "author_id": 1, ...}
  ]
}
```

### Test 4: Comment with Post

**GET /comments/1**

Comment with nested author and post.

---

# Part 5: Tags (Tag + PostTag)

## 5.1 Adding Tag and PostTag Models

> **Important:** The `Tag` class must be defined **above** the `Post` class in `models.py`, otherwise `list[Tag]` will cause `NameError`.

Add to `models.py` (between `User` and `Post`):

```python
class Tag(OxydeModel):
    """Tag for posts."""

    id: int | None = Field(default=None, db_pk=True)
    name: str = Field(db_unique=True)
    slug: str = Field(db_unique=True, db_index=True)

    class Meta:
        is_table = True
        table_name = "tags"


class PostTag(OxydeModel):
    """Many-to-many relationship between Post and Tag."""

    id: int | None = Field(default=None, db_pk=True)
    post: Post | None = Field(default=None, db_on_delete="CASCADE")
    tag: Tag | None = Field(default=None, db_on_delete="CASCADE")

    class Meta:
        is_table = True
        table_name = "post_tags"
        unique_together = [("post", "tag")]  # Unique pair
```

**What's new here:**

| Element | Description |
|---------|-------------|
| `unique_together` | Composite UNIQUE constraint. A tag can only be added to a post once |
| `PostTag` | Junction table for M2M relationship |

## 5.2 Adding M2M to Post

Update the `Post` model:

```python
class Post(OxydeModel):
    """Blog post."""

    id: int | None = Field(default=None, db_pk=True)
    title: str
    content: str
    published: bool = Field(default=False)
    created_at: datetime | None = Field(default=None, db_default="CURRENT_TIMESTAMP")
    updated_at: datetime | None = Field(default=None, db_default="CURRENT_TIMESTAMP")

    author: User | None = Field(default=None, db_on_delete="CASCADE")
    comments: list["Comment"] = Field(default=[], db_reverse_fk="post")

    # Many-to-Many relationship with tags
    tags: list[Tag] = Field(default=[], db_m2m=True, db_through="PostTag")

    class Meta:
        is_table = True
        table_name = "posts"
```

**M2M in Oxyde:**

- `db_m2m=True` — indicates this is an M2M relationship
- `db_through="PostTag"` — name of the junction model
- The field is virtual, used with `prefetch("tags")`

## 5.3 Migration

```bash
oxyde makemigrations
oxyde migrate
```

## 5.4 Tag Routes

Create `routes/tags.py`:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import re

from models import Tag, Post, PostTag

router = APIRouter(prefix="/tags", tags=["tags"])


class TagCreate(BaseModel):
    name: str


def slugify(text: str) -> str:
    """Simple function to create slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text


@router.get("")
async def list_tags():
    """Get all tags."""
    return await Tag.objects.order_by("name").all()


@router.post("", status_code=201)
async def create_tag(data: TagCreate):
    """Create tag."""
    slug = slugify(data.name)

    if await Tag.objects.filter(slug=slug).exists():
        raise HTTPException(status_code=400, detail="Tag already exists")

    return await Tag.objects.create(name=data.name, slug=slug)


@router.get("/{slug}")
async def get_tag(slug: str):
    """Get tag by slug."""
    tag = await Tag.objects.get_or_none(slug=slug)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.delete("/{slug}", status_code=204)
async def delete_tag(slug: str):
    """Delete tag."""
    count = await Tag.objects.filter(slug=slug).delete()
    if not count:
        raise HTTPException(status_code=404, detail="Tag not found")


@router.get("/{slug}/posts")
async def list_posts_by_tag(slug: str):
    """Get all posts with this tag."""
    tag = await Tag.objects.get_or_none(slug=slug)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Get post_id through junction table
    post_tags = await PostTag.objects.filter(tag_id=tag.id).all()
    post_ids = [pt.post_id for pt in post_tags]

    if not post_ids:
        return []

    return await Post.objects.filter(id__in=post_ids).join("author").all()
```

## 5.5 Adding Tags to Posts

Add to `routes/posts.py`:

```python
from models import Post, User, Tag, PostTag

# ... existing code ...

class PostTagUpdate(BaseModel):
    tag_ids: list[int]


@router.put("/{post_id}/tags")
async def set_post_tags(post_id: int, data: PostTagUpdate):
    """Set tags for post (replaces existing)."""
    if not await Post.objects.filter(id=post_id).exists():
        raise HTTPException(status_code=404, detail="Post not found")

    # Check that all tags exist
    existing_tags = await Tag.objects.filter(id__in=data.tag_ids).all()
    if len(existing_tags) != len(data.tag_ids):
        raise HTTPException(status_code=400, detail="One or more tags not found")

    # Remove old relationships
    await PostTag.objects.filter(post_id=post_id).delete()

    # Create new ones
    for tag_id in data.tag_ids:
        await PostTag.objects.create(post_id=post_id, tag_id=tag_id)

    return {"post_id": post_id, "tag_ids": data.tag_ids}


@router.post("/{post_id}/tags/{tag_id}", status_code=201)
async def add_tag_to_post(post_id: int, tag_id: int):
    """Add tag to post."""
    if not await Post.objects.filter(id=post_id).exists():
        raise HTTPException(status_code=404, detail="Post not found")

    if not await Tag.objects.filter(id=tag_id).exists():
        raise HTTPException(status_code=404, detail="Tag not found")

    # Check if already added
    if await PostTag.objects.filter(post_id=post_id, tag_id=tag_id).exists():
        raise HTTPException(status_code=400, detail="Tag already added to post")

    return await PostTag.objects.create(post_id=post_id, tag_id=tag_id)


@router.delete("/{post_id}/tags/{tag_id}", status_code=204)
async def remove_tag_from_post(post_id: int, tag_id: int):
    """Remove tag from post."""
    count = await PostTag.objects.filter(post_id=post_id, tag_id=tag_id).delete()
    if not count:
        raise HTTPException(status_code=404, detail="Relationship not found")
```

**New lookups:**

| Lookup | Description |
|--------|-------------|
| `id__in=[1, 2, 3]` | SQL: `id IN (1, 2, 3)` |

## 5.6 Updating List Posts Endpoint

Update `list_posts` in `routes/posts.py` to load tags:

```python
@router.get("")
async def list_posts(
    published: bool | None = Query(None, description="Filter by publication status"),
    author_id: int | None = Query(None, description="Filter by author"),
):
    """Get list of posts."""
    query = Post.objects.join("author").prefetch("tags").order_by("-created_at")

    if published is not None:
        query = query.filter(published=published)

    if author_id is not None:
        query = query.filter(author_id=author_id)

    return await query.all()
```

## 5.7 Updating Endpoints to Load Tags

Update `get_post` and `get_post_full` in `routes/posts.py` to return tags:

```python
@router.get("/{post_id}")
async def get_post(post_id: int):
    """Get post by ID."""
    post = await Post.objects.filter(id=post_id).prefetch("tags").first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get("/{post_id}/full")
async def get_post_full(post_id: int):
    """Get post with all comments."""
    post = await Post.objects.filter(id=post_id).join("author").prefetch("comments", "tags").first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
```

## 5.8 Connecting the Router

Update `main.py`:

```python
import uvicorn
from fastapi import FastAPI
from oxyde import db

from oxyde_config import DATABASES
from routes import users, posts, comments, tags

app = FastAPI(
    title="Blog API",
    description="REST API for blog with Oxyde ORM",
    version="0.1.0",
    lifespan=db.lifespan(**DATABASES)
)

app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(tags.router)


@app.get("/")
async def root():
    return {"message": "Blog API is running!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
```

## 5.9 Verification

### Test 1: Creating Tags

**POST /tags**
```json
{"name": "Python"}
```

```json
{"name": "FastAPI"}
```

```json
{"name": "Oxyde"}
```

### Test 2: List of Tags

**GET /tags**

```json
[
  {"id": 1, "name": "FastAPI", "slug": "fastapi"},
  {"id": 2, "name": "Oxyde", "slug": "oxyde"},
  {"id": 3, "name": "Python", "slug": "python"}
]
```

### Test 3: Adding Tags to Post

**POST /posts/1/tags/1** — add FastAPI tag

**POST /posts/1/tags/3** — add Python tag

### Test 4: Viewing Post with Tags

**GET /posts/1**

```json
{
  "id": 1,
  "title": "My first post",
  "...",
  "tags": [
    {"id": 1, "name": "FastAPI", "slug": "fastapi"},
    {"id": 3, "name": "Python", "slug": "python"}
  ]
}
```

### Test 5: Posts by Tag

**GET /tags/python/posts**

All posts with Python tag.

### Test 6: Replacing Tags

**PUT /posts/1/tags**
```json
{"tag_ids": [2, 3]}
```

Now the post has Oxyde and Python tags (FastAPI removed).

---

# Part 6: Search and Filtering

## 6.1 Q Expressions for Complex Queries

Add to `routes/posts.py`:

```python
from oxyde import Q

@router.get("/search")
async def search_posts(
    q: str = Query(..., min_length=2, description="Search query"),
):
    """Search posts by title and content."""
    posts = await Post.objects.filter(
        Q(title__icontains=q) | Q(content__icontains=q)
    ).join("author").prefetch("tags").order_by("-created_at").all()

    return posts
```

**Q expressions:**

| Operator | Description |
|----------|-------------|
| `Q(...) \| Q(...)` | OR — at least one condition |
| `Q(...) & Q(...)` | AND — both conditions |
| `~Q(...)` | NOT — negation |
| `__icontains` | ILIKE '%...%' — case-insensitive search |

## 6.2 Extended Filtering

Update `list_posts` for more flexible filtering:

```python
from datetime import datetime

@router.get("")
async def list_posts(
    published: bool | None = Query(None, description="Filter by publication status"),
    author_id: int | None = Query(None, description="Filter by author"),
    created_after: datetime | None = Query(None, description="Posts after date"),
    created_before: datetime | None = Query(None, description="Posts before date"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Records per page"),
):
    """Get list of posts with filtering and pagination."""
    query = Post.objects.join("author").prefetch("tags")

    # Filters
    if published is not None:
        query = query.filter(published=published)

    if author_id is not None:
        query = query.filter(author_id=author_id)

    if created_after is not None:
        query = query.filter(created_at__gte=created_after)

    if created_before is not None:
        query = query.filter(created_at__lt=created_before)

    # Count total
    total = await query.count()

    # Pagination
    offset = (page - 1) * per_page
    posts = await query.order_by("-created_at").offset(offset).limit(per_page).all()

    return {
        "items": posts,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    }
```

**Date lookups:**

| Lookup | SQL | Description |
|--------|-----|-------------|
| `created_at__gte=date` | `>= date` | After or equal |
| `created_at__lt=date` | `< date` | Before |
| `created_at__year=2024` | `EXTRACT(YEAR ...)` | By year |
| `created_at__between=[d1, d2]` | `BETWEEN` | In range |

## 6.3 Statistics

Add a statistics endpoint:

```python
@router.get("/stats")
async def posts_stats():
    """Post statistics."""
    total = await Post.objects.count()
    published = await Post.objects.filter(published=True).count()
    drafts = await Post.objects.filter(published=False).count()

    return {
        "total": total,
        "published": published,
        "drafts": drafts
    }
```

## 6.4 Verification

### Test 1: Search

**GET /posts/search?q=first**

Will find posts containing "first" in title or content.

### Test 2: Pagination

**GET /posts?page=1&per_page=5**

```json
{
  "items": [...],
  "total": 12,
  "page": 1,
  "per_page": 5,
  "pages": 3
}
```

### Test 3: Date Filter

**GET /posts?created_after=2024-01-01T00:00:00**

### Test 4: Combined Filter

**GET /posts?published=true&author_id=1&page=1&per_page=10**

### Test 5: Statistics

**GET /posts/stats**

```json
{"total": 5, "published": 3, "drafts": 2}
```

---

# Part 7: Transactions and Final Touches

## 7.1 Atomic Post Creation with Tags

Add to `routes/posts.py`:

```python
from oxyde.db import transaction

class PostCreateWithTags(BaseModel):
    title: str
    content: str
    author_id: int
    published: bool = False
    tag_ids: list[int] = []


@router.post("/with-tags", status_code=201)
async def create_post_with_tags(data: PostCreateWithTags):
    """
    Create post with tags atomically.

    If something goes wrong — everything is rolled back.
    """
    # Checks before transaction
    if not await User.objects.filter(id=data.author_id).exists():
        raise HTTPException(status_code=400, detail="Author not found")

    if data.tag_ids:
        existing_tags = await Tag.objects.filter(id__in=data.tag_ids).all()
        if len(existing_tags) != len(data.tag_ids):
            raise HTTPException(status_code=400, detail="One or more tags not found")

    # Atomic operation
    async with transaction.atomic():
        # Create post
        post = await Post.objects.create(
            title=data.title,
            content=data.content,
            author_id=data.author_id,
            published=data.published
        )

        # Add tags
        for tag_id in data.tag_ids:
            await PostTag.objects.create(post_id=post.id, tag_id=tag_id)

    return post
```

**Transactions in Oxyde:**

```python
from oxyde.db import transaction

async with transaction.atomic():
    # All operations inside — one transaction
    # On exception — automatic ROLLBACK
    # On success — automatic COMMIT
```

## 7.2 Nested Transactions (savepoints)

```python
async with transaction.atomic():
    user = await User.objects.create(username="alice", email="alice@test.com")

    try:
        async with transaction.atomic():  # Savepoint
            await Post.objects.create(title="Test", content="Content", author_id=user.id)
            raise ValueError("Error!")
    except ValueError:
        pass  # Only Post is rolled back

    # User will still be created
```

## 7.3 Comment Counter for User

Add an endpoint for user statistics in `routes/users.py`:

```python
from models import User, Post, Comment

@router.get("/{user_id}/stats")
async def get_user_stats(user_id: int):
    """User statistics."""
    user = await User.objects.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    posts_count = await Post.objects.filter(author_id=user_id).count()
    comments_count = await Comment.objects.filter(author_id=user_id).count()
    published_posts = await Post.objects.filter(author_id=user_id, published=True).count()

    return {
        "user": user,
        "posts_count": posts_count,
        "published_posts_count": published_posts,
        "comments_count": comments_count
    }
```

## 7.4 Complete models.py File

For reference — final version of `models.py`:

```python
from datetime import datetime
from oxyde import OxydeModel, Field


class User(OxydeModel):
    """Blog user."""

    id: int | None = Field(default=None, db_pk=True)
    username: str = Field(db_unique=True, db_index=True)
    email: str = Field(db_unique=True)
    created_at: datetime | None = Field(default=None, db_default="CURRENT_TIMESTAMP")

    class Meta:
        is_table = True
        table_name = "users"


class Tag(OxydeModel):
    """Tag for posts."""

    id: int | None = Field(default=None, db_pk=True)
    name: str = Field(db_unique=True)
    slug: str = Field(db_unique=True, db_index=True)

    class Meta:
        is_table = True
        table_name = "tags"


class Post(OxydeModel):
    """Blog post."""

    id: int | None = Field(default=None, db_pk=True)
    title: str
    content: str
    published: bool = Field(default=False)
    created_at: datetime | None = Field(default=None, db_default="CURRENT_TIMESTAMP")
    updated_at: datetime | None = Field(default=None, db_default="CURRENT_TIMESTAMP")

    author: User | None = Field(default=None, db_on_delete="CASCADE")
    comments: list["Comment"] = Field(default=[], db_reverse_fk="post")
    tags: list[Tag] = Field(default=[], db_m2m=True, db_through="PostTag")

    class Meta:
        is_table = True
        table_name = "posts"


class Comment(OxydeModel):
    """Comment on a post."""

    id: int | None = Field(default=None, db_pk=True)
    content: str
    created_at: datetime | None = Field(default=None, db_default="CURRENT_TIMESTAMP")

    post: Post | None = Field(default=None, db_on_delete="CASCADE")
    author: User | None = Field(default=None, db_on_delete="CASCADE")

    class Meta:
        is_table = True
        table_name = "comments"


class PostTag(OxydeModel):
    """Many-to-many relationship between Post and Tag."""

    id: int | None = Field(default=None, db_pk=True)
    post: Post | None = Field(default=None, db_on_delete="CASCADE")
    tag: Tag | None = Field(default=None, db_on_delete="CASCADE")

    class Meta:
        is_table = True
        table_name = "post_tags"
        unique_together = [("post", "tag")]
```

## 7.5 Verification

### Test 1: Creating Post with Tags (transaction)

**POST /posts/with-tags**
```json
{
  "title": "New post with tags",
  "content": "This post was created atomically with tags",
  "author_id": 1,
  "published": true,
  "tag_ids": [1, 2]
}
```

### Test 2: User Statistics

**GET /users/1/stats**

```json
{
  "user": {"id": 1, "username": "alice_updated", ...},
  "posts_count": 3,
  "published_posts_count": 2,
  "comments_count": 1
}
```

---

# Summary

## What We Learned

1. **Models** — defining with `OxydeModel`, `Field`, `Meta`
2. **Migrations** — `oxyde makemigrations` and `oxyde migrate`
3. **Stub files** — auto-generating `.pyi` for typing and IDE autocompletion
4. **CRUD** — `create()`, `all()`, `get_or_none()`, `save()`, `delete()`
5. **Foreign Keys** — `db_on_delete`, automatic `_id` columns
6. **Joins** — `join()` for eager loading related models
7. **Reverse FK** — `db_reverse_fk` and `prefetch()`
8. **Many-to-Many** — `db_m2m`, `db_through`, junction tables
9. **Filtering** — lookups (`__gte`, `__icontains`, `__in`)
10. **Q expressions** — complex conditions with OR, AND, NOT
11. **Pagination** — `offset()`, `limit()`, `count()`
12. **Transactions** — `transaction.atomic()` for atomic operations
13. **SQL defaults** — `db_default="CURRENT_TIMESTAMP"`

## API Reference

### Users

| Method | Path | Description |
|--------|------|-------------|
| GET | `/users` | List of users |
| GET | `/users/{id}` | User by ID |
| POST | `/users` | Create user |
| PATCH | `/users/{id}` | Update user |
| DELETE | `/users/{id}` | Delete user |
| GET | `/users/{id}/posts` | User's posts |
| GET | `/users/{id}/stats` | User statistics |

### Posts

| Method | Path | Description |
|--------|------|-------------|
| GET | `/posts` | List of posts (with pagination) |
| GET | `/posts/search?q=` | Search posts |
| GET | `/posts/stats` | Post statistics |
| GET | `/posts/{id}` | Post by ID |
| GET | `/posts/{id}/full` | Post with comments |
| POST | `/posts` | Create post |
| POST | `/posts/with-tags` | Create post with tags |
| PATCH | `/posts/{id}` | Update post |
| DELETE | `/posts/{id}` | Delete post |
| PUT | `/posts/{id}/tags` | Set tags |
| POST | `/posts/{id}/tags/{tag_id}` | Add tag |
| DELETE | `/posts/{id}/tags/{tag_id}` | Remove tag |

### Comments

| Method | Path | Description |
|--------|------|-------------|
| GET | `/posts/{id}/comments` | Comments on post |
| POST | `/posts/{id}/comments` | Add comment |
| GET | `/comments/{id}` | Comment by ID |
| PATCH | `/comments/{id}` | Update comment |
| DELETE | `/comments/{id}` | Delete comment |

### Tags

| Method | Path | Description |
|--------|------|-------------|
| GET | `/tags` | List of tags |
| POST | `/tags` | Create tag |
| GET | `/tags/{slug}` | Tag by slug |
| DELETE | `/tags/{slug}` | Delete tag |
| GET | `/tags/{slug}/posts` | Posts with tag |

---

## Useful Links

- [Oxyde Documentation](https://oxyde.readthedocs.io/)
- [GitHub Oxyde](https://github.com/mr-fatalyst/oxyde)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## License

MIT License
