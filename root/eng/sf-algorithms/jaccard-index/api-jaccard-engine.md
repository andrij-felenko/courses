# 📋 Довідник інтерфейсу та структур даних Jaccard Engine

Цей довідник містить повну технічну специфікацію системного ABI-інтерфейсу, структур даних, кодів помилок, інваріантів та сигнатур функцій системної бібліотеки **Jaccard Engine**, призначеної для високопродуктивного точного та імовірнісного пошуку за схожістю у великих масивах даних.

Бібліотеку спроєктовано з урахуванням суворих вимог до системного програмування: забезпечення строгої зворотної сумісності C ABI, відсутність глобального прихованого стану, повна потокобезпечність читання та мінімізація накладних витрат на виділення динамічної пам'яті. Вона надає як нізькорівневий С99 інтерфейс для інтеграції у C-проєкти та зв'язки з іншими мовами (FFI), так і високорівневу C++20 обгортку на основі семантики переміщення та RAII.

## 1. Архітектурні принципи та коди помилок

Усі функції C API бібліотеки повертають цілочисельний статус виконання типу `jaccard_status_t`. Значення `0` позначає успішне завершення операції, тоді як від'ємні значення вказують на конкретні категорії виняткових ситуацій. Такий підхід гарантує передбачувану обробку помилок у системному коді без використання небезпечних побічних ефектів чи механізмів винятків на рівні C ABI.

При розробці систем високого навантаження обробка кодів помилок є обов'язковою на кожному кроці виклику API. Якщо функція повертає від'ємний статус, усі вихідні буфери та вказівники вважаються невалидними і не повинні використовуватися для подальших обчислень.

Нижче наведено повний перелік кодів помилок, які може генерувати бібліотека Jaccard Engine:

- `JACCARD_OK` (код `0`): Операцію виконано успішно без жодних зауважень чи збоїв.
- `JACCARD_ERR_NULL_POINTER` (код `-1`): Передано некоректний вказівник `NULL` як один із обов'язкових аргументів функції.
- `JACCARD_ERR_INVALID_PARAM` (код `-2`): Надано недопустиме значення конфігураційних чи обчислювальних параметрів (наприклад, порогова схожість `threshold <= 0` або кількість хеш-функцій `minhash_k == 0`).
- `JACCARD_ERR_NO_MEMORY` (код `-3`): Спроба виділення динамічної пам'яті у системній купі за допомогою `malloc` або `posix_memalign` повернула `NULL` через вичерпання ресурсів системи.
- `JACCARD_ERR_CAPACITY_EXCEEDED` (код `-4`): Перевищено максимальну дозволену місткість індексу або дозволений розмір сигнатури.
- `JACCARD_ERR_BUFFER_TOO_SMALL` (код `-5`): Наданий викликачем вихідний буфер має недостатній розмір для збереження обчислених результатів.

Для отримання людиночитаного текстового опису помилки використовують функцію `jaccard_status_to_str(jaccard_status_t status)`, яка повертає константний рядок із поясненням причини збою для логування та діагностики.

## 2. Структури даних C ABI та розміщення в пам'яті

Системний інтерфейс C ABI розроблено з дотриманням вимог сумісності з POSIX та стандартом C99. Усі структури мають явне вирівнювання полів для уникнення неочікуваних байтових зазорів та забезпечення сумісності між різними компіляторами та архітектурами процесорів.

### Режими розрахунку та структура конфігурації `jaccard_config_t`

Перелічувальний тип `jaccard_calc_mode_t` позначає алгоритмічну стратегію, яку застосовуватиме двигун під час обчислень:
- `JACCARD_MODE_EXACT_SORTED`: використовує точний порівняльний аналіз двох попередньо відсортованих масивів 64-бітних хешів за допомогою двопокажчикового проходу за `O(|A| + |B|)`.
- `JACCARD_MODE_EXACT_HASH`: застосовує точне порівняння через побудову внутрішньої хеш-таблиці для нерозпорядкованих дискретних елементів.
- `JACCARD_MODE_MINHASH`: вмикає імовірнісну оцінку коефіцієнта Жаккара на основі генерації та порівняння компактних сигнатур MinHash фіксованого розміру `K`.

:::tabs
```c
typedef enum {
    JACCARD_MODE_EXACT_SORTED = 0,
    JACCARD_MODE_EXACT_HASH   = 1,
    JACCARD_MODE_MINHASH      = 2
} jaccard_calc_mode_t;

typedef struct {
    jaccard_calc_mode_t mode; // Режим розрахунку схожості
    size_t shingle_size;      // Довжина k-грами у символах (за замовчуванням: 4)
    size_t minhash_k;         // Кількість хеш-функцій MinHash (за замовчуванням: 128)
    double sim_threshold;     // Порогове значення схожості τ ∈ (0, 1]
    uint64_t random_seed;     // Початкове зерно генератора випадкових чисел
} jaccard_config_t;
```
```cpp
enum class Mode : uint32_t {
    ExactSorted = 0,
    ExactHash   = 1,
    MinHash     = 2
};

struct Config {
    Mode mode = Mode::ExactSorted;
    size_t shingle_size = 4;
    size_t minhash_k = 128;
    double sim_threshold = 0.5;
    uint64_t random_seed = 42;
};
```
:::

Параметр `shingle_size` контролює довжину ковзного вікна при розбитті тексту на підрядки `k`-грам. Параметр `minhash_k` задає кількість універсальних хеш-функцій для формування сигнатур MinHash. Вищий поріг `sim_threshold` відсіює більше кандидатів на етапі розмірного та префіксного фільтрів. Початкове зерно `random_seed` забезпечує детерміновану відтворюваність перестановок MinHash між повторними запусками програми.

### Структури зберігання множин та сигнатур

Для зберігання дискретних даних та компактних профілів застосовують такі структури:

:::tabs
```c
typedef struct {
    uint32_t id;         // Унікальний ідентифікатор об'єкта/документа
    size_t count;        // Кількість унікальних елементів у множині
    uint64_t *elements;  // Відсортований масив 64-бітних хешів елементів
} jaccard_set_t;

typedef struct {
    uint32_t id;         // Ідентифікатор об'єкта
    size_t k_len;        // Кількість хеш-значень (розмір масиву sig)
    uint64_t *sig;       // Динамічний масив мінімальних хешів (розміру k_len)
} jaccard_signature_t;

typedef struct {
    uint32_t id_a;       // Ідентифікатор першого об'єкта
    uint32_t id_b;       // Ідентифікатор другого об'єкта
    double similarity;   // Обчислений коефіцієнт схожості Жаккара J ∈ [0, 1]
} jaccard_match_t;
```
```cpp
struct Set {
    uint32_t id = 0;
    std::vector<uint64_t> elements;
};

struct Signature {
    uint32_t id = 0;
    std::vector<uint64_t> sig;
};

struct Match {
    uint32_t id_a = 0;
    uint32_t id_b = 0;
    double similarity = 0.0;
};
```
:::

Масив `elements` у структурі `jaccard_set_t` повинен бути суворо відсортованим за зростанням і не містити дублікатів. Власником пам'яті під масиви `elements` та `sig` є викликач, якщо функція явно не документує передачу володіння.

## 3. Специфікація функцій C API та правила їхнього виклику

Функції бібліотеки поділено на три фундаментальні групи: управління конфігурацією, точний розрахунок та імовірнісний аналіз сигнатур.

### Управління конфігурацією та ініціалізація

Перед використанням конфігураційної структури її необхідно ініціалізувати значеннями за замовчуванням:

:::tabs
```c
jaccard_status_t jaccard_config_init_default(jaccard_config_t *cfg);
jaccard_status_t jaccard_config_validate(const jaccard_config_t *cfg);
```
```cpp
Config make_default_config();
bool is_valid_config(const Config& cfg) noexcept;
```
:::

Функція `jaccard_config_init_default` встановлює значення `mode = JACCARD_MODE_EXACT_SORTED`, `shingle_size = 4`, `minhash_k = 128` та `sim_threshold = 0.5`. Функція `jaccard_config_validate` здійснює сувору перевірку коректності всіх полів: вона переконується, що `sim_threshold` лежить у межах `(0, 1]`, а `minhash_k > 0`. Якщо виявлено помилку, повертається `JACCARD_ERR_INVALID_PARAM`.

### Точні операції обчислення схожості

Для прямого порівняння двох підготовлених множин використовують точний модуль обчислення:

:::tabs
```c
jaccard_status_t jaccard_compute_exact_sorted(
    const jaccard_set_t *set_a,
    const jaccard_set_t *set_b,
    double *out_similarity
);

bool jaccard_pass_size_filter(
    size_t len_a,
    size_t len_b,
    double threshold
);
```
```cpp
double compute_exact_sorted(
    std::span<const uint64_t> set_a,
    std::span<const uint64_t> set_b
);

bool pass_size_filter(
    size_t len_a,
    size_t len_b,
    double threshold
) noexcept;
```
:::

Функція `jaccard_compute_exact_sorted` виконує порівняння двох відсортованих масивів елементів за `O(|A| + |B|)` операцій. Вона записує обчислений коефіцієнт схожості у змінну за вказівником `out_similarity`. Якщо обидві множини порожні, повертається значення `1.0`. 

Функція `jaccard_pass_size_filter` здійснює швидку перевірку нерівності `threshold * len_a <= len_b && len_b <= len_a / threshold` за `O(1)` операцій. Вона повертає `true`, якщо розміри множин допускають існування схожості не нижчої за `threshold`, і `false` у протилежному випадку.

### Модуль MinHash та імовірнісного пошуку

Для імовірнісного стиснення та порівняння великих масивів документів призначено модуль MinHash Engine:

:::tabs
```c
typedef struct jaccard_minhash_engine jaccard_minhash_engine_t;

jaccard_status_t jaccard_minhash_engine_create(
    const jaccard_config_t *cfg,
    jaccard_minhash_engine_t **out_engine
);

jaccard_status_t jaccard_minhash_compute_sig(
    const jaccard_minhash_engine_t *engine,
    const jaccard_set_t *set_in,
    jaccard_signature_t *out_sig
);

jaccard_status_t jaccard_minhash_compare_sigs(
    const jaccard_signature_t *sig_a,
    const jaccard_signature_t *sig_b,
    double *out_similarity
);

void jaccard_minhash_engine_destroy(jaccard_minhash_engine_t *engine);
```
```cpp
class MinHashEngine {
public:
    explicit MinHashEngine(const Config& cfg);
    ~MinHashEngine();

    [[nodiscard]] std::vector<uint64_t> compute_sig(std::span<const uint64_t> set_in) const;
    [[nodiscard]] static double compare_sigs(std::span<const uint64_t> sig_a, std::span<const uint64_t> sig_b);
};
```
:::

Об'єкт `jaccard_minhash_engine_t` є непрозорим вказівником (*Opaque Pointer*), що приховує внутрішню структуру коефіцієнтів хеш-функцій. Він є повністю потокобезпечним (англ. *Thread-Safe*): після створення декілька паралельних робочих потоків можуть одночасно викликати `jaccard_minhash_compute_sig` без використання синхронізуючих м'ютексів. Після завершення роботи екземпляр двигуна необхідно знищити за допомогою `jaccard_minhash_engine_destroy`.

## 4. Специфікація обгортки C++ RAII

Для використання бібліотеки в сучасних C++20 проєктах надається клас-обгортка `jaccard::JaccardEngine`, який реалізує концепцію RAII (Resource Acquisition Is Initialization) і повністю усуває загрозу витоків пам'яті.

```cpp
namespace jaccard {

class JaccardEngine {
public:
    explicit JaccardEngine(Config config);
    ~JaccardEngine();

    JaccardEngine(const JaccardEngine&) = delete;
    JaccardEngine& operator=(const JaccardEngine&) = delete;

    JaccardEngine(JaccardEngine&&) noexcept;
    JaccardEngine& operator=(JaccardEngine&&) noexcept;

    [[nodiscard]] static double compute_exact(
        std::span<const uint64_t> a,
        std::span<const uint64_t> b
    );

    [[nodiscard]] static bool check_size_filter(
        size_t len_a,
        size_t len_b,
        double threshold
    ) noexcept;

    [[nodiscard]] std::vector<uint64_t> compute_signature(
        std::span<const uint64_t> shingles
    ) const;

    [[nodiscard]] static double compare_signatures(
        std::span<const uint64_t> sig_a,
        std::span<const uint64_t> sig_b
    );

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace jaccard
```

Клас підтримує семантику переміщення (*Move Semantics*), забороняє потенційно небезпечне неявне копіювання важких внутрішніх ресурсів та використовує C++20 `std::span` для безаварійного доступу до неперервних масивів пам'яті без залучення сирих вказівників.

## 5. Вимоги до розміщення в пам'яті, вирівнювання та кеш-оптимізацій

Для досягнення максимальної обчислювальної продуктивності на процесорах архітектури x86_64 та ARM64 рекомендується дотримуватися таких системних інваріантів:

1. **Кеш-вирівнювання масивів (Cache Line Alignment):** Масиви `elements` у `jaccard_set_t` та `sig` у `jaccard_signature_t` повинні вирівнюватися за межею 64 байтів (`alignas(64)` або `posix_memalign`). Це відповідає стандартному розміру кеш-лінії більшості процесорів архітектури x86_64 та ARM64 і дозволяє застосовувати векторні інструкції AVX-512 та ARM Neon без штрафів за невирівняний доступ.
2. **Незмінність даних (Immutability):** Після генерації масиву сигнатур MinHash він розглядається як незмінний (`const`), що дозволяє безаварійний паралельний доступ з багатьох потоків без використання блокувань (*Lock-Free Read*).
3. **Конвертація кодів помилок у C++:** Усі від'ємні коди помилок C API у C++ обгортці трансуються у стандартні винятки `std::invalid_argument` або `std::bad_alloc`, що полегшує інтеграцію у сучасні корпоративні системи.
