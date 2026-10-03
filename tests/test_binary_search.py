from binary_search import BinarySearch


# simple test case for binary search for insert, check, and delete
def test_binary_search():
    search = BinarySearch(["a", "b", "c"])
    assert search.check("a")
    assert not search.check("d")
    assert not search.check("e")

    search.insert("d")
    assert search.check("d")

    search.delete("b")
    assert not search.check("b")