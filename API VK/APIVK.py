import requests
import time
from datetime import datetime
from igraph import Graph, plot
import numpy as np
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import config


def check_bdate(bdate):
    dmy = bdate.split(".") # date_month_year
    if len(dmy) < 3:
        return "not year"
    else:
        return dmy[2]
    
    pass


def get_friends(user_id, fields):
    """ Returns a list of user IDs or detailed information about a user's friends """
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert isinstance(fields, str), "fields must be string"
    assert user_id > 0, "user_id must be positive integer"
    # PUT YOUR CODE HERE
    
    query_params = {
       # 'domain' : domain,
        'access_token': config.access_token,
        'user_id': user_id,
        'fields': fields
    }
    
    #query = "{domain}/friends.get?access_token={access_token}&user_id={user_id}&fields={fields}&v=5.53".format(**query_params)
    
    response = get(config.domain, 'friends.get', query_params)    
    list_friends = response.json()
    return list_friends

def get_users_ids(list_friends):
    users_ids = []
    for i in range(list_friends['response']['count']):
        users_ids.append((int(list_friends['response']['items'][i]['id']), list_friends['response']['items'][i]['last_name']))
    return users_ids    

def age_predict(user_id):
    """
    >>> age_predict(???)
    ???
    """
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert user_id > 0, "user_id must be positive integer"
    # PUT YOUR CODE HERE
    list_friends = get_friends(user_id, "bdate")
    count_friends = list_friends["response"]["count"]
    average_age = 0
    unknown_age = 0
    
    for i in range(count_friends):
        if 'bdate' in list_friends['response']['items'][i]:
            bdate_friend = check_bdate(list_friends["response"]["items"][i]['bdate'])
            if bdate_friend != "not year":
                average_age += (2017 - int(bdate_friend))
            else:
                unknown_age += 1
        else:
            unknown_age += 1
    if count_friends > unknown_age: 
        average_age = average_age // (count_friends - unknown_age)    
    return average_age


def get_many_messages(user_id, offset, quantity):
    history = []
    ans = []
    start = 0
    while quantity != 0:
        if quantity >= 200:
            quantity -= 200
            thm = messages_get_history(user_id, offset=start, count=20)
            history.append(thm['response']['items'])
            start += 20
        else:
            thm = messages_get_history(user_id, offset=start, count=quantity)
            history.append(thm['response']['items'])
            quantity = 0
    for i in history:
        for j in i:
            ans.append(j)
    return ans        
        


def messages_get_history(user_id, offset=0, count=20):
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert user_id > 0, "user_id must be positive integer"
    assert isinstance(offset, int), "offset must be positive integer"
    assert offset >= 0, "user_id must be positive integer"
    assert count >= 0, "user_id must be positive integer"
    # PUT YOUR CODE HERE
    
    query_params = {
        #'domain' : domain,
        'access_token': config.access_token,
        'user_id': user_id,
        'offset': offset,
        'count': count
    }   
    if count > 200:
        return get_many_messages(user_id, offset, count)
    else:    
        response = get(config.domain, 'messages.getHistory', query_params)
    try:
        return response.json()
    except ValueError:
        return {}
    #return messagess


def count_dates_from_messages(messages):
    #PUT YOUR CODE HERE
    frequency = {}   
    count_messages = messages['response']['count'] - 5
    for i in range(int(count_messages)):
        data = datetime.fromtimestamp(messages['response']['items'][i]['date']).strftime("%Y-%m-%d")
        if data in frequency:
            frequency[data] += 1
        else:
            frequency[data] = 1
  
    return sorted(frequency.items(),key=lambda x:x[1],reverse=True)


def get_network(users_ids, as_edgelist=True):
    """ Building a friend graph for an arbitrary list of users """
    # PUT YOUR CODE HERE
    dictionary_id = {}
    new_id = 0
    eges = []
    vertices = []
    for i in range(users_ids['response']['count']):
        dictionary_id[int(users_ids['response']['items'][i]['id'])] = new_id
        new_id += 1
        vertices.append(users_ids['response']['items'][i]['last_name'])     
    for i in range(users_ids['response']['count']):
        if 'deactivated' in users_ids['response']['items'][i]:
            continue
        else:
            
            start = time.time()
            fof = get_friends(int(users_ids['response']['items'][i]['id']), 'sex')
            #print(fof)
            for j in range(fof['response']['count']):
                if int(fof['response']['items'][j]['id']) in dictionary_id:
                    eges.append((dictionary_id[int(users_ids['response']['items'][i]['id'])], 
                                 dictionary_id[int(fof['response']['items'][j]['id'])])) 
            end = time.time()
            if end - start < 0.33:
                time.sleep(0.33 - end + start)
    
    
    g = Graph(vertex_attrs={"label":vertices}, edges=eges, directed=False)  
    N = len(vertices)
    visual_style = {}
    visual_style['edge_color'] = '#C0C0C0'
    visual_style['vertex_size'] = 10
    visual_style['vertex_label_color'] = 'blue'
    visual_style['vertex_label_dist'] = 2
    g.simplify(multiple=True, loops=True)
    visual_style['vertex_color'] = ['blue']
    visual_style["layout"] = g.layout_fruchterman_reingold(
        maxiter=1000,
        area=N**3,
        repulserad=N**3)    
    plot(g, **visual_style)


def eplot(user_id):
    x = []
    y = []
    dictionary = count_dates_from_messages(messages_get_history(user_id, 0, 200))
    dictionary.sort()
    for i in range(len(dictionary)):
        x.append(dictionary[i][0])
        y.append(dictionary[i][1])
    print(x)
    print(y)
    data = [go.Scatter(x=x,y=y)]
    py.iplot(data)


def get(url, command, params={}, timeout=5, max_retries=5, backoff_factor=0.3): 
    """ Выполнить GET-запрос

    :param url: адрес, на который необходимо выполнить запрос
    :param params: параметры запроса
    :param timeout: максимальное время ожидания ответа от сервера
    :param max_retries: максимальное число повторных запросов
    :param backoff_factor: коэффициент экспоненциального нарастания задержки
    """
    # PUT YOUR CODE HERE
    query = url + "/" + command + "?" 
    for key in params: 
        query += key + "=" + str(params[key]) + "&" 
    query += "v=5.53" 
    delay = 0 
    for i in range(max_retries): 
        try: 
            response = requests.get(query) 
            return response
        except: 
            print(sys.exc_info()[0]) 
            time.sleep(delay) 
            delay = min(delay * backoff_factor, timeout) 
            delay += random.random() 
            return None

#print(messages_get_history(119508224, 0, 33))

