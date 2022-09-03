# -*- coding: utf-8 -*-
from __future__ import annotations

from os import environ
from typing import Any, Dict, List, Optional

from bson.objectid import ObjectId
from conf import config
from pymongo import MongoClient
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.database import Database

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
        self.__database = self.__client.get_database(cfg.db_name)

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
        self.__database = self.__client.get_database(cfg.db_name)
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

    def insert(self, data: Dict[str, Any]) -> None:
        if self.__collection is None:
            raise Exception("Collection is empty")
        self.__collection.insert_one(data)

    def bulk_insert(self):
        pass

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

    def find(self, query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if self.__collection is None:
            raise Exception("Collection is empty")
        result = self.__collection.find_one(query)
        return Mongo.serialize(result)

    def finds(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if self.__collection is None:
            raise Exception("Collection is empty")
        result = list(self.__collection.find(query))
        return Mongo.serialize(result)

    def update(self):
        pass

    def updates(self):
        pass

    def delete(self):
        pass
