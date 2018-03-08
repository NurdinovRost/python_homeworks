import requests
import collections
from bs4 import BeautifulSoup
import pprint
import sqlalchemy
import BDNews
from bottle import route, run, template, request
from bottle import redirect
import string
import NBClassifier


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
        

@route('/update_news')
def update_news():
    get_news("https://news.ycombinator.com/newest")
    print(news_list)
    i = 0
    for new in news_list:
        row = BDNews.s.query(BDNews.News).filter(BDNews.News.author == new['author'], 
                                                 BDNews.News.title == new['title']).all()
        if len(row) == 0:
            
            news = BDNews.News(title = new['title'],
                       author = new['author'],
                       url = new['url'],
                       comments = new['comments'],
                       points = new['points'])
            BDNews.s.add(news)
            BDNews.s.commit()
    redirect('/news')       


@route('/news')
def news_list():
    rows = BDNews.s.query(BDNews.News).filter(BDNews.News.label == None).all()
    return template('news_template', rows=rows)


@route('/add_label/')
def add_label():

    label = request.query.label or label
    id = request.query.id or id
    BDNews.s.query(BDNews.News).filter(BDNews.News.id == id).all()[0].label = label 
    BDNews.s.commit()    
    redirect('/news')


@route('/recommendations')
def recommendations():
    classified = BDNews.s.query(BDNews.News).filter(BDNews.News.label == None).all()
    news = BDNews.s.query(BDNews.News).filter(BDNews.News.label != None).all()
    X_train = []
    y_train = []
    X_test = []
    for new in news:
        X_train.append(new.title)
        y_train.append(new.label)
    for new in classified:
        X_test.append(new.title)
        
    model = NBClassifier.NaiveBayesClassifier(0.05)
    model.fit(X_train, y_train)
    y = model.predict(X_test)
    for i in range(len(classified)):
        classified[i].label = y[i]
    BDNews.s.commit() 
    classified_news = []
    for new in classified:
        if new.label == 'good':
            classified_news.append(new)
    for new in classified:
        if new.label == 'maybe':
            classified_news.append(new)
    for new in classified:
        if new.label == 'never':
            classified_news.append(new)

    return template('news_recommendations', rows=classified_news)


run(host='localhost', port=8080)
