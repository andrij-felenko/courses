# ⚙️ Практична реалізація Timsort: від ідентифікації серій до галопу

Реалізація адаптивного гібридного сортування вимагає не лише знання асимптотичних формул, а й точного узгодження багатьох низькорівневих компонентів: акуратного виділення тимчасового буфера, безпечної роботи з сирими вказівниками пам'яті, коректної підтримки інваріантів стека серій та швидкого перемикання між покроковим скануванням і експоненційним пошуком. Помилка навіть в один індекс у процедурі двійкового пошуку або неврахування переповнення стека перетворює високоефективний алгоритм на джерело аварійних завершень процесу. Ця вставка містить вичерпну практичну реалізацію Timsort мовами C та C++, розбираючи крок за кроком кожну функцію — від розпізнавання природних серій до оптимізованого двостороннього злиття.

## Архітектурний каркас та структури даних

Алгоритм підтримує внутрішній стан, який включає стек дескрипторів активних серій та динамічний буфер для тимчасового збереження даних меншої серії. Кожна серія на стеку описується початковим індексом у головному масиві та своєю довжиною.

Дескриптор серії `TimSortRun` містить два числових поля: індекс початку відрізка в основному масиві (`start`) та кількість елементів у ньому (`len`). Завдяки компактному розміру (два слова по 8 байтів кожне на 64-бітній архітектурі) весь стек із 85 елементів займає менше 1.5 кілобайта пам'яті і постійно перебуває в найшвидшому регістровому кеші L1 процесора.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MIN_GALLOP_DEFAULT 7
#define MAX_STACK_SIZE 85

typedef struct {
    size_t start;
    size_t len;
} TimSortRun;

typedef struct {
    int *array;
    size_t size;
    int *temp_buf;
    size_t temp_capacity;
    size_t min_gallop;
    TimSortRun stack[MAX_STACK_SIZE];
    size_t stack_size;
} TimSortState;
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <algorithm>
#include <utility>
#include <functional>
#include <cstddef>
#include <memory>

template <typename T, typename Compare = std::less<T>>
class TimSort {
public:
    static constexpr size_t MIN_GALLOP_DEFAULT = 7;
    static constexpr size_t MAX_STACK_SIZE = 85;

    struct Run {
        size_t start;
        size_t len;
    };

    explicit TimSort(Compare comp = Compare()) 
        : comp_(comp), min_gallop_(MIN_GALLOP_DEFAULT), stack_size_(0) {}

    void sort(std::span<T> data);

private:
    Compare comp_;
    size_t min_gallop_;
    std::vector<T> temp_buf_;
    Run stack_[MAX_STACK_SIZE];
    size_t stack_size_;

    void merge_collapse(std::span<T> data);
    void merge_force_collapse(std::span<T> data);
    void merge_at(std::span<T> data, size_t i);
    void merge_lo(std::span<T> data, size_t base_a, size_t len_a, size_t base_b, size_t len_b);
    void merge_hi(std::span<T> data, size_t base_a, size_t len_a, size_t base_b, size_t len_b);
};
```
:::

У реалізації мовою C стан інкапсульовано у структуру `TimSortState`. Управління виділенням динамічної пам'яті під буфер здійснюється через функцію `ensure_temp_capacity`, яка використовує системний виклик `realloc`. Це дозволяє динамічно нарощувати тимчасовий буфер лише тоді, коли поточна довжина серії перевищує раніше виділену ємність `temp_capacity`. Оскільки розмір буфера ніколи не перевищує `N / 2`, для масиву з мільйона 32-бітних цілих чисел (4 мегабайти) максимальний розмір буфера складе лише 2 мегабайти, причому цей самий буфер багаторазово переініціалізується та перевикористовується на всіх рівнях злиття без додаткових звернень до ядра ОС.

У варіанті C++ клас `TimSort` є узагальненим шаблоном, що підтримує довільні типи даних `T` та власні функціональні об'єкти компараторів `Compare`. Використання контейнера `std::vector<T>` як тимчасового буфера забезпечує суворе дотримання ідіоми RAII (Resource Acquisition Is Initialization): пам'ять автоматично звільняється при виході з області видимості, навіть якщо під час виконання порівняння користувацький компаратор згенерує виняток. Крім того, виклик методу `std::move` замість копіювання дозволяє сортувати важкі об'єкти (наприклад, складні структури з динамічними рядками `std::string` чи вкладеними векторами) із нульовим накладним дублюванням їхнього внутрішнього динамічного вмісту.

## Розрахунок minrun та розпізнавання природних серій

Першим кроком сортування є визначення мінімальної довжини серії `minrun` на основі 6 найстарших бітів загальної кількості елементів `N`. Функція `calculate_minrun` побітово зсуває число `N` вправо, доки воно не стане меншим за 64, одночасно акумулюючи побітовим «АБО» факт наявності хоча б одного одиничного біта серед відкинутих молодших розрядів.

Наприклад, якщо `N = 2112` (у двійковому записі `100001000000₂`):
1. На першому кроці `2112 >= 64`, відкидається молодший біт 0, `r = 0`.
2. Після 5 зсувів число стає `66 >= 64`, `r = 0`.
3. На шостому зсуві число стає `33 < 64`, відкинутий біт дорівнював 0, але попередні зсуви зафіксували одиницю на 6-й позиції, тому `r = 1`.
4. Результат: `33 + 1 = 34`. Масив розбивається на `2112 / 34 ≈ 62` серії, що є числом, дуже близьким до степеня двійки 64.

Після розрахунку `minrun` алгоритм починає послідовне сканування вхідного масиву за допомогою функції `count_and_reverse_run`. Вона порівнює перший та другий елементи неперевіреної ділянки для визначення напрямку монотонності:

- Якщо `arr[start + 1] < arr[start]`, виявлено спадну послідовність. Сканування продовжується строго доти, доки кожен наступний елемент є меншим за попередній (`arr[k] < arr[k - 1]`). Знайдений відрізок негайно інвертується на місці класичним алгоритмом двох зустрічних вказівників.
- Якщо `arr[start + 1] >= arr[start]`, виявлено неспадна послідовність. Сканування триває, поки `arr[k] >= arr[k - 1]`. Цей відрізок залишається без змін.

:::tabs
```c
static size_t calculate_minrun(size_t n) {
    size_t r = 0;
    while (n >= 64) {
        r |= (n & 1);
        n >>= 1;
    }
    return n + r;
}

static size_t count_and_reverse_run(int *arr, size_t start, size_t n) {
    if (start >= n) return 0;
    if (start == n - 1) return 1;

    size_t run_len = 2;
    if (arr[start + 1] < arr[start]) {
        // Строго спадна серія: шукаємо межу, поки елементи зменшуються
        while (start + run_len < n && arr[start + run_len] < arr[start + run_len - 1]) {
            run_len++;
        }
        // Розвертаємо серію на місці
        size_t left = start;
        size_t right = start + run_len - 1;
        while (left < right) {
            int tmp = arr[left];
            arr[left] = arr[right];
            arr[right] = tmp;
            left++;
            right--;
        }
    } else {
        // Неспадна серія
        while (start + run_len < n && arr[start + run_len] >= arr[start + run_len - 1]) {
            run_len++;
        }
    }
    return run_len;
}
```
```cpp
template <typename T, typename Compare>
size_t calculate_minrun_impl(size_t n) {
    size_t r = 0;
    while (n >= 64) {
        r |= (n & 1);
        n >>= 1;
    }
    return n + r;
}

template <typename T, typename Compare>
size_t count_and_reverse_run_impl(std::span<T> data, size_t start, Compare comp) {
    const size_t n = data.size();
    if (start >= n) return 0;
    if (start == n - 1) return 1;

    size_t run_len = 2;
    if (comp(data[start + 1], data[start])) {
        // Строго спадна серія
        while (start + run_len < n && comp(data[start + run_len], data[start + run_len - 1])) {
            run_len++;
        }
        std::reverse(data.begin() + start, data.begin() + start + run_len);
    } else {
        // Неспадна серія
        while (start + run_len < n && !comp(data[start + run_len], data[start + run_len - 1])) {
            run_len++;
        }
    }
    return run_len;
}
```
:::

Критично важливим нюансом реалізації є використання строгої нерівності `comp(data[start + 1], data[start])` для спадних серій. Якщо два сусідні елементи мають однакові значення (`a == b`), умова спадання повертає `false`. Це запобігає включенню дублікатів у спадну серію, яка потім інвертується: якби рівні елементи були розгорнуті, їхній початковий взаємний порядок порушився б, що зруйнувало б стійкість сортування.

## Досортовування серій сортуванням бінарними вставками

Якщо довжина природної серії `run_len` менша за `minrun`, її необхідно подовжити за рахунок наступних елементів масиву до розміру `force = min(minrun, n - start)`. Досортовування виконується процедурою `binary_insertion_sort`.

На відміну від звичайного сортування вставками, яке покроково порівнює новий елемент із кожним попереднім (`O(i)` порівнянь на ітерацію), бінарні вставки застосовують двійковий пошук точки вставки:

1. Для вставки елемента `key = arr[start + i]` виконується бінарний пошук у діапазоні `[start, start + i)`.
2. Кількість порівнянь скорочується з `i` до `⌈log₂(i + 1)⌉`.
3. Коли точний індекс `left` знайдено, всі елементи від `left` до `start + i - 1` зсуваються вправо рівно на один осередок за допомогою однієї інструкції `memmove` (або `std::move_backward` у C++).
4. Елемент `key` поміщається на звільнений осередок `arr[left]`.

:::tabs
```c
static void binary_insertion_sort(int *arr, size_t start, size_t len, size_t sorted_len) {
    for (size_t i = sorted_len; i < len; ++i) {
        int key = arr[start + i];
        // Двійковий пошук точки вставки ключа у відрізку arr[start .. start + i - 1]
        size_t left = start;
        size_t right = start + i;
        while (left < right) {
            size_t mid = left + (right - left) / 2;
            if (key < arr[mid]) {
                right = mid;
            } else {
                left = mid + 1; // Забезпечує стійкість (стабільність) сортування
            }
        }
        // Зсуваємо елементи праворуч для звільнення осередку на позиції left
        size_t count = (start + i) - left;
        if (count > 0) {
            memmove(&arr[left + 1], &arr[left], count * sizeof(int));
        }
        arr[left] = key;
    }
}
```
```cpp
template <typename T, typename Compare>
void binary_insertion_sort_impl(std::span<T> data, size_t start, size_t len, size_t sorted_len, Compare comp) {
    for (size_t i = sorted_len; i < len; ++i) {
        T key = std::move(data[start + i]);
        // Двійковий пошук правої межі (upper_bound) для збереження стійкості
        auto it = std::upper_bound(data.begin() + start, data.begin() + start + i, key, comp);
        size_t insert_pos = std::distance(data.begin(), it);
        
        // Зсув елементів вправо
        std::move_backward(data.begin() + insert_pos, data.begin() + start + i, data.begin() + start + i + 1);
        data[insert_pos] = std::move(key);
    }
}
```
:::

Зверніть увагу на гілку `else { left = mid + 1; }`: якщо ключ `key` дорівнює елементу `arr[mid]`, межа пошуку зсувається вправо. Це еквівалентно функції `std::upper_bound` і гарантує, що новий елемент буде розміщено строго **після** всіх уже наявних еквівалентних ключів, зберігаючи початковий хронологічний порядок додавання записів.

## Підтримання інваріантів стека серій

Коли серія довжиною не менше `minrun` сформована, її дескриптор `(start, len)` поміщається на вершину стека `stack`. Після кожного додавання викликається функція `merge_collapse`, яка перевіряє стан серій і за потреби виконує злиття.

Сучасна виправлена версія алгоритму (після формальної верифікації 2015 року) перевіряє до чотирьох верхніх серій на стеку:

```
Нехай n = stack_size - 2 (індекс передостаннього елемента).
Перевіряються умови:
1. n >= 1 та len[n-1] <= len[n] + len[n+1]
2. n >= 2 та len[n-2] <= len[n-1] + len[n]
3. len[n] <= len[n+1]
```

Якщо порушено першу або другу умову, алгоритм обирає, яку пару серій вигідніше злити: якщо `len[n-1] < len[n+1]`, зливається пара `(n-1, n)`, інакше — пара `(n, n+1)`. Якщо порушено третю умову, зливається пара `(n, n+1)`. Злиття повторюється в циклі `while (stack_size > 1)`, доки всі інваріанти не будуть повністю задоволені.

:::tabs
```c
static void merge_at(TimSortState *state, size_t i);

static void merge_collapse(TimSortState *state) {
    while (state->stack_size > 1) {
        size_t n = state->stack_size - 2;

        if ((n >= 1 && state->stack[n - 1].len <= state->stack[n].len + state->stack[n + 1].len) ||
            (n >= 2 && state->stack[n - 2].len <= state->stack[n - 1].len + state->stack[n].len)) {
            if (state->stack[n - 1].len < state->stack[n + 1].len) {
                n--;
            }
            merge_at(state, n);
        } else if (state->stack[n].len <= state->stack[n + 1].len) {
            merge_at(state, n);
        } else {
            break; // Всі інваріанти задоволено
        }
    }
}

static void merge_force_collapse(TimSortState *state) {
    while (state->stack_size > 1) {
        size_t n = state->stack_size - 2;
        if (n > 0 && state->stack[n - 1].len < state->stack[n + 1].len) {
            n--;
        }
        merge_at(state, n);
    }
}
```
```cpp
template <typename T, typename Compare>
void TimSort<T, Compare>::merge_collapse(std::span<T> data) {
    while (stack_size_ > 1) {
        size_t n = stack_size_ - 2;

        if ((n >= 1 && stack_[n - 1].len <= stack_[n].len + stack_[n + 1].len) ||
            (n >= 2 && stack_[n - 2].len <= stack_[n - 1].len + stack_[n].len)) {
            if (stack_[n - 1].len < stack_[n + 1].len) {
                n--;
            }
            merge_at(data, n);
        } else if (stack_[n].len <= stack_[n + 1].len) {
            merge_at(data, n);
        } else {
            break;
        }
    }
}

template <typename T, typename Compare>
void TimSort<T, Compare>::merge_force_collapse(std::span<T> data) {
    while (stack_size_ > 1) {
        size_t n = stack_size_ - 2;
        if (n > 0 && stack_[n - 1].len < stack_[n + 1].len) {
            n--;
        }
        merge_at(data, n);
    }
}
```
:::

Процедура `merge_force_collapse` викликається на самомуприкінці сортування, коли вхідний масив вичерпано. Вона примусово зливає всі дескриптори, що залишилися на стеку, доки стек не стиснеться до єдиної серії, яка покриває весь вхідний масив від індексу `0` до `N - 1`.

## Алгоритм експоненційного пошуку (Галоп)

Під час злиття двох серій часто виникає ситуація, коли одна серія містить довгий суцільний блок елементів, які всі менші за перший елемент іншої серії. У такому разі покрокове порівняння кожного елемента стає неефективним.

Процедура `gallop_right` знаходить точну точку вставки ключа `key` у відсортованому відрізку `arr[base .. base + len - 1]`, починаючи від заданого початкового зсуву `hint`. Алгоритм виконується у дві фази:

1. **Фаза експоненційних стрибків:** Алгоритм перевіряє зміщення `ofs = 1, 3, 7, 15, 31, ..., 2^k - 1`. Стрибки подвоюються на кожному кроці, поки значення в масиві не перевищить `key` або не буде досягнуто кінця діапазону `len`.
2. **Фаза бінарного звуження:** Попередній крок обмежив положення ключа відрізком `[base + last_ofs, base + ofs)`. Усередині цього невеликого відрізка викликається класичний двійковий пошук, який за `O(log(ofs - last_ofs))` кроків повертає точний підсумковий індекс.

Процедура `gallop_left` є дзеркальним двійником `gallop_right`: вона шукає першу позицію вставки з умовою строгої нерівності (`key <= arr[i]`), що критично необхідно при зворотній фазі злиття `merge_hi`.

:::tabs
```c
static size_t gallop_right(int key, const int *arr, size_t base, size_t len, size_t hint) {
    size_t ofs = 1;
    size_t last_ofs = 0;

    if (key < arr[base + hint]) {
        // Галоп вліво від позиції hint
        size_t max_ofs = hint + 1;
        while (ofs < max_ofs && key < arr[base + hint - ofs]) {
            last_ofs = ofs;
            ofs = (ofs << 1) + 1;
        }
        if (ofs > max_ofs) ofs = max_ofs;

        size_t tmp = last_ofs;
        last_ofs = hint + 1 - ofs;
        ofs = hint + 1 - tmp;
    } else {
        // Галоп вправо від позиції hint
        size_t max_ofs = len - hint;
        while (ofs < max_ofs && key >= arr[base + hint + ofs]) {
            last_ofs = ofs;
            ofs = (ofs << 1) + 1;
        }
        if (ofs > max_ofs) ofs = max_ofs;

        last_ofs += hint;
        ofs += hint;
    }

    // Двійковий пошук у локалізованому діапазоні [last_ofs, ofs)
    last_ofs++;
    while (last_ofs < ofs) {
        size_t m = last_ofs + (ofs - last_ofs) / 2;
        if (key < arr[base + m]) {
            ofs = m;
        } else {
            last_ofs = m + 1;
        }
    }
    return ofs;
}

static size_t gallop_left(int key, const int *arr, size_t base, size_t len, size_t hint) {
    size_t ofs = 1;
    size_t last_ofs = 0;

    if (key <= arr[base + hint]) {
        size_t max_ofs = hint + 1;
        while (ofs < max_ofs && key <= arr[base + hint - ofs]) {
            last_ofs = ofs;
            ofs = (ofs << 1) + 1;
        }
        if (ofs > max_ofs) ofs = max_ofs;

        size_t tmp = last_ofs;
        last_ofs = hint + 1 - ofs;
        ofs = hint + 1 - tmp;
    } else {
        size_t max_ofs = len - hint;
        while (ofs < max_ofs && key > arr[base + hint + ofs]) {
            last_ofs = ofs;
            ofs = (ofs << 1) + 1;
        }
        if (ofs > max_ofs) ofs = max_ofs;

        last_ofs += hint;
        ofs += hint;
    }

    last_ofs++;
    while (last_ofs < ofs) {
        size_t m = last_ofs + (ofs - last_ofs) / 2;
        if (key <= arr[base + m]) {
            ofs = m;
        } else {
            last_ofs = m + 1;
        }
    }
    return ofs;
}
```
```cpp
template <typename T, typename Compare>
size_t gallop_right_impl(const T &key, std::span<const T> arr, size_t base, size_t len, size_t hint, Compare comp) {
    size_t ofs = 1;
    size_t last_ofs = 0;

    if (comp(key, arr[base + hint])) {
        size_t max_ofs = hint + 1;
        while (ofs < max_ofs && comp(key, arr[base + hint - ofs])) {
            last_ofs = ofs;
            ofs = (ofs << 1) + 1;
        }
        if (ofs > max_ofs) ofs = max_ofs;

        size_t tmp = last_ofs;
        last_ofs = hint + 1 - ofs;
        ofs = hint + 1 - tmp;
    } else {
        size_t max_ofs = len - hint;
        while (ofs < max_ofs && !comp(key, arr[base + hint + ofs])) {
            last_ofs = ofs;
            ofs = (ofs << 1) + 1;
        }
        if (ofs > max_ofs) ofs = max_ofs;

        last_ofs += hint;
        ofs += hint;
    }

    last_ofs++;
    while (last_ofs < ofs) {
        size_t m = last_ofs + (ofs - last_ofs) / 2;
        if (comp(key, arr[base + m])) {
            ofs = m;
        } else {
            last_ofs = m + 1;
        }
    }
    return ofs;
}

template <typename T, typename Compare>
size_t gallop_left_impl(const T &key, std::span<const T> arr, size_t base, size_t len, size_t hint, Compare comp) {
    size_t ofs = 1;
    size_t last_ofs = 0;

    if (!comp(arr[base + hint], key)) {
        size_t max_ofs = hint + 1;
        while (ofs < max_ofs && !comp(arr[base + hint - ofs], key)) {
            last_ofs = ofs;
            ofs = (ofs << 1) + 1;
        }
        if (ofs > max_ofs) ofs = max_ofs;

        size_t tmp = last_ofs;
        last_ofs = hint + 1 - ofs;
        ofs = hint + 1 - tmp;
    } else {
        size_t max_ofs = len - hint;
        while (ofs < max_ofs && comp(arr[base + hint + ofs], key)) {
            last_ofs = ofs;
            ofs = (ofs << 1) + 1;
        }
        if (ofs > max_ofs) ofs = max_ofs;

        last_ofs += hint;
        ofs += hint;
    }

    last_ofs++;
    while (last_ofs < ofs) {
        size_t m = last_ofs + (ofs - last_ofs) / 2;
        if (!comp(arr[base + m], key)) {
            ofs = m;
        } else {
            last_ofs = m + 1;
        }
    }
    return ofs;
}
```
:::

## Двостороннє злиття: детальний розбір merge_lo та merge_hi

Функція `merge_at` координує злиття двох сусідніх серій на стеку з індексами `i` та `i + 1`:

1. **Попередня оптимізація меж:**
   - Алгоритм шукає перший елемент серії `B` всередині серії `A` через `gallop_right`. Усі елементи `A`, що передують цій точці, вже менші за будь-який елемент `B` і стоять на остаточних місцях (`base_a += k; len_a -= k;`).
   - Алгоритм шукає останній елемент серії `A` всередині серії `B` через `gallop_left`. Усі елементи `B`, що стоять правіше, вже більші за будь-який елемент `A` і виключаються з діапазону злиття (`len_b = k;`).
2. **Вибір напрямку злиття:**
   - Якщо `len(A) <= len(B)`, викликається `merge_lo`: ліва менша серія `A` копіюється у тимчасовий буфер, а злиття йде зліва направо.
   - Якщо `len(B) < len(A)`, викликається `merge_hi`: права менша серія `B` копіюється у буфер, а злиття йде справа наліво.

У процедурі `merge_hi` обробка ведеться від старших індексів до молодших. Вказівник `dest` встановлюється на кінець об'єднаного діапазону `base_b + len_b - 1`. Елементи з масиву `A` та тимчасового буфера `temp_buf` порівнюються, і більший елемент записується у позицію `dest--`.

:::tabs
```c
static void ensure_temp_capacity(TimSortState *state, size_t needed) {
    if (state->temp_capacity < needed) {
        state->temp_buf = (int *)realloc(state->temp_buf, needed * sizeof(int));
        state->temp_capacity = needed;
    }
}

static void merge_lo(TimSortState *state, size_t base_a, size_t len_a, size_t base_b, size_t len_b) {
    ensure_temp_capacity(state, len_a);
    memcpy(state->temp_buf, &state->array[base_a], len_a * sizeof(int));

    size_t cursor_a = 0;
    size_t cursor_b = base_b;
    size_t dest = base_a;
    size_t min_gallop = state->min_gallop;

    while (cursor_a < len_a && cursor_b < base_b + len_b) {
        size_t count_a = 0;
        size_t count_b = 0;

        // Покроковий режим
        do {
            if (state->array[cursor_b] < state->temp_buf[cursor_a]) {
                state->array[dest++] = state->array[cursor_b++];
                count_b++;
                count_a = 0;
                if (cursor_b == base_b + len_b) goto outer_lo;
            } else {
                state->array[dest++] = state->temp_buf[cursor_a++];
                count_a++;
                count_b = 0;
                if (cursor_a == len_a) goto outer_lo;
            }
        } while ((count_a | count_b) < min_gallop);

        // Режим галопу
        do {
            count_a = gallop_right(state->array[cursor_b], state->temp_buf, cursor_a, len_a - cursor_a, 0);
            if (count_a > 0) {
                memcpy(&state->array[dest], &state->temp_buf[cursor_a], count_a * sizeof(int));
                dest += count_a;
                cursor_a += count_a;
                if (cursor_a == len_a) goto outer_lo;
            }
            state->array[dest++] = state->array[cursor_b++];
            if (cursor_b == base_b + len_b) goto outer_lo;

            count_b = gallop_left(state->temp_buf[cursor_a], state->array, cursor_b, base_b + len_b - cursor_b, 0);
            if (count_b > 0) {
                memmove(&state->array[dest], &state->array[cursor_b], count_b * sizeof(int));
                dest += count_b;
                cursor_b += count_b;
                if (cursor_b == base_b + len_b) goto outer_lo;
            }
            state->array[dest++] = state->temp_buf[cursor_a++];
            if (cursor_a == len_a) goto outer_lo;

            min_gallop--;
        } while (count_a >= MIN_GALLOP_DEFAULT || count_b >= MIN_GALLOP_DEFAULT);

        if (min_gallop < 1) min_gallop = 1;
        min_gallop += 2; // Штраф за вихід із галопу
    }

outer_lo:
    state->min_gallop = (min_gallop < 1) ? 1 : min_gallop;
    if (cursor_a < len_a) {
        memcpy(&state->array[dest], &state->temp_buf[cursor_a], (len_a - cursor_a) * sizeof(int));
    }
}

static void merge_hi(TimSortState *state, size_t base_a, size_t len_a, size_t base_b, size_t len_b) {
    ensure_temp_capacity(state, len_b);
    memcpy(state->temp_buf, &state->array[base_b], len_b * sizeof(int));

    size_t cursor_a = base_a + len_a - 1;
    size_t cursor_b = len_b - 1;
    size_t dest = base_b + len_b - 1;
    size_t min_gallop = state->min_gallop;

    while (len_a > 0 && len_b > 0) {
        size_t count_a = 0;
        size_t count_b = 0;

        do {
            if (state->temp_buf[cursor_b] < state->array[cursor_a]) {
                state->array[dest--] = state->array[cursor_a--];
                len_a--;
                count_a++;
                count_b = 0;
                if (len_a == 0) goto outer_hi;
            } else {
                state->array[dest--] = state->temp_buf[cursor_b--];
                len_b--;
                count_b++;
                count_a = 0;
                if (len_b == 0) goto outer_hi;
            }
        } while ((count_a | count_b) < min_gallop);

        do {
            count_a = len_a - gallop_right(state->temp_buf[cursor_b], state->array, base_a, len_a, len_a - 1);
            if (count_a > 0) {
                dest -= count_a;
                cursor_a -= count_a;
                len_a -= count_a;
                memmove(&state->array[dest + 1], &state->array[cursor_a + 1], count_a * sizeof(int));
                if (len_a == 0) goto outer_hi;
            }
            state->array[dest--] = state->temp_buf[cursor_b--];
            len_b--;
            if (len_b == 0) goto outer_hi;

            count_b = len_b - gallop_left(state->array[cursor_a], state->temp_buf, 0, len_b, len_b - 1);
            if (count_b > 0) {
                dest -= count_b;
                cursor_b -= count_b;
                len_b -= count_b;
                memcpy(&state->array[dest + 1], &state->temp_buf[cursor_b + 1], count_b * sizeof(int));
                if (len_b == 0) goto outer_hi;
            }
            state->array[dest--] = state->array[cursor_a--];
            len_a--;
            if (len_a == 0) goto outer_hi;

            min_gallop--;
        } while (count_a >= MIN_GALLOP_DEFAULT || count_b >= MIN_GALLOP_DEFAULT);

        if (min_gallop < 1) min_gallop = 1;
        min_gallop += 2;
    }

outer_hi:
    state->min_gallop = (min_gallop < 1) ? 1 : min_gallop;
    if (len_b > 0) {
        memcpy(&state->array[dest - len_b + 1], state->temp_buf, len_b * sizeof(int));
    }
}

static void merge_at(TimSortState *state, size_t i) {
    size_t base_a = state->stack[i].start;
    size_t len_a = state->stack[i].len;
    size_t base_b = state->stack[i + 1].start;
    size_t len_b = state->stack[i + 1].len;

    state->stack[i].len = len_a + len_b;
    if (i == state->stack_size - 3) {
        state->stack[i + 1] = state->stack[i + 2];
    }
    state->stack_size--;

    size_t k = gallop_right(state->array[base_b], state->array, base_a, len_a, 0);
    base_a += k;
    len_a -= k;
    if (len_a == 0) return;

    len_b = gallop_left(state->array[base_a + len_a - 1], state->array, base_b, len_b, len_b - 1);
    if (len_b == 0) return;

    if (len_a <= len_b) {
        merge_lo(state, base_a, len_a, base_b, len_b);
    } else {
        merge_hi(state, base_a, len_a, base_b, len_b);
    }
}
```
```cpp
template <typename T, typename Compare>
void TimSort<T, Compare>::merge_lo(std::span<T> data, size_t base_a, size_t len_a, size_t base_b, size_t len_b) {
    if (temp_buf_.size() < len_a) {
        temp_buf_.resize(len_a);
    }
    std::move(data.begin() + base_a, data.begin() + base_a + len_a, temp_buf_.begin());

    size_t cursor_a = 0;
    size_t cursor_b = base_b;
    size_t dest = base_a;
    size_t min_gallop = min_gallop_;

    while (cursor_a < len_a && cursor_b < base_b + len_b) {
        size_t count_a = 0;
        size_t count_b = 0;

        do {
            if (comp_(data[cursor_b], temp_buf_[cursor_a])) {
                data[dest++] = std::move(data[cursor_b++]);
                count_b++;
                count_a = 0;
                if (cursor_b == base_b + len_b) goto outer_lo;
            } else {
                data[dest++] = std::move(temp_buf_[cursor_a++]);
                count_a++;
                count_b = 0;
                if (cursor_a == len_a) goto outer_lo;
            }
        } while ((count_a | count_b) < min_gallop);

        do {
            count_a = gallop_right_impl(data[cursor_b], std::span<const T>(temp_buf_.data(), len_a), cursor_a, len_a - cursor_a, 0, comp_);
            if (count_a > 0) {
                std::move(temp_buf_.begin() + cursor_a, temp_buf_.begin() + cursor_a + count_a, data.begin() + dest);
                dest += count_a;
                cursor_a += count_a;
                if (cursor_a == len_a) goto outer_lo;
            }
            data[dest++] = std::move(data[cursor_b++]);
            if (cursor_b == base_b + len_b) goto outer_lo;

            count_b = gallop_left_impl(temp_buf_[cursor_a], std::span<const T>(data.data(), base_b + len_b), cursor_b, base_b + len_b - cursor_b, 0, comp_);
            if (count_b > 0) {
                std::move(data.begin() + cursor_b, data.begin() + cursor_b + count_b, data.begin() + dest);
                dest += count_b;
                cursor_b += count_b;
                if (cursor_b == base_b + len_b) goto outer_lo;
            }
            data[dest++] = std::move(temp_buf_[cursor_a++]);
            if (cursor_a == len_a) goto outer_lo;

            min_gallop--;
        } while (count_a >= MIN_GALLOP_DEFAULT || count_b >= MIN_GALLOP_DEFAULT);

        if (min_gallop < 1) min_gallop = 1;
        min_gallop += 2;
    }

outer_lo:
    min_gallop_ = (min_gallop < 1) ? 1 : min_gallop;
    if (cursor_a < len_a) {
        std::move(temp_buf_.begin() + cursor_a, temp_buf_.begin() + len_a, data.begin() + dest);
    }
}

template <typename T, typename Compare>
void TimSort<T, Compare>::merge_hi(std::span<T> data, size_t base_a, size_t len_a, size_t base_b, size_t len_b) {
    if (temp_buf_.size() < len_b) {
        temp_buf_.resize(len_b);
    }
    std::move(data.begin() + base_b, data.begin() + base_b + len_b, temp_buf_.begin());

    size_t cursor_a = base_a + len_a - 1;
    size_t cursor_b = len_b - 1;
    size_t dest = base_b + len_b - 1;
    size_t min_gallop = min_gallop_;

    while (len_a > 0 && len_b > 0) {
        size_t count_a = 0;
        size_t count_b = 0;

        do {
            if (comp_(data[cursor_a], temp_buf_[cursor_b])) {
                data[dest--] = std::move(temp_buf_[cursor_b--]);
                len_b--;
                count_b++;
                count_a = 0;
                if (len_b == 0) goto outer_hi;
            } else {
                data[dest--] = std::move(data[cursor_a--]);
                len_a--;
                count_a++;
                count_b = 0;
                if (len_a == 0) goto outer_hi;
            }
        } while ((count_a | count_b) < min_gallop);

        do {
            count_a = len_a - gallop_right_impl(temp_buf_[cursor_b], std::span<const T>(data.data(), base_a + len_a), base_a, len_a, len_a - 1, comp_);
            if (count_a > 0) {
                dest -= count_a;
                cursor_a -= count_a;
                len_a -= count_a;
                std::move_backward(data.begin() + cursor_a + 1, data.begin() + cursor_a + 1 + count_a, data.begin() + dest + count_a + 1);
                if (len_a == 0) goto outer_hi;
            }
            data[dest--] = std::move(temp_buf_[cursor_b--]);
            len_b--;
            if (len_b == 0) goto outer_hi;

            count_b = len_b - gallop_left_impl(data[cursor_a], std::span<const T>(temp_buf_.data(), len_b), 0, len_b, len_b - 1, comp_);
            if (count_b > 0) {
                dest -= count_b;
                cursor_b -= count_b;
                len_b -= count_b;
                std::move(temp_buf_.begin() + cursor_b + 1, temp_buf_.begin() + cursor_b + 1 + count_b, data.begin() + dest + 1);
                if (len_b == 0) goto outer_hi;
            }
            data[dest--] = std::move(data[cursor_a--]);
            len_a--;
            if (len_a == 0) goto outer_hi;

            min_gallop--;
        } while (count_a >= MIN_GALLOP_DEFAULT || count_b >= MIN_GALLOP_DEFAULT);

        if (min_gallop < 1) min_gallop = 1;
        min_gallop += 2;
    }

outer_hi:
    min_gallop_ = (min_gallop < 1) ? 1 : min_gallop;
    if (len_b > 0) {
        std::move(temp_buf_.begin(), temp_buf_.begin() + len_b, data.begin() + dest - len_b + 1);
    }
}

template <typename T, typename Compare>
void TimSort<T, Compare>::merge_at(std::span<T> data, size_t i) {
    size_t base_a = stack_[i].start;
    size_t len_a = stack_[i].len;
    size_t base_b = stack_[i + 1].start;
    size_t len_b = stack_[i + 1].len;

    stack_[i].len = len_a + len_b;
    if (i == stack_size_ - 3) {
        stack_[i + 1] = stack_[i + 2];
    }
    stack_size_--;

    size_t k = gallop_right_impl(data[base_b], std::span<const T>(data.data(), data.size()), base_a, len_a, 0, comp_);
    base_a += k;
    len_a -= k;
    if (len_a == 0) return;

    len_b = gallop_left_impl(data[base_a + len_a - 1], std::span<const T>(data.data(), data.size()), base_b, len_b, len_b - 1, comp_);
    if (len_b == 0) return;

    if (len_a <= len_b) {
        merge_lo(data, base_a, len_a, base_b, len_b);
    } else {
        merge_hi(data, base_a, len_a, base_b, len_b);
    }
}
```
:::

## Головна точка входу та повний тестовий стенд

Функція `timsort` утворює єдину точку входу для зовнішнього клієнтського коду: вона ініціалізує внутрішній стан, послідовно виділяє та подовжує серії, підтримує інваріанти стека й гарантує коректне вивільнення виділеної динамічної пам'яті.

Наведений нижче тестовий стенд перевіряє як правильність впорядкування чисел, так і збереження стабільності відносного розташування однакових ключів у структурах даних `Item`.

:::tabs
```c
void timsort(int *arr, size_t n) {
    if (n < 2) return;

    size_t minrun = calculate_minrun(n);
    TimSortState state;
    state.array = arr;
    state.size = n;
    state.temp_buf = NULL;
    state.temp_capacity = 0;
    state.min_gallop = MIN_GALLOP_DEFAULT;
    state.stack_size = 0;

    size_t start = 0;
    while (start < n) {
        size_t run_len = count_and_reverse_run(arr, start, n);

        if (run_len < minrun) {
            size_t force = (n - start < minrun) ? (n - start) : minrun;
            binary_insertion_sort(arr, start, force, run_len);
            run_len = force;
        }

        state.stack[state.stack_size].start = start;
        state.stack[state.stack_size].len = run_len;
        state.stack_size++;

        merge_collapse(&state);
        start += run_len;
    }

    merge_force_collapse(&state);

    if (state.temp_buf) {
        free(state.temp_buf);
    }
}

int main(void) {
    int test_data[] = { 42, 17, 93, 8, 12, 65, 88, 5, 23, 71, 3, 50, 81, 19, 34, 99 };
    size_t n = sizeof(test_data) / sizeof(test_data[0]);

    printf("Початковий масив:\n");
    for (size_t i = 0; i < n; i++) printf("%d ", test_data[i]);
    printf("\n");

    timsort(test_data, n);

    printf("Відсортований масив:\n");
    for (size_t i = 0; i < n; i++) printf("%d ", test_data[i]);
    printf("\n");

    for (size_t i = 1; i < n; i++) {
        if (test_data[i] < test_data[i - 1]) {
            printf("ПОМИЛКА СОРТУВАННЯ!\n");
            return 1;
        }
    }
    printf("Сортування успішно підтверджено!\n");
    return 0;
}
```
```cpp
template <typename T, typename Compare>
void TimSort<T, Compare>::sort(std::span<T> data) {
    const size_t n = data.size();
    if (n < 2) return;

    size_t minrun = calculate_minrun_impl<T, Compare>(n);
    stack_size_ = 0;
    min_gallop_ = MIN_GALLOP_DEFAULT;

    size_t start = 0;
    while (start < n) {
        size_t run_len = count_and_reverse_run_impl(data, start, comp_);

        if (run_len < minrun) {
            size_t force = std::min(minrun, n - start);
            binary_insertion_sort_impl(data, start, force, run_len, comp_);
            run_len = force;
        }

        stack_[stack_size_++] = Run{ start, run_len };
        merge_collapse(data);
        start += run_len;
    }

    merge_force_collapse(data);
}

struct Item {
    int key;
    int original_index;
};

int main() {
    std::vector<Item> items = {
        {5, 0}, {2, 1}, {8, 2}, {5, 3}, {1, 4}, {5, 5}, {2, 6}, {9, 7}
    };

    TimSort<Item, decltype([](const Item &a, const Item &b) { return a.key < b.key; })> sorter;
    sorter.sort(items);

    std::cout << "Відсортований масив (key, orig_index):\n";
    for (const auto &it : items) {
        std::cout << "{" << it.key << ", " << it.original_index << "} ";
    }
    std::cout << "\n";

    bool stable = true;
    for (size_t i = 1; i < items.size(); ++i) {
        if (items[i].key < items[i - 1].key) {
            std::cerr << "Помилка порядку ключів!\n";
            return 1;
        }
        if (items[i].key == items[i - 1].key && items[i].original_index < items[i - 1].original_index) {
            stable = false;
        }
    }

    std::cout << "Стійкість сортування: " << (stable ? "ЗБЕРЕЖЕНО (OK)" : "ПОРУШЕНО (ПОМИЛКА)") << "\n";
    return 0;
}
```
:::

## Крайові випадки та поведінка алгоритму

Реалізація забезпечує стійку та оптимальну обробку всіх критичних граничних станів:

1. **Масив нульової або одиничної довжини (`N < 2`):** Вихід відбувається на першому ж рядку функції `timsort` без виконання жодних порівнянь або алокацій пам'яті.
2. **Вже відсортований масив:** Алгоритм виконує рівно `N - 1` порівнянь у циклі `count_and_reverse_run`, фіксує єдину природну серію довжиною `N`, кладе її на стек і завершує роботу за лінійний час `O(N)` без використання додаткової пам'яті.
3. **Повністю зворотно впорядкований масив:** Алгоритм виявляє спадну послідовність за `N - 1` порівнянь, розвертає її на місці за `N / 2` обмінів і завершує сортування за час `O(N)`.
4. **Масив з однакових елементів:** Усі елементи трактуються як одна неспадна серія (`arr[k] <= arr[k+1]`), що забезпечує лінійну швидкість `O(N)` без зайвих перестановок.
5. **Масив з великою кількістю дублікатів:** Присутність однакових ключів у режимі злиття коректно обробляється пріоритетом лівої серії, що запобігає виникненню нескінченних циклів або деградації швидкості.
6. **Випадкові та дрібноструктуровані дані:** Алгоритм розбиває дані на серії довжиною `minrun`, підтримує баланс через стек серій та забезпечує гарантований час виконання `O(N log N)`.

## Покрокове простеження стану алгоритму (Execution Trace)

Щоб детально простежити взаємодію всіх підсистем, розглянемо виконання алгоритму на конкретному масиві з 16 цілих чисел: `[14, 11, 8, 3, 5, 12, 18, 25, 90, 75, 42, 19, 4, 15, 2, 33]`.

Оскільки `N = 16 < 64`, алгоритм встановлює `minrun = 16`. Весь масив розглядається як єдина цільова серія, яку необхідно впорядкувати бінарними вставками на основі першої знайденої природної серії:

1. **Крок 1 (Виявлення серії):** Алгоритм починає сканування з індексу 0. Порівнюючи `arr[1] = 11 < arr[0] = 14`, виявляється спадна послідовність `[14, 11, 8, 3]`. Спадання переривається на числі 5 (`5 > 3`). Довжина природної серії становить 4 елементи.
2. **Крок 2 (Інверсія спадної серії):** Серія `arr[0..3]` розгортається на місці двома вказівниками. Масив набуває стану: `[3, 8, 11, 14, 5, 12, 18, 25, 90, 75, 42, 19, 4, 15, 2, 33]`.
3. **Крок 3 (Бінарне подовження):** Оскільки `run_len = 4 < minrun = 16`, запускається `binary_insertion_sort` для решти елементів від індексу 4 до 15:
   - Елемент `arr[4] = 5`: двійковий пошук у `[3, 8, 11, 14]` знаходить позицію між 3 та 8 (індекс 1). Елементи `[8, 11, 14]` зсуваються вправо. Масив: `[3, 5, 8, 11, 14, 12, ...]`.
   - Елемент `arr[5] = 12`: вставляється на індекс 4 після 11. Масив: `[3, 5, 8, 11, 12, 14, 18, ...]`.
   - Процес повторюється для кожного наступного числа.
4. **Крок 4 (Фінал):** Після досягнення кінця масиву весь масив розміром 16 елементів повністю впорядкований. Дескриптор `(start=0, len=16)` поміщається на стек і завершує роботу.

Для великих масивів (наприклад, `N = 1000`, `minrun = 32`) кожні виділені серії розміром ≥ 32 потрапляють на стек, де процедура `merge_collapse` поступово зливає їх у збалансовані блоки розміром 64, 128, 256 і 512 елементів, діючи аналогічно побудові дерева рекурсії сортування злиттям знизу вгору (bottom-up mergesort).

## Архітектурні оптимізації та кеш-пам'ять процесора

Виняткова продуктивність Timsort у порівнянні з класичними алгоритмами досягається завдяки глибокій оптимізації під мікроархітектуру сучасних процесорів:

1. **Кеш-локальність природних серій:** Сканування серій виконується суворо послідовно за адресами пам'яті. Апаратний блок попередньої вибірки процесора (Hardware Stream Prefetcher) завчасно підвантажує сусідні кеш-лінії розміром 64 байти в кеш L1D. Завдяки цьому прохід пошуку серій практично не генерує кеш-промахів (cache misses).
2. **Векторизовані зсуви вставками:** При розмірі серії `minrun ≤ 64` весь блок даних займає щонайбільше 256–512 байтів. Інструкція `memmove` у стандартній бібліотеці компілятора розгортається у векторні SIMD-регістри (AVX2 / NEON), копіюючи по 32 або 64 байти за один такт процесора без покрокових скалярних циклів. При компіляції з прапорцями `-O3 -march=native -flto` компілятор GCC або Clang здатний повністю розгорнути двійковий пошук для константних довжин серій у безрозгалужені інструкції умовного пересилання `cmov`.
3. **Передбачення розгалужень (Branch Prediction):** На майже впорядкованих даних цикли виявлення серій виконують однотипні переходи `arr[i] <= arr[i+1]` із точністю передбачення понад 99%, що запобігає скиданню конвеєра інструкцій процесора.
4. **Адаптивний поріг галопу як запобіжник:** Якщо дані випадкові, перехід у двійковий пошук спричиняє часті хибні передбачення переходів (branch mispredictions). Динамічне збільшення порогу `min_gallop += 2` при невдалому галопі виступає негативним зворотним зв'язком, миттєво повертаючи алгоритм до швидкого покрокового лінійного злиття.
5. **Нульове динамічне виділення пам'яті для малих масивів:** Якщо розмір масиву не перевищує 64 елементів, Timsort взагалі не виділяє пам'ять на купі (heap), повністю завершуючи роботу в межах стекового фрейму функції без системних викликів ядра.

## Поширені пастки та типові помилки реалізації

При самостійному написанні Timsort інженери найчастіше припускаються таких критичних помилок:

- **Порушення умови строгого спадання:** Використання нестрогої нерівності `arr[k] <= arr[k-1]` при пошуку спадної серії призводить до того, що однакові елементи міняються місцями під час інверсії. Це непомітно руйнує стійкість сортування при роботі зі складними об'єктами.
- **Відсутність перевірки 4-елементного інваріанта:** Реалізація лише двох оригінальних правил Пітера 2002 року спричиняє переповнення стека серій `stack` на спеціально підібраних великих вхідних масивах. Необхідно обов'язково перевіряти стан серії `stack[n - 2]` відносно `stack[n - 1]` та `stack[n]`.
- **Витік пам'яті при зміні розміру буфера:** Використання `malloc` на кожному кроці злиття замість кешування та виклику `realloc` у структурі стану створює колосальні накладні витрати на взаємодію з ядром операційної системи.
- **Зміщення індексів у галопі:** Помилка в один елемент між закритим інтервалом `[last_ofs, ofs]` та напіввідкритим `[last_ofs, ofs)` у двійковому пошуку галопу призводить до пропуску граничних елементів і появи невпорядкованих пар у фінальному масиві.

