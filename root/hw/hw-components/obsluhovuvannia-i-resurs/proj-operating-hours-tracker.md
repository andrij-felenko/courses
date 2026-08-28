# ⚙️ Модуль обліку мотогодин і ресурсу компонентів у Flash-пам'яті

Цей проект реалізує модуль вбудованого програмного забезпечення для бортового мікроконтролера, який веде незмінний облік напрацювання апарата: загальних мотогодин під навантаженням, інтегрального споживання струму (ампер-годин), кількості вмикань живлення та циклів підключення силових роз'ємів. Збереження метрик у енергонезалежній пам'яті (Flash/EEPROM) організовано за принципом циклічного кільцевого буфера з вирівнюванням зносу (*wear-leveling*) та контролем цілісності CRC16.

## Фізичні обмеження енергонезалежної пам'яті вбудованих систем

Мікроконтролери безпілотних і автономних систем (сімейств STM32, ESP32, RP2040 або nRF52) використовують для збереження налаштувань і системних журналів вбудовану або зовнішню Flash-пам'ять із послідовним інтерфейсом SPI/QSPI (типу W25Qxx). Фізична структура комірок NOR Flash накладає жорсткі апаратні обмеження, зумовлені фізикою напівпровідникового плаваючого затвора:

1. **Асиметрія запису та стирання:** Flash-пам'ять дозволяє довільно переводити окремі біти зі стану логічної одиниці в нуль (`1 → 0`) на рівні окремих байтів або 32-бітних слів за час програмування сторінки `t_prog ≈ 0.7 ... 1.5 мс`. Проте зворотний перехід (`0 → 1`) неможливий без операції високовольтного стирання всього мінімального фізичного сектора (зазвичай 4096 байтів), яка триває `t_SE ≈ 45 ... 100 мс`.
2. **Обмежений ресурс циклів перепрограмування (Endurance):** Кожне стирання сектора супроводжується подачею напруги 15–20 В на тунельний діелектрик плаваючого затвора, що накопичує пастки заряду в тонкому шарі діоксиду кремнію `SiO₂`. Гарантований ресурс більшості мікросхем становить від `10 000` (для дешевих кристалів) до `100 000` циклів на сектор.

Якщо мікропрограма зберігатиме напрацьовані мотогодини простим оновленням фіксованої структури за однією незмінною адресою Flash щохвилини, сектор гарантовано вичерпає свій ресурс і почне повертати помилки запису вже через `100 000 хвилин ≈ 1 666 годин` (менше 70 діб сумарної роботи).

## Архітектура циклічного журналу без попереднього стирання (Append-Only Ring)

Щоб розподілити навантаження перепрограмування по всьому масиву комірок та усунути постійні високовольтні стреси діелектрика, модуль реалізує архітектуру **посекторного кільцевого журналу записів фіксованої довжини (Append-Only Ring Buffer)**:

```
+-----------------------------------------------------------------------------------+
|                           СЕКТОР FLASH (4096 БАЙТІВ)                              |
+-------------------+-------------------+-------------------+-----+-----------------+
| Слот #0 (32 байти)| Слот #1 (32 байти)| Слот #2 (32 байти)| ... | Слот #127 (32Б) |
| Seq=101, CRC=0x4A | Seq=102, CRC=0x9B | Seq=103, CRC=0x1F | ... | 0xFF...0xFF     |
+-------------------+-------------------+-------------------+-----+-----------------+
  ^ Найстаріший                                               ^     ^ Вільний слот
                                                     Поточний активний
```

### Алгоритм роботи:

1. Виділяється один фізичний сектор розміром 4096 байтів.
2. Розмір одиничного запису стану ресурсу (`LifeRecord`) оптимізовано до рівно 32 байтів. Таким чином, один сектор вміщує рівно `4096 / 32 = 128` слотів запису.
3. При кожному збереженні мікроконтролер записує 32 байти у **наступний вільний слот** (де всі байти мають стан `0xFF`), збільшуючи монотонний номер послідовності `sequence_id`. Операція стирання сектора при цьому **не викликається**.
4. Стирання всього сектора здійснюється лише один раз на 128 операцій збереження — коли останній слот #127 заповнюється даними.
5. Математичний виграш ресурсу: за збереження стану раз на 5 хвилин польоту один сектор витримує `128 · 100 000 = 12 800 000` записів. Це забезпечує понад `1 066 000` годин (понад 120 років) безперервної експлуатації чіпа пам'яті.

## Стійкість до раптового знеструмлення (Power-Loss Recovery)

У безпілотному апараті відключення ходової батареї або аварійне скидання живлення може статися в будь-яку мілісекунду, зокрема прямо посеред виконання команди запису сторінки Flash.

Для забезпечення абсолютної цілісності даних модуль застосовує двоступеневу перевірку:
- Кожен запис містить унікальну магічну сигнатуру `magic = 0xA55A` у перших двох байтах.
- Останні два байти структури містять контрольну суму `CRC16-CCITT` (поліном `0x1021`), розраховану по всіх попередніх 30 байтах.
- Під час ініціалізації при старті системи скануються всі 128 слотів сектора. Якщо запис має пошкоджену контрольну суму (що свідчить про обрив живлення під час запису або спонтанний бітовий витік заряду в зношеній комірці), він ігнорується, а система автоматично відновлює стан за попереднім валідним слотом.

### Робота з апаратним детектором просідання напруги (Brownout Detector)

Для критично важливих вузлів запис у Flash ініціюється не лише за таймером, а й за апаратним перериванням детектора напруги живлення `BOD` (Brownout Detector). 

Коли напруга живлення мікроконтролера падає нижче порогу 2.9 В, переривання високого пріоритету має близько `1 ... 3 мс` часу до повного знеструмлення за рахунок енергії, накопиченої в буферних керамічних конденсаторах шини 3.3 В:

```
t_hold = (C_bus · ΔV) / I_mcu
```

При сумарній ємності шини `C_bus = 47 мкФ`, перепаді напруги `ΔV = 2.9 В - 2.4 В = 0.5 В` та споживанні мікроконтролера `I_mcu = 15 мА`:

```
t_hold = (47 · 10⁻⁶ Ф · 0.5 В) / 0.015 А
       = 0.0000235 / 0.015
       = 1.56 мс
```

Цього інтервалу `1.56 мс` цілком достатньо для завершення запису 32-байтної структури по шині SPI на частоті 20 МГц (що триває менше 0.8 мс разом із затримкою програмування буфера кристала), що гарантує фіксацію фактичного часу польоту навіть у момент катастрофічного відстрілу батареї.

## Реалізація модуля обліку

Нижче наведено робочу реалізацію модуля: у вкладці C — низькорівнева робота зі структурами та покажчиками, у вкладці C++ — об'єктно-орієнтований клас із семантикою `std::expected`, перевірками меж і строгими типами.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FLASH_SECTOR_SIZE   4096U
#define RECORD_MAGIC        0xA55A

/* 32-байтна структура збереження життєвого циклу */
typedef struct __attribute__((packed)) {
    uint16_t magic;            /* Сигнатура валідності (0xA55A) */
    uint16_t sequence_id;      /* Монотонно зростаючий лічильник записів */
    uint32_t flight_time_sec;  /* Напрацювання в польоті під навантаженням (секунди) */
    uint32_t total_milliamp_s; /* Інтеграл струму: міліампер-секунди (кулони) */
    uint16_t power_cycles;     /* Кількість увімкнень живлення (холодні старти) */
    uint16_t connector_cycles; /* Оцінка підключень силового роз'єму */
    uint16_t max_temp_c;       /* Зафіксована пікова температура (°C · 10) */
    uint16_t esc_vibration_idx;/* Середній індекс вібраційного навантаження */
    uint8_t  reserved[12];     /* Запас для майбутніх метрик */
    uint16_t crc16;            /* Контрольна сума CRC-CCITT */
} LifeRecord;

/* Прототипи апаратного рівня (HAL) */
extern bool hal_flash_read(uint32_t address, void* buffer, size_t length);
extern bool hal_flash_write(uint32_t address, const void* data, size_t length);
extern bool hal_flash_erase_sector(uint32_t sector_address);

static uint16_t crc16_ccitt(const uint8_t* data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

typedef struct {
    uint32_t sector_base_addr;
    uint32_t current_slot_idx;
    LifeRecord active_state;
} WearTracker;

bool wear_tracker_init(WearTracker* tracker, uint32_t sector_addr) {
    tracker->sector_base_addr = sector_addr;
    tracker->current_slot_idx = 0;
    memset(&tracker->active_state, 0, sizeof(LifeRecord));

    uint16_t max_seq = 0;
    bool found_valid = false;
    uint32_t num_slots = FLASH_SECTOR_SIZE / sizeof(LifeRecord);

    /* Сканування сектора для пошуку найсвіжішого валідного запису */
    for (uint32_t i = 0; i < num_slots; i++) {
        LifeRecord rec;
        uint32_t slot_addr = sector_addr + i * sizeof(LifeRecord);
        if (!hal_flash_read(slot_addr, &rec, sizeof(LifeRecord))) {
            return false;
        }

        if (rec.magic == RECORD_MAGIC) {
            uint16_t expected_crc = crc16_ccitt((const uint8_t*)&rec, sizeof(LifeRecord) - sizeof(uint16_t));
            if (rec.crc16 == expected_crc) {
                if (!found_valid || rec.sequence_id >= max_seq) {
                    max_seq = rec.sequence_id;
                    tracker->active_state = rec;
                    tracker->current_slot_idx = i;
                    found_valid = true;
                }
            }
        }
    }

    if (found_valid) {
        /* Переходимо до наступного вільного слота */
        tracker->current_slot_idx = (tracker->current_slot_idx + 1) % num_slots;
    } else {
        /* Сектор порожній або пошкоджений: ініціалізуємо новий */
        hal_flash_erase_sector(sector_addr);
        tracker->active_state.magic = RECORD_MAGIC;
        tracker->active_state.sequence_id = 1;
        tracker->current_slot_idx = 0;
    }

    return true;
}

bool wear_tracker_commit(WearTracker* tracker) {
    uint32_t num_slots = FLASH_SECTOR_SIZE / sizeof(LifeRecord);

    /* Якщо дійшли до кінця сектора — стираємо та починаємо з 0 */
    if (tracker->current_slot_idx == 0 && tracker->active_state.sequence_id > 1) {
        if (!hal_flash_erase_sector(tracker->sector_base_addr)) {
            return false;
        }
    }

    tracker->active_state.magic = RECORD_MAGIC;
    tracker->active_state.sequence_id++;
    tracker->active_state.crc16 = crc16_ccitt(
        (const uint8_t*)&tracker->active_state,
        sizeof(LifeRecord) - sizeof(uint16_t)
    );

    uint32_t target_addr = tracker->sector_base_addr + tracker->current_slot_idx * sizeof(LifeRecord);
    if (!hal_flash_write(target_addr, &tracker->active_state, sizeof(LifeRecord))) {
        return false;
    }

    tracker->current_slot_idx = (tracker->current_slot_idx + 1) % num_slots;
    return true;
}

void wear_tracker_add_flight_time(WearTracker* tracker, uint32_t seconds, uint32_t current_ma) {
    tracker->active_state.flight_time_sec += seconds;
    tracker->active_state.total_milliamp_s += seconds * current_ma;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <algorithm>

namespace hardware::telemetry {

inline constexpr uint32_t FlashSectorSize = 4096;
inline constexpr uint16_t RecordMagic = 0xA55A;

enum class TrackerError : uint8_t {
    FlashReadFailed,
    FlashWriteFailed,
    FlashEraseFailed,
    CorruptedData
};

struct [[gnu::packed]] LifeRecord {
    uint16_t magic{RecordMagic};
    uint16_t sequenceId{0};
    uint32_t flightTimeSec{0};
    uint32_t totalMilliampSec{0};
    uint16_t powerCycles{0};
    uint16_t connectorCycles{0};
    uint16_t maxTempDecicelsius{0};
    uint16_t escVibrationIndex{0};
    uint8_t  reserved[12]{};
    uint16_t crc16{0};

    [[nodiscard]] uint16_t computeCrc() const noexcept {
        auto rawSpan = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(this),
            sizeof(LifeRecord) - sizeof(uint16_t)
        );
        uint16_t crc = 0xFFFF;
        for (uint8_t byte : rawSpan) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                crc = (crc & 0x8000) ? (static_cast<uint16_t>(crc << 1) ^ 0x1021)
                                     : static_cast<uint16_t>(crc << 1);
            }
        }
        return crc;
    }

    [[nodiscard]] bool isValid() const noexcept {
        return magic == RecordMagic && crc16 == computeCrc();
    }
};

class FlashWearTracker {
public:
    explicit constexpr FlashWearTracker(uint32_t sectorAddress) noexcept
        : m_sectorAddress(sectorAddress) {}

    std::expected<void, TrackerError> init() noexcept {
        uint16_t maxSeq = 0;
        bool foundValid = false;
        constexpr uint32_t totalSlots = FlashSectorSize / sizeof(LifeRecord);

        for (uint32_t i = 0; i < totalSlots; ++i) {
            LifeRecord rec{};
            const uint32_t slotAddr = m_sectorAddress + i * sizeof(LifeRecord);
            if (!halRead(slotAddr, std::span<uint8_t>(reinterpret_cast<uint8_t*>(&rec), sizeof(LifeRecord)))) {
                return std::unexpected(TrackerError::FlashReadFailed);
            }

            if (rec.isValid()) {
                if (!foundValid || rec.sequenceId >= maxSeq) {
                    maxSeq = rec.sequenceId;
                    m_state = rec;
                    m_currentSlot = i;
                    foundValid = true;
                }
            }
        }

        if (foundValid) {
            m_currentSlot = (m_currentSlot + 1) % totalSlots;
        } else {
            if (!halErase(m_sectorAddress)) {
                return std::unexpected(TrackerError::FlashEraseFailed);
            }
            m_state = LifeRecord{.magic = RecordMagic, .sequenceId = 1};
            m_currentSlot = 0;
        }
        return {};
    }

    std::expected<void, TrackerError> commit() noexcept {
        constexpr uint32_t totalSlots = FlashSectorSize / sizeof(LifeRecord);

        if (m_currentSlot == 0 && m_state.sequenceId > 1) {
            if (!halErase(m_sectorAddress)) {
                return std::unexpected(TrackerError::FlashEraseFailed);
            }
        }

        m_state.magic = RecordMagic;
        m_state.sequenceId++;
        m_state.crc16 = m_state.computeCrc();

        const uint32_t targetAddr = m_sectorAddress + m_currentSlot * sizeof(LifeRecord);
        auto dataSpan = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&m_state),
            sizeof(LifeRecord)
        );

        if (!halWrite(targetAddr, dataSpan)) {
            return std::unexpected(TrackerError::FlashWriteFailed);
        }

        m_currentSlot = (m_currentSlot + 1) % totalSlots;
        return {};
    }

    void recordFlight(uint32_t durationSeconds, uint32_t currentMilliamps) noexcept {
        m_state.flightTimeSec += durationSeconds;
        m_state.totalMilliampSec += durationSeconds * currentMilliamps;
    }

    [[nodiscard]] const LifeRecord& state() const noexcept { return m_state; }

private:
    uint32_t m_sectorAddress{0};
    uint32_t m_currentSlot{0};
    LifeRecord m_state{};

    // Зовнішні апаратні виклики (mock/HAL)
    static bool halRead(uint32_t addr, std::span<uint8_t> dst) noexcept;
    static bool halWrite(uint32_t addr, std::span<const uint8_t> src) noexcept;
    static bool halErase(uint32_t sectorAddr) noexcept;
};

} // namespace hardware::telemetry
```
:::

## Інтеграція з діагностичним контуром та пороги тривоги

Модуль викликається у двох режимах:
1. **Періодичний крок (раз на 1–5 хвилин польоту):** накопичує секунди роботи моторів та інтегрує показники шунта струму.
2. **Подія зупинки/роззброєння (Disarm):** фіксує підсумковий стан польоту перед вимкненням живлення.

### Ресурсні прапорці телеметрії (Health Flags)

Контролер порівнює накопичені поля структури `LifeRecord` із системними граничними порогами:

```
Показник у LifeRecord        Поріг спрацьовування       Подія / Статус обслуговування
-----------------------------------------------------------------------------------
flight_time_sec >= 360 000  (100 мотогодин)            MAINTENANCE_BEARINGS_DUE
connector_cycles >= 200     (200 підключень XT60)      MAINTENANCE_CONNECTOR_INSPECT
total_milliamp_s >= 3.6e9   (1 000 А·год через міст)   MAINTENANCE_CAPACITORS_CHECK
max_temp_c >= 950           (нагрів > 95.0 °C)         OVERHEAT_LATCH_RECORDED
```

Коли будь-який із лічильників досягає порогового значення, польотний контролер виставляє прапорець передпольотного попередження `MAINTENANCE_REQUIRED` у пакеті телеметрії MAVLink/MSP (наприклад, у полі `SYS_STATUS.onboard_control_sensors_health`), сигналізуючи оператору на наземній станції про необхідність обов'язкової дефектовки підшипників, заміни силових роз'ємів або перевірки електролітичних фільтрів перед наступним вильотом.
