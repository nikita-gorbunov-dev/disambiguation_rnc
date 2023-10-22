import stanza
import xml.etree.ElementTree as ET
import os
from tqdm import tqdm

# Путь к папке с неразмеченными параллельными текстами в формате .xml
input_directory = 'C:/Users/Nikita/PycharmProjects/Stanza/xml'  # Пример дирректории

# Создание подпапки для сохранения размеченных .xml файлов, по умолчанию называется ready
output_directory = os.path.join(input_directory, 'ready')
os.makedirs(output_directory, exist_ok=True)

# Создание списка со всеми .xml файлами в выбранной дирректории
xml_files = [f for f in os.listdir(input_directory) if f.endswith('.xml')]
for xml_file in tqdm(xml_files, desc="Обработка файлов"):
    input_xml_file_path = os.path.join(input_directory, xml_file)
    tree = ET.parse(input_xml_file_path)
    root = tree.getroot()
    # Сопоставление тегов языков в .xml файлах с названиями моделей в Stanza
    lang_mapping = {
        'eng': 'en',
        'spa': 'es',
        'ita': 'it',
        'deu': 'de',
        'por': 'pt',
        'fra': 'fr'
    }

    # Создание объектов для обработки каждого из языков (Кроме русского)
    nlp = {}
    for se_element in root.findall(".//se"):
        lang = se_element.get('lang')
        if lang not in nlp:
            if lang == 'rus':
                nlp[lang] = None
            elif lang in lang_mapping:
                stanza_lang = lang_mapping[lang]
                stanza.download(stanza_lang)
                nlp[lang] = stanza.Pipeline(stanza_lang, processors='tokenize,mwt,pos,lemma,depparse')

    # Извлечение текста из .xml файла и разметка
    for se_element in root.findall(".//se"):
        lang = se_element.get('lang')
        if lang in nlp and nlp[lang]:
            text = se_element.text
            if text:
                doc = nlp[lang](text)
                se_element.text = ''
                for sentence in doc.sentences:
                    for word in sentence.words:
                        attributes = f"Lemma: {word.lemma}, POS: {word.pos}"
                        if hasattr(word, 'gender'):
                            attributes += f", Gender: {word.gender}"
                        if hasattr(word, 'number'):
                            attributes += f", Number: {word.number}"
                        if hasattr(word, 'case'):
                            attributes += f", Case: {word.case}"
                        # Проверка наличия feats перед разделением
                        if word.feats:
                            # Разметка других граммем
                            for feature in word.feats.split('|'):
                                key, value = feature.split('=')
                                attributes += f", {key}: {value}"
                        if word.text == '<':
                            word.text = '&lt;'
                        elif word.text == '>':
                            word.text = '&gt;'
                        if word.pos != "PUNCT":
                            se_element.text += f" <w><ana lex=\"{word.lemma}\" gr=\"{word.pos}\"/>{word.text} {attributes}</w>"
                        else:
                            se_element.text += f"{word.text}"
    # Сохранение в созданной ранее подпапке
    output_xml_file_path = os.path.join(output_directory, xml_file)
    output_tree = ET.ElementTree(root)
    output_tree.write(output_xml_file_path, encoding='utf-8')

print("Все файлы размечены и сохранены.")
