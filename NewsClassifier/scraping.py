import requests
from bs4 import BeautifulSoup


def extract_news(tr_list):
    index = 0
    while index < 89:
        dictionary = {}
        helper = tr_list[index].findAll('a')[1]
        dictionary['url'] = helper['href']
        dictionary['title'] = helper.string
        index += 1
        point = tr_list[index].span.string.split(' ')
        dictionary['points'] = int(point[0])
        dictionary['author'] = tr_list[index].a.string
        comments = tr_list[index].findAll('a')[-1].string
        if comments == 'discuss':
            dictionary['comments'] = 0
        else:
            dictionary['comments'] = int(comments.split('\xa0')[0])
        news_list.append(dictionary)
        index += 2
    

def extract_next_page(tr_list):
    return 'https://news.ycombinator.com/' + tr_list[91].a['href']


def get_news(url, n_pages = 3):
    global news_list
    news_list = []
    for i in range(n_pages):
        html_doc = requests.get(url)
        page = BeautifulSoup(html_doc.text, 'html.parser')
        print(i)
        tbl_list = page.table.findAll('table')
        tr_list = tbl_list[1].findAll('tr')
        
        extract_news(tr_list)
        url = extract_next_page(tr_list)
    return news_list    