def integer_sqrt(n: int) -> int:
    """Обчислює floor(sqrt(n)) через двійковий пошук за відповіддю."""
    if n < 0:
        return -1
    if n == 0:
        return 0

    low = 1
    high = n
    ans = 1

    while low <= high:
        mid = low + (high - low) // 2
        
        # Перевірка монотонної умови mid^2 <= n
        if mid <= n // mid:
            ans = mid     # Фіксуємо поточну найкращу відповідь
            low = mid + 1 # Пробуємо знайти більше значення
        else:
            high = mid - 1

    return ans

if __name__ == "__main__":
    number = 50
    print(f"integer_sqrt({number}) = {integer_sqrt(number)}") # Поверне 7
