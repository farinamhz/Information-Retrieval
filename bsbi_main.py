from indexer.constructor import BSBIIndex

DATASET_PATH = './Dataset_IR/Train'
OUTPUT_DIR = './Output/'


if __name__ == '__main__':
    BSBI_instance = BSBIIndex(data_dir=DATASET_PATH, output_dir=OUTPUT_DIR)
    # BSBI_instance.index()
    query = input('search >>  ')
    result = BSBI_instance.retrieve(query)
    print(f'Number of retrieve docs: {len(result)}')
    print('Directory of retrieve docs: ')
    for each in result:
        print(each)
