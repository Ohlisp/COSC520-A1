import pytest

from cuckoo_filter import CuckooFilter


def test_cuckoo_filter_supports_insert_check_and_delete():
    cuckoo_filter = CuckooFilter(capacity=4, seed=520)

    cuckoo_filter.insert("alice")
    cuckoo_filter.insert("bob")

    assert cuckoo_filter.check("alice")
    assert cuckoo_filter.check("bob")
    assert not cuckoo_filter.check("charlie")

    cuckoo_filter.delete("alice")
    assert not cuckoo_filter.check("alice")
    assert cuckoo_filter.check("bob")


def test_cuckoo_filter_loads_initial_items():
    cuckoo_filter = CuckooFilter(["a", "b"], capacity=2)

    assert cuckoo_filter.check("a")
    assert cuckoo_filter.check("b")


def test_cuckoo_filter_allows_duplicate_fingerprints():
    cuckoo_filter = CuckooFilter(capacity=2)
    cuckoo_filter.insert("alice")
    cuckoo_filter.insert("alice")

    cuckoo_filter.delete("alice")
    assert cuckoo_filter.check("alice")


def test_cuckoo_filter_rejects_invalid_configuration():
    with pytest.raises(ValueError, match="bucket_size"):
        CuckooFilter(bucket_size=0)

    with pytest.raises(ValueError, match="load_factor"):
        CuckooFilter(load_factor=0)


def test_cuckoo_filter_reports_full_capacity():
    cuckoo_filter = CuckooFilter(
        capacity=1, bucket_size=1, max_kicks=1, load_factor=1, seed=520
    )
    cuckoo_filter.insert("a")

    with pytest.raises(OverflowError, match="full"):
        cuckoo_filter.insert("b")