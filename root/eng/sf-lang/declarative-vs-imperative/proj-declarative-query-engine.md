# ⚙️ Побудова рушія запитів: від імперативного циклу до декларативного конвеєра

У цій практичній роботі ми розберемо, як транслювати декларативний опис обробки даних у безкомпромісно швидкий машинний код без зайвих виділень динамічної пам'яті. Ми створимо конвеєр аналізу телеметричних даних сенсорів, порівняємо покроковий імперативний алгоритм із декларативною моделлю ітераторів та перевіримо асемблерний вивід компілятора на відповідність [принципу абстракцій без витрат](root:sf-lang/zero-cost-abstractions).

### Постановка задачі

Уявімо масив вимірювань із вбудованих датчиків. Кожен запис містить ідентифікатор пристрою, числовий показник, часову мітку та прапорець валідності:

```
struct SensorRecord {
    uint32_t sensor_id;
    double   value;
    uint64_t timestamp;
    bool     is_valid;
};
```

Перед нами стоїть аналітична задача, яку в бізнес-термінах можна сформулювати так:
1. **Фільтрація:** відібрати тільки валідні записи (`is_valid == true`) для датчика з `sensor_id == 42`, показник яких перевищує поріг `value >= 10.0`.
2. **Трансформація:** застосувати калібрувальний коефіцієнт: `calibrated = value * 1.08 + 0.5`.
3. **Обмеження:** взяти щонайбільше перші `LIMIT = 5` записів, що задовольнили критерій.
4. **Агрегація:** порахувати суму каліброваних значень.

Усі обчислення мають виконуватися в умовах жорстких обмежень на ресурси: жодних динамічних алокацій пам'яті в [купі](root:sf-lang/heap-dynamic-memory), жодних проміжних копій масивів та мінімальна кількість промахів кешу процесора.

---

### Підхід 1: Ручний імперативний цикл

У класичному імперативному підході розробник вручну організовує керування потоком виконання. Програма явно маніпулює змінними стану: заводить індекси для обходу масиву, мутує акумулятор суми, явно перевіряє ланцюг умов через `if`, інкрементує лічильник знайдених елементів та достроково перериває обхід за допомогою інструкції `break`.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t sensor_id;
    double   value;
    uint64_t timestamp;
    bool     is_valid;
} SensorRecord;

double process_imperative(const SensorRecord* records, size_t count, uint32_t target_sensor, double threshold, size_t limit) {
    double sum = 0.0;
    size_t matches = 0;

    for (size_t i = 0; i < count; ++i) {
        // Явна покрокова перевірка фільтрів
        if (!records[i].is_valid) {
            continue;
        }
        if (records[i].sensor_id != target_sensor) {
            continue;
        }
        if (records[i].value < threshold) {
            continue;
        }

        // Трансформація та мутація стану
        double calibrated = records[i].value * 1.08 + 0.5;
        sum += calibrated;
        matches++;

        // Дострокове завершення
        if (matches >= limit) {
            break;
        }
    }

    return sum;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>

struct SensorRecord {
    std::uint32_t sensor_id;
    double        value;
    std::uint64_t timestamp;
    bool          is_valid;
};

double process_imperative(std::span<const SensorRecord> records, std::uint32_t target_sensor, double threshold, std::size_t limit) {
    double sum = 0.0;
    std::size_t matches = 0;

    for (const auto& record : records) {
        if (!record.is_valid || record.sensor_id != target_sensor || record.value < threshold) {
            continue;
        }

        double calibrated = record.value * 1.08 + 0.5;
        sum += calibrated;
        ++matches;

        if (matches >= limit) {
            break;
        }
    }

    return sum;
}
```
:::

**Переваги та недоліки імперативного варіанта:**
- *Швидкодія на залізі:* Процесор виконує інструкції абсолютно лінійно, без викликів підпрограм, стек-фреймів чи проміжних об'єктів. Якщо вхідний масив відсортовано, передбачувач переходів (branch predictor) CPU працює зі стовідсотковою точністю.
- *Архітектурна монолітність:* Уся логіка (фільтрація, математична калібровка, лімітування вибірки та редукція суми) спресована в єдиний монолітний блок. Якщо завтра знадобиться замінити ліміт на обчислення медіани або використати ту саму калібровку для іншого потоку вимірювань, код доведеться або дублювати через копіювання, або розбивати на проміжні буфери пам'яті.

---

### Підхід 2: Декларативний конвеєр з лінивими ітераторами

Щоб зробити код модульним і придатним до композиції, ми розбиваємо задачу на незалежні трансформації: `data | filter | transform | take`.

Головна архітектурна небезпека наївного декларативного коду полягає в жадібному обчисленні (*eager evaluation*): якщо оператор `filter` створить новий проміжний масив у пам'яті, а `transform` — ще один, ми витратимо гігабайти пам'яті на великих датасетах.

Щоб цього уникнути, ми застосовуємо **модель витягування** (англ. *pull-based iterator model*, відому в теорії баз даних як модель ітераторів Volcano). У цій моделі кожен вузол конвеєра зберігає лише посилання на джерело даних і запитує черговий елемент викликом `next()` тільки тоді, коли кінцевий споживач готовий його прийняти.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t sensor_id;
    double   value;
    uint64_t timestamp;
    bool     is_valid;
} SensorRecord;

// 1. Ітератор джерела: обгортка над сирим масивом
typedef struct {
    const SensorRecord* data;
    size_t count;
    size_t index;
} SourceIterator;

static inline bool source_next(SourceIterator* it, SensorRecord* out) {
    if (it->index < it->count) {
        *out = it->data[it->index++];
        return true;
    }
    return false;
}

// 2. Ітератор фільтрації: пропускає елементи, що не відповідають предикату
typedef bool (*PredicateFn)(const SensorRecord*);

typedef struct {
    SourceIterator* src;
    PredicateFn predicate;
} FilterIterator;

static inline bool filter_next(FilterIterator* it, SensorRecord* out) {
    SensorRecord item;
    while (source_next(it->src, &item)) {
        if (it->predicate(&item)) {
            *out = item;
            return true;
        }
    }
    return false;
}

// 3. Ітератор обмеження (Take): зупиняє потік після N успішних записів
typedef struct {
    FilterIterator* src;
    size_t limit;
    size_t taken;
} TakeIterator;

static inline bool take_next(TakeIterator* it, SensorRecord* out) {
    if (it->taken >= it->limit) return false;
    if (filter_next(it->src, out)) {
        it->taken++;
        return true;
    }
    return false;
}

// Предикат та калібровка як чисті функції
static bool custom_sensor_filter(const SensorRecord* r) {
    return r->is_valid && r->sensor_id == 42 && r->value >= 10.0;
}

static inline double calibrate_transform(double raw_val) {
    return raw_val * 1.08 + 0.5;
}

// Декларативне складання конвеєра
double process_declarative_pipeline(const SensorRecord* records, size_t count, size_t limit) {
    SourceIterator src = { .data = records, .count = count, .index = 0 };
    FilterIterator flt = { .src = &src, .predicate = custom_sensor_filter };
    TakeIterator   tk  = { .src = &flt, .limit = limit, .taken = 0 };

    double sum = 0.0;
    SensorRecord record;
    while (take_next(&tk, &record)) {
        sum += calibrate_transform(record.value);
    }
    return sum;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <vector>
#include <ranges>
#include <numeric>
#include <iostream>

struct SensorRecord {
    std::uint32_t sensor_id;
    double        value;
    std::uint64_t timestamp;
    bool          is_valid;
};

// Декларативний конвеєр C++20 через std::views
double process_declarative_pipeline(std::span<const SensorRecord> records, std::uint32_t target_sensor, double threshold, std::size_t limit) {
    // 1. Опис предиката як чистої лямбди
    auto is_matching = [target_sensor, threshold](const SensorRecord& r) noexcept {
        return r.is_valid && r.sensor_id == target_sensor && r.value >= threshold;
    };

    // 2. Опис трансформації
    auto calibrate = [](const SensorRecord& r) noexcept {
        return r.value * 1.08 + 0.5;
    };

    // 3. Композиція конвеєра: декларативний ланцюг обчислення
    auto pipeline = records
        | std::views::filter(is_matching)
        | std::views::transform(calibrate)
        | std::views::take(limit);

    // 4. Агрегація (згортання результату)
    double sum = 0.0;
    for (double val : pipeline) {
        sum += val;
    }
    return sum;
}
```
:::

---

### Механіка компіляції та асемблерний аналіз

Щоб переконатися, що декларативний запис на C++20 не накладає штрафів на швидкодію, проаналізуємо роботу оптимізатора GCC/Clang під час компіляції з прапорцями `-O2` або `-O3`.

#### Трансформації компілятора над `std::views`:

1. **Повний інлайнінг (Full Inlining):**
   Шаблони адаптерів `std::views::filter`, `std::views::transform` та `std::views::take` не мають віртуальних таблиць. Їхні методи `begin()` та `operator++()` мають специфікатори `constexpr` та `inline`. Компілятор повністю розчиняє виклики методів і підставляє тіла лямбда-функцій безпосередньо у внутрішній цикл обходу пам'яті.

2. **Елімінація об'єктів (Scalar Replacement of Aggregates):**
   Жодних екземплярів ітераторів у пам'яті стека чи купи не виділяється. Оптимізатор розкладає структури на окремі скалярні змінні й розміщує вказівник на поточний елемент масиву в регістрі `%rdi`, кінцеву адресу — в `%rsi`, лічильник узятих записів — в `%rcx`, а акумулятор суми — у векторному регістрі `%xmm0`.

3. **Злиття конвеєра (Pipeline Fusion):**
   Компілятор об'єднує незалежні етапи фільтрації, множення та додавання в єдиний лінійний блок машинних інструкцій.

Погляньмо на згенерований асемблер x86-64 для внутрішнього тіла циклу:

```text
.L_loop:
    movzbl  24(%rdi), %eax          ; завантажити поле record.is_valid (зсув 24 байти)
    testb   %al, %al
    je      .L_skip                 ; якщо is_valid == false -> перехід до наступного
    cmpl    %edx, (%rdi)            ; перевірити sensor_id == target_sensor
    jne     .L_skip
    movsd   8(%rdi), %xmm1          ; завантажити record.value (зсув 8 байтів)
    ucomisd %xmm2, %xmm1            ; порівняти value >= threshold
    jb      .L_skip
    mulsd   .LC_FACTOR(%rip), %xmm1 ; помножити на 1.08
    addsd   .LC_BIAS(%rip), %xmm1   ; додати 0.5
    addsd   %xmm1, %xmm0            ; додати результат до загальної суми
    incq    %rcx                    ; matches++
    cmpq    %r8, %rcx               ; перевірити досягнення limit
    jge     .L_done                 ; достроковий вихід
.L_skip:
    addq    $32, %rdi               ; пересунути вказівник на наступний SensorRecord (+32 байти)
    cmpq    %rsi, %rdi
    jne     .L_loop
.L_done:
```

Цей асемблерний лістинг **повністю ідентичний** машинному коду, породженому з ручного імперативного циклу. Це і є практичний доказ принципу нульових витрат: декларативний опис не коштує жодного зайвого такту процесора.

---

### Крайові випадки та архітектурні пастки

Під час практичного проєктування декларативних конвеєрів інженер мусить враховувати такі крайові стани:

1. **Порожній вхідний діапазон (`count == 0`):**
   Ітератор джерела `source_next` негайно повертає `false`. Цикл агрегації виконує рівно нуль ітерацій і повертає початкове значення `0.0` без спроб невалідного розіменування нульових покажчиків.
2. **Ліміт перевищує кількість знайдених записів (`limit > matches`):**
   Конвеєр безпечно вичерпує вхідний масив до кінця, не зависаючи і не виходячи за межі виділеної пам'яті.
3. **Побічні ефекти всередині декларативних адаптерів:**
   Якщо всередині лямбди `filter` або `transform` розробник почне модифікувати зовнішній стан (наприклад, вести глобальний лог або змінювати глобальну змінну), гарантії компілятора щодо перевпорядкування операцій та векторизації руйнуються. Декларативні адаптери зобов'язані бути чистими функціями.

### Висновок

Декларативний підхід у сучасних мовах системного програмування переносить тягар побудови покрокового алгоритму з людини на компілятор. Інженер описує бізнес-правила у вигляді чистої композиції функцій, а оптимізуючий транслятор транслює їх у такий самий швидкий машинний код, як і написаний вручну низькорівневий цикл C.
