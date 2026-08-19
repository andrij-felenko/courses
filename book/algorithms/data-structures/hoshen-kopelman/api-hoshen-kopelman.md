# 📋 Специфікація інтерфейсу та контракт бібліотеки Hoshen–Kopelman

Бібліотека `libhoshenkopelman` надає високоефективний програмний інтерфейс для маркування зв'язаних кластерів, аналізу перколяційних структур та обчислення статистичних характеристик на двовимірних і тривимірних регулярних ґратках. Інтерфейс спроєктовано за принципом нульових накладних витрат (Zero-Overhead Abstraction), що дозволяє використовувати бібліотеку як у пакетному режимі (Batch Processing), так і в однопрохідному потоковому режимі (Streaming Mode) з мінімальним споживанням оперативної пам'яті `O(L)`.

Нижче наведено повну структурну специфікацію типів даних, сигнатур функцій, умов контрактів, гарантій винятків та протоколів взаємодії для мов C та C++.

## 1. Архітектурні принципи та інваріанти інтерфейсу

1. **Відокремлення сканування від збереження результату**:
   Користувач може передавати бінарну ґратку рядок за рядком (або 2D-зріз за зрізом для 3D). Бібліотека не вимагає попереднього завантаження всього масиву в оперативну пам'ять, що дозволяє обробляти терапіксельні масиви з фіксованим робочим буфером.
2. **Нульове динамічне виділення пам'яті у гарячому циклі**:
   Усі робочі буфери сусідок виділяються одноразово під час створення дескриптора контексту `hk_context_t` або об'єкта `GridLabeler`. Під час обробки рядка пам'ять динамічно розширюється лише у разі вичерпання місткості масиву міток за геометричною прогресією (коефіцієнт зростання 2.0).
3. **Строга безпека пам'яті та володіння ресурсами (Resource Ownership)**:
   Бібліотека чітко розмежовує вхідні буфери користувача (передаються як константні покажчики або `std::span<const uint8_t>`) та внутрішні таблиці еквівалентностей. Вхідні дані ніколи не модифікуються бібліотекою.
4. **Детермінізм та відтворюваність результатів**:
   Порядок нумерації канонічних кластерів `1..K` строго детермінований і визначається топологічним порядком першої появи кожного кластера під час растрового сканування згори вниз і зліва направо.

## 2. Константи, типи переліків та коди помилок

### Коди завершення операцій

Кожна функція C API повертає статус виконання через перелік `hk_error_t`, тоді як C++ API використовує винятки або типи повернення зі статусом.

:::tabs
```c
typedef enum {
    HK_SUCCESS                =  0,  /* Операція завершилася успішно без помилок */
    HK_ERROR_NULL_PTR         = -1,  /* Передано нульовий покажчик (NULL) у критичний аргумент */
    HK_ERROR_INVALID_DIM      = -2,  /* Некоректні просторові розміри (width <= 0, height <= 0) */
    HK_ERROR_OUT_OF_MEMORY    = -3,  /* Помилка виділення динамічної пам'яті (malloc повернув NULL) */
    HK_ERROR_INVALID_STATE    = -4,  /* Виклик функції у невідповідному стані контексту */
    HK_ERROR_ROW_OVERFLOW     = -5,  /* Спроба передати більше рядків, ніж задекларовано при створенні */
    HK_ERROR_BUFFER_TOO_SMALL = -6   /* Наданий користувачем вихідний масив є замалим */
} hk_error_t;
```
```cpp
enum class ErrorCode {
    Success = 0,
    NullPointer = -1,
    InvalidDimensions = -2,
    OutOfMemory = -3,
    InvalidState = -4,
    RowOverflow = -5,
    BufferTooSmall = -6
};
```
:::

### Детальний опис значень статусів помилок

- **`HK_SUCCESS`**: Команда виконана успішно. Усі вихідні структури містять коректні дані, інваріанти структури збережено.
- **`HK_ERROR_NULL_PTR`**: Функція отримала `NULL` для аргументів, які обов'язково повинні вказувати на дійсні об'єкти пам'яті (наприклад, дескриптор `ctx`, вхідний масив `row_input` або покажчик для запису статистики `stats_out`). Внутрішній стан бібліотеки не змінюється.
- **`HK_ERROR_INVALID_DIM`**: Просторові розміри `width`, `height` або `depth` мають значення менше або рівне 0, або перевищують максимально допустимий цілочисельний ліміт `INT_MAX / 2`.
- **`HK_ERROR_OUT_OF_MEMORY`**: Системний виклик `malloc` або `realloc` повернув `NULL`. Бібліотека гарантує сильну безпеку винятків: попередньо виділені ресурси залишаються валідними, що дозволяє користувачеві коректно закрити контекст.
- **`HK_ERROR_INVALID_STATE`**: Порушено протокол викликів автомата станів (наприклад, спроба викликати `hk_get_stats` до завершення сканування `hk_finalize`, або спроба повторного додавання рядків після фіналізації).
- **`HK_ERROR_ROW_OVERFLOW`**: Функція `hk_process_row` викликана більше разів, ніж параметр `height`, задекларований при створенні контексту.
- **`HK_ERROR_BUFFER_TOO_SMALL`**: Розмір масиву, наданого користувачем для збереження розмірів кластерів або розміченої ґратки, менший за фактичну кількість елементів.

### Режими граничних умов та зв'язності

:::tabs
```c
/* Режими просторових границь */
typedef enum {
    HK_BOUNDARY_OPEN     = 0,  /* Відкриті границі: вузли за межами сітки вважаються порожніми */
    HK_BOUNDARY_PERIODIC = 1   /* Періодичні тороїдальні границі: протилежні краї замкнені */
} hk_boundary_t;

/* Топологічна зв'язність сусідів */
typedef enum {
    HK_CONNECTIVITY_4  = 4,    /* 2D: 4-зв'язність (спільні ребра: Top, Bottom, Left, Right) */
    HK_CONNECTIVITY_8  = 8,    /* 2D: 8-зв'язність (ребра та діагоналі) */
    HK_CONNECTIVITY_6  = 6,    /* 3D: 6-зв'язність (спільні грані кубічних комірок) */
    HK_CONNECTIVITY_26 = 26    /* 3D: 26-зв'язність (грані, ребра та кутові вершини) */
} hk_connectivity_t;
```
```cpp
enum class BoundaryCondition {
    Open = 0,       // Відкриті (фіксовані) границі
    Periodic = 1    // Періодичні (тороїдальні) границі
};

enum class Connectivity {
    Four = 4,       // 2D 4-зв'язність
    Eight = 8,      // 2D 8-зв'язність
    Six = 6,        // 3D 6-зв'язність
    TwentySix = 26  // 3D 26-зв'язність
};
```
:::

## 3. Структури статистичних даних та дескрипторів

### Фізична статистика кластерної конфігурації

Структура `hk_stats_t` містить повний набір фізичних спостережуваних величин, обчислених за результатами сканування ґратки.

:::tabs
```c
typedef struct {
    int total_clusters;            /* Загальна кількість незалежних зв'язаних кластерів */
    int total_occupied_sites;      /* Загальна кількість зайнятих вузлів на ґратці */
    int max_cluster_size;          /* Розмір (кількість вузлів) найбільшого знайденого кластера */
    double mean_cluster_size;      /* Зважений середній розмір скінченних кластерів S(p) = M_2 / M_1 */
    double cluster_density;        /* Питома кількість кластерів на один вузол ґратки M_0 = K / N */
    bool has_spanning_cluster_x;   /* Наявність протікання вздовж осі X (зліва направо) */
    bool has_spanning_cluster_y;   /* Наявність протікання вздовж осі Y (згори вниз) */
    bool has_spanning_cluster_z;   /* Наявність протікання вздовж осі Z (вглиб, для 3D) */
} hk_stats_t;
```
```cpp
struct PercolationStats {
    int total_clusters{0};
    int total_occupied_sites{0};
    int max_cluster_size{0};
    double mean_cluster_size{0.0};
    double cluster_density{0.0};
    bool has_spanning_cluster_x{false};
    bool has_spanning_cluster_y{false};
    bool has_spanning_cluster_z{false};
};
```
:::

#### Опис полів структури статистики:
- `total_clusters`: Кількість неперетинних компонентів зв'язності `K`. Дорівнює числу додатних канонічних міток.
- `total_occupied_sites`: Сума розмірів усіх знайдених кластерів. Дорівнює загальній кількості одиниць у вхідній ґратці `N_occ = ∑ t_i`.
- `max_cluster_size`: Кількість вузлів у гігантському (найбільшому) кластері `s_max = max(s_i)`.
- `mean_cluster_size`: Фізичний середній розмір кластера `S(p) = (∑ s_i²) / (∑ s_i)`, обчислений без урахування протікаючого кластера (якщо протікання виявлено). Слугує чисельним індикатором наближення до порогу перколації.
- `cluster_density`: Відношення загальної кількості кластерів до площі/об'єму системи `n = K / N`.
- `has_spanning_cluster_x/y/z`: Бінарні прапорці макроскопічного протікання за відповідними просторовими осями.

### Геометричні характеристики окремого кластера

:::tabs
```c
typedef struct {
    int cluster_id;                /* Канонічний порядковий номер кластера (1..total_clusters) */
    int size;                      /* Маса кластера (кількість зайнятих вузлів) */
    double center_of_mass_x;       /* Координата X геометричного центру мас */
    double center_of_mass_y;       /* Координата Y геометричного центру мас */
    double center_of_mass_z;       /* Координата Z геометричного центру мас (0.0 для 2D) */
    double radius_of_gyration;     /* Радіус гірації R_s (просторова протяжність) */
    bool touches_boundary;         /* Прапорець торкання хоча б однієї геометричної межі */
} hk_cluster_info_t;
```
```cpp
struct ClusterInfo {
    int cluster_id{0};
    int size{0};
    double center_of_mass_x{0.0};
    double center_of_mass_y{0.0};
    double center_of_mass_z{0.0};
    double radius_of_gyration{0.0};
    bool touches_boundary{false};
};
```
:::

## 4. Специфікація функцій управління життєвим циклом

### Створення та знищення контексту

Управління ресурсами в C API базується на непрозорому дескрипторі `hk_context_t`, тоді як у C++ використовується парадигма RAII (Resource Acquisition Is Initialization).

:::tabs
```c
/* Створення контексту для обробки 2D ґратки */
hk_error_t hk_context_create_2d(
    hk_context_t** ctx_out,
    int width,
    int height,
    hk_connectivity_t connectivity,
    hk_boundary_t boundary
);

/* Звільнення всіх ресурсів контексту */
void hk_context_destroy(hk_context_t* ctx);

/* Очищення стану контексту для обробки нової ґратки тих самих розмірів */
hk_error_t hk_context_reset(hk_context_t* ctx);
```
```cpp
// Конструктор класу ініціалізує всі необхідні буфери
// Деструктор автоматично звільняє виділені ресурси
class GridLabeler2D {
public:
    explicit GridLabeler2D(
        int width,
        int height,
        Connectivity connectivity = Connectivity::Four,
        BoundaryCondition boundary = BoundaryCondition::Open
    );
    ~GridLabeler2D();

    void reset();
};
```
:::

#### Контракт виконання:
- **Перед-умови**: `width >= 1`, `height >= 1`, `ctx_out != NULL`. Параметри `connectivity` та `boundary` повинні належати відповідним типам переліків.
- **Пост-умови**: Створено дескриптор із внутрішнім буфером рядка розміром `width · sizeof(int)` та вектором міток DSU початкової місткості `max(1024, (width · height) / 4)`.
- **Гарантія безпеки**: Функція `hk_context_destroy` безпечно приймає `NULL`.

## 5. Специфікація потокових операцій сканування

### Обробка рядків та зрізів у реальному часі

Функція `hk_process_row` виконує перший прохід растрового сканування. Вона зчитує вхідні бінарні байти поточного рядка, порівнює їх із попереднім буфером і призначає тимчасові мітки.

:::tabs
```c
/* Обробка одного рядка 2D ґратки */
hk_error_t hk_process_row(
    hk_context_t* ctx,
    const uint8_t* row_input,
    int* row_output_labels
);

/* Обробка одного 2D зрізу 3D ґратки */
hk_error_t hk_process_slice_3d(
    hk_context_t* ctx,
    const uint8_t* slice_input,
    int* slice_output_labels
);
```
```cpp
// Потокова обробка рядка у C++
void process_row(
    std::span<const uint8_t> binary_row,
    std::optional<std::span<int>> output_labels = std::nullopt
);

// Потокова обробка 3D зрізу у C++
void process_slice_3d(
    std::span<const uint8_t> binary_slice,
    std::optional<std::span<int>> output_labels = std::nullopt
);
```
:::

#### Контракт виконання:
- **Перед-умови**: Контекст перебуває у стані `INITIALIZED` або `PROCESSING`. Кількість викликів не перевищує параметр `height` (або `depth`). Масив `row_input` містить щонайменше `width` байтів.
- **Параметр `row_output_labels`**: Може бути `NULL` (або `std::nullopt`), якщо користувача цікавить лише підсумкова фізична статистика без збереження повної розфарбованої карти міток.
- **Часова складність**: `O(width · α(N))` амортизовано.
- **Просторова складність**: `O(1)` додаткової пам'яті за виклик (використовується фіксований буфер контексту).

## 6. Фіналізація та вилучення результатів

Після передачі всіх рядків ґратки викликається функція `hk_finalize`, яка переводить контекст у стан `FINALIZED`, розв'язує тороїдальні зв'язки та будує масив канонічної ренумерації.

:::tabs
```c
/* Завершення першого проходу та формування канонічних кластерів */
hk_error_t hk_finalize(hk_context_t* ctx);

/* Отримання зведеної статистики перколації */
hk_error_t hk_get_stats(const hk_context_t* ctx, hk_stats_t* stats_out);

/* Отримання масиву розмірів кластерів за канонічними індексами 1..total_clusters */
hk_error_t hk_get_cluster_sizes(
    const hk_context_t* ctx,
    int* sizes_out,
    int max_count,
    int* actual_count_out
);

/* Заміна тимчасових міток на канонічні номери 1..K у вихідному масиві */
hk_error_t hk_relabel_grid(
    const hk_context_t* ctx,
    int* grid_inout,
    size_t total_elements
);
```
```cpp
// Завершення обробки та методи доступу у C++
void finalize();

[[nodiscard]] PercolationStats get_stats() const;
[[nodiscard]] std::vector<int> get_cluster_sizes() const;

void relabel_grid(std::span<int> grid_inout) const;
```
:::

#### Послідовність станів автомата контексту (State Machine Invariant):
1. `CREATED` → стан після створення контексту функцією `hk_context_create_2d`.
2. `PROCESSING` → стан після першого виклику `hk_process_row`. Дозволено повторні виклики `hk_process_row` до досягнення ліміту `height`.
3. `FINALIZED` → стан після виклику `hk_finalize`. У цьому стані дозволено лише функції зчитування статистики (`hk_get_stats`, `hk_get_cluster_sizes`, `hk_relabel_grid`). Спроба викликати `hk_process_row` у стані `FINALIZED` повертає помилку `HK_ERROR_INVALID_STATE`.
4. `RESET` → після виклику `hk_context_reset`. Контекст повертається у стан `CREATED` без перевиділення пам'яті.

## 7. Модуль паралельної декомпозиції доменів (Domain Decomposition API)

Для організації паралельних обчислень на комп'ютерних кластерах та багатоядерних процесорах бібліотека надає інтерфейс зшивання піддоменів.

:::tabs
```c
/* Злиття незалежно оброблених горизонтальних смуг ґратки */
hk_error_t hk_merge_subdomains_2d(
    hk_context_t* master_ctx,
    hk_context_t** stripe_contexts,
    int num_stripes,
    const int** border_bottom_rows,
    const int** border_top_rows
);
```
```cpp
// Паралельне злиття піддоменів у C++
void merge_subdomains_2d(
    GridLabeler2D& master_labeler,
    std::span<GridLabeler2D*> stripe_labelers,
    std::span<const int*> border_bottom_rows,
    std::span<const int*> border_top_rows
);
```
:::

#### Контракт багатопотоковості:
- **Thread Safety**: Окремі дескриптори `hk_context_t` не мають спільного змінюваного стану (No Shared Mutable State) і можуть паралельно виконуватися в окремих потоках ОС без використання м'ютексів чи атомарних операцій.
- **Синхронізація**: Функція `hk_merge_subdomains_2d` викликається в головному потоці після завершення паралельного сканування всіма потоками-виконавцями.

## 8. Повний приклад інтеграції та використання

Нижче наведено робочий приклад обробки бінарного масиву з виведенням статистики та перевіркою протікання.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

/* Демонстраційний приклад використання C API */
int run_c_api_demo(void) {
    const int W = 6, H = 6;
    const uint8_t lattice[36] = {
        1, 1, 0, 1, 1, 0,
        1, 0, 0, 0, 1, 0,
        1, 1, 1, 1, 1, 0,
        0, 0, 0, 0, 0, 1,
        0, 1, 1, 0, 0, 1,
        0, 1, 1, 0, 0, 0
    };

    hk_context_t* ctx = NULL;
    hk_error_t err = hk_context_create_2d(&ctx, W, H, HK_CONNECTIVITY_4, HK_BOUNDARY_OPEN);
    if (err != HK_SUCCESS) {
        fprintf(stderr, "Помилка створення контексту: %d\n", err);
        return 1;
    }

    int* labeled_matrix = (int*)malloc((size_t)(W * H) * sizeof(int));
    if (!labeled_matrix) {
        hk_context_destroy(ctx);
        return 1;
    }

    /* Потокове сканування по рядках */
    for (int r = 0; r < H; ++r) {
        hk_process_row(ctx, &lattice[r * W], &labeled_matrix[r * W]);
    }

    /* Фіналізація та ренумерація */
    hk_finalize(ctx);
    hk_relabel_grid(ctx, labeled_matrix, (size_t)(W * H));

    hk_stats_t stats;
    hk_get_stats(ctx, &stats);

    printf("=== Результати аналізу перколації ===\n");
    printf("Кількість кластерів: %d\n", stats.total_clusters);
    printf("Найбільший кластер:   %d вузлів\n", stats.max_cluster_size);
    printf("Середній розмір S(p): %.3f\n", stats.mean_cluster_size);
    printf("Протікання (Y):       %s\n", stats.has_spanning_cluster_y ? "ТАК" : "НІ");

    free(labeled_matrix);
    hk_context_destroy(ctx);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>

/* Демонстраційний приклад використання C++20 API */
int run_cpp_api_demo() {
    constexpr int W = 6, H = 6;
    const std::vector<uint8_t> lattice = {
        1, 1, 0, 1, 1, 0,
        1, 0, 0, 0, 1, 0,
        1, 1, 1, 1, 1, 0,
        0, 0, 0, 0, 0, 1,
        0, 1, 1, 0, 0, 1,
        0, 1, 1, 0, 0, 0
    };

    try {
        hoshen_kopelman::GridLabeler2D labeler(W, H,
            hoshen_kopelman::Connectivity::Four,
            hoshen_kopelman::BoundaryCondition::Open);

        std::vector<int> labeled_grid(W * H, 0);

        for (int r = 0; r < H; ++r) {
            std::span<const uint8_t> row_in(&lattice[r * W], W);
            std::span<int> row_out(&labeled_grid[r * W], W);
            labeler.process_row(row_in, row_out);
        }

        labeler.finalize();
        labeler.relabel_grid(labeled_grid);

        auto stats = labeler.get_stats();
        auto sizes = labeler.get_cluster_sizes();

        std::cout << "=== Результати аналізу перколації (C++20) ===\n";
        std::cout << "Кількість кластерів: " << stats.total_clusters << "\n";
        std::cout << "Найбільший кластер:   " << stats.max_cluster_size << "\n";
        std::cout << "Середній розмір S(p): " << stats.mean_cluster_size << "\n";
        std::cout << "Протікання по Y:      " << (stats.has_spanning_cluster_y ? "ТАК" : "НІ") << "\n";

        for (size_t i = 1; i < sizes.size(); ++i) {
            std::cout << "  Кластер #" << i << ": розмір = " << sizes[i] << "\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "Виник виняток: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
```
:::

## 9. Гарантії бінарної сумісності та FFI-інтеграція (ABI Stability)

Для забезпечення безшовної інтеграції з високорівневими мовами наукових обчислень (Python, Julia, Rust, MATLAB) бібліотека гарантує стабільний бінарний інтерфейс (ABI, Application Binary Interface):

1. **Узгодження викликів (Calling Convention)**:
   Усі відкриті C-функції експортуються зі стандартною угодою викликів `cdecl` (для x86/x86-64) та стандартним вирівнюванням стек-фрейму. Усі заголовкові файли загорнуті в блок `extern "C"`, що запобігає манглінгу імен компілятором C++.
2. **Вирівнювання та пакування структур (Struct Layout & Alignment)**:
   Усі експортовані структури (`hk_stats_t`, `hk_cluster_info_t`) мають природне 64-бітне вирівнювання полів без неявного падінгу (`padding bytes`), що забезпечує пряме зіставлення з `ctypes.Structure` у Python та `#[repr(C)]` у Rust.
3. **Семантика покажчиків і нульове копіювання**:
   Вхідний бінарний масив інтерпретується як послідовний одновимірний буфер у форматі row-major (`C-contiguous`). Це дозволяє передавати дані безпосередньо з `numpy.ndarray.ctypes.data` без створення проміжних копій у пам'яті.

:::tabs
```c
/* Експортний C-заголовок для FFI прив'язок */
#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int32_t total_clusters;
    int32_t total_occupied_sites;
    int32_t max_cluster_size;
    double  mean_cluster_size;
    double  cluster_density;
    bool    has_spanning_cluster_x;
    bool    has_spanning_cluster_y;
    bool    has_spanning_cluster_z;
} hk_stats_ffi_t;

#ifdef __cplusplus
}
#endif
```
```cpp
// Приклад інтеграції через C++ FFI заголовок
extern "C" {
    struct HKStatsFFI {
        int32_t total_clusters;
        int32_t total_occupied_sites;
        int32_t max_cluster_size;
        double mean_cluster_size;
        double cluster_density;
        bool has_spanning_cluster_x;
        bool has_spanning_cluster_y;
        bool has_spanning_cluster_z;
    };
}
```
:::

## 10. Протокол обробки виняткових ситуацій та відновлення після помилок

У критичних виробничих системах та тривалих симуляціях Монте-Карло критично важливо гарантувати, що збій на одному кроці не призведе до витоку пам'яті чи зависання процесу.

### Стратегія обробки помилок пам'яті:
1. **Збереження цілісності при дефіциті RAM (`HK_ERROR_OUT_OF_MEMORY`)**:
   Якщо під час виклику `hk_process_row` системний виклик `realloc` повертає `NULL` через нестачу фізичної пам'яті для масиву міток `labels[]`, бібліотека не змінює внутрішній стан контексту (Strong Exception Safety). Попередній масив залишається валідним, а функція негайно повертає код помилки `HK_ERROR_OUT_OF_MEMORY`. Користувач може або звільнити пам'ять і повторити спробу, або коректно завершити процес через `hk_context_destroy`.
2. **Валідація розмірностей та покажчиків**:
   Усі функції виконують перевірку вхідних аргументів на початку виклику (Sanity Check) за `O(1)` часу. Передача нульового покажчика або від'ємного розміру не призводить до сегментації пам'яті (`Segmentation Fault`), а повертає відповідний детермінований код помилки.
3. **Гарантія безпечного скидання стану (`hk_context_reset`)**:
   Функція `hk_context_reset` очищає лічильник міток `max_label = 0` та обнуляє буфер попереднього рядка `prev_row`, зберігаючи вже виділену місткість масиву DSU. Це дозволяє багаторазово використовувати один контекст для мільйонів послідовних ітерацій Монте-Карло без накладних витрат на звернення до системного алокатора `malloc/free`.

## 11. Асимптотичні гарантії продуктивності та профілі споживання ресурсів

| Сценарій застосування | Часова складність на вузол | Споживання пам'яті для 2D `L × L` | Споживання пам'яті для 3D `L × L × L` |
|---|---|---|---|
| **Потоковий аналіз перколації (Streaming Stats)** | `O(α(K)) ≈ O(1)` | `2 · L · 4 Б + K_max · 4 Б` | `L² · 4 Б + K_max · 4 Б` |
| **Повне двопрохідне маркування матриці (Full CCL)** | `O(α(K)) ≈ O(1)` | `L² · 4 Б + K_max · 4 Б` | `L³ · 4 Б + K_max · 4 Б` |
| **Паралельна декомпозиція на P потоків** | `O(N / P · α(K))` | `P · (2 · L · 4 Б + K_local · 4 Б)` | `P · (L² · 4 Б + K_local · 4 Б)` |

де `α` — обернена функція Аккермана (`α(N) < 5`), а `K_max` — максимальна кількість одночасно народжених тимчасових міток під час сканування (у середньому `K_max ≈ 0.1 · N` для критичної концентрації `p ≈ p_c`).

## 12. Розширена конфігурація та параметри оптимізації (`hk_config_t`)

Для тонкого налаштування продуктивності в різних сценаріях застосування бібліотека надає структуру конфігурації `hk_config_t`:

:::tabs
```c
typedef struct {
    size_t initial_label_capacity; /* Початкова місткість масиву міток DSU (за замовчуванням 2048) */
    double growth_factor;          /* Коефіцієнт геометричного розширення місткості (1.5 - 2.0) */
    bool enable_simd;              /* Дозвіл використання векторних інструкцій AVX2 / NEON */
    bool compute_moments_on_fly;   /* Обчислення моментів другого порядку M_2 безпосередньо у першому проході */
    bool track_bounding_boxes;     /* Відстеження прямокутників обмеження (Bounding Box) для кожного кластера */
} hk_config_t;

/* Отримання конфігурації за замовчуванням */
void hk_config_init_default(hk_config_t* config);
```
```cpp
struct LabelerConfig {
    size_t initial_label_capacity{2048};
    double growth_factor{2.0};
    bool enable_simd{true};
    bool compute_moments_on_fly{true};
    bool track_bounding_boxes{false};
};
```
:::

#### Призначення параметрів конфігурації:
- `initial_label_capacity`: Якщо очікується висока фрагментація ґратки (поблизу порогу перколації `p ≈ 0.59`), встановлення початкової місткості на рівні `(width · height) / 8` повністю усуває затримки на системні виклики `realloc` під час сканування.
- `enable_simd`: Вмикає апаратні інструкції перевірки нульових блоків (AVX2 `_mm256_testz_si256` на x86-64 або ARM Neon `vmaxvq_u8`), що прискорює обробку порожніх ділянок ґратки у 4–8 разів.
- `compute_moments_on_fly`: Дозволяє під час операцій `union_labels` та `add_site` безпосередньо оновлювати накопичувальні суми `M_1 = ∑ s` та `M_2 = ∑ s²`, що робить отримання `mean_cluster_size` миттєвою операцією з часовою складністю `O(1)` одразу після завершення першого проходу.

## 13. Подійно-орієнтований інтерфейс зворотного виклику (Callback Streaming API)

Для інтеграції в асинхронні мережеві пайплайни або обробку відеопотоків із камер промислового зору бібліотека підтримує механізм callback-функцій:

:::tabs
```c
/* Тип функції зворотного виклику при виявленні злиття кластерів */
typedef void (*hk_cluster_event_cb)(
    int event_type,        /* 1 - створення нового кластера, 2 - злиття кластерів */
    int primary_root,
    int merged_root,
    int new_total_size,
    void* user_data
);

/* Реєстрація функції зворотного виклику в контексті */
hk_error_t hk_set_cluster_event_callback(
    hk_context_t* ctx,
    hk_cluster_event_cb callback,
    void* user_data
);
```
```cpp
using ClusterEventCallback = std::function<void(
    int event_type,
    int primary_root,
    int merged_root,
    int new_total_size
)>;

void set_cluster_event_callback(ClusterEventCallback callback);
```
:::

Цей механізм дозволяє підписникам у реальному часі реагувати на замикання контурів (наприклад, у моніторингу виникнення критичних провідних містків у напівпровідникових діелектриках під час тестування TDDB).

## 14. Розподілена декомпозиція для кластерів MPI (`hk_mpi_exchange`)

Для моделювання перколації на суперкомп'ютерних кластерах із терабайтними об'ємами ґраток бібліотека надає протокол узгодження граничних міток між окремими обчислювальними вузлами через стандартний інтерфейс передачі повідомлень (MPI):

:::tabs
```c
/* Протокол обміну граничними мітками між сусідніми процесами MPI */
hk_error_t hk_mpi_resolve_borders_2d(
    hk_context_t* ctx,
    int rank,
    int num_ranks,
    int* local_top_border,
    int* local_bottom_border
);
```
```cpp
void mpi_resolve_borders_2d(
    GridLabeler2D& local_labeler,
    int rank,
    int num_ranks,
    std::span<int> local_top_border,
    std::span<int> local_bottom_border
);
```
:::

## 15. Вирівнювання пам'яті та оптимізація кеш-ліній (Cache Line Alignment)

Для досягнення максимальної пропускної здатності на сучасних процесорних архітектурах із багаторівневою ієрархією кеш-пам'яті внутрішні буфери бібліотеки оптимізовані під розмір стандартної кеш-лінії процесора (64 байти):

1. **Вирівнювання буферів рядків (`posix_memalign` / `_aligned_malloc`)**:
   Усі одновимірні масиви рядків `prev_row` та `curr_row` вирівнюються за адресами, кратними 64 байтам. Це усуває розщеплення звернень до пам'яті (Unaligned Split Loads) та гарантує, що векторні інструкції AVX-512 та AVX2 завантажують дані за один такт шини L1D без штрафів латентності.
2. **Організація бітового кодування у масиві `labels[]`**:
   Знаковий біт (MSB, Bit 31) 32-бітного цілого числа використовується як розпізнавач типу вершини:
   - Якщо `Bit 31 == 1` (значення від'ємне в доповняльному коді): біти `0..30` кодують абсолютну величину маси кластера `size ∈ [1, 2³¹ - 1]`.
   - Якщо `Bit 31 == 0` (значення додатне): біти `0..30` вказують на прямий індекс батьківського вузла `parent ∈ [1, 2³¹ - 1]`.
   Таке бітове представлення дозволяє перевіряти статус вершини (`is_root`) за одну інструкцію процесора без додаткових логічних прапорців або структурних накладних витрат.

:::tabs
```c
/* Допоміжний макрос перевірки статусу кореня через бітові операції */
#define HK_IS_ROOT_LABEL(val) ((val) < 0)
#define HK_GET_CLUSTER_SIZE(val) (-(val))
#define HK_GET_PARENT_LABEL(val) (val)
```
```cpp
// Константні constexpr-утиліти для бітового кодування
constexpr bool is_root_label(int val) noexcept { return val < 0; }
constexpr int get_cluster_size(int val) noexcept { return -val; }
constexpr int get_parent_label(int val) noexcept { return val; }
```
:::

## 16. Контракт верифікації та тестові вектори валідації (`hk_validate`)

Бібліотека включає вбудований модуль самодіагностики та перевірки цілісності (Self-Test Suite), який дозволяє верифікувати коректність функціонування DSU та растрового сканера на цільовій апаратній платформі:

:::tabs
```c
/* Запуск вбудованого набору валідаційних тестів */
hk_error_t hk_run_self_test(void);
```
```cpp
bool run_self_test() noexcept;
```
:::

Модуль автоматично виконує перевірку на чотирьох еталонних конфігураціях:
1. **Тестовий вектор «Шахова дошка 8 × 8»**: перевіряє генерацію рівно 32 ізольованих кластерів розміру 1 та коректність динамічного розширення місткості DSU.
2. **Тестовий вектор «Спіраль Архімеда 16 × 16»**: перевіряє глибину стиснення шляхів при обході довгого безперервного лабіринту з одним коренем.
3. **Тестовий вектор «U-подібний міст 32 × 32»**: перевіряє відсутність колізійних артефактів та точність підсумовування маси при об'єднанні двох великих кластерів.
4. **Тестовий вектор «Тороїдальний бублик 64 × 64»**: перевіряє коректність виявлення макроскопічного протікання за періодичних тороїдальних граничних умов.

## 17. Політика версіонування та зворотної сумісності (Semantic Versioning)

Бібліотека суворо дотримується стандартів семантичного версіонування (SemVer 2.0.0):

:::tabs
```c
/* Макроси версії бібліотеки */
#define HK_VERSION_MAJOR 2
#define HK_VERSION_MINOR 1
#define HK_VERSION_PATCH 0
#define HK_VERSION_STRING "2.1.0"

/* Отримання поточної версії під час виконання */
const char* hk_get_version_string(void);
```
```cpp
// Константна інформація про версію C++
inline constexpr int VersionMajor = 2;
inline constexpr int VersionMinor = 1;
inline constexpr int VersionPatch = 0;
inline constexpr std::string_view VersionString = "2.1.0";

[[nodiscard]] inline std::string_view get_version_string() noexcept {
    return VersionString;
}
```
:::

- **Мажорні зміни (Major version bump)**: зміна розміру або порядку полів у структурах `hk_stats_t` та `hk_cluster_info_t`, зміна сигнатур відкритих функцій.
- **Мінорні зміни (Minor version bump)**: додавання нових аналітичних функцій (наприклад, обчислення додаткових моментів `M_3` або нових типів зв'язності для трикутних ґраток), збереження повної зворотної сумісності заголовочних файлів та бінарного ABI.
- **Патчі (Patch bump)**: виправлення внутрішніх крайових випадків у DSU без змін API.



