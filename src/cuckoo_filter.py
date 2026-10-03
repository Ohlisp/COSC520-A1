import math
import random

from mmh3 import hash

from login_checher import LoginChecker

# defaullt parameters for cuckoo filter
DEFAULT_CUCKOO_CAPACITY = 100
DEFAULT_FINGERPRINT_SIZE = 16
DEFAULT_MAX_KICKS = 500
# use a max load factor of 95% with 4 fingerprints per bucket
DEFAULT_BUCKET_SIZE = 4
DEFAULT_LOAD_FACTOR = 0.95


# a space-efficient probabilistic set using cuckoo filter
# cuckoo filter may return false positives
# cuckoo filter support native deletion

class CuckooFilter(LoginChecker):

    # capacity is the expected stored fingerprints in the filter
    # bucket_size is the number of fingerprints stored in each bucket
    # fingerprint_size is the number of bits used for each fingerprint
    # max_kicks is the maximum number of times to kick out an existing fingerprint
    # which prevents infinite loops
    # load_factor is the maximum load factor before resizing the filter

    
    def __init__(
        self,
        items: list[str] | None = None,
        capacity: int = DEFAULT_CUCKOO_CAPACITY,
        bucket_size: int = DEFAULT_BUCKET_SIZE,
        fingerprint_size: int = DEFAULT_FINGERPRINT_SIZE,
        max_kicks: int = DEFAULT_MAX_KICKS,
        load_factor: float = DEFAULT_LOAD_FACTOR,
        seed: int | None = None,
    ) -> None:
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        if bucket_size < 1:
            raise ValueError("bucket_size must be at least 1")
        if fingerprint_size < 1:
            raise ValueError("fingerprint_size must be at least 1")
        if max_kicks < 1:
            raise ValueError("max_kicks must be at least 1")
        if not 0 < load_factor <= 1:
            raise ValueError("load_factor must be greater than 0 and at most 1")

        self.capacity = capacity
        self.bucket_size = bucket_size
        self.fingerprint_size = fingerprint_size
        self.max_kicks = max_kicks
        self.load_factor = load_factor
        self._size = 0
       
        self._random = random.Random(seed)

        # as load factor = total items / (total buckets * bucket size)
        required_buckets = math.ceil(
            capacity / (bucket_size * load_factor)
        )
        # round up to the next power of 2
        # number of buckets = nextpowerof2(required_buckets)
        self._bucket_count = 1 << (required_buckets - 1).bit_length()
        self._buckets: list[list[int]] = [
            [] for _ in range(self._bucket_count)
        ]

        for item in items or []:
            self.insert(item)

    # get the fingerprint of an 
    # fingerprint(x) 
    def _fingerprint(self, item: str) -> int:
        # for example, if fingerprint_size is 16, then mask = 0xFFFF
        mask = (1 << self.fingerprint_size) - 1
        # for example, if a hash is 0x12345678, then fingerprint = 0x5678, which keeps the last 16 bits of the hash
        fingerprint = hash(item, 1, signed=False) & mask
        return fingerprint or 1

    # h1(x) = hash(x) 
    def _index(self, item: str) -> int:
        return hash(item, 0, signed=False) & (self._bucket_count - 1)

    # h2(x) = h1(x) XOR hash(fingerprint(x))
    def _alternate_index(self, index: int, fingerprint: int) -> int:
        fingerprint_hash = hash(str(fingerprint), 2, signed=False)
        return (index ^ fingerprint_hash) & (self._bucket_count - 1)

    def _candidate_buckets(self, item: str) -> tuple[int, int, int]:
        fingerprint = self._fingerprint(item)
        first = self._index(item)
        second = self._alternate_index(first, fingerprint)
        return first, second, fingerprint

    def insert(self, item: str) -> None:
        first, second, fingerprint = self._candidate_buckets(item)
        for index in (first, second):
            if len(self._buckets[index]) < self.bucket_size:
                self._buckets[index].append(fingerprint)
                self._size += 1
                return

        current_fingerprint = fingerprint
        # relocate exising fingerprints
        current_index = self._random.choice((first, second))
        swaps: list[tuple[int, int, int]] = []

        for _ in range(self.max_kicks):
            # randomly select a slot in the current bucket to kick out
            slot = self._random.randrange(self.bucket_size)
            bucket = self._buckets[current_index]
            displaced = bucket[slot]
            #swap the fingerprints
            swaps.append((current_index, slot, displaced))
            bucket[slot] = current_fingerprint
            current_fingerprint = displaced
            current_index = self._alternate_index(
                current_index, current_fingerprint
            )
            #if the new bucket has space, insert the fingerprint and retur
            if len(self._buckets[current_index]) < self.bucket_size:
                self._buckets[current_index].append(current_fingerprint)
                self._size += 1
                return

        for index, slot, displaced in reversed(swaps):
            current_fingerprint = self._buckets[index][slot]
            self._buckets[index][slot] = displaced

        raise OverflowError(
            "Cuckoo filter is full; increase capacity or max_kicks."
        )

    def delete(self, item: str) -> None:
        first, second, fingerprint = self._candidate_buckets(item)
        for index in (first, second):
            bucket = self._buckets[index]
            if fingerprint in bucket:
                bucket.remove(fingerprint)
                self._size -= 1
                return

    # Check if an item is in the cuckoo filter.
    def check(self, item: str) -> bool:
        first, second, fingerprint = self._candidate_buckets(item)
        return (
            fingerprint in self._buckets[first]
            or fingerprint in self._buckets[second]
        )
