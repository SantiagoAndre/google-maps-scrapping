import random
import signal
from abc import ABC, abstractmethod
from concurrent.futures import wait, ThreadPoolExecutor
from queue import Queue
from queue import Empty
from threading import Lock
import traceback
# class SharedObject:
#     def __init__(self):
#         self.producer_count = 0
#         self.lock = Lock()

class AbstractProducer(ABC):
    def __init__(self, name="", ): 
        self.name = name
        self.status = "CREATED"
        

    def produce(self, queue):
        self.status   = "STARTED"

        print(f"Producer {self.name} started")
        for value in self.generate_items():
            queue.put(value)
        self.status = "COMPLETED"
        
            
       
class AbstractConsumer(ABC):
    def __init__(self,name=""):
        self.status = "CREATED"
        self.name = name
        self.final_data = list()
        self.should_stop_signal = False
        self.lock = Lock()  # Lock to protect access to should_stop_signal
        self.lock_final_data = Lock()


    def consume(self, queue):
        self.status   = "STARTED"
        print(f"Consumer {self.name} started")
        while True:
            # Check if we should stop
            
            try:
                item = queue.get(timeout=1)
                self.process_item(item)
                queue.task_done()
            except Empty:
                if self.should_stop() and queue.empty():
                    self.stop()
                    break
                continue
        self.status = "COMPLETED"
        
    def stop_signal(self):
        # Set should_stop to True in a thread-safe way
        print("Accessing to  status thread lock")
        
        with self.lock:
            self.status = "ENDING"
            self.should_stop_signal = True
        print("Status thread  lock end successfully")
        
    def should_stop(self):
        print("Accessing to  status thread lock")
        response = False
        with self.lock:   
            response  = self.should_stop_signal
        print(f"Status thread  lock end successfully {response}")
        return response
        
        pass
    @abstractmethod
    def process_item(self, item):
        pass

    def get_final_data(self,lock = False):
        return self.final_data
    

class UniqueQueue(object):
    def __init__(self):
        self._data = set()
        self._queue = Queue()

    async def put(self, item):
        if item not in self._data:
            self._data.add(item)
            await self._queue.put(item)

    async def get(self):
        item = await self._queue.get()
        self._data.remove(item)
        return item

    def task_done(self):
        self._queue.task_done()

    async def join(self):
        await self._queue.join()

class Scheduler:
    def __init__(self,) -> None:
        self.producers =None
        self.consumers = None
        self.producer_futures = None
        self.consumer_futures = None
        self.executor = ThreadPoolExecutor()
        self.exceptions = []
    def run(self,producers,consumers,QueueClass=Queue):
            # Create a queue
            queue = QueueClass()
            # shared = SharedObject()
            # Launch producers and consumers
            self.producers = producers
            self.consumers = consumers
             # Launch producers and consumers
            # producers_len = len(producers)
            self.producer_futures = [self.executor.submit(self._wrap_task, producer.produce, queue) for producer in producers]
            self.consumer_futures = [self.executor.submit(self._wrap_task, consumer.consume, queue) for consumer in consumers]

    def _wrap_task(self, task, *args, **kwargs):
        # This method wraps your task to handle exceptions
        try:
            task(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            self.exceptions.append(e)
            

    def await_until_end(self):
        # Wait until all producers have finished
        wait(self.producer_futures)
        # Call stop_signal on all consumers
        
        for consumer in self.consumers:
            print("send stop signal")
            # consumer = future.result()
            consumer.stop_signal()
        # Wait until all consumers have finished
        wait(self.consumer_futures)

        if self.exceptions:
            raise Exception(f"Errors occurred in threads: {self.exceptions}")

    def get_all_data(self):
        # Print the final data of each consumer
        all_data = []
        all_data_json = {}
        for  task in self.consumers:


            # print(f"Final data of consumer {i} = ", consumer.get_final_data())
            final_data = task.get_final_data()
            if type(final_data) == dict:
                all_data_json.update(final_data)
            else:
                all_data.extend(final_data)
        return all_data or all_data_json



import time

# use  example

class NumberProducer(AbstractProducer):
    def __init__(self,number) -> None:
        self.number = number
        self.name = f"Producer {number}"
        super().__init__()
    async def generate_items(self):
        for i in range(5):
            value = f"{self.number}=> {i}"
            time.sleep(random.randint(1,3))
            print(f"Producer `{value}`")
            yield value


class NumberConsumer(AbstractConsumer):
    def __init__(self,number) -> None:
        self.name = f"Consumer {number}"
        super().__init__()
        self.final_data  = set()

    async def process_item(self, item):
        print(f"{self.name}: processing `{item}`")

        self.final_data.add(item)
        
        time.sleep(random.randint(1,3))
    def stop(self):
        print(f"{self.name} Finishing")

def test_():
    n,m =4,2
    # Initialize the producers and consumers
    producers = [NumberProducer(i+1) for i in range(n)]  # replace 'n' with the number of producers you want
    consumers = [NumberConsumer(j+1) for j in range(m)]  # replace 'm' with the number of consumers you want

    results = run_tasks(producers,consumers)
    print("All results joined")
    print(list(results))
# test_()