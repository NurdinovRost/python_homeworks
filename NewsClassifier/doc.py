from bottle import route, run, template

@route('/news')
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template('news_template', rows=rows)

run(host='localhost', port=8080)

