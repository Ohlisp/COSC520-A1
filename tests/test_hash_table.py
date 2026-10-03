import pytest

from hash_table import HashTable


# simple test case for insert, check, and delete
def test_hash_table_supports_insert_check_and_delete():
    table = HashTable(["a", "b", "c"])

    assert table.check("a")
    assert not table.check("d")

    table.insert("d")
    assert table.check("d")

    table.delete("b")
    assert not table.check("b")


# test case for inserting duplicate items
def test_hash_table_rejects_duplicate_items():
    table = HashTable(["a"])

    with pytest.raises(ValueError, match="Item 'a' already exists"):
        table.insert("a")

# test case for resizing the hash table capacity
def test_hash_table_resizes_and_preserves_items():
    table = HashTable(capacity=2, load_factor=0.75)

    table.insert("a")
    table.insert("b")

    assert table._capacity == 4
    assert table._size == 2
    assert table.check("a")
    assert table.check("b")

    for i in range(10):
        table.insert(f"item_{i}")

    assert table._capacity >= 12
    assert table._size == 12
    assert table.check("a")
    assert table.check("b")

# test case for handling multiple items in the same bucket
def test_hash_table_handles_hash_collisions():
    items = ["a", "b", "c", "string 1", "string 2", "string 3"]
    table = HashTable(capacity=1, load_factor=10)

    for item in items:
        table.insert(item)

    assert all(table._get_hash_index(item) == 0 for item in items)
    assert all(table.check(item) for item in items)

    table.delete("b")

    assert not table.check("b")
    assert table.check("a")
    assert table.check("string 1")
    assert table.check("string 2")
    assert table.check("string 3")
    