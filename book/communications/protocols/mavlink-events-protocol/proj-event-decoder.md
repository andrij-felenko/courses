# ⚙️ Реалізація декодера подій MAVLink та автомата відновлення пропусків

У розподілених безпілотних комплексах надійність доставки діагностичних сповіщень є критичним фактором безпеки польотів. Коли автопілот фіксує відмову сенсора або зміну режиму навігації, подія повинна бути гарантовано доставлена до наземної станції керування (QGroundControl, MAVSDK) або бортового супутнього комп'ютера (Companion Computer) навіть за умов 20% втрат пакетів у зашумленому радіоканалі.

Для реалізації цієї вимоги розробляється спеціалізований програмний рушій, що складається з двох взаємопов'язаних компонентів: бортового кільцевого буфера автопілота (Autopilot Ring Buffer), який зберігає історію останніх подій у статичній оперативній пам'яті, та клієнтського автомата виявлення пропусків і декодування (GCS Event Decoder Engine), який відстежує послідовність номерів, надсилає вибіркові запити на повторну передачу та перетворює двійкові аргументи у зрозумілий інтерфейс пілота.

---

### Архітектура та вимоги до бортового кільцевого буфера

У вбудованих операційних системах реального часу (RTOS, таких як NuttX або FreeRTOS), на яких працюють сучасні польотні контролери, динамічне виділення оперативної пам'яті (функції `malloc` або оператор `new`) під час польоту суворо заборонено. Спроба виділити пам'ять у контексті переривання або високопріоритетного навігаційного циклу з частотою 400 Гц може призвести до фрагментації купи (Heap Fragmentation) та непередбачуваної затримки виконання (Unbounded Execution Latency), що загрожує втратою стабілізації апарата.

З цієї причини кільцевий буфер подій автопілота проектується як статичний масив фіксованого розміру `EVENT_BUFFER_SIZE` (зазвичай від 32 до 64 записів). Буфер підтримує два вказівники стану: монотонно зростаючий номер наступного запису `head_sequence` та номер найстарішого збереженого кадру `oldest_sequence`. 

Коли кількість згенерованих подій перевищує місткість масиву, буфер починає циклічний перезапис найстаріших елементів. При цьому автопілот виставляє прапорець `has_wrapped`, що сигналізує про витіснення застарілих даних. Якщо наземна станція надсилає команду `REQUEST_EVENT` на відновлення номера, який уже був перетертий новими записами, автопілот коректно відхиляє запит і повідомляє станцію про переповнення буфера через бітовий прапорець `OVERFLOW` у повідомленні `CURRENT_EVENT_SEQUENCE`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define EVENT_BUFFER_SIZE 32 // Кількість збережених подій у пам'яті RAM

// Структура збереженого кадру події в оперативній пам'яті автопілота
typedef struct {
    uint32_t id;                    // 32-бітний хеш події (event_id)
    uint32_t time_boot_ms;          // Часова мітка від старту процесора (мс)
    uint16_t sequence;              // Порядковий номер у черзі
    uint8_t  destination_component; // Цільовий компонент (0 = broadcast)
    uint8_t  destination_system;    // Цільова система (0 = broadcast)
    uint8_t  log_levels;            // Бітове поле рівнів важливості
    uint8_t  arguments[40];         // Двійковий масив аргументів
    uint8_t  payload_length;        // Фактична довжина корисних даних
} stored_event_t;

// Стан кільцевого буфера подій польотного контролера
typedef struct {
    stored_event_t buffer[EVENT_BUFFER_SIZE];
    uint16_t       head_sequence;   // Номер наступної події для запису
    uint16_t       oldest_sequence; // Номер найстарішої доступної події
    bool           has_wrapped;     // Ознака циклічного заповнення масиву
} autopilot_event_buffer_t;

// Ініціалізація статичного буфера подій
void event_buffer_init(autopilot_event_buffer_t *eb) {
    memset(eb, 0, sizeof(autopilot_event_buffer_t));
    eb->head_sequence = 0;
    eb->oldest_sequence = 0;
    eb->has_wrapped = false;
}

// Додавання нової події до кільцевого буфера
uint16_t event_buffer_push(autopilot_event_buffer_t *eb,
                           uint32_t id,
                           uint32_t time_boot_ms,
                           uint8_t log_levels,
                           const uint8_t *args,
                           uint8_t args_len) {
    uint16_t seq = eb->head_sequence;
    size_t index = seq % EVENT_BUFFER_SIZE;

    stored_event_t *ev = &eb->buffer[index];
    ev->id = id;
    ev->time_boot_ms = time_boot_ms;
    ev->sequence = seq;
    ev->destination_component = 0;
    ev->destination_system = 0;
    ev->log_levels = log_levels;

    size_t copy_bytes = (args_len > 40) ? 40 : args_len;
    memcpy(ev->arguments, args, copy_bytes);
    if (copy_bytes < 40) {
        memset(&ev->arguments[copy_bytes], 0, 40 - copy_bytes);
    }
    ev->payload_length = (uint8_t)(13 + copy_bytes);

    // Оновлення монотонного лічильника та меж доступності
    eb->head_sequence = (uint16_t)((seq + 1) & 0xFFFF);
    if (eb->has_wrapped) {
        eb->oldest_sequence = (uint16_t)((eb->oldest_sequence + 1) & 0xFFFF);
    } else if (eb->head_sequence >= EVENT_BUFFER_SIZE) {
        eb->has_wrapped = true;
        eb->oldest_sequence = 0;
    }

    return seq;
}

// Пошук події за номером послідовності для повторного відправлення
bool event_buffer_get(const autopilot_event_buffer_t *eb,
                      uint16_t sequence,
                      stored_event_t *out_event) {
    uint16_t diff = (uint16_t)(eb->head_sequence - sequence);
    if (diff == 0 || diff > EVENT_BUFFER_SIZE) {
        return false; // Подія ще не настала або вже витіснена з пам'яті
    }

    size_t index = sequence % EVENT_BUFFER_SIZE;
    if (eb->buffer[index].sequence == sequence) {
        memcpy(out_event, &eb->buffer[index], sizeof(stored_event_t));
        return true;
    }
    return false;
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <optional>
#include <cstring>
#include <algorithm>

struct StoredEvent {
    uint32_t                id{0};
    uint32_t                timeBootMs{0};
    uint16_t                sequence{0};
    uint8_t                 destinationComponent{0};
    uint8_t                 destinationSystem{0};
    uint8_t                 logLevels{0};
    std::array<uint8_t, 40> arguments{};
    uint8_t                 payloadLength{0};
};

template <size_t BufferSize = 32>
class AutopilotEventBuffer {
public:
    uint16_t push(uint32_t id,
                  uint32_t timeBootMs,
                  uint8_t logLevels,
                  std::span<const uint8_t> args) noexcept {
        const uint16_t seq = m_headSequence;
        const size_t idx = seq % BufferSize;

        auto& ev = m_buffer[idx];
        ev.id = id;
        ev.timeBootMs = timeBootMs;
        ev.sequence = seq;
        ev.destinationComponent = 0;
        ev.destinationSystem = 0;
        ev.logLevels = logLevels;

        const size_t copyBytes = std::min(args.size(), ev.arguments.size());
        std::memcpy(ev.arguments.data(), args.data(), copyBytes);
        if (copyBytes < ev.arguments.size()) {
            std::memset(ev.arguments.data() + copyBytes, 0, ev.arguments.size() - copyBytes);
        }
        ev.payloadLength = static_cast<uint8_t>(13 + copyBytes);

        m_headSequence = static_cast<uint16_t>((seq + 1) & 0xFFFF);
        if (m_hasWrapped) {
            m_oldestSequence = static_cast<uint16_t>((m_oldestSequence + 1) & 0xFFFF);
        } else if (m_headSequence >= BufferSize) {
            m_hasWrapped = true;
            m_oldestSequence = 0;
        }

        return seq;
    }

    [[nodiscard]] std::optional<StoredEvent> get(uint16_t sequence) const noexcept {
        const uint16_t diff = static_cast<uint16_t>(m_headSequence - sequence);
        if (diff == 0 || diff > BufferSize) {
            return std::nullopt;
        }

        const size_t idx = sequence % BufferSize;
        if (m_buffer[idx].sequence == sequence) {
            return m_buffer[idx];
        }
        return std::nullopt;
    }

    [[nodiscard]] uint16_t headSequence() const noexcept { return m_headSequence; }

private:
    std::array<StoredEvent, BufferSize> m_buffer{};
    uint16_t m_headSequence{0};
    uint16_t m_oldestSequence{0};
    bool     m_hasWrapped{false};
};
```
:::

---

### Механізми безпечного вилучення двійкових аргументів

Двійковий масив `arguments[40]` передає числові параметри події у щільно упакованому вигляді без вирівнювання за межами слів (Packed layout). Наприклад, якщо першим аргументом є 1-байтовий індекс сенсора `uint8_t`, а другим — 4-байтове число з рухомою комою `float`, друге число починається зі зсуву 1.

На 32-бітних мікроконтролерах із процесорними ядрами ARM Cortex-M0 або Cortex-M3 пряме розіменування вказівника на непарну адресу `*(float*)&arguments[1]` генерує апаратний виняток `HardFault` (Unaligned Memory Access Fault). Навіть на новіших процесорах Cortex-M4/M7 та x86 несиметричне читання вимагає додаткових циклів шини пам'яті.

Щоб гарантувати абсолютну апаратну сумісність та безпеку типів, вилучення аргументів виконується через копіювання байтів `memcpy` у мові C або через стандартизований шаблон `std::bit_cast` та допоміжний буфер у мові C++:

:::tabs
```c
#include <stdint.h>
#include <string.h>

// Безпечне вилучення 8-бітного беззнакового цілого
uint8_t unpack_u8(const uint8_t *buf, size_t offset) {
    return buf[offset];
}

// Безпечне вилучення 16-бітного цілого у форматі little-endian
uint16_t unpack_u16_le(const uint8_t *buf, size_t offset) {
    uint16_t val;
    memcpy(&val, &buf[offset], sizeof(uint16_t));
    return val;
}

// Безпечне вилучення 32-бітного цілого у форматі little-endian
uint32_t unpack_u32_le(const uint8_t *buf, size_t offset) {
    uint32_t val;
    memcpy(&val, &buf[offset], sizeof(uint32_t));
    return val;
}

// Безпечне вилучення 32-бітного дробового числа IEEE 754 float
float unpack_f32_le(const uint8_t *buf, size_t offset) {
    float val;
    memcpy(&val, &buf[offset], sizeof(float));
    return val;
}

// Безпечне вилучення 64-бітного цілого у форматі little-endian
uint64_t unpack_u64_le(const uint8_t *buf, size_t offset) {
    uint64_t val;
    memcpy(&val, &buf[offset], sizeof(uint64_t));
    return val;
}
```
```cpp
#include <cstdint>
#include <cstring>
#include <span>
#include <bit>
#include <type_traits>

// Універсальний розпакувальник скалярних типів (C++20)
template <typename T>
T unpackArgLE(std::span<const uint8_t> buf, size_t offset) noexcept {
    static_assert(std::is_trivially_copyable_v<T>, "Тип аргументу має бути тривіально копійованим");
    T val{};
    if (offset + sizeof(T) <= buf.size()) {
        std::memcpy(&val, buf.data() + offset, sizeof(T));
    }
    return val;
}

inline uint8_t unpackU8(std::span<const uint8_t> buf, size_t offset) noexcept {
    return unpackArgLE<uint8_t>(buf, offset);
}

inline uint16_t unpackU16LE(std::span<const uint8_t> buf, size_t offset) noexcept {
    return unpackArgLE<uint16_t>(buf, offset);
}

inline uint32_t unpackU32LE(std::span<const uint8_t> buf, size_t offset) noexcept {
    return unpackArgLE<uint32_t>(buf, offset);
}

inline float unpackF32LE(std::span<const uint8_t> buf, size_t offset) noexcept {
    return unpackArgLE<float>(buf, offset);
}

inline uint64_t unpackU64LE(std::span<const uint8_t> buf, size_t offset) noexcept {
    return unpackArgLE<uint64_t>(buf, offset);
}
```
:::

---

### Клієнтський автомат виявлення пропусків (Gap Recovery Engine)

Автомат наземної станції відстежує послідовність отриманих подій окремо для кожного компонента апарата (`sysid`/`compid`). Логіка роботи автомата будується навколо трьох станів:

1. **Нормальний режим (In-Sync):** Отриманий номер події `received_seq` строго дорівнює очікуваному `expected_sequence`. Подія негайно передається на десеріалізацію та відображення пілоту, а очікуваний номер збільшується на одиницю.
2. **Виявлення прогалини (Gap Detected):** Отримано номер `received_seq > expected_sequence`. Станція фіксує діапазон втрачених кадрів `[expected_sequence .. received_seq - 1]`, надсилає автопілоту команду `REQUEST_EVENT` та запускає таймер очікування повторної передачі (зазвичай 800 мс).
3. **Обробка тайм-ауту та повтор (Retry / Drop):** Якщо протягом встановленого інтервалу відповідь не надійшла, станція повторює запит (до трьох спроб). Якщо ліміт спроб вичерпано, пропущені події вважаються безповоротно втраченими в ефірі, лічильник `expected_sequence` примусово просувається вперед, а оператор отримує попередження про втрату фрагмента журналу.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

#define ARQ_MAX_RETRIES     3
#define ARQ_TIMEOUT_MS      800

typedef struct {
    uint16_t expected_sequence;
    bool     is_initialized;
    bool     gap_active;
    uint16_t gap_first_seq;
    uint16_t gap_last_seq;
    uint32_t last_request_time_ms;
    uint8_t  retry_count;
} event_gap_tracker_t;

void gap_tracker_init(event_gap_tracker_t *tracker) {
    memset(tracker, 0, sizeof(event_gap_tracker_t));
}

// Обробка номера послідовності з вхідного EVENT або CURRENT_EVENT_SEQUENCE
void gap_tracker_on_sequence(event_gap_tracker_t *tracker,
                             uint16_t received_seq,
                             uint32_t current_time_ms,
                             uint8_t sys_id,
                             uint8_t comp_id) {
    if (!tracker->is_initialized) {
        tracker->expected_sequence = (uint16_t)((received_seq + 1) & 0xFFFF);
        tracker->is_initialized = true;
        return;
    }

    if (received_seq == tracker->expected_sequence) {
        tracker->expected_sequence = (uint16_t)((tracker->expected_sequence + 1) & 0xFFFF);
        if (tracker->gap_active && tracker->expected_sequence > tracker->gap_last_seq) {
            tracker->gap_active = false;
            tracker->retry_count = 0;
        }
    } else {
        uint16_t diff = (uint16_t)(received_seq - tracker->expected_sequence);
        if (diff < 32768) {
            tracker->gap_active = true;
            tracker->gap_first_seq = tracker->expected_sequence;
            tracker->gap_last_seq = (uint16_t)((received_seq - 1) & 0xFFFF);
            tracker->last_request_time_ms = current_time_ms;
            tracker->retry_count = 1;

            printf("[ARQ] Gap detected: missing %u..%u. Sending REQUEST_EVENT (sys=%u comp=%u)\n",
                   tracker->gap_first_seq, tracker->gap_last_seq, sys_id, comp_id);
        }
    }
}

// Періодичне оновлення стану та повтор запитів за тайм-аутом
void gap_tracker_poll(event_gap_tracker_t *tracker,
                      uint32_t current_time_ms,
                      uint8_t sys_id,
                      uint8_t comp_id) {
    if (!tracker->gap_active) {
        return;
    }

    if (current_time_ms - tracker->last_request_time_ms >= ARQ_TIMEOUT_MS) {
        if (tracker->retry_count < ARQ_MAX_RETRIES) {
            tracker->retry_count++;
            tracker->last_request_time_ms = current_time_ms;
            printf("[ARQ] Retry %u/%u for missing %u..%u\n",
                   tracker->retry_count, ARQ_MAX_RETRIES,
                   tracker->gap_first_seq, tracker->gap_last_seq);
        } else {
            printf("[ARQ] Gap %u..%u permanently lost after %u retries.\n",
                   tracker->gap_first_seq, tracker->gap_last_seq, ARQ_MAX_RETRIES);
            tracker->expected_sequence = (uint16_t)((tracker->gap_last_seq + 1) & 0xFFFF);
            tracker->gap_active = false;
            tracker->retry_count = 0;
        }
    }
}
```
```cpp
#include <cstdint>
#include <iostream>
#include <optional>

class EventGapTracker {
public:
    static constexpr uint8_t  MaxRetries = 3;
    static constexpr uint32_t TimeoutMs  = 800;

    void onSequenceReceived(uint16_t receivedSeq,
                            uint32_t currentTimeMs,
                            uint8_t sysId,
                            uint8_t compId) {
        if (!m_initialized) {
            m_expectedSequence = static_cast<uint16_t>((receivedSeq + 1) & 0xFFFF);
            m_initialized = true;
            return;
        }

        if (receivedSeq == m_expectedSequence) {
            m_expectedSequence = static_cast<uint16_t>((m_expectedSequence + 1) & 0xFFFF);
            if (m_gapActive && m_expectedSequence > m_gapLastSeq) {
                m_gapActive = false;
                m_retryCount = 0;
            }
        } else {
            const uint16_t diff = static_cast<uint16_t>(receivedSeq - m_expectedSequence);
            if (diff < 32768) {
                m_gapActive = true;
                m_gapFirstSeq = m_expectedSequence;
                m_gapLastSeq = static_cast<uint16_t>((receivedSeq - 1) & 0xFFFF);
                m_lastRequestTimeMs = currentTimeMs;
                m_retryCount = 1;

                sendRequestEvent(sysId, compId, m_gapFirstSeq, m_gapLastSeq);
            }
        }
    }

    void poll(uint32_t currentTimeMs, uint8_t sysId, uint8_t compId) {
        if (!m_gapActive) {
            return;
        }

        if (currentTimeMs - m_lastRequestTimeMs >= TimeoutMs) {
            if (m_retryCount < MaxRetries) {
                ++m_retryCount;
                m_lastRequestTimeMs = currentTimeMs;
                sendRequestEvent(sysId, compId, m_gapFirstSeq, m_gapLastSeq);
            } else {
                std::cerr << "[ARQ] Gap " << m_gapFirstSeq << ".." << m_gapLastSeq
                          << " dropped after max retries!\n";
                m_expectedSequence = static_cast<uint16_t>((m_gapLastSeq + 1) & 0xFFFF);
                m_gapActive = false;
                m_retryCount = 0;
            }
        }
    }

private:
    void sendRequestEvent(uint8_t sys, uint8_t comp, uint16_t firstSeq, uint16_t lastSeq) {
        std::cout << "[ARQ] Requesting events " << firstSeq << ".." << lastSeq
                  << " from sys=" << static_cast<int>(sys)
                  << " comp=" << static_cast<int>(comp) << "\n";
    }

    uint16_t m_expectedSequence{0};
    uint16_t m_gapFirstSeq{0};
    uint16_t m_gapLastSeq{0};
    uint32_t m_lastRequestTimeMs{0};
    uint8_t  m_retryCount{0};
    bool     m_initialized{false};
    bool     m_gapActive{false};
};
```
:::

---

### Декодування та динамічна підстановка аргументів у шаблон

Останнім етапом обробки є інтерполяція значень у текстовий шаблон інтерфейсу. Отримавши двійковий кадр `EVENT`, станція знаходить відповідний запис у словнику метаданих за ключем `event_id`, вилучає числові значення за відомими зсувами та підставляє їх у плейсхолдери шаблону `{1}`, `{2:.1f}`.

:::tabs
```c
#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    uint32_t id;
    uint32_t time_boot_ms;
    uint16_t sequence;
    uint8_t  internal_log_level;
    uint8_t  external_severity;
    char     display_text[256];
    char     action_text[256];
} formatted_event_t;

// Декодування та форматування події збою калібрування компаса (0x8A12B4C0)
bool decode_and_format_event(const uint8_t *raw_payload,
                             size_t payload_len,
                             formatted_event_t *out_event) {
    if (payload_len < 13 + sizeof(uint8_t) + sizeof(float)) {
        return false;
    }

    uint32_t id;
    memcpy(&id, &raw_payload[0], sizeof(uint32_t));
    if (id != 0x8A12B4C0) {
        return false; // Невідомий або інший event_id
    }

    out_event->id = id;
    memcpy(&out_event->time_boot_ms, &raw_payload[4], sizeof(uint32_t));
    memcpy(&out_event->sequence, &raw_payload[8], sizeof(uint16_t));

    uint8_t log_levels = raw_payload[12];
    out_event->internal_log_level = (log_levels >> 4) & 0x0F;
    out_event->external_severity = log_levels & 0x0F;

    const uint8_t *args = &raw_payload[13];
    uint8_t sensor_id = unpack_u8(args, 0);
    float deviation = unpack_f32_le(args, 1);

    // Підстановка аргументів у локалізований рядок українською мовою
    snprintf(out_event->display_text, sizeof(out_event->display_text),
             "Збій калібрування компаса №%u (відхилення: %.1f°)",
             sensor_id, deviation);

    snprintf(out_event->action_text, sizeof(out_event->action_text),
             "Відійдіть на 15 метрів від металевих конструкцій та повторіть процедуру.");

    return true;
}
```
```cpp
#include <cstdint>
#include <string>
#include <format>
#include <optional>
#include <span>

struct FormattedEvent {
    uint32_t    id{0};
    uint32_t    timeBootMs{0};
    uint16_t    sequence{0};
    uint8_t     internalLogLevel{0};
    uint8_t     externalSeverity{0};
    std::string displayText;
    std::string actionText;
};

// Декодування події за допомогою std::span та std::format (C++20)
std::optional<FormattedEvent> decodeAndFormatEvent(std::span<const uint8_t> payload) {
    constexpr size_t MinHeaderAndArgs = 13 + sizeof(uint8_t) + sizeof(float);
    if (payload.size() < MinHeaderAndArgs) {
        return std::nullopt;
    }

    const uint32_t id = unpackArgLE<uint32_t>(payload, 0);
    if (id != 0x8A12B4C0) {
        return std::nullopt;
    }

    FormattedEvent event{};
    event.id = id;
    event.timeBootMs = unpackArgLE<uint32_t>(payload, 4);
    event.sequence   = unpackArgLE<uint16_t>(payload, 8);

    const uint8_t logLevels = payload[12];
    event.internalLogLevel = (logLevels >> 4) & 0x0F;
    event.externalSeverity = logLevels & 0x0F;

    auto args = payload.subspan(13);
    const uint8_t sensorId  = unpackU8(args, 0);
    const float   deviation = unpackF32LE(args, 1);

    event.displayText = std::format(
        "Збій калібрування компаса №{} (відхилення: {:.1f}°)",
        sensorId, deviation
    );

    event.actionText = "Відійдіть на 15 метрів від металевих конструкцій та повторіть процедуру.";

    return event;
}
```
:::

---

### Інженерні крайові випадки та синхронізація

1. **Модульна арифметика переповнення лічильника (Wrap-Around):** Поле `sequence` є 16-бітним числом (`0..65535`). При переході через нуль звичайна перевірка `received_seq > expected_seq` ламається. Порівняння обов'язково виконується через різницю зведену до беззнакового типу: `(uint16_t)(received_seq - expected_seq) < 32768`.
2. **Переповнення кільцевого буфера при тривалій втраті зв'язку (Buffer Overrun):** Якщо апарат перебував поза зоною прямої видимості протягом хвилини і згенерував понад 32 події, найстаріші записи буде втрачено. Отримавши прапорець `OVERFLOW` у повідомленні `CURRENT_EVENT_SEQUENCE`, станція скидає очікуваний номер на поточний актуальний та відображає оператору статус `[Частину журналу подій втрачено]`.
3. **Захист від блокування інтерфейсу при сплесках подій (Event Storm):** При аварійних сценаріях (відмова шини живлення або каскадний збій сенсорів) черга може отримувати десятки подій за мілісекунду. Автомат декодування зобов'язаний обмежувати швидкість оновлення графічного інтерфейсу (Throttling), групуючи однотипні сповіщення для запобігання зависанню програми оператора.
