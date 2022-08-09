import json
from typing import Dict, List

from pydantic import BaseModel

from backend.models import Row, TransactionRow, UserRow
from backend.models.interfaces import Database


class InMemoryDB(Database):
    def __init__(self):
        self.users: List[UserRow] = []
        self.transactions: List[TransactionRow] = []
        self._tables: Dict[str, List[Row]] = {
            "transactions": {
                "schema": TransactionRow,
                "data": self.transactions,
            },
            "users": {"schema": UserRow, "data": self.users},
        }
        self.load("backend/db/tables.json")

    def load(self, filename: str):
        """Loads data from a JSON file to initiate the database"""
        with open(filename, encoding="utf-8") as file:
            raw_data = json.load(file)
        for table_name, table_data in raw_data.items():
            if table_name in self._tables:
                schema = self._tables[table_name]["schema"]
                for row in table_data:
                    self._tables[table_name]["data"].append(schema(**row))

    def scan(self, table: str):
        """Returns all rows in a table"""
        if table not in self._tables:
            raise KeyError(f"Table {table} does not exist")
        return self._tables[table]["data"]

    def get(self, table: str, id_: int):
        """Returns the first row in the table with the given id or None if not found"""
        if table not in self._tables:
            raise KeyError(f"Table {table} does not exist")
        return next((t for t in self._tables[table]["data"] if t.id == id_), None)

    def put(self, table: str, item: BaseModel):
        """Adds a new item to the table and returns it

        Note: the item's original `id` field is ignored and overwritten with the next available id"""
        if table not in self._tables:
            raise KeyError(f"Table {table} does not exist")
        schema = self._tables[table]["schema"]
        if not isinstance(item, schema):
            raise ValueError(f"Invalid item type {type(item)} for table {table}")
        id_ = len(self._tables[table]["data"]) + 1
        item.id = id_
        self._tables[table]["data"].append(item)
        return item
