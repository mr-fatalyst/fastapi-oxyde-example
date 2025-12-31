from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from oxyde import Q
from oxyde.db import transaction

from models import Post, Tag, PostTag, User

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


class PostTagUpdate(BaseModel):
    tag_ids: list[int]


class PostCreateWithTags(BaseModel):
    title: str
    content: str
    author_id: int
    published: bool = False
    tag_ids: list[int] = []


# --- Endpoints ---

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


@router.get("/search")
async def search_posts(
    q: str = Query(..., min_length=2, description="Search query"),
):
    """Search posts by title and content."""
    posts = await Post.objects.filter(
        Q(title__icontains=q) | Q(content__icontains=q)
    ).join("author").prefetch("tags").order_by("-created_at").all()

    return posts


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
