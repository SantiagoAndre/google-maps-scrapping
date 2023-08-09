import errno
import os
import json
from sys import platform


def is_docker():
    path = '/proc/self/cgroup'

    return (
        os.path.exists('/.dockerenv') or
        os.path.isfile(path) and any('docker' in line for line in open(path))
        or os.environ.get('KUBERNETES_SERVICE_HOST') is not None
    )

def is_mac():
    return platform == "darwin"

def is_linux():
    return platform == "linux" or platform == "linux2"

def is_windows():
    return os.name == 'nt'

def relative_path(path, goback=0):
    levels = [".."] * (goback + -1)
    return os.path.abspath(os.path.join(os.getcwd(), *levels, path))
def silentremove(filename):
    try:
        os.remove(filename)
        return True
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
        else:
            return False




def write_html( data, path,):
    with open(path, 'w', encoding="utf-8") as fp:
        fp.write(data)


def write_file( data, path,):
    with open(path, 'w', encoding="utf-8") as fp:
        fp.write(data)


def read_json(path):
    try:
        with open(path, 'r') as fp:
            users = json.load(fp)
            return users
    except :
        pass
def read_file(path):
    with open(path, 'r') as fp:
        content = fp.read()
        return content
        
def write_json(data, path,  indent=4):
    if type(data) is set:
        data = list(data)
    with open(path, 'w') as fp:
        json.dump(data, fp, indent=indent)

from io import BytesIO
import pandas as pd
def json_to_excel_io(data,**kwargs):
    output = BytesIO()
    pandas_wirter = pd.ExcelWriter(output, engine='xlsxwriter')
    df  =pd.DataFrame(data,)
    df.to_excel(pandas_wirter,**kwargs)
    # print(dir(pandas_wirter))
    pandas_wirter._save()
    
    return output

def json_to_excel(data,filename):
    pandas_wirter = pd.ExcelWriter(filename, engine='xlsxwriter')
    df  =pd.DataFrame(data,)
    df.to_excel(pandas_wirter)
    # print(dir(pandas_wirter))
    pandas_wirter._save()

import time

def timer_decorator_print(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"La función {func.__name__} se ejecutó en {elapsed_time:.6f} segundos.")
        
        return result
    
    return wrapper


def timer_decorator_log(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        with open("execution_times.log", "a") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - La función {func.__name__} se ejecutó en {elapsed_time:.6f} segundos.\n")
        
        return result
    
    return wrapper