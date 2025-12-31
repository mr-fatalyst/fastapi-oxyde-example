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

    return await Comment.objects.filter(
        post_id=post_id
    ).join("author").order_by("created_at").all()


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
