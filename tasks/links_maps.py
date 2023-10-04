
import urllib.parse
from urllib.parse import urlparse, urlunparse
from utils import read_json,write_json
from drivers import Wait,Scroller,TaskConfig

class LinksMapsTask():
    def __init__(self,driver,data,config) -> None:
        self.driver = driver
        self.data = data
        self.config = config
        self.current_url = None
    def visit_gmap(self,driver, keyword):
        endpoint = f'maps/search/{urllib.parse.quote_plus(keyword)}'
        url = f'https://www.google.com/{endpoint}'
        self.current_url = url
        print("opening ", url)
        driver.get_by_current_page_referrer(url)

        if not driver.is_in_page(endpoint, Wait.LONG):
            if driver.is_in_page("consent.google.com", Wait.SHORT):
                el = driver.get_element_or_none_by_selector('form:nth-child(2) > div > div > button', Wait.LONG)
                el.click()
            print('Revisiting')
            self.visit_gmap(driver, keyword)


    def get_links(self,driver, main_selector,content_selector, keyword, max_results=None):
        self.visit_gmap(driver, keyword)
        # maps_exception= driver.get_element_or_none_by_selector("div.s61tDd > span, div.L5xkq > div, div.Hk4XGb > div,div.Bt0TOd", Wait.SHORT)

        
        # if maps_exception:
        #     print(maps_exception)        
        #     print("maps exception: ",maps_exception.text,'->',self.current_url)
        #     return []
        # else:
        #     print("there are results, starting links extraction for ",keyword)

        scroller = Scroller(driver, main_selector,content_selector, max_results=max_results,how_much = 40000)
        f_is_the_end =  lambda driver: driver.get_element_or_none_by_selector("p.fontBodyMedium > span > span", Wait.SHORT)
        while scroller.scroll(f_is_the_end):
            pass

        def extract_links(elements):
            def remove_query_parameters(url):
                parsed_url = urlparse(url)
                return urlunparse(
                    (parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', '')
                )
            def extract_link(el):
                url = el.get_attribute("href")
                if url:
                    return remove_query_parameters(url)

            return list(map(extract_link, elements))

        els = driver.get_elements_or_none_by_selector(content_selector, Wait.LONG)
        
        links = extract_links(els) if els else []

        if max_results is not None:
            return links[:max_results]

        return links


    def run( self):
        keyword = self.data['keyword']
        max_results = self.data.get('max_results')
        main_selector = '[role="feed"]'
        content_selector = '[role="feed"] >  div > div > a'
        links = list(self.get_links(self.driver, main_selector,content_selector, keyword, max_results))
        # print("scroll ended ")
        for i in range(self.config.reviews):
            print(f"Reviewing {i+1}")
            self.driver.sleep(1)
            new_links = self.get_links(self.driver, main_selector,content_selector, keyword, max_results)
            links.update(new_links)  # this is a set, only add when the element doesn't exist in the set
        len_links = len(links)
        # if len(links) <=1:
       
        print(f'Fetched {len(links)} links.')
        return links

        