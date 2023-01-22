import timer
from locust import HttpUser, task,between
class User(HttpUser):
    host = 'http://127.0.0.1:8000/'

    @task
    def authenticate_task(self):
        print(self.client.get("accounts/profile/samanmr"))
        print(self.client.get("accounts/profile/samanmr2"))

    
    def on_start(self):
        print(self.client.get('http://127.0.0.1:8000/accounts/users/'))
