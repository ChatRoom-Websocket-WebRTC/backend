import timer
from locust import HttpUser, task,between,HttpLocust,TaskSet,event
from websocket import create_connection
import json
import time
import gevent

class chat(HttpUser):
    host = 'ws://127.0.0.1:8000/'

    @task
    def sent(self):
        print("hello")
        counter = 0
        while counter < 10:
            start_at = time.time()
            body = json.dumps({'message': 'hello, world','message_type':'TEXT','username':'samanmr', 'room_name': '1'})
            self.ws.send(body)


    def on_start(self):
        print("hello0")
        ws = create_connection('chat/room/samanmr/')
        self.ws = ws

        counter = 0
        while counter < 20:
            res = ws.recv()
            data = json.loads(res)
            print(data)
            end_at = time.time()
            response_time = int((end_at - data['start_at']) * 1000000)
