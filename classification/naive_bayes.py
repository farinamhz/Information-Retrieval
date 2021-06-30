from sklearn.naive_bayes import MultinomialNB
from elasticsearch import Elasticsearch

import utils
from elastic2 import ElasticHandler


if __name__ == '__main__':
    train_df = utils.get_df('../Dataset_IR/Train/')
    test_df = utils.get_df('../Dataset_IR/Test/')

    merged_df = train_df.append(test_df)
    train_x = utils.get_td_idf_matrix(utils.get_tf_matrix(train_df, merged_df))
    test_x = utils.get_td_idf_matrix(utils.get_tf_matrix(test_df, merged_df))

    model = MultinomialNB(alpha=1)
    model.fit(train_x, train_df.category)
    predicted = model.predict(test_x)

    test_df['category'] = predicted
    merged_df = train_df.append(test_df)
    print(':)')
    el = Elasticsearch()
    # print(el.indices.create(index='my-index', ignore=400))
    doc_list = utils.to_dict_convertor(merged_df)
    elastic = ElasticHandler('test')
    elastic.index_documents(doc_list)
    result = elastic.search(input('search: '))
    for each in result:
        print(each)
    elastic.delete_all_docs()





