import flask
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import http.client
import sqlite3
import time
from api import get_pb,check_pbs

import psycopg2


connection = psycopg2.connect(database="postgres", user="postgres", password="misha15042005", host="localhost", port=5432)
cur = connection.cursor()


def set_time(user,cred):
   cur.execute(f"INSERT INTO public(user_name,take_time,credentials) VALUES ('{user}','{time.time()}','{cred}')")


def if_returned(id,station_id):
   flag = False
   #проверить какие айди возвращает и дальше наладить работу с этими айди в функциях ниже.
   print(check_pbs(station_id)['data']['batteries'])
   res = check_pbs(station_id)['data']['batteries']
   for i in range(len(res)):
      if id in res[i]['batteryId']:
         flag = True
   return flag








app = Flask(__name__)
#разобраться с кнопками. разобраться как вставить параметр запроса в редирект. активировать станцию
@app.route('/',methods=['get','post'])
def index():
   if request.method == "POST":
      res = request.json
      if res["btn_type"]=='submit':
         return {'re':url_for('giveout',id = res['pb_id'])}
      elif res["btn_type"]=='return':
         return {'re': url_for('return_pb', id=res['pb_id'])}

   return render_template('index.html')



@app.route('/giveout',methods=['get','post'])
def giveout():
   query = request.args
   station_id=query['id']

   if request.method == "POST":
      res = request.json
      if res["btn_type"] == 'submit':
         #заполнение формы оплаты. Сделать разветвление на если данные были привязаны или нет
         user,cred= 'test','test'
         get_pb(station_id)
         set_time(user,cred)

         return {'status':'ok'}
   return render_template('index1.html')


# то есть по айди станции есть страница где берешь и где возвращаешь. На странице возврата вводишь айди повербанка и нажимаешь кнопку вернуть после чего вставляешь павербанк обратно. Если не вернуть, то счетчик бабок продолжит капать. И каждый час выписывается счет от тинька.
# после того как ввел айди и нажал на кнопку вернуть, запускается таймер 10 сек если за 10 сек не вставляешь, то пизда вася давай по новой
@app.route('/return_pb',methods=['get','post'])
def return_pb():
   change = 'Статус возвращения'
   query = request.args
   station_id=query['id'] #id станции который получаем из параметра запроса
   if request.method == "POST":
      res = request.json
      if res["btn_type"] == 'return':
         if if_returned(res['pb_id'],station_id):
            #Дальше идет закрытие оплаты
            user = 'test'
            change = 'Все окэй'
            return render_template('index_r.html', change=change)

            #cur.execute(f"DELETE FROM status WHERE user = {user}")
         else:
            change = 'Вставьте павербанк пожалуйста, в противном случае оплата продолжит начисляться и в итоге мы спишем с вам большую блин сумму'
            return render_template('index_r.html', change=change)

   return render_template('index_r.html',change=change)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=86, debug=False)