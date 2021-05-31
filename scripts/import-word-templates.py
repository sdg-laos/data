import yaml
import os
from sdg.inputs import InputWordMeta

source_language = 'en'

meta_input = InputWordMeta(path_pattern='meta/*.docm', git=False)
meta_input.execute(None)

for indicator_id in meta_input.indicators:
    filename = os.path.join('translations', 'meta', source_language, indicator_id) + '.yml'
    with open(filename, 'w', encoding='utf-8') as stream:
        yaml.dump(meta_input.indicators[indicator_id].meta, stream, allow_unicode=True)
