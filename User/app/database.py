# -*- coding: utf-8 -*-
from __future__ import annotations

from os import environ
from typing import Any, Dict, List, Optional, Tuple

from bson.objectid import ObjectId
from conf import config
from pymongo import MongoClient
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import _WriteResult

cfg = config("database")
USERNAME = environ.get("MONGO_ROOT_USERNAME", "")
PASSWORD = environ.get("MONGO_ROOT_PASSWORD", "")


def to_str(id: Any) -> str:
    return str(id)


class Mongo:
    __instance: Optional[Mongo] = None
    __client: Optional[MongoClient] = None
    __database: Optional[Database] = None
    __collection: Optional[Collection] = None
    session: Optional[ClientSession] = None
    collection: Optional[str] = None

    def __new__(cls, *args: Any, **kwagrs: Any) -> Mongo:
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, host: str = cfg.host, port: int = cfg.port) -> None:
        self.__client = MongoClient(
            host=host,
            port=port,
            username=USERNAME,
            password=PASSWORD,
            tz_aware=True,
        )
        self.__database = self.__client.get_database(cfg.name)

    def __call__(self, collection: str) -> Mongo:
        if self.__instance is None:
            raise Exception("Fail to allocate")
        if self.__client is None:
            raise Exception("Fail to initialize")
        if self.__database is None:
            raise Exception("Fail to connect database")
        self.collection = collection
        return self

    def __enter__(self) -> Mongo:
        self.session = self.__client.start_session()
        self.__client = self.session.client
        self.__database = self.__client.get_database(cfg.name)
        self.__collection = self.__database.get_collection(self.collection)
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        try:
            self.session.end_session()
        finally:
            self.session = None
            self.__client = None
            self.__database = None
            self.__collection = None

    @property
    def databases(self) -> List[str]:
        return self.__client.list_database_names()

    @property
    def collections(self) -> List[str]:
        if self.__database is None:
            raise Exception("Database is empty")
        return self.__database.list_collection_names()

    @staticmethod
    def serialize(data: Any) -> Any:
        if isinstance(data, Dict):
            output = {}
            for k, v in data.items():
                output[k] = Mongo.serialize(v)
            return output
        if isinstance(data, List):
            return [Mongo.serialize(v) for v in data]
        if isinstance(data, ObjectId):
            return str(data)
        return data

    def __check_collection(self) -> None:
        if self.__collection is None:
            raise Exception("Collection is None")

    @staticmethod
    def _check_acknowledged(result: _WriteResult) -> None:
        if not result.acknowledged:
            raise Exception("Can't execute write operation")

    def insert(self, data: Dict[str, Any]) -> str:
        self.__check_collection()
        result = self.__collection.insert_one(data)
        Mongo._check_acknowledged(result)
        return result.inserted_id

    def bulk_insert(self):
        pass

    def find(self, filter_query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.__check_collection()
        result = self.__collection.find_one(filter=filter_query)
        return Mongo.serialize(result)

    def find_by_id(self, id: str) -> Dict[str, Any]:
        filter_query = {"_id": ObjectId(id)}
        return self.find(filter_query)

    def finds(
        self, filter_query: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        self.__check_collection()
        result = list(self.__collection.find(filter=filter_query))
        return Mongo.serialize(result)

    def finds_by_id(self, id: str) -> List[Dict[str, Any]]:
        self.__check_collection()
        filter_query = {"_id": id}
        return self.finds(filter_query)

    def update(
        self, filter_query: Dict[str, Any], update_data: Dict[str, Any]
    ) -> Tuple[int, int]:
        self.__check_collection()
        update_query = {"$set": update_data}
        result = self.__collection.update_one(filter=filter_query, update=update_query)
        Mongo._check_acknowledged(result)
        return (result.matched_count, result.modified_count)

    def update_by_id(self, id: str, update_data: Dict[str, Any]) -> Tuple[int, int]:
        self.__check_collection()
        filter_query = {"_id": ObjectId(id)}
        return self.update(filter_query, update_data)

    def upsert(
        self, filter_query: Dict[str, Any], update_data: Dict[str, Any]
    ) -> Tuple[int, int, int]:
        self.__check_collection()
        update_query = {"$set": update_data}
        result = self.__collection.update_one(
            filter=filter_query, update=update_query, upsert=True
        )
        Mongo._check_acknowledged(result)
        return (result.matched_count, result.modified_count, result.upserted_id)

    def upsert_by_id(self, id: str, update_data: Dict[str, Any]) -> Tuple[int, int, int]:
        self.__check_collection()
        filter_query = {"_id": id}
        return self.upsert(filter_query, update_data)

    def delete(self, filter_query: Dict[str, Any]) -> int:
        self.__check_collection()
        result = self.__collection.delete_one(filter=filter_query)
        Mongo._check_acknowledged(result)
        return result.deleted_count

    def delete_by_id(self, id: str) -> int:
        self.__check_collection()
        filter_query = {"_id": ObjectId(id)}
        return self.delete(filter_query)
