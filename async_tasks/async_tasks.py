
import asyncio
import random

async def producer(queue,generator):
    print("Producer started")

    for value in generator:
        await queue.put(value)
        print(f'Producer add: {value}')
        # espera un segundo
        # await asyncio.sleep(1)

async def consumer(queue,f_consumer_task:callable):
    print("Consumer started")
    while True:
        # espera un elemento de la cola
        item =  await queue.get()
        # proceso del elemento
        print(f'Counsumer got : {item}')
        f_consumer_task(item)
        # Indica a la cola que el elemento ha sido procesado.
        queue.task_done()

    


def run_tasks(generator,f_consumer_task):

    try:
        
        async def main():
            # Crea una cola
            queue = asyncio.Queue()  # Establece un límite de tamaño para la cola
            
            # lanza productor y consumidor
            producer_coro = asyncio.create_task(producer(queue,generator))

            consumer_coro = asyncio.create_task(consumer(queue,f_consumer_task))

            # espera hasta que las tareas se completen 
            await asyncio.gather(producer_coro, consumer_coro)
        asyncio.run(main())
        
    except KeyboardInterrupt:
        # el usuario presionó CTRL+C, cancela las tareas
        # producer_coro.cancel()
        # consumer_coro.cancel()
        print("Tareas canceladas.")


from time import sleep
def test_async_tasks():
    generator = (i for i in range(100))
    final_data  = set()
    def consumer_f(item):
        print(f"processing {item } item")
        final_data.add(item)
        # asyncio.sleep()(random.randint(1,3))

    run_tasks(generator,consumer_f)
    print("final data = ",final_data)

test_async_tasks()

