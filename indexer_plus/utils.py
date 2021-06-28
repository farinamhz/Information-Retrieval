import ast


class DocInfo:

    def __init__(self, term_id_map, save_path='./Output/Doc/'):
        self.term_id_map = term_id_map
        self.save_path = save_path

    def _convert_keys_to_id(self, term_dict: dict) -> dict:
        converted_dict = dict()
        for term in term_dict:
            key = term if isinstance(term, int) else self.term_id_map[term]
            converted_dict.update({key: term_dict[term]})
        return converted_dict

    def save(self, doc_info: dict, terms: dict, doc_id: int):
        converted_terms = self._convert_keys_to_id(terms)
        doc_info.update({'terms': converted_terms})

        with open(self.save_path + str(doc_id), 'w') as f:
            f.write(str(doc_info))

    def _load(self, doc_id: int) -> dict:
        try:
            f = open(self.save_path + str(doc_id), 'r')
            data = ast.literal_eval(f.read())
            return data
        except FileNotFoundError:
            return {}

    def __getitem__(self, key):
        if not isinstance(key, int):
            return {}
        return self._load(key)
