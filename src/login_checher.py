from abc import ABC, abstractmethod
class LoginChecker:

    @abstractmethod
    def __init__(self, items: list[str] | None = None) -> None:
        pass

    # interface for insert an item into loginchecker
    @abstractmethod
    def insert(self, item: str) -> None:
        raise NotImplementedError
    
    # interface for delete an item in loginchecker, optional as bloom filter does not support delete
    def delete(self, item: str) -> None:
        pass

    # interface for search an item in loginchecker
    @abstractmethod 
    def check(self, item: str) -> bool:
        raise NotImplementedError
    


