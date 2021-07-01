import numpy as np

from indexer_plus.inverted_index import InvertedIndex


class Idf:
    """Build idf dictionary and return idf of a term, whether in or not in built dictionary.
        Recall from PA1 that postings_dict maps termID to a 3 tuple of
        (start_position_in_index_file, number_of_postings_in_list, length_in_bytes_of_postings_list)

        Remember that it's possible for a term to not appear in the collection corpus.
        Thus to guard against such a case, we will apply Laplace add-one smoothing.

        Note: We expect you to store the idf as {term: idf} and handle term which is not in posting_list

        Hint: For term not in built dictionary, we should return math.log10(total_doc_num / 1.0).
    """

    def __init__(self, loaded_index):
        """Build an idf dictionary"""

        self.total_doc_num = len(loaded_index.doc_id_map)
        self.total_term_num = len(loaded_index.term_id_map)
        self.postings_dict = {}
        with InvertedIndex(loaded_index.index_name, postings_encoding=loaded_index.postings_encoding,
                           directory=loaded_index.output_dir) as inverted_index:
            self.postings_dict = inverted_index.postings_dict
        self.termsID = loaded_index.term_id_map
        self.idf = {}

    def get_idf(self, term=None):
        """Return idf of return idf of a term, whether in or not in built dictionary.
        Args:
            term(str) : term to return its idf
        Return(float):
            idf of the term
        """
        if not isinstance(term, int):
            term = self.termsID[term]
        start_posting_pointer, posting_list_len, bytes_num = self.postings_dict[term]
        return np.log(((self.total_doc_num - posting_list_len + 0.5) / (posting_list_len + 0.5)) + 1)

