import json, os, sys
from pymongo import MongoClient
parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.append(parent_dir)
from services.secrets_manager import SecretsManager

class Database:
    def __init__(
        self, name: str, database: str="house-rent-591"
    ):
        self._name = name
        self._database = database 
        self.client = None
        self._sm = SecretsManager()
        self._db_connection = self._sm.db_connection
        self._db = self._connect_to_db()
        
    @property
    def db(self):
        return self._db

    def _connect_to_db(self) -> MongoClient:
        if self._name in self._db_connection:
            connection_str, user, password = self._db_connection[self._name]
            return self._connect(connection_str, user, password)
        else:
            raise ValueError(f"Unknown database name: {self._name}")

    def _connect(
        self, connection_str: str, user: str, password: str
    ) -> MongoClient:
        if user and password:
            self.client = MongoClient(connection_str, username=user, password=password)
        else:
            self.client = MongoClient(connection_str)
        return self.client[self._database]

    def disconnect(self):
        self.client.close()

