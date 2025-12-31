from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from models import User, Post, Comment

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


@router.get("/{user_id}/posts")
async def list_user_posts(user_id: int):
    """Get all posts by user."""
    if not await User.objects.filter(id=user_id).exists():
        raise HTTPException(status_code=404, detail="User not found")

    return await Post.objects.filter(author_id=user_id).order_by("-created_at").all()


@router.get("/{user_id}/stats")
async def get_user_stats(user_id: int):
    """User statistics."""
    user = await User.objects.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    posts_count = await Post.objects.filter(author_id=user_id).count()
    comments_count = await Comment.objects.filter(author_id=user_id).count()
    published_posts = await Post.objects.filter(
        author_id=user_id, published=True
    ).count()

    return {
        "user": user,
        "posts_count": posts_count,
        "published_posts_count": published_posts,
        "comments_count": comments_count
    }
