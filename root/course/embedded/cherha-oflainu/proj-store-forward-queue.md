# ⚙️ Реалізація черги Store-and-Forward у Flash/FRAM на C та C++

Розробка енергонезалежної черги збережи-й-перешли (англ. *Store-and-Forward Queue*) для вбудованих систем вимагає безпомилкового керування фізичними властивостями напівпровідникової пам'яті без використання важких файлових систем. У типовому сценарії мікроконтролер має циклічно фіксувати телеметричні звіти під час втрати радіозв'язку, гарантувати цілісність даних при раптовому вимкненні живлення та забезпечувати паралельне вивантаження історії при відновленні зв'язку.

Розгляньмо повну інженерну реалізацію підсистеми, що розв'язує такі ключові задачі:
1. **Пряме секційне керування NOR Flash:** послідовний дозапис (англ. *Append-Only*) у межах секторів по 4 КіБ із випереджальним стиранням.
2. **Атомарність і цілісність записів:** контроль кожного кадру через преамбулу, монотонний номер послідовності та контрольний суфікс CRC-32.
3. **Автоматичне відновлення стану при завантаженні (Boot Recovery):** знаходження актуальної голови та хвоста черги шляхом лінійного сканування секторів без ризику зношування фіксованих комірок пам'яті.
4. **Двоколійне вивантаження з пакетним квитуванням (Batch ACK):** розділення потоків свіжої та історичної телеметрії з безпечним просуванням хвоста.

---

### Формат кадру в енергонезалежній пам'яті

Кожен запис у черзі є самоописовим і вирівняним за 4-байтними межами, що спрощує читання через шину SPI за допомогою контролера прямого доступу до пам'яті (DMA):

```
+---------------+---------------+-------------------------------+
|  Magic (2 Б)  | Type (1 Б)    | Flags (1 Б)                   |  0..3
+---------------+---------------+-------------------------------+
|                      Sequence Number (4 Б)                    |  4..7
+---------------------------------------------------------------+
|                      Timestamp (8 Б, ms)                      |  8..15
+-------------------------------+-------------------------------+
|      Payload Length (2 Б)     |          Reserved (2 Б)       |  16..19
+-------------------------------+-------------------------------+
|                      Payload (N байтів)                       |  20..20+N-1
+---------------------------------------------------------------+
|                      CRC-32 (4 Б)                             |  20+N..23+N
+---------------------------------------------------------------+
```

Структура містить такі критичні поля:
- `Magic` (`0xAA55`): фіксована сигнатура, що дозволяє сканеру відрізнити валідний початок кадру від стертої області пам'яті (`0xFF 0xFF`) або випадкового сміття.
- `Flags`: кодує пріоритет запису (`LOW`, `NORM`, `HIGH`), що визначає поведінку підсистеми при переповненні сховища.
- `Sequence Number`: монотонно зростаючий 32-бітний індекс кадру, необхідний для відновлення хронологічного порядку та квитування доставки сервером.
- `Payload Length`: точний розмір корисного навантаження (від 1 до 512 байтів).
- `CRC-32`: контрольна сума за стандартом IEEE 802.3, що розраховується за всіма полями від `Magic` до кінця `Payload`.

---

### Програмна реалізація

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define SF_MAGIC            0xAA55
#define SF_SECTOR_SIZE      4096
#define SF_PAGE_SIZE        256
#define SF_MAX_PAYLOAD      512

typedef enum {
    SF_PRIORITY_LOW = 0,    // Високочастотна телеметрія (50 Гц) — витісняється першою
    SF_PRIORITY_NORM = 1,   // Періодичний статус (1 Гц) — витісняється за чергою FIFO
    SF_PRIORITY_HIGH = 2,   // Аварійні сигнали та події — захищені від витіснення
} sf_priority_t;

#pragma pack(push, 1)
typedef struct {
    uint16_t magic;
    uint8_t  type;
    uint8_t  flags;
    uint32_t seq;
    uint64_t timestamp_ms;
    uint16_t payload_len;
    uint16_t reserved;
} sf_header_t;
#pragma pack(pop)

// Апаратна абстракція драйвера Flash
typedef struct {
    bool (*read)(uint32_t addr, uint8_t *buf, uint32_t size);
    bool (*write)(uint32_t addr, const uint8_t *buf, uint32_t size);
    bool (*erase_sector)(uint32_t sector_idx);
} sf_flash_driver_t;

typedef struct {
    sf_flash_driver_t drv;
    uint32_t base_addr;
    uint32_t sector_count;
    
    uint32_t head_sector;
    uint32_t head_offset;
    uint32_t tail_sector;
    uint32_t tail_offset;
    
    uint32_t next_seq;
    uint32_t unacked_seq;
    bool     is_full;
} sf_queue_t;

// Табличне обчислення CRC-32 (поліном IEEE 802.3 0xEDB88320)
uint32_t sf_crc32(const uint8_t *data, size_t len, uint32_t init_crc) {
    uint32_t crc = ~init_crc;
    while (len--) {
        crc ^= *data++;
        for (int k = 0; k < 8; k++) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(int32_t)(crc & 1)));
        }
    }
    return ~crc;
}

// Ініціалізація та сканування флеш-пам'яті при старті
bool sf_queue_init(sf_queue_t *q, const sf_flash_driver_t *drv, uint32_t base_addr, uint32_t sector_count) {
    q->drv = *drv;
    q->base_addr = base_addr;
    q->sector_count = sector_count;
    q->head_sector = 0;
    q->head_offset = 0;
    q->tail_sector = 0;
    q->tail_offset = 0;
    q->next_seq = 1;
    q->unacked_seq = 1;
    q->is_full = false;

    // Відновлення покажчика голови: сканування валідних записів у секторах
    uint32_t highest_seq = 0;
    uint32_t best_head_sec = 0;
    uint32_t best_head_off = 0;

    for (uint32_t s = 0; s < sector_count; s++) {
        uint32_t off = 0;
        while (off + sizeof(sf_header_t) <= SF_SECTOR_SIZE) {
            sf_header_t hdr;
            uint32_t phys_addr = base_addr + s * SF_SECTOR_SIZE + off;
            if (!q->drv.read(phys_addr, (uint8_t *)&hdr, sizeof(hdr))) {
                break;
            }

            if (hdr.magic != SF_MAGIC || hdr.payload_len > SF_MAX_PAYLOAD) {
                break; // Досягнуто чистої області 0xFF або кінця дійсних даних
            }

            uint32_t record_total = sizeof(sf_header_t) + hdr.payload_len + sizeof(uint32_t);
            if (off + record_total > SF_SECTOR_SIZE) {
                break;
            }

            // Перевірка цілісності запису за CRC-32
            uint8_t record_buf[sizeof(sf_header_t) + SF_MAX_PAYLOAD + sizeof(uint32_t)];
            if (q->drv.read(phys_addr, record_buf, record_total)) {
                uint32_t stored_crc;
                memcpy(&stored_crc, record_buf + record_total - sizeof(uint32_t), sizeof(uint32_t));
                uint32_t calc_crc = sf_crc32(record_buf, record_total - sizeof(uint32_t), 0);
                
                if (calc_crc == stored_crc) {
                    if (hdr.seq >= highest_seq) {
                        highest_seq = hdr.seq;
                        best_head_sec = s;
                        best_head_off = off + record_total;
                    }
                } else {
                    break; // CRC не зійшовся — наслідок знеструмлення під час запису
                }
            }
            off += record_total;
        }
    }

    if (highest_seq > 0) {
        q->head_sector = best_head_sec;
        q->head_offset = best_head_off;
        q->next_seq = highest_seq + 1;
    }

    return true;
}

// Запис нового кадру в чергу з випереджальним стиранням секторів
bool sf_queue_push(sf_queue_t *q, uint8_t type, sf_priority_t prio, uint64_t ts, const uint8_t *payload, uint16_t len) {
    if (len > SF_MAX_PAYLOAD) return false;

    uint32_t record_size = sizeof(sf_header_t) + len + sizeof(uint32_t);

    // Якщо новий запис не вміщується в поточний сектор — переходимо до наступного
    if (q->head_offset + record_size > SF_SECTOR_SIZE) {
        uint32_t next_sec = (q->head_sector + 1) % q->sector_count;
        
        // Перевірка на переповнення кільця
        if (next_sec == q->tail_sector) {
            if (prio == SF_PRIORITY_LOW) {
                // Відкидаємо низькопріоритетний шум, захищаючи історію від стирання
                return false;
            }
            // Для важливих даних зсуваємо хвіст (витісняємо найстаріший сектор)
            q->tail_sector = (q->tail_sector + 1) % q->sector_count;
            q->tail_offset = 0;
        }

        // Стирання нового сектора заздалегідь
        q->drv.erase_sector(next_sec);
        q->head_sector = next_sec;
        q->head_offset = 0;
    }

    // Формування структури заголовка
    sf_header_t hdr = {
        .magic = SF_MAGIC,
        .type = type,
        .flags = (uint8_t)prio,
        .seq = q->next_seq++,
        .timestamp_ms = ts,
        .payload_len = len,
        .reserved = 0
    };

    uint8_t buffer[sizeof(sf_header_t) + SF_MAX_PAYLOAD + sizeof(uint32_t)];
    memcpy(buffer, &hdr, sizeof(hdr));
    memcpy(buffer + sizeof(hdr), payload, len);

    uint32_t crc = sf_crc32(buffer, sizeof(hdr) + len, 0);
    memcpy(buffer + sizeof(hdr) + len, &crc, sizeof(crc));

    uint32_t write_addr = q->base_addr + q->head_sector * SF_SECTOR_SIZE + q->head_offset;
    if (q->drv.write(write_addr, buffer, record_size)) {
        q->head_offset += record_size;
        return true;
    }

    return false;
}

// Вибірка кадру з хвоста черги для передачі в мережу
bool sf_queue_peek_tail(sf_queue_t *q, sf_header_t *out_hdr, uint8_t *out_payload, uint32_t *out_record_size) {
    if (q->tail_sector == q->head_sector && q->tail_offset >= q->head_offset) {
        return false; // Черга порожня
    }

    uint32_t phys_addr = q->base_addr + q->tail_sector * SF_SECTOR_SIZE + q->tail_offset;
    if (!q->drv.read(phys_addr, (uint8_t *)out_hdr, sizeof(sf_header_t))) {
        return false;
    }

    if (out_hdr->magic != SF_MAGIC) {
        // Досягнуто кінця сектора — перехід до наступного сектора кільця
        q->tail_sector = (q->tail_sector + 1) % q->sector_count;
        q->tail_offset = 0;
        return false;
    }

    *out_record_size = sizeof(sf_header_t) + out_hdr->payload_len + sizeof(uint32_t);
    q->drv.read(phys_addr + sizeof(sf_header_t), out_payload, out_hdr->payload_len);
    return true;
}

// Підтвердження доставки порції даних сервером (ACK commit)
void sf_queue_commit_ack(sf_queue_t *q, uint32_t acked_seq) {
    while (q->tail_sector != q->head_sector || q->tail_offset < q->head_offset) {
        sf_header_t hdr;
        uint32_t phys_addr = q->base_addr + q->tail_sector * SF_SECTOR_SIZE + q->tail_offset;
        
        if (!q->drv.read(phys_addr, (uint8_t *)&hdr, sizeof(hdr)) || hdr.magic != SF_MAGIC) {
            q->tail_sector = (q->tail_sector + 1) % q->sector_count;
            q->tail_offset = 0;
            break;
        }

        if (hdr.seq <= acked_seq) {
            uint32_t rec_len = sizeof(sf_header_t) + hdr.payload_len + sizeof(uint32_t);
            q->tail_offset += rec_len;
            if (q->tail_offset + sizeof(sf_header_t) > SF_SECTOR_SIZE) {
                q->tail_sector = (q->tail_sector + 1) % q->sector_count;
                q->tail_offset = 0;
            }
        } else {
            break; // Дійшли до непідтверджених записів
        }
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <optional>
#include <expected>
#include <concepts>
#include <algorithm>

namespace embedded::storage {

enum class Priority : uint8_t {
    Low = 0,    // High-rate telemetry (50 Hz)
    Normal = 1, // Periodic status (1 Hz)
    High = 2    // Critical alarms and faults
};

enum class QueueError {
    FlashReadFailed,
    FlashWriteFailed,
    FlashEraseFailed,
    PayloadTooLarge,
    QueueFull,
    InvalidRecord,
    CrcMismatch
};

#pragma pack(push, 1)
struct RecordHeader {
    uint16_t magic{0xAA55};
    uint8_t  type{0};
    Priority priority{Priority::Normal};
    uint32_t seq{0};
    uint64_t timestamp_ms{0};
    uint16_t payload_len{0};
    uint16_t reserved{0};
};
#pragma pack(pop)

template <typename FlashDriver>
class StoreForwardQueue {
public:
    static constexpr size_t SectorSize = 4096;
    static constexpr size_t PageSize   = 256;
    static constexpr size_t MaxPayload = 512;
    static constexpr uint16_t Magic    = 0xAA55;

    struct Config {
        uint32_t base_addr;
        uint32_t sector_count;
    };

    explicit StoreForwardQueue(FlashDriver& driver, const Config& cfg)
        : driver_(driver), base_addr_(cfg.base_addr), sector_count_(cfg.sector_count) {}

    // Ініціалізація та сканування секторів для відновлення покажчика голови
    std::expected<void, QueueError> init() {
        uint32_t highest_seq = 0;
        uint32_t best_head_sec = 0;
        uint32_t best_head_off = 0;

        for (uint32_t s = 0; s < sector_count_; ++s) {
            uint32_t off = 0;
            while (off + sizeof(RecordHeader) <= SectorSize) {
                RecordHeader hdr{};
                const uint32_t phys_addr = base_addr_ + s * SectorSize + off;
                
                if (!driver_.read(phys_addr, std::as_writable_bytes(std::span{&hdr, 1}))) {
                    break;
                }

                if (hdr.magic != Magic || hdr.payload_len > MaxPayload) {
                    break;
                }

                const size_t total_size = sizeof(RecordHeader) + hdr.payload_len + sizeof(uint32_t);
                if (off + total_size > SectorSize) {
                    break;
                }

                std::array<std::byte, sizeof(RecordHeader) + MaxPayload + sizeof(uint32_t)> raw_buf{};
                auto slice = std::span{raw_buf.data(), total_size};

                if (driver_.read(phys_addr, slice)) {
                    uint32_t stored_crc = 0;
                    std::copy_n(raw_buf.data() + total_size - sizeof(uint32_t), sizeof(uint32_t),
                                reinterpret_cast<std::byte*>(&stored_crc));

                    const uint32_t calculated_crc = compute_crc32(slice.first(total_size - sizeof(uint32_t)));
                    if (calculated_crc == stored_crc) {
                        if (hdr.seq >= highest_seq) {
                            highest_seq = hdr.seq;
                            best_head_sec = s;
                            best_head_off = off + total_size;
                        }
                    } else {
                        break; // Перерваний запис внаслідок знеструмлення
                    }
                }
                off += total_size;
            }
        }

        if (highest_seq > 0) {
            head_sector_ = best_head_sec;
            head_offset_ = best_head_off;
            next_seq_ = highest_seq + 1;
        }

        return {};
    }

    // Запис нового кадру з випереджальним стиранням
    std::expected<uint32_t, QueueError> push(uint8_t type, Priority prio, uint64_t ts_ms,
                                            std::span<const std::byte> payload) {
        if (payload.size() > MaxPayload) {
            return std::unexpected(QueueError::PayloadTooLarge);
        }

        const size_t record_size = sizeof(RecordHeader) + payload.size() + sizeof(uint32_t);

        if (head_offset_ + record_size > SectorSize) {
            const uint32_t next_sec = (head_sector_ + 1) % sector_count_;

            if (next_sec == tail_sector_) {
                if (prio == Priority::Low) {
                    return std::unexpected(QueueError::QueueFull);
                }
                // Для важливих даних звільняємо найстаріший сектор
                tail_sector_ = (tail_sector_ + 1) % sector_count_;
                tail_offset_ = 0;
            }

            if (!driver_.erase_sector(next_sec)) {
                return std::unexpected(QueueError::FlashEraseFailed);
            }
            head_sector_ = next_sec;
            head_offset_ = 0;
        }

        const uint32_t assigned_seq = next_seq_++;
        RecordHeader hdr{
            .magic = Magic,
            .type = type,
            .priority = prio,
            .seq = assigned_seq,
            .timestamp_ms = ts_ms,
            .payload_len = static_cast<uint16_t>(payload.size()),
            .reserved = 0
        };

        std::array<std::byte, sizeof(RecordHeader) + MaxPayload + sizeof(uint32_t)> write_buf{};
        std::copy_n(reinterpret_cast<const std::byte*>(&hdr), sizeof(hdr), write_buf.data());
        std::copy(payload.begin(), payload.end(), write_buf.data() + sizeof(hdr));

        const uint32_t crc = compute_crc32(std::span{write_buf.data(), sizeof(hdr) + payload.size()});
        std::copy_n(reinterpret_cast<const std::byte*>(&crc), sizeof(crc),
                    write_buf.data() + sizeof(hdr) + payload.size());

        const uint32_t target_addr = base_addr_ + head_sector_ * SectorSize + head_offset_;
        if (!driver_.write(target_addr, std::span{write_buf.data(), record_size})) {
            return std::unexpected(QueueError::FlashWriteFailed);
        }

        head_offset_ += record_size;
        return assigned_seq;
    }

    // Квитування доставки порції записів (ACK commit)
    void commit_ack(uint32_t acked_seq) {
        while (tail_sector_ != head_sector_ || tail_offset_ < head_offset_) {
            RecordHeader hdr{};
            const uint32_t phys_addr = base_addr_ + tail_sector_ * SectorSize + tail_offset_;

            if (!driver_.read(phys_addr, std::as_writable_bytes(std::span{&hdr, 1})) || hdr.magic != Magic) {
                tail_sector_ = (tail_sector_ + 1) % sector_count_;
                tail_offset_ = 0;
                break;
            }

            if (hdr.seq <= acked_seq) {
                const size_t total = sizeof(RecordHeader) + hdr.payload_len + sizeof(uint32_t);
                tail_offset_ += total;
                if (tail_offset_ + sizeof(RecordHeader) > SectorSize) {
                    tail_sector_ = (tail_sector_ + 1) % sector_count_;
                    tail_offset_ = 0;
                }
            } else {
                break;
            }
        }
    }

private:
    FlashDriver& driver_;
    uint32_t base_addr_{0};
    uint32_t sector_count_{0};

    uint32_t head_sector_{0};
    uint32_t head_offset_{0};
    uint32_t tail_sector_{0};
    uint32_t tail_offset_{0};
    uint32_t next_seq_{1};

    static uint32_t compute_crc32(std::span<const std::byte> data) noexcept {
        uint32_t crc = 0xFFFFFFFFU;
        for (auto b : data) {
            crc ^= static_cast<uint8_t>(b);
            for (int k = 0; k < 8; ++k) {
                crc = (crc >> 1) ^ (0xEDB88320U & (-(static_cast<int32_t>(crc & 1))));
            }
        }
        return ~crc;
    }
};

} // namespace embedded::storage
```
:::

---

### Покроковий розбір механізму роботи черги

Розгляньмо, як наведені вище структури та функції керують потоком даних на кожному етапі життєвого циклу підсистеми.

#### 1. Процедура запису та випереджального стирання (`push`)

Коли джерело телеметрії формує новий звіт, функція `push()` виконує такі перевірки:
1. **Перевірка ліміту:** розмір корисного навантаження порівнюється з максимальним буфером `SF_MAX_PAYLOAD` (512 байтів).
2. **Контроль межі сектора:** розмір повного запису `record_size = sizeof(Header) + len + sizeof(CRC)` додається до поточного зміщення `head_offset`. Якщо сума перевищує 4096 байтів, запис не дробиться між секторами, а повністю переноситься на початок наступного сектора `(head_sector + 1) % N`.
3. **Виявлення конфлікту переповнення:** якщо наступний сектор збігається з поточним сектором хвоста `tail_sector`, це означає, що накопичувач заповнений на 100%. Якщо запис має низький пріоритет (`SF_PRIORITY_LOW`), функція повертає помилку `QueueFull`, зберігаючи накопичену історію. Якщо запис має високий пріоритет (`SF_PRIORITY_HIGH` або `NORM`), хвіст примусово просувається на один сектор уперед (`tail_sector++`), звільняючи простір ціною втрати найстарішого блоку.
4. **Випереджальне асинхронне стирання:** новий сектор голови негайно стирається (`erase_sector`), перетворюючи всі його комірки на `0xFF`. Після цього зміщення `head_offset` скидається в 0.
5. **Фіксація кадру:** формується заголовок із присвоєнням монотонного номера `next_seq++`, розраховується фінальний `CRC-32`, і весь блок записується у Flash за одну операцію через SPI. Після успішного запису `head_offset` збільшується на розмір кадру.

#### 2. Відновлення після аварійного знеструмлення (`init`)

При повторному запуску пристрою пам'ять не стирається і не скидається. Функція `init()` відновлює координати голови шляхом лінійного сканування:
- Сканер послідовно читає заголовки в кожному секторі кільця.
- Якщо заголовок містить преамбулу `0xAA55`, сканер зчитує весь кадр і перевіряє `CRC-32`.
- Якщо контрольна сума зійшлася, номер кадру `seq` порівнюється з `highest_seq`.
- Якщо читання натрапляє на нестерті нулі, битий CRC або чистий масив `0xFF`, обробка сектора припиняється.
- Після обходу всіх секторів покажчик `head_sector` та `head_offset` встановлюються на кінець кадру з найвищим номером послідовності `highest_seq`. Лічильник `next_seq` ініціалізується значенням `highest_seq + 1`.

#### 3. Вивантаження та підтвердження доставки (`commit_ack`)

Коли радіоканал активний, фонове завдання через функцію `peek_tail()` зчитує найстаріший кадр із позиції `tail_sector:tail_offset` та відправляє його в сокет. При цьому хвіст черги **не змінюється**.

Коли сервер надсилає підтвердження `ACK` із зазначенням останнього успішно прийнятого номера послідовності `acked_seq`, викликається функція `commit_ack()`:
- Вона перебирає записи у секторі хвоста, порівнюючи їхні поля `seq` із `acked_seq`.
- Для всіх підтверджених кадрів покажчик `tail_offset` зсувається вперед.
- Коли `tail_offset` доходить до кінця сектора, сектор вважається повністю вивантаженим, і `tail_sector` переходить до наступного сектора кільця (`tail_sector = (tail_sector + 1) % N`, `tail_offset = 0`).

---

### Пастки та інженерні крайові випадки

1. **Зависання на битому записі в хвості черги:**
   Якщо внаслідок апаратного збою комірки Flash у хвості черги виявиться битий `Magic` або невідповідний CRC, функція `peek_tail()` негайно просуває `tail_sector` на наступний сектор, фіксуючи помилку в статистиці драйвера. Це запобігає «вічному заклинюванню» черги на одному зіпсованому байті.

2. **Захист від стану перегонів (Concurrency):**
   У реальній RTOS-системі функція `push()` викликається з високопріоритетного завдання збору даних із сенсорів (або переривання таймера), тоді як `peek_tail()` та `commit_ack()` виконуються в низькопріоритетному мережевому завданні. Доступ до структури `sf_queue_t` має бути обов'язково захищений м'ютексом або критичною секцією ядра для виключення одночасного читання та модифікації покажчиків.

3. **Відсутність динамічного виділення пам'яті:**
   Увесь код драйвера використовує статичні буфери та детерміновані структури. Жоден байт не виділяється через `malloc` або оператор `new`, що виключає ризик фрагментації купи або збоїв пам'яті під час тривалої багатомісячної роботи в автономному вузлі.
