import pytest
from fastapi import status
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.post import Post


# `GET /posts` API가 성공적으로 동작한다.
@pytest.mark.asyncio
async def test_get_posts_successfully(client: AsyncClient, session: AsyncSession):
    # given
    # 서버 내에 여러 개의 Post 데이터가 저장되어 있다.
    post_1 = Post(
        title="title 1",
        content="content 1",
    )
    post_2 = Post(
        title="title 2",
        content="content 2",
    )
    session.add_all([post_1, post_2])
    await session.commit()
    await session.refresh(post_1)
    await session.refresh(post_2)

    # when
    # `GET /posts` API를 호출한다.
    response = await client.get("/posts")

    # then
    # 응답 상태 코드가 200이어야 한다.
    assert response.status_code == status.HTTP_200_OK

    # 응답 본문에는 id가 큰 순서대로 Post 데이터가 포함되어 있어야 한다.
    data = response.json()
    assert data == [
        {
            "id": post_2.id,
            "title": post_2.title,
            "content": post_2.content,
            "created_at": post_2.created_at.isoformat(),
        },
        {
            "id": post_1.id,
            "title": post_1.title,
            "content": post_1.content,
            "created_at": post_1.created_at.isoformat(),
        },
    ]
