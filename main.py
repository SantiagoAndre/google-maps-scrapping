from pymongo.errors import BulkWriteError

from tasks import LinksMapsTask, PlaceMapsTask
from drivers import LazyDriverWrapper, TaskConfig
from utils import read_json, json_to_excel, timer_decorator_log
from mongo import BatchedMongoSaver
# import sync
import settings
import random
from urllib.parse import urlparse
import sys

class KeywordGenerator:
    def __init__(self, states):
        self.states = states

    def get_all_keywords(self):
        industries = settings.industries_collection.find({})
        industries = list(industries)
        for industry in industries:
            for state in self.states:
                for country in state['countries']:
                    for zip in country['zips']:
                        yield (f"{industry['name']} {country['name']} {state['name']} {zip}")

class LinkCollector:
    def __init__(self, driver):
        self.driver = driver
    def get_all_links(self, queries):
        config = TaskConfig(reviews=0)
        for  query in queries:
            # status = sync.get_sync_status(action= 'links_scroll',keyword=query['keyword'])

            # if status == sync.SYNC_STATUS.completed: 
            #     print(f"Links scroll for {query['keyword']} skiped, already completed ")
            #     continue
            n_links_in_db = settings.links_collection.count_documents({'keyword':query['keyword']})
            if n_links_in_db > settings.N_LINKS_TO_SKIP_LINKS_SCROLL:
                print(f"Links scroll for {query['keyword']} skiped, already completed, there are {n_links_in_db} links. ")
                continue
            task = LinksMapsTask(self.driver, query, config)
            links = task.run()
            if not links:continue
            batch = [{'link':link , 'keyword':query['keyword']} for link in links]
            # inserted_limks = [doc.get("_id") for doc in batch]  # Preinicializa con todos los IDs
            try:
                settings.links_collection.insert_many(batch,ordered=False)

                # inserted_ids = response.inserted_ids
            except BulkWriteError:
                # # Maneja o registra los errores
                # for error in bwe.details["writeErrors"]:
                #     if error["code"] == 11000:  # código de error de duplicado
                #         # print(f"Error de duplicado en el link: {error['op']['link']}")
                #         # Elimina los IDs de los documentos que causaron errores
                #         index = error["index"]
                #         links[index] = None

                # Limpia los None de la lista
                pass
                # links = [i for i in links if i is not None]
            
class DataCollector:
    def __init__(self, driver):
        self.driver = driver
        self.batch_contacts_saver = BatchedMongoSaver(settings.contacts_collection,batch_size=100)
        # print(settings.contacts_collection)
    def get_links(self,keyword):
        pipeline = [
            {
                "$match": {"keyword": keyword}
            },
            {
                "$lookup": {
                    "from": settings.CONTACTS_COLLECTION,
                    "localField": "link",
                    "foreignField": "link",
                    "as": "contact_links"
                }
            },
            {
                "$match": {
                    "contact_links": []
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "link": 1
                }
            }
        ]

        result = list(settings.links_collection.aggregate(pipeline))
        return  [doc['link'] for doc in result]

    def visit_pages(self,keyword):
        links = self.get_links(keyword)
        for link in links:
            
            results = PlaceMapsTask(self.driver, {'link': link},config={'keyword':keyword}).run()
            self.batch_contacts_saver.add(results)
            
        self.batch_contacts_saver.flush()

class ReportGenerator:
    def __init__(self) -> None:
        pass

    def generate_report(self, keyword):
        def tranformed_data_generator(cursor):
            for contact in cursor:
                yield self.transform_data(contact)

        cursor = settings.contacts_collection.find({'keyword':keyword})
    
        json_to_excel(tranformed_data_generator(cursor), 'outputs/'+keyword + '.xlsx')
        # cursor.close()
    def remove_protocol(self,url):
        if url:
            parsed_url = urlparse(url)
            return parsed_url.netloc
    def transform_data(self, data):
        return {
            'uuid': str(data['place_id']),  # Convert ObjectId to string
            'created_at': data['create_at'].strftime("%d/%m/%Y"),  # Format date to desired format
            'query': data['keyword'],
            'name': data['title'],
            'fulladdr': data['address'],
            # 'fulladdr1': data['address_1'],
            'local_name': '',  # Data not provided
            'local_fulladdr': data['title'],
            'phone_numbers': data['phone'],
            'latitude': data['coordinates']['latitude'],
            'longitude': data['coordinates']['longitude'],
            'categories': ', '.join(data['categories']),
            # 'reviews': data['reviews'],
            # 'rating': data['rating'],
            'url': data['website'],
            'domain': self.remove_protocol(data['website']),  # Assumption based on provided data
            'thumbnail': data['thumbnail'],
            'addr1': data['complete_address']['street'],
            'addr2': '',  # Data not provided
            'addr3': "",
            'addr4': "",
            'district': data["complete_address"]["borough"],  # Data not provided
            'timezone': data['time_zone']
        }
@timer_decorator_log
def sync_main(states):
    all_keywords = list(KeywordGenerator(states).get_all_keywords())
    # print(all_keywords)
    random.shuffle(all_keywords)
    # queries = [{"keyword": keyword,"max_results": 5} for keyword in all_keywords]
    queries = [{"keyword": keyword} for keyword in all_keywords]
    driver = LazyDriverWrapper(block_images_fonts_css=True, headless=True, use_undetected_driver=False)
    LinkCollector(driver).get_all_links(queries)
    report_generator = ReportGenerator()
    for keyword in all_keywords:

        DataCollector(driver).visit_pages(keyword,)
        report_generator.generate_report(keyword)
        driver.close()

if __name__ == "__main__":
    states_file = sys.argv[1]
    print(f"Processing {states_file}")
    states = read_json(states_file)
    sync_main(states)
class QueriesStatus:
    PENDDING = 'P' 
    LINKS_TASK = 'LT'
    PLACES_TASK = 'PT'
    COMPLETED  =  'C'


# report_generator = ReportGenerator()
# report_generator.generate_report("test")

# docker run \
# --env-file .env \
# --network mongo_default \
# -v $(pwd)/outputs:/src/outputs \
# -v $(pwd)/queries.json:/src/queries.json \
# santosdev20/googlemapsscrapping:v1 
