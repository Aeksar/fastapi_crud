from abc import ABC, abstractmethod


class BaseCrudRepository(ABC):
    @abstractmethod
    async def get(self): ...
    
    @abstractmethod
    async def get_list(self): ...

    @abstractmethod
    async def update(self): ...

    @abstractmethod
    async def delete(self): ...

    @abstractmethod
    async def create(self): ...

class BaseTaskRepository(BaseCrudRepository):
    ...