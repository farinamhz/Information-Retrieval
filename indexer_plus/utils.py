import json


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

        with open(self.save_path + str(doc_id) + '.json', 'w') as f:
            json.dump(doc_info, f)

    def load(self, doc_id: int) -> dict:
        try:
            f = open(self.save_path + str(doc_id) + '.json', 'r')
            data = json.loads(f.read())
            return data
        except FileNotFoundError:
            return {}
