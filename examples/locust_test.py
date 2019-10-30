import time
import pyexasol
from pyexasol.connection import ExaConnection

from locust import Locust, TaskSet, events, task

class PyexasolExtensionClient():

    def __init__(self,exa_extension):
        self.exa_extension = exa_extension

    def __getattr__(self, name):
        func = getattr(self.exa_extension,name)
        def wrapper(*args, **kwargs):
            response_type = f"ExaExtension.{name}"
            response_name = f"{args},{kwargs}"
            ignore_error ="locust_ignore_error" in kwargs and kwargs["locust_ignore_error"]
            if "locust_ignore_error" in kwargs:
                del kwargs["locust_ignore_error"]
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                total_time = int((time.time() - start_time) * 1000)
                if not ignore_error:
                    events.request_failure.fire(request_type=response_type, name=response_name, response_time=total_time, exception=e)
                else:
                    events.request_success.fire(request_type=response_type+"(ignore_error)", name=response_name, response_time=total_time, response_length=0)
                raise e
            else:
                total_time = int((time.time() - start_time) * 1000)
                events.request_success.fire(request_type=response_type, name=response_name, response_time=total_time, response_length=0)
                return result
                # In this example, I've hardcoded response_length=0. If we would want the response length to be 
                # reported correctly in the statistics, we would probably need to hook in at a lower level
        return wrapper


class PyexasolClient():
    def __init__(self,dsn,user,password):
        self.conn = pyexasol.connect(dsn=dsn,user=user,password=password,socket_timeout=100)
        self.exa_extension = PyexasolExtensionClient(self.conn.ext) 
       
    def __getattr__(self, name):
        func = getattr(self.conn,name)
        if name == "ext":
            return self.exa_extension
        else:
            def wrapper(*args, **kwargs):
                response_type = f"ExaConnection.{name}"
                response_name = f"{args},{kwargs}"
                ignore_error ="locust_ignore_error" in kwargs and kwargs["locust_ignore_error"]
                if "locust_ignore_error" in kwargs:
                    del kwargs["locust_ignore_error"]
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    total_time = int((time.time() - start_time) * 1000)
                    if not ignore_error:
                        events.request_failure.fire(request_type=response_type, name=response_name, response_time=total_time, exception=e)
                    else:
                        events.request_success.fire(request_type=response_type+"(ignore_error)", name=response_name, response_time=total_time, response_length=0)
                    raise e
                else:
                    total_time = int((time.time() - start_time) * 1000)
                    events.request_success.fire(request_type=response_type, name=response_name, response_time=total_time, response_length=0)
                    return result
                    # In this example, I've hardcoded response_length=0. If we would want the response length to be 
                    # reported correctly in the statistics, we would probably need to hook in at a lower level
            return wrapper

class PyexasolLocust(Locust):
    def __init__(self, *args, **kwargs):
        super(PyexasolLocust, self).__init__(*args, **kwargs)
        self.client = lambda : PyexasolClient(self.dsn,self.user,self.password)

class MyTaskSet(TaskSet):
    schema = "locust"
    table = "import_table"

    def on_start(self):
        client = self.client()
        try:
            client.execute(f"CREATE SCHEMA IF NOT EXISTS {self.schema};")
            client.open_schema(self.schema)
            try:
                client.execute(f"CREATE TABLE {self.table}(a int, b varchar(1000), c float);",locust_ignore_error=True)
            except Exception as e:
                print("Error while creating table",e,flush=True)
        finally:
           client.close()

    @task
    def my_task(self):
        client = self.client()
        try:
           client.open_schema(self.schema)
           client.execute("select 1;")
#           client.ext.insert_multi(self.table,[(i,f"test{i}",i*1.5) for i in range(1)])
           client.import_from_iterable([(i,f"test{i}",i*1.5) for i in range(1)],self.table)
        finally:
            client.close()

class MyLocust(PyexasolLocust):
    task_set = MyTaskSet
    min_wait = 50
    max_wait = 150
    dsn = "localhost:8888"
    user = "sys"
    password = "exasol"
