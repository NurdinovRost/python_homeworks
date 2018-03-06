import requests
import copy
import csv
import collections
from bs4 import BeautifulSoup
import pprint
from math import log
import sqlalchemy
import BDNews
from bottle import route, run, template, request
from bottle import redirect
import string


def test():
    with open("SMSSpamCollection", encoding='utf-8') as f:
        data = list(csv.reader(f, delimiter="\t"))    
    X, y = [], []
    for target, msg in data:
        X.append(msg)
        y.append(target)
    X = [clean(x).lower() for x in X]
    X_train, y_train, X_test, y_test = X[:3900], y[:3900], X[3900:], y[3900:]
    model = NaiveBayesClassifier(0.05)
    model.fit(X_train, y_train)
    print(model.score(X_test, y_test))   


class NaiveBayesClassifier:
    
    def __init__(self, alpha):
        self.alpha = alpha
        self.defdict = collections.defaultdict()
        self.probability = collections.Counter()
        pass


    def fit(self, X, y):
        """ Fit Naive Bayes classifier according to X, y. """
        classes = set(y)
        for i in range(len(X)):
            words = X[i].split(' ')
            for word in words:
                if word not in self.defdict:
                    self.defdict[word] = {i: [0, 0] for i in classes}
                self.defdict[word][y[i]][0] += 1

        d = len(self.defdict)
        counter = collections.Counter()
        for word in self.defdict:
            for elem in classes:
                counter[elem] += self.defdict[word][elem][0]

        for word in self.defdict:
            for elem in classes:
                self.defdict[word][elem][1] = ((self.defdict[word][elem][0] + self.alpha) / 
                                               (counter[elem] + self.alpha * d))

        self.probability = collections.Counter(y)
        for elem in self.probability:
            self.probability[elem] /= len(y)
            self.probability[elem] = round(log(self.probability[elem])) 
            
    def predict(self, X):
        """ Perform classification on an array of test vectors X. """
        y = []
        for i in X:
            copy_classes = self.probability.copy()
            words = i.split(" ")
            for word in words:
                for elem in self.probability:
                    copy_classes[elem] += calculate(word, elem, self.defdict)

            y.append(prediction(copy_classes))                            
        return y                
    
    def score(self, X_test, y_test):
        """ Returns the mean accuracy on the given test data and labels. """
        count = 0
        predict = self.predict(X_test)
        for i in range(len(predict)):
            if y_test[i] == predict[i]:
                count += 1
        return count / len(y_test)


def prediction(copy_classes):
    maximum = -10000000
    for i in copy_classes:
        if copy_classes[i] > maximum:
            key = i
            maximum = copy_classes[i]
    return key        


def calculate(word, elem, defdict):
    try:
        value = defdict[word][elem][1]
    except KeyError:
        value = 0   
    if value == 0:
        return 0
    else:
        return log(value)


def clean(s):
    translator = str.maketrans("", "", string.punctuation)
    return s.translate(translator)
       

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


def get_news(url, n_pages = 20):
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
        
    model = NaiveBayesClassifier(0.05)
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

