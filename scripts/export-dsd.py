import yaml
import os
from sdg.translations import TranslationInputYaml
from sdg.helpers import files
import xml.etree.ElementTree as ET

translation_input = TranslationInputYaml(source='translations/dsd')
translation_input.execute()
translations = translation_input.get_translations()

dsd_source = 'https://nsiws-stable-camstat-live.officialstatistics.org/rest/dataflow/KH_NIS/DF_SDG_KH/1.2?references=all&detail=referencepartial'
filename = 'dsd.xml'
request_params = {
    'headers': {
        'User-Agent': 'Mozilla'
    }
}
files.download_remote_file(dsd_source, filename, request_params=request_params)
namespaces = dict([node for _, node in ET.iterparse(filename, events=['start-ns'])])
if 'xml' not in namespaces:
    namespaces['xml'] = 'http://www.w3.org/XML/1998/namespace'
for ns in namespaces:
    ET.register_namespace(ns, namespaces[ns])

def get_namespace_alias(namespace_address):
    for alias, address in namespaces.items():
        if address == namespace_address:
            return alias
    raise Exception('Unable to find alias for ' + namespace_address)

tree = ET.parse(filename)
root = tree.getroot()
structure_ns = get_namespace_alias('http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure')
common_ns = get_namespace_alias('http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common')
def str_ns(element):
    return structure_ns + ':' + element
def com_ns(element):
    return common_ns + ':' + element
def get_codes(concept):
    codelist = concept.find('./' + str_ns('LocalRepresentation') + '/' + str_ns('Enumeration') + '/Ref', namespaces)
    if codelist is None:
        return []
    else:
        return root.findall('.//' + str_ns('Codelist') + '[@id="' + codelist.attrib['id'] + '"]/' + str_ns('Code'), namespaces)

dimensions = root.findall('.//' + str_ns('DimensionList') + '/' + str_ns('Dimension'), namespaces)
attributes = root.findall('.//' + str_ns('AttributeList') + '/' + str_ns('Attribute'), namespaces)
for concept in dimensions + attributes:
    key = concept.attrib['id']
    for code in get_codes(concept):
        code_id = code.attrib['id']
        for language in translations:
            if key in translations[language] and code_id in translations[language][key] and translations[language][key][code_id] != '':
                found_name = False
                lang_ns = '{' + namespaces['xml'] + '}lang'
                for name in code.findall('./' + com_ns('Name'), namespaces):
                    code_lang = name.attrib[lang_ns]
                    if code_lang == language:
                        found_name = True
                        if name.text != translations[language][key][code_id]:
                            name.text = translations[language][key][code_id]
                if not found_name:
                    name = ET.SubElement(code, com_ns('Name'), {lang_ns: language})
                    name.text = translations[language][key][code_id]

export_filename = os.path.join('_site', 'dsd-exported.xml')
tree.write(export_filename, encoding='utf-8', xml_declaration=True)
