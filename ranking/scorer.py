from ranking.idf import Idf
import math
from collections import Counter

class BM25Scorer:
    """ An abstract class for a scorer. 
        Implement query vector and doc vector.
        Needs to be extended by each specific implementation of scorers.
    """

    def __init__(self, idf, query_weight_scheme=None, doc_weight_scheme=None):  # Modified
        self.idf = idf

        self.b = 0.75
        self.k1 = 1.5

        self.N = yechizi

        self.calc_avg_length()

        self.default_query_weight_scheme = {"tf": 'b', "df": 't', "norm": None}  # boolean, idf, none
        self.default_doc_weight_scheme = {"tf": 'n', "df": 'n', "norm": None}  # natural, none

        self.query_weight_scheme = query_weight_scheme if query_weight_scheme is not None \
            else self.default_query_weight_scheme  # Modified (added)
        self.doc_weight_scheme = doc_weight_scheme if doc_weight_scheme is not None \
            else self.default_doc_weight_scheme  # Modified (added)


    ### Begin your code
    def countfrequency(self, my_list):
        freq = {}
        for item in my_list:
            if item in freq:
                freq[item] += 1
            else:
                freq[item] = 1
        return freq


    ### End your code

    def get_query_vector(self, q):
        query_vec = {}
        ### Begin your code
        wordlist = q.split()
        query_dic = self.countfrequency(wordlist)

        for term, tf in query_dic.items():
            # print(tf)
            # print(term)
            term_idf = self.idf.get_idf(term)
            query_vec[term] = math.log(((self.N - term_idf + 0.5) / (term_idf + 0.5)) + 1)
        ### End your code
        return query_vec

    def get_doc_vector(self, q, d, doc_weight_scheme=None):
        doc_vec = {}

        ### Begin your code

        ### End your code

        doc_vec = self.normalize_doc_vec(q, d, doc_vec)
        return doc_vec

    def normalize_doc_vec(self, q, d, doc_vec):
        ### Begin your code

        ### End your code
        ...
    def bm25f_normalize_doc_vec(self, q, d, doc_vec):
        """ Normalize the raw term frequencies in fields in document d
            using above equation (1).
        Args:
            q (Query) : the query
            d (Document) : the document
            doc_vec (dict) : the doc vector
        Return:
            doc_vec (dict) : the doc vector after normalization
        """
        ### Begin your code

        ### End your code

    def get_sim_score(self, q, d):
        """ Score each document for each query.
        Args:
            q (Query): the Query
            d (Document) :the Document

        Returns:
            pass now, will be implement in task 1, 2 and 3
            *** score ***
        """
        query_vec = self.get_query_vector(q)
        self.doc_weight_scheme['norm'] = self.bm25f_normalize_doc_vec
        norm_doc_vec = self.get_doc_vector(q, d, self.doc_weight_scheme)
        return self.get_total_score(q, query_vec, d, norm_doc_vec)


if __name__ == '__main__':
    idf = Idf()
    scorer = BM25Scorer()
    d = "here is the document"
    q = "here is the query"
    score = scorer.get_sim_score(q, d)
    print(score)
