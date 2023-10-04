
from selenium.common.exceptions import InvalidSessionIdException
from threading import Lock

from .windows_driver_admin import WindowsDriverAdmin

from factory.factory import CustomDriverFactory,BrowserConfig

windowsadmin = WindowsDriverAdmin(lock=Lock())
class LazyDriverWrapper:
    # block_images_fonts_css=True,headless=self.headless,use_undetected_driver=False
    def __init__(self,**kwargs):
        self._driver = None
        self.headless =kwargs.get("headless",False)
        self.kwargs = kwargs
        self.current_url = None

    @property
    def driver(self):
        if self._driver is None:
            self._driver = self.create_driver()
        return self._driver
    
    def create_driver(self):
        # headless = True
        driver  =  CustomDriverFactory().create_driver(BrowserConfig(**self.kwargs))
        if self.current_url:  # Navigate to the stored URL if it exists
            self._driver.get(self.current_url)
        if not self.headless:
            windowsadmin.add_driver(driver)
        return driver

    def __getattr__(self, attr):
        # print(attr)
        obj_attr  = getattr(self.driver, attr)
        if attr == "close" and not self.headless and callable(obj_attr): 
            def wrapper(*args,**kwargs):
                windowsadmin.remove_driver(self.driver)
                return obj_attr(*args,**kwargs)
            return wrapper
        if callable(obj_attr):
        
            def wrapper(*args,**kwargs):
                try:
                    result = obj_attr(*args, **kwargs)
                    if attr == "get":  # Capture the URL when the 'get' method is called
                        self.current_url = args[0] if args else None
                    return result
                except InvalidSessionIdException:
                    self._driver = None
                    print("Driver restarted")
                        
                    return getattr(self.driver, attr)(*args, **kwargs)
            return wrapper
        return obj_attr