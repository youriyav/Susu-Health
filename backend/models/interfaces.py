from abc import ABC, abstractmethod
from typing import Any, List, Optional


class Database(ABC):
    @abstractmethod
    def scan(self, table: str) -> List[Any]:
        pass

    @abstractmethod
    def get(self, table: str, id_: int) -> Optional[Any]:
        pass

    @abstractmethod
    def put(self, table: str, item: Any) -> None:
        pass
