import timer
from locust import HttpUser, task,between,HttpLocust,TaskSet,event
from websocket import create_connection
import json
import time
import gevent


class chat(HttpUser):
    wait_time = between(1, 5)
    host = 'ws://127.0.0.1:8000/'
    #    ws://127.0.0.1:8000/chat/room/samanmr/
    @task
    def sent(self):
        # print("hello")
        counter = 0
        while counter < 20:
            time.sleep(0.1)
            start_at = time.time()
            body = json.dumps({'message': 'hello, world','message_type':'TEXT','username':'samanmr', 'room_name': 'g2'})
            self.ws.send(body)

    def on_stop(self):
        self.ws.close()
        return super().on_stop()
    
    def on_start(self):
        print("hello0")
        ws = create_connection('ws://127.0.0.1:8000/chat/room/g2/')
        self.ws = ws

