import hazm
import parsivar
import re


def get_characters():
    f = open('./indexer/resource/chars', encoding='utf-8')
    chars = f.read()
    return set([w for w in chars.split('\n') if w])


def get_stop_words():
    nmz = parsivar.Normalizer()
    f = open('./indexer/resource/persian', encoding='utf-8')
    words = f.read()
    return set([nmz.normalize(w) for w in words.split('\n') if w])


class TextCleaner:
    normalizer = parsivar.Normalizer()
    tokenizer = parsivar.Tokenizer()
    stemmer = parsivar.FindStems()
    lemmatizer = hazm.Lemmatizer()
    stop_words = get_stop_words()

    @classmethod
    def tokenize(cls, text):
        clean_tokens = set()
        text = cls.delete_specific_char(cls.normalize(text))
        tokens = cls.tokenizer.tokenize_words(text)
        for token in tokens:
            token = cls.token_convertor(token)
            if token not in cls.stop_words and \
                    token not in [';', ',', '&', '?', 'amp', 'nbsp', '.', 'o'] and \
                    not re.match(r'\d+', token):
                clean_tokens.add(token)
        return list(clean_tokens)

    @classmethod
    def token_convertor(cls, token):
        new_token = cls.stemmer.convert_to_stem(token)
        if '&' in new_token:
            new_token = new_token.split('&')[0]
        new_token = cls.lemmatizer.lemmatize(new_token)
        if '#' in new_token:
            new_token = new_token.split('#')[0]
        return new_token

    @classmethod
    def normalize(cls, text):
        return cls.normalizer.normalize(text)

    @staticmethod
    def delete_specific_char(text):
        chars = get_characters()
        chars = list(chars)
        chars += [';', ',', '&', '?', '.', '%']
        for each in chars:
            text = text.replace(each, ' ')
        return text
