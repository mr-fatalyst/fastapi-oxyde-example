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
