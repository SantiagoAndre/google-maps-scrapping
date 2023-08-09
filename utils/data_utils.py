def get_range(_from, _to):
    return ",".join(map(str, list(range(_from, _to))))


def find_by_key(ls,  key, value):
    for index in range(len(ls)):
        user = ls[index]
        if user[key] == value:
            return user


def find_by_id(ls, id):
    return find_by_key(ls, 'id', id)


def remove_nones(list):
    return [element for element in list if element is not None]



def merge_list_of_dicts(*dicts):
    result = []
    for i in range(len(dicts[0])):
        el = {}
        for each_dict in dicts:
            el.update(each_dict[i])
        result.append(el)
    return result


def merge_dicts_in_one_dict(*dicts):
    el = {}
    for each_dict in dicts:
        el.update(each_dict)
    return el


def wrap_with_dict(ls, key):
    def wrap(i):
        return {f'{key}': i}
    return list(map(wrap, ls))


def delete_from_dicts(ls, key):
    for x in ls:
        x.pop(key)
    return ls


def extract_from_dict(ls, key):
    return list(map(lambda i: i[key], ls))



def flatten(l):
    return [item for sublist in l for item in sublist]

def istuple(el):
    return type(el) is tuple

def divide_list(input_list, num_of_groups=6, skip_if_less_than=20):
    if skip_if_less_than is not None and len(input_list) < skip_if_less_than:
        return [input_list]

    group_size = len(input_list) // num_of_groups
    remainder = len(input_list) % num_of_groups

    divided_list = [input_list[i*group_size:(i+1)*group_size] for i in range(num_of_groups)]
    
    for i in range(remainder):
        divided_list[i].append(input_list[-i-1])
        
    return divided_list
