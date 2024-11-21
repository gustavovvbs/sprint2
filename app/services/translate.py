import os
from operator import itemgetter 
from dotenv import load_dotenv
from google.cloud import translate_v2 as translate 

load_dotenv()


class TranslateService:
    def __init__(self):
        self.translator = translate.Client()

    def translate_fields(self, data, target_language='pt'):
        strings_to_translate = []
        paths = []

        def collect_strings(d, path=[]):
            if isinstance(d, dict):
                for k, v in d.items():
                    if k not in ['Location', 'Contacts']:
                        collect_strings(v, path + [k])
            elif isinstance(d, list):
                for idx, item in enumerate(d):
                    collect_strings(item, path + [idx])
            elif isinstance(d, str):
                if d.strip():  
                    strings_to_translate.append(d)
                    paths.append(path)

        collect_strings(data)

        if not strings_to_translate:
            return data

        try:
            result = self.translator.translate(strings_to_translate, target_language=target_language)
            translated_texts = [item['translatedText'] for item in result]
        except Exception as e:
            current_app.logger.error(f"Erro na tradução: {e}")
            return data

        for translated_text, path in zip(translated_texts, paths):
            d = data
            for p in path[:-1]:
                d = d[p]
            d[path[-1]] = translated_text

        return data
        



