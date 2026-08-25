# 📋 Інтерфейс логарифмічного трансд'юсера та контракт зведення за логарифмічною пам'яттю

Цей довідник визначає формальний контракт абстрактного автомата (логарифмічного трансд'юсера), правила зведення задач за логарифмічною пам'яттю (`≤_L`), специфікацію віртуального протоколу композиції функцій без буферизації (Lazy Bit Query Protocol), а також системний POSIX-інтерфейс моніторингу просторових ресурсів у реальному виконанні.

Оскільки логарифмічна пам'ять не дозволяє зберігати навіть проміжні результати обчислень у пам'яті (довжина яких може сягати поліноміальних розмірів `O(n^k)`), взаємодія між модулями та складностійними трансд'юсерами вимагає строго визначеного автоматного та системного контракту.

---

## 1. Автоматний контракт тристрічкової машини Тюринга

Логарифмічний трансд'юсер є формальним детермінованим автоматом, який обчислює функцію `f: Σ* → Σ*` з використанням робочої пам'яті `O(\log n)`. Для забезпечення підрахунку ресурсів використовується тристрічкова модель, у якій функціональні обов'язки кожного елемента носія пам'яті чітко розграничені.

### Формальна п'ятірка стрічкової конфігурації
Трансд'юсер визначається кортежем:
```
M = (Q, Σ, Γ, δ, q₀, q_accept, q_reject)
```

Де елементи малювання обчислення мають такі значення:
- **`Q`** — скінченна множина внутрішніх станів контролера, яка визначає поточну фазу виконання алгоритму.
- **`Σ`** — вхідний та вихідний алфавіт (включаючи спеціальні символи початку `├` та кінця стрічки `┤`).
- **`Γ`** — алфавіт робочої стрічки, причому `Σ ⊂ Γ` та `⊔ ∈ Γ` (символ пробілу).
- **`q₀ ∈ Q`** — початковий стан, у якому автомат починає обчислення при отриманні вхідного слова `x`.
- **`q_accept, q_reject ∈ Q`** — термінальні стани прийняття та відхилення вхідного слова.

### Контракт тристрічкової перехідної функції δ
Функція переходу описує атомний крок обчислення автомата і має таку сигнатуру:
```
δ: Q × Σ × Γ  ──>  Q × Γ × {L, R, S} × (Σ ∪ {ε}) × {R, S}
```

Де аргументи та значення означають:
1. **`Q` (Поточний стан):** внутрішній стан контролера в даний момент часу.
2. **`Σ` (Вхідний символ):** символ під головкою вхідної стрічки у поточному положенні вказівника.
3. **`Γ` (Робочий символ):** символ під головкою робочої стрічки.
4. **`Q` (Новий стан):** наступний внутрішній стан контролера.
5. **`Γ` (Запис робочого символу):** символ, який записується на робочу стрічку у поточну комірку.
6. **`{L, R, S}` (Рух вхідної головки):** `L` (вліво), `R` (вправо), `S` (залишитися на місці).
7. **`(Σ ∪ {ε})` (Символ виходу):** один символ, який виводиться на вихідну стрічку, або порожній символ `ε` (нічого не виводиться).
8. **`{R, S}` (Рух вихідної головки):** `R` (зсув вправо після запису символу) або `S` (залишитися на місці при `ε`).

### Інваріанти обмеження ресурсів (Resource Invariants)
Будь-яка коректна реалізація логарифмічного трансд'юсера повинна підтримувати такі суворі інваріанти:

```
[Інваріант 1: Вхідна стрічка (Read-Only)]
Вхідна стрічка доступна тільки для читання. Жодна команда δ не може змінити вміст вхідної стрічки. 
Зчитувальна головка може довільно рухатися у будь-який бік, але вхідні дані є повністю незмінними.

[Інваріант 2: Робоча пам'ять (Space Bound)]
Кількість відвіданих комірок робочої стрічки протягом усього обчислення не перевищує:
S(n) ≤ c · ⌈log₂ n⌫ + d
де n = |x| — довжина вхідного слова, c > 0 та d ≥ 0 — сталі константи машини M.

[Інваріант 3: Вихідна стрічка (Write-Only & One-Way)]
Вихідна стрічка є монотонно зростаючою. Головка вихідної стрічки переміщується виключно вправо (рух 'L' заборонено).
Машина M НЕ здатна зчитувати раніше записані символи з вихідної стрічки.
```

Ці три інваріанти ґрантують, що трансд'юсер не може використати власну вихідну стрічку як додаткову робочу пам'ять.

---

## 2. Формальний контракт зведення за логарифмічною пам'яттю (≤_L API)

Зведення мови `A ⊆ Σ*` до мови `B ⊆ Σ*` за логарифмічною пам'яттю (`A ≤_L B`) визначає функціональний контракт між двома задачами.

У теорії NP-повноти використовують поліноміальні зведення за Карпом `≤_P`. Проте у внутрішній структурі класу P поліноміальне зведення є неефективним інструментом: поліноміальний трансд'юсер мав би достатньо ресурсів, щоб повністю розв'язати будь-яку задачу з L або NL самостійно, ще до звернення до цільової задачі. Зведення за логарифмічною пам'яттю `≤_L` гарантує, що трансд'юсер здійснює лише легку структурну трансформацію входу.

### Таблиця вимог та гарантій контракту зведення

| Елемент контракту | Математична специфікація | Інженерна інтерпретація |
| :--- | :--- | :--- |
| **Еквівалентність** | `∀ x ∈ Σ*: x ∈ A ⇔ f(x) ∈ B` | Слово `x` є розв'язком `A` ⇔ трансформоване слово `f(x)` є розв'язком `B`. |
| **Обмеження пам'яті** | `Space(M_f(x)) = O(\log \|x\|)` | Трансформація виконується у робочій пам'яті `O(\log n)`. |
| **Розмір виходу** | `\|f(x)\| ≤ \|x\|ᵏ + c` | Довжина вихідного слова `f(x)` обмежена поліномом від входу. |
| **Односпрямованість** | `OutputTape = WriteOnly` | Результат генерується у вигляді потоку бітів без перечитання. |

### Формальна визначеність L-повноти та NL-повноти
Мова `L_complete` є **NL-повною за логарифмічним зведенням**, якщо виконуються дві умови:
1. `L_complete ∈ NL`.
2. Для будь-якої мови `A ∈ NL` виконується логарифмічне зведення `A ≤_L L_complete`.

Аналогічно, мова є **P-повною за логарифмічним зведенням**, якщо вона належить до класу P і кожна задача з P зводиться до неї за допомогою логарифмічного трансд'юсера `≤_L`. Це демонструє, що логарифмічні зведення є універсальним інструментом калібрування складності всередині поліноміального часу.

---

## 3. Специфікація віртуального протоколу композиції (Lazy Bit Query Protocol)

Коли маємо два трансд'юсери `f: Σ* → Σ*` та `g: Σ* → Σ*`, пряме збереження виходу `f(x)` вимагало б `O(n^k)` пам'яті, що зламало б просторове обмеження `O(\log n)`. Для забезпечення транзитивності зведень `g(f(x))` застосовується віртуальний протокол за вимогою.

Замість збереження проміжного результату `f(x)` на диск чи у буфер RAM, симулятор виконання `g` розглядає вихід трансд'юсера `f` як **віртуальний потік даних**, звертаючись до нього через процедуру запиту конкретного біта.

### Архітектура інтерфейсу BitQuery
Замість передачі масиву даних, симулятор `g` взаємодіє з трансд'юсером `f` через функціональний інтерфейс:

```
char BitQuery(uint64_t bit_index, const char* original_input_x, uint64_t input_len)
```

### Алгоритмічна специфікація симуляції BitQuery

```
Специфікація функції BitQuery(i, x, n):
1. Перевірка межі: якщо i == 0 або i > MaxOutputLength(n), повернути EOF.
2. Ініціалізація симулятора трансд'юсера f:
   - Встановлюємо робочу пам'ять f у початковий стан (заповнюємо ⊔).
   - Встановлюємо стан q = q₀.
   - Встановлюємо вхідну головку f на позицію 1 вхідного слова x.
   - Встановлюємо внутрішній лічильник виведених символів: out_counter = 0.
3. Цикл обчислення трансд'юсера f:
   - Поки q ∉ {q_accept, q_reject}:
     a. Зчитуємо вхідний символ in_char = x[input_pos].
     b. Зчитуємо робочий символ work_char = work_tape[work_pos].
     c. Обчислюємо transition = δ(q, in_char, work_char).
     d. Оновлюємо робочу стрічку та стан: q = transition.new_state.
     e. Оновлюємо позицію вхідної головки input_pos += transition.input_move.
     f. Перевіряємо вихідний символ transition.emit_char:
        - Якщо transition.emit_char != ε:
          * Збільшуємо out_counter = out_counter + 1.
          * Якщо out_counter == i:
            Повертаємо значення transition.emit_char і СКИДАЄМО стан f!
4. Якщо машина f завершилася до того, як out_counter сягнув i, повернути EOF.
```

### Диаграма взаємодії станів при віртуальній композиції

```
 [ Симулятор g ]                      [ Оракул-симулятор f ]
       │                                       │
       │ ─── 1. BitQuery(index=42, x) ───────> │
       │                                       │ ── Скидання стану f
       │                                       │ ── Запуск f(x) від кроку 0
       │                                       │ ── Генерація 42 символів...
       │ <── 2. Повертає символ '1' ────────── │
       │                                       │ ── Скидання стану f
       │                                       │
       │ ─── 3. Обчислення продовжується ─────> │
```

Цей лінивий протокол дозволяє виконувати будь-яку скінченну кількість композицій `h(g(f(x)))` у пам'яті `O(\log n)`. Кожен наступний шар лише зберігає один додатковий індекс позиції для попереднього шару, що додає сталу кількість бітів пам'яті.

---

## 4. Системний POSIX-інтерфейс моніторингу логарифмічної пам'яті

При практичній реалізації алгоритмів із логарифмічною пам'яттю мовами C та C++ необхідно жорстко контролювати просторові ресурси на рівні операційної системи Linux/POSIX. Системний інтерфейс надає механізми для встановлення меж віртуальної пам'яті та стека, унеможливлюючи неконтрольоване динамічне виділення пам'яті.

### Обмеження ресурсів через setrlimit()
Два ключові параметри операційної системи визначають межі пам'яті процесу:
- **`RLIMIT_AS` (Virtual Memory Size):** максимальний обсяг віртуальної пам'яті процесу в байтах. Якщо процес намагається розширити свою адресну область через `mmap` або `brk` понад цю межу, операційна система повертає помилку `ENOMEM`.
- **`RLIMIT_STACK` (Stack Size):** максимальний розмір стека викликів процесу. При спробі перевищити цей поріг процес негайно термінується сигналом `SIGSEGV`.

Нижче наведено C-код встановлення жорсткого просторового обмеження для обчислювального процесу:

:::tabs
```c
#include <sys/resource.h>
#include <stdio.h>
#include <stdlib.h>

/* Sets strict virtual memory limit for logspace execution */
int set_logspace_memory_limit(size_t limit_bytes) {
    struct rlimit rl;
    
    rl.rlim_cur = limit_bytes; /* Soft limit */
    rl.rlim_max = limit_bytes; /* Hard limit */

    if (setrlimit(RLIMIT_AS, &rl) != 0) {
        perror("Failed to set RLIMIT_AS memory limit");
        return -1;
    }
    
    return 0;
}
```
```cpp
// C++20 implementation: Memory limit configuration with std::expected
#include <sys/resource.h>
#include <system_error>
#include <expected>
#include <cstddef>
#include <cerrno>

namespace space_complexity {

[[nodiscard]] inline std::expected<void, std::error_code> set_logspace_memory_limit(size_t limit_bytes) noexcept {
    struct rlimit rl;
    rl.rlim_cur = limit_bytes;
    rl.rlim_max = limit_bytes;

    if (setrlimit(RLIMIT_AS, &rl) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

} // namespace space_complexity
```
:::

### Програмувальний інтерфейс Arena-алокатора з фіксованим буфером
Для запобігання динамічному виділенню пам'яті (`malloc`/`free`) реалізується арена-алокатор фіксованого розміру `O(\log n)`, який гарантує виконання обчислення у межах заздалегідь виділеного статичного буфера.

:::tabs
```c
/* C11 Static Arena Allocator contract for Logspace Execution */
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#define LOGSPACE_BUFFER_SIZE 4096 /* 4 KB fixed work tape */

typedef struct {
    uint8_t buffer[LOGSPACE_BUFFER_SIZE];
    size_t offset;
} LogspaceArena;

void logspace_arena_init(LogspaceArena *arena) {
    arena->offset = 0;
}

void* logspace_arena_alloc(LogspaceArena *arena, size_t bytes) {
    /* Align bytes to 8-byte boundary */
    size_t aligned_bytes = (bytes + 7) & ~((size_t)7);
    
    if (arena->offset + aligned_bytes > LOGSPACE_BUFFER_SIZE) {
        return NULL; /* Out of logspace buffer error! */
    }
    
    void *ptr = &arena->buffer[arena->offset];
    arena->offset += aligned_bytes;
    return ptr;
}

void logspace_arena_reset(LogspaceArena *arena) {
    arena->offset = 0;
}
```
```cpp
// C++20 Fixed Work-Tape Allocator Specification
#include <cstddef>
#include <cstdint>
#include <span>
#include <array>
#include <expected>
#include <new>

namespace space_complexity {

template <size_t BufferSize = 4096>
class FixedWorkTape {
public:
    constexpr FixedWorkTape() noexcept : offset_(0) {}

    // Non-copyable, non-movable to guarantee physical memory stability
    FixedWorkTape(const FixedWorkTape&) = delete;
    FixedWorkTape& operator=(const FixedWorkTape&) = delete;

    [[nodiscard]] std::expected<std::span<uint8_t>, std::errc> allocate(size_t bytes) noexcept {
        const size_t aligned = (bytes + 7) & ~size_t{7};
        if (offset_ + aligned > BufferSize) {
            return std::unexpected(std::errc::not_enough_memory);
        }
        uint8_t* ptr = &buffer_[offset_];
        offset_ += aligned;
        return std::span<uint8_t>(ptr, bytes);
    }

    constexpr void reset() noexcept {
        offset_ = 0;
    }

    [[nodiscard]] constexpr size_t used_bytes() const noexcept {
        return offset_;
    }

    [[nodiscard]] constexpr size_t capacity() const noexcept {
        return BufferSize;
    }

private:
    alignas(8) std::array<uint8_t, BufferSize> buffer_{};
    size_t offset_{0};
};

} // namespace space_complexity
```
:::

---

## 5. Зчитування метрик пам'яті через procfs та getrusage()

Для верифікації того, що виконана програма не вийшла за межі `O(\log n)` бітів оперативної пам'яті, використовуються системні виклики POSIX та простеження через `/proc/self/statm`.

Аналіз споживання пам'яті процесу в Linux здійснюється на основі концепції сторінок пам'яті (Page Size, зазвичай 4096 байтів). Програма може профілювати пікове використання пам'яті для перевірки відповідності просторовим обмеженням.

### Інтерфейс виклику getrusage()
Структура `rusage` повертає максимальний розмір резидентної пам'яті (Resident Set Size, RSS), який показує фізичний обсяг RAM, виділений процесу ядрами Linux:

:::tabs
```c
#include <sys/resource.h>
#include <stdio.h>

void print_peak_memory_usage(void) {
    struct rusage usage;
    if (getrusage(RUSAGE_SELF, &usage) == 0) {
        /* ru_maxrss returns memory in kilobytes on Linux */
        printf("Peak Resident Set Size (RSS): %ld KB\n", usage.ru_maxrss);
    }
}
```
```cpp
// C++20 implementation: Memory usage reader with std::optional
#include <sys/resource.h>
#include <iostream>
#include <optional>
#include <cstdint>

namespace space_complexity {

[[nodiscard]] inline std::optional<uint64_t> get_peak_rss_kb() noexcept {
    struct rusage usage;
    if (getrusage(RUSAGE_SELF, &usage) == 0) {
        return static_cast<uint64_t>(usage.ru_maxrss);
    }
    return std::nullopt;
}

inline void print_peak_memory_usage() {
    if (auto rss = get_peak_rss_kb(); rss.has_value()) {
        std::cout << "Peak Resident Set Size (RSS): " << *rss << " KB\n";
    }
}

} // namespace space_complexity
```
:::

### Програмний доступ до procfs (/proc/self/statm)
Файл `/proc/self/statm` у Linux надає точну інформацію про сторінки пам'яті процесу в реальному часі. Зчитування цього файла не створює накладних витрат і може виконуватися у будь-який момент виконання алгоритму.

Поля файлу `/proc/self/statm`:
1. `size` — загальний розмір програмованої віртуальної пам'яті (у сторінках).
2. `resident` — кількість резидентних сторінок у RAM.
3. `shared` — кількість спільних (shared) сторінок пам'яті.
4. `text` — розмір коду (виконуваного сегмента).
5. `data` — розмір стека та даних.

:::tabs
```c
/* C11 procfs memory reader for Logspace Verification */
#include <stdio.h>
#include <stdint.h>

typedef struct {
    uint64_t total_pages;
    uint64_t resident_pages;
    uint64_t shared_pages;
} StatmMemoryInfo;

bool read_proc_statm(StatmMemoryInfo *info) {
    FILE *f = fopen("/proc/self/statm", "r");
    if (!f) return false;

    if (fscanf(f, "%lu %lu %lu", &info->total_pages, &info->resident_pages, &info->shared_pages) != 3) {
        fclose(f);
        return false;
    }

    fclose(f);
    return true;
}
```
```cpp
// C++20 procfs Memory Monitor Specification
#include <fstream>
#include <cstdint>
#include <optional>
#include <string>

namespace space_complexity {

struct ProcMemoryStats {
    uint64_t total_pages{0};
    uint64_t resident_pages{0};
    uint64_t shared_pages{0};

    [[nodiscard]] uint64_t resident_bytes(uint64_t page_size = 4096) const noexcept {
        return resident_pages * page_size;
    }
};

class ProcfsMonitor {
public:
    [[nodiscard]] static std::optional<ProcMemoryStats> current_usage() noexcept {
        std::ifstream statm_file("/proc/self/statm");
        if (!statm_file.is_open()) {
            return std::nullopt;
        }

        ProcMemoryStats stats;
        if (statm_file >> stats.total_pages >> stats.resident_pages >> stats.shared_pages) {
            return stats;
        }
        return std::nullopt;
    }
};

} // namespace space_complexity
```
:::

### Специфікація таблиці порівняння просторових системних викликів

| POSIX API / Файл | Призначення | Обмеження / Точність | Застосування в Logspace |
| :--- | :--- | :--- | :--- |
| **`setrlimit(RLIMIT_AS)`** | Встановлення межі віртуальної пам'яті | Точність до байта | Блокування `malloc` при перевищенні порогу. |
| **`setrlimit(RLIMIT_STACK)`** | Встановлення межі стека викликів | Точність до сторінки (4 KB) | Запобігання глибокій рекурсії за межі `O(\log² n)`. |
| **`getrusage(RUSAGE_SELF)`** | Отримання максимального RSS | Точність у KB (`ru_maxrss`) | Профілювання пікового споживання пам'яті. |
| **`/proc/self/statm`** | Зчитування поточного стану сторінок | Динамічне зчитування у сторінках | Моніторинг у реальному часі без зупинки процесу. |

Ця специфікація повністю описує інтерфейсний та системний контракт логарифмічного трансд'юсера, гарантуючи коректне розмежування ресурсів як на математичному, так і на апаратно-системному рівнях.
