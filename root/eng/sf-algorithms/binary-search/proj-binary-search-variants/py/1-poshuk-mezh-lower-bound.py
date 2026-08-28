def lower_bound(arr: list[int], target: int) -> int:
    """Повертає найменший індекс i такий, що arr[i] >= target."""
    low = 0
    high = len(arr)  # Напіввідкритий інтервал [low, high)
    
    while low < high:
        mid = low + (high - low) // 2
        if arr[mid] >= target:
            high = mid  # Кандидат знайдено, перевіряємо лівішу частину
        else:
            low = mid + 1
            
    return low

def upper_bound(arr: list[int], target: int) -> int:
    """Повертає найменший індекс i такий, що arr[i] > target."""
    low = 0
    high = len(arr)  # Напіввідкритий інтервал [low, high)
    
    while low < high:
        mid = low + (high - low) // 2
        if arr[mid] > target:
            high = mid
        else:
            low = mid + 1
            
    return low

# Демонстрація використання
if __name__ == "__main__":
    data = [1, 2, 2, 2, 3, 5, 8]
    target = 2
    
    lb = lower_bound(data, target)
    ub = upper_bound(data, target)
    
    print(f"lower_bound (>= 2): index {lb} (значення {data[lb]})")
    print(f"upper_bound (> 2):  index {ub} (значення {data[ub]})")
    print(f"Кількість елементів: {ub - lb}")
