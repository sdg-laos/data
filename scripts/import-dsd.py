import yaml
import os
from sdg.translations import TranslationInputSdmx

source_language = 'en'

source = 'LSB_DSD.xml'
translation_input = TranslationInputSdmx(source=source)
translation_input.execute()
translations = translation_input.get_translations()

for concept in translations[source_language]:
    filename = os.path.join('translations', 'dsd', source_language, concept) + '.yml'
    with open(filename, 'w', encoding='utf-8') as stream:
        yaml.dump(translations[source_language][concept], stream, allow_unicode=True, width=1000)
