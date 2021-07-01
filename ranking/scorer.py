import math

from ranking.idf import Idf
from indexer_plus.constructor import BSBIIndex
from indexer_plus.text_preprocess import TextCleaner
from indexer_plus.utils import DocInfo
# from indexer_plus.helper import IdMap


class BM25Scorer:
    """ An abstract class for a scorer. 
        Implement query vector and doc vector.
        Needs to be extended by each specific implementation of scorers.
    """

    def __init__(self, idf, index, query_weight_scheme=None, doc_weight_scheme=None):  # Modified
        self.idf = idf
        self.index = index

        self.b = 0.75
        self.k1 = 1.5

        self.text_cleaner = TextCleaner()
        self.doc_info = DocInfo(index.term_id_map)

        self.N, self.avg_length = self.calc_avg_length()

        self.default_query_weight_scheme = {"tf": 'b', "df": 't', "norm": None}  # boolean, idf, none
        self.default_doc_weight_scheme = {"tf": 'n', "df": 'n', "norm": None}  # natural, none

        self.query_weight_scheme = query_weight_scheme if query_weight_scheme is not None \
            else self.default_query_weight_scheme  # Modified (added)
        self.doc_weight_scheme = doc_weight_scheme if doc_weight_scheme is not None \
            else self.default_doc_weight_scheme  # Modified (added)

    def calc_avg_length(self):
        # get from json files and calculate the avg
        len_sum = 0
        docinfo_len = len(self.index.doc_id_map)
        for i in range(docinfo_len):
            len_sum += self.doc_info[i]['length']
        avg = len_sum / docinfo_len
        return docinfo_len, avg

    def get_total_score(self, q, query_vec, d, doc_vec):
        f = dict()
        for t in query_vec:
            if t in doc_vec:
                # f[t] += doc_vec[t]
                f[t] = f.get(t, 0) + doc_vec[t]
        score = sum([query_vec[t] * ((f[t] * (self.k1 + 1))
                                     / (f[t] + self.k1 *
                                        (1 - self.b + self.b * (self.doc_info[d]['length'] / self.avg_length))))
                     for t in query_vec.keys()])
        return score

    def get_query_vector(self, q):
        query_vec = {}

        query_dic = {}
        for term, tf in q.items():
            query_dic[self.index.term_id_map[term]] = tf

        for term, tf in query_dic.items():
            term_idf = self.idf.get_idf(term)
            # query_vec[term] = math.log(((self.N - term_idf + 0.5) / (term_idf + 0.5)) + 1)
            query_vec[term] = term_idf
        return query_vec

    def get_doc_vector(self, q, d, doc_weight_scheme=None):
        doc_vec = {}

        query_vec = self.get_query_vector(q)
        doc_dict_info = self.doc_info[d]['terms']

        for qv in query_vec:
            if qv in doc_dict_info:
                if qv not in doc_vec:
                    doc_vec[qv] = (doc_dict_info[qv] + 1) * self.idf.get_idf(qv)
            else:
                doc_vec[qv] = 1

        doc_vec = self.normalize_doc_vec(q, d, doc_vec)
        return doc_vec

    def normalize_doc_vec(self, q, d, doc_vec):

        x = 0
        for item in doc_vec:
            x += (doc_vec[item] * doc_vec[item])
        for item in doc_vec:
            doc_vec[item] = doc_vec[item] / math.sqrt(x)
        return doc_vec


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
        norm_doc_vec = self.get_doc_vector(q, d)
        return self.get_total_score(q, query_vec, d, norm_doc_vec)


if __name__ == '__main__':
    index = BSBIIndex(data_dir='./Dataset_IR/Train', output_dir='./Output/')
    index.load()
    idf = Idf(index)
    scorer = BM25Scorer(idf, index)
    d = "here is the document"
    q = "here is the query"
    score = scorer.get_sim_score(q, d)
    print(score)
