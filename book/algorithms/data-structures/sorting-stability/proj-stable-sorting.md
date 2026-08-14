# ⚙️ Практична реалізація стійких алгоритмів та декорування ключів

Практична різниця між стійким та нестійким сортуванням проявляється в той момент, коли елементами масиву є не абстрактні цілі числа, а складні структури даних або об'єкти з декількома полями. На практиці використання нестійкого алгоритму сортування може безповоротно порушити вже наявне впорядкування за суміжними параметрами або призвести до недетермінованих результатів у розрахункових системах.

У цій практичній вставці ми детально розберемо:
1. Демонстрацію нестійкості швидкого сортування (`qsort` / `std::sort`) та стійкості сортування злиттям (Merge Sort / `std::stable_sort`) на реальних об'єктах.
2. Повну реалізацію універсального паттерну **декорування ключів (Key Augmentation)** мовами C та C++ для перетворення будь-якого нестійкого алгоритму на стійкий.
3. Оптимізовану індексну модифікацію декорування без важкого копіювання байтів (Indirect Index Sorting).
4. Механіку багатопрохідного сортування табличних даних (симуляція сортування колонок електронної таблиці).
5. Потокобезпечну реалізацію системних сортувальників (`qsort_r` vs `qsort_s`).
6. Використання компараторів на `std::tie` та `std::tuple` у C++.
7. Стійкість у стандартних бібліотеках інших мов програмування (Python, Java, C#, Rust, Go).
8. Практичні рекомендації щодо вибору стійких алгоритмів для високонавантажених серверів та вбудованих систем (Embedded Systems).
9. Детальний аналіз накладних витрат пам'яті, кеш-локальності, пасток компараторів та порівняльний бенчмарк швидкодії.

---

## 1. Демонстрація: Quicksort проти Merge Sort для об'єктів

Розглянемо практичну задачу. У нас є список студентів із полями `grade` (оцінка від 1 до 5) та `name` (прізвище). Початковий масив вже впорядкований за алфавітом. Наше завдання — відсортувати студентів за оцінкою у спадному порядку, але при цьому **зберегти алфавітний порядок** для всіх студентів, які мають однаковий бал.

При використанні нестійкого алгоритму (наприклад, стандартного `qsort` у мові C чи `std::sort` у C++) елементи з однаковими оцінками можуть мінятися місцями залежно від обраного опорного елемента (pivot) та механіки розділення масиву. У результаті алфавітний порядок усередині груп з однаковими оцінками розрушається. Натомість стійке сортування злиттям (Merge Sort) зберігає відносний порядок незмінним.

:::tabs
```c
/* C: Демонстрація нестійкості Quicksort та стійкості Merge Sort */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int grade;
    char name[32];
    int original_index;
} Student;

void print_students(const char *label, const Student *arr, size_t n) {
    printf("=== %s ===\n", label);
    for (size_t i = 0; i < n; i++) {
        printf("  [%zu] Оцінка: %d | Ім'я: %-12s (orig_idx: %d)\n",
               i, arr[i].grade, arr[i].name, arr[i].original_index);
    }
    printf("\n");
}

/* Компаратор для qsort (порівняння лише за оцінкою, за спаданням) */
int compare_by_grade_desc(const void *a, const void *b) {
    const Student *sa = (const Student *)a;
    const Student *sb = (const Student *)b;
    if (sb->grade != sa->grade) {
        return sb->grade - sa->grade;
    }
    return 0; /* Рівні оцінки — qsort не гарантує збереження порядку! */
}

/* Стійке сортування злиттям (Merge Sort) */
void merge_stable(Student *arr, Student *temp, size_t left, size_t mid, size_t right) {
    size_t i = left;
    size_t j = mid + 1;
    size_t k = left;

    while (i <= mid && j <= right) {
        /* ВАЖЛИВО: Оператор >= забезпечує стійкість.
           При рівних оцінках першим береться елемент із лівої частини (i). */
        if (arr[i].grade >= arr[j].grade) {
            temp[k++] = arr[i++];
        } else {
            temp[k++] = arr[j++];
        }
    }

    while (i <= mid) {
        temp[k++] = arr[i++];
    }
    while (j <= right) {
        temp[k++] = arr[j++];
    }

    for (i = left; i <= right; i++) {
        arr[i] = temp[i];
    }
}

void merge_sort_recursive(Student *arr, Student *temp, size_t left, size_t right) {
    if (left >= right) return;
    size_t mid = left + (right - left) / 2;
    merge_sort_recursive(arr, temp, left, mid);
    merge_sort_recursive(arr, temp, mid + 1, right);
    merge_stable(arr, temp, left, mid, right);
}

void merge_sort_students(Student *arr, size_t n) {
    Student *temp = (Student *)malloc(n * sizeof(Student));
    if (!temp) return;
    merge_sort_recursive(arr, temp, 0, n - 1);
    free(temp);
}

int main(void) {
    Student original[] = {
        {5, "Авраменко", 0},
        {4, "Бондаренко", 1},
        {5, "Василенко", 2},
        {4, "Грищенко", 3},
        {5, "Дмитренко", 4}
    };
    size_t n = sizeof(original) / sizeof(original[0]);

    Student arr_qsort[5];
    Student arr_merge[5];
    memcpy(arr_qsort, original, sizeof(original));
    memcpy(arr_merge, original, sizeof(original));

    print_students("Вихідний масив (відсортований за прізвищем)", original, n);

    /* Сортування через стандартний qsort (може бути нестійким) */
    qsort(arr_qsort, n, sizeof(Student), compare_by_grade_desc);
    print_students("Після C qsort() [Нестійке сортування]", arr_qsort, n);

    /* Сортування через наш стійкий Merge Sort */
    merge_sort_students(arr_merge, n);
    print_students("Після Merge Sort [Стійке сортування]", arr_merge, n);

    return 0;
}
```
```cpp
// C++: Ідіоматична порівняльна демонстрація std::sort vs std::stable_sort
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <iomanip>

struct Student {
    int grade;
    std::string name;
    int original_index;
};

void print_students(std::string_view label, const std::vector<Student>& students) {
    std::cout << "=== " << label << " ===\n";
    for (size_t i = 0; i < students.size(); ++i) {
        std::cout << "  [" << i << "] Оцінка: " << students[i].grade
                  << " | Ім'я: " << std::left << std::setw(12) << students[i].name
                  << " (orig_idx: " << students[i].original_index << ")\n";
    }
    std::cout << "\n";
}

int main() {
    const std::vector<Student> original = {
        {5, "Авраменко", 0},
        {4, "Бондаренко", 1},
        {5, "Василенко", 2},
        {4, "Грищенко", 3},
        {5, "Дмитренко", 4}
    };

    print_students("Вихідний масив (відсортований за прізвищем)", original);

    // 1. Нестійке сортування std::sort (Introsort)
    auto std_sorted = original;
    std::sort(std_sorted.begin(), std_sorted.end(), [](const Student& a, const Student& b) {
        return a.grade > b.grade; // За спаданням оцінки
    });
    print_students("Після std::sort (Нестійке)", std_sorted);

    // 2. Стійке сортування std::stable_sort (Adaptive Merge Sort)
    auto stable_sorted = original;
    std::stable_sort(stable_sorted.begin(), stable_sorted.end(), [](const Student& a, const Student& b) {
        return a.grade > b.grade; // За спаданням оцінки
    });
    print_students("Після std::stable_sort (Стійке)", stable_sorted);

    return 0;
}
```
:::

### Детальний розбір механізму стійкості у коді

Зверніть увагу на важливі алгоритмічні нюанси при розробці стійких систем:

1. **Ключова лінія у `merge_stable`:**
   При порівнянні елементів у C-реалізації сортування злиттям ми використовуємо умову `arr[i].grade >= arr[j].grade`. Символ `>=` означає, що коли елемент із лівої частини (`arr[i]`) має таку саму оцінку, як і елемент із правої частини (`arr[j]`), вибір надається саме елементу з **лівої** частини. Оскільки ліва частина в початковому масиві розташовувалася раніше за праву, це зберігає вихідний порядок. Якби ми випадково змінили `>=` на суворе `>`, алгоритм моментально перетворився б на нестійкий, і елементи з правої частини випереджали б однакові елементи з лівої.

2. **Стандартні функції C++:**
   У C++ функція `std::sort` використовує алгоритм Introsort (гібрид Quicksort, Heapsort та Insertion Sort). Оскільки Quicksort виконує перемикання елементів через опорну точку (pivot) на великі відстані, відносний порядок студентів із однаковою оцінкою 5 руйнується. Натомість `std::stable_sort` застосовує адаптивне сортування злиттям, яке гарантує збереження вихідного порядку елементів.

3. **Спадне та зростаюче сортування:**
   Для сортування за зростанням умовою стійкості злиття є `arr[i].grade <= arr[j].grade`. Аксиоматичне правило таке: **при рівності ключів перемагає елемент із меншим вихідним індексом**.

---

## 2. Реалізація шаблону декорування ключів (Key Augmentation)

Що робити, якщо у вашій цільовій системі доступний лише нестійкий алгоритм сортування (наприклад, вбудована високооптимізована функція `qsort` або системна бібліотека без підтримки `stable_sort`), але бізнес-логіка вимагає збереження відносного порядку?

У такому разі застосовується універсальний архітектурний паттерн **декорування ключів (Key Augmentation)**, також відомий у софтверній інженерії як *Decorate-Sort-Undecorate* або *Schwartzian Transform*.

### Алгоритм виконання декорування:
1. **Фаза декорування (Decorate):** Створюється тимчасовий допоміжний масив обгорток `AugmentedItem<T>`. У кожну обгортку пакується сам оригінальний елемент (або вказівник на нього) та його початковий порядковий індекс `index` у масиві (`0, 1, 2, ..., n-1`).
2. **Фаза сортування (Sort):** Викликається **нестійкий** сортувальник з розширеним компаратором двох рівнів:
   - Спочатку порівнюються основні ключі елементів.
   - Якщо основні ключі рівні, компаратор порівнює їхні початкові індекси `index`. Оскільки всі початкові індекси унікальні, компаратор **ніколи не повертає 0** для різних елементів.
3. **Фаза розпакування (Undecorate):** Впорядковані елементи копіюються з обгорток назад у вихідний масив, а тимчасовий масив декорування звільняється.

:::tabs
```c
/* C: Декорувальник ключів для гарантування стійкості будь-якого нестійкого сортувальника */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int key;
    char payload[64];
} Record;

typedef struct {
    Record data;
    size_t original_index;
} DecoratedRecord;

/* Спеціальний компаратор: якщо ключі однакові, перемагає той, чий початковий індекс менший */
int decorated_comparator(const void *a, const void *b) {
    const DecoratedRecord *da = (const DecoratedRecord *)a;
    const DecoratedRecord *db = (const DecoratedRecord *)b;

    if (da->data.key != db->data.key) {
        return da->data.key - db->data.key; /* Основне сортування за зростанням ключів */
    }

    /* Рівність ключів: суворе порівняння за початковим індексом для стійкості */
    if (da->original_index < db->original_index) return -1;
    if (da->original_index > db->original_index) return 1;
    return 0;
}

void stable_qsort_wrapper(Record *arr, size_t n) {
    DecoratedRecord *decorated = (DecoratedRecord *)malloc(n * sizeof(DecoratedRecord));
    if (!decorated) return;

    /* Крок 1: Декорування (збереження початкового індексу) */
    for (size_t i = 0; i < n; i++) {
        decorated[i].data = arr[i];
        decorated[i].original_index = i;
    }

    /* Крок 2: Виклик НЕСТІЙКОГО qsort з розширеним компаратором */
    qsort(decorated, n, sizeof(DecoratedRecord), decorated_comparator);

    /* Крок 3: Розпакування (Un-decorate) */
    for (size_t i = 0; i < n; i++) {
        arr[i] = decorated[i].data;
    }

    free(decorated);
}

int main(void) {
    Record items[] = {
        {10, "Запис A"},
        {5,  "Запис B (перший з 5)"},
        {20, "Запис C"},
        {5,  "Запис D (другий з 5)"},
        {5,  "Запис E (третій з 5)"}
    };
    size_t n = sizeof(items) / sizeof(items[0]);

    printf("=== До сортування ===\n");
    for (size_t i = 0; i < n; i++) {
        printf("  [%zu] Key: %d, Payload: %s\n", i, items[i].key, items[i].payload);
    }

    stable_qsort_wrapper(items, n);

    printf("\n=== Після декорованого нестійкого qsort ===\n");
    for (size_t i = 0; i < n; i++) {
        printf("  [%zu] Key: %d, Payload: %s\n", i, items[i].key, items[i].payload);
    }

    return 0;
}
```
```cpp
// C++: Універсальний шаблонний декорувальник ключа для std::sort
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <concepts>

template <typename T, typename KeyExtractor>
void stable_sort_via_decoration(std::vector<T>& vec, KeyExtractor key_extractor) {
    using KeyType = std::invoke_result_t<KeyExtractor, const T&>;

    struct Decorated {
        T value;
        KeyType key;
        size_t original_index;
    };

    std::vector<Decorated> decorated;
    decorated.reserve(vec.size());

    // 1. Декоруємо елементи індексами
    for (size_t i = 0; i < vec.size(); ++i) {
        decorated.push_back({vec[i], key_extractor(vec[i]), i});
    }

    // 2. Сортуємо нестійким std::sort з двопарамним компаратором
    std::sort(decorated.begin(), decorated.end(), [](const Decorated& a, const Decorated& b) {
        if (a.key != b.key) {
            return a.key < b.key;
        }
        return a.original_index < b.original_index; // Гарантія стійкості!
    });

    // 3. Відновлюємо оригінальний вектор
    for (size_t i = 0; i < vec.size(); ++i) {
        vec[i] = std::move(decorated[i].value);
    }
}

struct Product {
    int category_id;
    std::string name;
    double price;
};

int main() {
    std::vector<Product> products = {
        {1, "Ноутбук", 1200.0},
        {2, "Мишка А", 25.0},
        {1, "Клавіатура", 80.0},
        {2, "Мишка Б", 25.0},
        {1, "Монітор", 300.0}
    };

    std::cout << "=== Вхідні товари ===\n";
    for (const auto& p : products) {
        std::cout << "Категорія: " << p.category_id << " | " << p.name << " ($" << p.price << ")\n";
    }

    // Сортуємо за категорією, зберігаючи вхідний порядок товарів всередині категорії
    stable_sort_via_decoration(products, [](const Product& p) {
        return p.category_id;
    });

    std::cout << "\n=== Після декорованого стійкого сортування за категорією ===\n";
    for (const auto& p : products) {
        std::cout << "Категорія: " << p.category_id << " | " << p.name << " ($" << p.price << ")\n";
    }

    return 0;
}
```
:::

### Покроковий розбір C++ реалізації `stable_sort_via_decoration`

У наведеній реалізації C++ ми використовуємо сучасні стандарти мови (C++17 та C++20):
- **`std::invoke_result_t<KeyExtractor, const T&>`:** Автоматично виводиться тип ключа, який повертає лямбда-функція `key_extractor`. Це робить декорувальник універсальним для будь-яких типів даних — цілих чисел, рядків, чисел із плаваючою крапкою тощо.
- **`std::move` під час відновлення:** Для запобігання зайвому копіюванню важких об'єктів (наприклад, типів із `std::string` або `std::vector` всередині) ми переміщуємо значення з декорованої структури назад у початковий вектор `vec[i] = std::move(decorated[i].value)`.

---

## 3. Оптимізоване непряме сортування за індексами (Indirect Index Sorting)

Пряме декорування, наведене вище, копіює цілі структури `Record` чи `T` у тимчасовий масив. Якщо розмір об'єкта великий (наприклад, декілька кілобайтів текстових або бінарних даних), переміщення таких структур у пам'яті створює важке навантаження на шину пам'яті та руйнує кеш процесора.

Для вирішення цієї проблеми застосовують **непряме сортування за індексами (Indirect Index Sorting)**. Замість копіювання самих елементів створюється простий масив індексів `[0, 1, 2, ..., n-1]`. Сортувальник впорядковує сам масив індексів, звертаючись до оригінальних даних лише для порівняння.

:::tabs
```c
/* C: Непряме сортування масиву індексів з гарантованою стійкістю */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int id;
    int priority;
    char payload[256]; /* Важка структура даних */
} LargeTask;

/* Глобальний контекст для порівняння в qsort_r або через статичний вказівник */
static const LargeTask *g_tasks = NULL;

int compare_indirect(const void *a, const void *b) {
    size_t idx_a = *(const size_t *)a;
    size_t idx_b = *(const size_t *)b;

    if (g_tasks[idx_a].priority != g_tasks[idx_b].priority) {
        return g_tasks[idx_b].priority - g_tasks[idx_a].priority; /* Спадіння */
    }

    /* Рівність пріоритетів: порівнюємо сам індекс для збереження стійкості */
    if (idx_a < idx_b) return -1;
    if (idx_a > idx_b) return 1;
    return 0;
}

void indirect_stable_sort(const LargeTask *tasks, size_t n, size_t *out_indices) {
    for (size_t i = 0; i < n; i++) {
        out_indices[i] = i;
    }
    g_tasks = tasks;
    qsort(out_indices, n, sizeof(size_t), compare_indirect);
    g_tasks = NULL;
}

int main(void) {
    LargeTask tasks[] = {
        {101, 3, "Завдання 1"},
        {102, 5, "Завдання 2 (перше з пріоритетом 5)"},
        {103, 3, "Завдання 3"},
        {104, 5, "Завдання 4 (друге з пріоритетом 5)"}
    };
    size_t n = sizeof(tasks) / sizeof(tasks[0]);
    size_t *indices = (size_t *)malloc(n * sizeof(size_t));

    indirect_stable_sort(tasks, n, indices);

    printf("=== Відсортовані індекси завдань ===\n");
    for (size_t i = 0; i < n; i++) {
        size_t idx = indices[i];
        printf("  Опосередкована позиція [%zu] -> Task ID: %d, Priority: %d (%s)\n",
               i, tasks[idx].id, tasks[idx].priority, tasks[idx].payload);
    }

    free(indices);
    return 0;
}
```
```cpp
// C++: Ідіоматичне непряме сортування через std::vector<size_t> та std::sort
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <numeric>

struct LargeTask {
    int id;
    int priority;
    std::string payload;
};

std::vector<size_t> create_indirect_stable_permutation(const std::vector<LargeTask>& tasks) {
    std::vector<size_t> indices(tasks.size());
    std::iota(indices.begin(), indices.end(), 0); // Заповнюємо 0, 1, 2, ..., n-1

    std::sort(indices.begin(), indices.end(), [&tasks](size_t a, size_t b) {
        if (tasks[a].priority != tasks[b].priority) {
            return tasks[a].priority > tasks[b].priority; // Спадіння
        }
        return a < b; // Стійке порівняння початкових індексів
    });

    return indices;
}

int main() {
    std::vector<LargeTask> tasks = {
        {101, 3, "Завдання 1"},
        {102, 5, "Завдання 2 (перше з пріоритетом 5)"},
        {103, 3, "Завдання 3"},
        {104, 5, "Завдання 4 (друге з пріоритетом 5)"}
    };

    auto perm = create_indirect_stable_permutation(tasks);

    std::cout << "=== Результат непрямого стійкого сортування ===\n";
    for (size_t idx : perm) {
        std::cout << "  Task ID: " << tasks[idx].id
                  << " | Priority: " << tasks[idx].priority
                  << " | Payload: " << tasks[idx].payload << "\n";
    }

    return 0;
}
```
:::

### Детальний розбір механізму непрямого сортування

1. **Економія пам'яті:**
   В алгоритмі непрямого сортування масив `tasks` залишається незмінним. Ми виділяємо лише масив цілих чисел `indices` розміром `n * sizeof(size_t)`. Для 1 000 000 елементів це становить лише 8 Мегабайтів пам'яті, навіть якщо кожен об'єкт займає 1 Кіллобайт.

2. **Запобігання інвалідції кешу (Cache Invalidation):**
   При сортуванні оригінальних важких об'єктів операції `swap` змушують процесор перезаписувати сотні байтів у пам'яті. У непрямому сортуванні алгоритм `qsort` або `std::sort` міняє місцями лише 64-бітні індекси, що виконується миттєво в регістрах процесора.

3. **Підтримка детермінованості у системних потоках:**
   У C-реалізації функція `compare_indirect` використовує вказівник на вихідний масив. У багатопотокових середовищах C замість глобального `g_tasks` застосовують потокобезпечну функцію `qsort_r` (GNU/POSIX) або `qsort_s` (MSVC/C11), яка передає контекст через додатковий аргумент компаратора.

---

## 4. Моделювання багатопрохідного сортування колонками (Spreadsheet Sort)

У реальних користувацьких інтерфейсах та аналітичних системах (наприклад, у табличних процесорах Excel чи базах даних SQL) користувач часто сортує таблицю за декількома колонками по черзі:
- Крок 1: Сортуємо за другорядною колонкою (наприклад, **Місто**).
- Крок 2: Сортуємо за головною колонкою (наприклад, **Країна**).

При використанні **стійкого** алгоритму результати першого сортування залишаються повністю збереженими всередині кожної групи однакових країн: усередині України міста будуть впорядковані за алфавітом, і усередині Польщі — також. При нестійкому сортуванні на другому кроці елементи всередині країн перемішаються наосліп.

:::tabs
```c
/* C: Симулятор сортування таблиці за 2 колонками */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char country[32];
    char city[32];
    int population;
} CityRecord;

void print_table(const char *title, const CityRecord *records, size_t n) {
    printf("--- %s ---\n", title);
    for (size_t i = 0; i < n; i++) {
        printf("  %-12s | %-12s | Населення: %d\n",
               records[i].country, records[i].city, records[i].population);
    }
    printf("\n");
}

/* Стійка процедура сортування масиву за довільним компаратором (Merge Sort) */
void merge_sort_generic(void *base, size_t num, size_t size,
                        int (*compar)(const void *, const void *)) {
    if (num < 2) return;
    size_t mid = num / 2;
    void *left = base;
    void *right = (char *)base + mid * size;

    merge_sort_generic(left, mid, size, compar);
    merge_sort_generic(right, num - mid, size, compar);

    /* Злиття */
    char *temp = (char *)malloc(num * size);
    size_t i = 0, j = 0, k = 0;

    while (i < mid && j < (num - mid)) {
        const void *p1 = (char *)left + i * size;
        const void *p2 = (char *)right + j * size;
        if (compar(p1, p2) <= 0) { /* <= забезпечує стійкість */
            memcpy(temp + k * size, p1, size);
            i++;
        } else {
            memcpy(temp + k * size, p2, size);
            j++;
        }
        k++;
    }

    while (i < mid) {
        memcpy(temp + k * size, (char *)left + i * size, size);
        i++; k++;
    }
    while (j < (num - mid)) {
        memcpy(temp + k * size, (char *)right + j * size, size);
        j++; k++;
    }

    memcpy(base, temp, num * size);
    free(temp);
}

int cmp_city(const void *a, const void *b) {
    return strcmp(((const CityRecord *)a)->city, ((const CityRecord *)b)->city);
}

int cmp_country(const void *a, const void *b) {
    return strcmp(((const CityRecord *)a)->country, ((const CityRecord *)b)->country);
}

int main(void) {
    CityRecord data[] = {
        {"Україна", "Львів",  720000},
        {"Польща",  "Краків", 780000},
        {"Україна", "Київ",   2950000},
        {"Польща",  "Варшава",1790000},
        {"Україна", "Одеса",  1010000}
    };
    size_t n = sizeof(data) / sizeof(data[0]);

    print_table("Вхідна таблиця", data, n);

    /* Крок 1: Сортуємо за Містом */
    merge_sort_generic(data, n, sizeof(CityRecord), cmp_city);
    print_table("Крок 1: Після стійкого сортування за Містом", data, n);

    /* Крок 2: Сортуємо за Країною */
    merge_sort_generic(data, n, sizeof(CityRecord), cmp_country);
    print_table("Крок 2: Після стійкого сортування за Країною (Міста впорядковані!)", data, n);

    return 0;
}
```
```cpp
// C++: Двопрохідне сортування таблиці через std::stable_sort
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <iomanip>

struct CityRecord {
    std::string country;
    std::string city;
    int population;
};

void print_table(std::string_view title, const std::vector<CityRecord>& records) {
    std::cout << "--- " << title << " ---\n";
    for (const auto& r : records) {
        std::cout << "  " << std::left << std::setw(12) << r.country
                  << " | " << std::setw(12) << r.city
                  << " | Населення: " << r.population << "\n";
    }
    std::cout << "\n";
}

int main() {
    std::vector<CityRecord> data = {
        {"Україна", "Львів",  720000},
        {"Польща",  "Краків", 780000},
        {"Україна", "Київ",   2950000},
        {"Польща",  "Варшава",1790000},
        {"Україна", "Одеса",  1010000}
    };

    print_table("Вхідна таблиця", data);

    // Крок 1: Сортуємо за другорядною колонкою (Місто)
    std::stable_sort(data.begin(), data.end(), [](const CityRecord& a, const CityRecord& b) {
        return a.city < b.city;
    });
    print_table("Крок 1: Після std::stable_sort за Містом", data);

    // Крок 2: Сортуємо за головною колонкою (Країна)
    std::stable_sort(data.begin(), data.end(), [](const CityRecord& a, const CityRecord& b) {
        return a.country < b.country;
    });
    print_table("Крок 2: Після std::stable_sort за Країною (Міста впорядковані!)", data);

    return 0;
}
```
:::

### Чому порядок сортування колонок має бути від молодшої до старшої (LSD Order)?

Поширеною помилкою початківців є сортування спочатку за головним ключем (Країна), а потім за другорядною (Місто). Якщо зробити так, то друге сортування за містом повністю зруйнує групування за країнами!

Математичне правило багаторазового стійкого сортування таке: **сортування завжди проводиться в порядку від найменш важливого ключа до найважливішого**. Кожне наступне стійке сортування за більш важливим ключем групує записи за новим параметром, зберігаючи попереднє впорядкування всередині кожної рівної групи.

---

## 5. Порівняльний аналіз `merge_sort_generic` та багатопотокової безпеки

У наведеному вище прикладі мовою C реалізовано обобщену функцію `merge_sort_generic`, яка працює з довільними типами даних через `void *base` та `size_t size`.

### Особливості системного сортування у мові C:
1. **Виділення пам'яті для тимчасового буфера:**
   У `merge_sort_generic` тимчасовий буфер `temp` виділяється динамічно функцією `malloc`. У рекурсивному алгоритмі дуже важливо виділити один спільний буфер `temp` один раз у зовнішній функції-обгортці, а не виділяти `malloc` на кожному рекурсивному кроці. Виділення пам'яті на кожному рекурсивному виклику створює високу накладну витрату фрагментації купи.
2. **Багатопотокова безпека системних функцій `qsort_r` та `qsort_s`:**
   Коли ми використовували непряме сортування за індексами у Розділі 3, для передачі масиву об'єктів у компаратор використовувався глобальний вказівник `g_tasks`. У системних багатопотокових серверах використання глобальних змінних призводить до гонитви даних (Data Race).
   Для забезпечення потокобезпечності стандарти C надають розширені функції:
   - POSIX / GNU C: `qsort_r(base, num, size, compar_arg, arg)` — контекст `arg` передається останнім аргументом у компаратор.
   - C11 / MSVC: `qsort_s(base, num, size, compar_arg, arg)` — контекст передається першим аргументом.

---

## 6. Використання сучасних компараторів `std::tie` та проєкцій C++20 `std::ranges::stable_sort`

У сучасній мові C++ (починаючи з C++11 та C++20) вишуканим і коротким способом написання багатокритеріальних компараторів є використання функції `std::tie` з бібліотеки `<tuple>` або проєкцій стандарту C++20.

Замість написання довгих каскадів `if-else` порівнянь:

```cpp
// Традиційний марудно написаний компаратор
bool compare_manual(const CityRecord& a, const CityRecord& b) {
    if (a.country != b.country) return a.country < b.country;
    if (a.city != b.city) return a.city < b.city;
    return a.population < b.population;
}

// Ідіоматичний та елегантний C++ компаратор через std::tie
bool compare_tuple(const CityRecord& a, const CityRecord& b) {
    return std::tie(a.country, a.city, a.population) <
           std::tie(b.country, b.city, b.population);
}
```

Функція `std::tie` створює кортеж посилань, для якого в стандартній бібліотеці C++ вже визначено лексикографічний оператор `<`. Це усуває можливість припуститися помилок у логіці складних ієрархічних порівнянь. У C++20 діапазони (`std::ranges::stable_sort`) дозволяють передавати проєкцію елемента через вказівник на член класу `&CityRecord::country`, що робить код надзвичайно читабельним та запобігає написанню дубльованого boilerplate-коду.

---

## 7. Поведінка стійкості у стандартних бібліотеках інших мов

Різні мови програмування по-різному підходять до контракту стійкості у своїх стандартних бібліотеках:

- **Python (`list.sort()`, `sorted()`):** Усі дефолтні сортування в Python є **100% стійкими**, оскільки Python із 2002 року використовує алгоритм Timsort. Це дозволяє розробникам Python виконувати послідовні сортування за різними ключами без побоювання втратити попередній порядок.
- **Java (`Arrays.sort()`, `Collections.sort()`):** Для масивів примітивних типів Java використовує Dual-Pivot Quicksort (нестійкий, бо для примітивів стійкість не має значення). Для масивів об'єктів (`Object[]`) та списків (`List<T>`) Java гарантує **стійке сортування** через Timsort або адаптивний Merge Sort.
- **C# / .NET (`Array.Sort` vs `Enumerable.OrderBy`):** У .NET стандартний метод `Array.Sort()` використовує нестійкий Introsort. Проте методи LINQ (`Enumerable.OrderBy` та `ThenBy`) гарантують **стійке сортування**, реалізуючи збереження початкового порядкового індексу елементів під час побудови послідовності.
- **Rust (`slice::sort` vs `slice::sort_unstable`):** Rust чітко розділяє алгоритми на рівні імен методів. Метод `slice::sort` гарантує стійкість і використовує адаптивне сортування злиттям, а метод `slice::sort_unstable` реалізує нестійкий Pattern-Defeating Quicksort (pdqsort), який працює швидше та не потребує додаткової пам'яті.
- **Go (`slices.Sort` vs `slices.SortStableFunc`):** У стандартній бібліотеці Go стандартна функція `slices.Sort` є нестійким pdqsort, тоді як для стійкого сортування розробники явно викликають `slices.SortStableFunc`.

---

## 8. Практичні рекомендації щодо вибору алгоритмів для High-Load та Embedded систем

При виборі між стійким та нестійким сортуванням у реальних проектувальних рішеннях керуйтеся такими правилами:

1. **Вбудовані системи (Embedded Systems / Microcontrollers):**
   У мікроконтролерах із суворим обмеженням RAM (наприклад, STM32 чи ESP32 із кількома кілобайтами RAM) використання `std::stable_sort` або Merge Sort вимагає виділення додаткового буфера O(N), що може викликати збій переповнення пам'яті (Out of Memory). Якщо даних небагато, використовуйте стійке **сортування вставками (Insertion Sort)**; якщо даних багато і стійкість критична — використовуйте **декорування індексів** або примусовий `std::stable_sort` із заздалегідь виділеним статичним буфером.

2. **Високонавантажені веб-сервери та бази даних (High-Load Backend):**
   У базах даних та сервісах обробки JSON/Protobuf вимагається **строга детермінованість виводу**. Сортування результатів SQL-запитів без стійкості може повертати різний порядок рядків при кожному повторному виклику API, що зламає pagination (посторінкову навігацію) та юніт-тести. Використовуйте стійкий сортувальник (`std::stable_sort` у C++, `timsort` у Python/Java, `slice::sort` у Rust).

---

## 9. Порівняльний бенчмарк швидкодії та пастки компараторів

Скільки коштує використання стійкого сортування у порівнянні з нестійким на великих масивах даних? Наведений нижче C++ бенчмарк порівнює `std::stable_sort` (нативний адаптивний Merge/Timsort) із процедурою декорування ключів над `std::sort`.

:::tabs
```cpp
// C++: Порівняння швидкодії std::stable_sort проти декорованого std::sort
#include <iostream>
#include <vector>
#include <random>
#include <chrono>
#include <algorithm>

struct BenchmarkItem {
    int key;
    int payload[8]; // Навантаження пам'яті
};

int main() {
    const size_t N = 1000000;
    std::cout << "Генерація " << N << " елементів з дубльованими ключами...\n";

    std::mt19937 rng(42);
    std::uniform_int_distribution<int> dist(1, 100); // Багато однаковіх ключів (від 1 до 100)

    std::vector<BenchmarkItem> data(N);
    for (size_t i = 0; i < N; ++i) {
        data[i].key = dist(rng);
        data[i].payload[0] = static_cast<int>(i);
    }

    // Тест 1: std::stable_sort (нативний Merge/Timsort)
    {
        auto test_data = data;
        auto start = std::chrono::high_resolution_clock::now();

        std::stable_sort(test_data.begin(), test_data.end(), [](const BenchmarkItem& a, const BenchmarkItem& b) {
            return a.key < b.key;
        });

        auto end = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double, std::milli> duration = end - start;
        std::cout << "Час std::stable_sort: " << duration.count() << " ms\n";
    }

    // Тест 2: Декорований std::sort (Key Augmentation + Introsort)
    {
        auto test_data = data;
        auto start = std::chrono::high_resolution_clock::now();

        struct Decorated {
            BenchmarkItem item;
            size_t orig_idx;
        };

        std::vector<Decorated> decorated(N);
        for (size_t i = 0; i < N; ++i) {
            decorated[i] = {test_data[i], i};
        }

        std::sort(decorated.begin(), decorated.end(), [](const Decorated& a, const Decorated& b) {
            if (a.item.key != b.item.key) return a.item.key < b.item.key;
            return a.orig_idx < b.orig_idx;
        });

        for (size_t i = 0; i < N; ++i) {
            test_data[i] = decorated[i].item;
        }

        auto end = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double, std::milli> duration = end - start;
        std::cout << "Час декорованого std::sort: " << duration.count() << " ms\n";
    }

    return 0;
}
```
:::

### Головні практичні пастки при роботі зі стійким сортуванням:

1. **Пастка оператора порівняння у C++ (`Strict Weak Ordering`):**
   У C++ предикат для `std::sort` та `std::stable_sort` повинен реалізовувати **строгий слабкий порядок**. Це означає, що для рівних елементів компаратор зобов'язаний повертати `false` (`a < b` при `a == b` має дати `false`). Спроба написати `return a.key <= b.key;` замість `return a.key < b.key;` є важкою помилкою, яка призводить до невизначеної поведінки (Undefined Behavior), виходу за межі масиву або фатального збою `Segmentation Fault` у реалізації `std::sort` через порушення вимог строгального порядку!

2. **Ілюзія стійкості при використанні нестійких суб-компараторів:**
   Якщо ви сортуєте об'єкти за двома полями одночасно в один прохід, перевіряючи спочатку перше поле, а потім друге, переконайтеся, що компаратор другого поля покриває **усі можливі властивості об'єкта**. Якщо після порівняння всіх полів компаратор повертає 0 для двох різних об'єктів з різними адресами, нестійкий сортувальник все одно може поміняти їх місцями у пам'яті.

3. **Обмеження пам'яті для `std::stable_sort`:**
   У C++ функція `std::stable_sort` намагається виділити додатковий буфер розміром `O(N)` у купі (heap). Якщо динамічна пам'ять обмежена або її виділення завершується помилкою `std::bad_alloc`, алгоритм не падає, а автоматично переключається на in-place сортування зліпками зі складністю `O(N log² N)`. Це може призвести до несподіваного сповільнення роботи програми у критичних умовах.

4. **Кеш-локальність та розмір обгортки декорування:**
   На сучасних процесорах із декількома рівнями кеш-пам'яті (L1/L2/L3) декорування великих структур `AugmentedItem<T>` погіршує кеш-локальність. Процесор змушений переміщати великі блоки даних під час кожного порівняння в `std::sort`. Використання масиву вказівників або індексних масивів `std::vector<size_t> indices` з наступним сортуванням самого індексного масиву за компаратором `vec[a] < vec[b]` є значно ефективнішим підходом для великих структур.
