# ⚙️ Практичні приклади жадібних алгоритмів: інтервальне планування та розмін монет

Жадібні алгоритми вирізняються високою швидкодією та простотою реалізації. У цій практичній вставці розглядаються два класичні алгоритми: **інтервальне планування** (вибір максимальної кількості несумісних подій) та **розмін монет у канонічній грошовій системі**.

Для обох задач наведено ідіоматичний код мовами **C++** та **Python**.

---

## 1. Інтервальне планування (Interval Scheduling)

### Постановка задачі
Дано n інтервалів (подій або задач), кожен з яких описується часом початку sᵢ та часом закінчення fᵢ (sᵢ < fᵢ). Два інтервали сумісні, якщо вони не перетинаються в часі (тобто sⱼ ≥ fᵢ або sᵢ ≥ fⱼ). 

**Мета:** Знайти підмножину максимального розміру, що складається з взаємно сумісних інтервалів.

### Жадібний алгоритм
1. Відсортувати всі інтервали за зростанням часу їхнього закінчення fᵢ.
2. Обрати перший інтервал у відсортованому списку.
3. Проходити по решті інтервалів і обирати наступний інтервал лише тоді, коли його час початку sₖ не менший за час закінчення останнього обраного інтервалу.

### Складність
- **За часом:** O(n log n) через сортування інтервалів. Сам жадібний прохід виконується за O(n).
- **За пам'яттю:** O(n) для збереження результату (або O(1) додаткової пам'яті при модифікації масиву in-place).

### Код реалізації

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <algorithm>

// Структура для представлення інтервалу події
struct Interval {
    int id;
    int start;
    int finish;
};

// Функція розв'язання задачі інтервального планування
std::vector<Interval> scheduleIntervals(std::vector<Interval>& intervals) {
    if (intervals.empty()) {
        return {};
    }

    // Крок 1: Жадібне сортування за часом закінчення finish
    std::sort(intervals.begin(), intervals.end(), [](const Interval& a, const Interval& b) {
        if (a.finish != b.finish) {
            return a.finish < b.finish;
        }
        return a.start < b.start;
    });

    std::vector<Interval> result;
    // Крок 2: Обираємо перший інтервал з найранішим фінішем
    result.push_back(intervals[0]);
    int lastFinish = intervals[0].finish;

    // Крок 3: Жадібне фільтрування решти інтервалів
    for (size_t i = 1; i < intervals.size(); ++i) {
        if (intervals[i].start >= lastFinish) {
            result.push_back(intervals[i]);
            lastFinish = intervals[i].finish;
        }
    }

    return result;
}

int main() {
    std::vector<Interval> intervals = {
        {1, 0, 3},
        {2, 1, 4},
        {3, 2, 6},
        {4, 3, 7},
        {5, 5, 8},
        {6, 7, 10}
    };

    std::vector<Interval> scheduled = scheduleIntervals(intervals);

    std::cout << "Обрано інтервалів: " << scheduled.size() << "\n";
    for (const auto& item : scheduled) {
        std::cout << "Подія " << item.id << ": [" << item.start << ", " << item.finish << "]\n";
    }

    return 0;
}
```
```py
from typing import List, Dict, Any

def schedule_intervals(intervals: List[Dict[str, int]]) -> List[Dict[str, int]]:
    """
    Знаходить максимальну кількість сумісних інтервалів.
    Кожен інтервал є словником {'id': int, 'start': int, 'finish': int}.
    """
    if not intervals:
        return []

    # Крок 1: Сортування за часом закінчення finish
    sorted_intervals = sorted(intervals, key=lambda x: (x['finish'], x['start']))

    result = []
    # Крок 2: Обираємо перший інтервал
    result.append(sorted_intervals[0])
    last_finish = sorted_intervals[0]['finish']

    # Крок 3: Жадібний вибір наступних сумісних інтервалів
    for interval in sorted_intervals[1:]:
        if interval['start'] >= last_finish:
            result.append(interval)
            last_finish = interval['finish']

    return result


if __name__ == "__main__":
    test_intervals = [
        {'id': 1, 'start': 0, 'finish': 3},
        {'id': 2, 'start': 1, 'finish': 4},
        {'id': 3, 'start': 2, 'finish': 6},
        {'id': 4, 'start': 3, 'finish': 7},
        {'id': 5, 'start': 5, 'finish': 8},
        {'id': 6, 'start': 7, 'finish': 10}
    ]

    selected = schedule_intervals(test_intervals)
    print(f"Обрано інтервалів: {len(selected)}")
    for item in selected:
        print(f"Подія {item['id']}: [{item['start']}, {item['finish']}]")
```
:::

---

## 2. Розмін монет у канонічній системі (Coin Change Problem)

### Постановка задачі
Дано цільову суму грошей N та доступні номінали монет C = {c₁, c₂, ..., cₖ}. Необхідно видати суму N за допомогою мінімальної сумарної кількості монет.

Припускаємо, що система монет є **канонічною** (наприклад, стандартні банкноти та монети євро або гривні: {1, 2, 5, 10, 20, 50, 100, 200, 500}), для якої жадібний вибір гарантує точний оптимум.

### Жадібний алгоритм
1. Впорядкувати номінали монет за спаданням.
2. Для кожного номіналу взяти максимально можливу кількість монет ⌊ залишок / cᵢ ⌋.
3. Зменшити залишок суми на взяті монети і перейти до наступного номіналу.

### Складність
- **За часом:** O(k log k) для сортування номіналів. При відсортованому масиві з k номіналів розвідання суми займає O(k) операцій.
- **За пам'яттю:** O(k) для збереження підсумкового набору монет.

### Код реалізації

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <algorithm>

struct CoinCount {
    int denomination;
    int count;
};

// Функція жадібного розміну суми amount
std::vector<CoinCount> minCoinsGreedy(int amount, std::vector<int>& coins) {
    if (amount <= 0 || coins.empty()) {
        return {};
    }

    // Крок 1: Сортування номіналів за спаданням
    std::sort(coins.rbegin(), coins.rend());

    std::vector<CoinCount> result;
    int currentAmount = amount;

    // Крок 2: Жадібний вибір найбільшого номіналу
    for (int coin : coins) {
        if (currentAmount == 0) {
            break;
        }
        if (coin <= currentAmount) {
            int count = currentAmount / coin;
            currentAmount %= coin;
            result.push_back({coin, count});
        }
    }

    // Якщо залишилася невидана решта — система не дає розшити суму цілком
    if (currentAmount > 0) {
        return {}; // Неможливо видати точну суму
    }

    return result;
}

int main() {
    std::vector<int> denominations = {1, 2, 5, 10, 20, 50, 100, 200, 500};
    int targetAmount = 878;

    std::vector<CoinCount> change = minCoinsGreedy(targetAmount, denominations);

    std::cout << "Розмін суми " << targetAmount << ":\n";
    int totalCoins = 0;
    for (const auto& item : change) {
        std::cout << "  Монета " << item.denomination << " грн: " << item.count << " шт.\n";
        totalCoins += item.count;
    }
    std::cout << "Загальна кількість монет: " << totalCoins << "\n";

    return 0;
}
```
```py
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
```
:::

---

## 3. Крайові випадки та обробка помилок

Під час розробки виробничого коду жадібних алгоритмів важливо враховувати наступні крайові ситуації:

1. **Порожній вхідний масив:** Алгоритм має коректно повертати порожній результат або 0 без викидання винятків переповнення пам'яті (`IndexOutOfBoundsException`).
2. **Негативні або нульові значення:** У задачі інтервалів невалідна тривалість (sᵢ ≥ fᵢ) повинна відфільтровуватися на етапі валідації входів.
3. **Неканонічні системи монет:** У неканонічних системах (наприклад, {1, 3, 4} при розміні 6) жадібний алгоритм поверне {4, 1, 1} (3 монети) замість оптимуму {3, 3} (2 монети). Якщо гарантії канонічності немає, код повинен вмикати перевірку динамічним програмуванням.
