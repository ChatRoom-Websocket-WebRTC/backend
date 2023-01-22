import timer
from locust import HttpUser, task,between,HttpLocust,TaskSet,event
from websocket import create_connection
import json
import time
import gevent

class chatTaskSet(TaskSet):
    host = 'http://127.0.0.1:8000/'

    @task
    def authenticate_task(self):
        ws = create_connection('ws://127.0.0.1:5000/chat/room/saman')
        self.ws = ws

        counter = 0
        while counter < 20:
            res = ws.recv()
            data = json.loads(res)
            print(data)
            end_at = time.time()
            response_time = int((end_at - data['start_at']) * 1000000)

    @task
    def sent(self):
        counter = 0
        while counter < 10:
            start_at = time.time()
            body = json.dumps({'message': 'hello, world','message_type':'TEXT','username':'samanmr', 'room_name': '1'})
            self.ws.send(body)
    
    def on_start(self):
        print(self.client.get('http://127.0.0.1:8000/accounts/users/'))


class chatLocust(HttpUser):
    tasks = [chatTaskSet]
    min_wait = 0
    max_wait = 100
