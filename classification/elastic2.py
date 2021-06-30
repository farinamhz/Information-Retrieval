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
        return self.els.search(index=self.index_name,
                               body={"query": {
                                   "multi_match": {
                                       "query": query,
                                       "fields": fields}}})['hits']['hits']

    def delete_all_docs(self):
        self.els.delete_by_query(index=[self.index_name, ], body={"query": {"match_all": {}}})
