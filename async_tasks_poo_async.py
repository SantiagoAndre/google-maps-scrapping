import asyncio
import random
import signal
from abc import ABC, abstractmethod

class AbstractProducer(ABC):
    def __init__(self,name=""):
        self.name = name
    async def produce(self, queue):
        print(f"Producer {self.name} started")
        async for value in self.generate_items():
            await queue.put(value)
            # print(f'Producer added: {value}')

    @abstractmethod
    async def generate_items(self):
        pass


class AbstractConsumer(ABC):
    def __init__(self,name=""):
        self.name = name
        self.final_data = list()
        self.should_stop_signal = False
        self.lock = asyncio.Lock()  # Lock to protect access to should_stop
    async def consume(self, queue):
        print(f"Consumer {self.name} started")
        while True:
            # Check if we should stop
            if await self.should_stop() and queue.empty():
                self.stop()
                break
            item = await queue.get()
            await self.process_item(item)
            queue.task_done()
    async def stop_signal(self):
        # Set should_stop to True in a thread-safe way
        async with self.lock:
            self.should_stop_signal = True
    async def should_stop(self):
        async with self.lock:   
            return self.should_stop_signal
    def stop(self):
        pass
    @abstractmethod
    async def process_item(self, item):
        pass

    def get_final_data(self):
        return self.final_data
    

class UniqueQueue(object):
    def __init__(self):
        self._data = set()
        self._queue = asyncio.Queue()

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
        self.p_coros = None
        self.c_coros = None
    async def run(self,producers,consumers,QueueClass=asyncio.Queue):
            # Create a queue
            queue = QueueClass()

        
            # Launch producers and consumers
            self.producers = producers
            self.consumers = consumers
            self.p_coros = [asyncio.create_task(task.produce(queue)) for task in producers]
            self.c_coros = [asyncio.create_task(task.consume(queue)) for task in consumers]
            print("hola")
            def signal_handler(sig, frame):
                for coro in self.p_coros+self.c_coros:
                    coro.cancel()
                print("Tasks cancelled.")

            signal.signal(signal.SIGINT, signal_handler)
                # Wait until tasks are complete
            print("hola end")
            

    async def await_ultil_end(self):
        await asyncio.gather(self.p_coros)
        for consumer in self.consumers:
            await consumer.stop_signal()
        await asyncio.gather(self.c_coros)

    def sync_await_ultil_end(self):
        try:
            asyncio.run(self.await_ultil_end())
        except asyncio.exceptions.CancelledError:
            pass

    def sync_run(self,producers,consumers,QueueClass=asyncio.Queue):        
        try:
            asyncio.run(self.run(producers,consumers,QueueClass))
        except asyncio.exceptions.CancelledError:
            pass
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





# use  example

class NumberProducer(AbstractProducer):
    def __init__(self,number) -> None:
        self.number = number
        self.name = f"Producer {number}"
        super().__init__()
    async def generate_items(self):
        for i in range(5):
            value = f"{self.number}=> {i}"
            await asyncio.sleep(random.randint(1,3))
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
        
        await asyncio.sleep(random.randint(1,3))
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