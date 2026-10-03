from mmh3 import hash

from login_checher import LoginChecker

# default load factor for hash table
DEFAULT_HASHTABLE_LOAD_FACTOR = 0.75


class HashTable(LoginChecker):
    def __init__(
        self,
        items: list[str] | None = None,
        capacity: int = 8,
        load_factor: float = DEFAULT_HASHTABLE_LOAD_FACTOR,
    ) -> None:
        # initialize the hash table
        self._capacity = capacity
        self._buckets: list[list[str]] = [[] for _ in range(self._capacity)]
        self._size = 0
        self._load_factor = load_factor

        # initialize the hash table with keys
        for item in items or []:
            self.insert(item)

    # get the hash index for an item
    def _get_hash_index(self, item: str) -> int:
        return hash(item) % self._capacity

    # insert an item into the hash table
    # raise an error if the item already exists
    def insert(self, item: str) -> None:
        bucket = self._buckets[self._get_hash_index(item)]
        if item in bucket:
            raise ValueError(f"Item '{item}' already exists in the hash table.")

        bucket.append(item)
        self._size += 1
        # resize the hash table if the load factor threshold is exceeded
        if self._size / self._capacity > self._load_factor:
            self._resize()

    # delete an item from the hash table
    def delete(self, item: str) -> None:
        bucket = self._buckets[self._get_hash_index(item)]
        if item in bucket:
            bucket.remove(item)
            self._size -= 1

    # check if an item exists in the hash table
    def check(self, item: str) -> bool:
        return item in self._buckets[self._get_hash_index(item)]

    # resize the hash table by doubling its capacity, also rehash all items
    def _resize(self) -> None:
        old_items = [item for bucket in self._buckets for item in bucket]
        self._capacity *= 2
        self._buckets = [[] for _ in range(self._capacity)]

        # rehash all items into the new buckets
        for item in old_items:
            self._buckets[self._get_hash_index(item)].append(item)
