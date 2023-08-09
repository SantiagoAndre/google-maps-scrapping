from datetime import datetime
from fake_useragent import UserAgent

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
from time import sleep
import os
from .filesystem_management import is_windows,silentremove,read_json


# time management

def keep_doing(func, wait=1):
    while True:
        func()
        sleep(wait)
def sleep_for_n_seconds(n):
    print(f"Sleeping for {n} seconds...")
    sleep(n)


def sleep_forever():
    print('Sleeping Forever')
    while True:
        sleep(100)
def current_timestamp():
    return int(datetime.now().timestamp())


def time_it(func, message=''):
    now = current_timestamp()
    result = func()
    end = current_timestamp()
    print('Execution time: ' + message, end - now)
    return result

# prints


def pretty_print(result):
    print(json.dumps(result, indent=4))
def pretty_format_time(time):
   return time.strftime("%H:%M:%S, %d %B %Y").replace(" 0", " ").lstrip("0")


# datetime

datetime_format = '%Y-%m-%d %H:%M:%S'

def str_to_datetime(when):
    return datetime.strptime(
        when, datetime_format)


def datetime_to_str(when):
    return when.strftime(datetime_format)


# selenium driver utils


def get_current_profile_path(config): 
    profiles_path = f'profiles/{config.profile}/'
    # profiles_path =  relative_path(path, 0)
    return profiles_path



def get_boolean_variable(name: str, default_value: bool = None):
    # Add more entries if you want, like: `y`, `yes`, ...
    true_ = ('True', 'true', '1', 't')
    false_ = ('False', 'false', '0', 'f')
    value = os.getenv(name, None)
    if value is None:
        if default_value is None:
            raise ValueError(f'Variable `{name}` not set!')
        else:
            value = str(default_value)
    if value.lower() not in true_ + false_:
        raise ValueError(f'Invalid value `{value}` for variable `{name}`')
    return value in true_

from .filesystem_management import relative_path,write_json
def save_cookies(driver, config):
            current_profile_data = get_current_profile_path(config) + 'profile.json'
            current_profile_data_path =  relative_path(current_profile_data, 0)

            driver.execute_cdp_cmd('Network.enable', {})
            cookies = (driver.execute_cdp_cmd('Network.getAllCookies', {}))
            driver.execute_cdp_cmd('Network.disable', {})

            if type(cookies) is not list:
                cookies = cookies.get('cookies')
            write_json(cookies, current_profile_data_path)

def get_driver_url_safe(driver):
    try:
        return driver.current_url
    except:
        return "Failed to get driver url"

def get_page_source_safe(driver):
    try:
        return driver.page_source
    except:
        return "Failed to get page_source"


def get_user_agent():
        ua = UserAgent()

        # Obtenemos un user agent válido para Chrome
        user_agent = ua.chrome
        print(f"Automatic choose user agent = {user_agent}")
        return user_agent


def create_profile_path(user_id):
    PROFILES_PATH = 'profiles'
    PATH = f'{PROFILES_PATH}/{user_id}'
    path = relative_path(PATH, 0)
    return path

def hide_automation_flags(options):
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--disable-blink-features")

    options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # New Options
    options.add_argument("--ignore-certificate-errors")
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-extensions")

def get_driver_path():
    executable_name = "chromedriver.exe" if is_windows() else "chromedriver"
    dest_path = f"build/{executable_name}"
    return dest_path



def get_driver_string(driver_attributes):
    driver_string = f"Creating Driver with window_size={driver_attributes['window_size']} and user_agent={driver_attributes['user_agent']}"
    if driver_attributes["profile"] is not None:
        driver_string = f"Creating Driver with profile {driver_attributes['profile']}, {driver_string}"
    return driver_string

def get_eager_startegy():

    caps = DesiredCapabilities().CHROME
    # caps["pageLoadStrategy"] = "normal"  #  Waits for full page load
    caps["pageLoadStrategy"] = "none"   # Do not wait for full page load
    return caps

def delete_corrupted_files(user_id):
    is_success = silentremove(
        f'{create_profile_path(user_id)}/SingletonCookie')
    silentremove(f'{create_profile_path(user_id)}/SingletonSocket')
    silentremove(f'{create_profile_path(user_id)}/SingletonLock')

    if is_success:
        print('Fixed Profile by deleting Corrupted Files')
    else:
        print('No Corrupted Profiles Found')


def load_cookies(driver, config):
    if driver.__class__.__name__ != "CustomDriver": return

    current_profile = get_current_profile_path(config)
    current_profile_path = relative_path(current_profile, 0)

    if not os.path.exists(current_profile_path):
        os.makedirs(current_profile_path)

    current_profile_data = get_current_profile_path(config) + 'profile.json'
    current_profile_data_path = relative_path(current_profile_data, 0)

    if not os.path.isfile(current_profile_data_path):
        return

    cookies = read_json(current_profile_data_path)
    # Enables network tracking so we may use Network.setCookie method
    driver.execute_cdp_cmd('Network.enable', {})
    # Iterate through pickle dict and add all the cookies
    for cookie in cookies:
        # Fix issue Chrome exports 'expiry' key but expects 'expire' on import
        if 'expiry' in cookie:
            cookie['expires'] = cookie['expiry']
            del cookie['expiry']
        # Replace domain 'apple.com' with 'microsoft.com' cookies
        cookie['domain'] = cookie['domain'].replace(
            'apple.com', 'microsoft.com')
        # Set the actual cookie
        driver.execute_cdp_cmd('Network.setCookie', cookie)

    driver.execute_cdp_cmd('Network.disable', {})

