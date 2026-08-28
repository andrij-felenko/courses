def ncr_multiplicative(n: int, k: int) -> int:
    """Обчислення C(n, k) за допомогою мультиплікативної формули.
    У Python цілі числа мають необмежену розрядність, тому переповнення неможливе.
    Складність за часом: O(k), додаткова пам'ять: O(1).
    """
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    
    # Використовуємо симетрію C(n, k) = C(n, n - k) для мінімізації ітерацій
    if k > n - k:
        k = n - k
        
    res = 1
    for i in range(1, k + 1):
        res = res * (n - k + i) // i
    return res
