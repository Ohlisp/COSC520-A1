from login_checher import LoginChecker


class LinearSearch(LoginChecker):
    # initialize the linear search with a list
    def __init__(self, items: list[str] | None = None) -> None:
        self.items = items.copy() if items else []

    # insert an item into the list when it does not exist, otherwise raise an error
    def insert(self, item: str) -> None:
        if not self.check(item):
            self.items.append(item)
        else:
            raise ValueError(f"Item '{item}' already exists in the list.")

    # delete an item from the list when it exists
    def delete(self, item: str) -> None:
        if self.check(item):
            self.items.remove(item)

    # check if an item exist in the list
    def check(self, item: str) -> bool:
        return item in self.items
