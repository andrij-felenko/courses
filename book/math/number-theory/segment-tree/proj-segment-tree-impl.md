# ⚙️ Практична реалізація дерева відрізків: точкові оновлення, відкладена пропогація та арифметичні точкові/інтервальні запити

Практичне втілення дерева відрізків вимагає свідомого вибору структури збереження в пам'яті, реалізації логарифмічних інтервальних запитів та ретельної обробки крайніх випадків (породження порожніх інтервалів, переповнення цілочисельних типів даних та контроль глибини рекурсивного спуску). 

У цьому розборі розглянуто практичну реалізацію трьох фундаментальних різновидів дерева відрізків:
1. **Дерева з точковими оновленнями та моноїдом найбільшого спільного дільника (Range GCD):** застосовується для динамічних числових послідовностей, де необхідно підтримувати спільні дільники при зміні поодиноких елементів.
2. **Дерева з груповими оновленнями та відкладеною пропогацією (Lazy Propagation):** призначено для обробки інтервальних модифікацій (додавання числа на відрізку) із збереженням логарифмічної складності `O(log N)`.
3. **Нерекурсивного (Bottom-Up) дерева відрізків:** оптимізованого варіанта для систем реального часу з мінімальними процесорними накладними витратами.

Обидві структури подано у вигляді ідіоматичних реалізацій мовами C та C++.

## 1. Точкові оновлення та інтервальний НСД (Point Update & Range GCD)

Для масиву з `N` елементів дерево відрізків компактно розміщується в плоскому масиві розміром `4N`. Кожен вузол із індексом `v` має лівого сина `2v` та правого сина `2v + 1`. Кореневий вузол лежить за індексом `v = 1` і відповідає повному інтервалу `[0, N - 1]`.

При виклику побудови `build` масив рекурсивно ділиться навпіл. Кожен листок отримує відповідне значення початкового масиву, а внутрішні вузли агрегують результат за допомогою бінарної операції `gcd(a, b)`.

Обчислення НСД на інтервалі виконується функцією `query_gcd_rec`. У разі повного виходу за межі запиту функція повертає нейтральний елемент моноїда `0`, оскільки за фундаментальною властивістю дільників `gcd(a, 0) = a`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

/* Обчислення найбільшого спільного дільника за алгоритмом Евкліда */
static uint64_t gcd_op(uint64_t a, uint64_t b) {
    while (b != 0) {
        uint64_t temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

typedef struct {
    uint64_t *tree;
    size_t n;
} SegTreeGCD;

/* Ініціалізація та побудова дерева відрізків */
static void build_gcd(SegTreeGCD *st, const uint64_t *arr, size_t v, size_t tl, size_t tr) {
    if (tl == tr) {
        st->tree[v] = arr[tl];
        return;
    }
    size_t tm = tl + (tr - tl) / 2;
    build_gcd(st, arr, 2 * v, tl, tm);
    build_gcd(st, arr, 2 * v + 1, tm + 1, tr);
    st->tree[v] = gcd_op(st->tree[2 * v], st->tree[2 * v + 1]);
}

SegTreeGCD* segtree_gcd_create(const uint64_t *arr, size_t n) {
    if (n == 0) return NULL;
    SegTreeGCD *st = (SegTreeGCD*)malloc(sizeof(SegTreeGCD));
    if (!st) return NULL;
    st->n = n;
    st->tree = (uint64_t*)calloc(4 * n, sizeof(uint64_t));
    if (!st->tree) {
        free(st);
        return NULL;
    }
    build_gcd(st, arr, 1, 0, n - 1);
    return st;
}

void segtree_gcd_free(SegTreeGCD *st) {
    if (st) {
        free(st->tree);
        free(st);
    }
}

/* Обчислення НСД на відрізку [l, r] */
static uint64_t query_gcd_rec(const SegTreeGCD *st, size_t v, size_t tl, size_t tr, size_t l, size_t r) {
    if (l > r) return 0; /* Нейтральний елемент моноїда НСД */
    if (l == tl && r == tr) {
        return st->tree[v];
    }
    size_t tm = tl + (tr - tl) / 2;
    size_t right_l = (l > tm + 1) ? l : tm + 1;
    size_t left_r = (r < tm) ? r : tm;

    uint64_t left_res = (l <= tm) ? query_gcd_rec(st, 2 * v, tl, tm, l, left_r) : 0;
    uint64_t right_res = (r > tm) ? query_gcd_rec(st, 2 * v + 1, tm + 1, tr, right_l, r) : 0;

    return gcd_op(left_res, right_res);
}

uint64_t segtree_gcd_query(const SegTreeGCD *st, size_t l, size_t r) {
    if (!st || l >= st->n || r >= st->n || l > r) return 0;
    return query_gcd_rec(st, 1, 0, st->n - 1, l, r);
}

/* Точкове оновлення значення за індексом idx */
static void update_gcd_rec(SegTreeGCD *st, size_t v, size_t tl, size_t tr, size_t idx, uint64_t new_val) {
    if (tl == tr) {
        st->tree[v] = new_val;
        return;
    }
    size_t tm = tl + (tr - tl) / 2;
    if (idx <= tm) {
        update_gcd_rec(st, 2 * v, tl, tm, idx, new_val);
    } else {
        update_gcd_rec(st, 2 * v + 1, tm + 1, tr, idx, new_val);
    }
    st->tree[v] = gcd_op(st->tree[2 * v], st->tree[2 * v + 1]);
}

void segtree_gcd_update(SegTreeGCD *st, size_t idx, uint64_t new_val) {
    if (!st || idx >= st->n) return;
    update_gcd_rec(st, 1, 0, st->n - 1, idx, new_val);
}
```
```cpp
#include <vector>
#include <numeric>
#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>

template <typename T = uint64_t>
class SegmentTreeGCD {
private:
    size_t n_;
    std::vector<T> tree_;

    static T combine(T a, T b) noexcept {
        return std::gcd(a, b);
    }

    void build(std::span<const T> arr, size_t v, size_t tl, size_t tr) {
        if (tl == tr) {
            tree_[v] = arr[tl];
            return;
        }
        size_t tm = tl + (tr - tl) / 2;
        build(arr, 2 * v, tl, tm);
        build(arr, 2 * v + 1, tm + 1, tr);
        tree_[v] = combine(tree_[2 * v], tree_[2 * v + 1]);
    }

    T query_rec(size_t v, size_t tl, size_t tr, size_t l, size_t r) const noexcept {
        if (l > r) return 0;
        if (l == tl && r == tr) {
            return tree_[v];
        }
        size_t tm = tl + (tr - tl) / 2;
        size_t right_l = (l > tm + 1) ? l : tm + 1;
        size_t left_r = (r < tm) ? r : tm;

        T left_res = (l <= tm) ? query_rec(2 * v, tl, tm, l, left_r) : 0;
        T right_res = (r > tm) ? query_rec(2 * v + 1, tm + 1, tr, right_l, r) : 0;

        return combine(left_res, right_res);
    }

    void update_rec(size_t v, size_t tl, size_t tr, size_t idx, T new_val) {
        if (tl == tr) {
            tree_[v] = new_val;
            return;
        }
        size_t tm = tl + (tr - tl) / 2;
        if (idx <= tm) {
            update_rec(2 * v, tl, tm, idx, new_val);
        } else {
            update_rec(2 * v + 1, tm + 1, tr, idx, new_val);
        }
        tree_[v] = combine(tree_[2 * v], tree_[2 * v + 1]);
    }

public:
    explicit SegmentTreeGCD(std::span<const T> arr) : n_(arr.size()), tree_(4 * arr.size(), 0) {
        if (n_ > 0) {
            build(arr, 1, 0, n_ - 1);
        }
    }

    [[nodiscard]] T query(size_t l, size_t r) const noexcept {
        if (l >= n_ || r >= n_ || l > r) return 0;
        return query_rec(1, 0, n_ - 1, l, r);
    }

    void update(size_t idx, T new_val) {
        if (idx >= n_) return;
        update_rec(1, 0, n_ - 1, idx, new_val);
    }

    [[nodiscard]] size_t size() const noexcept { return n_; }
};
```
:::

У версії C++ реалізація узагальнена шаблоном `SegmentTreeGCD<T>` та бере дані з сучасного стандартизованого типу `std::span<const T>`, що запобігає зайвому копіюванню пам'яті. Виклики `std::gcd` забезпечують апаратно обчислений НСД із використанням алгоритму Евкліда.

## 2. Групові оновлення та відкладена пропогація (Lazy Propagation)

Для обробки інтервальних модифікацій (додавання числа `addend` до всіх елементів підмасиву `[l, r]`) у кожному вузлі зберігається додатковий прапорець `lazy[v]`. 

При виконанні будь-якої операції (запиту суми або оновлення відрізка), перед спуском у дочірні піддерева викликається функція `push(v, tl, tr)`. Ця функція передає накопичений відкладений зсув до дочірніх вузлів та оновлює їхні сумарні значення за правилом:
```
sum[child] = sum[child] + lazy[parent] · len_child
```
Після успішного проштовхування значення `lazy[v]` скидається в 0.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef struct {
    int64_t *sum;
    int64_t *lazy;
    size_t n;
} SegTreeLazy;

SegTreeLazy* segtree_lazy_create(const int64_t *arr, size_t n) {
    if (n == 0) return NULL;
    SegTreeLazy *st = (SegTreeLazy*)malloc(sizeof(SegTreeLazy));
    if (!st) return NULL;
    st->n = n;
    st->sum = (int64_t*)calloc(4 * n, sizeof(int64_t));
    st->lazy = (int64_t*)calloc(4 * n, sizeof(int64_t));
    if (!st->sum || !st->lazy) {
        free(st->sum);
        free(st->lazy);
        free(st);
        return NULL;
    }
    return st;
}

void segtree_lazy_free(SegTreeLazy *st) {
    if (st) {
        free(st->sum);
        free(st->lazy);
        free(st);
    }
}

/* Передача відкладеного прапорця вниз по дереву */
static void push(SegTreeLazy *st, size_t v, size_t tl, size_t tr) {
    if (st->lazy[v] != 0) {
        size_t tm = tl + (tr - tl) / 2;
        size_t left_len = tm - tl + 1;
        size_t right_len = tr - tm;

        /* Оновлюємо лівого сина */
        st->sum[2 * v] += st->lazy[v] * (int64_t)left_len;
        st->lazy[2 * v] += st->lazy[v];

        /* Оновлюємо правого сина */
        st->sum[2 * v + 1] += st->lazy[v] * (int64_t)right_len;
        st->lazy[2 * v + 1] += st->lazy[v];

        /* Скидаємо прапорець поточного вузла */
        st->lazy[v] = 0;
    }
}

/* Групове оновлення додаванням на відрізку [l, r] */
static void update_range_rec(SegTreeLazy *st, size_t v, size_t tl, size_t tr, size_t l, size_t r, int64_t addend) {
    if (l > r) return;
    if (l == tl && r == tr) {
        st->sum[v] += addend * (int64_t)(tr - tl + 1);
        st->lazy[v] += addend;
        return;
    }
    push(st, v, tl, tr);
    size_t tm = tl + (tr - tl) / 2;
    size_t right_l = (l > tm + 1) ? l : tm + 1;
    size_t left_r = (r < tm) ? r : tm;

    if (l <= tm) update_range_rec(st, 2 * v, tl, tm, l, left_r, addend);
    if (r > tm) update_range_rec(st, 2 * v + 1, tm + 1, tr, right_l, r, addend);

    st->sum[v] = st->sum[2 * v] + st->sum[2 * v + 1];
}

void segtree_lazy_update_range(SegTreeLazy *st, size_t l, size_t r, int64_t addend) {
    if (!st || l >= st->n || r >= st->n || l > r) return;
    update_range_rec(st, 1, 0, st->n - 1, l, r, addend);
}

/* Інтервальний запит суми на [l, r] з урахуванням відкладених оновлень */
static int64_t query_sum_rec(SegTreeLazy *st, size_t v, size_t tl, size_t tr, size_t l, size_t r) {
    if (l > r) return 0;
    if (l == tl && r == tr) {
        return st->sum[v];
    }
    push(st, v, tl, tr);
    size_t tm = tl + (tr - tl) / 2;
    size_t right_l = (l > tm + 1) ? l : tm + 1;
    size_t left_r = (r < tm) ? r : tm;

    int64_t left_res = (l <= tm) ? query_sum_rec(st, 2 * v, tl, tm, l, left_r) : 0;
    int64_t right_res = (r > tm) ? query_sum_rec(st, 2 * v + 1, tm + 1, tr, right_l, r) : 0;

    return left_res + right_res;
}

int64_t segtree_lazy_query_sum(SegTreeLazy *st, size_t l, size_t r) {
    if (!st || l >= st->n || r >= st->n || l > r) return 0;
    return query_sum_rec(st, 1, 0, st->n - 1, l, r);
}
```
```cpp
#include <vector>
#include <cstdint>
#include <cstddef>
#include <span>

template <typename T = int64_t>
class SegmentTreeLazy {
private:
    size_t n_;
    std::vector<T> sum_;
    std::vector<T> lazy_;

    void push(size_t v, size_t tl, size_t tr) noexcept {
        if (lazy_[v] != 0) {
            size_t tm = tl + (tr - tl) / 2;
            size_t left_len = tm - tl + 1;
            size_t right_len = tr - tm;

            sum_[2 * v] += lazy_[v] * static_cast<T>(left_len);
            lazy_[2 * v] += lazy_[v];

            sum_[2 * v + 1] += lazy_[v] * static_cast<T>(right_len);
            lazy_[2 * v + 1] += lazy_[v];

            lazy_[v] = 0;
        }
    }

    void update_range_rec(size_t v, size_t tl, size_t tr, size_t l, size_t r, T addend) {
        if (l > r) return;
        if (l == tl && r == tr) {
            sum_[v] += addend * static_cast<T>(tr - tl + 1);
            lazy_[v] += addend;
            return;
        }
        push(v, tl, tr);
        size_t tm = tl + (tr - tl) / 2;
        size_t right_l = (l > tm + 1) ? l : tm + 1;
        size_t left_r = (r < tm) ? r : tm;

        if (l <= tm) update_range_rec(2 * v, tl, tm, l, left_r, addend);
        if (r > tm) update_range_rec(2 * v + 1, tm + 1, tr, right_l, r, addend);

        sum_[v] = sum_[2 * v] + sum_[2 * v + 1];
    }

    T query_sum_rec(size_t v, size_t tl, size_t tr, size_t l, size_t r) {
        if (l > r) return 0;
        if (l == tl && r == tr) {
            return sum_[v];
        }
        push(v, tl, tr);
        size_t tm = tl + (tr - tl) / 2;
        size_t right_l = (l > tm + 1) ? l : tm + 1;
        size_t left_r = (r < tm) ? r : tm;

        T left_res = (l <= tm) ? query_sum_rec(2 * v, tl, tm, l, left_r) : 0;
        T right_res = (r > tm) ? query_sum_rec(2 * v + 1, tm + 1, tr, right_l, r) : 0;

        return left_res + right_res;
    }

public:
    explicit SegmentTreeLazy(size_t n) : n_(n), sum_(4 * n, 0), lazy_(4 * n, 0) {}

    void update_range(size_t l, size_t r, T addend) {
        if (l >= n_ || r >= n_ || l > r) return;
        update_range_rec(1, 0, n_ - 1, l, r, addend);
    }

    [[nodiscard]] T query_sum(size_t l, size_t r) {
        if (l >= n_ || r >= n_ || l > r) return 0;
        return query_sum_rec(1, 0, n_ - 1, l, r);
    }
};
```
:::

Особливість реалізації полягає у суворому дотриманні логіки `push`: відкладений прапорець оновлює безпосередні суми дочірніх вузлів та додається до їхніх власних прапорців `lazy`, після чого `lazy` поточного вузла обнуляється. Це гарантує правильність при каскадних накладаннях оновлень.

## 3. Нерекурсивна (Bottom-Up) реалізація дерева відрізків

У системах із підвищеними вимогами до продуктивності (наприклад, алгоритми обробки фінансових транзакцій або обчислювальні графічні ядра) накладні витрати на виклики рекурсивних функцій є небажаними. Нерекурсивне дерево відрізків зберігає листки початкового масиву у другій половині плоского масиву за індексами `n + i` (де `0 ≤ i < N`).

Внутрішні вузли будуються заповненням від індексу `N - 1` до `1` за формулою:
```
tree[i] = tree[2i] ⊗ tree[2i + 1]
```

### Аналіз бітових операцій нерекурсивного запиту

Нерекурсивний алгоритм запиту обходить дерево підйомом угору від листків `l` та `r` до спільної вершини. 

Умови `l & 1` та `r & 1` обробляють межі покриття:
- Умова `if (l & 1)` перевіряє, чи є `l` правим сином свого батька. Якщо це так, цей вузол не можна об'єднувати з лівим братом, оскільки лівий брат лежить поза межами запиту `[l, r]`. Тому значення `tree[l]` додається до лівого акумулятора `res`, а індекс просувається праворуч `l++`.
- Умова `if (r & 1)` перевіряє, чи є `r` правим сином свого батька. При використанні напіввідкритого інтервалу `[l, r)`, якщо `r` є правим сином, то лівий син `r - 1` повністю входить у запит. Індекс зменшується `--r`, і значення `tree[r]` додається до правого акумулятора.
- Зсув `l >>= 1` та `r >>= 1` піднімає межі запиту на один рівень угору до батьківських вузлів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef struct {
    uint64_t *tree;
    size_t n;
} SegTreeIterative;

SegTreeIterative* segtree_iterative_create(const uint64_t *arr, size_t n) {
    if (n == 0) return NULL;
    SegTreeIterative *st = (SegTreeIterative*)malloc(sizeof(SegTreeIterative));
    if (!st) return NULL;
    st->n = n;
    st->tree = (uint64_t*)calloc(2 * n, sizeof(uint64_t));
    if (!st->tree) {
        free(st);
        return NULL;
    }
    /* Копіюємо листки у другу половину масиву */
    for (size_t i = 0; i < n; ++i) {
        st->tree[n + i] = arr[i];
    }
    /* Заповнюємо внутрішні вузли знизу вгору */
    for (size_t i = n - 1; i > 0; --i) {
        st->tree[i] = st->tree[2 * i] + st->tree[2 * i + 1];
    }
    return st;
}

void segtree_iterative_update(SegTreeIterative *st, size_t p, uint64_t val) {
    if (!st || p >= st->n) return;
    for (st->tree[p += st->n] = val; p > 1; p >>= 1) {
        st->tree[p >> 1] = st->tree[p] + st->tree[p ^ 1];
    }
}

uint64_t segtree_iterative_query(const SegTreeIterative *st, size_t l, size_t r) {
    if (!st || l >= st->n || r >= st->n || l > r) return 0;
    uint64_t res = 0;
    for (l += st->n, r += st->n + 1; l < r; l >>= 1, r >>= 1) {
        if (l & 1) res += st->tree[l++];
        if (r & 1) res += st->tree[--r];
    }
    return res;
}

void segtree_iterative_free(SegTreeIterative *st) {
    if (st) {
        free(st->tree);
        free(st);
    }
}
```
```cpp
#include <vector>
#include <cstdint>
#include <cstddef>
#include <span>

template <typename T = uint64_t>
class SegmentTreeIterative {
private:
    size_t n_;
    std::vector<T> tree_;

public:
    explicit SegmentTreeIterative(std::span<const T> arr) : n_(arr.size()), tree_(2 * arr.size(), 0) {
        for (size_t i = 0; i < n_; ++i) {
            tree_[n_ + i] = arr[i];
        }
        for (size_t i = n_ - 1; i > 0; --i) {
            tree_[i] = tree_[2 * i] + tree_[2 * i + 1];
        }
    }

    void update(size_t p, T val) noexcept {
        if (p >= n_) return;
        for (tree_[p += n_] = val; p > 1; p >>= 1) {
            tree_[p >> 1] = tree_[p] + tree_[p ^ 1];
        }
    }

    [[nodiscard]] T query(size_t l, size_t r) const noexcept {
        if (l >= n_ || r >= n_ || l > r) return 0;
        T res = 0;
        for (l += n_, r += n_ + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res += tree_[l++];
            if (r & 1) res += tree_[--r];
        }
        return res;
    }
};
```
:::

У функції оновлення `segtree_iterative_update` використано вираз `p ^ 1`. Побітове виключальне АБО з одиницею дозволяє за один такт обчислити індекс парного сусіда-брата: якщо `p` є парним (лівий син), `p ^ 1 = p + 1` (правий син); якщо `p` непарне (правий син), `p ^ 1 = p - 1` (лівий син). Це гарантує точне об'єднання двох дітей для оновлення батька `p >> 1`.

Нерекурсивна версія вимагає точно `2N` комірок пам'яті (замість `4N`), що удвічі економить оперативну пам'ять і забезпечує ідеальну кеш-локальність для процесорних ліній L1/L2.

## 4. Аналіз керування пам'яттю та інженерні пастки

### 4.1. Динамічне виділення пам'яті в C проти RAII в C++

У реалізації C виділення пам'яті через `calloc(4 * n, sizeof(...))` виконується явно. Клієнтський код повинен гарантувати виклик `segtree_gcd_free` або `segtree_lazy_free`. Перевірки `if (!st->tree)` гарантують відсутність краху при браку системного ресурсу RAM.

У реалізації C++ використання `std::vector` повністю абстрагує виділення пам'яті за принципом RAII (Resource Acquisition Is Initialization). Деструктор класу автоматично очищає пам'ять при виході об'єкта зі сфери видимості, виключаючи витоки пам'яті.

### 4.2. Обчислення середньої точки без переповнення

Обчислення середини інтервалу `tm` у коді виконується через вираз `tl + (tr - tl) / 2`. 

Прямолінійне обчислення `(tl + tr) / 2` при великих індексах (близьких до `SIZE_MAX`) спричиняє цілочисельне переповнення, що призводить до непередбачуваної поведінки. Формула `tl + (tr - tl) / 2` арифметично тотожна, але повністю захищена від переповнення розрядів.

### 4.3. Прапорець `noexcept` та оптимізація компілятора

У C++ версії методи, які не викидають винятків (наприклад, `query` та `size`), позначені специфікатором `noexcept` та атрибутом `[[nodiscard]]`. Це попереджає ігнорування поверненого значення та дозволяє компілятору генерувати оптимізований машинний код без блоків обробки винятків.
