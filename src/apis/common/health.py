from src.elastic_client import get_elasticsearch_client


def handler() -> dict:
    es_client = get_elasticsearch_client()
    if es_client.ping():
        return {"status": "Elasticsearch is connected!"}
    return {"status": "Elasticsearch connection failure"}
