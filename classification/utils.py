from text_preprocess import TextCleaner
from sklearn import preprocessing
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
import pandas as pd
import os


def get_df(path, clean_data=True):
    list_row = list()
    list_of_file_dir = os.listdir(path)
    for each in list_of_file_dir:
        full_path = path + '/' + each
        if os.path.isdir(full_path):
            list_of_entry = os.listdir(full_path)
            for entry in list_of_entry:
                file_path = full_path + '/' + entry
                if not os.path.isdir(file_path):
                    file = open(file_path, encoding='utf8')
                    text = file.read()
                    if clean_data:
                        text = TextCleaner().get_clean_text(text)
                    list_row.append({'category': each, 'text': text})
                    file.close()
    return pd.DataFrame(list_row)


def get_tf_matrix(df: pd.DataFrame, fit_data: pd.DataFrame):
    count_vect = CountVectorizer(max_features=500)
    count_vect.fit(fit_data.text)
    return count_vect.transform(df.text)


def get_td_idf_matrix(tf_matrix):
    tfidf_transformer = TfidfTransformer()
    return tfidf_transformer.fit_transform(tf_matrix)


def label_encoder(df, col_name):
    le = preprocessing.LabelEncoder()
    le.fit(df[col_name].unique())
    return le.transform(df[col_name])


def get_inverse_label(predict_list, unique_items):
    le = preprocessing.LabelEncoder()
    le.fit(unique_items)
    return le.inverse_transform(predict_list)


def unique_items(df, col_name):
    return list(df[col_name].unique())


def to_dict_convertor(df):
    col_names = list(df.columns)
    item_list = list()

    for index, row in df.iterrows():
        item = dict()
        for name in col_names:
            item[name] = row[name]
        item_list.append(item)

    return item_list



