import spacy
import xml.etree.ElementTree as ET
import os
import shutil

# После первого использования удалите из кода строки с загрузкой
spacy.cli.download("en_core_web_sm")
spacy.cli.download("fr_core_news_sm")
spacy.cli.download("es_core_news_sm")
spacy.cli.download("it_core_news_sm")
spacy.cli.download("de_core_news_sm")
spacy.cli.download("pt_core_news_sm")

# Функция для форматирования морфологических признаков
def format_morph_features(morph):
    morph_dict = morph.to_dict()
    morph_features = []

    for feature, value in morph_dict.items():
        if feature == "POS":
            # Маппинг частей речи на сокращенные обозначения
            pos_mapping = {
                "ADJ": "A",
                "ADP": "PR",
                "ADV": "ADV",
                "AUX": "V",
                "CONJ": "CONJ",
                "CCONJ": "CONJ",
                "DET": "PRO",
                "INTJ": "PART",
                "NOUN": "S",
                "NUM": "NUM",
                "PART": "PART",
                "PRON": "PRO",
                "PROPN": "S",
                "PUNCT": "PUNCT",
                "SCONJ": "CONJ",
                "SYM": "SYM",
                "VERB": "V",
                "X": "X"
            }
            morph_features.append(f"{pos_mapping.get(value, value)}")
        else:
            morph_features.append(f"{value}")

    return '|'.join(morph_features)

# Подгрузка моделей Spacy для разных языков
nlp_en = spacy.load("en_core_web_sm")  # Английский
nlp_fr = spacy.load("fr_core_news_sm")  # Французский
nlp_es = spacy.load("es_core_news_sm")  # Испанский
nlp_it = spacy.load("it_core_news_sm")  # Итальянский
nlp_de = spacy.load("de_core_news_sm")  # Немецкий
nlp_pt = spacy.load("pt_core_news_sm")  # Португальский

# Путь к папке с неразмеченными параллельными текстами в формате .xml
input_directory = r'C:\Users\Nikita\PycharmProjects\Spacy\xml'  # Пример дирректории

# Создание подпапки для сохранения размеченных .xml файлов, по умолчанию называется ready
output_directory = os.path.join(input_directory, 'ready')
os.makedirs(output_directory, exist_ok=True)

# Создание списка со всеми .xml файлами в выбранной дирректории
xml_files = [f for f in os.listdir(input_directory) if f.endswith('.xml')]
for xml_file in xml_files:
    input_xml_file_path = os.path.join(input_directory, xml_file)
    tree = ET.parse(input_xml_file_path)
    root = tree.getroot()

    # Сопоставление тегов языков в .xml файлах с названиями моделей в Spacy
    nlp = {
        'rus': None,
        'eng': nlp_en,
        'fra': nlp_fr,
        'spa': nlp_es,
        'ita': nlp_it,
        'deu': nlp_de,
        'por': nlp_pt,
    }
    # Путь для сохранения обработанного .xml файла
    output_xml_file_path = os.path.join(output_directory, xml_file)
    shutil.copy(input_xml_file_path, output_xml_file_path)
    output_tree = ET.ElementTree(root)

    for se_element in root.findall(".//se"):
        lang = se_element.get('lang')
        if lang in nlp and nlp[lang]:
            text = se_element.text
            if text:
                doc = nlp[lang](text)
                se_element.text = ''
                for token in doc:
                    if not token.is_punct:
                        # Формирование строки с аннотацией для слова
                        ana_str = f'<ana lex="{token.lemma_}" gr="{token.pos_},{format_morph_features(token.morph)}"/>'
                        se_element.text += f"<w>{ana_str}{token.text}</w>"
    # Сохранение в созданной ранее подпапке
    output_tree.write(output_xml_file_path, encoding='utf-8')

print("Все файлы размечены и сохранены.")