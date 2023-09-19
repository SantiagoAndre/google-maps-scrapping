from pymongo import MongoClient
from bson import ObjectId
import settings
class BatchedMongoSaver:
    def __init__(self, collection, batch_size=1000):
        # self.db =  settings.db
        self.collection = collection
        self.buffer = []
        self.batch_size = batch_size

    def add(self, data):
        """Agrega datos al buffer y guarda en MongoDB si se alcanza el tamaño del lote."""
        if '_id' not in data: data['_id'] = ObjectId()
        self.buffer.append(data)
        if len(self.buffer) >= self.batch_size:
            self.flush()
        return data['_id']

    def flush(self):
        """Guarda los datos en MongoDB y limpia el buffer."""
        if self.buffer:
            try:
                self.collection.insert_many(self.buffer,ordered=False)
            except:
                pass
            self.buffer = []

    def close(self):
        """Guarda cualquier dato restante y cierra la conexión."""
        self.flush()
        # self.client.close()

# Uso:
# saver = BatchedMongoSaver("all_data_sync", batch_size=1000)
# for data in data_generator():
#     saver.add(data)
# saver.close()
