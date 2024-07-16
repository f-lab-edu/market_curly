import datetime
from typing import Annotated

from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apis.dependencies import get_session
from src.models.post import Post


class GetPostResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime.datetime


async def handler(
    post_id: int, session: Annotated[AsyncSession, Depends(get_session)]
) -> GetPostResponse:
    post = await session.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return GetPostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        created_at=post.created_at,
    )
