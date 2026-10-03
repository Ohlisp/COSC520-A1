from login_checher import LoginChecker


class BinarySearch(LoginChecker):
    # initialize the binary search with sorted list
    def __init__(self, items: list[str] | None = None) -> None:
        self.items = sorted(items) if items else []

    def insert(self, item: str) -> None:
        if not self.check(item):
            self.items.append(item)
            self.items.sort()
        else:
            raise ValueError(f"Item '{item}' already exists in the list.")

    def _find_idx(self, item: str) -> int:
        left, right = 0, len(self.items) - 1
        while left <= right:
            mid = (left + right) // 2
            if self.items[mid] == item:
                return mid
            elif self.items[mid] < item:
                left = mid + 1
            else:
                right = mid - 1
        return -1

    # delete an item from the list when it exists
    # reconstruct the list by shift the elements of the right of the deleted item to the left
    def delete(self, item: str) -> None:
        idx = self._find_idx(item)
        if idx == -1:
            return
        for pos in range(idx, len(self.items) - 1):
            self.items[pos] = self.items[pos + 1]
        # after shifting remove the last item as it is a dup
        self.items.pop()

    # check if an item exist in the list using binary search
    def check(self, item: str) -> bool:
        left, right = 0, len(self.items) - 1
        while left <= right:
            mid = (left + right) // 2
            if self.items[mid] == item:
                return True
            elif self.items[mid] < item:
                left = mid + 1
            else:
                right = mid - 1
        return False
