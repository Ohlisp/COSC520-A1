from bloom_filter import BloomFilter


# test case for inserting and checking items in the bloom filter
def test_bloom_filter_supports_insert_and_check():
    bloom_filter = BloomFilter(capacity=3)

    bloom_filter.insert("alice")
    bloom_filter.insert("bob")

    assert bloom_filter.check("alice")
    assert bloom_filter.check("bob")
    assert not bloom_filter.check("charlie")


# test case for initializing bloom with loaded list
def test_bloom_filter_loads_initial_items():
    bloom_filter = BloomFilter(["a", "b"])

    assert bloom_filter.check("a")
    assert bloom_filter.check("b")
    assert not bloom_filter.check("c")


# test case for try to inserting duplicate items in the bloom filter
def test_bloom_filter_duplicate_insert_keeps_item_present():
    bloom_filter = BloomFilter(capacity=2)

    bloom_filter.insert("alice")
    bloom_filter.insert("alice")

    assert bloom_filter.check("alice")


# test case for checking an item that was definitely not added to the bloom filter
# we have a chance of false positive, but we can be sure that the item is not present if the check returns False
def test_bloom_filter_reports_a_definitely_missing_item():
    items = [f"user-{index}" for index in range(1_000)]
    bloom_filter = BloomFilter(items)

    assert not bloom_filter.check("user-that-was-not-added")
