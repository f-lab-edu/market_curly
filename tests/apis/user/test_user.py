import pytest
from fastapi import status
from httpx import AsyncClient

from src.models.repository import UserRepository
from src.models.user import Buyer, Seller, User, UserType
from src.service.session import SessionService
from src.service.user import UserService


# 'POST /register' API가 판매자(Seller)를 성공적으로 등록한다.
@pytest.mark.asyncio
async def test_register_seller_successfully(client: AsyncClient, mocker):
    mock_seller_data = {
        "email": "test@example.com",
        "password": "hashed_password",
        "user_type": UserType.SELLER,
        "registration_number": "000-00-00000",
        "brand_name": "테스트",
        "contact_number": "0000-0000",
    }
    created_user = User(
        id=1,
        email=mock_seller_data["email"],
        password=mock_seller_data["password"],
        user_type=mock_seller_data["user_type"],
    )
    created_seller = Seller(
        id=1,
        user_id=created_user.id,
        registration_number=mock_seller_data["registration_number"],
        brand_name=mock_seller_data["brand_name"],
        contact_number=mock_seller_data["contact_number"],
        user=created_user,
    )

    mocker.patch.object(UserRepository, "get_user_by_email", return_value=None)
    mocker.patch.object(
        UserRepository, "validate_seller_unique_data", return_value=True
    )
    mocker.patch.object(
        UserService, "hash_password", return_value=mock_seller_data["password"]
    )
    mocker.patch.object(
        UserRepository, "save_entity", side_effect=[created_user, created_seller]
    )
    mocker.patch(
        "src.apis.user.register_user_handler.add_email_to_stream", return_value=None
    )

    response = await client.post("/register", json=mock_seller_data)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data == {
        "user_type": created_user.user_type,
        "email": created_user.email,
        "name": created_seller.brand_name,
    }


# 'POST /register' API가 중복된 사업자등록번호를 사용하는 경우 400을 응답한다.
@pytest.mark.asyncio
async def test_register_seller_with_duplicate_registration_number(
    client: AsyncClient, mocker
):
    mock_seller_data = {
        "email": "test@example.com",
        "password": "hashed_password",
        "user_type": UserType.SELLER,
        "registration_number": "000-00-00000",  # 이미 등록된 사업자등록번호
        "brand_name": "테스트",
        "contact_number": "0000-0000",
    }

    # 중복된 사업자등록번호를 가진 판매자가 이미 존재한다고 가정
    mocker.patch.object(
        UserRepository, "validate_seller_unique_data", return_value=False
    )

    response = await client.post("/register", json=mock_seller_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Seller data validation failed."}


# 'POST /register' API가 구매자(Buyer)를 성공적으로 등록한다.
@pytest.mark.asyncio
async def test_register_buyer_successfully(client: AsyncClient, mocker):
    mock_buyer_data = {
        "email": "test@example.com",
        "password": "hashed_password",
        "user_type": UserType.BUYER,
        "name": "사용자",
        "phone_number": "010-0000-0000",
        "address": "xx도 oo시 xx동",
    }
    created_user = User(
        id=1,
        email=mock_buyer_data["email"],
        password=mock_buyer_data["password"],
        user_type=mock_buyer_data["user_type"],
    )
    created_buyer = Buyer(
        id=1,
        user_id=created_user.id,
        name=mock_buyer_data["name"],
        phone_number=mock_buyer_data["phone_number"],
        address=mock_buyer_data["address"],
        user=created_user,
    )

    mocker.patch.object(UserRepository, "get_user_by_email", return_value=None)
    mocker.patch.object(
        UserRepository, "validate_seller_unique_data", return_value=True
    )
    mocker.patch.object(
        UserService, "hash_password", return_value=mock_buyer_data["password"]
    )
    mocker.patch.object(
        UserRepository, "save_entity", side_effect=[created_user, created_buyer]
    )
    mocker.patch(
        "src.apis.user.register_user_handler.add_email_to_stream", return_value=None
    )

    response = await client.post("/register", json=mock_buyer_data)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data == {
        "user_type": created_user.user_type,
        "email": created_user.email,
        "name": created_buyer.name,
    }


# 'POST /register' API가 이미 등록된 이메일을 사용하는 경우 400을 반환한다.
@pytest.mark.asyncio
async def test_register_user_with_existing_email(client: AsyncClient, mocker):
    mock_user_data = {
        "email": "test@example.com",  # 이미 등록된 이메일
        "password": "hashed_password",
        "user_type": UserType.BUYER,
        "name": "사용자",
        "phone_number": "010-0000-0000",
        "address": "xx도 oo시 xx동",
    }
    existing_user = User(id=1, email="test@example.com")

    # 중복된 이메일을 가진 사용자가 이미 존재한다고 가정
    mocker.patch.object(UserRepository, "get_user_by_email", return_value=existing_user)

    response = await client.post("/register", json=mock_user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# 'POST /login' API가 성공적으로 로그인한다.
@pytest.mark.asyncio
async def test_login_user_successfully(client: AsyncClient, mocker):
    mock_login_data = {"email": "test@example.com", "password": "hashed_password"}
    user: User = User(
        id=1,
        email=mock_login_data["email"],
        password=mock_login_data["password"],
        user_type=UserType.BUYER,
    )
    created_session_id = "mock_session_id"

    mocker.patch.object(UserRepository, "get_user_by_email", return_value=user)
    mocker.patch.object(UserService, "verify_password", return_value=True)
    mocker.patch.object(
        SessionService, "create_session", return_value=created_session_id
    )

    response = await client.post("/login", json=mock_login_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Login successful"}
    assert response.cookies["session_id"] == created_session_id


# 'POST /login' API가 잘못된 비밀번호를 입력하는 경우 401을 반환한다.
@pytest.mark.asyncio
async def test_login_user_invalid_password(client: AsyncClient, mocker):
    mock_login_data = {
        "email": "test@example.com",
        "password": "wrong_password",  # 잘못된 비밀번호
    }
    user: User = User(
        id=1,
        email=mock_login_data["email"],
        password="hashed_password",
        user_type=UserType.BUYER,
    )

    mocker.patch.object(UserRepository, "get_user_by_email", return_value=user)
    mocker.patch.object(UserService, "verify_password", return_value=False)

    response = await client.post("/login", json=mock_login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not Authorized"}


# 'POST /logout' API가 성공적으로 로그아웃한다.
@pytest.mark.asyncio
async def test_logout_user_successfully(client: AsyncClient, mocker):
    mock_session_id = "valid_session_id"
    mock_login_user_data = {"user_id": 1, "user_type": UserType.BUYER}

    mocker.patch.object(
        SessionService, "get_session", return_value=mock_login_user_data
    )
    mocker.patch.object(SessionService, "delete_session")

    response = await client.post("/logout", cookies={"session_id": mock_session_id})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Logout successful"}


# 'POST /logout' API가 유효하지 않은 세션 ID의 경우 404를 반환한다.
@pytest.mark.asyncio
async def test_logout_user_invalid_session_id(client: AsyncClient, mocker):
    invalid_session_id = "invalid_session_id"

    mocker.patch.object(SessionService, "get_session", return_value=None)

    response = await client.post("/logout", cookies={"session_id": invalid_session_id})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Session Not Found"}


# 'GET /me' API가 판매자(Seller) 정보를 성공적으로 반환한다.
@pytest.mark.asyncio
async def test_get_seller_info_successfully(client: AsyncClient, mocker):
    mock_session_id = "valid_session_id"
    mock_user = User(
        id=1,
        email="test@example.com",
        password="hashed_password",
        user_type=UserType.SELLER,
    )
    mock_seller_info = Seller(
        id=1,
        user_id=mock_user.id,
        registration_number="000-00-00000",
        brand_name="테스트 브랜드",
        contact_number="0000-0000",
        user=mock_user,
    )

    mocker.patch.object(
        SessionService,
        "get_session",
        return_value={"user_id": mock_user.id, "user_type": mock_user.user_type},
    )
    mocker.patch.object(UserRepository, "get_user_by_id", return_value=mock_user)

    response = await client.get("/me", cookies={"session_id": mock_session_id})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == {
        "email": mock_user.email,
        "registration_number": mock_seller_info.registration_number,
        "brand_name": mock_seller_info.brand_name,
        "contact_number": mock_seller_info.contact_number,
    }


# 'GET /me' API가 구매자(Buyer) 정보를 성공적으로 반환한다.
@pytest.mark.asyncio
async def test_get_buyer_info_successfully(client: AsyncClient, mocker):
    mock_session_id = "valid_session_id"
    mock_user = User(
        id=1,
        email="test@example.com",
        password="hashed_password",
        user_type=UserType.BUYER,
    )
    mock_buyer_info = Buyer(
        id=1,
        user_id=mock_user.id,
        name="사용자",
        phone_number="010-0000-0000",
        address="xx도 oo시 xx동",
        user=mock_user,
    )

    mocker.patch.object(
        SessionService,
        "get_session",
        return_value={"user_id": mock_user.id, "user_type": mock_user.user_type},
    )
    mocker.patch.object(UserRepository, "get_user_by_id", return_value=mock_user)

    response = await client.get("/me", cookies={"session_id": mock_session_id})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == {
        "email": mock_user.email,
        "name": mock_buyer_info.name,
        "phone_number": mock_buyer_info.phone_number,
        "address": mock_buyer_info.address,
    }


# 'GET /me' API가 세션 ID가 유효하지 않은 경우 404를 반환한다.
@pytest.mark.asyncio
async def test_get_user_info_invalid_session_id(client: AsyncClient, mocker):
    invalid_session_id = "invalid_session_id"

    mocker.patch.object(SessionService, "get_session", return_value=None)

    response = await client.get("/me", cookies={"session_id": invalid_session_id})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Session Not Found"}
