from abc import ABC, abstractmethod
from typing import Any, List, Union


class Command(ABC):
    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> Union[str, List[Any]]:
        pass
