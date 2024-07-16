from typing import Annotated

from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apis.dependencies import get_session
from src.apis.posts.get_post import GetPostResponse
from src.models.post import Post


async def handler(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> list[GetPostResponse]:
    posts = (await session.exec(select(Post))).all()
    return sorted(
        [
            GetPostResponse(
                id=post.id,
                title=post.title,
                content=post.content,
                created_at=post.created_at,
            )
            for post in posts
        ],
        key=lambda post: -post.id,
    )
