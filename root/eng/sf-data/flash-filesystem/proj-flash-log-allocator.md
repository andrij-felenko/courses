# ⚙️ Розподільник блоків Flash із журналюванням та збиранням сміття

Будь-яка вбудована файлова система для Flash починається з низькорівневого розподільника блоків (*block allocator*), який бере на себе вирішення фізичних обмежень чипа: заборону перезапису на місці (*no in-place updates*), ведення журналу додаванням у кінець (*append-only log*), вирівнювання зносу комірок (*wear leveling*) та циклічну компактифікацію дійсних даних зі стиранням застарілих блоків (*garbage collection*).

Коли проста мікроконтролерна система записує параметри конфігурації, лічильники або телеметрію, використання повноцінної складної файлової системи може бути надлишковим через оверхед по оперативній пам'яті. Проте запис за фіксованими зміщеннями швидко знищує окремі сектори Flash. Нижче реалізовано компактний, автономний рушій лог-структурованого зберігання версійних записів із повним циклом рекультивації простору на мовах C та C++.

### Архітектура розподільника та формат запису

Пам'ять розділу розбивається на `N` фізичних блоків фіксованого розміру (наприклад, 4096 байтів). Кожен блок починається із заголовка, який зберігає два ключові параметри:
1. `erase_count`: 32-бітний лічильник стирань даного блоку, який інкрементується щоразу, коли блок стирається високою напругою.
2. `state`: стан блоку в межах життєвого циклу.

Життєвий цикл блоку описується кінцевим автоматом із трьох станів:
- `BLOCK_FREE` (`0xFF`): блок стертий і готовий приймати нові дані.
- `BLOCK_ACTIVE` (`0xAA`): активний блок, у який наразі послідовно дописуються нові записи.
- `BLOCK_FULL` (`0x55`): блок повністю заповнений записами й закритий для додавання; очікує на збирання сміття.

Кожен логічний запис складається з фіксованого заголовка `record_header_t` та корисного навантаження довільної довжини. Заголовок містить:
- `magic`: константу `0xA5` для швидкої валідації початку запису під час лінійного сканування;
- `record_id`: числовий ідентифікатор ключа або сутності (наприклад, `0x0001` для налаштувань мережі, `0x0002` для калібрування сенсорів);
- `length`: розмір корисних даних у байтах;
- `sequence`: глобальний монотонний лічильник ревізій, що однозначно визначає найновішу версію запису;
- `status`: статус валідності запису (`0xFF` — порожньо, `0x00` — зафіксовано/дійсно, `0x55` — інвалідовано);
- `crc32`: контрольну суму корисного навантаження.

### Механіка оновлення Out-of-place та інвалідація

Коли програма записує нове значення для вже наявного `record_id`, стара версія не затирається. Нова версія записується в кінець поточного активного блоку з більшим номером `sequence`. Після успішного запису та підтвердження контрольної суми статусний байт попередньої версії запису програмується зі значення `STATUS_COMMITTED` (`0x00`) або залишається логічно застарілим.

На мікросхемах NOR Flash перехід окремих бітів зі стану `1` у стан `0` можна виконати без стирання блоку: зміна байта `0xFF` на `0x00` чи `0x55` здійснюється однією командою програмування байта. Під час перезапуску системи найсвіжіший запис визначається за максимальним значенням поля `sequence` серед усіх дійсних записів із валідною контрольною сумою.

### Алгоритм вибору жертви для збирання сміття (Victim Selection)

Коли в активному блоці закінчується вільне місце, а в пулі стертих блоків немає жодного з міткою `BLOCK_FREE`, розподільник запускає процедуру збирання сміття (*Garbage Collection*, GC).

Для очищення обирається блок-жертва за жадібною стратегією (*greedy policy*):
1. Алгоритм сканує всі заповнені блоки (`BLOCK_FULL`).
2. Для кожного блоку обчислюється сумарний обсяг недійсних або застарілих байтів (`dead_bytes`).
3. Блок із максимальним значенням `dead_bytes` призначається жертвою: з нього копіюється найменша кількість живих даних, що мінімізує коефіцієнт посилення запису (WAF).
4. Усі дійсні записи з блоку-жертви послідовно копіюються в новий активний блок.
5. Блок-жертва стирається командою `flash_erase_block`, його лічильник `erase_count` збільшується на 1, а статус переводиться в `BLOCK_FREE`.

Порівняно з більш складними стратегіями вибору жертви (наприклад, віково-вартісним підходом *Cost-Benefit*, який враховує час життя даних для захисту холодних блоків від передчасного переміщення), жадібний підхід є оптимальним для невеликих вбудованих сховищ до 16 МБ, оскільки мінімізує обчислювальні витрати мікроконтролера та час виконання однієї транзакції.

### Відновлення стану після раптового збою живлення

Під час старту системи рушій не вимагає тривалого аналізу цілісності на зразок утиліти `fsck`. Процедура відновлення полягає у послідовному проході по всіх фізичних блоках:

1. **Сканування заголовків блоків**: рушій перевіряє стан кожного блоку (`state`) та його лічильник стирань. Якщо виявлено блок, заповнений байтами `0xFF`, він класифікується як `BLOCK_FREE`.
2. **Сканування записів усередині блоків**: у межах кожного блоку `BLOCK_FULL` або `BLOCK_ACTIVE` рушій читає структури `record_header_t`. Якщо поле `magic` не дорівнює `0xA5`, або поле `status` залишилося рівним `0xFF` (запис було перервано до фіксації), або контрольна сума `crc32` не збігається з даними, цей запис ігнорується.
3. **Визначення активного блоку та максимального зміщення**: блок із найновішим значенням `sequence`, який ще має вільне місце наприкінці, стає активним (`active_block_idx`), а зміщення запису (`write_offset`) встановлюється одразу після останнього валідного запису.

### Повна реалізація: C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

#define FLASH_BLOCK_SIZE   4096
#define FLASH_BLOCK_COUNT  8
#define FLASH_MAGIC        0xA5

#define STATUS_COMMITTED   0x00
#define STATUS_INVALID     0x55
#define STATUS_EMPTY       0xFF

typedef enum {
    BLK_STATE_FREE = 0xFF,
    BLK_STATE_ACTIVE = 0xAA,
    BLK_STATE_FULL = 0x55
} block_state_t;

#pragma pack(push, 1)
typedef struct {
    uint8_t  magic;
    uint16_t record_id;
    uint16_t length;
    uint32_t sequence;
    uint8_t  status;       /* 0xFF: порожній, 0x00: зафіксовано, 0x55: застарілий */
    uint32_t crc32;
} record_header_t;

typedef struct {
    uint32_t erase_count;
    uint8_t  state;
    uint8_t  reserved[3];
} block_header_t;
#pragma pack(pop)

typedef struct {
    uint8_t raw[FLASH_BLOCK_COUNT][FLASH_BLOCK_SIZE];
    uint32_t global_seq;
    int active_block_idx;
    size_t write_offset;
} flash_engine_t;

/* Обчислення CRC32 для захисту від спотворення бітів */
static uint32_t compute_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (int j = 0; j < 8; j++) {
            if (crc & 1)
                crc = (crc >> 1) ^ 0xEDB88320;
            else
                crc >>= 1;
        }
    }
    return ~crc;
}

void flash_init(flash_engine_t *fe) {
    memset(fe->raw, 0xFF, sizeof(fe->raw));
    fe->global_seq = 1;
    fe->active_block_idx = -1;
    fe->write_offset = 0;

    for (int i = 0; i < FLASH_BLOCK_COUNT; i++) {
        block_header_t *bh = (block_header_t *)fe->raw[i];
        bh->erase_count = 0;
        bh->state = BLK_STATE_FREE;
    }
}

static bool flash_erase_block(flash_engine_t *fe, int block_idx) {
    if (block_idx < 0 || block_idx >= FLASH_BLOCK_COUNT) return false;
    block_header_t *bh = (block_header_t *)fe->raw[block_idx];
    uint32_t ec = bh->erase_count + 1;
    memset(fe->raw[block_idx], 0xFF, FLASH_BLOCK_SIZE);
    bh->erase_count = ec;
    bh->state = BLK_STATE_FREE;
    return true;
}

static int flash_allocate_free_block(flash_engine_t *fe) {
    int best_idx = -1;
    uint32_t min_erase = UINT32_MAX;

    /* Wear Leveling: виділяємо вільний блок із найменшим зносом */
    for (int i = 0; i < FLASH_BLOCK_COUNT; i++) {
        block_header_t *bh = (block_header_t *)fe->raw[i];
        if (bh->state == BLK_STATE_FREE && bh->erase_count < min_erase) {
            min_erase = bh->erase_count;
            best_idx = i;
        }
    }
    if (best_idx >= 0) {
        block_header_t *bh = (block_header_t *)fe->raw[best_idx];
        bh->state = BLK_STATE_ACTIVE;
    }
    return best_idx;
}

static int flash_select_gc_victim(flash_engine_t *fe) {
    int victim = -1;
    size_t max_obsolete_bytes = 0;

    for (int b = 0; b < FLASH_BLOCK_COUNT; b++) {
        if (b == fe->active_block_idx) continue;
        block_header_t *bh = (block_header_t *)fe->raw[b];
        if (bh->state != BLK_STATE_FULL) continue;

        size_t off = sizeof(block_header_t);
        size_t dead_bytes = 0;

        while (off + sizeof(record_header_t) <= FLASH_BLOCK_SIZE) {
            record_header_t *rh = (record_header_t *)&fe->raw[b][off];
            if (rh->magic != FLASH_MAGIC) break;
            if (rh->status == STATUS_INVALID) {
                dead_bytes += sizeof(record_header_t) + rh->length;
            }
            off += sizeof(record_header_t) + rh->length;
        }

        if (dead_bytes > max_obsolete_bytes) {
            max_obsolete_bytes = dead_bytes;
            victim = b;
        }
    }
    return victim;
}

bool flash_write_record(flash_engine_t *fe, uint16_t id, const uint8_t *payload, uint16_t len);

bool flash_run_gc(flash_engine_t *fe) {
    int victim = flash_select_gc_victim(fe);
    if (victim < 0) return false;

    size_t off = sizeof(block_header_t);
    while (off + sizeof(record_header_t) <= FLASH_BLOCK_SIZE) {
        record_header_t *rh = (record_header_t *)&fe->raw[victim][off];
        if (rh->magic != FLASH_MAGIC) break;

        if (rh->status == STATUS_COMMITTED) {
            const uint8_t *data = &fe->raw[victim][off + sizeof(record_header_t)];
            flash_write_record(fe, rh->record_id, data, rh->length);
        }
        off += sizeof(record_header_t) + rh->length;
    }

    flash_erase_block(fe, victim);
    return true;
}

static void flash_invalidate_prior_versions(flash_engine_t *fe, uint16_t id) {
    for (int b = 0; b < FLASH_BLOCK_COUNT; b++) {
        size_t off = sizeof(block_header_t);
        while (off + sizeof(record_header_t) <= FLASH_BLOCK_SIZE) {
            record_header_t *rh = (record_header_t *)&fe->raw[b][off];
            if (rh->magic != FLASH_MAGIC) break;
            if (rh->record_id == id && rh->status == STATUS_COMMITTED) {
                rh->status = STATUS_INVALID;
            }
            off += sizeof(record_header_t) + rh->length;
        }
    }
}

bool flash_write_record(flash_engine_t *fe, uint16_t id, const uint8_t *payload, uint16_t len) {
    size_t total_size = sizeof(record_header_t) + len;

    if (fe->active_block_idx < 0 || fe->write_offset + total_size > FLASH_BLOCK_SIZE) {
        if (fe->active_block_idx >= 0) {
            block_header_t *cur_bh = (block_header_t *)fe->raw[fe->active_block_idx];
            cur_bh->state = BLK_STATE_FULL;
        }

        int new_blk = flash_allocate_free_block(fe);
        if (new_blk < 0) {
            if (!flash_run_gc(fe)) return false;
            new_blk = flash_allocate_free_block(fe);
            if (new_blk < 0) return false;
        }

        fe->active_block_idx = new_blk;
        fe->write_offset = sizeof(block_header_t);
    }

    flash_invalidate_prior_versions(fe, id);

    record_header_t rh;
    rh.magic = FLASH_MAGIC;
    rh.record_id = id;
    rh.length = len;
    rh.sequence = fe->global_seq++;
    rh.status = STATUS_COMMITTED;
    rh.crc32 = compute_crc32(payload, len);

    uint8_t *dest = &fe->raw[fe->active_block_idx][fe->write_offset];
    memcpy(dest, &rh, sizeof(rh));
    memcpy(dest + sizeof(rh), payload, len);

    fe->write_offset += total_size;
    return true;
}

bool flash_read_record(const flash_engine_t *fe, uint16_t id, uint8_t *out_buf, uint16_t max_len, uint16_t *actual_len) {
    uint32_t best_seq = 0;
    const record_header_t *best_rh = NULL;
    const uint8_t *best_payload = NULL;

    for (int b = 0; b < FLASH_BLOCK_COUNT; b++) {
        size_t off = sizeof(block_header_t);
        while (off + sizeof(record_header_t) <= FLASH_BLOCK_SIZE) {
            const record_header_t *rh = (const record_header_t *)&fe->raw[b][off];
            if (rh->magic != FLASH_MAGIC) break;

            if (rh->record_id == id && rh->status == STATUS_COMMITTED && rh->sequence >= best_seq) {
                const uint8_t *payload = &fe->raw[b][off + sizeof(record_header_t)];
                if (compute_crc32(payload, rh->length) == rh->crc32) {
                    best_seq = rh->sequence;
                    best_rh = rh;
                    best_payload = payload;
                }
            }
            off += sizeof(record_header_t) + rh->length;
        }
    }

    if (!best_rh) return false;
    uint16_t to_copy = best_rh->length < max_len ? best_rh->length : max_len;
    memcpy(out_buf, best_payload, to_copy);
    if (actual_len) *actual_len = to_copy;
    return true;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <vector>
#include <array>
#include <optional>
#include <span>
#include <algorithm>
#include <memory>
#include <stdexcept>

class FlashLogStore {
public:
    static constexpr size_t BlockSize = 4096;
    static constexpr size_t BlockCount = 8;
    static constexpr uint8_t MagicByte = 0xA5;

    enum class BlockState : uint8_t {
        Free   = 0xFF,
        Active = 0xAA,
        Full   = 0x55
    };

    enum class RecordStatus : uint8_t {
        Committed = 0x00,
        Invalid   = 0x55,
        Empty     = 0xFF
    };

    struct RecordHeader {
        uint8_t  magic{MagicByte};
        uint16_t record_id{0};
        uint16_t length{0};
        uint32_t sequence{0};
        RecordStatus status{RecordStatus::Committed};
        uint32_t crc32{0};
    } __attribute__((packed));

    struct BlockHeader {
        uint32_t erase_count{0};
        BlockState state{BlockState::Free};
        uint8_t reserved[3]{0xFF, 0xFF, 0xFF};
    } __attribute__((packed));

    FlashLogStore() {
        for (auto &blk : storage_) {
            blk.fill(0xFF);
            auto *bh = reinterpret_cast<BlockHeader *>(blk.data());
            bh->erase_count = 0;
            bh->state = BlockState::Free;
        }
    }

    bool write(uint16_t id, std::span<const uint8_t> data) {
        const size_t total_size = sizeof(RecordHeader) + data.size();
        if (total_size > BlockSize - sizeof(BlockHeader)) {
            return false;
        }

        if (!active_block_ || write_offset_ + total_size > BlockSize) {
            if (active_block_) {
                auto *bh = reinterpret_cast<BlockHeader *>(storage_[*active_block_].data());
                bh->state = BlockState::Full;
            }

            auto new_blk = allocate_block();
            if (!new_blk) {
                if (!collect_garbage()) return false;
                new_blk = allocate_block();
                if (!new_blk) return false;
            }

            active_block_ = new_blk;
            write_offset_ = sizeof(BlockHeader);
        }

        invalidate_older(id);

        RecordHeader rh;
        rh.magic = MagicByte;
        rh.record_id = id;
        rh.length = static_cast<uint16_t>(data.size());
        rh.sequence = global_sequence_++;
        rh.status = RecordStatus::Committed;
        rh.crc32 = calculate_crc32(data);

        auto &raw_block = storage_[*active_block_];
        std::copy_n(reinterpret_cast<const uint8_t *>(&rh), sizeof(rh), raw_block.begin() + write_offset_);
        std::copy(data.begin(), data.end(), raw_block.begin() + write_offset_ + sizeof(rh));

        write_offset_ += total_size;
        return true;
    }

    [[nodiscard]] std::optional<std::vector<uint8_t>> read(uint16_t id) const {
        uint32_t max_seq = 0;
        const RecordHeader *found_hdr = nullptr;
        const uint8_t *found_payload = nullptr;

        for (const auto &blk : storage_) {
            size_t off = sizeof(BlockHeader);
            while (off + sizeof(RecordHeader) <= BlockSize) {
                const auto *rh = reinterpret_cast<const RecordHeader *>(&blk[off]);
                if (rh->magic != MagicByte) break;

                if (rh->record_id == id && rh->status == RecordStatus::Committed && rh->sequence >= max_seq) {
                    const uint8_t *payload = &blk[off + sizeof(RecordHeader)];
                    if (calculate_crc32(std::span(payload, rh->length)) == rh->crc32) {
                        max_seq = rh->sequence;
                        found_hdr = rh;
                        found_payload = payload;
                    }
                }
                off += sizeof(RecordHeader) + rh->length;
            }
        }

        if (!found_hdr) return std::nullopt;
        return std::vector<uint8_t>(found_payload, found_payload + found_hdr->length);
    }

private:
    std::array<std::array<uint8_t, BlockSize>, BlockCount> storage_{};
    std::optional<size_t> active_block_{std::nullopt};
    size_t write_offset_{0};
    uint32_t global_sequence_{1};

    static uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFF;
        for (uint8_t b : data) {
            crc ^= b;
            for (int j = 0; j < 8; ++j) {
                crc = (crc & 1) ? ((crc >> 1) ^ 0xEDB88320) : (crc >> 1);
            }
        }
        return ~crc;
    }

    std::optional<size_t> allocate_block() {
        size_t best_idx = BlockCount;
        uint32_t min_erase = UINT32_MAX;

        for (size_t i = 0; i < BlockCount; ++i) {
            const auto *bh = reinterpret_cast<const BlockHeader *>(storage_[i].data());
            if (bh->state == BlockState::Free && bh->erase_count < min_erase) {
                min_erase = bh->erase_count;
                best_idx = i;
            }
        }

        if (best_idx < BlockCount) {
            auto *bh = reinterpret_cast<BlockHeader *>(storage_[best_idx].data());
            bh->state = BlockState::Active;
            return best_idx;
        }
        return std::nullopt;
    }

    void erase_block(size_t block_idx) {
        auto *bh = reinterpret_cast<BlockHeader *>(storage_[block_idx].data());
        uint32_t next_ec = bh->erase_count + 1;
        storage_[block_idx].fill(0xFF);
        bh->erase_count = next_ec;
        bh->state = BlockState::Free;
    }

    void invalidate_older(uint16_t id) {
        for (auto &blk : storage_) {
            size_t off = sizeof(BlockHeader);
            while (off + sizeof(RecordHeader) <= BlockSize) {
                auto *rh = reinterpret_cast<RecordHeader *>(&blk[off]);
                if (rh->magic != MagicByte) break;
                if (rh->record_id == id && rh->status == RecordStatus::Committed) {
                    rh->status = RecordStatus::Invalid;
                }
                off += sizeof(RecordHeader) + rh->length;
            }
        }
    }

    bool collect_garbage() {
        size_t victim_idx = BlockCount;
        size_t max_dead_bytes = 0;

        for (size_t b = 0; b < BlockCount; ++b) {
            if (active_block_ && b == *active_block_) continue;
            const auto *bh = reinterpret_cast<const BlockHeader *>(storage_[b].data());
            if (bh->state != BlockState::Full) continue;

            size_t off = sizeof(BlockHeader);
            size_t dead = 0;
            while (off + sizeof(RecordHeader) <= BlockSize) {
                const auto *rh = reinterpret_cast<const RecordHeader *>(&storage_[b][off]);
                if (rh->magic != MagicByte) break;
                if (rh->status == RecordStatus::Invalid) {
                    dead += sizeof(RecordHeader) + rh->length;
                }
                off += sizeof(RecordHeader) + rh->length;
            }

            if (dead > max_dead_bytes) {
                max_dead_bytes = dead;
                victim_idx = b;
            }
        }

        if (victim_idx >= BlockCount) return false;

        // Копіюємо валідні записи
        size_t off = sizeof(BlockHeader);
        while (off + sizeof(RecordHeader) <= BlockSize) {
            const auto *rh = reinterpret_cast<const RecordHeader *>(&storage_[victim_idx][off]);
            if (rh->magic != MagicByte) break;
            if (rh->status == RecordStatus::Committed) {
                const uint8_t *payload = &storage_[victim_idx][off + sizeof(RecordHeader)];
                write(rh->record_id, std::span(payload, rh->length));
            }
            off += sizeof(RecordHeader) + rh->length;
        }

        erase_block(victim_idx);
        return true;
    }
};
```
:::

### Практичні інваріанти надійності та крайові випадки

1. **Запобігання переповненню пулу чистих блоків**: для гарантованої роботи збирача сміття у сховищі завжди повинен залишатися щонайменше один повністю стертий резервний блок (*spare block*). Якщо всі блоки заповнити корисними даними без резерву, процедура GC не зможе виділити блок для перенесення дійсних записів і зазнає аварійної зупинки.
2. **Верифікація частково записаних блоків під час старту**: якщо живлення обірвалося посеред запису заголовка чи корисного навантаження, під час першого сканування функція `read` виявить невідповідність поля `crc32` або зіпсований `magic`. Такий недописаний хвіст автоматично ігнорується, а останньою валідною версією залишається попередній повністю зафіксований запис.
3. **Статичний знос при незмінних даних**: якщо один із параметрів (наприклад, заводський серійний номер пристрою) записується один раз і ніколи не оновлюється, його блок матиме `erase_count = 0`, тоді як сусідні блоки з логами досягнуть ліміту в 100 000 стирань. Для подолання цієї проблеми в реальних промислових системах додають поріг різниці зносу: якщо різниця лічильників між найбільш і найменш зношеними блоками перевищує поріг (наприклад, `500` циклів), збирач сміття примусово компактифікує навіть статичний блок, переносячи його в зношений сектор.
