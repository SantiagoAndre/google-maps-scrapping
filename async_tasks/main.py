


from  async_tasks_poo import AbstractConsumer,AbstractProducer,Scheduler

from tasks import LinksMapsTask,PlaceMapsTask

from drivers import TaskConfig,LazyDriverWrapper

from utils import write_json,read_json,divide_list,json_to_excel

from threading import Lock
from concurrent.futures import wait

import random

class LinksProducer(AbstractProducer):
    lock = Lock()
    summary_links_lock = Lock()
    def __init__(self,number,driver,queries,all_links) -> None:
        self.queries = queries
        self.driver = driver
        self.number = number
        self.all_links = all_links
        self.name = f"Producer {number}"
        self.links_summary = []
        super().__init__(f"LinksProducer {number}")
    
    
    def links_summary_f(self,query,current_url,links):
        # print("Accessing to summary links lock")
        # with self.summary_links_lock:
            query.update({'link':current_url,'count':len(links)})
            self.links_summary.append(query)
            if len(self.links_summary) > 30:
                links_summary = read_json("links_summary_sync.json") or []
                links_summary.extend(self.links_summary)
                write_json(links_summary,"links_summary_sync.json")
                self.links_summary = []
        # print("Summary links lock end successfully")
        
    def generate_items(self):
        config = TaskConfig(reviews=0)
        print(self.queries)
        for i,query in enumerate(self.queries):
            print("query ",i)
            task = LinksMapsTask(self.driver,query,config)
            links = task.run()
            self.links_summary_f(query,task.current_url,links)
            for link in links:
                # print("Accessing to Links lock")
                data = None
                # with self.lock:
                if link not in self.all_links: 
                    self.all_links.append(link)
                    data =  {'link':link,'config':query}
                # print("Summary links lock end successfully")
                    yield data 
                
            self.driver.sleep( 0.5)
        self.stop()
    def stop(self):
        links_summary = read_json("links_summary_sync.json") or []
        links_summary.extend(self.links_summary)
        write_json(links_summary,"links_summary_sync.json")
        self.links_summary = []
        # self.driver.close()



class PlacesConsumer(AbstractConsumer):
    def __init__(self,number,driver) -> None:
        self.name = f"Places Consumer {number}"
        self.driver =driver
        super().__init__(f"PlacesConsummer {number}")
        self.final_data  = list()
        self.lock_final_data = Lock()

    def process_item(self, data):
        link = data['link']
        keyword = data['keyword']
        results = PlaceMapsTask(self.driver,{'link':link,"keyword":keyword}).run()
        # print("Accessing to  final data lock")

        with self.lock_final_data:
            self.final_data.append(results)
        # print("Final data lock end successfully")
        
    def clean_finaldata(self):
        # print("Accessing to  final data lock")
        final_data = []
        with self.lock_final_data:
            final_data = self.final_data
            self.final_data = []
        # print("Final data lock end successfully")
        return final_data


    def stop(self):
        print(f"{self.name} Finishing")
        # self.driver.close()
from threading import Lock

from time import sleep
def batch_saving(consumers):
    
    all_data = []
    active_consumers =  True
    while active_consumers:
        print("Batch saving: Sleeping 20 sec ...")
        sleep(20)
        active_consumers = False
        all_data = []
        for consumer in consumers:
            if consumer.status != "COMPLETED": active_consumers = True
            data  = consumer.clean_finaldata()
            all_data.extend(data)
        if all_data:
            all_all_data = read_json("all_data.json") or []
            all_all_data.extend(all_data)
            write_json(all_all_data,"all_data.json")
            print(f"Batch saving: Saved a batch. Batch len {len(all_data)}. Total data len {len(all_all_data)} ...")
        else:
            print(f"Batch saving: Empty batch")

    print(f"Batch saving: There is no active consumers, ending.")
    json_to_excel(all_all_data , "all_all_data.xlsx")
    print(f"Batch saving: all_all_data.xlsx created, ending.")


def get_all_keywords():
    industries = read_json("industries.json")
    states = [
        {
            "name": "PENNSYLVANIA",
            "countries": [
                {
                    "name": "JEFFERSON COUNTY",
                    "zips": [
                        19140
                    ]
                },
                {
                    "name": "PHILADELPHIA COUNTY",
                    "zips": [
                        19092,19093
                    ]
                },
                {
                    "name": "DELAWARE COUNTY",
                    "zips": [
                        19010,19013
                    ]
                }
            ]
        }
    ]
    #         {
    #         "name":"PENNSYLVANIA",
    #         "countries":[
    #             {
    #                 "name":"JEFFERSON COUNTY",
    #                  "zips":[19140,1934,12313,312,]
    #             },
    #             {
    #                 "name":"JEFFERSON COUNTY",
    #                  "zips":[19140,1934]
    #             }
    #         ]
    #     }
    # ]
    # zips = [19140]
    # PEST CONTROL JEFFERSON COUNTY PENNSYLVANIA  15730
    # * 59 industrias PENNSYLVANIA - PHILADELPHIA COUNTY - 19140
    for industry in industries:
        for state in states:
            for country in state['countries']:
                for zip in country['zips']:
                    yield (f"{industry} {country['name']} {state['name']} {zip}")





            


def test_all():
    all_keywords = list(get_all_keywords())
    random.shuffle(all_keywords)
    all_keywords =all_keywords
    print("allkeywords: ",len(all_keywords))
    queries = [{"keyword":keyword} for keyword in all_keywords]
    # print(len(queries))
    # print(len(divide_list(queries, num_of_groups=1, skip_if_less_than=10)))
    all_links = []
    producers = [LinksProducer(i+1,LazyDriverWrapper(),part,all_links) for i,part in enumerate(divide_list(queries, num_of_groups=2, skip_if_less_than=10))]
    places_consumers = [PlacesConsumer(i+1,LazyDriverWrapper()) for i in range(3)]
    # links_middleware = UniqueLinksMiddleware(1)
    print("workers created")
    unique_links_scheduler = Scheduler()

    unique_links_scheduler.run(producers,places_consumers)
    
    # places_data_scheduler =  Scheduler()
    # print("workers stage 1 started")

    # places_data_scheduler.run([links_middleware],places_consumers)
    # print("workers stage 2 started")
    # batch_saving_futures  = unique_links_scheduler.executor.submit(batch_saving,places_consumers)

    batch_saving(places_consumers)
    unique_links_scheduler.await_until_end()


    # wait(batch_saving_futures)
    # print("Waiting to stop first stage")
    # places_data_scheduler.await_until_end()
    # print("Waiting to stop second stage")

    # places_data = places_data_scheduler.get_all_data()
    # write_json(places_data , "places_data.json")
