import pytest
from fastapi import status
from httpx import AsyncClient

from src.models.product import Product, TertiaryCategory
from src.models.repository import ProductRepository, UserRepository
from src.models.user import Seller, User, UserType
from src.service.session import SessionService


# 'POST /products/' API가 성공적으로 동작한다.
@pytest.mark.asyncio
async def test_create_product_successfully(client: AsyncClient, mocker):
    mock_session_id = "valid_session_id"
    mock_user = User(
        id=1, email="test@example.com", password="hashed_pw", user_type=UserType.SELLER
    )
    mock_seller = Seller(
        id=1,
        user_id=1,
        registration_number="111-11-11111",
        brand_name="TestBrand",
        contact_number="000-000-0000",
        user=mock_user,
    )
    product_data = {
        "seller_id": mock_seller.id,
        "product_name": "테스트 상품",
        "category_id": 1,
        "price": 10000,
    }
    created_product = Product(id=1, **product_data)

    mocker.patch.object(
        SessionService,
        "get_session",
        return_value={"user_id": 1, "user_type": UserType.SELLER},
    )
    mocker.patch("src.service.auth.verify_seller", return_value=1)
    mocker.patch.object(UserRepository, "get_user_by_id", return_value=mock_user)
    mocker.patch.object(
        ProductRepository, "create_product", return_value=created_product
    )

    response = await client.post(
        "/products", json=product_data, cookies={"session_id": mock_session_id}
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data == {
        "id": created_product.id,
        "product_name": created_product.product_name,
        "price": created_product.price,
        "discounted_price": created_product.discounted_price,
    }


# 'POST /products/' API가 잘못된 데이터를 받으면 422를 응답한다.
@pytest.mark.asyncio
async def test_create_product_with_invalid_data(client: AsyncClient, mocker):
    mock_session_id = "valid_session_id"
    mocker.patch("src.service.auth.verify_seller", return_value=1)

    # 잘못된 요청 데이터 (예: price가 없는 경우)
    invalid_product_data = {
        "id": 1,
        "product_name": "테스트 상품",
        # "price": 10000,
        "discounted_price": 8000,
    }

    response = await client.post(
        "/products", json=invalid_product_data, cookies={"session_id": mock_session_id}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# 'GET /products/{product_id}' API가 성공적으로 동작한다.
@pytest.mark.asyncio
async def test_get_product_by_id_successfully(client: AsyncClient, mocker):
    mock_session_id = "valid_session_id"
    mock_user = User(
        id=1, email="test@example.com", password="hashed_pw", user_type=UserType.SELLER
    )
    mock_seller = Seller(
        id=1,
        user_id=1,
        registration_number="111-11-11111",
        brand_name="TestBrand",
        contact_number="000-000-0000",
        user=mock_user,
    )
    mock_category = TertiaryCategory(id=1, name="카테고리")

    product = Product(
        id=1,
        seller_id=mock_seller.id,
        product_name="테스트 상품",
        category_id=mock_category.id,
        price=100,
        inventory_quantity=10,
        seller=mock_seller,
        category=mock_category,
    )

    mocker.patch.object(
        SessionService,
        "get_session",
        return_value={"user_id": 1, "user_type": UserType.SELLER},
    )
    mocker.patch("src.service.auth.verify_seller", return_value=1)
    mocker.patch.object(UserRepository, "get_user_by_id", return_value=mock_user)
    mocker.patch.object(ProductRepository, "get_product_by_id", return_value=product)

    response = await client.get(
        f"/products/{product.id}", cookies={"session_id": mock_session_id}
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data == {
        "id": product.id,
        "category": f"{product.category.name}({product.category_id})",
        "product_name": product.product_name,
        "price": product.price,
        "discounted_price": product.discounted_price,
        "capacity": product.capacity,
        "key_specification": product.key_specification,
        "expiration_date": product.expiration_date,
        "how_to_use": product.how_to_use,
        "ingredient": product.ingredient,
        "caution": product.caution,
        "inventory_quantity": product.inventory_quantity,
        "use_status": product.use_status,
    }


# 'GET /products/{product_id}' API가 존재하지 않는 ID에 대해서는 404를 응답한다.
@pytest.mark.asyncio
async def test_get_product_by_id_not_found(client: AsyncClient, mocker):
    mock_session_id = "valid_session_id"
    mocker.patch("src.service.auth.verify_seller", return_value=1)

    non_existent_product_id = 0  # 존재하지 않는 ID

    mocker.patch.object(ProductRepository, "get_product_by_id", return_value=None)

    response = await client.get(
        f"/products/{non_existent_product_id}", cookies={"session_id": mock_session_id}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


# 'PATCH /products/{product_id}' API가 성공적으로 동작한다.
@pytest.mark.asyncio
async def test_update_product_successfully(client: AsyncClient, mocker):
    mock_session_id = "valid_session_id"
    mock_user = User(
        id=1, email="test@example.com", password="hashed_pw", user_type=UserType.SELLER
    )
    mock_seller = Seller(
        id=1,
        user_id=1,
        registration_number="111-11-11111",
        brand_name="TestBrand",
        contact_number="000-000-0000",
        user=mock_user,
    )
    mock_category = TertiaryCategory(id=1, name="카테고리")

    product = Product(
        id=1,
        seller_id=mock_seller.id,
        product_name="기존 상품",
        category_id=mock_category.id,
        price=100,
        inventory_quantity=10,
        seller=mock_seller,
        category=mock_category,
    )

    update_data = {"product_name": "업데이트된 상품", "price": 50}
    update_product = Product(
        id=product.id,
        seller_id=product.seller_id,
        product_name=update_data["product_name"],
        category_id=product.category_id,
        price=update_data["price"],
        inventory_quantity=product.inventory_quantity,
        seller=product.seller,
        category=product.category,
    )

    mocker.patch.object(
        SessionService,
        "get_session",
        return_value={"user_id": 1, "user_type": UserType.SELLER},
    )
    mocker.patch("src.service.auth.verify_seller", return_value=1)
    mocker.patch.object(UserRepository, "get_user_by_id", return_value=mock_user)
    mocker.patch.object(ProductRepository, "get_product_by_id", return_value=product)
    mocker.patch.object(
        ProductRepository, "update_product", return_value=update_product
    )

    response = await client.patch(
        f"/products/{product.id}",
        json=update_data,
        cookies={"session_id": mock_session_id},
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data == {
        "id": update_product.id,
        "product_name": update_product.product_name,
        "price": update_product.price,
        "discounted_price": update_product.discounted_price,
    }


# 'PATCH /products/{product_id}' API가 존재하지 않는 ID에 대해서는 404를 응답한다.
@pytest.mark.asyncio
async def test_update_product_not_found(client: AsyncClient, mocker):
    mock_session_id = "valid_session_id"
    mocker.patch("src.service.auth.verify_seller", return_value=1)

    non_existent_product_id = 0  # 존재하지 않는 ID

    mocker.patch.object(ProductRepository, "get_product_by_id", return_value=None)

    update_data = {"price": 50}

    response = await client.patch(
        f"/products/{non_existent_product_id}",
        json=update_data,
        cookies={"session_id": mock_session_id},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


# 'DELETE /products/{product_id}' API가 성공적으로 동작한다.
@pytest.mark.asyncio
async def test_delete_product_successfully(client: AsyncClient, mocker):
    mock_session_id = "valid_session_id"
    mock_user = User(
        id=1, email="test@example.com", password="hashed_pw", user_type=UserType.SELLER
    )
    mock_seller = Seller(
        id=1,
        user_id=1,
        registration_number="111-11-11111",
        brand_name="TestBrand",
        contact_number="000-000-0000",
        user=mock_user,
    )
    mock_category = TertiaryCategory(id=1, name="카테고리")

    product = Product(
        id=1,
        seller_id=mock_seller.id,
        product_name="기존 상품",
        category_id=mock_category.id,
        price=100,
        use_status=True,  # 해당 상품 사용 가능 상태
        seller=mock_seller,
        category=mock_category,
    )

    mocker.patch.object(
        SessionService,
        "get_session",
        return_value={"user_id": 1, "user_type": UserType.SELLER},
    )
    mocker.patch("src.service.auth.verify_seller", return_value=1)
    mocker.patch.object(UserRepository, "get_user_by_id", return_value=mock_user)
    mocker.patch.object(ProductRepository, "get_product_by_id", return_value=product)
    mocker.patch.object(ProductRepository, "delete_product")

    response = await client.delete(
        f"/products/{product.id}", cookies={"session_id": mock_session_id}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


# 'DELETE /products/{product_id}' API가 존재하지 않는 ID에 대해서는 404를 응답한다.
@pytest.mark.asyncio
async def test_delete_product_not_found(client: AsyncClient, mocker):
    mock_session_id = "valid_session_id"
    mocker.patch("src.service.auth.verify_seller", return_value=1)

    non_existent_product_id = 0  # 존재하지 않는 ID

    mocker.patch.object(ProductRepository, "get_product_by_id", return_value=None)

    response = await client.delete(
        f"/products/{non_existent_product_id}", cookies={"session_id": mock_session_id}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
