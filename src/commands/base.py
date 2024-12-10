from abc import ABC, abstractmethod
from typing import Any


class Command(ABC):
    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> str | list[Any]:  # noqa: ANN401
        pass
