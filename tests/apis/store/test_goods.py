import pytest
from fastapi import status
from httpx import AsyncClient

from src.models.product import Product, TertiaryCategory
from src.models.repository import ProductRepository
from src.models.user import Seller


# 'GET /goods' API가 성공적으로 동작한다.
@pytest.mark.asyncio
async def test_goods_list_successfully(client: AsyncClient, mocker):
    seller_1 = Seller(id=1, brand_name="판매자1")
    seller_2 = Seller(id=2, brand_name="판매자2")

    product_1 = Product(
        id=1,
        seller_id=1,
        product_name="테스트 상품1",
        category_id=1,
        price=100,
        inventory_quantity=10,
        use_status=True,
        seller=seller_1,
    )
    product_2 = Product(
        id=2,
        seller_id=2,
        product_name="테스트 상품2",
        category_id=2,
        price=200,
        inventory_quantity=20,
        use_status=False,
        seller=seller_2,
    )
    product_3 = Product(
        id=3,
        seller_id=2,
        product_name="테스트 상품3",
        category_id=3,
        price=300,
        inventory_quantity=30,
        use_status=True,
        seller=seller_2,
    )

    # get_product_list 메서드가 use_status=True인 상품만 반환되도록 설정
    mocker.patch.object(
        ProductRepository, "get_product_list", return_value=[product_1, product_3]
    )

    response = await client.get("/goods")

    assert response.status_code == status.HTTP_200_OK

    # use_status=True인 상품들만 포함되어야 하며, id 값이 큰 순서대로 데이터가 포함되어야 한다.
    data = response.json()
    assert data == [
        {
            "id": product_3.id,
            "brand_name": product_3.seller.brand_name,
            "product_name": product_3.product_name,
            "price": product_3.price,
            "discounted_price": product_3.discounted_price,
        },
        {
            "id": product_1.id,
            "brand_name": product_1.seller.brand_name,
            "product_name": product_1.product_name,
            "price": product_1.price,
            "discounted_price": product_1.discounted_price,
        },
    ]


# 'GET /goods?category=' 유효한 쿼리 스트링이 주어졌을 때, 필터링된 결과가 반환된다.
@pytest.mark.asyncio
async def test_goods_list_with_valid_category(client: AsyncClient, mocker):
    mock_seller = Seller(id=1, brand_name="판매자 브랜드")
    mock_product = Product(
        id=1,
        seller_id=1,
        product_name="테스트 상품",
        category_id=1,
        price=100,
        seller=mock_seller,
    )

    mocker.patch.object(
        ProductRepository, "get_product_list_by_category", return_value=[mock_product]
    )

    response = await client.get("/goods?category=tertiary1")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data == [
        {
            "id": mock_product.id,
            "brand_name": mock_product.seller.brand_name,
            "product_name": mock_product.product_name,
            "price": mock_product.price,
            "discounted_price": mock_product.discounted_price,
        }
    ]


# 'GET /goods?category=' 유효하지 않은 쿼리 스트링이 주어지면 400을 반환한다.
@pytest.mark.asyncio
async def test_goods_list_with_invalid_category(client: AsyncClient, mocker):
    response = await client.get("/goods?category=invalid-query")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Invalid query format."}


# 'GET /goods/{goods_id}' API가 성공적으로 동작한다.
@pytest.mark.asyncio
async def test_get_goods_by_id_successfully(client: AsyncClient, mocker):
    seller = Seller(id=1, brand_name="판매자", contact_number="000-000-0000")
    category = TertiaryCategory(id=1, name="카테고리")

    product = Product(
        id=1,
        seller_id=1,
        product_name="테스트 상품",
        category_id=1,
        price=100,
        inventory_quantity=10,
        seller=seller,
        category=category,
    )

    mocker.patch.object(ProductRepository, "get_product_by_id", return_value=product)

    response = await client.get(f"/goods/{product.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data == {
        "id": product.id,
        "category": product.category.name,
        "brand_name": product.seller.brand_name,
        "product_name": product.product_name,
        "price": product.price,
        "discounted_price": product.discounted_price,
        "capacity": product.capacity,
        "key_specification": product.key_specification,
        "expiration_date": product.expiration_date,
        "how_to_use": product.how_to_use,
        "ingredient": product.ingredient,
        "caution": product.caution,
        "contact_number": product.seller.contact_number,
    }


# 'GET /goods/{goods_id}' API가 존재하지 않는 ID에 대해서는 404를 응답한다.
@pytest.mark.asyncio
async def test_get_goods_by_id_not_found(client: AsyncClient, mocker):
    non_existent_goods_id = 0  # 존재하지 않는 ID

    mocker.patch.object(ProductRepository, "get_product_by_id", return_value=None)

    response = await client.get(f"/goods/{non_existent_goods_id}")

    # 상품을 찾지 못한 경우 응답 상태 코드가 404
    assert response.status_code == status.HTTP_404_NOT_FOUND
