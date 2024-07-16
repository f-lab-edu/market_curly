from fastapi import APIRouter, status

from src.apis.posts import create_post, get_post, get_posts

post_router = APIRouter(tags=["posts"])

post_router.add_api_route(
    methods=["POST"],
    path="/posts",
    endpoint=create_post.handler,
    response_model=create_post.CreatePostResponse,
    status_code=status.HTTP_201_CREATED,
)
post_router.add_api_route(
    methods=["GET"],
    path="/posts",
    endpoint=get_posts.handler,
    response_model=list[get_posts.GetPostResponse],
    status_code=status.HTTP_200_OK,
)

post_router.add_api_route(
    methods=["GET"],
    path="/posts/{post_id}",
    endpoint=get_post.handler,
    response_model=get_post.GetPostResponse,
    status_code=status.HTTP_200_OK,
)
