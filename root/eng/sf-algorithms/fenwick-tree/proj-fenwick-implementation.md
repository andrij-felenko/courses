# ⚙️ Реалізація дерева Фенвіка: точкові, інтервальні та двовимірні структури

У цій практичній вставка представлено вихідний код реалізації дерева Фенвіка (Binary Indexed Tree / BIT) мовами C та C++. Подано варіанти для одновимірного точкового оновлення, двовимірного прямокутного підсумовування, інтервальних модифікацій через двохмасивний розклад та алгоритм двійкового підйому (Binary Lifting) для пошуку елемента за накопиченою сумою. Кожна реалізація супроводжується детальним розбором інженерних та архітектурних рішень, обробки крайових умов, оптимізацій пам'яті та локальності кешу.

### 1. Одновимірне дерево Фенвіка (1D Fenwick Tree)

Класична одновимірна структура даних інкапсулює динамічний масив `tree_` розміром `N + 1`. Математична модель дерева Фенвіка вимагає 1-індексації елементів (`1 ≤ i ≤ N`), де індекс `0` відповідає порожньому префіксу. Щоб створити зручний та безаварійний інтерфейс для розробників, клас-обгортка автоматично транслює зовнішню 0-індексацію (`0 ≤ idx < N`) у внутрішню 1-індексацію (`i = idx + 1`).

#### Принцип роботи точкового оновлення add()

Коли користувач викликає метод `add(idx, val)`, алгоритм додає значення `val` до елемента `A[idx]` та оновлює всі покриваючі вузли `tree_[i]`. Початковий 1-індекс обчислюється як `i = idx + 1`. На кожному кроці циклу значення `tree_[i]` збільшується на `val`, після чого здійснюється перехід до наступного батьківського вузла за формулою `i += i & (-i)`. Процес продовжується, доки індекс `i` не перевищить загальну кількість елементів `N`. Завдяки побітовим операціям кількість ітерацій циклу не перевищує `log_2(N)`.

#### Принцип роботи префіксного запиту query_prefix()

Метод `query_prefix(idx)` обчислює накопичувальну суму елементів масиву від `A[0]` до `A[idx]` включно. Для цього обхід починається з позиції `i = idx + 1`. Змінна-акумулятор `sum` накопичує значення `tree_[i]`, після чого індекс `i` зменшується на наймолодший встановлений біт `i -= i & (-i)`. Цикл зупиняється, коли `i` стає рівним `0`. Кількість доданок у сумі строго дорівнює кількості одиничних бітів у двійковому записі індексу `idx + 1`.

#### Запит суми на довільному відрізку query_range()

Обчислення суми елементів на довільному закритому інтервалі `[left, right]` спирається на двоїсту властивість префіксних сум. Якщо `left == 0`, метод напряму повертає `query_prefix(right)`. Якщо ж `left > 0`, формула `query_prefix(right) - query_prefix(left - 1)` скорочує спільний лівий префікс `A[0..left-1]`, залишаючи лише суму шуканого відрізка `A[left..right]`.

#### Особливості побудови за лінійний час O(N)

Замість виконання `N` точкових додавань `add()`, кожне з яких займає `O(log N)` часу (що сумарно дає `O(N log N)`), у конструкторі реалізовано алгоритм лінійної побудови за `O(N)`. Ідея полягає в тому, що після скопіювання вихідних елементів у масив `tree_`, кожен вузол `i` передає своє накопичене значення безпосередньому батьківському вузлу `parent = i + LSB(i)`. Оскільки кожен вузол обробляється рівно один раз послідовно від `i = 1` до `N`, усі суми піднімаються вгору по дереву за один лінійний прохід.

:::tabs
```cpp
#include <vector>
#include <cstddef>
#include <stdexcept>

template <typename T = long long>
class FenwickTree {
private:
    std::size_t n_;
    std::vector<T> tree_;

    static constexpr std::size_t lsb(std::size_t i) noexcept {
        return i & (-i);
    }

public:
    explicit FenwickTree(std::size_t size)
        : n_(size), tree_(size + 1, T{0}) {}

    // Ініціалізація за O(N) з вихідного вектора
    explicit FenwickTree(const std::vector<T>& data)
        : n_(data.size()), tree_(data.size() + 1, T{0}) {
        for (std::size_t i = 0; i < n_; ++i) {
            tree_[i + 1] += data[i];
            std::size_t parent = (i + 1) + lsb(i + 1);
            if (parent <= n_) {
                tree_[parent] += tree_[i + 1];
            }
        }
    }

    // Точкове додавання значення v до елемента за індексом idx (0-based)
    void add(std::size_t idx, T val) {
        if (idx >= n_) {
            throw std::out_of_range("Індекс виходить за межі дерева Фенвіка");
        }
        for (std::size_t i = idx + 1; i <= n_; i += lsb(i)) {
            tree_[i] += val;
        }
    }

    // Префіксна сума від елемента 0 до idx включно (0-based)
    [[nodiscard]] T query_prefix(std::size_t idx) const {
        if (idx >= n_) {
            throw std::out_of_range("Індекс виходить за межі дерева Фенвіка");
        }
        T sum = T{0};
        for (std::size_t i = idx + 1; i > 0; i -= lsb(i)) {
            sum += tree_[i];
        }
        return sum;
    }

    // Запит суми на відрізку [left, right] включно (0-based)
    [[nodiscard]] T query_range(std::size_t left, std::size_t right) const {
        if (left > right || right >= n_) {
            throw std::out_of_range("Некоректні межі відрізка запиту");
        }
        if (left == 0) {
            return query_prefix(right);
        }
        return query_prefix(right) - query_prefix(left - 1);
    }

    [[nodiscard]] std::size_t size() const noexcept {
        return n_;
    }
};
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    size_t size;
    long long* tree;
} fenwick_tree_t;

static inline size_t fenwick_lsb(size_t i) {
    return i & (-i);
}

fenwick_tree_t* fenwick_create(size_t size) {
    fenwick_tree_t* ft = (fenwick_tree_t*)malloc(sizeof(fenwick_tree_t));
    if (!ft) return NULL;
    ft->size = size;
    ft->tree = (long long*)calloc(size + 1, sizeof(long long));
    if (!ft->tree) {
        free(ft);
        return NULL;
    }
    return ft;
}

void fenwick_destroy(fenwick_tree_t* ft) {
    if (ft) {
        free(ft->tree);
        free(ft);
    }
}

// Лінійна побудова за O(N)
fenwick_tree_t* fenwick_create_from_array(const long long* data, size_t size) {
    fenwick_tree_t* ft = fenwick_create(size);
    if (!ft) return NULL;

    for (size_t i = 0; i < size; ++i) {
        ft->tree[i + 1] += data[i];
        size_t parent = (i + 1) + fenwick_lsb(i + 1);
        if (parent <= size) {
            ft->tree[parent] += ft->tree[i + 1];
        }
    }
    return ft;
}

bool fenwick_add(fenwick_tree_t* ft, size_t idx, long long val) {
    if (!ft || idx >= ft->size) return false;
    for (size_t i = idx + 1; i <= ft->size; i += fenwick_lsb(i)) {
        ft->tree[i] += val;
    }
    return true;
}

long long fenwick_query_prefix(const fenwick_tree_t* ft, size_t idx) {
    if (!ft || idx >= ft->size) return 0;
    long long sum = 0;
    for (size_t i = idx + 1; i > 0; i -= fenwick_lsb(i)) {
        sum += ft->tree[i];
    }
    return sum;
}

long long fenwick_query_range(const fenwick_tree_t* ft, size_t left, size_t right) {
    if (!ft || left > right || right >= ft->size) return 0;
    if (left == 0) {
        return fenwick_query_prefix(ft, right);
    }
    return fenwick_query_prefix(ft, right) - fenwick_query_prefix(ft, left - 1);
}
```
:::

---

### 2. Двовимірне дерево Фенвіка (2D Fenwick Tree)

Двовимірне дерево Фенвіка слугує для оновлення окремих комірок прямокутної матриці та обчислення сум у довільних прямокутних підобластях. Замість використання складних 2D дерев відрізків із динамічними вузлами, 2D BIT будується на плоскому або вкладеному масиві розміром `(rows + 1) × (cols + 1)`.

#### Логіка виконання двовимірних операцій

- **Точкове оновлення `add(r, c, val)`:** запускає два вкладені цикли. Зовнішній цикл піднімається по рядках `i += LSB(i)`, а внутрішній — по стовпцях `j += LSB(j)`. Сумарно оновлюється не більше ніж `log_2(rows) · log_2(cols)` комірок.
- **Запит суми прямокутника `query_rect(r1, c1, r2, c2)`:** обчислює суму за принципом включень-виключень. Спочатку обчислюється префіксна сума великого прямокутника від `(0,0)` до `(r2, c2)`, після чого віднімаються дві перекриваючі смуги `(0,0)..(r1-1, c2)` та `(0,0)..(r2, c1-1)`, а перетин `(0,0)..(r1-1, c1-1)` додається назад.

:::tabs
```cpp
#include <vector>
#include <cstddef>
#include <stdexcept>

template <typename T = long long>
class FenwickTree2D {
private:
    std::size_t rows_;
    std::size_t cols_;
    std::vector<std::vector<T>> tree_;

    static constexpr std::size_t lsb(std::size_t i) noexcept {
        return i & (-i);
    }

public:
    FenwickTree2D(std::size_t rows, std::size_t cols)
        : rows_(rows), cols_(cols),
          tree_(rows + 1, std::vector<T>(cols + 1, T{0})) {}

    void add(std::size_t r, std::size_t c, T val) {
        if (r >= rows_ || c >= cols_) {
            throw std::out_of_range("Некоректні індекси 2D дерева Фенвіка");
        }
        for (std::size_t i = r + 1; i <= rows_; i += lsb(i)) {
            for (std::size_t j = c + 1; j <= cols_; j += lsb(j)) {
                tree_[i][j] += val;
            }
        }
    }

    [[nodiscard]] T query_prefix(std::size_t r, std::size_t c) const {
        if (r >= rows_ || c >= cols_) {
            throw std::out_of_range("Некоректні індекси 2D дерева Фенвіка");
        }
        T sum = T{0};
        for (std::size_t i = r + 1; i > 0; i -= lsb(i)) {
            for (std::size_t j = c + 1; j > 0; j -= lsb(j)) {
                sum += tree_[i][j];
            }
        }
        return sum;
    }

    [[nodiscard]] T query_rect(std::size_t r1, std::size_t c1, std::size_t r2, std::size_t c2) const {
        if (r1 > r2 || c1 > c2 || r2 >= rows_ || c2 >= cols_) {
            throw std::out_of_range("Некоректні межі прямокутника");
        }
        T res = query_prefix(r2, c2);
        if (r1 > 0) res -= query_prefix(r1 - 1, c2);
        if (c1 > 0) res -= query_prefix(r2, c1 - 1);
        if (r1 > 0 && c1 > 0) res += query_prefix(r1 - 1, c1 - 1);
        return res;
    }
};
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    size_t rows;
    size_t cols;
    long long* tree; // Одновимірний масив для плоского представлення rows*cols
} fenwick_2d_t;

static inline size_t fenwick_2d_lsb(size_t i) {
    return i & (-i);
}

fenwick_2d_t* fenwick_2d_create(size_t rows, size_t cols) {
    fenwick_2d_t* ft = (fenwick_2d_t*)malloc(sizeof(fenwick_2d_t));
    if (!ft) return NULL;
    ft->rows = rows;
    ft->cols = cols;
    ft->tree = (long long*)calloc((rows + 1) * (cols + 1), sizeof(long long));
    if (!ft->tree) {
        free(ft);
        return NULL;
    }
    return ft;
}

void fenwick_2d_destroy(fenwick_2d_t* ft) {
    if (ft) {
        free(ft->tree);
        free(ft);
    }
}

#define TREE_2D_AT(ft, i, j) ((ft)->tree[(i) * ((ft)->cols + 1) + (j)])

bool fenwick_2d_add(fenwick_2d_t* ft, size_t r, size_t c, long long val) {
    if (!ft || r >= ft->rows || c >= ft->cols) return false;
    for (size_t i = r + 1; i <= ft->rows; i += fenwick_2d_lsb(i)) {
        for (size_t j = c + 1; j <= ft->cols; j += fenwick_2d_lsb(j)) {
            TREE_2D_AT(ft, i, j) += val;
        }
    }
    return true;
}

long long fenwick_2d_query_prefix(const fenwick_2d_t* ft, size_t r, size_t c) {
    if (!ft || r >= ft->rows || c >= ft->cols) return 0;
    long long sum = 0;
    for (size_t i = r + 1; i > 0; i -= fenwick_2d_lsb(i)) {
        for (size_t j = c + 1; j > 0; j -= fenwick_2d_lsb(j)) {
            sum += TREE_2D_AT(ft, i, j);
        }
    }
    return sum;
}

long long fenwick_2d_query_rect(const fenwick_2d_t* ft, size_t r1, size_t c1, size_t r2, size_t c2) {
    if (!ft || r1 > r2 || c1 > c2 || r2 >= ft->rows || c2 >= ft->cols) return 0;
    long long res = fenwick_2d_query_prefix(ft, r2, c2);
    if (r1 > 0) res -= fenwick_2d_query_prefix(ft, r1 - 1, c2);
    if (c1 > 0) res -= fenwick_2d_query_prefix(ft, r2, c1 - 1);
    if (r1 > 0 && c1 > 0) res += fenwick_2d_query_prefix(ft, r1 - 1, c1 - 1);
    return res;
}
```
:::

---

### 3. Двохмасивне дерево Фенвіка для Range Update & Range Query

Для виконання інтервальних додавань `A[left..right] += val` та інтервальних запитів сум `sum(A[left..right])` за логарифмічний час використовується алгебра двох дерев Фенвіка. Перше дерево `t1_` зберігає різницевий масив `D[i]`, а друге дерево `t2_` зберігає зважений різницевий масив `(i - 1) · D[i]`.

#### Розрахунок вагових компенсацій

При додаванні значення `val` на відрізку `[left, right]`:
1. У `t1_` додається `val` у позицію `left` та `-val` у позицію `right + 1`.
2. У `t2_` додається `val · left` у позицію `left` та `-val · (right + 1)` у позицію `right + 1`.

Сума префікса обчислюється за формулою `Pref(p) = (p + 1) · t1.query(p) - t2.query(p)`, що забезпечує точне збереження лінійного накопичення за час `O(log N)`.

:::tabs
```cpp
#include <vector>
#include <cstddef>
#include <stdexcept>

template <typename T = long long>
class FenwickRangeRange {
private:
    std::size_t n_;
    FenwickTree<T> t1_;
    FenwickTree<T> t2_;

    [[nodiscard]] T prefix_sum(std::size_t idx) const {
        if (idx == static_cast<std::size_t>(-1)) return T{0};
        T sum1 = t1_.query_prefix(idx);
        T sum2 = t2_.query_prefix(idx);
        return sum1 * static_cast<T>(idx + 1) - sum2;
    }

public:
    explicit FenwickRangeRange(std::size_t size)
        : n_(size), t1_(size), t2_(size) {}

    // Додати val до всіх елементів на відрізку [left, right] (0-based)
    void range_add(std::size_t left, std::size_t right, T val) {
        if (left > right || right >= n_) {
            throw std::out_of_range("Некоректні межі для RangeAdd");
        }
        t1_.add(left, val);
        t2_.add(left, val * static_cast<T>(left));

        if (right + 1 < n_) {
            t1_.add(right + 1, -val);
            t2_.add(right + 1, -val * static_cast<T>(right + 1));
        }
    }

    // Сума елементів на відрізку [left, right] (0-based)
    [[nodiscard]] T query_range(std::size_t left, std::size_t right) const {
        if (left > right || right >= n_) {
            throw std::out_of_range("Некоректні межі для RangeQuery");
        }
        if (left == 0) return prefix_sum(right);
        return prefix_sum(right) - prefix_sum(left - 1);
    }
};
```
```c
typedef struct {
    size_t size;
    fenwick_tree_t* t1;
    fenwick_tree_t* t2;
} fenwick_range_range_t;

fenwick_range_range_t* fenwick_rr_create(size_t size) {
    fenwick_range_range_t* frr = (fenwick_range_range_t*)malloc(sizeof(fenwick_range_range_t));
    if (!frr) return NULL;
    frr->size = size;
    frr->t1 = fenwick_create(size);
    frr->t2 = fenwick_create(size);
    if (!frr->t1 || !frr->t2) {
        fenwick_destroy(frr->t1);
        fenwick_destroy(frr->t2);
        free(frr);
        return NULL;
    }
    return frr;
}

void fenwick_rr_destroy(fenwick_range_range_t* frr) {
    if (frr) {
        fenwick_destroy(frr->t1);
        fenwick_destroy(frr->t2);
        free(frr);
    }
}

static long long fenwick_rr_prefix(const fenwick_range_range_t* frr, size_t idx) {
    long long sum1 = fenwick_query_prefix(frr->t1, idx);
    long long sum2 = fenwick_query_prefix(frr->t2, idx);
    return sum1 * (long long)(idx + 1) - sum2;
}

bool fenwick_rr_add(fenwick_range_range_t* frr, size_t left, size_t right, long long val) {
    if (!frr || left > right || right >= frr->size) return false;
    fenwick_add(frr->t1, left, val);
    fenwick_add(frr->t2, left, val * (long long)left);

    if (right + 1 < frr->size) {
        fenwick_add(frr->t1, right + 1, -val);
        fenwick_add(frr->t2, right + 1, -val * (long long)(right + 1));
    }
    return true;
}

long long fenwick_rr_query(const fenwick_range_range_t* frr, size_t left, size_t right) {
    if (!frr || left > right || right >= frr->size) return 0;
    if (left == 0) return fenwick_rr_prefix(frr, right);
    return fenwick_rr_prefix(frr, right) - fenwick_rr_prefix(frr, left - 1);
}
```
:::

---

### 4. Двійковий підйом (Binary Lifting) на дереві Фенвіка

Якщо вихідні елементи масиву `A[i]` є невід'ємними (`A[i] ≥ 0`), то послідовність префіксних сум є неупорядковано монотонно зростаючою. Це дозволяє виконувати пошук найменшого індексу `idx`, для якого `query_prefix(idx) ≥ target_sum`, за час `O(log N)` без використання бінарного пошуку поверх префіксних запитів (який займав би `O(log^2 N)`).

#### Механіка двійкового проходу по бітах

Алгоритм стартує з найвищого степеня двійки `max_pow ≤ N` і випробовує кроки `len = max_pow, max_pow/2, ..., 1`. Якщо додавання блоку `tree_[idx + len]` до накопиченої суми `current_sum` залишає результат строго меншим за `target_sum`, індекс `idx` зміщується на `len`, а сума накопичується. По закінченні циклу `idx` вказує на точну межу пошуку.

:::tabs
```cpp
#include <vector>
#include <cstddef>

// Знаходження найменшого 0-based індексу idx, для якого query_prefix(idx) >= target_sum
// Умова: усі елементи масиву неот'ємні (A[i] >= 0)
template <typename T = long long>
std::size_t lower_bound_fenwick(const FenwickTree<T>& ft, T target_sum) {
    if (target_sum <= 0) return 0;

    std::size_t n = ft.size();
    std::size_t idx = 0;
    T current_sum = T{0};

    // Знаходимо найближчу більшу або рівну степінь двійки
    std::size_t max_pow = 1;
    while ((max_pow << 1) <= n) {
        max_pow <<= 1;
    }

    for (std::size_t len = max_pow; len > 0; len >>= 1) {
        std::size_t next_idx = idx + len;
        if (next_idx <= n && current_sum + ft.tree_[next_idx] < target_sum) {
            idx = next_idx;
            current_sum += ft.tree_[idx];
        }
    }

    // idx повертає 0-based індекс шуканого елемента
    return idx;
}
```
```c
#include <stdio.h>
#include <stdlib.h>

// Повертає 0-based індекс першого елемента, префіксна сума якого >= target_sum
size_t fenwick_lower_bound(const fenwick_tree_t* ft, long long target_sum) {
    if (!ft || target_sum <= 0) return 0;

    size_t idx = 0;
    long long current_sum = 0;

    size_t max_pow = 1;
    while ((max_pow << 1) <= ft->size) {
        max_pow <<= 1;
    }

    for (size_t len = max_pow; len > 0; len >>= 1) {
        size_t next_idx = idx + len;
        if (next_idx <= ft->size && current_sum + ft->tree[next_idx] < target_sum) {
            idx = next_idx;
            current_sum += ft->tree[idx];
        }
    }

    return idx;
}
```
:::

---

### 5. Інженерні нюанси та порівняння мовних реалізацій

При виборі між мовами C та C++ розробники повинні враховувати наступні системні аспекти:

1. **Інкапсуляція та шаблонність у C++:** Реалізація у вигляді шаблону `template <typename T>` дозволяє інстанціювати дерево Фенвіка для будь-яких типів даних, що підтримують додавання й віднімання (наприклад, `double`, `std::complex`, модульні цілі `ModInt` або матриці). Використання `std::vector` ґарантує автоматичне звільнення пам'яті (RAII) та відсутність витоків ресурсів при виникненні винятків.
2. **Низькорівнева швидкодія у C:** Версія мовою C використовує плоскі масиви `long long*` з прямим виділенням через `calloc`. Вона ідеально підходить для розробки компонентів операційних систем, драйверів, систем обробки сигналів на мікроконтролерах та вбудованих платформах без стандартної бібліотеки C++.
3. **Управління винятками:** Версія C++ генерує стандартні винятки `std::out_of_range` при некоректних аргументах, що робить її безпечною у високонавантажених сервісах. Версія C повертає `false` або `0`, що вимагає перевірки статусів у коді виклику.
