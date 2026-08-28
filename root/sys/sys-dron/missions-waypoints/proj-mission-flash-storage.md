# ⚙️ Дводіапазонний транзакційний драйвер сховища місій у FRAM та Flash

Збереження польотного завдання в енергонезалежній пам'яті польотного контролера вимагає бездоганного захисту від апаратного пошкодження даних під час раптового зникнення живлення або перезавантаження бортового процесора. Якщо запис нової місії виконується безпосередньо поверх активного списку точок, знеструмлення в середині циклу запису перетворить файл місії на напівстертий двійковий масив. При наступному старті автопілот спробує злетіти за спотвореними координатами або зіткнеться з аварійним падінням у режим зависання.

Для гарантування повної відмовостійкості використовується архітектура подвійного буфера. Енергонезалежна пам'ять розділяється на два незалежних фізичних слоти однакового розміру та окремий сектор однобайтового покажчика активного слота.

## Порівняння фізичних носіїв: Flash проти FRAM

Польотні контролери використовують два основних типи незалежної пам'яті, які принципово відрізняються часовими характеристиками, фізикою запису та ресурсом циклів перезапису.

### Зовнішня SPI/QSPI NOR Flash

Мікросхеми послідовної NOR Flash-пам'яті широко застосовуються завдяки низькій вартості та великому обсягу. Проте вони мають жорсткі фізичні обмеження при записі даних:

Перед записом нових байтів необхідно обов'язково виконати операцію стирання сектора розміром 4096 байтів. Стирання переводить усі біти сектора у стан логічної одиниці. Подальший запис сторінками по 256 байтів здатний лише змінювати окремі біти з одиниці в нуль, але не навпаки.

Стирання сектора є тривалим апаратним процесом, який триває від 30 до 200 мілісекунд через необхідність накопичення високої напруги на внутрішніх зарядових помпах кристала. Під час стирання чіп переходить у стан зайнятості та повністю блокує відповіді на запити читання. Якщо Flash-пам'ять підключена до спільної шини SPI з критичним інерційним давачем кутових швидкостей та прискорень, тривале блокування шини призводить до зриву циклу оцінювача просторової орієнтації.

Крім того, ресурс NOR Flash обмежений 100 000 циклами стирання на сектор. Часте оновлення місій або збереження активної точки під час польоту може призвести до деградації комірок пам'яті.

### Сегнетоелектрична пам'ять FRAM

Сегнетоелектрична пам'ять кардинально відрізняється від кремнієвих накопичувачів із плаваючим затвором:

Збереження стану базується на зміні просторової поляризації кристалічної решітки цирконату-титанату свинцю під дією електричного поля. Пам'ять не потребує попереднього стирання секторів та підтримує довільний побайтовий перезапис без створення проміжних сторінкових буферів.

Запис відбувається на повній тактовій частоті шини SPI (до 40 МГц) з нульовою затримкою очікування шини. Це дозволяє безпечно записувати поточний прогрес місії безпосередньо всередині високочастотних навігаційних переривань.

Ресурс пам'яті становить сто трильйонів циклів перезапису, що повністю усуває проблему апаратного зношування носія протягом усього терміну експлуатації безпілотного апарата.

## Архітектура подвійної буферизації

Незалежно від фізичного типу пам'яті, логічний драйвер зобов'язаний розглядати операцію запису як потенційно переривану в будь-який момент часу через вібраційне відключення акумулятора, просідання бортової напруги або спрацьовування сторожового таймера процесора.

Для захисту даних пам'ять розбивається на три ізольовані зони:

1. **Сектор метаданих (Active Slot Pointer):** містить 1 байт індексу активного слота (`0x01` для слота A, `0x02` для слота B) та власну контрольну суму.
2. **Слот A (Slot A):** починається з 32-байтового заголовка (магічне число `0x4D495353`, лічильник точок `count`, індекс активної точки `current_seq`, контрольна сума CRC-16-CCITT усього масиву точок) і містить неперервний масив упакованих структур `mission_item_storage_t`.
3. **Слот B (Slot B):** точна дзеркальна копія слота A, розташована за фіксованим зсувом адреси.

```text
Зсув адреси   Розмір      Зміст блоку пам'яті
------------------------------------------------------------------------------------------------
0x0000        4096 байтів Сектор метаданих покажчика активного слота (Active Slot Pointer)
0x1000        61440 байт  Слот A: Заголовок (32B) + Масив точок (до 1500 точок по 38 байтів)
0x10000       61440 байт  Слот B: Заголовок (32B) + Масив точок (до 1500 точок по 38 байтів)
```

## Алгоритм транзакційного запису та аварійного відновлення

Під час завантаження нової місії драйвер виконує строго детерміновану послідовність кроків:

1. **Вибір цільового слота:** Драйвер зчитує покажчик активного слота. Якщо активним є Слот A, новий запис спрямовується в тіньовий Слот B.
2. **Підготовка носія:** Якщо використовується Flash-пам'ять, драйвер стирає необхідну кількість секторів Слота B.
3. **Потоковий запис точок:** У міру надходження пакетів `MISSION_ITEM_INT` від наземної станції точки записуються в тіньовий слот, а паралельний акумулятор оновлює розрахунок контрольної суми CRC-16.
4. **Фіксація заголовка слота:** Після прийому останньої точки формується структура `mission_storage_header_t` із розрахованим CRC-16 і записується на початок Слота B.
5. **Верифікація зчитуванням (Read-Back Check):** Драйвер зчитує весь масив Слота B, повторно розраховує CRC-16 і порівнює його зі значенням у заголовку. Якщо виявлено невідповідність (апаратний збій Flash), транзакція відхиляється, а активний слот не перемикається.
6. **Атомарний крок перемикання:** Драйвер стирає сектор метаданих і записує туди значення `0x02`. З цієї миті активним для навігатора стає Слот B.

Якщо живлення зникає на кроках 1–5, у секторі метаданих залишається значення `0x01`. Під час повторного запуску автопілот відкриє непошкоджений Слот A, а недописані дані в Слот B ігноруються.

## Програмна реалізація драйвера на C та C++

Наведений код реалізує повнофункціональний драйвер дводіапазонного сховища місій з апаратними абстракціями читання/запису та верифікацією CRC-16.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MISSION_MAGIC           0x4D495353u // 'MISS'
#define STORAGE_SLOT_A_OFFSET   0x1000u
#define STORAGE_SLOT_B_OFFSET   0x10000u
#define MAX_MISSION_ITEMS       1500u

typedef struct __attribute__((packed)) {
    float param1;
    float param2;
    float param3;
    float param4;
    int32_t x;
    int32_t y;
    float z;
    uint16_t seq;
    uint16_t command;
    uint8_t frame;
    uint8_t current;
    uint8_t autocontinue;
    uint8_t mission_type;
} mission_item_storage_t;

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint16_t version;
    uint16_t count;
    uint16_t current_seq;
    uint16_t crc16;
    uint8_t reserved[20];
} mission_storage_header_t;

typedef struct {
    uint8_t active_slot; // 1 = Slot A, 2 = Slot B
    uint16_t cached_count;
    uint16_t current_seq;
    bool is_valid;
} mission_storage_driver_t;

// Апаратні функції читання/запису Flash/FRAM
extern bool hal_flash_read(uint32_t addr, void *buf, size_t len);
extern bool hal_flash_write(uint32_t addr, const void *buf, size_t len);
extern bool hal_flash_erase_sector(uint32_t addr);

// Табличний розрахунок CRC-16-CCITT (поліном 0x1021, ініціалізація 0xFFFF)
uint16_t calculate_crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t j = 0; j < 8; ++j) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

// Ініціалізація та пошук валідного слота при старті
bool mission_storage_init(mission_storage_driver_t *drv) {
    drv->active_slot = 0;
    drv->cached_count = 0;
    drv->current_seq = 0;
    drv->is_valid = false;

    uint8_t slot_ptr = 0;
    if (!hal_flash_read(0x0000, &slot_ptr, 1)) {
        return false;
    }

    uint8_t preferred_slot = (slot_ptr == 2) ? 2 : 1;
    uint8_t fallback_slot = (preferred_slot == 1) ? 2 : 1;

    uint8_t slots[2] = {preferred_slot, fallback_slot};
    for (int i = 0; i < 2; ++i) {
        uint8_t s = slots[i];
        uint32_t offset = (s == 1) ? STORAGE_SLOT_A_OFFSET : STORAGE_SLOT_B_OFFSET;
        
        mission_storage_header_t hdr;
        if (!hal_flash_read(offset, &hdr, sizeof(hdr))) {
            continue;
        }

        if (hdr.magic != MISSION_MAGIC || hdr.count > MAX_MISSION_ITEMS) {
            continue;
        }

        // Перевірка CRC усього масиву точок
        uint16_t calculated_crc = 0xFFFF;
        bool read_ok = true;
        mission_item_storage_t item;
        for (uint16_t j = 0; j < hdr.count; ++j) {
            uint32_t item_addr = offset + sizeof(mission_storage_header_t) + j * sizeof(mission_item_storage_t);
            if (!hal_flash_read(item_addr, &item, sizeof(item))) {
                read_ok = false;
                break;
            }
            calculated_crc = calculate_crc16((const uint8_t*)&item, sizeof(item));
        }

        if (read_ok && calculated_crc == hdr.crc16) {
            drv->active_slot = s;
            drv->cached_count = hdr.count;
            drv->current_seq = hdr.current_seq;
            drv->is_valid = true;
            return true;
        }
    }

    return false; // Обидва слоти пошкоджені або порожні
}

// Запис нового списку місії в тіньовий слот з атомарним перемиканням
bool mission_storage_commit(mission_storage_driver_t *drv, const mission_item_storage_t *items, uint16_t count) {
    if (count > MAX_MISSION_ITEMS) {
        return false;
    }

    uint8_t target_slot = (drv->active_slot == 1) ? 2 : 1;
    uint32_t target_offset = (target_slot == 1) ? STORAGE_SLOT_A_OFFSET : STORAGE_SLOT_B_OFFSET;

    // Стираємо сектори цільового слота
    hal_flash_erase_sector(target_offset);

    // Розрахунок контрольної суми та послідовний запис точок
    uint16_t crc = 0xFFFF;
    for (uint16_t i = 0; i < count; ++i) {
        crc = calculate_crc16((const uint8_t*)&items[i], sizeof(mission_item_storage_t));
        uint32_t item_addr = target_offset + sizeof(mission_storage_header_t) + i * sizeof(mission_item_storage_t);
        if (!hal_flash_write(item_addr, &items[i], sizeof(mission_item_storage_t))) {
            return false;
        }
    }

    // Запис заголовка цільового слота
    mission_storage_header_t hdr = {
        .magic = MISSION_MAGIC,
        .version = 1,
        .count = count,
        .current_seq = 0,
        .crc16 = crc,
        .reserved = {0}
    };

    if (!hal_flash_write(target_offset, &hdr, sizeof(hdr))) {
        return false;
    }

    // Атомарне оновлення покажчика активного слота
    if (!hal_flash_erase_sector(0x0000) || !hal_flash_write(0x0000, &target_slot, 1)) {
        return false;
    }

    drv->active_slot = target_slot;
    drv->cached_count = count;
    drv->current_seq = 0;
    drv->is_valid = true;
    return true;
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <expected>
#include <optional>
#include <cstring>

#pragma pack(push, 1)
struct MissionItemStorage {
    float param1{0.0f};
    float param2{0.0f};
    float param3{0.0f};
    float param4{0.0f};
    int32_t x{0};
    int32_t y{0};
    float z{0.0f};
    uint16_t seq{0};
    uint16_t command{16};
    uint8_t frame{3};
    uint8_t current{0};
    uint8_t autocontinue{1};
    uint8_t mission_type{0};
};

struct MissionStorageHeader {
    uint32_t magic{0x4D495353}; // 'MISS'
    uint16_t version{1};
    uint16_t count{0};
    uint16_t current_seq{0};
    uint16_t crc16{0xFFFF};
    std::array<uint8_t, 20> reserved{};
};
#pragma pack(pop)

static_assert(sizeof(MissionStorageHeader) == 32, "Header must strictly be 32 bytes");

enum class StorageError : uint8_t {
    ReadFailed,
    WriteFailed,
    EraseFailed,
    InvalidMagic,
    CrcMismatch,
    CapacityExceeded,
    CorruptedSlots
};

class FlashHal {
public:
    virtual ~FlashHal() = default;
    [[nodiscard]] virtual bool read(uint32_t addr, std::span<uint8_t> buffer) = 0;
    [[nodiscard]] virtual bool write(uint32_t addr, std::span<const uint8_t> data) = 0;
    [[nodiscard]] virtual bool erase_sector(uint32_t addr) = 0;
};

class TransactionalMissionStorage {
public:
    static constexpr uint32_t POINTER_OFFSET = 0x0000;
    static constexpr uint32_t SLOT_A_OFFSET  = 0x1000;
    static constexpr uint32_t SLOT_B_OFFSET  = 0x10000;
    static constexpr uint16_t MAX_ITEMS      = 1500;

    explicit TransactionalMissionStorage(FlashHal& hal) : m_hal(hal) {}

    [[nodiscard]] std::expected<void, StorageError> init() noexcept {
        uint8_t slot_ptr{1};
        std::array<uint8_t, 1> ptr_buf{};
        if (m_hal.read(POINTER_OFFSET, ptr_buf)) {
            slot_ptr = (ptr_buf[0] == 2) ? 2 : 1;
        }

        const std::array<uint8_t, 2> trial_slots = {
            slot_ptr, 
            static_cast<uint8_t>(slot_ptr == 1 ? 2 : 1)
        };

        for (uint8_t s : trial_slots) {
            uint32_t offset = (s == 1) ? SLOT_A_OFFSET : SLOT_B_OFFSET;
            MissionStorageHeader hdr{};
            
            auto hdr_span = std::as_writable_bytes(std::span{&hdr, 1});
            if (!m_hal.read(offset, hdr_span)) {
                continue;
            }

            if (hdr.magic != 0x4D495353 || hdr.count > MAX_ITEMS) {
                continue;
            }

            // Перевірка цілісності CRC
            uint16_t calculated_crc = 0xFFFF;
            bool read_success = true;
            MissionItemStorage item{};
            auto item_span = std::as_writable_bytes(std::span{&item, 1});

            for (uint16_t i = 0; i < hdr.count; ++i) {
                uint32_t addr = offset + sizeof(MissionStorageHeader) + i * sizeof(MissionItemStorage);
                if (!m_hal.read(addr, item_span)) {
                    read_success = false;
                    break;
                }
                calculated_crc = compute_crc16(item_span, calculated_crc);
            }

            if (read_success && calculated_crc == hdr.crc16) {
                m_active_slot = s;
                m_count = hdr.count;
                m_current_seq = hdr.current_seq;
                m_is_valid = true;
                return {};
            }
        }

        return std::unexpected(StorageError::CorruptedSlots);
    }

    [[nodiscard]] std::expected<void, StorageError> commit(std::span<const MissionItemStorage> items) noexcept {
        if (items.size() > MAX_ITEMS) {
            return std::unexpected(StorageError::CapacityExceeded);
        }

        uint8_t target_slot = (m_active_slot == 1) ? 2 : 1;
        uint32_t target_offset = (target_slot == 1) ? SLOT_A_OFFSET : SLOT_B_OFFSET;

        if (!m_hal.erase_sector(target_offset)) {
            return std::unexpected(StorageError::EraseFailed);
        }

        uint16_t crc = 0xFFFF;
        for (size_t i = 0; i < items.size(); ++i) {
            auto item_bytes = std::as_bytes(std::span{&items[i], 1});
            crc = compute_crc16(item_bytes, crc);

            uint32_t addr = target_offset + sizeof(MissionStorageHeader) + i * sizeof(MissionItemStorage);
            if (!m_hal.write(addr, item_bytes)) {
                return std::unexpected(StorageError::WriteFailed);
            }
        }

        MissionStorageHeader hdr{
            .magic = 0x4D495353,
            .version = 1,
            .count = static_cast<uint16_t>(items.size()),
            .current_seq = 0,
            .crc16 = crc
        };

        auto hdr_bytes = std::as_bytes(std::span{&hdr, 1});
        if (!m_hal.write(target_offset, hdr_bytes)) {
            return std::unexpected(StorageError::WriteFailed);
        }

        // Атомарне оновлення покажчика активного слота
        std::array<uint8_t, 1> ptr_data{target_slot};
        if (!m_hal.erase_sector(POINTER_OFFSET) || !m_hal.write(POINTER_OFFSET, ptr_data)) {
            return std::unexpected(StorageError::WriteFailed);
        }

        m_active_slot = target_slot;
        m_count = static_cast<uint16_t>(items.size());
        m_current_seq = 0;
        m_is_valid = true;
        return {};
    }

    [[nodiscard]] uint16_t count() const noexcept { return m_count; }
    [[nodiscard]] uint16_t current_seq() const noexcept { return m_current_seq; }
    [[nodiscard]] bool is_valid() const noexcept { return m_is_valid; }

private:
    static uint16_t compute_crc16(std::span<const uint8_t> data, uint16_t seed = 0xFFFF) noexcept {
        uint16_t crc = seed;
        for (uint8_t byte : data) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (uint8_t j = 0; j < 8; ++j) {
                if (crc & 0x8000) {
                    crc = (crc << 1) ^ 0x1021;
                } else {
                    crc <<= 1;
                }
            }
        }
        return crc;
    }

    FlashHal& m_hal;
    uint8_t m_active_slot{1};
    uint16_t m_count{0};
    uint16_t m_current_seq{0};
    bool m_is_valid{false};
};
```
:::
