from mmh3 import hash
import math
from bitarray import bitarray
from login_checher import LoginChecker

DEFAULT_FALSE_POSITIVE_PROBABILITY = 0.01

# delete method is not implemented as it is not supported, which might cause
# deletion of other items
class BloomFilter(LoginChecker):
    def __init__(
        self,
        items: list[str] | None = None,
        false_positive_probability: float = DEFAULT_FALSE_POSITIVE_PROBABILITY,
        # item expected to be stored, used to calculate the optimal bit array size
        capacity = None
    ) -> None:

        # false positive probability in decimal
        self.false_positive_probability = false_positive_probability

        # size of bit array to use
        capacity = capacity if capacity else len(items) if items else 1
        self.size = self._get_size(capacity, false_positive_probability)

        # number of hash functions to use
        self.hash_count = self._get_hash_count(self.size, capacity)

        # bitarray to store the bits
        # initialize all bits to 0
        self.bit_array = bitarray(self.size)
        self.bit_array.setall(0)

        for item in items or []:
            self.insert(item)

    # add an item in the bloom filter
    def insert(self, item: str) -> None:
        for i in range(self.hash_count):
            # create a hash/digest of the item using the ith hash function
            # digest is created differently for each i
            digest = hash(item, i) % self.size
            # set the bit at the index of the hash to 1
            self.bit_array[digest] = True

    # check for existence of an item in the bloom filter
    # returns False if the item is definitely not in the filter
    # returns True if the item might be in the filter, have a false positive probability
    def check(self, item: str) -> bool:
        for i in range(self.hash_count):
            digest = hash(item, i) % self.size
            if not self.bit_array[digest]:
                return False
        return True
    

    # calculate the optimal size of bit array(m) using this formula:
    # m = -(n * ln(p)) / (ln(2)^2)
    # n is the number of items expected to be stored
    # p is the false positive probability in decimal
    def _get_size(self, n, p) -> int:
        return int(-(n * math.log(p)) / (math.log(2) ** 2))

    # calculate the optimal number of hash functions(k) using this formula:
    # k = (m/n) * ln(2)
    # m is the size of bit array
    # n is the number of items expected to be stored
    def _get_hash_count(self, m, n) -> int:
        return int((m / n) * math.log(2))