import os
from sdg.translations import TranslationInputYaml
import xml.etree.ElementTree as ET

language_fixes = {
    'zh_Hans': 'zh'
}

translation_input = TranslationInputYaml(source='translations/dsd')
translation_input.execute()
translations = translation_input.get_translations()

filename = 'LSB_DSD.xml'
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
                fixed_language = language_fixes[language] if language in language_fixes else language
                found_name = False
                name_index = 0
                lang_ns = '{' + namespaces['xml'] + '}lang'
                name_ns = '{' + namespaces[common_ns] + '}Name'
                for index, child in enumerate(code):
                    if child.tag == name_ns:
                        name_index = index
                        code_lang = child.attrib[lang_ns]
                        if code_lang == fixed_language:
                            found_name = True
                            if child.text != translations[language][key][code_id]:
                                child.text = translations[language][key][code_id]
                if not found_name:
                    name = ET.Element(com_ns('Name'), {lang_ns: fixed_language})
                    code.insert(name_index, name)
                    name.text = translations[language][key][code_id]

export_filename = os.path.join('_site', 'dsd-exported.xml')
tree.write(export_filename, encoding='utf-8', xml_declaration=True)
