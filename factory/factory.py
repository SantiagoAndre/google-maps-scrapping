import os
from selenium.webdriver.chrome.options import Options as GoogleChromeOptions
from undetected_chromedriver import ChromeOptions
from selenium.common.exceptions import WebDriverException

from .window_size import WindowSize

from .download_driver import download_driver
from utils import (is_windows,is_docker,relative_path,retry_if_is_error,NETWORK_ERRORS)
from utils import  (get_driver_string,get_eager_startegy,create_profile_path,get_driver_path,
                    hide_automation_flags,load_cookies,delete_corrupted_files,get_user_agent)
from drivers import UndetectedDriver,CustomDriver



class BrowserConfig:
    def __init__( self, 
                  headless=False,  
                  use_undetected_driver=False, 
                  block_images_fonts_css = False, 
                  profile=None, 
                  is_tiny_profile=False,
                  user_agent=None,
                  window_size=WindowSize.window_size_1920_1080, 
                  is_eager=False, 
                  ):
        self.user_agent = user_agent or get_user_agent()
        self.headless = headless
        self.window_size = window_size
        self.block_images_fonts_css = block_images_fonts_css


        if profile is not None:
            self.profile = str(profile)
        else:
            self.profile = None
        self.is_eager = is_eager
        self.use_undetected_driver = use_undetected_driver

        self.is_tiny_profile = is_tiny_profile

        if self.is_tiny_profile and self.profile is None:
            raise Exception('Profile must be given when using tiny profile')
        





class CustomDriverFactory:

    def create_directories(self,):
        dir_paths = ['build/', 'tasks/', 'output/', 'profiles/']
        driver_path = 'build/chromedriver.exe' if is_windows() else 'build/chromedriver'

        if not os.path.isfile(driver_path):
            print('[INFO] Downloading Chrome Driver in build/ directory. This is a one-time process. Download in progress...')
            download_driver()

        for dir_path in dir_paths:
            abs_path = relative_path(dir_path, 0)
            if not os.path.exists(abs_path):
                os.makedirs(abs_path)
    def configure_options(self, config, options):
        if config.headless:
            options.add_argument('--headless=new')

        if is_docker():
            print("Running in Docker, So adding sandbox arguments")
            options.arguments.extend(["--no-sandbox", "--disable-setuid-sandbox"])

        if config.block_images_fonts_css:
            options.add_experimental_option(
                "prefs", {
                    "profile.managed_default_content_settings.images": 2,
                    "profile.managed_default_content_settings.stylesheet": 2,
                    "profile.managed_default_content_settings.fonts": 2,
                }
            )
        
    
    def add_essential_options(self,options, profile, window_size, user_agent):
        options.add_argument("--start-maximized")
        options.add_argument(f'--user-agent={user_agent}')


        if profile is not None:
            profile = str(profile)
            path = create_profile_path(profile)
            user_data_path = f"--user-data-dir={path}"
            options.add_argument(user_data_path)

        return {"window_size": window_size, "user_agent": user_agent, "profile": profile}
    def create_driver(self,config: BrowserConfig):
        def run():
            self.create_directories()
            is_undetected = config.use_undetected_driver
            options = ChromeOptions() if is_undetected else GoogleChromeOptions()

            self.configure_options(config, options)
            driver_attributes = self.add_essential_options(options, None if config.is_tiny_profile else config.profile, config.window_size, config.user_agent)

            print(get_driver_string(driver_attributes))

            desired_capabilities = get_eager_startegy() if config.is_eager else None

            if is_undetected:
                driver = UndetectedDriver(desired_capabilities=desired_capabilities, options=options)
            else:
                hide_automation_flags(options)
                options.arguments.extend(["--disable-web-security", "--disable-site-isolation-trials", "--disable-application-cache"])
                path = relative_path(get_driver_path(), 0)
                print(path)
                driver = CustomDriver(desired_capabilities=desired_capabilities, chrome_options=options, executable_path=path)

            if driver_attributes["profile"] is None:
                del driver_attributes["profile"]

            driver._init_data = driver_attributes
            return driver

        driver = retry_if_is_error(run, NETWORK_ERRORS + [(WebDriverException, lambda: delete_corrupted_files(config.profile) if config.profile else None)], 5)
        print("Launched Browser")

        if config.is_tiny_profile:
            load_cookies(driver, config)

        driver.browser_config = config
        print("asd")
        return driver