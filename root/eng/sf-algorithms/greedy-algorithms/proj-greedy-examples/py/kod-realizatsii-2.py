from typing import List, Tuple

def min_coins_greedy(amount: int, denominations: List[int]) -> List[Tuple[int, int]]:
    """
    Видає суму amount мінімальною кількістю монет у канонічній системі.
    Повертає список пар (номінал, кількість).
    """
    if amount <= 0 or not denominations:
        return []

    # Крок 1: Сортування номіналів у порядку спадання
    sorted_coins = sorted(denominations, reverse=True)

    result = []
    current_amount = amount

    # Крок 2: Жадібний вибір найбільш можливої монети
    for coin in sorted_coins:
        if current_amount == 0:
            break
        if coin <= current_amount:
            count = current_amount // coin
            current_amount %= coin
            result.append((coin, count))

    # Перевірка на нерозмінний залишок
    if current_amount > 0:
        return []

    return result


if __name__ == "__main__":
    coins_list = [1, 2, 5, 10, 20, 50, 100, 200, 500]
    target = 878

    change_plan = min_coins_greedy(target, coins_list)

    print(f"Розмін суми {target}:")
    total_count = 0
    for coin, count in change_plan:
        print(f"  Монета {coin} грн: {count} шт.")
        total_count += count
    print(f"Загальна кількість монет: {total_count}")
