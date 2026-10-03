from linear_search import LinearSearch


# simple test case for linear search for insert, check, and delete
def test_linear_search():
	search = LinearSearch(["a", "b", "c"])

	assert search.check("a")
	assert not search.check("d")
	assert not search.check("e")

	search.insert("d")
	assert search.check("d")

	search.delete("b")
	assert not search.check("b")
