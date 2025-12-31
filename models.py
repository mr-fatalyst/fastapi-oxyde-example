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

    # Many-to-Many relationship with tags
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
