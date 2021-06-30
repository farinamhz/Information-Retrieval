from .scorer import BM25Scorer
from ranking.idf import Idf
from indexer_plus.constructor import BSBIIndex
from indexer_plus.text_preprocess import TextCleaner
from indexer_plus.utils import DocInfo


class Ranker:
    text_cleaner = TextCleaner()

    def __init__(self):
        self.index = BSBIIndex(data_dir='./Dataset_IR/Train', output_dir='./Output/')
        self.index.load()
        self.idf = Idf(self.index)
        self.scorer = BM25Scorer(self.idf, self.index)

    def get_result(self, query: str) -> list:
        """
        return the sorted list of doc as result of query
        """
        query_dict = self.text_cleaner.tokenize(query)
        related_docs = self.index.retrieve(query_dict)

        doc_score = list()
        for doc_id in related_docs:
            doc_score.append((doc_id, self.scorer.get_sim_score(query_dict, doc_id)))

        return self.get_sorted_result(doc_score)

    def get_sorted_result(self, doc_score):
        sorted_list = sorted(doc_score, key=lambda item: item[1], reverse=True)
        return [self.index.doc_id_map[doc[0]] for doc in sorted_list]


if __name__ == "__main__":
    ranker = Ranker()
    query = input("search: ")
    print(ranker.get_result(query))
