import telebot
import requests
import html5lib
import config
import datetime
from bs4 import BeautifulSoup

access_token = config.access_token
# Создание бота с указанным токеном доступа
bot = telebot.TeleBot(access_token)


def test_week(week):
    if week == '1' or week == '2' or week == '0' or week == '':
        return False
    else:
        return True


def get_page(group, week=''):
    if week:
        week = str(week) + '/'
    url = '{domain}/{group}/{week}raspisanie_zanyatiy_{group}.htm'.format(
        domain=config.domain, 
        week=week, 
        group=group)
    response = requests.get(url)
    web_page = response.text
    return web_page


def get_schedule(web_page, day):
    soup = BeautifulSoup(web_page, "html5lib")
    
    notes = {'monday' : '1day', 'tuesday': '2day', 'wednesday': '3day',
             'thursday': '4day', 'friday': '5day', 'saturday': '6day'}
    

    schedule_table = soup.find("table", attrs={"id": notes[day]})
   # print("YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
   # print(schedule_table)
   # print("YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
    if schedule_table == None:
        return None, None, None

    # Время проведения занятий
    times_list = schedule_table.find_all("td", attrs={"class": "time"})
    times_list = [time.span.text for time in times_list]

    # Место проведения занятий
    locations_list = schedule_table.find_all("td", attrs={"class": "room"})
    locations_list = [room.span.text for room in locations_list]

    # Название дисциплин и имена преподавателей
    lessons_list = schedule_table.find_all("td", attrs={"class": "lesson"})
    lessons_list = [lesson.text.split('\n\n') for lesson in lessons_list]
    lessons_list = [', '.join([info for info in lesson_info if info]) for lesson_info in lessons_list]

    return times_list, locations_list, lessons_list


@bot.message_handler(commands=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'all'])
def get_table1(message):
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    day, week_number, group = message.text.split()
    day = day[1:]
    if test_week(week_number):
        bot.send_message(message.chat.id, 'Введена неверная четность', parse_mode='HTML')
        return
    
    web_page = get_page(group, week_number)
    if day == 'all':
        for d in days:
            times_lst, locations_lst, lessons_lst = get_schedule(web_page, d)
            if times_lst == None or locations_lst == None or lessons_lst == None:
                bot.send_message(message.chat.id, 'Введена неверная группа', parse_mode='HTML')
                return
                
            resp = ''
            for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
                resp += '<b>{}</b>, {}, {}\n'.format(time, location, lession)
            
            bot.send_message(message.chat.id, d, parse_mode='HTML')
            bot.send_message(message.chat.id, resp, parse_mode='HTML')
    else:
        times_lst, locations_lst, lessons_lst = get_schedule(web_page, day)
        if times_lst == None or locations_lst == None or lessons_lst == None:
            bot.send_message(message.chat.id, 'Введена неверная группа', parse_mode='HTML')
            return
        
        
        resp = ''
        for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
            resp += '<b>{}</b>, {}, {}\n'.format(time, location, lession)

        bot.send_message(message.chat.id, resp, parse_mode='HTML')        


@bot.message_handler(commands=['tommorow'])
def get_table2(message):
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    _, group = message.text.split()
    day = datetime.datetime.today().weekday()
    week = int(datetime.datetime.today().strftime('%U'))
    
    if day == 6 or day == 5:
        day = 0
        week = (week + 1) % 2 + 1
    else:
        day = day + 1
        week = week % 2 + 1  
        
    web_page = get_page(group, week)
    times_lst, locations_lst, lessons_lst = get_schedule(web_page, days[day])
    if times_lst == None or locations_lst == None or lessons_lst == None:
        bot.send_message(message.chat.id, 'Введена неверная группа', parse_mode='HTML')
        return

    resp = ''
    for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
        resp += '<b>{}</b>, {}, {}\n'.format(time, location, lession)

    bot.send_message(message.chat.id, resp, parse_mode='HTML')        


@bot.message_handler(commands=['near_lesson'])
def get_table3(message):
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    _, group = message.text.split()
    date = datetime.datetime.today()
    time_now = str(date.hour)+ ":" + str(date.minute)
    date = datetime.datetime.today().weekday()
    week = int(datetime.datetime.today().strftime('%U'))
    flag = True
    if date == 6:
        flag = False
        date = 0
        week = (week + 1) % 2 + 1
    else:
        date = date
        week = week % 2 + 1
        
    
    web_page = get_page(group, week)

    times_lst, locations_lst, lessons_lst = get_schedule(web_page, days[date])
    if times_lst == None or locations_lst == None or lessons_lst == None:
        flag = False
    
    index = -1
    if flag == True:
        for i in range(len(times_lst)):
            t = times_lst[i].split('-')
            if len(t[0]) >= len(time_now):
                if t[0] > time_now:
                    index = i
                    print('YYYYYYYYYYYYYYYYYYYYYYYYYY')
                    flag = False
                    break
            else:
                continue
    if index != -1:
        time = times_lst[i]
        location = locations_lst[i]
        lession = lessons_lst[i]
        resp = ''
        resp += '<b>{}</b>, {}, {}\n'.format(time, location, lession)        
        bot.send_message(message.chat.id, resp, parse_mode='HTML') 
        return
    else:
        for i in range(14):
            date += 1
            if date == 6:
                date = 0
                if week == 1:
                    week = 2
                else:
                    week = 1
                web_page = get_page(group, week)
            times_lst, locations_lst, lessons_lst = get_schedule(web_page, days[date])
            if times_lst != None and locations_lst != None and lessons_lst != None:
                time = times_lst[0]
                location = locations_lst[0]
                lession = lessons_lst[0]
                resp = ''
                resp += '<b>{}</b>, {}, {}\n'.format(time, location, lession)        
                bot.send_message(message.chat.id, resp, parse_mode='HTML') 
                return
            else:
                print("YO")
                continue
        bot.send_message(message.chat.id, 'Введена несуществующая группа', parse_mode='HTML')
        return
                
                


   
if __name__ == '__main__':
    bot.polling(none_stop=True)    