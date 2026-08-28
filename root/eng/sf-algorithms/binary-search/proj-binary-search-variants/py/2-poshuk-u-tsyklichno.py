def search_rotated(arr: list[int], target: int) -> int:
    """Пошук елемента в циклічно зсунутому впорядкованому масиві за O(log N)."""
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = low + (high - low) // 2

        if arr[mid] == target:
            return mid

        # Перевіряємо, чи ліва половина є монотонно зростаючою
        if arr[low] <= arr[mid]:
            if arr[low] <= target < arr[mid]:
                high = mid - 1  # Шукаємо у монотонній лівій частині
            else:
                low = mid + 1   # Переходимо в праву частину
        # Інакше монотонною є права половина
        else:
            if arr[mid] < target <= arr[high]:
                low = mid + 1   # Шукаємо у монотонній правій частині
            else:
                high = mid - 1  # Переходимо в ліву частину

    return -1

if __name__ == "__main__":
    rotated = [4, 5, 6, 7, 0, 1, 2]
    target = 0
    idx = search_rotated(rotated, target)
    print(f"Елемент {target} знайдено на індексі: {idx}")
