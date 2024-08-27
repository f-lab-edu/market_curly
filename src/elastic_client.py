from elasticsearch import Elasticsearch

from src.config import es as es_config

es_client = Elasticsearch(
    hosts=[es_config.host],
    http_auth=(es_config.username, es_config.password),
    ca_certs=es_config.ca_certs,
    verify_certs=True,
)


def get_elasticsearch_client() -> Elasticsearch:
    return es_client
