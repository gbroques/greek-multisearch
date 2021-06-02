
import random
import sys
import webbrowser
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from jinja2 import Environment, PackageLoader, select_autoescape
from PyQt5.QtWidgets import QApplication, QInputDialog, QLineEdit, QWidget

__all__ = ['greek_multisearch']

env = Environment(
    loader=PackageLoader('greek_multisearch'),
    autoescape=select_autoescape()
)
template = env.get_template('index.html')

link_templates = [
    'https://www.google.gr/search?tbm=isch&q={}',
    'https://translate.google.com/?sl=el&tl=en&text={}&op=translate'
    'https://el.wiktionary.org/wiki/{}',
    'https://forvo.com/search/{}/',
    'https://www.wordreference.com/gren/{}'
]


class App(QWidget):

    def __init__(self):
        super().__init__()
        text, ok = QInputDialog.getText(
            self, 'Greek Multisearch', 'Enter your search phrase:', QLineEdit.Normal, '')
        if ok and text != '':
            for link_template in link_templates:
                link = link_template.format(text)
                webbrowser.open_new_tab(link)
            search_greekpod101_dictionary(text)
        sys.exit()


def search_greekpod101_dictionary(search_query):
    user_agent = get_user_agent()
    url = 'https://www.greekpod101.com/learningcenter/reference/dictionary_post'
    data = {'post': 'dictionary_reference', 'search_query': search_query}
    headers = {
        'User-Agent': user_agent,
        'Origin': 'https://www.greekpod101.com',
        'Referer': 'https://www.greekpod101.com/greek-dictionary/'
    }

    x = requests.post(url, data, headers=headers, verify=True)
    soup = BeautifulSoup(x.text, 'html.parser')
    results = soup.find_all('div', 'dc-result-row')
    result_dicts = []
    for result in results:
        word = find_text(result, '.dc-vocab')
        romanization = find_text(result, '.dc-vocab_romanization')
        translation = find_text(result, '.dc-english')
        gender = find_text(result, '.dc-gender')
        source = result.find('source')
        audio = source['src'] if source else ''

        result_dicts.append({
            'word': word,
            'gender': gender,
            'romanization': romanization,
            'translation': translation,
            'audio': audio
        })
    parent_path = Path(__file__).parent
    index_html_path = parent_path.joinpath('index.html').absolute()
    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write(template.render(results=result_dicts))
    webbrowser.open_new_tab(
        'file:///' + str(index_html_path))


def find_text(result, class_name):
    element = result.select_one(class_name)
    return element.get_text() if element else ''


def get_user_agent():
    user_agent_list = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    ]
    return random.choice(user_agent_list)


def greek_multisearch():
    app = QApplication(sys.argv)
    App()
    sys.exit(app.exec_())
