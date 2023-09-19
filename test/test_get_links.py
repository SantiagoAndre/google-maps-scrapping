
from tasks import LinksMapsTask,PlaceMapsTask
from drivers import TaskConfig,LazyDriverWrapper
from utils import write_json,read_json
driver=  LazyDriverWrapper(block_images_fonts_css=True,headless=True,use_undetected_driver=False)
def test_getlinks():
    str_queries = """PEST CONTROL JEFFERSON COUNTY PENNSYLVANIA  13734
    PEST CONTROL JEFFERSON COUNTY PENNSYLVANIA  15730
    PEST CONTROL JEFFERSON COUNTY PENNSYLVANIA  10731
    PEST CONTROL JEFFERSON COUNTY PENNSYLVANIA  12732
    PEST CONTROL JEFFERSON COUNTY PENNSYLVANIA  15733
    PEST CONTROL JEFFERSON COUNTY PENNSYLVANIA  13734
    PEST CONTROL JEFFERSON COUNTY PENNSYLVANIA  15735"""
    try:
        queries = [{"keyword":q} for q in str_queries.split("\n")]
        config = TaskConfig(reviews=0)
        all_links = set()
        for query in queries:
            links = LinksMapsTask(driver,query,config).run()
            all_links.update(links)
        write_json(all_links,"all_links.json")
        
    except Exception as e:
        write_json(all_links,"all_links.json")
        raise e
def test_place_maps():
    links  = read_json("all_links.json")
    results = PlaceMapsTask(driver,{'links':links}).run()
    write_json(results,"results.json")