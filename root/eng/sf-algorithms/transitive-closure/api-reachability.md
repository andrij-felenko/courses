# 📋 Інтерфейс та специфікація рушія досяжності (Reachability Engine API)

Ця вставка містить повну специфікацію програмного інтерфейсу (API) рушія обчислення та опитування досяжності у графі (`Reachability Engine`). Вона визначає публічний контракт мовами C та C++, структури даних, коди помилок, правила керування пам'яттю, контракти потокобезпечності (Thread Safety) та часові гарантії для інтеграції у високонавантажені системи безпеки (RBAC), системні аналізатори коду та бази даних.

---

### Архітектура та життєвий цикл рушія досяжності

Програмний рушій досяжності розроблений для роботи в двох основних режимах: пакетному (Batch Mode) та інкрементному (Incremental Dynamic Mode). У залежності від обраного режиму рушій проходить через декілька чітко визначених станів автоматного життєвого циклу:

1. **Стан ініціалізації (`UNINITIALIZED` → `CONFIGURED`):** 
   Під час виклику функції створення рушія `tc_engine_create()` виконується валідація конфігураційної структури `tc_config_t`. Перевіряється допустимість кількості вершин `vertices > 0`, обирається внутрішній режим обчислень `tc_mode_t` (скалярний, векторизований бітсет або розріджений DFS) та налаштовується прапорець автоматичної рефлексивності `auto_reflexive`. Якщо всі параметри коректні, система резервує неперервний блок оперативної пам'яті під матрицю досяжності і переводить рушій у стан `CONFIGURED`.

2. **Стан побудови графа (`BUILDING`):** 
   Наповнення графа вихідними орієнтованими ребрами виконується за допомогою послідовних викликів `tc_add_edge(engine, u, v)`. У пакетному режимі перевірки досяжності в цьому стані заблоковані або повертають помилку `TC_ERR_NOT_COMPUTED`, оскільки матриця замикання ще не була обрахована глобально. Кожен виклик `tc_add_edge()` на даному етапі встановлює бітові прапорці безпосередньої суміжності у внутрішній матриці за час `O(1)`.

3. **Стан обчислення та заморожування (`COMPUTING` → `FROZEN`):** 
   Виклик процедури `tc_compute(engine)` запускає векторизований алгоритм Уоршелла складності `O(V³ / 64)`. Упродовж цієї фази обчислень внесення нових ребер через `tc_add_edge()` блокується. Після завершення обрахунку прапорець `is_computed` встановлюється в значення `true`, а граф переходить у зафіксований стан `FROZEN`. У цьому стані будь-яка спроба модифікації структури графа викликає код помилки `TC_ERR_FROZEN`, що гарантує цілісність та незмінність обчисленої матриці.

4. **Стан високонавантажених запитів (`QUERYABLE`):** 
   Після переходу у стан `FROZEN` рушій надає миттєвий доступ до точкових запитів досяжності `tc_is_reachable(u, v)` за час `O(1)` або сканування всієї множини досяжних вершин `tc_get_reachable_set(u)` за час `O(V / 64)`. У цьому стані дозволено паралельний доступ із довільної кількості потоків без використання блокувальних м'ютексів чи атоміків (Lock-Free Multiple-Reader Read Operations).

---

### Керування пам'яттю, вирівнювання та кЕш-оптимізація

Щоб забезпечити максимальну швидкість читання при `50 000+` запитах на секунду, матриця досяжності упаковується у плоский одновимірний масив машинних слів `uint64_t`.

- **Вирівнювання пам'яті (Memory Alignment):** 
  Масив матриці вирівнюється на межу 64 байтів (розмір кЕш-лінійки більшості сучасних процесорів x86_64 та ARM64) за допомогою `posix_memalign` у C або `std::aligned_alloc` у C++20. Це виключає розщеплення кЕш-ліній (Cache Line Splitting) при векторизованому зчитуванні бітсетів за допомогою SIMD інструкцій AVX2 та AVX-512. Якщо вирівнювання відсутнє, завантаження 256-бітного регістра з межі двох кеш-ліній змушує процесор виконувати дві шинні операції зчитування замість однієї.

- **Уникнення фальшивого спільного використання (False Sharing):** 
  При паралельних запитах із декількох потоків масив матриці є строго read-only. Оскільки робочі потоки лише зчитують дані без виконання операцій запису у кеш-лінії, процесорні ядра не надсилають сигналів інвалідації кешу (Cache Invalidation Overhead / MESI Protocol Invalidation), що дає ідеальну лінійну масштабованість читання відносно кількості ядер CPU.

- **Формула розрахунку ширини рядка та обсягу пам'яті:** 
  Для графа з `V` вершинами кількість 64-бітних слів у кожному рядку обчислюється як:
  ```
  words_per_row = (V + 63) / 64
  ```
  Загальний обсяг виділеної оперативної пам'яті складає `V × words_per_row × sizeof(uint64_t)` байтів. Для графа з `V = 4000` вершин ширина рядка складає 63 слова (`504` байти), а загальний обсяг пам'яті під матрицю становить приблизно `2.016` Мегабайтів, що повністю вміщується у L3 кЕш сучасних процесорів.

---

### Безкопійна десеріалізація та миттєвий старт (Zero-Copy Persistence)

Для високонавантажених мікросервісів, які перезапускаються у хмарі (Kubernetes pods), критично важливо уникнути повторного кубічного обчислення транзитивного замикання `O(V³ / 64)` при кожному ініціалізуючому старті.

Формат пам'яті `reachability_engine_t` проектувався з урахуванням прямої безкопійної десеріалізації (Zero-Copy Deserialization). Оскільки заморожена бітова матриця є суцільним масивом без внутрішніх системних вказівників, її можна зберегти на диск як бінарний файл образу досяжності (`.tcimg`). При старті нового процесу сервіс виконує системний виклик `mmap()` у режимі `MAP_SHARED` або `MAP_PRIVATE`, підключаючи готовий бінарний файл безпосередньо з диска у свій віртуальний адресний простір.

Це дозволяє завантажувати обчислену матрицю досяжності розміром у сотні мегабайтів менш ніж за 1 мілісекунду без жодної операції парсингу JSON, Protobuf чи виділення пам'яті у купі, роблячи ініціалізацію сервісів безпеки практично миттєвою.

---

### Контракт потокобезпечності (Thread Safety) та паралельний доступ

У багатьох інженерних сценаріях (наприклад, у веб-серверах авторизації або базах даних) матриця досяжності обчислюється один раз при старті системи або при оновленні схеми прав доступу, після чого піддається інтенсивному опитуванню з сотень паралельних робочих потоків (Worker Threads).

1. **Гарантія для читаючих потоків (Multiple Readers):** 
   Після переходу рушія у стан `FROZEN` усі функції опитування досяжності `tc_is_reachable()` та `tc_get_reachable_set()` є повністю потокобезпечними (Thread-Safe) і не вимагають жодних зовнішніх м'ютексів, спінлоків чи читацько-письменницьких блокувань (`pthread_rwlock_t` або `std::shared_mutex`). Зчитування 64-бітних слів є атомарним на рівні шини процесора x86_64/ARM64.

2. **Ексклюзивний запис (Single Writer):** 
   Під час виконання процедур ініціалізації `tc_add_edge()` або обчислення `tc_compute()` доступ до об'єкта рушія мусить бути строго ексклюзивним. Якщо граф оновлюється динамічно в фоновому режимі, рекомендується використовувати патерн **Read-Copy-Update (RCU)** або **Double Buffering**: фоновий потік будує та обчислює нову версію `reachability_engine_t`, після чого атомарно змінює глобальний вказівник `std::atomic<reachability_engine_t*>` для всіх читаючих потоків.

---

### Сумісність із міжпроцесною пам'яттю (POSIX Shared Memory IPC)

Оскільки заморожена матриця досяжності є суцільним плоским масивом вирівняних байтів без внутрішніх вказівників чи посилань, об'єкт рушія можна легко розмістити у **спільній пам'яті процесів** (POSIX Shared Memory via `shm_open` та `mmap`).

Це дозволяє обчислити матрицю досяжності в єдиному майстер-процесі демона (Master Service Daemon), після чого надати доступ до читання `O(1)` для десятків ізольованих робочих процесів-клієнтів (Worker Processes) на цьому самому хості без викликів мережевого IPC, доменних сокетів Unix або міжпроцесного копіювання серіалізованих даних. Робочі процеси відображають масив матриці у власний адресний простір у режимі `PROT_READ | MAP_SHARED` і виконують точкові перевірки досяжності з нульовою затримкою.

---

### Сучасні шаблони C++20, концепти та оптимізація нульових накладних витрат

У сучасних стандартах мови C++ (C++20 та C++23) програмний інтерфейс рушія досяжності підтримує концептуальну стадійну оптимізацію (Compile-Time Concepts Check).

Використання C++20 концепту `template <typename T> requires std::unsigned_integral<T>` для індексів вершин дозволяє уникнути будь-яких прихованих копіювань чи приведень типів при передачі вузлів. Функція `getReachableSet()` підтримує повернення безпечних зрізів пам'яті через `std::span<const size_t>`, що виключає дублювання масивів у пам'яті та гарантує виконання принципу Zero-Overhead Abstraction.

---

### Стабільність ABI, непрозорі хендли та версіонування

При постачанні рушія досяжності у вигляді динамічної системної бібліотеки (`.so` у Linux, `.dylib` у macOS або `.dll` у Windows) критично важливо забезпечити стабільність бінарного інтерфейсу додатків (Application Binary Interface, ABI):

- **Непрозорі вказівники (Opaque Struct Handles):** 
  Структура `reachability_engine_t` декларується у заголовочному файлі `reachability.h` як непрозорий тип без розкриття її полів (`typedef struct reachability_engine reachability_engine_t;`). Вся внутрішня реалізація (поля розміру, прапорці, вказівник `bit_matrix`) схована всередині C-файлу. Це дозволяє розробникам бібліотеки змінювати внутрішні структури даних або додавати векторизацію AVX-512 без порушення сумісності з уже скомпільованими клієнтськими програмами.

- **Запобігання викривленню імен (C Name Mangling Protection):** 
  Для забезпечення сумісності з компіляторами C++ усі функції C API обгорнуті в макрос `#ifdef __cplusplus extern "C" { ... }`. Це гарантує створення класичних C-символів у таблиці експорту динамічної бібліотеки без декорування типів.

- **Макроси версіонування API:** 
  Заголовочний файл визначає макроси версії `REACHABILITY_API_VERSION_MAJOR (1)` та `REACHABILITY_API_VERSION_MINOR (0)`, що дозволяє клієнтському коду виконувати перевірки сумісності під час компіляції за допомогою препроцесора.

---

### Детальний опис типів даних та кодів помилок C API

Для забезпечення надійної взаємодії у системних мовах програмування C API визначає суворий перелік кодів помилок `tc_status_t`. Кожна функція бібліотеки повертає один із цих кодів, що дозволяє детально діагностувати будь-які виняткові ситуації під час виконання:

- **`TC_SUCCESS (0)`:** 
  Операція була виконана без жодних відхилень. Усі вхідні аргументи були валідними, а необхідна пам'ять була успішно виділена.

- **`TC_ERR_NULL_POINTER (-1)`:** 
  У функцію було передано некоректний вказівник `NULL` замість вказівника на об'єкт рушія `reachability_engine_t`, конфігураційну структуру `tc_config_t` або буфер результату `out_reachable`.

- **`TC_ERR_INVALID_VERTEX (-2)`:** 
  Вказаний індекс вершини `u` або `v` знаходиться поза допустимим діапазоном `[0, V - 1]`. Цей код помилки захищає від виходу за межі виділеного масиву пам'яті (Buffer Overflow Protection) та запобігає потенційним вразливостям безпеки при роботі з ненадійними вхідними даними.

- **`TC_ERR_NO_MEMORY (-3)`:** 
  Системній функції виділення пам'яті `calloc` чи `posix_memalign` не вдалося зарезервувати необхідний блок ОЗП під матрицю досяжності. Додаток мусить обробити цю помилку і вивільнити проміжні ресурси.

- **`TC_ERR_FROZEN (-4)`:** 
  Викликано операцію додавання ребра `tc_add_edge()` після того, як граф вже був обчислений і переведений у зафіксований стан `FROZEN`. Додавання нових ребер у заморожений граф вимагає перезапуску або використання інкрементного рушія.

- **`TC_ERR_NOT_COMPUTED (-5)`:** 
  Виконано точковий запит досяжності `tc_is_reachable()` або витягнення множини `tc_get_reachable_set()` до того, як був викликаний метод обрахунку замикання `tc_compute()`. Захищає від зчитування недостовірних або часткових даних.

---

### Специфікація інтерфейсу мовою C (`reachability.h`) та C++ (`ReachabilityEngine.hpp`)

Нижче наведено специфікацію заголовочних файлів та декларацій API для системних заголовочнихфайлів мовами C та C++.

:::tabs
```c
#ifndef REACHABILITY_H
#define REACHABILITY_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

#define REACHABILITY_API_VERSION_MAJOR 1
#define REACHABILITY_API_VERSION_MINOR 0

typedef enum {
    TC_SUCCESS            =  0,
    TC_ERR_NULL_POINTER   = -1,
    TC_ERR_INVALID_VERTEX = -2,
    TC_ERR_NO_MEMORY      = -3,
    TC_ERR_FROZEN         = -4,
    TC_ERR_NOT_COMPUTED   = -5
} tc_status_t;

typedef enum {
    TC_MODE_WARSHALL_SCALAR  = 0,
    TC_MODE_WARSHALL_BITSET  = 1,
    TC_MODE_SPARSE_DFS       = 2
} tc_mode_t;

typedef struct {
    size_t vertices;
    tc_mode_t mode;
    bool auto_reflexive;
} tc_config_t;

typedef struct reachability_engine reachability_engine_t;

#ifdef __cplusplus
extern "C" {
#endif

tc_status_t tc_engine_create(const tc_config_t *config, reachability_engine_t **out_engine);
void tc_engine_destroy(reachability_engine_t *engine);
tc_status_t tc_add_edge(reachability_engine_t *engine, size_t u, size_t v);
tc_status_t tc_compute(reachability_engine_t *engine);
tc_status_t tc_is_reachable(const reachability_engine_t *engine, size_t u, size_t v, bool *out_reachable);
tc_status_t tc_get_reachable_set(const reachability_engine_t *engine, size_t u, size_t *out_vertices, size_t *out_count);

#ifdef __cplusplus
}
#endif

#endif // REACHABILITY_H
```
```cpp
#pragma once

#include <vector>
#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <span>

namespace graph::analytics {

enum class AlgorithmMode {
    ScalarWarshall,
    BitsetVectorized,
    SparseDFS
};

struct EngineConfig {
    size_t vertices;
    AlgorithmMode mode{AlgorithmMode::BitsetVectorized};
    bool auto_reflexive{false};
};

enum class Status {
    Success = 0,
    NullPointer = -1,
    InvalidVertex = -2,
    NoMemory = -3,
    Frozen = -4,
    NotComputed = -5
};

class ReachabilityEngine {
public:
    explicit ReachabilityEngine(const EngineConfig& config);
    ~ReachabilityEngine() noexcept;

    ReachabilityEngine(const ReachabilityEngine&) = delete;
    ReachabilityEngine& operator=(const ReachabilityEngine&) = delete;

    ReachabilityEngine(ReachabilityEngine&&) noexcept;
    ReachabilityEngine& operator=(ReachabilityEngine&&) noexcept;

    void addEdge(size_t u, size_t v);
    void compute();
    [[nodiscard]] bool isReachable(size_t u, size_t v) const;
    [[nodiscard]] std::vector<size_t> getReachableSet(size_t u) const;
    [[nodiscard]] size_t vertexCount() const noexcept;
    [[nodiscard]] bool isComputed() const noexcept;

private:
    class Impl;
    Impl* impl_;
};

} // namespace graph::analytics
```
:::

---

### Детальний простежувальний аналіз функцій API

Розглянемо детальніше внутрішній механізм роботи двох найважливіших функцій API — `tc_add_edge` та `tc_is_reachable`:

#### Функція `tc_add_edge(engine, u, v)`
1. **Перевірка входів:** Спочатку перевіряється, чи не є `engine` нульовим вказівником (`NULL`). У разі невдачі повертається `TC_ERR_NULL_POINTER`.
2. **Перевірка меж індексів:** Оцінюються умови `u < engine->vertices` та `v < engine->vertices`. Якщо один із індексів виходить за межі, повертається `TC_ERR_INVALID_VERTEX`.
3. **Обчислення бітового зсуву:** Індекс `v` розбивається на індекс слова `word_idx = v / 64` та побітовий зсув `bit_shift = v % 64`.
4. **Запис у матрицю:** Виконується побітова операція `engine->bit_matrix[u * words_per_row + word_idx] |= (1ULL << bit_shift)`.
5. **Повернення:** Повертається статусне значення `TC_SUCCESS`.

#### Функція `tc_is_reachable(engine, u, v, out_reachable)`
1. **Перевірка стану обчислення:** Функція перевіряє прапорець `is_computed`. Якщо обчислення транзитивного замикання ще не виконувалося, повертається `TC_ERR_NOT_COMPUTED`.
2. **Побітове зчитування за O(1):** Для пари `(u, v)` витягується відповідний біт за формулою:
:::tabs
```c
uint64_t word = engine->bit_matrix[u * words_per_row + (v / 64)];
*out_reachable = (word & (1ULL << (v % 64))) != 0;
```
```cpp
const uint64_t word = bit_matrix_[u * words_per_row_ + (v / 64)];
return (word & (1ULL << (v % 64))) != 0;
```
:::
3. **Часова складність:** Операція зчитування виконує строго дві машинні інструкції (зсув та побітове І), що гарантує час виконання `O(1)` при суцільній відсутності блокувань потоків.

---

### Повна реалізація API на мовах C та C++

Приклад повної внутрішньої реалізації хендлів рушія та його безпечної C++ обгортки (RAII):

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

struct reachability_engine {
    size_t vertices;
    size_t words_per_row;
    tc_mode_t mode;
    bool auto_reflexive;
    bool is_computed;
    bool is_frozen;
    uint64_t *bit_matrix;
};

tc_status_t tc_engine_create(const tc_config_t *config, reachability_engine_t **out_engine) {
    if (!config || !out_engine) return TC_ERR_NULL_POINTER;
    if (config->vertices == 0) return TC_ERR_INVALID_VERTEX;

    reachability_engine_t *eng = (reachability_engine_t*)malloc(sizeof(reachability_engine_t));
    if (!eng) return TC_ERR_NO_MEMORY;

    eng->vertices = config->vertices;
    eng->words_per_row = (config->vertices + 63) / 64;
    eng->mode = config->mode;
    eng->auto_reflexive = config->auto_reflexive;
    eng->is_computed = false;
    eng->is_frozen = false;

    size_t total_words = eng->vertices * eng->words_per_row;
    eng->bit_matrix = (uint64_t*)calloc(total_words, sizeof(uint64_t));
    if (!eng->bit_matrix) {
        free(eng);
        return TC_ERR_NO_MEMORY;
    }

    if (eng->auto_reflexive) {
        for (size_t i = 0; i < eng->vertices; ++i) {
            size_t word_idx = i * eng->words_per_row + (i / 64);
            eng->bit_matrix[word_idx] |= (1ULL << (i % 64));
        }
    }

    *out_engine = eng;
    return TC_SUCCESS;
}

void tc_engine_destroy(reachability_engine_t *engine) {
    if (!engine) return;
    free(engine->bit_matrix);
    free(engine);
}

tc_status_t tc_add_edge(reachability_engine_t *engine, size_t u, size_t v) {
    if (!engine) return TC_ERR_NULL_POINTER;
    if (u >= engine->vertices || v >= engine->vertices) return TC_ERR_INVALID_VERTEX;
    if (engine->is_frozen) return TC_ERR_FROZEN;

    size_t word_idx = u * engine->words_per_row + (v / 64);
    engine->bit_matrix[word_idx] |= (1ULL << (v % 64));
    return TC_SUCCESS;
}

tc_status_t tc_compute(reachability_engine_t *engine) {
    if (!engine) return TC_ERR_NULL_POINTER;
    const size_t v = engine->vertices;
    const size_t wpr = engine->words_per_row;
    uint64_t *m = engine->bit_matrix;

    for (size_t k = 0; k < v; ++k) {
        size_t k_word = k / 64;
        uint64_t k_mask = (1ULL << (k % 64));

        for (size_t i = 0; i < v; ++i) {
            if ((m[i * wpr + k_word] & k_mask) != 0) {
                uint64_t *row_i = &m[i * wpr];
                const uint64_t *row_k = &m[k * wpr];
                for (size_t w = 0; w < wpr; ++w) {
                    row_i[w] |= row_k[w];
                }
            }
        }
    }

    engine->is_computed = true;
    engine->is_frozen = true;
    return TC_SUCCESS;
}

tc_status_t tc_is_reachable(const reachability_engine_t *engine, size_t u, size_t v, bool *out_reachable) {
    if (!engine || !out_reachable) return TC_ERR_NULL_POINTER;
    if (u >= engine->vertices || v >= engine->vertices) return TC_ERR_INVALID_VERTEX;
    if (!engine->is_computed) return TC_ERR_NOT_COMPUTED;

    size_t word_idx = u * engine->words_per_row + (v / 64);
    *out_reachable = (engine->bit_matrix[word_idx] & (1ULL << (v % 64))) != 0;
    return TC_SUCCESS;
}

tc_status_t tc_get_reachable_set(const reachability_engine_t *engine, size_t u, size_t **out_vertices, size_t *out_count) {
    if (!engine || !out_vertices || !out_count) return TC_ERR_NULL_POINTER;
    if (u >= engine->vertices) return TC_ERR_INVALID_VERTEX;
    if (!engine->is_computed) return TC_ERR_NOT_COMPUTED;

    size_t wpr = engine->words_per_row;
    const uint64_t *row_u = &engine->bit_matrix[u * wpr];

    size_t count = 0;
    for (size_t v = 0; v < engine->vertices; ++v) {
        if ((row_u[v / 64] & (1ULL << (v % 64))) != 0) {
            count++;
        }
    }

    size_t *res = (size_t*)malloc(count * sizeof(size_t));
    if (!res && count > 0) return TC_ERR_NO_MEMORY;

    size_t idx = 0;
    for (size_t v = 0; v < engine->vertices; ++v) {
        if ((row_u[v / 64] & (1ULL << (v % 64))) != 0) {
            res[idx++] = v;
        }
    }

    *out_vertices = res;
    *out_count = count;
    return TC_SUCCESS;
}
```
```cpp
#include <vector>
#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <memory>

namespace graph::analytics {

class ReachabilityEngine::Impl {
private:
    EngineConfig config_;
    size_t words_per_row_;
    bool is_computed_{false};
    bool is_frozen_{false};
    std::vector<uint64_t> bit_matrix_;

public:
    explicit Impl(const EngineConfig& config)
        : config_(config),
          words_per_row_((config.vertices + 63) / 64),
          bit_matrix_(config.vertices * ((config.vertices + 63) / 64), 0) {
        if (config.vertices == 0) {
            throw std::invalid_argument("Vertex count must be > 0");
        }
        if (config.auto_reflexive) {
            for (size_t i = 0; i < config.vertices; ++i) {
                const size_t word_idx = i * words_per_row_ + (i / 64);
                bit_matrix_[word_idx] |= (1ULL << (i % 64));
            }
        }
    }

    void addEdge(size_t u, size_t v) {
        if (u >= config_.vertices || v >= config_.vertices) {
            throw std::out_of_range("Vertex index out of range");
        }
        if (is_frozen_) {
            throw std::logic_error("Engine is frozen after computation");
        }
        const size_t word_idx = u * words_per_row_ + (v / 64);
        bit_matrix_[word_idx] |= (1ULL << (v % 64));
    }

    void compute() {
        const size_t v = config_.vertices;
        const size_t wpr = words_per_row_;
        uint64_t* m = bit_matrix_.data();

        for (size_t k = 0; k < v; ++k) {
            const size_t k_word = k / 64;
            const uint64_t k_mask = (1ULL << (k % 64));

            for (size_t i = 0; i < v; ++i) {
                if ((m[i * wpr + k_word] & k_mask) != 0) {
                    uint64_t* row_i = &m[i * wpr];
                    const uint64_t* row_k = &m[k * wpr];
                    for (size_t w = 0; w < wpr; ++w) {
                        row_i[w] |= row_k[w];
                    }
                }
            }
        }
        is_computed_ = true;
        is_frozen_ = true;
    }

    [[nodiscard]] bool isReachable(size_t u, size_t v) const {
        if (u >= config_.vertices || v >= config_.vertices) return false;
        if (!is_computed_) throw std::logic_error("Transitive closure not computed");
        const size_t word_idx = u * words_per_row_ + (v / 64);
        return (bit_matrix_[word_idx] & (1ULL << (v % 64))) != 0;
    }

    [[nodiscard]] std::vector<size_t> getReachableSet(size_t u) const {
        if (u >= config_.vertices) throw std::out_of_range("Vertex out of range");
        if (!is_computed_) throw std::logic_error("Transitive closure not computed");

        std::vector<size_t> result;
        const size_t wpr = words_per_row_;
        const uint64_t* row_u = &bit_matrix_[u * wpr];

        for (size_t v = 0; v < config_.vertices; ++v) {
            if ((row_u[v / 64] & (1ULL << (v % 64))) != 0) {
                result.push_back(v);
            }
        }
        return result;
    }

    [[nodiscard]] size_t vertexCount() const noexcept { return config_.vertices; }
    [[nodiscard]] bool isComputed() const noexcept { return is_computed_; }
};

ReachabilityEngine::ReachabilityEngine(const EngineConfig& config)
    : impl_(new Impl(config)) {}

ReachabilityEngine::~ReachabilityEngine() noexcept {
    delete impl_;
}

void ReachabilityEngine::addEdge(size_t u, size_t v) { impl_->addEdge(u, v); }
void ReachabilityEngine::compute() { impl_->compute(); }
bool ReachabilityEngine::isReachable(size_t u, size_t v) const { return impl_->isReachable(u, v); }
std::vector<size_t> ReachabilityEngine::getReachableSet(size_t u) const { return impl_->getReachableSet(u); }
size_t ReachabilityEngine::vertexCount() const noexcept { return impl_->vertexCount(); }
bool ReachabilityEngine::isComputed() const noexcept { return impl_->isComputed(); }

} // namespace graph::analytics
```
:::

---

### Приклади використання та інженерні сценарії

#### Сценарій 1: Системна авторизація у C (RBAC Permission Checker)

У великій корпоративній системі користувачеві виділено роль `User (ID: 5)`, яка є членом групи `Engineering (ID: 12)`, що в свою чергу володіє правом доступу `DB_WRITE (ID: 105)`. Завдяки рушію досяжності перевірка прав у сервері авторизації виконується за лічені наносекунди:

:::tabs
```c
#include "reachability.h"
#include <stdio.h>

void check_rbac_permission(void) {
    tc_config_t cfg = {
        .vertices = 1000,
        .mode = TC_MODE_WARSHALL_BITSET,
        .auto_reflexive = true
    };

    reachability_engine_t *engine = NULL;
    if (tc_engine_create(&cfg, &engine) != TC_SUCCESS) {
        fprintf(stderr, "Failed to create reachability engine\n");
        return;
    }

    // Додаємо зв'язки ролей: User 5 -> Role 12 -> Permission 105
    tc_add_edge(engine, 5, 12);
    tc_add_edge(engine, 12, 105);

    tc_compute(engine);

    bool can_access = false;
    if (tc_is_reachable(engine, 5, 105, &can_access) == TC_SUCCESS) {
        if (can_access) {
            printf("Access GRANTED for user 5 to permission 105\n");
        }
    }

    tc_engine_destroy(engine);
}
```
```cpp
#include "ReachabilityEngine.hpp"
#include <iostream>

void checkRbacPermissionCpp() {
    using namespace graph::analytics;

    EngineConfig cfg{
        .vertices = 1000,
        .mode = AlgorithmMode::BitsetVectorized,
        .auto_reflexive = true
    };

    ReachabilityEngine engine(cfg);

    // Додаємо зв'язки ролей: User 5 -> Role 12 -> Permission 105
    engine.addEdge(5, 12);
    engine.addEdge(12, 105);

    engine.compute();

    if (engine.isReachable(5, 105)) {
        std::cout << "Access GRANTED for user 5 to permission 105\n";
    }
}
```
:::

#### Сценарій 2: Витягнення множини всіх досяжних вузлів

Для проведення аудиту безпеки адміністратор може витягнути список абсолютно всіх прав та ресурсів, до яких користувач `5` має прямий або непрямий доступ:

:::tabs
```c
void audit_user_permissions(reachability_engine_t *engine, size_t user_id) {
    size_t *reachable_nodes = NULL;
    size_t count = 0;

    if (tc_get_reachable_set(engine, user_id, &reachable_nodes, &count) == TC_SUCCESS) {
        printf("User %zu has access to %zu permissions/roles:\n", user_id, count);
        for (size_t i = 0; i < count; ++i) {
            printf(" - Node ID: %zu\n", reachable_nodes[i]);
        }
        free(reachable_nodes); // Обов'язкове звільнення виділеної масивної пам'яті
    }
}
```
```cpp
void auditUserPermissionsCpp(const graph::analytics::ReachabilityEngine& engine, size_t userId) {
    std::vector<size_t> reachableNodes = engine.getReachableSet(userId);
    std::cout << "User " << userId << " has access to " << reachableNodes.size() << " permissions/roles:\n";
    for (size_t nodeId : reachableNodes) {
        std::cout << " - Node ID: " << nodeId << "\n";
    }
}
```
:::

---

### Обробка помилок та інваріанти захищеного програмування

При інтеграції рушія у промислові сервери критично важливо дотримуватися правил безпечної розробки (Defensive Programming Practices):

1. **Захист від Buffer Overflow:** 
   Усі вхідні індекси вершин `u` та `v` проходять перевірку через сувору умову `u < vertices && v < vertices`. У разі спроби передачі від'ємного значення (або числа, приведеного з від'ємного `int`) чи індексу за межами графа функція миттєво припиняє виконання та повертає статус `TC_ERR_INVALID_VERTEX`.

2. **Забігання витокам пам'яті при винятках у C++:** 
   Використання ідіоми PImpl (Pointer to Implementation) та контейнера `std::vector<uint64_t>` всередині класу `ReachabilityEngine::Impl` забезпечує строгі гарантії безпеки винятків (Strong Exception Guarantee). Якщо під час виконання метода `getReachableSet()` виділення пам'яті під результат викликає виняток `std::bad_alloc`, стан самого рушія залишається повністю цілісним та замороженим для подальших читань.

3. **Логування та метрики продуктивності Prometheus:** 
   Для інтеграції у системні сервери підтримується експорт лічильників метрик: загальна кількість перевірок досяжності `reachability_queries_total`, середня затримка виконання точкового запиту `reachability_query_duration_nanoseconds` та обсяг споживаного ОЗП `reachability_memory_bytes`.
