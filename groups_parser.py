import requests
from bs4 import BeautifulSoup

HEADERS = {
    'Host': 'rasp.rea.ru',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
    'X-MicrosoftAjax': 'Delta=true',
    'X-Requested-With': 'XMLHttpRequest',
    'Cache-Control': 'no-cache',
    'Referer': 'https://rasp.rea.ru/'
}

URL = 'https://rasp.rea.ru/default'

ASP_KEYS_TITLES = [
    '__EVENTVALIDATION',
    '__LASTFOCUS',
    '__VIEWSTATE',
    '__VIEWSTATEGENERATOR',
]

session = requests.Session()  # Set session


# GET запрос к главной странице
def get_main_page():
    response = session.get(URL, headers=HEADERS)
    dom = BeautifulSoup(response.content, 'html.parser')
    return dom


def get_asp_keys(dom, method):
    asp_keys = {}
    if method == 'get':
        for asp_key_title in ASP_KEYS_TITLES:
            asp_keys[asp_key_title] = dom.find('input', {'name': asp_key_title}).get('value')
        return asp_keys
    if method == 'post':
        start_index = dom.text.find('0|hiddenField|__EVENTTARGET|')
        array_with_keys = dom.text[start_index:].split('|')
        for asp_key_title in ASP_KEYS_TITLES:
            index_of_key = array_with_keys.index(asp_key_title) + 1
            asp_keys[asp_key_title] = array_with_keys[index_of_key]
        return asp_keys
    return


# Создание словаря из:
# Факультетов - 'ddlFaculty'
# Курсов - 'ddlCourse'
# Уровней - 'ddlBachelor'
# Групп - 'ddlGroup'
def parse_select(dom, select_name):
    options = dom.find('select', {'name': select_name}).find_all('option')[1:]
    options_dict = {}
    for option in options:
        options_dict.update({option.text: option.get('value')})
    return options_dict


def post_main_page(data, target):
    data_default = {
        '__ASYNCPOST': 'true',
        '__EVENTARGUMENT': '',
        '__EVENTTARGET': target,
        'ctl11': 'upSelectGroup|' + target,
        'txtGroupName': ''
    }
    data_default.update(data)
    response = session.post(URL, data=data_default, headers=HEADERS)
    dom = BeautifulSoup(response.content, 'html.parser')
    return dom


def get_groups(faculty, course, bachelor):
    dom = get_main_page()
    faculty_dict = parse_select(dom, 'ddlFaculty')
    asp_keys = get_asp_keys(dom, 'get')

    data = {
        'ddlBachelor': 'na',
        'ddlCourse': 'na',
        'ddlFaculty': faculty_dict[faculty],
        'ddlGroup': 'na',
    }
    data.update(asp_keys)
    dom = post_main_page(data, 'ddlFaculty')
    course_dict = parse_select(dom, 'ddlCourse')
    asp_keys = get_asp_keys(dom, 'post')

    data = {
        'ddlBachelor': 'na',
        'ddlCourse': course_dict[course],
        'ddlFaculty': faculty_dict[faculty],
        'ddlGroup': 'na',
    }
    data.update(asp_keys)
    dom = post_main_page(data, 'ddlCourse')
    bachelor_dict = parse_select(dom, 'ddlBachelor')
    asp_keys = get_asp_keys(dom, 'post')

    data = {
        'ddlBachelor': bachelor_dict[bachelor],
        'ddlCourse': course_dict[course],
        'ddlFaculty': faculty_dict[faculty],
        'ddlGroup': 'na',
    }
    data.update(asp_keys)
    dom = post_main_page(data, 'ddlBachelor')
    group_dict = parse_select(dom, 'ddlGroup')
    return group_dict


if __name__ == '__main__':
    get_groups('факультет "Международная школа бизнеса и мировой экономики"','1-й курс','Бакалавр')