from ranking.idf import Idf


class BM25Scorer:
    """ An abstract class for a scorer. 
        Implement query vector and doc vector.
        Needs to be extended by each specific implementation of scorers.
    """

    def __init__(self, idf, query_weight_scheme=None, doc_weight_scheme=None):  # Modified
        self.idf = idf

        self.default_query_weight_scheme = {"tf": 'b', "df": 't', "norm": None}  # boolean, idf, none
        self.default_doc_weight_scheme = {"tf": 'n', "df": 'n', "norm": None}  # natural, none

        self.query_weight_scheme = query_weight_scheme if query_weight_scheme is not None \
            else self.default_query_weight_scheme  # Modified (added)
        self.doc_weight_scheme = doc_weight_scheme if doc_weight_scheme is not None \
            else self.default_doc_weight_scheme  # Modified (added)

    def get_sim_score(self, q, d):
        """ Score each document for each query.
        Args:
            q (Query): the Query
            d (Document) :the Document

        Returns:
            pass now, will be implement in task 1, 2 and 3
        """

    ### Begin your code

    ### End your code

    def get_query_vector(self, q):
        query_vec = {}
        ### Begin your code

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

    def calc_avg_length(self):
        """ Set up average lengths for BM25F, also handling PageRank.
        You need to
        Initialize any data structures needed.
        Perform any preprocessing you would like to do on the fields.
        Handle pagerank
        Accumulate lengths of fields in documents.
        Hint: You could use query_dict
        """
        ### Begin your code

        ### End your code



if __name__ == '__main__':
    idf = Idf()
    scorer = BM25Scorer()
    d = "here is the document"
    q = "here is the query"
    score = scorer.get_sim_score(q, d)
    print(score)
