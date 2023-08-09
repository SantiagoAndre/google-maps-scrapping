from .chromedriver import CustomDriver
from .undetecteddriver import UndetectedDriver
from .windows_driver_admin import WindowsDriverAdmin
class Wait:
    SHORT = 4
    LONG = 8
    VERY_LONG = 16




class TaskConfig:
    def __init__(self,number_of_scrapers=1,reviews=1):
        self.number_of_scrapers=number_of_scrapers
        self.reviews = reviews
class Scroller:
    def __init__(self, driver, main_selector,content_selector, how_much = 10000,max_results=None):
        self.driver = driver
        self.main_selector = main_selector
        self.content_selector = content_selector
        self.max_results = max_results
        self.number_of_times_not_scrolled = 0
        self.how_much = how_much

    def scroll(self,f_is_the_end =None):
        # print("hola new scroll")

        el = self.driver.get_element_or_none_by_selector(self.main_selector, Wait.SHORT)
        if el is None:
            return False
        # print("hola el = ",el)

        did_element_scroll = self.driver.scroll_element(el,self.how_much)
        # print("hola did_element_scroll = ",did_element_scroll)

        end_el = f_is_the_end(self.driver) if f_is_the_end else None 
        # print("hola end_el = ",end_el)

        if end_el is not None or (not did_element_scroll and self.number_of_times_not_scrolled > 10):
            return False

        self.number_of_times_not_scrolled += not did_element_scroll
        # print("number_of_times_not_scrolled end_el = ",self.number_of_times_not_scrolled)

        if self.max_results:

            els = self.driver.get_elements_or_none_by_selector(self.content_selector, Wait.SHORT)
            # print("els = ",els)
            if len(els) >= self.max_results:
                # print("returning false max results...")

                return False

        if did_element_scroll:
            print("Scrolling...")
        # print("hola scroll")
        return True