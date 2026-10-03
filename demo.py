# show insert, search, and delete operations for all five structures

from __future__ import annotations

from binary_search import BinarySearch
from bloom_filter import BloomFilter
from cuckoo_filter import CuckooFilter
from hash_table import HashTable
from linear_search import LinearSearch


ITEMS = [
    "alice",
    "bob",
    "carol",
    "dylan",
    "eve",
    "frank",
    "grace",
    "henry",
    "iris",
    "jack",
    "karen",
    "leo",
    "mia",
    "nina",
    "oliver",
    "paula",
    "quinn",
    "rachel",
    "sam",
    "tina",
    "victor",
]
NEW_ITEM = "dave"
REMOVED_ITEM = "bob"


def show_operations(name: str, structure: object) -> None:
    # run the common operations for one data structure
    insert = structure.insert  # type: ignore[attr-defined]
    check = structure.check  # type: ignore[attr-defined]
    delete = structure.delete  # type: ignore[attr-defined]
    print(f"\n{name}")
    print(f"  initial data: {ITEMS}")

    print(f"  search({REMOVED_ITEM!r}): {check(REMOVED_ITEM)}")

    if isinstance(structure, BloomFilter):
        print("  delete(...): not supported by this data structure")
    else:
        delete(REMOVED_ITEM)
        print(f"  delete({REMOVED_ITEM!r})")

    print(f"  search({REMOVED_ITEM!r}): {check(REMOVED_ITEM)}")
    print(f"  search({NEW_ITEM!r}): {check(NEW_ITEM)}")
    insert(NEW_ITEM)
    print(f"  insert({NEW_ITEM!r})")
    print(f"  search({NEW_ITEM!r}): {check(NEW_ITEM)}")


def main() -> None:
    # use the same operations for all five implementations
    structures = (
        ("linear search", LinearSearch(ITEMS)),
        ("binary search", BinarySearch(ITEMS)),
        ("hash table", HashTable(ITEMS)),
        ("bloom filter", BloomFilter(ITEMS, capacity=20)),
        ("cuckoo filter", CuckooFilter(ITEMS, capacity=20, seed=1)),
    )

    print("data structure operation demo")
    print("note: probabilistic filters may report false positives.")
    for name, structure in structures:
        show_operations(name, structure)


if __name__ == "__main__":
    main()
