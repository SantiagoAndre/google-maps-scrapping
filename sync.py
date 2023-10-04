import settings 
class SYNC_STATUS:
    started = 'started'
    completed = 'completed'
    not_found = 'not_found'


def start_sync(filter_columns,**data):


    data['status'] = SYNC_STATUS.started
    filter_data = {k:v for k,v in data.items() if k in filter_columns}
    data = {k:v for k,v in data.items() if k not in filter_columns}
    # Realizar el upsert
    result = settings.sync_management_collection.update_one(
        filter=filter_data,
        update={'$set': data},
        upsert=True
    )
    data['_id'] = result.upserted_id
    return data



def complete_sync(sync_obj,status=SYNC_STATUS.completed):

    result = settings.sync_management_collection.update_one({'_id':sync_obj['_id']},{'$set':{'status':status}})
    success = result.matched_count !=0
    print(f"Complete sync {sync_obj['_id']} complete: {success}")
    return success

def get_sync_status(**filter):
    obj = settings.sync_management_collection.find_one(filter,{'status':1,'_id':1})
    if obj:
        return obj['status']
    return SYNC_STATUS.not_found


    

