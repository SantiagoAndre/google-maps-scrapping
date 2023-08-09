
import sys
import errno
import traceback
from time import sleep
from urllib.error import ContentTooShortError
from http.client import RemoteDisconnected
from urllib.error import ContentTooShortError, URLError
from .data_utils import istuple
def exit_with_failed_status():
    print('Exiting with status 1')
    sys.exit(1)



def on_exception(f, on_exception):
    try:
        f()
    except Exception as e:
        print(e)
        on_exception()



def ignore_errors(func, instances=None):
    try:
        created_result = func()
        return created_result
    except Exception as e:
        is_valid_error, index = is_errors_instance(
            instances, e)
        if not is_valid_error:
            raise e
        print('Ignoring')
        traceback.print_exc()


def retry_if_is_error(func, instances=None, retries=2, wait_time=None):
    tries = 0
    errors_only_instances = list(
        map(lambda el: el[0] if istuple(el) else el, instances))

    while tries < retries:
        tries += 1
        try:
            created_result = func()
            return created_result
        except Exception as e:
            is_valid_error, index = is_errors_instance(
                errors_only_instances, e)

            if not is_valid_error:
                raise e

            traceback.print_exc()

            if istuple(instances[index]):
                instances[index][1]()

            if tries == retries:
                raise e

            print('Retrying')

            if wait_time is not None:
                sleep(wait_time)

def is_errors_instance(instances, error):
    for i in range(len(instances)):
        ins = instances[i]
        if isinstance(error, ins):
            return True, i
    return False, -1

def retry(func, retry_wait=None, retries=5):
    tries = 0
    while tries < retries:
        tries += 1
        try:
            created_result = func()
            return created_result
        except Exception as e:

            traceback.print_exc()

            if tries == retries:
                raise e

            print('Retrying')

            if retry_wait is not None:
                sleep(retry_wait)


def is_error(errs):
    def fn(e):
        result, index = is_errors_instance(errs, e)
        return result
    return fn

NETWORK_ERRORS = [RemoteDisconnected, URLError,
                  ConnectionAbortedError, ContentTooShortError,  BlockingIOError]

is_network_error = is_error(NETWORK_ERRORS)