import asyncio
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from aiosmtplib import SMTP

from src.elastic_client import get_elasticsearch_client
from src.redis_client import get_task_redis_client

task_redis = get_task_redis_client()
es = get_elasticsearch_client()


async def process_tasks():
    while True:
        try:
            result = await task_redis.xreadgroup(
                groupname="task_group",
                consumername="worker_1",
                streams={"task_stream": ">"},
                count=1,
                block=1000,
            )

            if result:
                stream, messages = result[0]
                for message_id, message_data in messages:
                    task_type = message_data.get("type")

                    if task_type == "sync_product":
                        data = message_data.get("data")
                        if data:
                            product_info = json.loads(data)
                            await sync_product_to_elasticsearch(product_info)
                    elif task_type == "send_email":
                        data = message_data.get("data")
                        if data:
                            user_info = json.loads(data)
                            await send_email(user_info["email"], user_info["name"])

                    # 메시지 처리 완료 후 ack (완료 처리함)
                    await task_redis.xack("task_stream", "task_group", message_id)

        except Exception as e:
            print(f"Error processing tasks: {e}")
        await asyncio.sleep(1)  # 잠시 대기 후 다음 메시지 확인


async def add_product_to_stream(product_info: dict):
    await task_redis.xadd(
        "task_stream", {"type": "sync_product", "data": json.dumps(product_info)}
    )


async def add_email_to_stream(user_info: dict):
    await task_redis.xadd(
        "task_stream", {"type": "send_email", "data": json.dumps(user_info)}
    )


async def sync_product_to_elasticsearch(product_info: dict):
    try:
        await es.index(
            index="products",
            id=product_info["id"],
            body=product_info,
            refresh="wait_for",
        )
    except Exception as e:
        print(f"Error syncing product to Elasticsearch: {e}")


async def send_email(email: str, name: str):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = email
    msg["Subject"] = "Welcome to our service!"

    msg.attach(MIMEText(f"{name}, Thank you for register.", "plain"))

    try:
        async with SMTP(hostname=smtp_server, port=smtp_port) as client:
            if smtp_port == 587:
                await client.starttls()  # TLS 암호화 시작
            await client.login(smtp_user, smtp_password)  # 로그인
            await client.send_message(msg)  # 이메일 전송
        print(f"Email sent to {email}")
    except Exception as e:
        print(f"Error sending email: {e}")
