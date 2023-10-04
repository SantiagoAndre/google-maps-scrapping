
import re

import selenium
from drivers import Wait
from datetime import datetime

class PlaceMapsTask():
    def __init__(self,driver,data,config=None) -> None:
        self.driver = driver
        self.data = data
        self.config = config
    def get_heading_text(self,link, max_attempts=5):
        for _ in range(max_attempts):
            self.driver.get_by_current_page_referrer(link)
            heading = self.driver.get_element_or_none_by_selector('h1', Wait.SHORT)
            if heading and heading.text:
                return heading.text
            print("Did Not Get Heading. Retrying ...", link)
            self.driver.short_random_sleep()

        print("Failed to retrieve heading text after 5 attempts. Skipping...", link)
        self.driver.save_screenshot("screenshots")
        return ''

    def modify_address(self,address, full_state_name):
        # Quitar el nombre del negocio
        if address is None: return None
        address = address.split(',', 1)[-1].strip()
        if full_state_name:
            # Reemplazar el estado abreviado por el nombre completo del estado
            pattern = r',\s*([A-Z]{2})\s*(?=\d)'
            address = re.sub(pattern, f', {full_state_name} ', address)
        # Quitar el país al final
        address = re.sub(r',\s*Estados Unidos$', '', address)
        
        return address.strip()

    def run(self,):
        keyword = self.config['keyword']
        link = self.data['link']
        # keyword = self.data['keyword']
        title = self.get_heading_text(link)
        # if not title:
        #     return {'link':link,'keyword':keyword}

        out_dict = {'link': link, 'title': title,'keyword':keyword,'create_at':datetime.now()}#,'keyword':keyword}
        try:
            additional_data = self.driver.execute_file('get_more_data.js')
            out_dict.update(additional_data)
        except selenium.common.exceptions.JavascriptException as E:
            if self.driver.is_in_page("consent.google.com", Wait.LONG):
                el = self.driver.get_element_or_none_by_selector('form:nth-child(2) > div > div > button', Wait.LONG)
                if el: 
                    el.click()
                print('Revisiting')
                return self.get_data(link)
            out_dict['error'] = str(E)
        except:
            out_dict['error'] = str(E)
        out_dict['address'] = self.modify_address(out_dict['address'],out_dict['complete_address'].get('state',None))
        print('Done: ' + out_dict.get('title', ''))
        return out_dict

    # def run(self):
    #     results = [res for res in map(self.get_data, self.data['links']) if res is not None]
    #     return results
