from information_retrieval.constructor import BSBIIndex

DATASET_PATH = ''
OUTPUT_DIR = ''


if __name__ == '__main__':
    BSBI_instance = BSBIIndex(data_dir=DATASET_PATH, output_dir=OUTPUT_DIR)
    query = input('search >>  ')
    result = BSBI_instance.retrieve(query)