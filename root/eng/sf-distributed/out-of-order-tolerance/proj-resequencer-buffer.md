# ⚙️ Практична реалізація: ковзний буфер перевпорядкування (Resequencer)

Коли розподілена система не може зробити всі операції комутативними, вона змушена відновлювати лінійний порядок повідомлень безпосередньо перед передачею їх прикладному обробнику. Якщо споживач отримує потік із паралельних каналів або партицій із прогалинами у номерах послідовності, наївне очікування може призвести до мертвого блокування (англ. *deadlock*) або вичерпання оперативної пам'яті.

У цьому проекті реалізовано високопродуктивний ковзний буфер перевпорядкування (англ. *sliding resequencer buffer*). Він приймає повідомлення з довільними номерами послідовності, миттєво віддає неперервні ланцюжки, буферизує забігаючі наперед пакети, а в разі втрати пакетів спрацьовує за таймаутом прогалини (англ. *gap timeout*), примусово просуваючи вікно вперед.

## Архітектура та інваріанти буфера

Буфер підтримує такі ключові інваріанти та інженерні властивості:

1. **Монотонний лічильник доставки `expected_seq`:** Номер наступного обов'язкового повідомлення, яке очікує бізнес-обробник.
2. **Обмежене вікно пам'яті `WINDOW_CAPACITY`:** Захист від атак вичерпання пам'яті або збійних клієнтів, які надсилають повідомлення з нереалістично великими номерами послідовності.
3. **Таймер виявлення прогалини `gap_deadline`:** Якщо повідомлення з номером `expected_seq` затримується довше за встановлений ліміт `timeout_ms`, система вважає його безповоротно втраченим, викликає обробник пропуску (*on_gap_drop*) і скидає накопичені в буфері новіші повідомлення.
4. **Ідемпотентний фільтр дублікатів:** Будь-яке повідомлення з `seq < expected_seq` негайно відкидається без виділення пам'яті та без побічних ефектів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define RESEQUENCER_CAPACITY 256

typedef struct {
    uint64_t seq;
    char payload[128];
    bool occupied;
    uint64_t arrival_time_ms;
} ResequencerSlot;

typedef void (*DeliverCallback)(uint64_t seq, const char* payload, void* user_data);
typedef void (*GapDropCallback)(uint64_t lost_seq, void* user_data);

typedef struct {
    uint64_t expected_seq;
    uint64_t gap_timeout_ms;
    uint64_t gap_detected_at_ms;
    bool has_active_gap;
    ResequencerSlot buffer[RESEQUENCER_CAPACITY];
    DeliverCallback on_deliver;
    GapDropCallback on_gap_drop;
    void* user_data;
} Resequencer;

static uint64_t get_current_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;
}

void resequencer_init(Resequencer* r, uint64_t start_seq, uint64_t gap_timeout_ms,
                      DeliverCallback deliver_cb, GapDropCallback drop_cb, void* user_data) {
    r->expected_seq = start_seq;
    r->gap_timeout_ms = gap_timeout_ms;
    r->gap_detected_at_ms = 0;
    r->has_active_gap = false;
    r->on_deliver = deliver_cb;
    r->on_gap_drop = drop_cb;
    r->user_data = user_data;
    for (size_t i = 0; i < RESEQUENCER_CAPACITY; ++i) {
        r->buffer[i].occupied = false;
    }
}

static void flush_continuous_prefix(Resequencer* r) {
    while (true) {
        size_t slot_idx = r->expected_seq % RESEQUENCER_CAPACITY;
        ResequencerSlot* slot = &r->buffer[slot_idx];

        if (!slot->occupied || slot->seq != r->expected_seq) {
            break; // Знайдено прогалину
        }

        // Передаємо впорядковане повідомлення прикладному обробнику
        r->on_deliver(slot->seq, slot->payload, r->user_data);
        slot->occupied = false;
        r->expected_seq++;
    }

    // Перевіряємо, чи лишилися в буфері майбутні повідомлення
    bool has_pending = false;
    for (size_t i = 0; i < RESEQUENCER_CAPACITY; ++i) {
        if (r->buffer[i].occupied) {
            has_pending = true;
            break;
        }
    }

    if (has_pending) {
        if (!r->has_active_gap) {
            r->has_active_gap = true;
            r->gap_detected_at_ms = get_current_time_ms();
        }
    } else {
        r->has_active_gap = false;
    }
}

bool resequencer_push(Resequencer* r, uint64_t seq, const char* payload) {
    uint64_t now = get_current_time_ms();

    // 1. Відкидаємо застарілі дублікати
    if (seq < r->expected_seq) {
        return false;
    }

    // 2. Якщо повідомлення прибуло точно вчасно
    if (seq == r->expected_seq) {
        r->on_deliver(seq, payload, r->user_data);
        r->expected_seq++;
        flush_continuous_prefix(r);
        return true;
    }

    // 3. Позачергове майбутнє повідомлення — перевірка меж вікна
    if (seq >= r->expected_seq + RESEQUENCER_CAPACITY) {
        // Повідомлення виходить за межі буфера (Window Overflow)
        return false;
    }

    size_t slot_idx = seq % RESEQUENCER_CAPACITY;
    ResequencerSlot* slot = &r->buffer[slot_idx];

    if (slot->occupied && slot->seq == seq) {
        return false; // Повторний дублікат у буфері
    }

    slot->seq = seq;
    strncpy(slot->payload, payload, sizeof(slot->payload) - 1);
    slot->payload[sizeof(slot->payload) - 1] = '\0';
    slot->occupied = true;
    slot->arrival_time_ms = now;

    if (!r->has_active_gap) {
        r->has_active_gap = true;
        r->gap_detected_at_ms = now;
    }

    return true;
}

void resequencer_tick(Resequencer* r) {
    if (!r->has_active_gap) {
        return;
    }

    uint64_t now = get_current_time_ms();
    if (now - r->gap_detected_at_ms >= r->gap_timeout_ms) {
        // Таймаут вичерпано: фіксуємо втрату очікуваного повідомлення
        r->on_gap_drop(r->expected_seq, r->user_data);
        r->expected_seq++; // Примусово пропускаємо прогалину
        r->has_active_gap = false;

        // Просуваємо буфер далі
        flush_continuous_prefix(r);
    }
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <map>
#include <chrono>
#include <functional>
#include <optional>
#include <memory>

class Resequencer {
public:
    using Clock = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;
    using DeliverHandler = std::function<void(uint64_t seq, std::string_view payload)>;
    using GapDropHandler = std::function<void(uint64_t lost_seq)>;

    Resequencer(uint64_t start_seq,
                std::chrono::milliseconds gap_timeout,
                size_t max_window_size,
                DeliverHandler on_deliver,
                GapDropHandler on_gap_drop)
        : expected_seq_(start_seq)
        , gap_timeout_(gap_timeout)
        , max_window_size_(max_window_size)
        , on_deliver_(std::move(on_deliver))
        , on_gap_drop_(std::move(on_gap_drop)) {}

    bool push(uint64_t seq, std::string payload) {
        const auto now = Clock::now();

        // 1. Фільтрація старих дублікатів
        if (seq < expected_seq_) {
            return false;
        }

        // 2. Точне вчасне прибуття
        if (seq == expected_seq_) {
            on_deliver_(seq, payload);
            ++expected_seq_;
            flush_continuous_prefix(now);
            return true;
        }

        // 3. Перевірка ліміту вікна буфера
        if (seq >= expected_seq_ + max_window_size_) {
            return false; // Відхилено: надто далеке майбутнє
        }

        // 4. Збереження у відсортованій мапі
        auto [it, inserted] = buffer_.emplace(seq, std::move(payload));
        if (!inserted) {
            return false; // Дублікат уже в буфері
        }

        if (!gap_start_time_.has_value()) {
            gap_start_time_ = now;
        }

        return true;
    }

    void tick() {
        if (!gap_start_time_.has_value()) {
            return;
        }

        const auto now = Clock::now();
        if (now - *gap_start_time_ >= gap_timeout_) {
            // Таймаут очікування: пропускаємо втрачений seq
            on_gap_drop_(expected_seq_);
            ++expected_seq_;
            gap_start_time_.reset();

            flush_continuous_prefix(now);
        }
    }

    [[nodiscard]] uint64_t expected_sequence() const noexcept { return expected_seq_; }
    [[nodiscard]] size_t buffered_count() const noexcept { return buffer_.size(); }

private:
    void flush_continuous_prefix(TimePoint now) {
        while (!buffer_.empty()) {
            auto it = buffer_.begin();
            if (it->first != expected_seq_) {
                break; // Натрапили на наступну прогалину
            }

            on_deliver_(it->first, it->second);
            buffer_.erase(it);
            ++expected_seq_;
        }

        if (!buffer_.empty()) {
            if (!gap_start_time_.has_value()) {
                gap_start_time_ = now;
            }
        } else {
            gap_start_time_.reset();
        }
    }

    uint64_t expected_seq_;
    std::chrono::milliseconds gap_timeout_;
    size_t max_window_size_;
    DeliverHandler on_deliver_;
    GapDropHandler on_gap_drop_;

    std::map<uint64_t, std::string> buffer_;
    std::optional<TimePoint> gap_start_time_;
};
```
:::

## Глибокий розбір сценаріїв виконання

### 1. Ідеальний неперервний потік (Zero-Copy Fast Path)
Коли повідомлення прибувають у природному порядку `#100, #101, #102`, алгоритм працює за швидким шляхом (англ. *fast path*):
- Повідомлення `#100` порівнюється з `expected_seq = 100`.
- Оскільки `seq == expected_seq`, воно миттєво передається безпосередньо у функцію `on_deliver` без жодного копіювання у внутрішні таблиці чи виділення пам'яті в купі (*heap allocation*).
- Лічильник `expected_seq` збільшується до `101`. Буфер лишається абсолютно порожнім, затримка дорівнює нулю.

### 2. Забігання вперед та вибухове скидання (Out-of-Order Burst & Drain)
Розглянемо випадок надходження пакета з випередженням черги:
- Надходить потік: `#100`, потім `#103`, `#104`, `#105`.
- Пакет `#100` обробляється миттєво. Лічильник переходить у стан `expected_seq = 101`.
- Пакет `#103` фіксує прогалину (`103 > 101`). Він записується у внутрішній слот пам'яті, а система фіксує мітку часу початку прогалини `gap_detected_at_ms`.
- Пакети `#104` та `#105` так само зберігаються в буфері, не скидаючи початковий таймер прогалини.
- Коли через 15 мілісекунд надходить запізнілий пакет `#101`, метод `push` передає `#101` обробнику, збільшує `expected_seq = 102` і запускає цикл `flush_continuous_prefix()`.
- Якщо слідом надходить `#102`, буфер виявляє повний неперервний ланцюг і каскадно за один прохід виштовхує `#102 → #103 → #104 → #105`, скидаючи таймер активної прогалини.

### 3. Фізична втрата пакета та відновлення за таймаутом (Gap Drop & Recovery)
Якщо пакет `#101` було безповоротно втрачено (наприклад, через збій комутатора або аварійне падіння вузла-видавця), лічильник `expected_seq` залишається на значенні `101`.
- Періодичний виклик `tick()` (або фоновий таймер) порівнює поточний монотонний час із часом виявлення прогалини.
- Щойно різниця перевищує `gap_timeout_ms` (наприклад, 100 мс), буфер викликає функцію `on_gap_drop(101)`.
- Система збільшує `expected_seq = 102`, примусово переступаючи втрачений пакет, і моментально скидає всі накопичені наступні повідомлення `#103, #104, #105`.
- Це гарантує, що жодна мережева втрата не спричинить вічного зависання системи або переповнення оперативної пам'яті.

## Порівняння структур даних для буферизації

При виборі внутрішньої структури зберігання буфера інженер стикається з компромісом між пам'яттю, швидкістю та передбачуваністю латентності:

| Структура даних | Складність вставки | Складність виштовхування | Виділення пам'яті | Кеш-локальність | Рекомендоване застосування |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Кільцевий масив (Ring Buffer, як у C)** | `O(1)` | `O(1)` | `0` (статичний масив) | Ідеальна (послідовна пам'ять L1/L2) | Високонавантажені мережеві драйвери, L4-проксі, робота на рівні ядра |
| **Червоно-чорне дерево (`std::map`, як у C++)** | `O(log N)` | `O(1)` амортизовано | Динамічне на кожне повідомлення | Низька (розкидані вузли дерева) | Застосунки з довільним великим діапазоном запізнень і змінним розміром корисного навантаження |
| **Невпорядкований хеш-масив (`std::unordered_map`)** | `O(1)` в середньому | `O(1)` | Динамічне на кожне повідомлення | Середня (бакети) | Системи з великою кількістю розріджених ключів та ідентифікаторів потоків |

## Арифметика переповнення номерів послідовності

У реальних мережевих протоколах (наприклад, TCP або RTP) номери послідовності кодуються фіксованою розрядністю (`uint32_t` або `uint16_t`). Після досягнення значення `2³² - 1` наступний номер переповнюється і стає `0`.

Для коректного порівняння номерів в умовах переповнення використовується **арифметика послідовних чисел** (RFC 1982 *Serial Number Arithmetic*). Два числа `s₁` та `s₂` порівнюються через знакову різницю в просторі чисел по модулю `2ⁿ`:

:::tabs
```c
// Порівняння 32-розрядних номерів за стандартом RFC 1982:
// Повертає true, якщо s1 передує s2 у ковзному вікні розміром 2^31
static inline bool seq_less_than(uint32_t s1, uint32_t s2) {
    return (int32_t)(s1 - s2) < 0;
}
```
```cpp
#include <cstdint>

// Порівняння 32-розрядних номерів за стандартом RFC 1982
[[nodiscard]] constexpr bool seq_less_than(uint32_t s1, uint32_t s2) noexcept {
    return static_cast<int32_t>(s1 - s2) < 0;
}
```
:::

У 64-розрядних системах (`uint64_t`), де лічильник зростає на 1 000 000 повідомлень за секунду, переповнення настане лише через 584 942 роки, тому звичайне порівняння `seq < expected_seq` є абсолютно безпечним.

## Розрахунок таймауту прогалини та інтеграція в асинхронні цикли

Вибір значення `gap_timeout_ms` — це класичний архітектурний компроміс між повнотою даних та затримкою конвеєра:

1. **Занадто малий таймаут (наприклад, 5 мс при середньому RTT 20 мс):** Буфер буде передчасно скидати прогалини. Запізнілі повідомлення приходитимуть одразу після спрацьовування таймауту й відкидатимуться як застарілі дублікати, викликаючи штучну втрату даних.
2. **Занадто великий таймаут (наприклад, 5000 мс):** Будь-яка реальна втрата пакета зупинятиме весь потік на 5 секунд, що неприпустимо для інтерактивних сервісів.

**Формула практичного тюнінгу:**
```
gap_timeout_ms = p99.9(Network_RTT) + p99.9(Producer_Retry_Delay) + Safety_Margin
```
Для внутрішньокластерної комунікації в межах одного дата-центру типове значення становить `20–50 мс`. Для глобальної міжрегіональної мережі або мобільних клієнтів `gap_timeout_ms` встановлюють на рівні `200–500 мс`.

### Інтеграція в асинхронний цикл I/O (epoll / timerfd)
У високопродуктивних серверах виклик `tick()` не виконують у щільному нескінченному циклі опитування (*busy-wait*), оскільки це марно споживає 100% процесорного часу ядра. Натомість буфер інтегрують із подієвим циклом операційної системи через таймерні файлові дескриптори (`timerfd_create` на Linux або таймери `kqueue` на BSD/macOS). Коли виявляється перша прогалина, дескриптор `timerfd` армується на інтервал `gap_timeout_ms`. Ядро ОС прокидає потік обробника через `epoll_wait` лише тоді, коли таймаут справді вичерпано або в сокет надійшов новий мережевий пакет.
