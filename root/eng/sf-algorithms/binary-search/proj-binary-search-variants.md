# ⚙️ Практичні варіації двійкового пошуку: lower_bound, upper_bound та пошук у повернутому масиві

Класичний двійковий пошук дає відповідь на питання: «Чи є елемент у масиві, і якщо є, то за яким індексом?». Проте в реальних інженерних задачах часто потрібні складніші варіації:
1. Знайти **перше входження** елемента, який більший або дорівнює `target` (`lower_bound`);
2. Знайти **перше входження** елемента, який строго більший за `target` (`upper_bound`);
3. Порахувати **кількість дублікатів** елемента за час O(log N);
4. Знайти елемент у масиві, який був **циклічно зсунутий (повернутий)** на невідомий зсув;
5. Обчислити значення неперервної або дискретної монотонної функції («двійковий пошук за відповіддю»).

Розглянемо практичні алгоритми та їх ідіоматичні реалізації.

## 1. Пошук меж: lower_bound та upper_bound

Коли масив містить однакові елементи (наприклад, `A = [1, 2, 2, 2, 3, 5]`), класичний двійковий пошук при виклику для `target = 2` може повернути індекс 2 (середину групи дублікатів). 

Щоб отримати точний інтервал усіх дублікатів `[first_idx, last_idx]`, використовують дві фундаментальні функції:

- **`lower_bound`**: Повертає індекс першого елемента, значення якого **≥ target**. Якщо всі елементи менші за `target`, повертає N (розмір масиву).
- **`upper_bound`**: Повертає індекс першого елемента, значення якого **> target**. Якщо таких немає, повертає N.

Кількість елементів, що дорівнюють `target`, обчислюється як різниця: `upper_bound(target) - lower_bound(target)`.

:::tabs
```cpp
#include <iostream>
#include <vector>

// lower_bound: повертає найменший індекс i такий, що arr[i] >= target
int lower_bound(const std::vector<int>& arr, int target) {
    int low = 0;
    int high = arr.size(); // Напіввідкритий інтервал [low, high)

    while (low < high) {
        int mid = low + (high - low) / 2;
        if (arr[mid] >= target) {
            high = mid; // Звужуємо праворуч, зберігаючи потенційний кандидат mid
        } else {
            low = mid + 1; // arr[mid] < target, тому шукаємо строго праворуч
        }
    }
    return low; // low вказує на перший елемент >= target
}

// upper_bound: повертає найменший індекс i такий, що arr[i] > target
int upper_bound(const std::vector<int>& arr, int target) {
    int low = 0;
    int high = arr.size(); // Напіввідкритий інтервал [low, high)

    while (low < high) {
        int mid = low + (high - low) / 2;
        if (arr[mid] > target) {
            high = mid; // Звужуємо праворуч
        } else {
            low = mid + 1; // arr[mid] <= target, продовжуємо пошук праворуч
        }
    }
    return low; // low вказує на перший елемент > target
}

int main() {
    std::vector<int> data = {1, 2, 2, 2, 3, 5, 8};
    int target = 2;

    int lb = lower_bound(data, target);
    int ub = upper_bound(data, target);

    std::cout << "lower_bound (>= 2): index " << lb << " (значення " << data[lb] << ")\n";
    std::cout << "upper_bound (> 2):  index " << ub << " (значення " << data[ub] << ")\n";
    std::cout << "Кількість елементів = " << (ub - lb) << "\n";

    return 0;
}
```
```python
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
```
:::

Зверніть увагу: у реалізації `lower_bound` та `upper_bound` використовується **напіввідкритий інтервал** `[low, high)`, де `high = N`. Завдяки цьому, якщо елемент відсутній і більший за всі значення в масиві, алгоритм безпомилково повертає `N` без виходу за межі пам'яті.

## 2. Пошук у циклічно зсунутому (повернутому) масиві

Уявіть впорядкований масив `[0, 1, 2, 4, 5, 6, 7]`, який повернули навколо декількох елементів, отримавши `[4, 5, 6, 7, 0, 1, 2]`. Потрібно знайти індекс `target` за той самий час **O(log N)**.

Ключова ідея: якщо ми розділимо повернутий масив навпіл елементом `mid`, то **принаймні одна з двох половин (або ліва `[low..mid]`, або права `[mid..high]`) гарантовано є строго впорядкованою**!

Алгоритм дій:
1. Знаходимо `mid`. Якщо `A[mid] == target`, повертаємо `mid`.
2. Перевіряємо, яка половина впорядкована:
   - Якщо `A[low] <= A[mid]`, то **ліва половина впорядкована**.
     - Перевіряємо, чи належить `target` діапазону `[A[low], A[mid])`. Якщо так — шукаємо в лівій половині (`high = mid - 1`), інакше — у правій (`low = mid + 1`).
   - Інакше **права половина впорядкована**.
     - Перевіряємо, чи належить `target` діапазону `(A[mid], A[high]]`. Якщо так — шукаємо в правій половині (`low = mid + 1`), інакше — у лівій (`high = mid - 1`).

:::tabs
```cpp
#include <iostream>
#include <vector>

int search_rotated(const std::vector<int>& arr, int target) {
    int low = 0;
    int high = arr.size() - 1;

    while (low <= high) {
        int mid = low + (high - low) / 2;

        if (arr[mid] == target) {
            return mid;
        }

        // Перевіряємо, чи впорядкована ліва частина
        if (arr[low] <= arr[mid]) {
            // target лежить у відсортованому лівому сегменті
            if (arr[low] <= target && target < arr[mid]) {
                high = mid - 1;
            } else {
                low = mid + 1;
            }
        } 
        // Інакше впорядкована права частина
        else {
            // target лежить у відсортованому правому сегменті
            if (arr[mid] < target && target <= arr[high]) {
                low = mid + 1;
            } else {
                high = mid - 1;
            }
        }
    }
    return -1; // Не знайдено
}

int main() {
    std::vector<int> rotated = {4, 5, 6, 7, 0, 1, 2};
    int target = 0;
    int idx = search_rotated(rotated, target);

    std::cout << "Елемент " << target << " знайдено на індексі: " << idx << "\n";
    return 0;
}
```
```python
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
```
:::

Складність цього алгоритму становить строго **O(log N)** за часом і **O(1)** за додатковою пам'яттю, оскільки на кожному кроці ми гарантовано відкидаємо половину пошукового простору.

## 3. Двійковий пошук за відповіддю (Binary Search on Answer)

Часто в олімпіадному та системному програмуванні зустрічається задача наступного типу:
*«Знайдіть мінімальне значення X, при якому функція-предикат `check(X)` повертає true»*.

Якщо предикат `check(X)` є **монотонним** (тобто вигляд значень `check(X)` при зростанні X має форму `[false, false, ..., false, true, true, ..., true]`), ми можемо виконати двійковий пошук безпосередньо у просторі можливих відповідей `[X_min, X_max]`.

**Приклад: Обчислення цілочисельного квадратного кореня `⌊√n⌋` без використання плаваючої коми.**

:::tabs
```cpp
#include <iostream>

long long integer_sqrt(long long n) {
    if (n < 0) return -1;
    if (n == 0) return 0;

    long long low = 1;
    long long high = n;
    long long ans = 1;

    while (low <= high) {
        long long mid = low + (high - low) / 2;

        // Щоб уникнути переповнення mid * mid, порівнюємо mid з n / mid
        if (mid <= n / mid) {
            ans = mid;     // mid є можливим кандидатів, шукаємо більше значення
            low = mid + 1;
        } else {
            high = mid - 1; // mid * mid > n, звужуємо зверху
        }
    }
    return ans;
}

int main() {
    long long number = 50;
    std::cout << "integer_sqrt(" << number << ") = " << integer_sqrt(number) << "\n"; // Поверне 7
    return 0;
}
```
```python
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
```
:::

У даному прикладі двійковий пошук за відповіддю обчислює квадратний корінь з числа 50 за 6 порівнянь, не використовуючи жодної операції з числами з рухомою комою (float/double), що робить його ідеальним для мікроконтролерів та ядер операційних систем.
