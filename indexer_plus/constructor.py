import contextlib
from typing import *
import pickle as pkl
import os
from multiprocessing import Pool

from .inverted_index import InvertedIndexIterator, InvertedIndexWriter, InvertedIndexMapper
from .helper import IdMap
from .text_preprocess import TextCleaner
from .utils import DocInfo


class BSBIIndex:
    """
    Attributes
    ----------
    term_id_map IdMap: For mapping terms to termIDs
    doc_id_map(IdMap): For mapping relative paths of documents (eg path/to/docs/in/a/dir/) to docIDs
    data_dir(str): Path to data
    output_dir(str): Path to output index files
    index_name(str): Name assigned to index
    postings_encoding: Encoding used for storing the postings.
        The default (None) implies UncompressedPostings
    """

    def __init__(self, data_dir, output_dir, index_name="BSBI",
                 postings_encoding=None):
        self.term_id_map = IdMap()
        self.doc_id_map = IdMap()
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.index_name = index_name
        self.postings_encoding = postings_encoding

        # Stores names of intermediate indices
        self.intermediate_indices = []

    def save(self):
        """Dumps doc_id_map and term_id_map into output directory"""

        with open(os.path.join(self.output_dir, 'terms.dict'), 'wb') as f:
            pkl.dump(self.term_id_map, f)
        with open(os.path.join(self.output_dir, 'docs.dict'), 'wb') as f:
            pkl.dump(self.doc_id_map, f)

    def load(self):
        """Loads doc_id_map and term_id_map from output directory"""
        try:
            with open(os.path.join(self.output_dir, 'terms.dict'), 'rb') as f:
                self.term_id_map = pkl.load(f)
            with open(os.path.join(self.output_dir, 'docs.dict'), 'rb') as f:
                self.doc_id_map = pkl.load(f)
        except FileNotFoundError:
            self.index()

    def index(self):
        """Base indexing code

        This function loops through the data directories,
        calls parse_block to parse the documents
        calls invert_write, which inverts each block and writes to a new index
        then saves the id maps and calls merge on the intermediate indices
        """
        for block_dir_relative in sorted(next(os.walk(self.data_dir))[1]):
            td_pairs = self.parse_block(block_dir_relative)
            index_id = 'index_' + block_dir_relative
            self.intermediate_indices.append(index_id)
            with InvertedIndexWriter(index_id, directory=self.output_dir,
                                     postings_encoding=
                                     self.postings_encoding) as index:
                self.invert_write(td_pairs, index)
                td_pairs = None
        self.save()
        with InvertedIndexWriter(self.index_name, directory=self.output_dir,
                                 postings_encoding=
                                 self.postings_encoding) as merged_index:
            with contextlib.ExitStack() as stack:
                indices = [stack.enter_context(
                    InvertedIndexIterator(index_id,
                                          directory=self.output_dir,
                                          postings_encoding=
                                          self.postings_encoding))
                    for index_id in self.intermediate_indices]
                self.merge(indices, merged_index)

    def parse_block(self, block_dir_relative):
        """Parses a tokenized text file into termID-docID pairs

        Parameters
        ----------
        block_dir_relative : str
            Relative Path to the directory that contains the files for the block

        Returns
        -------
        List[Tuple[Int, Int]]
            Returns all the td_pairs extracted from the block

        Should use self.term_id_map and self.doc_id_map to get termIDs and docIDs.
        These persist across calls to parse_block
        """
        td_pairs = set()
        doc_saver = DocInfo(term_id_map=self.term_id_map)
        files = self.get_file_paths(path=self.data_dir + '/' + block_dir_relative)
        text_cleaner = TextCleaner()
        for file_path in files:
            file = open(file_path, encoding='utf8')
            text = file.read()
            doc_id = self.doc_id_map[file_path]
            tokens = text_cleaner.tokenize(text)
            doc_saver.save(text_cleaner.get_text_info(text), tokens, doc_id)
            td_pairs.update(list(map(lambda token: (self.term_id_map[token], doc_id), tokens.keys())))
        return list(td_pairs)

    @staticmethod
    def get_file_paths(path: str) -> list:
        """
        get the list of file's path
        :param path: path of directory
        :return: return a list of file's path
        """
        if not os.path.isdir(path):
            raise Exception("the path is not the path of directory")

        files = list()
        entries = os.listdir(path)
        for each in entries:
            full_path = path + '/' + each
            if not os.path.isdir(full_path):
                files.append(full_path)
        return files

    def invert_write(self, td_pairs, index):
        """Inverts td_pairs into postings_lists and writes them to the given index

        Parameters
        ----------
        td_pairs: List[Tuple[Int, Int]]
            List of termID-docID pairs
        index: InvertedIndexWriter
            Inverted index on disk corresponding to the block
        """
        last_term = -1
        postings_list = []
        for pair in sorted(set(td_pairs)):
            if pair[0] != last_term:
                if last_term != -1:
                    index.append(last_term, postings_list)
                postings_list = []
                last_term = pair[0]
            postings_list.append(pair[1])
        if last_term != -1:
            index.append(last_term, postings_list)

    def merge(self, indices, merged_index):
        """Merges multiple inverted indices into a single index

        Parameters
        ----------
        indices: List[InvertedIndexIterator]
            A list of InvertedIndexIterator objects, each representing an
            iterable inverted index for a block
        merged_index: InvertedIndexWriter
            An instance of InvertedIndexWriter object into which each merged
            postings list is written out one at a time
        """

        indices_dict = list()
        for index in indices:
            # convert InvertedIndexIterator into dict of term_id and posting list
            indices_dict.append(dict(list([each for each in index])))

        # merge the dicts and write to merged_index
        while indices_dict:
            main_dict = indices_dict.pop(0)
            for term_id in main_dict:
                posting_list = set(main_dict[term_id])
                for other_dict in indices_dict:
                    posting_list.update(set(other_dict.pop(term_id, [])))
                merged_index.append(term_id, posting_list)

    def retrieve(self, query: dict):
        """
        use InvertedIndexMapper here!
        Retrieves the documents corresponding to the conjunctive query

        Parameters
        ----------
        query: dict of terms and tf

        Result
        ------
        List[str]
            Sorted list of documents which contains each of the query tokens.
            Should be empty if no documents are found.

        Should NOT throw errors for terms not in corpus
        """
        if len(self.term_id_map) == 0 or len(self.doc_id_map) == 0:
            self.load()

        posting_lists = list()
        with InvertedIndexMapper(self.index_name, postings_encoding=self.postings_encoding,
                                 directory=self.output_dir) as index_mapper:
            for q in query.keys():
                q_id = self.term_id_map[q]
                posting_lists.append(set(index_mapper[q_id]))

        # get common docs
        common_posting_list = posting_lists[0]
        for posting_list in posting_lists[1:]:
            common_posting_list.intersection_update(posting_list)

        return list(common_posting_list)


def sorted_intersect(list1: List[Any], list2: List[Any]):
    """Intersects two (ascending) sorted lists and returns the sorted result

    Parameters
    ----------
    list1: List[Comparable]
    list2: List[Comparable]
        Sorted lists to be intersected

    Returns
    -------
    List[Comparable]
        Sorted intersection
    """
    ### Begin your code

    ### End your code
