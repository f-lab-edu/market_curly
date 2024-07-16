import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_successfully(client: AsyncClient):
    # when
    response = await client.get("/health")

    # then
    assert response.status_code == status.HTTP_200_OK
