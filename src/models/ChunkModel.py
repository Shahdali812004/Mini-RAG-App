from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk 
from models import DataBaseEnum
from pymongo import InsertOne
from bson.objectid import ObjectId

class ChunkModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    async def create_chunk(self, chunk: DataChunk):
        # insert one document in chunk collection
        result = await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))
        chunk._id = result.inserted_id
        return chunk
    
    async def get_chunk(self, chunk_id: str):
        # find one document in chunk collection
        record = await self.collection.find_one({
            "_id": ObjectId(chunk_id)
        })
        if record is None:
            return None
        return DataChunk(**record)
    
    async def insert_many_chunks(self, chunks: list, batch_size: int = 100):
        # insert many documents in chunk collection
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
           
            # define the operations to be performed in bulk
            operations = [
                InsertOne(chunk.dict(by_alias=True, exclude_unset=True)) for chunk in batch
            ]
            await self.collection.bulk_write(operations)

        return len(chunks)
    
    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        # delete many documents in chunk collection by project_id
        result = await self.collection.delete_many({
            "chunk_project_id": project_id
        })
        return result.deleted_count