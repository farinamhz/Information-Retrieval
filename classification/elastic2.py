from elasticsearch import Elasticsearch
from elasticsearch import helpers
from typing import *

from text_preprocess import TextCleaner


class ElasticHandler:

    def __init__(self, index_name: str, els=Elasticsearch()):
        self.index_name = index_name
        self.els = els

    def index_documents(self, doc_list: list):
        """
        :param: doc_list is a list of dictionaries
        """
        result = helpers.bulk(self.els, self._make_standard_doc_list(doc_list), raise_on_error=True)
        print(f'SUCCESS: {result[0]}\nErrors: {result[1]}')

    def _make_standard_doc_list(self, doc_list: list):
        return [
            {
                '_index': self.index_name,
                '_id': i,
                '_source': each,
            }
            for i, each in enumerate(doc_list, 1)
        ]

    def get_query(self, query=None):

        return self.els.search(index=self.index_name,body={'query': {'match_all': {}}})

    def search(self, query, with_category=True):
        fields = ['text', ]
        if with_category:
            fields.append('category')
        query = TextCleaner().get_clean_text(query)
        converted_and_query = self.get_and_query(query)
        converted_or_query = self.get_or_query(query)
        should = [
            {
                "query_string": {
                    "query": converted_and_query,
                    "fields": ['text', ]}
            }
        ]
        if with_category:
            should.append({"query_string": {
                "query": converted_or_query,
                "fields": ['category', ]}})
        query_body = {"query": {
            "bool": {
                "should": should
            }}}

        return self.els.search(index=self.index_name, body=query_body)['hits']['hits']

    @staticmethod
    def get_and_query(query):
        query_words = query.split()
        query = str()
        for each in query_words[:len(query_words) - 1]:
            query += f'({each}) AND '
        query += f'({query_words[-1]})'
        return query

    @staticmethod
    def get_or_query(query, with_star=True):
        char = "*" if with_star else ""
        query_words = query.split()
        query = str()
        for each in query_words[:len(query_words) - 1]:
            query += f'({char}{each}{char})OR '
        query += f'({char}{query_words[-1]}{char})'
        return query

    def delete_all_docs(self):
        self.els.delete_by_query(index=[self.index_name, ], body={"query": {"match_all": {}}})
