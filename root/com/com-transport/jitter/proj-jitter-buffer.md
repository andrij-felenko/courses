# ⚙️ Реалізація адаптивного буфера джитеру на C та C++

Буфер відтворення (Jitter Buffer) компенсує нестабільність часу прибуття мережевих пакетів, накопичуючи їх у впорядкованій черзі та видаючи звуковому драйверу або відеоплеєру з фіксованим строгим періодом. Без цього механізму найменша затримка пакета в маршрутизаторі викликає буферне виснаження аудіокарти (underrun), що сприймається людиною як тріск або випадіння слів.

Нижче наведено робочу реалізацію адаптивного буфера для аудіопотоку реального часу з відстеженням мережевого джитеру, перевпорядкуванням пакетів та визначенням дедлайнів відтворення.

---

### Архітектура та життєвий цикл пакета в буфері

Робота адаптивного буфера джитеру розділена між двома незалежними асинхронними потоками виконання: мережевим потоком прийому (Network Thread) та звуковим потоком вичитування (Audio Render Callback).

```
   Мережевий потік (UDP Socket)               Звуковий потік (DAC Callback)
          │                                                  │
          ▼                                                  ▼
   Отримано пакет UDP                             Спрацював таймер ЦАП (20 мс)
          │                                                  │
          ▼                                                  ▼
   Парсинг RTP (Seq, Time)                       Визначення next_play_seq
          │                                                  │
          ▼                                                  ▼
   Перевірка: чи не запізнився?                  Пошук у слоті (seq % Size)
   ┌──────┴──────┐                                    ┌──────┴──────┐
   ▼             ▼                                    ▼             ▼
[Запізнився]  [Вчасно]                             [Знайдено]   [Порожньо]
   │             │                                    │             │
   ▼             ▼                                    ▼             ▼
Late Drop    Вставка в кільце                      Видача на   Виклик PLC
             Оновлення EWMA                          ЦАП       (маскування)
```

1. **Мережевий потік (Ingress):** вичитує UDP-сокет, витягує заголовок RTP (номер послідовності `Sequence Number` та часову мітку `Timestamp`), фіксує локальний час надходження `arrival_time`, оновлює фільтр оцінки джитеру та записує корисне навантаження у відповідну комірку кільцевого масиву.
2. **Звуковий потік (Egress):** викликається апаратним перериванням аудіодрайвера строго кожні 20 мс. Він перевіряє слот з очікуваним номером `next_play_seq`. Якщо кадр присутній — він копіюється в буфер ЦАП; якщо кадр відсутній через затримку в мережі — фіксується подія `Underrun` і запускається алгоритм маскування втрат (PLC).

---

### Програмна реалізація

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define BUFFER_SLOTS      64
#define MAX_PAYLOAD_SIZE  160  /* 20 мс G.711 аудіо при 8 кГц */
#define CLOCK_RATE_HZ     8000
#define PACKET_TIME_MS    20
#define SAMPLES_PER_FRAME (CLOCK_RATE_HZ * PACKET_TIME_MS / 1000)

typedef struct {
    uint16_t seq_num;
    uint32_t timestamp;
    uint32_t arrival_time_ms;
    uint8_t  payload[MAX_PAYLOAD_SIZE];
    size_t   payload_len;
    bool     occupied;
} PacketSlot;

typedef struct {
    PacketSlot slots[BUFFER_SLOTS];
    uint16_t   next_play_seq;
    uint32_t   target_delay_ms;
    uint32_t   min_transit_ms;
    int32_t    jitter_q4;        /* Джитер у форматі Q4 (фіксована кома * 16) */
    uint32_t   last_transit_ms;
    bool       initialized;
    
    /* Статистика */
    uint32_t   packets_received;
    uint32_t   packets_played;
    uint32_t   packets_late_dropped;
    uint32_t   packets_underrun;
} JitterBuffer;

void jb_init(JitterBuffer *jb, uint32_t initial_target_delay_ms) {
    memset(jb, 0, sizeof(JitterBuffer));
    jb->target_delay_ms = initial_target_delay_ms;
    jb->min_transit_ms = UINT32_MAX;
}

/* Порівняння 16-бітних номерів послідовності з урахуванням переповнення */
static inline bool seq_less(uint16_t s1, uint16_t s2) {
    return (int16_t)(s1 - s2) < 0;
}

void jb_put_packet(JitterBuffer *jb, uint16_t seq, uint32_t timestamp,
                   const uint8_t *payload, size_t len, uint32_t arrival_ms) {
    jb->packets_received++;

    if (!jb->initialized) {
        jb->next_play_seq = seq;
        jb->initialized = true;
    }

    /* Відкидаємо пакети, чий дедлайн відтворення вже минув */
    if (seq_less(seq, jb->next_play_seq)) {
        jb->packets_late_dropped++;
        return;
    }

    /* Оцінка транзитної затримки та джитеру (RFC 3550 EWMA) */
    uint32_t transit_ms = arrival_ms - (timestamp / (CLOCK_RATE_HZ / 1000));
    if (transit_ms < jb->min_transit_ms) {
        jb->min_transit_ms = transit_ms;
    }

    if (jb->packets_received > 1) {
        int32_t diff_ms = (int32_t)transit_ms - (int32_t)jb->last_transit_ms;
        if (diff_ms < 0) diff_ms = -diff_ms;
        
        /* J_i = J_{i-1} + (|D| - J_{i-1}) / 16 */
        jb->jitter_q4 += diff_ms - (jb->jitter_q4 >> 4);
    }
    jb->last_transit_ms = transit_ms;

    /* Адаптація цільової затримки: Target = MinDelay + 3 * Jitter */
    uint32_t current_jitter_ms = (uint32_t)(jb->jitter_q4 >> 4);
    uint32_t calculated_target = current_jitter_ms * 3 + 20;
    if (calculated_target < 20) calculated_target = 20;
    if (calculated_target > 200) calculated_target = 200;
    jb->target_delay_ms = calculated_target;

    /* Збереження пакета в кільцевий слот */
    size_t idx = seq % BUFFER_SLOTS;
    PacketSlot *slot = &jb->slots[idx];
    slot->seq_num = seq;
    slot->timestamp = timestamp;
    slot->arrival_time_ms = arrival_ms;
    slot->payload_len = (len > MAX_PAYLOAD_SIZE) ? MAX_PAYLOAD_SIZE : len;
    memcpy(slot->payload, payload, slot->payload_len);
    slot->occupied = true;
}

/* Вичитування аудіокадру для відтворення (викликається кожні 20 мс) */
bool jb_get_frame(JitterBuffer *jb, uint8_t *out_frame, size_t *out_len) {
    if (!jb->initialized) {
        return false;
    }

    size_t idx = jb->next_play_seq % BUFFER_SLOTS;
    PacketSlot *slot = &jb->slots[idx];

    if (slot->occupied && slot->seq_num == jb->next_play_seq) {
        memcpy(out_frame, slot->payload, slot->payload_len);
        *out_len = slot->payload_len;
        slot->occupied = false;
        jb->next_play_seq++;
        jb->packets_played++;
        return true;
    }

    /* Буферне виснаження: потрібний пакет ще не дійшов */
    jb->packets_underrun++;
    jb->next_play_seq++; /* Пропускаємо дедлайн, передаємо керування PLC */
    return false;
}
```
```cpp
#include <iostream>
#include <vector>
#include <optional>
#include <span>
#include <cstdint>
#include <algorithm>
#include <chrono>

class AdaptiveJitterBuffer {
public:
    static constexpr size_t BufferCapacity = 64;
    static constexpr uint32_t ClockRateHz = 8000;
    static constexpr uint32_t FrameDurationMs = 20;

    struct Frame {
        uint16_t sequence_number;
        uint32_t timestamp;
        std::chrono::milliseconds arrival_time;
        std::vector<uint8_t> payload;
    };

    explicit AdaptiveJitterBuffer(std::chrono::milliseconds initial_target_delay = std::chrono::milliseconds(40))
        : target_delay_(initial_target_delay),
          slots_(BufferCapacity) {}

    void push_packet(uint16_t seq, uint32_t timestamp,
                     std::span<const uint8_t> payload,
                     std::chrono::milliseconds arrival_time) {
        packets_received_++;

        if (!initialized_) {
            next_play_seq_ = seq;
            initialized_ = true;
        }

        // Перевірка, чи не запізнився пакет остаточно
        if (seq_less(seq, next_play_seq_)) {
            packets_late_dropped_++;
            return;
        }

        // Оцінка затримки проходження та оновлення джитеру
        auto send_time_ms = std::chrono::milliseconds(timestamp / (ClockRateHz / 1000));
        auto transit_time = arrival_time - send_time_ms;

        if (last_transit_time_.has_value()) {
            auto delta = std::abs((transit_time - *last_transit_time_).count());
            // EWMA-фільтр RFC 3550: J_i = J_{i-1} + (|D| - J_{i-1}) / 16
            jitter_q4_ += static_cast<int32_t>(delta) - (jitter_q4_ >> 4);
        }
        last_transit_time_ = transit_time;

        // Адаптивне налаштування глибини буфера
        auto current_jitter_ms = static_cast<uint32_t>(jitter_q4_ >> 4);
        target_delay_ = std::chrono::milliseconds(
            std::clamp(current_jitter_ms * 3 + FrameDurationMs, 20u, 250u)
        );

        // Вставка у чергу
        size_t slot_idx = seq % BufferCapacity;
        slots_[slot_idx] = Frame{
            .sequence_number = seq,
            .timestamp = timestamp,
            .arrival_time = arrival_time,
            .payload = {payload.begin(), payload.end()}
        };
    }

    [[nodiscard]] std::optional<Frame> pop_frame() {
        if (!initialized_) {
            return std::nullopt;
        }

        size_t slot_idx = next_play_seq_ % BufferCapacity;
        auto& slot = slots_[slot_idx];

        if (slot.has_value() && slot->sequence_number == next_play_seq_) {
            Frame result = std::move(*slot);
            slot.reset();
            next_play_seq_++;
            packets_played_++;
            return result;
        }

        // Буферне виснаження: викликається модуль маскування втрат (PLC)
        packets_underrun_++;
        next_play_seq_++;
        return std::nullopt;
    }

    [[nodiscard]] std::chrono::milliseconds target_delay() const noexcept {
        return target_delay_;
    }

private:
    static bool seq_less(uint16_t s1, uint16_t s2) noexcept {
        return static_cast<int16_t>(s1 - s2) < 0;
    }

    std::chrono::milliseconds target_delay_;
    std::vector<std::optional<Frame>> slots_;
    uint16_t next_play_seq_{0};
    int32_t jitter_q4_{0};
    std::optional<std::chrono::milliseconds> last_transit_time_;
    bool initialized_{false};

    uint32_t packets_received_{0};
    uint32_t packets_played_{0};
    uint32_t packets_late_dropped_{0};
    uint32_t packets_underrun_{0};
};
```
:::

---

### Детальний аналіз ключових механізмів

#### 1. Модульна арифметика номерів послідовності RTP
Номер послідовності RTP є 16-бітним беззнаковим цілим (`uint16_t`), яке інкрементується на 1 для кожного надісланого пакета. Після досягнення значення `65535` наступний пакет отримує номер `0` (Sequence Rollover).

Пряме порівняння `seq1 < seq2` некоректно інтерпретує перехід: пакет з номером `0` вважатиметься старішим за пакет `65535`, що призведе до масового скидання валідних пакетів. Для розв'язання цієї проблеми застосовується модульне віднімання зі знаковим приведенням: `(int16_t)(s1 - s2) < 0`.

Принцип роботи: якщо `s1 = 65535` та `s2 = 0`, то `(uint16_t)(65535 - 0) = 65535`. Приведення до `int16_t` інтерпретує це число як `-1`. Умова `-1 < 0` повертає `true`, коректно визначаючи, що пакет 65535 передував пакету 0. Таке порівняння коректно працює для будь-якої дистанції перевпорядкування аж до `2¹⁵ - 1 = 32767` пакетів.

#### 2. Фіксована кома Q4 для фільтрації EWMA
У реалізації на мові C обчислення джитеру здійснюється у форматі фіксованої коми Q4 (ціле число домножене на 16): `jb->jitter_q4 += diff_ms - (jb->jitter_q4 >> 4);`.

Це дозволяє уникнути операцій із плаваючою комою `float` або `double` у внутрішньому ядрі обробника пакетів. Старші біти зберігають цілу частину мілісекунд, а 4 молодші біти — дробову частину з роздільною здатністю `1/16 = 0.0625` мс.

---

### Алгоритми динамічного масштабування часу (Time Scaling)

Якщо адаптивний буфер виявляє, що мережева затримка стабілізувалася і поточна глибина черги (наприклад, 120 мс) є надлишковою, просто викинути зайві кадри не можна — це викличе різкий акустичний тріск. Необхідно плавно «наздогнати» потік, прискоривши відтворення звуку на 5–10% непомітно для людського вуха.

```
Вхідний семпл                                    Результат WSOLA
[ Період 1 ][ Період 2 ][ Період 3 ]     ───►    [ Період 1 ][ Період 3 ]
                  ▲                                    ▲
                  └────── Перекриття та злиття ────────┘
```

#### Алгоритм WSOLA (Waveform Similarity Overlap-Add)
Для зміни тривалості сигналу без зміни висоти тону (Pitch) використовується метод часового перекриття з пошуком максимальної подібності хвильової форми:

1. **Аналіз автокореляції:** Алгоритм шукає довжину основного періоду коливання голосових зв'язок (Pitch Period, типово від 2 до 15 мс). Для цього обчислюється взаємна кореляція сусідніх фрагментів:
   ```
   R(k) = ∑_{n=0}^{N-1} x[n] · x[n + k]
   ```
2. **Зсув на період:** Оптимальна точка вирізання або вставки зміщується рівно на ціле число періодів основного тону `k_opt = argmax R(k)`.
3. **Віконне згладжування (Cross-Fading):** Зони стикування плавно перемножуються на спадне та висхідне вікно Ганнінга `w[n] = 0.5 · (1 - cos(π n / L))`:
   ```
   y[n] = x_1[n] · (1 - w[n]) + x_2[n] · w[n]
   ```
Завдяки цьому фазова узгодженість гармонік голосу повністю зберігається, і звуковий потік скорочується на 20 мс без виникнення клацань або спотворення тембру мовця.

---

### Маскування втрат пакетів (Packet Loss Concealment, PLC)

Коли буфер відтворення виявляє виснаження (`pop_frame()` повертає порожній результат), звуковий конвеєр викликає модуль PLC.

```
       Стратегії маскування втрат при буферному виснаженні
─────────────────────────────────────────────────────────────────────────────
  Метод                Складність    Якість    Акустичний ефект
─────────────────────────────────────────────────────────────────────────────
  Silence Insertion    Мінімальна    Низька    Провали в звуці, відчуття обриву
  Zero-Order Hold      Мінімальна    Низька    Металевий гул, клацання на стиках
  Waveform Repeat      Середня       Середня   Природне згасання звуку
  Pitch-Sync Decay     Висока        Висока    Повна непомітність випадіння
─────────────────────────────────────────────────────────────────────────────
```

У професійних VoIP-системах (наприклад, рекомендація ITU-T G.711 Appendix I) реалізується експоненційне згасання з повторенням останнього періоду основного тону:
- Перші 10 мс втраченого кадру синтезуються точним повторенням попередньої хвилі;
- Протягом наступних 10–30 мс амплітуда сигналу лінійно спадає до нуля з коефіцієнтом згасання `0.8` на кадр;
- Якщо пакетів немає понад 60 мс, вмикається генератор комфортного шуму (Comfort Noise Generation, CNG), щоб слухач не сприйняв паузу як розрив телефонного з'єднання.

---

### Організація пам'яті та багатопоточність

У високонавантажених серверах голосових конференцій (наприклад, WebRTC SFU або FreeSWITCH) на одному вузлі одночасно працюють тисячі буферів джитеру.

1. **Нульове динамічне виділення пам'яті (Zero Heap Allocation):**
   Усі структури даних та масиви семплів виділяються заздалегідь під час ініціалізації сесії. Операції `push_packet` та `pop_frame` працюють виключно з фіксованими слотами кільцевого буфера, що унеможливлює фрагментацію купи та затримки від збирача сміття або блокувань `malloc`.
2. **Lock-Free синхронізація Single-Producer Single-Consumer (SPSC):**
   Оскільки запис здійснює лише мережевий потік, а читання — виключно звуковий потік, для індексації слотів застосовуються атомарні змінні `std::atomic<uint16_t>` з семантикою `memory_order_release` / `memory_order_acquire`. Це повністю позбавляє критичну секцію аудіовідтворення від м'ютексів (`std::mutex`), гарантуючи виконання звукового колбеку за субмікросекундний час.
