# ⚙️ Практичні алгоритми та контрприклади у коді

Ця вставка розгортає принцип Діріхле у реальному програмному коді та алгоритмічному аналізі. Вона демонструє, як суто теорема існування перетворюється на практичні алгоритми з гарантованою часовою складністю, а також слугує математичним інструментом для оцінки фундаментальних меж обчислювальності. У розділі розібрано дев'ять практичних задач: лінійний пошук підмасиву із сумою, кратною `N`, знаходження дубліката за `O(N)` часу та `O(1)` пам'яті за допомогою аналізу функціональних графів (алгоритм Флойда), обчислення періоду зациклення псевдовипадкових генераторів (LCG), оцінка каскадного накопичення колізій у хеш-таблицях з відкритою адресацією, детекція хеш-колізій у пошуку підрядка Рабіна-Карпа, аналіз хибних спрацювань у фільтрі Блума, оцінка криптографічних колізій у хекс-хешуванні, аналіз витиснення у системному кеші процесора, а також програмну перевірку неможливості універсального стиснення без втрат.

---

## Задача 1: Лінійний пошук підмасиву із сумою, кратною N

### Математичний механізм та коректність остач

Дано масив `A` з `N` цілих чисел. Задача полягає у знаходженні безперервного відрізка `A[i..j]` (де `0 ≤ i ≤ j < N`), сума елементів якого ділиться на `N` без остачі.

Наївний підхід вимагає обчислення сум усіх можливих `N(N + 1) / 2` підмасивів, що дає часову складність `O(N²)`. Проте принцип Діріхле дозволяє скоротити обчислення до прямого лінійного проходу за `O(N)` часу та `O(N)` додаткової пам'яті.

Розглянемо `N + 1` префіксних сум:

```
S₀ = 0
S₁ = A[0]
S₂ = A[0] + A[1]
...
S_N = A[0] + A[1] + ... + A[N-1]
```

Для кожної префіксної суми обчислимо її математичний залишок від ділення на `N`: `Rₖ = Sₖ mod N`. 
Оскільки остач від ділення на `N` існує рівно `N` варіантів — з множини `{0, 1, 2, ..., N - 1}`, а префіксних сум ми маємо `N + 1` штук, за принципом Діріхле принаймні дві префіксні суми `S_i` та `S_j` (де `i < j`) матимуть абсолютно однакову остачу:

```
S_i ≡ S_j (mod N)
```

Звідси випливає, що їхня різниця ділиться на `N` без остачі:

```
S_j - S_i  =  (A[0] + ... + A[j-1]) - (A[0] + ... + A[i-1])
           =  A[i] + A[i+1] + ... + A[j-1]  ≡  0 (mod N)
```

Отже, підмасив елементів з індексу `i` до `j - 1` має суму, кратну `N`.

### Аналіз алгоритмічної складності та кеш-ефективність

З погляду системного програмування, цей алгоритм гарантує лінійний час виконання `O(N)` у найгіршому випадку. Пам'ять розподіляється одноразовим блоком під `N` цілих чисел. Оскільки префіксна сума накопичується послідовно в одному регістрі процесора, а звернення до масиву остач `pos[rem]` відбувається з локальністю за посиланнями, кеш-промахи першого рівня (L1 cache misses) є мінімальними.

Завдяки принципу Діріхле ми маємо абсолютну гарантію того, що алгоритм знайде шуканий підмасив ще до завершення циклу `N` кроків. Якщо одна з остач дорівнює `0` (що відповідає колізії з початковим рівнем `S₀ = 0`), вихід відбувається миттєво. Важливо підкреслити, що ця гарантія є детермінованою і не залежить від розподілу вхідних даних чи знаків елементів масиву. 

Практична цінність алгоритму полягає в тому, що він працює для довільних великих послідовностей у розлитому потоці даних (Streaming Algorithms).

### Крайові випадки та математичний модуль у коді

Під час реалізації цієї ідеї мовами C та C++ виникає важлива практична пастка: стандартний оператор `%` у C/C++ для від'ємних чисел повертає від'ємну остачу (наприклад, `-7 % 5 = -2`, тоді як математичний модуль має давати `3`). Для коректного відображення від'ємних остач у діапазон `[0, N - 1]` використовується формула:

```
R = ((S % N) + N) % N
```

Також варто врахувати крайові випадки:
1. Якщо у масиві є хоч один елемент `A[k]`, який вже ділиться на `N` (або дорівнює 0), то підмасив із цього єдиного елемента є розв'язком.
2. Якщо префіксна сума `S_j` сама по собі ділиться на `N` без остачі, то `S_j ≡ 0 (mod N)`. Оскільки `S₀ = 0` також має остачу `0`, колізія відбувається з `S₀`, і шуканим є підмасив від початку масиву `A[0..j-1]`.

Нижче наведено робочу реалізацію алгоритму мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int start_index; // Початковий індекс підмасиву (включно)
    int end_index;   // Кінцевий індекс підмасиву (включно)
    long long sum;   // Обчислена сума підмасиву
    int found;       // Прапор успішного знаходження (1 — знайдено, 0 — ні)
} SubarrayResult;

SubarrayResult find_zero_sum_mod_n(const int* arr, size_t n) {
    SubarrayResult res = { -1, -1, 0, 0 };
    if (n == 0 || arr == NULL) return res;

    // Масив для фіксації першої позиції кожної остачі (ініціалізуємо значенням -1)
    int* pos = (int*)malloc(n * sizeof(int));
    if (!pos) return res;

    for (size_t k = 0; k < n; ++k) {
        pos[k] = -1;
    }

    // Остача 0 зафіксована на префіксі довжиною 0 (перед початком масиву)
    pos[0] = 0;

    long long current_sum = 0;
    for (size_t j = 1; j <= n; ++j) {
        current_sum += arr[j - 1];

        // Коректне обчислення математичного модуля для від'ємних чисел
        long long mod_raw = current_sum % (long long)n;
        int rem = (int)((mod_raw + (long long)n) % (long long)n);

        if (pos[rem] != -1) {
            // Знайдено колізію остач за принципом Діріхле!
            res.start_index = pos[rem];       // Індекс початку (0-based)
            res.end_index = (int)j - 1;       // Індекс кінця (0-based)
            res.sum = current_sum;
            res.found = 1;
            free(pos);
            return res;
        }

        pos[rem] = (int)j;
    }

    free(pos);
    return res;
}

int main(void) {
    int data[] = { 4, -7, 2, 9, -5 };
    size_t n = sizeof(data) / sizeof(data[0]);

    SubarrayResult res = find_zero_sum_mod_n(data, n);
    if (res.found) {
        printf("Знайдено підмасив [індекси %d..%d]: ", res.start_index, res.end_index);
        long long sub_sum = 0;
        for (int k = res.start_index; k <= res.end_index; ++k) {
            printf("%d ", data[k]);
            sub_sum += data[k];
        }
        printf("\nСума підмасиву = %lld (кратно %zu)\n", sub_sum, n);
    } else {
        printf("Помилка: підмасив не знайдено (математично неможливо для N > 0).\n");
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <optional>
#include <span >

struct SubarrayRange {
    size_t start_index; // Включно (0-indexed)
    size_t end_index;   // Включно (0-indexed)
    long long sum;      // Сума підмасиву
};

std::optional<SubarrayRange> find_zero_sum_mod_n(std::span<const int> arr) {
    const size_t n = arr.size();
    if (n == 0) return std::nullopt;

    // Масив для збереження індексу префіксу (-1 означає "остача ще не зустрічалася")
    std::vector<int> first_seen_prefix(n, -1);
    first_seen_prefix[0] = 0; // S₀ = 0 дає остачу 0 на префіксі довжини 0

    long long current_prefix_sum = 0;
    for (size_t j = 1; j <= n; ++j) {
        current_prefix_sum += arr[j - 1];

        // Математичний модуль для довільних від'ємних і додатних сум
        long long mod_raw = current_prefix_sum % static_cast<long long>(n);
        size_t rem = static_cast<size_t>((mod_raw + static_cast<long long>(n)) % static_cast<long long>(n));

        if (first_seen_prefix[rem] != -1) {
            size_t i = static_cast<size_t>(first_seen_prefix[rem]);
            return SubarrayRange{
                .start_index = i,
                .end_index = j - 1,
                .sum = current_prefix_sum
            };
        }

        first_seen_prefix[rem] = static_cast<int>(j);
    }

    return std::nullopt;
}

int main() {
    const std::vector<int> data = { 4, -7, 2, 9, -5 };

    if (auto res = find_zero_sum_mod_n(data)) {
        std::cout << "Знайдено підмасив [індекси " << res->start_index 
                  << ".." << res->end_index << "]: ";
        long long sum = 0;
        for (size_t k = res->start_index; k <= res->end_index; ++k) {
            std::cout << data[k] << " ";
            sum += data[k];
        }
        std::cout << "\nСума = " << sum << " (кратно " << data.size() << ")\n";
    }
    return 0;
}
```
:::

---

## Задача 2: Знаходження дубліката у масиві (Алгоритм Флойда)

### Структура функціонального графа та аналіз сходження

Розглянемо класичну задачу з співбесід: маємо масив `A` довжиною `N + 1`, елементи якого є цілими числами в діапазоні від `1` до `N`. 

Оскільки вхідних елементів `N + 1` (об'єкти), а можливих значень лише `N` (комірки), за принципом Діріхле принаймні один елемент гарантовано дублюється. 

Завдання полягає у знаходженні цього дубліката за часовою складністю `O(N)` з використанням лише `O(1)` додаткової пам'яті та без модифікації вхідного масиву.

Створимо орієнтований граф, у якому кожні вершини є індексами `0, 1, ..., N`, а ребра задаються відображенням `i → A[i]`. 

Оскільки індекси лежать у діапазоні `[0, N]`, а значення `A[i]` — у діапазоні `[1, N]`:
- Індекс `0` не має вхідних ребер (бо значення `0` відсутнє в масиві).
- Кожна вершина має півстепінь виходу, рівний `1`.
- За принципом Діріхле, оскільки `N + 1` індексів посилаються на `N` значень, існує принаймні одна вершина з півстепенем заходу `≥ 2`.

Це означає, що такий граф **неодмінно містить цикл**, а точка входу в цей цикл відповідає значенням-дублікату.

```
Індекси:    0 ──> A[0] ──> A[A[0]] ──> ... ──> [ Точка входу в цикл ]
                                                      │           ▲
                                                      ▼           │
                                                      └───────────┘
```

### Двофазний алгоритм Флойда («черепаха та заєць»)

1. **Фаза 1 (Пошук точки зустрічі у циклі):** Запускаємо два вказівники з позиції `0`. «Черепаха» робить один крок `slow = A[slow]`, а «заєць» робить два кроки `fast = A[A[fast]]`. Вони неодмінно зустрінуться всередині циклу.
2. **Фаза 2 (Пошук входу в цикл):** Переставляємо «зайця» назад у початкову позицію `0`, а «черепаху» залишаємо у точці зустрічі. Тепер обидва вказівники рухаються з однаковою швидкістю по 1 кроку. Точка їхньої нової зустрічі є точною точкою входу в цикл, тобто значенням-дублікатом!

Математичне доведення того, чому фаза 2 знаходить саме точний вхід у цикл:
Нехай відстань від вершини `0` до входу в цикл дорівнює `F`, а довжина самого циклу дорівнює `C`. 
Під час першої фази, коли черепаха проходить `F + K` кроків (де `K` — відстань від входу до точки зустрічі), заєць проходить у два рази більше кроків `2(F + K)`. 
Оскільки вони зустрілися у циклі, різниця пройдених шляхів `(F + K)` мусить бути кратна довжині циклу `C`: `F + K = n · C`. 
Звідси відстань від початку до входу `F` задовольняє рівність `F = n · C - K`. 
Це означає, що якщо один вказівник стартує з позиції `0` і проходить `F` кроків, а другий вказівник стартує з точки зустрічі (відстань `K` від входу) і проходить ті самі `F` кроків, він зробить `n` повних кіл по циклу і опиниться у тій самій точці входу!

Порівняно з іншими підходами:
- Хеш-множина (HashSet) вимагає `O(N)` додаткової пам'яті.
- Сортування вимагає `O(N log N)` часу та модифікує вхідний масив.
- Двофазний алгоритм Флойда задовольнить усі вимоги: `O(N)` часу, `O(1)` пам'яті, без модифікацій.

Цей алгоритм демонструє, як суто неконструктивний принцип Діріхле перетворюється на елегантну обчислювальну процедуру з мінімальною просторовою складністю. Завдяки відсутності додаткових виділень пам'яті він широко застосовується у вбудованих системах (Embedded Systems) та критичному системному ПЗ.

:::tabs
```c
#include <stdio.h>

int find_duplicate_floyd(const int* arr, size_t size) {
    if (size <= 1 || arr == NULL) return -1;

    // Фаза 1: Пошук точки зустрічі всередині циклу
    int slow = arr[0];
    int fast = arr[arr[0]];

    while (slow != fast) {
        slow = arr[slow];
        fast = arr[arr[fast]];
    }

    // Фаза 2: Пошук точки входу в цикл (колізії Діріхле)
    fast = 0;
    while (slow != fast) {
        slow = arr[slow];
        fast = arr[fast];
    }

    return slow;
}

int main(void) {
    // Масив розміром N + 1 = 6 елементів (значення від 1 до 5)
    int numbers[] = { 3, 1, 3, 4, 2, 5 };
    size_t size = sizeof(numbers) / sizeof(numbers[0]);

    int dup = find_duplicate_floyd(numbers, size);
    printf("Масив з %zu елементів (значення 1..%zu): елемент-дублікат = %d\n",
           size, size - 1, dup);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span >

int find_duplicate_floyd(std::span<const int> arr) {
    if (arr.size() <= 1) return -1;

    // Фаза 1: Детекція циклу за допомогою двох швидкостей
    int slow = arr[0];
    int fast = arr[arr[0]];

    while (slow != fast) {
        slow = arr[slow];
        fast = arr[arr[fast]];
    }

    // Фаза 2: Зближення від початку масиву та з точки зустрічі
    fast = 0;
    while (slow != fast) {
        slow = arr[slow];
        fast = arr[fast];
    }

    return slow;
}

int main() {
    const std::vector<int> numbers = { 3, 1, 3, 4, 2, 5 };
    int dup = find_duplicate_floyd(numbers);
    std::cout << "Елемент-дублікат за принципом Діріхле: " << dup << "\n";
    return 0;
}
```
:::

---

## Задача 3: Період зациклення псевдовипадкових генераторів (LCG)

### Межі станів у цифрових автоматах та теорема Хулла-Добелла

Лінійний конгруентний генератор (LCG) є найпростішим алгоритмом генерування псевдовипадкових чисел. Він задається рекурентним співвідношенням:

```
X_{n+1} = (a · X_n + c) mod m
```

Оскільки модуль `m` обмежує кількість можливих станів генератора до `m` варіантів `{0, 1, ..., m - 1}`, за принципом Діріхле будь-яка послідовність з `m + 1` згенерованих чисел **неодмінно містить колізію станів**.

Як тільки стан повторюється `X_j = X_i` (де `i < j`), генератор замикається у цикл з періодом `P = j - i ≤ m`. Максимально можливий період дорівнює `m` і досягається лише за виконання умов теореми Хулла-Добелла:
1. Числа `c` та `m` є взаємно простими: `gcd(c, m) = 1`.
2. Число `a - 1` ділиться на всі прості дільники модуля `m`.
3. Якщо `m` ділиться на `4`, число `a - 1` також має ділитися на `4`.

Аналіз періодичності генератора вимагає відстеження першої появи кожного стану. За принципом комірок, масив відвіданих станів розміром `m` повністю вичерпує всі можливі випадки, гарантуючи припинення пошуку не пізніше ніж на `m`-му кроці.

Програмна перевірка дозволяє точно розрахувати як період `P`, так і довжину хвоста (pre-period) до входу у цикл.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    unsigned int period;
    unsigned int pre_period;
} LcgAnalysis;

LcgAnalysis analyze_lcg_period(unsigned int a, unsigned int c, unsigned int m, unsigned int seed) {
    LcgAnalysis res = { 0, 0 };
    if (m == 0) return res;

    // Масив для фіксації кроку, на якому стан зустрічається вперше (-1 = не зустрічався)
    int* visited_at = (int*)malloc(m * sizeof(int));
    if (!visited_at) return res;

    for (unsigned int i = 0; i < m; ++i) {
        visited_at[i] = -1;
    }

    unsigned int current = seed % m;
    int step = 0;

    while (visited_at[current] == -1) {
        visited_at[current] = step;
        current = (unsigned int)(((unsigned long long)a * current + c) % m);
        step++;
    }

    // За принципом Діріхле колізія настає не пізніше m кроків!
    res.pre_period = (unsigned int)visited_at[current];
    res.period = (unsigned int)step - res.pre_period;

    free(visited_at);
    return res;
}

int main(void) {
    // Приклад LCG: a=5, c=3, m=16, seed=1
    unsigned int a = 5, c = 3, m = 16, seed = 1;
    LcgAnalysis res = analyze_lcg_period(a, c, m, seed);

    printf("LCG (a=%u, c=%u, m=%u, seed=%u):\n", a, c, m, seed);
    printf("  Додовжина хвоста (pre-period): %u\n", res.pre_period);
    printf("  Період зациклення P (≤ m):      %u\n", res.period);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cstdint>

struct LcgAnalysis {
    uint32_t period;
    uint32_t pre_period;
};

LcgAnalysis analyze_lcg_period(uint32_t a, uint32_t c, uint32_t m, uint32_t seed) {
    if (m == 0) return {0, 0};

    std::vector<int> visited_at(m, -1);
    uint32_t current = seed % m;
    int step = 0;

    while (visited_at[current] == -1) {
        visited_at[current] = step;
        current = static_cast<uint32_t>((static_cast<uint64_t>(a) * current + c) % m);
        step++;
    }

    uint32_t pre = static_cast<uint32_t>(visited_at[current]);
    return LcgAnalysis{
        .period = static_cast<uint32_t>(step) - pre,
        .pre_period = pre,
    };
}

int main() {
    uint32_t a = 5, c = 3, m = 16, seed = 1;
    auto res = analyze_lcg_period(a, c, m, seed);

    std::cout << "Аналіз LCG за принципом Діріхле:\n"
              << "  Хвіст до зациклення: " << res.pre_period << "\n"
              << "  Період зациклення P: " << res.period << " (макс = " << m << ")\n";
    return 0;
}
```
:::

---

## Задача 4: Аналіз колізій у хеш-таблицях з відкритою адресацією

### Фактор заповнення та межа Діріхле

У хеш-таблиці з відкритою адресацією (Linear Probing) `N` ключових елементів вставляються безпосередньо у масив розміру `M`. 

Якщо фактор заповнення `α = N / M` наближається до `1.0`, за принципом Діріхле кількість вільних комірок тане до нуля:
- При `N = M` усі `M` комірок заповнені.
- Спроба вставити `(M + 1)`-ший елемент за принципом Діріхле спричиняє **неминуче переповнення таблиці**, оскільки вільних комірок більше немає.

Крім того, принцип Діріхле показує, що навіть при `N < M` скупчення елементів (кластеризація) викликає зростання кількості колізій зондування: коли `k` елементів потрапляють у ту саму групу послідовних комірок, наступна вставка вимагає `k + 1` перевірок.

Порівняно з методом ланцюжків (Separate Chaining), де колізії створюють зв'язані списки в кожній комірці і формальна межа заповнення може перевищувати 100%, у відкритій адресації межа Діріхле є жорстким апаратним бар'єром.

Нижче наведено робочий код хеш-таблиці з лінійним зондуванням, який демонструє підрахунок колізій та спрацювання жорсткої межі Діріхле при спробі переповнення.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int key;
    int value;
    int occupied;
} HashEntry;

typedef struct {
    HashEntry* entries;
    size_t capacity;
    size_t count;
} HashTable;

HashTable* hashtable_create(size_t capacity) {
    HashTable* table = (HashTable*)malloc(sizeof(HashTable));
    if (!table) return NULL;

    table->entries = (HashEntry*)calloc(capacity, sizeof(HashEntry));
    table->capacity = capacity;
    table->count = 0;
    return table;
}

void hashtable_free(HashTable* table) {
    if (table) {
        free(table->entries);
        free(table);
    }
}

int hashtable_insert(HashTable* table, int key, int value, size_t* probe_collisions) {
    if (!table || table->count >= table->capacity) {
        // Межа Діріхле: n = capacity + 1 об'єктів не можна вставити в capacity комірок!
        return 0; 
    }

    size_t hash = (size_t)((unsigned int)key % table->capacity);
    size_t idx = hash;
    size_t collisions = 0;

    while (table->entries[idx].occupied) {
        if (table->entries[idx].key == key) {
            table->entries[idx].value = value; // Оновлення значення
            if (probe_collisions) *probe_collisions = collisions;
            return 1;
        }
        collisions++;
        idx = (idx + 1) % table->capacity;
    }

    table->entries[idx].key = key;
    table->entries[idx].value = value;
    table->entries[idx].occupied = 1;
    table->count++;

    if (probe_collisions) *probe_collisions = collisions;
    return 1;
}

int main(void) {
    size_t capacity = 5;
    HashTable* ht = hashtable_create(capacity);

    printf("=== Аналіз колізій у хеш-таблиці ємністю M = %zu ===\n", capacity);
    int keys[] = { 10, 15, 20, 25, 30, 35 };

    for (size_t i = 0; i < sizeof(keys)/sizeof(keys[0]); ++i) {
        size_t col = 0;
        int ok = hashtable_insert(ht, keys[i], (int)(i + 1) * 100, &col);
        if (ok) {
            printf("Ключ %2d вставлено (колізій зондування: %zu). Елементів у таблиці: %zu/%zu\n",
                   keys[i], col, ht->count, ht->capacity);
        } else {
            printf("Ключ %2d ВІДХИЛЕНО: Межа Діріхле! Таблиця повна (%zu/%zu)\n",
                   keys[i], ht->count, ht->capacity);
        }
    }

    hashtable_free(ht);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <optional>

class LinearProbingHashTable {
    struct Entry {
        int key;
        int value;
        bool occupied{false};
    };

    std::vector<Entry> entries_;
    size_t count_{0};

public:
    explicit LinearProbingHashTable(size_t capacity) : entries_(capacity) {}

    bool insert(int key, int value, size_t& collision_count) {
        if (count_ >= entries_.size()) {
            // За принципом Діріхле таблиця повна — вставка неможлива без розширення
            return false;
        }

        size_t hash = static_cast<size_t>(key) % entries_.size();
        size_t idx = hash;
        collision_count = 0;

        while (entries_[idx].occupied) {
            if (entries_[idx].key == key) {
                entries_[idx].value = value;
                return true;
            }
            collision_count++;
            idx = (idx + 1) % entries_.size();
        }

        entries_[idx] = {key, value, true};
        count_++;
        return true;
    }

    [[nodiscard]] size_t size() const { return count_; }
    [[nodiscard]] size_t capacity() const { return entries_.size(); }
};

int main() {
    const size_t capacity = 5;
    LinearProbingHashTable ht(capacity);

    std::cout << "=== Хеш-таблиця з відкритою адресацією (M = " << capacity << ") ===\n";
    const std::vector<int> keys = { 10, 15, 20, 25, 30, 35 };

    for (size_t i = 0; i < keys.size(); ++i) {
        size_t collisions = 0;
        if (ht.insert(keys[i], static_cast<int>(i + 1) * 100, collisions)) {
            std::cout << "Ключ " << keys[i] << " додано (колізій: " << collisions 
                      << "). Заповнення: " << ht.size() << "/" << ht.capacity() << "\n";
        } else {
            std::cout << "Ключ " << keys[i] << " ВІДХИЛЕНО: спрацювала межа Діріхле! ("
                      << ht.size() << "/" << ht.capacity() << ")\n";
        }
    }
    return 0;
}
```
:::

---

## Задача 5: Детекція хеш-колізій у підрядковому пошуку Рабіна-Карпа

### Колізії ковзного хешу

В алгоритмі Рабіна-Карпа підрядок довжиною `M` шукається у тексті довжиною `N` за допомогою обчислення кільцевого (ковзного) хешу по модулю `P`.

Оскільки кількість можливих текстових вікон довжиною `M` у алфавіті розміру `Σ` дорівнює `|Σ|^M`, а можливих хеш-значень за модулем `P` лише `P` варіантів, якщо `|Σ|^M > P`, за принципом Діріхле **хибні спрацювання (колізії Діріхле)** є математично неминучими.

Математична структура ковзного хешу спирається на поліноміальне обчислення `H(S) = (S[0]·B^{M-1} + S[1]·B^{M-2} + ... + S[M-1]) mod P`. При переході до наступного вікна додається новий символ і віднімається старший символ за `O(1)` операцій. Але оскільки область значень хеш-функції обмежена модулем `P`, збіг хешів гарантує лише *потенційну* наявність паттерна. 

Це диктує необхідність обов'язкового посимвольного порівняння рядків кожного разу, коли значення ковзного хешу збігається з хешем паттерна.

:::tabs
```c
#include <stdio.h>
#include <string.h>

#define BASE 256
#define MOD 101 // Просте число для модуля

void rabin_karp_search(const char* pat, const char* txt) {
    size_t m = strlen(pat);
    size_t n = strlen(txt);
    if (m > n || m == 0) return;

    long long p_hash = 0;
    long long t_hash = 0;
    long long h = 1;

    for (size_t i = 0; i < m - 1; ++i) {
        h = (h * BASE) % MOD;
    }

    for (size_t i = 0; i < m; ++i) {
        p_hash = (BASE * p_hash + pat[i]) % MOD;
        t_hash = (BASE * t_hash + txt[i]) % MOD;
    }

    for (size_t i = 0; i <= n - m; ++i) {
        if (p_hash == t_hash) {
            // Перевірка на справжній збіг чи колізію Діріхле
            if (strncmp(txt + i, pat, m) == 0) {
                printf("Знайдено паттерн на індексі %zu\n", i);
            } else {
                printf("Хибна колізія Діріхле на індексі %zu!\n", i);
            }
        }
        if (i < n - m) {
            t_hash = (BASE * (t_hash - txt[i] * h) + txt[i + m]) % MOD;
            if (t_hash < 0) t_hash += MOD;
        }
    }
}

int main(void) {
    const char* text = "ABABDABACDABABCABAB";
    const char* pattern = "ABABC";
    rabin_karp_search(pattern, text);
    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <vector>

void rabin_karp_search(std::string_view pat, std::string_view txt) {
    const size_t m = pat.size();
    const size_t n = txt.size();
    if (m > n || m == 0) return;

    constexpr long long base = 256;
    constexpr long long mod = 101;

    long long p_hash = 0;
    long long t_hash = 0;
    long long h = 1;

    for (size_t i = 0; i < m - 1; ++i) {
        h = (h * base) % mod;
    }

    for (size_t i = 0; i < m; ++i) {
        p_hash = (base * p_hash + pat[i]) % mod;
        t_hash = (base * t_hash + txt[i]) % mod;
    }

    for (size_t i = 0; i <= n - m; ++i) {
        if (p_hash == t_hash) {
            if (txt.substr(i, m) == pat) {
                std::cout << "Точний збіг на позиції: " << i << "\n";
            } else {
                std::cout << "Колізія хешу Діріхле на позиції: " << i << "\n";
            }
        }
        if (i < n - m) {
            t_hash = (base * (t_hash - txt[i] * h) + txt[i + m]) % mod;
            if (t_hash < 0) t_hash += mod;
        }
    }
}

int main() {
    std::string_view text = "ABABDABACDABABCABAB";
    std::string_view pattern = "ABABC";
    rabin_karp_search(pattern, text);
    return 0;
}
```
:::

---

## Задача 6: Хибні позитивні спрацьовування у фільтрі Блума

### Простір бітових комірок та колізії

Фільтр Блума (Bloom Filter) — це ймовірнісна структура даних для швидкої перевірки належності елемента множині. Вона складається з бітового масиву розміром `M` та `k` незалежних хеш-функцій.

Під час додавання елемента `x` обчислиться `k` хеш-значень `h₁(x), h₂(x), ..., h_k(x) mod M`, і відповідні біти в масиві встановлюються в `1`.

Оскільки кількість можливих доданих елементів `N` зростає, а кількість бітів `M` обмежена, за узагальненим принципом Діріхле середній ступінь заповнення бітового масиву перевищує `1 - (1 - 1/M)^{k N}`. Як тільки більшість бітів стають рівними `1`, виникає колізія комірок: сторонній елемент `y` може дати хеш-значення, усі біти яких вже були встановлені раніше іншими елементами! Це викликає **хибне позитивне спрацьовування (false positive)**.

Оскільки фільтр Блума не зберігає самі елементи, а лише простір з `M` бітових комірок, розробники мусять враховувати неминучість спрацьовування принципу комірок при перевищенні обсягу записів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>

#define BLOOM_SIZE 16

typedef struct {
    unsigned char bits[BLOOM_SIZE / 8];
} BloomFilter;

void bloom_add(BloomFilter* bf, int val) {
    int h1 = (val * 7 + 3) % BLOOM_SIZE;
    int h2 = (val * 13 + 5) % BLOOM_SIZE;
    bf->bits[h1 / 8] |= (1 << (h1 % 8));
    bf->bits[h2 / 8] |= (1 << (h2 % 8));
}

int bloom_check(const BloomFilter* bf, int val) {
    int h1 = (val * 7 + 3) % BLOOM_SIZE;
    int h2 = (val * 13 + 5) % BLOOM_SIZE;
    int bit1 = (bf->bits[h1 / 8] >> (h1 % 8)) & 1;
    int bit2 = (bf->bits[h2 / 8] >> (h2 % 8)) & 1;
    return bit1 && bit2;
}

int main(void) {
    BloomFilter bf = {{0}};
    printf("=== Фільтр Блума: M = %d бітів ===\n", BLOOM_SIZE);
    int elements[] = { 1, 4, 9, 12, 15 };

    for (size_t i = 0; i < 5; ++i) {
        bloom_add(&bf, elements[i]);
    }

    // Перевірка елемента, якого НЕ додавали (тест колізії Діріхле)
    int test_val = 7;
    if (bloom_check(&bf, test_val)) {
        printf("Елемент %d не додавався, але фільтр каже 'присутній' (колізія Блума/Діріхле!)\n", test_val);
    } else {
        printf("Елемент %d відсутній.\n", test_val);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>

class SimpleBloomFilter {
    std::array<bool, 16> bits_{};

public:
    void add(int val) {
        size_t h1 = static_cast<size_t>((val * 7 + 3) % 16);
        size_t h2 = static_cast<size_t>((val * 13 + 5) % 16);
        bits_[h1] = true;
        bits_[h2] = true;
    }

    [[nodiscard]] bool contains(int val) const {
        size_t h1 = static_cast<size_t>((val * 7 + 3) % 16);
        size_t h2 = static_cast<size_t>((val * 13 + 5) % 16);
        return bits_[h1] && bits_[h2];
    }
};

int main() {
    SimpleBloomFilter bf;
    std::cout << "=== Перевірка колізій у фільтрі Блума ===\n";
    for (int v : {1, 4, 9, 12, 15}) bf.add(v);

    int test_val = 7;
    if (bf.contains(test_val)) {
        std::cout << "Елемент " << test_val 
                  << " викликав хибне позитивне спрацьовування за принципом Діріхле!\n";
    }
    return 0;
}
```
:::

---

## Задача 7: Аналіз колізій у криптографічних хеш-функціях та атака "днів народження"

### Неминучість колізій у скінченних криптографічних дайджестах

У криптографії хеш-функція (наприклад, MD5 з дайджестом 128 бітів або SHA-256 з дайджестом 256 бітів) приймає повідомлення довільної довжини і повертає хеш-значення фіксованої довжини `B` бітів.

Кількість можливих вхідних повідомлень довжиною до `N` бітів становить `2⁰ + 2¹ + ... + 2ᴺ = 2ᴺ⁺¹ - 1`. Оскільки кількість вихідних хеш-значень обмежена `2ℬ`, за принципом Діріхле існує нескінченна кількість пар різних повідомлень `M₁ ≠ M₂`, які мають однаковий хеш `H(M₁) = H(M₂)`.

Для дайджесту `B = 128` бітів принцип Діріхле гарантує, що серед будь-яких `2¹²⁸ + 1` повідомлень знайдеться колізійна пара. Ймовірнісна атака «днів народження» знижує цю межу до `2⁶⁴` операцій, проте фундаментальною причиною існування колізій є саме принцип комірок.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>

// Спрощена 16-бітна хеш-функція для демонстрації колізій Діріхле у криптографії
uint16_t simple_16bit_hash(const char* str) {
    uint16_t hash = 0x5555;
    while (*str) {
        hash ^= (uint16_t)(*str++);
        hash = (uint16_t)((hash << 5) | (hash >> 11)); // Циклічний зсув
    }
    return hash;
}

int main(void) {
    printf("=== Криптографічний аналіз: 16-бітний простір комірок ===\n");
    printf("Кількість унікальних 16-бітних хеш-кодів (комірок): %d\n", 1 << 16);
    printf("За принципом Діріхле, будь-яка множина з %d повідомлень\n", (1 << 16) + 1);
    printf("гарантовано містить принаймні одну криптографічну колізію!\n");

    const char* msg1 = "Message-A";
    const char* msg2 = "Message-B";
    printf("Хеш('%s') = 0x%04X\n", msg1, simple_16bit_hash(msg1));
    printf("Хеш('%s') = 0x%04X\n", msg2, simple_16bit_hash(msg2));
    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <cstdint>

uint16_t simple_16bit_hash(std::string_view str) {
    uint16_t hash = 0x5555;
    for (char ch : str) {
        hash ^= static_cast<uint16_t>(ch);
        hash = static_cast<uint16_t>((hash << 5) | (hash >> 11));
    }
    return hash;
}

int main() {
    constexpr uint32_t cell_count = 1 << 16;
    std::cout << "=== 16-бітний простір криптографічних комірок ===\n";
    std::cout << "Доступно комірок: " << cell_count << "\n";
    std::cout << "Межа Діріхле для 100% гарантії колізії: " << cell_count + 1 << " входів\n";

    std::string_view msg1 = "Message-A";
    std::string_view msg2 = "Message-B";
    std::cout << "Hash('" << msg1 << "') = 0x" << std::hex << simple_16bit_hash(msg1) << "\n";
    std::cout << "Hash('" << msg2 << "') = 0x" << std::hex << simple_16bit_hash(msg2) << "\n";
    return 0;
}
```
:::

---

## Задача 8: Неминучість витиснення елементів у процесорному кеші (L1/L2/L3)

### Апаратна асоціативність кеш-пам'яті

Апаратний кеш процесора (Cache line) має скінченну кількість набірно-асоціативних ліній (Set associative cache). Наприклад, у 8-канальному кеші L1 одна лінія кешу може містити точно `8` блоків пам'яті (комірок).

Якщо програма звертається до `9` різних адрес у оперативній пам'яті, які відображаються в один і той самий кеш-набір (за модулем розміру кеш-набору), за принципом Діріхле **принаймні один з елементів буде витиснений (Cache Conflict Eviction)**.

Це фундаментальне пояснення того, чому при крокуванні по масиву з кроком, кратним степеню двійки (наприклад, 4096 байтів), швидкодія процесора резко падає через масові колізії Діріхле у наборах кешу. Архітектори процесорів (x86, ARM, RISC-V) змушені застосовувати псевдовипадкову індексацію наборів кешу (skewed associative cache), щоб пом'якшити цей ефект.

:::tabs
```c
#include <stdio.h>

void simulate_cache_eviction(size_t cache_ways, size_t access_count) {
    printf("=== Кеш L1 (асоціативність: %zu шляхів) ===\n", cache_ways);
    printf("Спроба завантажити %zu блоків пам'яті в той самий кеш-набор:\n", access_count);

    if (access_count > cache_ways) {
        printf("РЕЗУЛЬТАТ: За принципом Діріхле, %zu блоків не вміщаються в %zu комірок.\n",
               access_count, cache_ways);
        printf("Виникає неминуче витиснення (Thrashing/Eviction) принаймні %zu блоків!\n",
               access_count - cache_ways);
    }
}

int main(void) {
    simulate_cache_eviction(8, 9);
    return 0;
}
```
```cpp
#include <iostream>

void simulate_cache_eviction(size_t cache_ways, size_t access_count) {
    std::cout << "=== Кеш L1 (" << cache_ways << "-way associative) ===\n";
    if (access_count > cache_ways) {
        std::cout << "За принципом Діріхле " << access_count << " адрес > " 
                  << cache_ways << " слотів кешу.\n"
                  << "Витиснення ліній кешу математично НЕМОЖЛИВО уникнути!\n";
    }
}

int main() {
    simulate_cache_eviction(8, 9);
    return 0;
}
```
:::

---

## Задача 9: Доказ неможливості універсального стиснення без втрат

### Обчислювальний аналіз потужностей бінарних просторів

Багато розробників початківців мріють створити алгоритм стиснення, який здатний зменшити розмір будь-якого довільного файлу. За допомогою принципу Діріхле ми можемо програмно довести, що такий алгоритм є математично неможливим.

Розглянемо множину всіх бінарних файлів фіксованої довжини `N` бітів. Кількість таких унікальних файлів дорівнює:

```
|Input_N| = 2ᴺ
```

Якщо алгоритм є універсальним і стискає **кожен** з цих `2ᴺ` файлів без втрат, вихідний стиснений файл повинен мати довжину строго меншу за `N` бітів (тобто від `0` до `N - 1` бітів).

Порахуємо загальну кількість усіх можливих бінарних послідовностей довжиною менше `N` бітів:

```
|Output_<N| = ∑_{k=0}^{N-1} 2ᵏ  =  2⁰ + 2¹ + 2² + ... + 2ᴺ⁻¹  =  2ᴺ - 1
```

Маємо:
- Кількість входів (об'єктів): `2ᴺ`
- Кількість доступних кодів (комірок): `2ᴺ - 1`

Оскільки `2ᴺ > 2ᴺ - 1`, за принципом Діріхле принаймні два різних вхідних файли `X₁ ≠ X₂` отримають **абсолютно однаковий стиснений код** `C(X₁) = C(X₂)`. Але це унеможливлює зворотне однозначне розпакування `D(C(X))`, оскільки декомпресор не зможе визначити, який із двох початкових файлів слід відновити!

Теоретико-інформаційний зміст цієї нерівності полягає в тому, що ентропія рівномірно-випадкового джерела є максимальною. Алгоритми стиснення без втрат (Huffman, LZ77, Zstandard) здатні зменшувати розмір лише тих файлів, ентропія яких строго менша за розмір файлу, збільшуючи при цьому довжину випадкових чи вже стиснених файлів. З погляду складності Колмогорова, нестисливими є ті файли, довжина найкоротшої програми для генерації яких дорівнює розміру самого файлу.

Нижче наведено програму, яка розраховує потужності вхідних та вихідних просторів і демонструє неминучу появу колізій при спробі універсального стиснення.

:::tabs
```c
#include <stdio.h>
#include <math.h>

void verify_compression_pigeonhole(unsigned int n_bits) {
    if (n_bits >= 30) {
        printf("Розмір N = %u занадто великий для обчислення 64-бітними числами.\n", n_bits);
        return;
    }

    // 2^N вхідних комбінацій
    unsigned long long input_space_size = 1ULL << n_bits;           
    // Сума 2^k для k від 0 до N-1 дорівнює 2^N - 1
    unsigned long long output_space_size = input_space_size - 1;    

    printf("=== Аналіз універсального стиснення для файлів N = %u бітів ===\n", n_bits);
    printf("Кількість унікальних вхідних файлів (2^N):   %llu\n", input_space_size);
    printf("Кількість вихідних кодів довжиною < N (2^N-1): %llu\n", output_space_size);

    if (input_space_size > output_space_size) {
        printf("ОЦІНКА: Вхідних файлів (%llu) > Вихідних комірок (%llu).\n",
               input_space_size, output_space_size);
        printf("ВИСНОВОК: За принципом Діріхле універсальне стиснення БЕЗ втрат ламається!\n");
        printf("Принаймні %llu файли отримають однаковий стиснений код (колізія).\n",
               input_space_size - output_space_size + 1);
    }
}

int main(void) {
    verify_compression_pigeonhole(3);
    printf("\n");
    verify_compression_pigeonhole(8);
    return 0;
}
```
```cpp
#include <iostream>
#include <cstdint>

void verify_compression_pigeonhole(uint32_t n_bits) {
    if (n_bits >= 62) return;

    const uint64_t input_count = 1ULL << n_bits;        // 2^N
    const uint64_t output_count = input_count - 1;      // 2^N - 1

    std::cout << "=== Перевірка принципу Діріхле для N = " << n_bits << " бітів ===\n";
    std::cout << "Вхідний простір (2^N):    " << input_count << " файлів\n";
    std::cout << "Вихідний простір (< N):   " << output_count << " слотів\n";

    if (input_count > output_count) {
        std::cout << "ВИСНОВОК: За принципом Діріхле (n > k), універсальне стиснення\n"
                  << "без втрат математично НЕДОСЯЖНЕ. Спроба стиснути всі "
                  << input_count << " файлів створить принаймні 1 колізію.\n";
    }
}

int main() {
    verify_compression_pigeonhole(4);
    std::cout << "\n";
    verify_compression_pigeonhole(16);
    return 0;
}
```
:::
