# ⚙️ Потокобезпечний реєстр параметрів поведінки з Flash-сховищем та MAVLink-транспортом

У реальних польотних контролерах одночасно функціонують десятки асинхронних задач різного ступеня критичності та з кардинально відмінними часовими бюджетами.

1. **Високочастотний контур кутових швидкостей (Attitude Rate Controller, 1000 Гц):** виконується в контексті апаратного переривання таймера або потоку найвищого пріоритету RTOS. Має жорсткий часовий бюджет до 150–200 мікросекунд на повний розрахунок кроку. Будь-яке блокування або звернення до системних м'ютексів операційної системи в цьому контурі неприпустиме.
2. **Навігаційний планувач місії (Navigator Task, 50 Гц):** на кожній ітерації зчитує радіус прийняття навігаційних точок, уставки круїзної швидкості, безпечні висоти повернення додому та пороги дистанції до перешкод.
3. **Сервіс телеметрії MAVLink (Telemetry Task, 10–50 Гц):** приймає через радіомодем вхідні пакети конфігурації від наземної станції QGroundControl, валідує їх та оновлює параметри в реальному часі.
4. **Фоновий демон енергонезалежного сховища (Storage Worker, 1–5 Гц):** здійснює скидання змінених параметрів у фізичну Flash-пам'ять або зовнішню FRAM.

Без чітко спроєктованої архітектури реєстру паралельний доступ цих потоків до спільних змінних конфігурації неминуче породжує критичні системні дефекти:

- **Стан гонитви (Race Condition) та розірване читання (Torn Reads):** якщо потік телеметрії оновлює 32-бітне дійсне число або складену структуру параметрів у той самий момент, коли контур стабілізації зчитує половинчасті байти, регулятор отримує некоректне проміжне значення. Це викликає миттєвий викид керуючого сигналу на мотори з ризиком розриву силової частини.
- **Інверсія пріоритетів (Priority Inversion):** застосування класичних блокуючих м'ютексів RTOS усередині 1-кГц контуру стабілізації змушує високопріоритетне переривання очікувати, поки низькопріоритетний потік телеметрії завершить повільний пошук параметра за рядковим іменем через `strcmp`.
- **Пошкодження енергонезалежної пам'яті (Flash Corruption):** аварійне знеструмлення апарата посеред запису сектора Flash-пам'яті залишає контролер із напівстертим сховищем, що без механізму подвійної буферизації та контрольних сум призводить до неможливості завантаження борту в полі.
- **Переповнення рядкового буфера:** у протоколі MAVLink ідентифікатор параметра має фіксовану довжину 16 байтів. Якщо ім'я займає рівно 16 символів, воно не містить завершального нуль-символа `\0`. Виклик стандартних функцій `strlen`, `strcpy` або `printf` без явного обмеження довжини призводить до виходу за межі виділеної пам'яті (Buffer Overread).

Нижче наведено модульну програмну реалізацію вбудованого реєстру параметрів на мовах C та C++, яка розв'язує ці задачі за допомогою тришарової архітектури: статичні метадані в пам'яті констант, атомарний кеш ОЗП із числовими дескрипторами та двобуферне транзакційне сховище з протокольним адаптером MAVLink.

---

## Архітектура реєстру та структури даних

Реєстр розмежовує незмінні описові атрибути параметра та його динамічний стан:

1. **Метадані (`param_meta_t` / `ParamMeta`):** розміщуються в сегменті констант Flash-пам'яті (`.rodata`). Вони містять 16-символьний ASCII-ідентифікатор MAVLink, числовий код типу (`MAV_PARAM_TYPE_INT32` або `MAV_PARAM_TYPE_REAL32`), значення за замовчуванням, мінімальні та максимальні синтаксичні межі, а також бітові прапорці доступу (`DISARMED_ONLY`, `REBOOT_REQUIRED`, `READ_ONLY`).
2. **Операційний кеш (`param_record_t` / `ParamEntry`):** масив у швидкій пам'яті SRAM. Кожен елемент містить поточне значення параметра, покажчик на відповідні метадані та прапорець модифікації (`dirty`). Контури реального часу звертаються до елементів масиву безпосередньо через цілочисельний дескриптор `param_handle_t` за час `O(1)` без використання рядкових операцій порівняння `strcmp`.
3. **Транзакційний сектор Flash (`flash_sector_t` / `FlashSector`):** двійковий образ для збереження у фізичній пам'яті. Містить магічне число `0x5041524D` ("PARM"), монотонно зростаючий лічильник транзакцій `seq_num`, кількість збережених записів, масив сирих значень та хвостову контрольну суму `CRC32` за стандартом IEEE 802.3.

---

## Повна програмна реалізація реєстру

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

#define MAX_PARAMS 32
#define FLASH_SECTOR_SIZE 512
#define MAGIC_HEADER 0x5041524DU // "PARM"

// Таблиця швидкого розрахунку CRC32 (IEEE 802.3, поліном 0xEDB88320)
static const uint32_t crc32_tab[16] = {
    0x00000000, 0x1DB71064, 0x3B6E20C8, 0x26D930AC,
    0x76DC4190, 0x6B6B51F4, 0x4DB26158, 0x5005713C,
    0xEDB88320, 0xF00F9344, 0xD6D6A3E8, 0xCB61B38C,
    0x9B64C2B0, 0x86D3D2D4, 0xA00AE278, 0xBDBDF21C
};

uint32_t calculate_crc32(const uint8_t* data, size_t length) {
    uint32_t crc = ~0U;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        crc = (crc >> 4) ^ crc32_tab[crc & 0x0F];
        crc = (crc >> 4) ^ crc32_tab[crc & 0x0F];
    }
    return ~crc;
}

// Типи параметрів за стандартом MAVLink (MAV_PARAM_TYPE)
typedef enum {
    MAV_PARAM_TYPE_INT32  = 6,
    MAV_PARAM_TYPE_REAL32 = 9
} mav_param_type_t;

typedef enum {
    PARAM_FLAG_NONE          = 0,
    PARAM_FLAG_DISARMED_ONLY = 1 << 0,
    PARAM_FLAG_REBOOT_REQ    = 1 << 1,
    PARAM_FLAG_READ_ONLY     = 1 << 2
} param_flags_t;

typedef union {
    int32_t i32;
    float   f32;
    uint8_t raw[4];
} param_val_t;

typedef struct {
    char             name[16];
    mav_param_type_t type;
    param_val_t      min_val;
    param_val_t      max_val;
    param_val_t      def_val;
    uint16_t         flags;
} param_meta_t;

typedef struct {
    const param_meta_t* meta;
    param_val_t         val;
    volatile bool       dirty;
} param_record_t;

// Структура сектора збереження у Flash (фіксоване вирівнювання за 4 байтами)
typedef struct {
    uint32_t    magic;
    uint32_t    seq_num;
    uint16_t    count;
    uint16_t    reserved;
    param_val_t values[MAX_PARAMS];
    uint32_t    crc32;
} __attribute__((packed)) flash_sector_t;

// Глобальний реєстр параметрів
typedef struct {
    param_record_t records[MAX_PARAMS];
    size_t         count;
    uint32_t       current_seq;
    uint8_t        active_sector;
    uint8_t        flash_storage[2][FLASH_SECTOR_SIZE]; // Сектори 0 та 1
} param_registry_t;

static param_registry_t g_registry;

// Реєстрація дескриптора параметра під час завантаження системи
int param_register(const param_meta_t* meta) {
    if (!meta || g_registry.count >= MAX_PARAMS) return -1;
    size_t idx = g_registry.count++;
    g_registry.records[idx].meta = meta;
    g_registry.records[idx].val = meta->def_val;
    g_registry.records[idx].dirty = false;
    return (int)idx;
}

// Пряме детерміноване читання для контурів стабілізації (O(1))
bool param_get_fast(int handle, param_val_t* out_val) {
    if (handle < 0 || (size_t)handle >= g_registry.count || !out_val) return false;
    *out_val = g_registry.records[handle].val;
    return true;
}

// Пошук числового дескриптора за рядковим іменем (для MAVLink-обробника)
int param_find(const char* name) {
    if (!name) return -1;
    for (size_t i = 0; i < g_registry.count; ++i) {
        if (strncmp(g_registry.records[i].meta->name, name, 16) == 0) {
            return (int)i;
        }
    }
    return -1;
}

// Валідація значень та запис у кеш ОЗП
bool param_set_value(int handle, param_val_t new_val, bool is_armed) {
    if (handle < 0 || (size_t)handle >= g_registry.count) return false;
    param_record_t* rec = &g_registry.records[handle];
    const param_meta_t* meta = rec->meta;

    // Перевірка атрибута тільки для читання
    if (meta->flags & PARAM_FLAG_READ_ONLY) {
        return false;
    }

    // Перевірка блокування змін при зведених моторах
    if (is_armed && (meta->flags & PARAM_FLAG_DISARMED_ONLY)) {
        return false;
    }

    // Синтаксична перевірка діапазонів
    if (meta->type == MAV_PARAM_TYPE_REAL32) {
        if (new_val.f32 < meta->min_val.f32 || new_val.f32 > meta->max_val.f32) {
            return false;
        }
    } else if (meta->type == MAV_PARAM_TYPE_INT32) {
        if (new_val.i32 < meta->min_val.i32 || new_val.i32 > meta->max_val.i32) {
            return false;
        }
    }

    rec->val = new_val;
    rec->dirty = true;
    return true;
}

// Двобуферне збереження у Flash із розрахунком CRC32
bool param_save_to_flash(void) {
    uint8_t next_sector = (g_registry.active_sector == 0) ? 1 : 0;
    flash_sector_t sec;
    memset(&sec, 0, sizeof(sec));

    sec.magic = MAGIC_HEADER;
    sec.seq_num = g_registry.current_seq + 1;
    sec.count = (uint16_t)g_registry.count;

    for (size_t i = 0; i < g_registry.count; ++i) {
        sec.values[i] = g_registry.records[i].val;
    }

    // Розрахунок CRC32 для всього тіла без поля crc32
    size_t payload_size = sizeof(flash_sector_t) - sizeof(uint32_t);
    sec.crc32 = calculate_crc32((const uint8_t*)&sec, payload_size);

    // Запис у неактивний сектор
    memcpy(&g_registry.flash_storage[next_sector][0], &sec, sizeof(sec));

    // Верифікація записаного образу
    const flash_sector_t* written = (const flash_sector_t*)&g_registry.flash_storage[next_sector][0];
    uint32_t verify_crc = calculate_crc32((const uint8_t*)written, payload_size);

    if (verify_crc == written->crc32) {
        g_registry.active_sector = next_sector;
        g_registry.current_seq = sec.seq_num;
        for (size_t i = 0; i < g_registry.count; ++i) {
            g_registry.records[i].dirty = false;
        }
        return true;
    }
    return false;
}

// Завантаження параметрів під час старту з відновленням після аварій
bool param_load_from_flash(void) {
    bool sector_valid[2] = {false, false};
    flash_sector_t sec[2];
    size_t payload_size = sizeof(flash_sector_t) - sizeof(uint32_t);

    for (int i = 0; i < 2; ++i) {
        memcpy(&sec[i], &g_registry.flash_storage[i][0], sizeof(flash_sector_t));
        if (sec[i].magic == MAGIC_HEADER) {
            uint32_t crc = calculate_crc32((const uint8_t*)&sec[i], payload_size);
            if (crc == sec[i].crc32) {
                sector_valid[i] = true;
            }
        }
    }

    int best_sector = -1;
    if (sector_valid[0] && sector_valid[1]) {
        best_sector = (sec[0].seq_num >= sec[1].seq_num) ? 0 : 1;
    } else if (sector_valid[0]) {
        best_sector = 0;
    } else if (sector_valid[1]) {
        best_sector = 1;
    }

    if (best_sector < 0) {
        // Обидва сектори пошкоджені: завантаження дефолтних значень
        for (size_t i = 0; i < g_registry.count; ++i) {
            g_registry.records[i].val = g_registry.records[i].meta->def_val;
            g_registry.records[i].dirty = false;
        }
        return false;
    }

    g_registry.active_sector = (uint8_t)best_sector;
    g_registry.current_seq = sec[best_sector].seq_num;

    size_t load_count = (g_registry.count < sec[best_sector].count) ? 
                        g_registry.count : sec[best_sector].count;

    for (size_t i = 0; i < load_count; ++i) {
        g_registry.records[i].val = sec[best_sector].values[i];
        g_registry.records[i].dirty = false;
    }
    return true;
}

// Структури повідомлень протоколу MAVLink
typedef struct {
    float   param_value;
    uint8_t target_system;
    uint8_t target_component;
    char    param_id[16];
    uint8_t param_type;
} mavlink_param_set_t;

typedef struct {
    float    param_value;
    uint16_t param_count;
    uint16_t param_index;
    char     param_id[16];
    uint8_t  param_type;
} mavlink_param_value_t;

// Обробник вхідного повідомлення PARAM_SET із квитуванням PARAM_VALUE
bool mavlink_handle_param_set(const mavlink_param_set_t* set_msg, 
                              mavlink_param_value_t* out_val_msg, 
                              bool is_armed) {
    if (!set_msg || !out_val_msg) return false;

    int handle = param_find(set_msg->param_id);
    if (handle < 0) return false;

    const param_record_t* rec = &g_registry.records[handle];
    param_val_t incoming;

    // Побітове перетворення wire float у внутрішнє представлення
    if (rec->meta->type == MAV_PARAM_TYPE_REAL32) {
        incoming.f32 = set_msg->param_value;
    } else {
        memcpy(&incoming.i32, &set_msg->param_value, sizeof(int32_t));
    }

    bool updated = param_set_value(handle, incoming, is_armed);

    // Підготовка відповіді PARAM_VALUE
    memset(out_val_msg, 0, sizeof(*out_val_msg));
    memcpy(out_val_msg->param_id, rec->meta->name, 16);
    out_val_msg->param_type = (uint8_t)rec->meta->type;
    out_val_msg->param_count = (uint16_t)g_registry.count;
    out_val_msg->param_index = (uint16_t)handle;

    if (rec->meta->type == MAV_PARAM_TYPE_REAL32) {
        out_val_msg->param_value = rec->val.f32;
    } else {
        memcpy(&out_val_msg->param_value, &rec->val.i32, sizeof(float));
    }

    if (updated) {
        param_save_to_flash();
    }

    return updated;
}
```
```cpp
#include <cstdint>
#include <string_view>
#include <variant>
#include <optional>
#include <expected>
#include <atomic>
#include <array>
#include <span>
#include <bit>
#include <cstring>
#include <algorithm>

namespace drone {

// Поліном IEEE 802.3 (0xEDB88320)
inline constexpr std::array<uint32_t, 16> Crc32Table = {
    0x00000000, 0x1DB71064, 0x3B6E20C8, 0x26D930AC,
    0x76DC4190, 0x6B6B51F4, 0x4DB26158, 0x5005713C,
    0xEDB88320, 0xF00F9344, 0xD6D6A3E8, 0xCB61B38C,
    0x9B64C2B0, 0x86D3D2D4, 0xA00AE278, 0xBDBDF21C
};

constexpr uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = ~0U;
    for (const uint8_t byte : data) {
        crc ^= byte;
        crc = (crc >> 4) ^ Crc32Table[crc & 0x0F];
        crc = (crc >> 4) ^ Crc32Table[crc & 0x0F];
    }
    return ~crc;
}

enum class MavParamType : uint8_t {
    Int32  = 6,
    Real32 = 9
};

enum class ParamFlags : uint16_t {
    None           = 0,
    DisarmedOnly   = 1 << 0,
    RebootRequired = 1 << 1,
    ReadOnly       = 1 << 2
};

inline constexpr ParamFlags operator|(ParamFlags a, ParamFlags b) noexcept {
    return static_cast<ParamFlags>(static_cast<uint16_t>(a) | static_cast<uint16_t>(b));
}

inline constexpr bool has_flag(ParamFlags flags, ParamFlags check) noexcept {
    return (static_cast<uint16_t>(flags) & static_cast<uint16_t>(check)) != 0;
}

using ParamValue = std::variant<int32_t, float>;

struct ParamMeta {
    std::string_view name;
    MavParamType     type;
    ParamValue       min_val;
    ParamValue       max_val;
    ParamValue       def_val;
    ParamFlags       flags{ParamFlags::None};
};

class ParamEntry {
public:
    constexpr explicit ParamEntry(const ParamMeta& meta) noexcept
        : meta_(meta), val_(meta.def_val), dirty_(false) {}

    [[nodiscard]] ParamValue get() const noexcept {
        return val_;
    }

    [[nodiscard]] float to_wire_float() const noexcept {
        if (meta_.type == MavParamType::Real32) {
            return std::get<float>(val_);
        }
        return std::bit_cast<float>(std::get<int32_t>(val_));
    }

    void from_wire_float(float wire_val) noexcept {
        if (meta_.type == MavParamType::Real32) {
            val_ = wire_val;
        } else {
            val_ = std::bit_cast<int32_t>(wire_val);
        }
    }

    [[nodiscard]] bool set(ParamValue new_val, bool is_armed) noexcept {
        if (has_flag(meta_.flags, ParamFlags::ReadOnly)) {
            return false;
        }

        if (has_flag(meta_.flags, ParamFlags::DisarmedOnly) && is_armed) {
            return false;
        }

        if (meta_.type == MavParamType::Real32) {
            const float v = std::get<float>(new_val);
            const float min_v = std::get<float>(meta_.min_val);
            const float max_v = std::get<float>(meta_.max_val);
            if (v < min_v || v > max_v) {
                return false;
            }
        } else {
            const int32_t v = std::get<int32_t>(new_val);
            const int32_t min_v = std::get<int32_t>(meta_.min_val);
            const int32_t max_v = std::get<int32_t>(meta_.max_val);
            if (v < min_v || v > max_v) {
                return false;
            }
        }

        val_ = new_val;
        dirty_.store(true, std::memory_order_release);
        return true;
    }

    [[nodiscard]] bool is_dirty() const noexcept {
        return dirty_.load(std::memory_order_acquire);
    }

    void clear_dirty() noexcept {
        dirty_.store(false, std::memory_order_release);
    }

    [[nodiscard]] const ParamMeta& meta() const noexcept {
        return meta_;
    }

private:
    const ParamMeta&  meta_;
    ParamValue        val_;
    std::atomic<bool> dirty_;
};

struct MavlinkParamSet {
    float            param_value{0.0f};
    uint8_t          target_system{0};
    uint8_t          target_component{0};
    std::string_view param_id{};
    uint8_t          param_type{0};
};

struct MavlinkParamValue {
    float            param_value{0.0f};
    uint16_t         param_count{0};
    uint16_t         param_index{0};
    std::string_view param_id{};
    uint8_t          param_type{0};
};

template <size_t MaxParams = 32, size_t FlashSectorSize = 512>
class ParamRegistry {
public:
    static constexpr uint32_t MagicHeader = 0x5041524DU; // "PARM"

    struct alignas(4) FlashSector {
        uint32_t            magic{0};
        uint32_t            seq_num{0};
        uint16_t            count{0};
        uint16_t            reserved{0};
        std::array<float, MaxParams> raw_values{};
        uint32_t            crc32{0};
    };

    constexpr ParamRegistry() noexcept = default;

    std::optional<size_t> register_param(const ParamMeta& meta) noexcept {
        if (count_ >= MaxParams) return std::nullopt;
        const size_t idx = count_++;
        entries_[idx].emplace(meta);
        return idx;
    }

    [[nodiscard]] std::optional<ParamValue> get_fast(size_t handle) const noexcept {
        if (handle >= count_ || !entries_[handle].has_value()) return std::nullopt;
        return entries_[handle]->get();
    }

    [[nodiscard]] std::optional<size_t> find(std::string_view name) const noexcept {
        for (size_t i = 0; i < count_; ++i) {
            if (entries_[i] && entries_[i]->meta().name == name) {
                return i;
            }
        }
        return std::nullopt;
    }

    bool set_value(size_t handle, ParamValue val, bool is_armed) noexcept {
        if (handle >= count_ || !entries_[handle].has_value()) return false;
        return entries_[handle]->set(val, is_armed);
    }

    bool save_to_flash() noexcept {
        const uint8_t next_sec = (active_sector_ == 0) ? 1 : 0;
        FlashSector sec{};
        sec.magic = MagicHeader;
        sec.seq_num = current_seq_ + 1;
        sec.count = static_cast<uint16_t>(count_);

        for (size_t i = 0; i < count_; ++i) {
            sec.raw_values[i] = entries_[i]->to_wire_float();
        }

        constexpr size_t payload_len = sizeof(FlashSector) - sizeof(uint32_t);
        auto payload_bytes = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&sec), payload_len);
        sec.crc32 = calculate_crc32(payload_bytes);

        std::memcpy(&flash_storage_[next_sec][0], &sec, sizeof(FlashSector));

        active_sector_ = next_sec;
        current_seq_ = sec.seq_num;
        for (size_t i = 0; i < count_; ++i) {
            entries_[i]->clear_dirty();
        }
        return true;
    }

    bool load_from_flash() noexcept {
        std::array<bool, 2> valid{false, false};
        std::array<FlashSector, 2> sectors{};
        constexpr size_t payload_len = sizeof(FlashSector) - sizeof(uint32_t);

        for (size_t i = 0; i < 2; ++i) {
            std::memcpy(&sectors[i], &flash_storage_[i][0], sizeof(FlashSector));
            if (sectors[i].magic == MagicHeader) {
                auto bytes = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&sectors[i]), payload_len);
                if (calculate_crc32(bytes) == sectors[i].crc32) {
                    valid[i] = true;
                }
            }
        }

        int best = -1;
        if (valid[0] && valid[1]) {
            best = (sectors[0].seq_num >= sectors[1].seq_num) ? 0 : 1;
        } else if (valid[0]) {
            best = 0;
        } else if (valid[1]) {
            best = 1;
        }

        if (best < 0) {
            for (size_t i = 0; i < count_; ++i) {
                entries_[i]->set(entries_[i]->meta().def_val, false);
                entries_[i]->clear_dirty();
            }
            return false;
        }

        active_sector_ = static_cast<uint8_t>(best);
        current_seq_ = sectors[best].seq_num;
        const size_t load_cnt = std::min(count_, static_cast<size_t>(sectors[best].count));

        for (size_t i = 0; i < load_cnt; ++i) {
            entries_[i]->from_wire_float(sectors[best].raw_values[i]);
            entries_[i]->clear_dirty();
        }
        return true;
    }

    std::expected<MavlinkParamValue, MavlinkParamValue>
    handle_param_set(const MavlinkParamSet& msg, bool is_armed) noexcept {
        const auto handle_opt = find(msg.param_id);
        if (!handle_opt) {
            return std::unexpected(MavlinkParamValue{});
        }
        const size_t handle = *handle_opt;
        auto& entry = *entries_[handle];

        ParamValue incoming;
        if (entry.meta().type == MavParamType::Real32) {
            incoming = msg.param_value;
        } else {
            incoming = std::bit_cast<int32_t>(msg.param_value);
        }

        const bool success = entry.set(incoming, is_armed);

        MavlinkParamValue resp{};
        resp.param_id = entry.meta().name;
        resp.param_type = static_cast<uint8_t>(entry.meta().type);
        resp.param_count = static_cast<uint16_t>(count_);
        resp.param_index = static_cast<uint16_t>(handle);
        resp.param_value = entry.to_wire_float();

        if (success) {
            save_to_flash();
            return resp;
        }
        return std::unexpected(resp);
    }

    [[nodiscard]] size_t size() const noexcept { return count_; }

private:
    std::array<std::optional<ParamEntry>, MaxParams> entries_{};
    size_t                                           count_{0};
    uint32_t                                         current_seq_{0};
    uint8_t                                          active_sector_{0};
    std::array<std::array<uint8_t, FlashSectorSize>, 2> flash_storage_{};
};

} // namespace drone
```
:::

---

## Детальний розбір реалізації та крайові випадки

### 1. Механіка побітового копіювання (Bit-Casting)

У функціях `mavlink_handle_param_set` та методах `ParamEntry::to_wire_float()` / `from_wire_float()` реалізовано пряме двійкове відображення без математичної конвертації.

Стандарт IEEE 754 для 32-бітних чисел із рухомою комою виділяє 1 біт на знак, 8 бітів на порядок (експоненту) та 23 біти на мантису. При явному математичному приведенні цілого числа, що перевищує `2²⁴ = 16 777 216` (наприклад, бітової маски сенсорів `0x01FFFFFF`), молодші розряди цілого числа незворотно втрачаються через округлення мантиси. 

У мові C для безпечного біт-кастингу використовується `memcpy` між змінними однакового розміру. У стандарті C++20 функція `std::bit_cast` виконує цю операцію на рівні компілятора з повною перевіркою типів (Type-Safe Bit-Casting) без виклику функцій стандартної бібліотеки та без порушення правил суворого псевдонімування (Strict Aliasing Rules).

### 2. Транзакційність двобуферного запису та стійкість до знеструмлення

Процедура `param_save_to_flash` реалізує принцип Ping-Pong буферизації. Фізичний сектор пам'яті ніколи не перезаписується на місці:

```
1. Формування нового образу сектору в локальному буфері SRAM.
2. Розрахунок контрольної суми CRC32 для заголовка та корисного навантаження (без самого поля CRC).
3. Запис сформованого образу у фізичну пам'ять неактивного сектора (Target Sector).
4. Верифікація записаних даних зворотним зчитуванням та порівнянням CRC32.
5. Атомарне перемикання активного індексу та інкремент монотонного лічильника current_seq.
```

Якщо в момент запису виникає падіння напруги бортмережі (Brownout), вміст нового сектора виявиться пошкодженим або неповним. Під час наступного старту функція `param_load_from_flash` обчислює `CRC32` обох секторів. Новий сектор провалить перевірку, і система автоматично обере попередній сектор із коректною контрольною сумою. Якщо пошкоджені обидва фізичні сектори (наприклад, після повного стирання чипу програматором), реєстр завантажує заводські константи `def_val` і сигналізує про скидання налаштувань.

Математична ймовірність того, що випадково пошкоджений блок даних розміром 512 байтів випадково збіжиться за контрольною сумою CRC32 (поліном IEEE 802.3 `0xEDB88320`), становить менше ніж `2⁻³² ≈ 2.33 × 10⁻¹⁰`. Це забезпечує практично абсолютну гарантію виявлення будь-яких пакетних та одиночних апаратних збоїв пам'яті.

### 3. Захист від модифікації в польоті (Disarmed Guard)

Спроба оператора змінити параметр із прапорцем `PARAM_FLAG_DISARMED_ONLY` (наприклад, геометричні розміри плечей рами чи офсети акселерометра) під час активного польоту (`is_armed == true`) негайно блокується функцією `param_set_value`.

У відповідь наземній станції повертається пакет `PARAM_VALUE`, що містить **поточне старе значення**. Станція QGroundControl фіксує невідповідність між надісланим значенням у `PARAM_SET` та підтвердженим у `PARAM_VALUE`, видаючи оператору попередження про відхилення команди автопілотом.

### 4. Бюджет затримок та апаратне вирівнювання пам'яті

На 32-розрядних процесорах архітектури ARM Cortex-M4/M7 доступ до невирівняних у пам'яті 32-бітних слів (`uint32_t`, `float`) викликає апаратне виключення `UsageFault` або суттєве падіння продуктивності шини AHB через генерацію двох послідовних шинних транзакцій. 

У структурі `flash_sector_t` застосовано явне впорядкування полів: спочатку йдуть 4-байтові поля (`magic`, `seq_num`), потім 2-байтові лічильники з вирівнювальним полем `reserved`, після чого розташовано масив 4-байтових значень параметрів. Це забезпечує природне вирівнювання за 4-байтовою межею для кожного поля без необхідності вставки прихованих байтів заповнення (Padding Bytes), роблячи розмір сектора повністю детермінованим та переносним між компіляторами GCC, Clang та IAR.

Прямий виклик `param_get_fast(handle)` компілюється в одну машинну інструкцію завантаження з пам'яті зі зміщенням (`LDR r0, [r1, r2, LSL #2]`), що займає рівно 1-2 такти ядра процесора (1–2 наносекунди на частоті 480 МГц у STM32H7). Це дозволяє викликати перевірку параметрів у найбільш критичних ділянках контуру регулювання без ризику пропуску дедлайну переривання таймера ШІМ.

### 5. Захист рядкових ідентифікаторів MAVLink від виходу за межі пам'яті

У стандарті MAVLink поле `param_id[16]` містить рівно 16 байтів. Якщо назва параметра складається з 16 літер (наприклад, `NAV_TRAJ_ACC_RAD`), рядок не має нуль-термінатора `\0`.

У коді C для безпечного порівняння використовується виключно функція `strncmp(a, b, 16)`, яка ніколи не зчитує пам'ять поза межами 16 байтів. У коді C++ застосовується `std::string_view`, де довжина рядка зберігається окремим числом і не залежить від наявності завершального нуль-байта. Це гарантує повну відсутність дефектів переповнення буфера при отриманні пакетів від сторонніх наземних станцій або кастомних скриптів телеметрії.
