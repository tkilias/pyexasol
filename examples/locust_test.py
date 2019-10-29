import time
import pyexasol
from pyexasol.connection import ExaConnection

from locust import Locust, TaskSet, events, task

class PyexasolClient():
    def __init__(self,dsn,user,password):
        self.conn = pyexasol.connect(dsn=dsn,user=user,password=password)
       
    def __getattr__(self, name):
        func = getattr(self.conn,name)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                total_time = int((time.time() - start_time) * 1000)
                events.request_failure.fire(request_type=name, name=name, response_time=total_time, exception=e)
            else:
                total_time = int((time.time() - start_time) * 1000)
                events.request_success.fire(request_type=name, name=name, response_time=total_time, response_length=0)
                # In this example, I've hardcoded response_length=0. If we would want the response length to be 
                # reported correctly in the statistics, we would probably need to hook in at a lower level
        
        return wrapper

class PyexasolLocust(Locust):
    def __init__(self, *args, **kwargs):
        super(PyexasolLocust, self).__init__(*args, **kwargs)
        self.client = PyexasolClient(self.dsn,self.user,self.password)

class MyTaskSet(TaskSet):
    @task
    def my_task(self):
        self.client.execute("select *")

class MyLocust(PyexasolLocust):
    task_set = MyTaskSet
    min_wait = 50
    max_wait = 150
    dsn = "localhost:8888"
    user = "sys"
    password = "exasol"
