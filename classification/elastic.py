from elasticsearch import Elasticsearch
from elasticsearch import helpers
from typing import *


class ElasticsearchConnector:

    def __init__(self, host_port, http_auth=None):
        self.host_port = host_port
        self.http_auth = http_auth

    def get_es_instance(self):
        if self.http_auth:
            return Elasticsearch(self.host_port, http_auth=self.http_auth)
        else:
            return Elasticsearch(self.host_port)


def retry_handler(success, errors, data_len):
    if data_len == success:
        return False
    print(errors)
    return True


class ElasticLoader:
    def __init__(self, connection: Elasticsearch, configs: dict):
        self.__conn = connection
        self.__configs = configs
        self.raise_on_error = True

    def __load_configs(self):
        self.__index_name = self.__configs['index']
        self.__batch_size = self.__configs.get('batch-size', 1000)

    def load_to_elastic(self, data_list: list, batch_size: int = 1000):
        for idx in range(0, len(data_list), batch_size):
            batch_doc_list = data_list[idx:idx + batch_size]
            self.__bulk_query(batch_doc_list)

    def __bulk_query(self, doc_list):
        while True:
            success, errors = helpers.bulk(self.__conn, doc_list, raise_on_error=self.raise_on_error)
            retry = retry_handler(success, errors, doc_list)
            if not retry:
                break


if __name__ == '__main__':
    pass
