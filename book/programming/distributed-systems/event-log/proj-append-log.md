# ⚙️ Реалізація сегментованого журналу подій з розрідженим індексом

У розподілених архітектурах журнал подій (англ. *event log* або *commit log*) є фундаментальним будівельним блоком персистентності, на якому тримаються розподілені черги повідомлень, механізми реплікації транзакційних баз даних та консенсусні протоколи типу Raft і Paxos. Головна перевага моделі журналу полягає у фізиці дискового вводу-виводу: послідовний запис (англ. *sequential I/O*) у кінець файлу виконується з максимальною пропускною здатністю накопичувача (150–250 МБ/с для магнітних HDD та 3–7 ГБ/с для швидких накопичувачів NVMe SSD), тоді як випадковий доступ (англ. *random I/O*) сповільнює роботу на кілька порядків через механічне переміщення головок диску або постійне перебалансування B-дерев і LSM-структур.

Створимо власну повноцінну інженерну реалізацію сегментованого журналу подій мовами C та C++, яка втілює ключові архітектурні механізми дискового зберігання Apache Kafka: бінарне фреймування повідомлень, розрахунок контрольних сум CRC32 для захисту від пошкоджень, розбиття на фіксовані сегменти, керування життєвим циклом файлів, часові індекси та швидкий двійковий пошук через пам'яттєво-ефективний розріджений індекс.

![Внутрішня будова сегментів та розрідженого індексу журналу](/book/programming/distributed-systems/event-log/img/log-segments-and-sparse-index.svg)
*Кожен сегмент складається з бінарного логу послідовних записів (.log) та розрідженого індексу (.index), що зіставляє логічний зсув із фізичною позицією байта на диску.*

---

## 1. Архітектура файлового сховища на диску

У промислових системах топік ніколи не зберігається як один гігантський файл розміром у сотні гігабайтів. Такий монолітний підхід унеможливлює видалення застарілих даних за терміном давності (англ. *retention policy*), оскільки видалення байтів із початку звичайного файлу операційної системи вимагає повного перезапису гігабайтів даних зі зсувом усього вмісту.

Замість цього секція логу розбивається на окремі **сегменти** (англ. *segments*). Кожен сегмент складається з групи файлів з однаковою базовою назвою:
1. `00000000000000000000.log` — файл первинних даних, куди послідовно записуються бінарні фрейми повідомлень.
2. `00000000000000000000.index` — файл розрідженого індексу зсувів (англ. *offset index*), який зіставляє логічний зсув повідомлення з його точною фізичною позицією (зсувом у байтах) усередині відповідного `.log`-файлу.
3. `00000000000000000000.timeindex` — файл розрідженого часового індексу (англ. *time index*), що дозволяє знаходити зсув повідомлення за часовою міткою створення (Unix Timestamp).

Назва кожного файлу сегмента формується як 20-значне десяткове число, доповнене нулями зліва (наприклад, `00000000000010500000.log`). Це число позначає **базовий зсув** (англ. *base offset*) — логічний порядковий номер найпершого повідомлення, збереженого в цьому сегменті.

### Правила ротації сегментів (Segment Rolling)

У будь-який момент часу в кожній секції існує рівно один **активний сегмент** (англ. *active segment*), до якого додаються нові повідомлення. Усі попередні сегменти є закритими (англ. *immutable / read-only*): вони доступні лише для читання споживачами або фонового очищення.

Ротація активного сегмента (створення нового файлу) відбувається за однією з трьох умов:
* **Ліміт за розміром:** Розмір поточного `.log` файлу досяг конфігураційного порогу `segment.bytes` (за замовчуванням у Kafka це 1 ГБ, у нашій навчальній реалізації — 10 МБ).
* **Ліміт за часом:** З моменту першого запису в сегмент минуло більше часу, ніж задано параметром `segment.ms` (зазвичай 7 днів), навіть якщо файл не заповнений повністю.
* **Заповнення індексу:** Розмір індексного файлу досяг ліміту `segment.index.bytes` (зазвичай 10 МБ).

Щойно умова спрацьовує, активний сегмент примусово скидає буфери на диск (`fflush`/`fsync`), закривається на запис, і відкривається новий сегмент, чиє ім'я точно дорівнює наступному вільному логічному зсуву (`next_offset`).

---

## 2. Формат бінарних даних та розріджений індекс

Журнал уникає використання текстових форматів (JSON, XML), оскільки вони збільшують обсяг даних на диску в 3–5 разів та витрачають значні ресурси процесора на строковий парсинг.

### Бінарний фрейм запису в `.log`

Кожен запис пакується в строго вирівняний бінарний контейнер:

```
+------------------+------------------+------------------+------------------+
| CRC32 (4 байти)  | Magic (1 байт)   | Flags (1 байт)   | Offset (8 байтів)|
+------------------+------------------+------------------+------------------+
| Timestamp (8 B)  | KeyLen (4 байти) | Key (змінна довжина)                |
+------------------+------------------+-------------------------------------+
| ValueLen (4 B)   | Value (змінна довжина)                                 |
+------------------+--------------------------------------------------------+
```

* **CRC32 (4 байти, IEEE 802.3):** Контрольна сума всього фрейму (крім самого поля CRC). Дозволяє миттєво відкинути неповні записи (англ. *torn writes*), спричинені раптовим вимкненням живлення.
* **Magic (1 байт):** Версія формату (наприклад, `0x01`). Забезпечує пряму й зворотну сумісність.
* **Flags (1 байт):** Атрибути запису (наприклад, біти 0–2 вказують на алгоритм стиснення: 0 — без стиснення, 1 — gzip, 2 — snappy, 3 — lz4, 4 — zstd).
* **Offset (8 байтів, int64):** Унікальний монотонічний логічний зсув запису.
* **Timestamp (8 байтів, int64):** Час створення запису (Unix Epoch у мілісекундах).
* **Key Length (4 байти, int32):** Довжина ключа в байтах. Значення `-1` означає відсутність ключа (null key).
* **Key Bytes:** Байти ключа, що використовуються для маршрутизації за секціями та ущільнення журналу.
* **Value Length (4 байти, int32):** Довжина корисного навантаження (тіла повідомлення).
* **Value Bytes:** Довільні бінарні дані повідомлення.

### Механіка розрідженого індексу `.index`

Якби індекс містив запис для кожного окремого повідомлення, розмір індексного файлу зрівнявся б із розміром файлу даних, витісняючи корисні дані з дискового кешу. 

Тому застосовується **розріджений індекс** (англ. *Sparse Index*). Запис в індекс додається лише тоді, коли обсяг записаних у `.log` байтів після попередньої індексної позначки перевищує інтервал `INDEX_INTERVAL_BYTES` (за замовчуванням у Kafka це 4096 байтів — розмір однієї фізичної сторінки віртуальної пам'яті x86-64):

```
+-------------------------------+-------------------------------+
| Relative Offset (4 байти)     | Physical Position (4 байти)   |
+-------------------------------+-------------------------------+
```

* **Relative Offset (4 байти, uint32):** Відносний зсув відносно базового зсуву сегмента:
  ```
  relative_offset = global_offset - base_offset
  ```
  Зберігання 4-байтового відносного числа замість 8-байтового абсолютного економить 50% пам'яті індексу.
* **Physical Position (4 байти, uint32):** Фізичний зсув у байтах від початку файлу `.log`.

Завдяки розрідженню індексний файл для сегмента розміром 1 ГБ займає лише `(1 ГБ / 4 КБ) × 8 байтів ≈ 2 МБ`. Такий мізерний обсяг дозволяє повністю завантажити індекс у пам'ять або відобразити його через `mmap(2)`, де пошук позиції виконується за алгоритмом двійкового пошуку `O(log N)` без жодного фізичного звернення до повільного диску.

---

## 3. Повний вихідний код рушія журналу

Нижче наведено робочу реалізацію рушія на мовах C та C++. Реалізація забезпечує створення сегментів, формування бінарних фреймів, обчислення контрольних сум, автоматичне ведення розрідженого індексу та двофазний пошук повідомлень (двійковий пошук в індексі з наступним коротким скануванням сторінки).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <errno.h>

#define INDEX_INTERVAL_BYTES 4096
#define MAX_SEGMENT_BYTES    (10 * 1024 * 1024) /* 10 МБ для навчального тесту */

/* Таблиця CRC32 IEEE 802.3 */
static uint32_t crc32_for_byte(uint32_t r) {
    for (int j = 0; j < 8; ++j)
        r = (r & 1 ? 0xEDB88320L : 0) ^ r >> 1;
    return r ^ 0xFF000000L;
}

static uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0;
    while (length--) {
        static uint32_t table[256];
        static bool table_init = false;
        if (!table_init) {
            for (size_t i = 0; i < 256; ++i)
                table[i] = crc32_for_byte((uint32_t)i);
            table_init = true;
        }
        crc = table[(uint8_t)crc ^ *data++] ^ crc >> 8;
    }
    return crc;
}

#pragma pack(push, 1)
typedef struct {
    uint32_t relative_offset;
    uint32_t physical_pos;
} IndexEntry;

typedef struct {
    uint32_t crc;
    uint8_t  magic;
    uint8_t  flags;
    uint64_t offset;
    uint64_t timestamp;
    int32_t  key_len;
} RecordHeader;
#pragma pack(pop)

typedef struct {
    char log_path[256];
    char idx_path[256];
    FILE *log_file;
    FILE *idx_file;
    uint64_t base_offset;
    uint64_t next_offset;
    uint32_t current_log_size;
    uint32_t bytes_since_last_index;
} LogSegment;

/* Відкриття або створення нового сегмента */
int segment_open(LogSegment *seg, const char *dir, uint64_t base_offset) {
    memset(seg, 0, sizeof(LogSegment));
    seg->base_offset = base_offset;
    seg->next_offset = base_offset;

    snprintf(seg->log_path, sizeof(seg->log_path), "%s/%020llu.log", dir, (unsigned long long)base_offset);
    snprintf(seg->idx_path, sizeof(seg->idx_path), "%s/%020llu.index", dir, (unsigned long long)base_offset);

    seg->log_file = fopen(seg->log_path, "a+b");
    if (!seg->log_file) return -1;

    seg->idx_file = fopen(seg->idx_path, "a+b");
    if (!seg->idx_file) {
        fclose(seg->log_file);
        return -1;
    }

    fseek(seg->log_file, 0, SEEK_END);
    seg->current_log_size = (uint32_t)ftell(seg->log_file);
    seg->bytes_since_last_index = 0;

    return 0;
}

/* Закриття сегмента та скидання буферів */
void segment_close(LogSegment *seg) {
    if (seg->log_file) { fflush(seg->log_file); fclose(seg->log_file); seg->log_file = NULL; }
    if (seg->idx_file) { fflush(seg->idx_file); fclose(seg->idx_file); seg->idx_file = NULL; }
}

/* Послідовне додавання нового запису в сегмент */
int segment_append(LogSegment *seg, const uint8_t *key, int32_t key_len,
                   const uint8_t *val, int32_t val_len, uint64_t *assigned_offset) {
    if (!seg->log_file || !seg->idx_file) return -1;

    uint64_t offset = seg->next_offset;
    uint64_t now_ms = (uint64_t)time(NULL) * 1000;
    uint32_t record_pos = seg->current_log_size;

    int32_t valid_klen = (key_len > 0) ? key_len : 0;
    int32_t valid_vlen = (val_len > 0) ? val_len : 0;

    /* Обчислення розміру тіла для CRC (все, крім 4 байт поля CRC) */
    size_t payload_size = sizeof(RecordHeader) - sizeof(uint32_t) + valid_klen + sizeof(int32_t) + valid_vlen;
    uint8_t *buf = (uint8_t*)malloc(payload_size);
    if (!buf) return -ENOMEM;

    uint8_t *ptr = buf;
    uint8_t magic = 0x01;
    uint8_t flags = 0x00;

    memcpy(ptr, &magic, 1); ptr += 1;
    memcpy(ptr, &flags, 1); ptr += 1;
    memcpy(ptr, &offset, 8); ptr += 8;
    memcpy(ptr, &now_ms, 8); ptr += 8;
    memcpy(ptr, &key_len, 4); ptr += 4;
    if (valid_klen > 0) { memcpy(ptr, key, valid_klen); ptr += valid_klen; }
    memcpy(ptr, &val_len, 4); ptr += 4;
    if (valid_vlen > 0) { memcpy(ptr, val, valid_vlen); ptr += valid_vlen; }

    uint32_t crc = calculate_crc32(buf, payload_size);

    /* Запис: CRC32 та корисне навантаження */
    if (fwrite(&crc, sizeof(uint32_t), 1, seg->log_file) != 1 ||
        fwrite(buf, payload_size, 1, seg->log_file) != 1) {
        free(buf);
        return -EIO;
    }
    free(buf);

    size_t total_record_bytes = sizeof(uint32_t) + payload_size;
    seg->current_log_size += (uint32_t)total_record_bytes;
    seg->bytes_since_last_index += (uint32_t)total_record_bytes;

    /* Оновлення розрідженого індексу при перевищенні 4 КБ */
    if (seg->bytes_since_last_index >= INDEX_INTERVAL_BYTES || offset == seg->base_offset) {
        IndexEntry ie;
        ie.relative_offset = (uint32_t)(offset - seg->base_offset);
        ie.physical_pos = record_pos;

        if (fwrite(&ie, sizeof(IndexEntry), 1, seg->idx_file) != 1) {
            return -EIO;
        }
        fflush(seg->idx_file);
        seg->bytes_since_last_index = 0;
    }

    fflush(seg->log_file);
    seg->next_offset++;
    if (assigned_offset) *assigned_offset = offset;
    return 0;
}

/* Двофазний пошук запису за цільовим зсувом */
int segment_read_at(LogSegment *seg, uint64_t target_offset,
                    uint8_t *out_val, int32_t *out_val_len) {
    if (target_offset < seg->base_offset || target_offset >= seg->next_offset)
        return -ENOENT;

    /* Фаза 1: Двійковий пошук в індексному файлі найближчої нижньої межі */
    fseek(seg->idx_file, 0, SEEK_END);
    long idx_file_size = ftell(seg->idx_file);
    int num_entries = (int)(idx_file_size / sizeof(IndexEntry));

    uint32_t search_rel_offset = (uint32_t)(target_offset - seg->base_offset);
    uint32_t best_physical_pos = 0;

    int low = 0, high = num_entries - 1;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        IndexEntry entry;
        fseek(seg->idx_file, mid * sizeof(IndexEntry), SEEK_SET);
        if (fread(&entry, sizeof(IndexEntry), 1, seg->idx_file) != 1) break;

        if (entry.relative_offset <= search_rel_offset) {
            best_physical_pos = entry.physical_pos;
            low = mid + 1; /* Звужуємо діапазон праворуч */
        } else {
            high = mid - 1;
        }
    }

    /* Фаза 2: Лінійне сканування максимум 4 КБ у .log від знайденого зсуву */
    fseek(seg->log_file, best_physical_pos, SEEK_SET);

    while (ftell(seg->log_file) < seg->current_log_size) {
        uint32_t stored_crc;
        if (fread(&stored_crc, sizeof(uint32_t), 1, seg->log_file) != 1) break;

        uint8_t magic, flags;
        uint64_t record_offset, ts;
        int32_t klen, vlen;

        if (fread(&magic, 1, 1, seg->log_file) != 1) break;
        if (fread(&flags, 1, 1, seg->log_file) != 1) break;
        if (fread(&record_offset, 8, 1, seg->log_file) != 1) break;
        if (fread(&ts, 8, 1, seg->log_file) != 1) break;
        if (fread(&klen, 4, 1, seg->log_file) != 1) break;

        if (klen > 0) fseek(seg->log_file, klen, SEEK_CUR);

        if (fread(&vlen, 4, 1, seg->log_file) != 1) break;

        if (record_offset == target_offset) {
            if (vlen > 0 && out_val) {
                if (fread(out_val, 1, vlen, seg->log_file) != (size_t)vlen) return -EIO;
                *out_val_len = vlen;
            } else {
                *out_val_len = 0;
            }
            return 0; /* Успішно знайдено */
        }

        if (vlen > 0) fseek(seg->log_file, vlen, SEEK_CUR);
    }

    return -ENOENT;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <fstream>
#include <filesystem>
#include <memory>
#include <chrono>
#include <expected>
#include <cstdint>
#include <cstring>

namespace fs = std::filesystem;

namespace eventlog {

constexpr size_t INDEX_INTERVAL_BYTES = 4096;

#pragma pack(push, 1)
struct IndexEntry {
    uint32_t relative_offset{0};
    uint32_t physical_pos{0};
};
#pragma pack(pop)

/* Клас сегмента журналу з безпечним RAII-керуванням ресурсами */
class LogSegment {
public:
    static std::expected<std::unique_ptr<LogSegment>, std::string>
    open(const fs::path& dir, uint64_t base_offset) {
        char name_buf[64];
        std::snprintf(name_buf, sizeof(name_buf), "%020llu", static_cast<unsigned long long>(base_offset));

        auto log_p = dir / (std::string(name_buf) + ".log");
        auto idx_p = dir / (std::string(name_buf) + ".index");

        auto seg = std::unique_ptr<LogSegment>(new LogSegment(base_offset, log_p, idx_p));
        if (!seg->init()) {
            return std::unexpected("Не вдалося відкрити файли сегмента: " + log_p.string());
        }
        return seg;
    }

    ~LogSegment() {
        flush();
    }

    LogSegment(const LogSegment&) = delete;
    LogSegment& operator=(const LogSegment&) = delete;

    LogSegment(LogSegment&&) noexcept = default;
    LogSegment& operator=(LogSegment&&) noexcept = default;

    /* Додавання нового повідомлення у кінець сегмента */
    std::expected<uint64_t, std::string>
    append(std::string_view key, std::string_view value) {
        if (!log_stream_.is_open() || !idx_stream_.is_open()) {
            return std::unexpected("Файли сегмента не готові до запису");
        }

        uint64_t offset = next_offset_;
        uint64_t now_ms = static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::system_clock::now().time_since_epoch()
            ).count()
        );

        uint32_t record_pos = current_log_size_;
        int32_t key_len = static_cast<int32_t>(key.size());
        int32_t val_len = static_cast<int32_t>(value.size());

        // Формування бінарного тіла фрейму
        std::vector<uint8_t> payload;
        payload.reserve(1 + 1 + 8 + 8 + 4 + key.size() + 4 + value.size());

        uint8_t magic = 0x01;
        uint8_t flags = 0x00;
        append_bytes(payload, &magic, 1);
        append_bytes(payload, &flags, 1);
        append_bytes(payload, &offset, sizeof(offset));
        append_bytes(payload, &now_ms, sizeof(now_ms));
        append_bytes(payload, &key_len, sizeof(key_len));
        if (!key.empty()) append_bytes(payload, key.data(), key.size());
        append_bytes(payload, &val_len, sizeof(val_len));
        if (!value.empty()) append_bytes(payload, value.data(), value.size());

        uint32_t crc = calculate_crc32(payload.data(), payload.size());

        // Фізичний запис у файл .log
        log_stream_.write(reinterpret_cast<const char*>(&crc), sizeof(crc));
        log_stream_.write(reinterpret_cast<const char*>(payload.data()), payload.size());

        if (log_stream_.bad()) {
            return std::unexpected("Помилка вводу-виводу при записі в .log");
        }

        size_t total_bytes = sizeof(crc) + payload.size();
        current_log_size_ += static_cast<uint32_t>(total_bytes);
        bytes_since_last_index_ += static_cast<uint32_t>(total_bytes);

        // Додавання мітки до розрідженого індексу
        if (bytes_since_last_index_ >= INDEX_INTERVAL_BYTES || offset == base_offset_) {
            IndexEntry entry{
                .relative_offset = static_cast<uint32_t>(offset - base_offset_),
                .physical_pos = record_pos
            };
            idx_stream_.write(reinterpret_cast<const char*>(&entry), sizeof(entry));
            idx_stream_.flush();
            bytes_since_last_index_ = 0;
        }

        log_stream_.flush();
        next_offset_++;
        return offset;
    }

    /* Швидкий пошук за зсувом через індекс */
    std::expected<std::string, std::string>
    read_at(uint64_t target_offset) {
        if (target_offset < base_offset_ || target_offset >= next_offset_) {
            return std::unexpected("Запитуваний зсув знаходиться поза межами цього сегмента");
        }

        // 1. Двійковий пошук найближчого меншого зсуву в .index
        std::ifstream idx_in(idx_path_, std::ios::binary | std::ios::ate);
        if (!idx_in.is_open()) return std::unexpected("Не вдалося відкрити індексний файл");

        auto idx_size = idx_in.tellg();
        size_t num_entries = idx_size / sizeof(IndexEntry);

        uint32_t search_rel = static_cast<uint32_t>(target_offset - base_offset_);
        uint32_t best_pos = 0;

        int low = 0, high = static_cast<int>(num_entries) - 1;
        while (low <= high) {
            int mid = low + (high - low) / 2;
            idx_in.seekg(mid * sizeof(IndexEntry));
            IndexEntry entry;
            idx_in.read(reinterpret_cast<char*>(&entry), sizeof(entry));

            if (entry.relative_offset <= search_rel) {
                best_pos = entry.physical_pos;
                low = mid + 1;
            } else {
                high = mid - 1;
            }
        }
        idx_in.close();

        // 2. Послідовне сканування логу від знайденої точки (максимум 4 КБ)
        std::ifstream log_in(log_path_, std::ios::binary);
        if (!log_in.is_open()) return std::unexpected("Не вдалося відкрити лог для читання");

        log_in.seekg(best_pos);

        while (log_in.tellg() < current_log_size_ && log_in.good()) {
            uint32_t crc;
            uint8_t magic, flags;
            uint64_t rec_offset, ts;
            int32_t klen, vlen;

            log_in.read(reinterpret_cast<char*>(&crc), sizeof(crc));
            log_in.read(reinterpret_cast<char*>(&magic), sizeof(magic));
            log_in.read(reinterpret_cast<char*>(&flags), sizeof(flags));
            log_in.read(reinterpret_cast<char*>(&rec_offset), sizeof(rec_offset));
            log_in.read(reinterpret_cast<char*>(&ts), sizeof(ts));
            log_in.read(reinterpret_cast<char*>(&klen), sizeof(klen));

            if (klen > 0) log_in.seekg(klen, std::ios::cur);
            log_in.read(reinterpret_cast<char*>(&vlen), sizeof(vlen));

            if (rec_offset == target_offset) {
                std::string result(vlen, '\0');
                if (vlen > 0) log_in.read(result.data(), vlen);
                return result;
            }

            if (vlen > 0) log_in.seekg(vlen, std::ios::cur);
        }

        return std::unexpected("Запис не знайдено в журналі");
    }

    [[nodiscard]] uint64_t base_offset() const noexcept { return base_offset_; }
    [[nodiscard]] uint64_t next_offset() const noexcept { return next_offset_; }
    [[nodiscard]] uint32_t size_bytes() const noexcept { return current_log_size_; }

private:
    LogSegment(uint64_t base_offset, fs::path log_p, fs::path idx_p)
        : base_offset_(base_offset), next_offset_(base_offset),
          log_path_(std::move(log_p)), idx_path_(std::move(idx_p)) {}

    bool init() {
        log_stream_.open(log_path_, std::ios::in | std::ios::out | std::ios::binary | std::ios::app);
        idx_stream_.open(idx_path_, std::ios::in | std::ios::out | std::ios::binary | std::ios::app);

        if (!log_stream_.is_open() || !idx_stream_.is_open()) return false;

        log_stream_.seekp(0, std::ios::end);
        current_log_size_ = static_cast<uint32_t>(log_stream_.tellp());
        return true;
    }

    void flush() {
        if (log_stream_.is_open()) log_stream_.flush();
        if (idx_stream_.is_open()) idx_stream_.flush();
    }

    static void append_bytes(std::vector<uint8_t>& buf, const void* data, size_t sz) {
        const auto* ptr = static_cast<const uint8_t*>(data);
        buf.insert(buf.end(), ptr, ptr + sz);
    }

    static uint32_t calculate_crc32(const uint8_t* data, size_t length) {
        uint32_t crc = 0;
        for (size_t i = 0; i < length; ++i) {
            uint8_t byte = data[i];
            crc ^= byte;
            for (int j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
            }
        }
        return crc;
    }

    uint64_t base_offset_{0};
    uint64_t next_offset_{0};
    uint32_t current_log_size_{0};
    uint32_t bytes_since_last_index_{0};

    fs::path log_path_;
    fs::path idx_path_;
    std::fstream log_stream_;
    std::fstream idx_stream_;
};

} // namespace eventlog
```
:::

---

## 4. Покроковий розбір алгоритму читання та пошуку

Алгоритм читання за довільним числовим зсувом (Offset Lookup) є компромісом між споживанням пам'яті та затримкою вводу-виводу. Розгляньмо його покроково на прикладі запиту `read_at(offset = 10072)` у сегменті з `base_offset = 10000`:

1. **Розрахунок відносного зсуву:** Рушій обчислює шуканий відносний індекс:
   ```
   search_rel = 10072 - 10000 = 72
   ```
2. **Двійковий пошук в індексі (Phase 1):** Рушій зчитує масив `IndexEntry` розміром 8 байтів кожен. Якщо індекс містить 1000 записів, алгоритм виконує `log2(1000) ≈ 10` ітерацій, щоб знайти найбільший запис, чий `relative_offset <= 72`.
   Припустимо, індекс містить позначки:
   * Запис 0: `rel_offset = 0  -> pos = 0`
   * Запис 1: `rel_offset = 45 -> pos = 4096`
   * Запис 2: `rel_offset = 92 -> pos = 8192`
   Найближчим меншим значенням до 72 є Запис 1 (`rel_offset = 45`, `pos = 4096`).
3. **Пряме позиціювання (Seek):** Рушій виконує одноразовий `fseek(log_file, 4096, SEEK_SET)`, миттєво переміщуючи покажчик читання в операційній системі на початок потрібної дискової сторінки.
4. **Обмежене лінійне сканування (Phase 2):** Рушій послідовно читає бінарні фрейми записів, починаючи з байта 4096. Оскільки розрідження індексу гарантує, що наступна позначка була створена не пізніше ніж через 4096 байтів, рушій гарантовано просканує не більше ніж 4 КБ даних.
5. **Валідація та вилучення:** Знайшовши заголовок із полем `offset == 10072`, рушій звіряє контрольну суму CRC32 і копіює корисне навантаження в буфер споживача.

Завдяки такій двофазній схемі будь-яке повідомлення з терабайтного сховища зчитується рівно за одну операцію дискового пошуку (seek) та одне коротке читання 4 КБ сторінки, яка майже завжди вже знаходиться в кеші ядра Linux.

---

## 5. Часовий індекс `.timeindex` та перемотування за часом

На практиці споживачам часто потрібно почати вичитування даних не за числовим зсувом (який є суто внутрішнім ідентифікатором брокера), а за календарним часом (наприклад: «перечитати всі події за вчора з 14:00», або «відновити стан бази даних на момент аварії об 11:35:00»).

Для цього поруч із файлом `.index` створюється третій файл сегмента — **часовий індекс** `.timeindex` (Time Index).

### Структура запису в `.timeindex`
Кожен запис у `.timeindex` займає фіксовані 12 байтів:

```
+-----------------------------------+-------------------------------+
| Timestamp (8 байтів, int64)       | Relative Offset (4 байти)     |
+-----------------------------------+-------------------------------+
```

* **Timestamp (8 байтів):** Найбільша часова мітка серед усіх повідомлень, доданих до логу з моменту попередньої індексної позначки.
* **Relative Offset (4 байти):** Відносний зсув першого повідомлення, чий час створення дорівнює або перевищує значення `Timestamp`.

### Двоетапне перетворення «Час → Фізичний байт»
Коли клієнт викликає API пошуку за часом (наприклад, `offsetsForTimes(ts = 1700000000000)`):
1. **Пошук сегмента:** Брокер переглядає список сегментів і знаходить той, чий діапазон часу містить запитуваний `ts`.
2. **Двійковий пошук у `.timeindex`:** Виконується двійковий пошук за масивом 12-байтових записів для визначення цільового `relative_offset`.
3. **Двійковий пошук у `.index`:** Знайдений `relative_offset` подається на вхід звичайного індексу зміщень `.index`, який повертає фізичну позицію байта у файлі `.log`.
4. **Сканування:** Сервер читає повідомлення з файлу `.log`, знаходячи перше повідомлення, чий заголовок містить `timestamp >= target_ts`.

---

## 6. Пакетування (Batching) та амортизація дискових витрат

Якщо продюсер надсилає повідомлення по одному (наприклад, корисне навантаження розміром 50 байтів), накладні витрати бінарного заголовка (CRC32, Offset, Timestamp, довжини ключів — разом 34 байти) становлять майже 40% від усього обсягу переданих даних. Більше того, кожен окремий мережевий пакет викликає окреме переривання ядра та системний виклик `write(2)`.

У промислових журналах подій цю проблему вирішують за допомогою **пакетування записів** (RecordBatch). Продюсер накопичує повідомлення в пам'яті протягом короткого вікна (наприклад, `linger.ms = 10` або до досягнення `batch.size = 64 КБ`).

Усі повідомлення в пакеті записуються під єдиним спільним заголовком пакета (Outer Batch Header):
* Обчислюється один спільний `CRC32` на весь пакет із сотень повідомлень.
* Зберігається один базовий зсув `base_offset` та базовий час `first_timestamp`.
* Усі повідомлення всередині пакета кодуються з використанням відносних дельт зміщення (`delta_offset = 0, 1, 2...`) та змінної довжини цілих чисел (Protobuf/ZigZag varint), що зменшує накладні витрати метаданих до кількох бітів на повідомлення.
* Весь пакет цілком стискається алгоритмом LZ4 або Zstd, після чого записується на диск за один системний виклик `writev(2)`.

---

## 7. Системні оптимізації ядра та захист від збоїв

Під час експлуатації журналу під високим навантаженням надійна робота рушія забезпечується низкою низькорівневих системних механізмів:

### Захист від обірваних записів (Torn Writes)
Якщо сервер зазнає раптової втрати електроживлення або апаратного збою ядра посеред запису великого пакета розміром 64 КБ, на диск може встигнути записатися лише 20 КБ. При перезапуску рушій виявить, що останній фрейм має пошкоджений заголовок або його обчислена контрольна сума не збігається з полем `CRC32`.
* Рушій автоматично викликає системний виклик `ftruncate(2)`, відтинаючи пошкоджений залишок файлу до останнього повністю валідного фрейму.
* Це гарантує, що журнал залишається внутрішньо несуперечливим, а неповні записи не потраплять до споживачів.

### Відновлення втраченого індексу (Index Rebuild)
Оскільки індексні файли `.index` та `.timeindex` є лише вторинними структурами прискорення пошуку, їхнє пошкодження або раптове видалення не призводить до втрати бізнес-даних. При виявленні битого індексу рушій видаляє пошкоджений `.index` файл і виконує швидкий послідовний прохід файлом `.log` від початку до кінця, записуючи нову індексну позначку через кожні 4 КБ. Відновлення індексу для гігабайтного файлу займає менше 1 секунди.

### Налаштування сторінкового кешу та скидання брудних сторінок (Dirty Page Writeback)

Оскільки журнал подій повністю покладається на сторінковий кеш ядра Linux замість керування буферами всередині пам'яті процесу (Heap), продуктивність запису безпосередньо залежить від параметрів підсистеми віртуальної пам'яті ОС:

1. **`vm.dirty_background_ratio` (зазвичай 5–10%):** Відсоток загальної оперативної пам'яті системи, заповненої «брудними» (ще не записаними на диск) сторінками, при досягненні якого фонові потоки ядра Linux (`flusher threads` або `kworker`) починають асинхронно скидати дані на накопичувач. Це не блокує виконання прикладного процесу брокера.
2. **`vm.dirty_ratio` (зазвичай 20–30%):** Жорсткий поріг брудних сторінок. Якщо швидкість вхідного потоку продюсерів перевищує фізичну пропускну здатність дисків, і обсяг брудних даних досягає цього значення, ядро Linux примусово переводить усі виклики `write(2)` у синхронний блокуючий режим. Процес брокера заморожується, поки накопичувач не звільнить частину сторінок.
3. **`vm.dirty_expire_centisecs` (зазвичай 3000 = 30 секунд):** Максимальний вік брудної сторінки в пам'яті, після якого вона підлягає обов'язковому скиданню на диск.

Правильне налаштування цих параметрів запобігає раптовим лавиноподібним «I/O Spikes», коли ядро намагається одночасно скинути десятки гігабайтів накопичених даних, що могло б викликати зависання мережевих сокетів та тайм-аути клієнтів.

Часто виникає питання: чому б не використовувати прямий ввід-вивід із прапорцем `O_DIRECT`, обходячи сторінковий кеш ОС? Прапорець `O_DIRECT` змушує будь-яке читання й запис звертатися безпосередньо до фізичного накопичувача, що вимагає вирівнювання буферів у пам'яті за розміром сектора диска (512 або 4096 байтів). У моделі журналу подій це було б катастрофою для продуктивності: якщо кілька незалежних споживачів читають свіжі повідомлення з різницею в частки секунди, сторінковий кеш віддає дані прямо з RAM без жодного читання з диска. Використання `O_DIRECT` змусило б накопичувач повторно зчитувати ті самі блоки диска для кожного клієнта, миттєво перевантажуючи шину PCIe та контролер SSD.

### Перевага нульового копіювання (Zero-Copy Transfer)
У традиційних застосунках передача даних із файлу в мережевий сокет вимагає чотирьох перемикань контексту (User/Kernel mode) та чотирьох копіювань пам'яті:
1. `Disk` -> `Page Cache` ядра (через контролер DMA).
2. `Page Cache` -> `User Space Buffer` (копіювання процесором).
3. `User Space Buffer` -> `Socket Buffer` ядра (копіювання процесором).
4. `Socket Buffer` -> `Network Interface Controller (NIC)` (через контролер DMA).

У журналі подій дані у файлі зберігаються в тому самому бінарному вигляді, у якому вони передаються клієнтам по мережі. Це дозволяє використовувати системний виклик **`sendfile(2)`** або **`splice(2)`**, який передає байти безпосередньо зі сторінкового кешу ядра Linux у чергу мережевого адаптера (DMA-to-DMA). Це повністю усуває завантаження центрального процесора на копіювання пам'яті та дозволяє одному серверу утилізувати мережеві канали 100 Gbps на повній швидкості.
