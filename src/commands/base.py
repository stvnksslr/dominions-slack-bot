from abc import ABC, abstractmethod
from typing import Any, List


class Command(ABC):
    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> str:
        pass
