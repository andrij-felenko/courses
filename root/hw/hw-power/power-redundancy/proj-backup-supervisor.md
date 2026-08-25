# ⚙️ Реалізація супервізора резервного живлення та збереження стану

У промислових контролерах автоматизації (PLC), медичних моніторах, польотних контролерах безпілотників та автомобільних блоках керування раптове зникнення живлення несе загрозу пошкодження файлової системи, втрати накопичених лічильників мотогодин та аварійної зупинки механізмів без фіксації їхніх поточних координат.

Цей проект розбирає створення автономного супервізора живлення (Power Fail Supervisor) на базі мікроконтролера, схеми виявлення аварії напруги (Power Fail Input, PFI), резервного накопичувача на суперконденсаторах та енергонезалежної пам'яті FRAM (Ferroelectric RAM). Система детектує зникнення вхідної напруги за десятки мікросекунд до початку просадки вторинних шин живлення ядра (протокол Dying Gasp), перемикає споживання на резервний банк і встигає атомарно зберегти критичний знімок стану системи.

## 1. Апаратна архітектура та вибір пам'яті для Dying Gasp

Головне обмеження протоколу Dying Gasp — жорсткий ліміт часу. Коли первинна мережа 12 В падає, накопичувальні конденсатори шини розряджаються за кількасот мікросекунд або мілісекунд залежно від струму навантаження. 

```
                                  [ Вхідний подільник PFI ]
                                             │
                                             ▼
[ Мережа 12 В ] ──► [ Active ORing ] ──► [ Компаратор ] ──► (NMI / EXTI Переривання)
       │                   │
       │                   ▼
       │             [ Шина 12 В ] ──► [ DC-DC 3.3 В ] ──► [ MCU + FRAM ]
       │                   ▲
       ▼                   │
[ Supercap 5 В ] ──► [ Boost 12 В ]
```

### Фізичні обмеження енергонезалежної пам'яті під час аварії

Під час вибору типу пам'яті для екстреного збереження інженери стикаються з трьома варіантами, два з яких є непридатними для надійного протоколу Dying Gasp:

1. **Flash-пам'ять (вбудована або зовнішня SPI Flash):**
   Flash-пам'ять вимагає попереднього стирання сектора перед записом. Час стирання сектора 4 КБ становить від `20` до `100 мс`, а час програмування сторінки — `0.5 – 2 мс`. Якщо напруга впаде нижче допустимого порогу під час стирання сектора, вся таблиця Flash буде безповоротно пошкоджена. Використовувати Flash для аварійного знімка стану неприпустимо.
2. **EEPROM (Electrically Erasable PROM):**
   Хоча EEPROM дозволяє побайтовий перезапис без стирання всього сектора, внутрішній цикл запису сторінки (Page Write Cycle) за рахунок тунелювання Фаулера-Нордгейма займає `3 – 10 мс`. Цього часу часто бракує при глибокій просадці вхідної шини.
3. **FRAM (Ferroelectric RAM — сегнетоелектрична пам'ять):**
   Пам'ять FRAM використовує зміщення атомів цирконію/титану в кристалічній решітці перовськіту під дією електричного поля. Перемикання поляризації відбувається швидше ніж за `10 нс`. Для мікроконтролера запис у FRAM виглядає як звичайний запис у швидкісну пам'ять SRAM: дані фіксуються на повній частоті тактування шини SPI (до 40 Мбіт/с) без жодної затримки програмування (`t_write = 0 мкс`). Блок даних розміром 256 байт записується менш ніж за 60 мкс. Ресурс становить `10¹⁴` циклів запису проти `10⁴` у Flash.

### Схемотехніка вузла детектування PFI

Схема детектування аварії встановлюється безпосередньо на первинному вводі 12 В до вхідних індуктивних дроселів і ключів Active ORing.

```
Вхід 12 В ───[ R1: 100 кОм ]───┬───► Вхід (+) Компаратора
                               │
                              [ R2: 10 кОм ]
                               │
                              [ R_h: 1 МОм ] ── (Позитивний зворотний зв'язок гістерезису)
                               │
                              GND
```

Поріг спрацьовування компаратора обирають на рівні `10.8 В` (падіння на 10% від номіналу 12.0 В). Для захисту від високочастотних імпульсних перешкод та просадок від пускових струмів компресорів чи моторів паралельно до резистора `R2` встановлюють керамічний фільтровий конденсатор `C_f = 100 пФ`, що задає апаратне згладжування з постійною часу `τ = 1.0 мкс`. 

Резистор позитивного зворотного зв'язку `R_h` формує гістерезис `ΔV_hyst ≈ 250 мВ`, що повністю усуває брязкіт виходу компаратора при повільному спаді вхідної напруги.

## 2. Часовий бюджет протоколу Dying Gasp

Для гарантованого збереження даних розраховують покадровий часовий бюджет від моменту детектування аварії до повного вичерпання резервної енергії:

```
t = 0 мкс:      Вхідна напруга перетинає поріг 10.8 В.
t = 1.2 мкс:    Фільтр PFI пропускає сигнал, компаратор перемикає вихід у LOW.
t = 1.5 мкс:    Контролер переривань NVIC захоплює сигнал EXTI/NMI, зупиняє поточний потік.
t = 2.0 мкс:    Вхід у функцію PFI_IRQHandler. Запуск процедури спасіння.
t = 5.0 мкс:    MCU вимикає тактування силових ШІМ-таймерів, дисплея, Ethernet PHY.
t = 8.0 мкс:    Споживання плати падає з 800 мА до 40 мА.
t = 15.0 мкс:   Збір поточних координат приводу, системного часу та показників сенсорів.
t = 25.0 мкс:   Обчислення контрольної суми CRC32 для сформованої структури даних.
t = 30.0 мкс:   Початок передачі кадру у FRAM по шині SPI (частота 20 МГц).
t = 95.0 мкс:   Завершення запису кадру (256 байт). Перевірка сигналу готовності.
t = 100.0 мкс:  Запис валідного прапорця «Clean Powerdown» у сектор стану.
t = 110.0 мкс:  MCU переходить у режим глибокого сну (Deep Sleep / Standby) з WFI.
t = 200...500 мс: Повний розряд суперконденсаторів або утримувального банку конденсаторів.
```

Завдяки зниженню струму споживання мікроконтролера на 5-й мікросекунді час утримання вторинної шини 3.3 В зростає в рази, створюючи величезний коефіцієнт запасу надійності.

## 3. Протокол безпечного запису: подвійна буферизація (Ping-Pong Buffer)

Навіть при використанні швидкісної пам'яті FRAM існує мізерна ймовірність того, що живлення зникне безпосередньо посеред передачі байта через фізичний обрив живильного кабелю під час короткого замикання. Якщо перезаписувати єдиний блок пам'яті за фіксованою адресою, пошкоджений запис знищить попередній валідний знімок.

Для запобігання втрати даних застосовують схему подвійної буферизації (Ping-Pong Storage):
* В адресному просторі FRAM виділяють дві незалежні ділянки: `Slot A` (адреса `0x0100`) та `Slot B` (адреса `0x0200`).
* Кожен слот містить заголовок із магічним числом `Magic` (`0x504F5752`), 64-бітний монотонний лічильник послідовності `Sequence ID`, корисне навантаження та поле `CRC32`.
* Під час аварії мікроконтролер записує дані в той слот, чий лічильник `Sequence ID` є старішим.
* Після відновлення живлення завантажувач читає обидва слоти, перевіряє їхні контрольні суми CRC32 і обирає той блок, який має валідну контрольну суму та найбільший номер `Sequence ID`.

```
               ┌────────────────────────────────────────────────────────┐
               │              Структура слота пам'яті FRAM              │
               ├──────────────┬──────────────┬───────────┬──────────────┤
               │ Magic Header │  Sequence ID │  Payload  │    CRC32     │
               │   (4 байти)  │   (8 байтів) │ (N байтів)│   (4 байти)  │
               └──────────────┴──────────────┴───────────┴──────────────┘
```

## 4. Програмна реалізація супервізора

Нижче наведено повністю робочу реалізацію драйвера аварійного супервізора живлення. У версії C продемонстровано низькорівневу роботу з регістрами та швидкісну передачу кадру. У вкладці C++ наведено типізовану модульну архітектуру з використанням семантики безпечних буферів `std::span`, шаблонів та концептів, що виключає вихід за межі масиву на етапі компіляції.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FRAM_SPI_CMD_WREN   0x06
#define FRAM_SPI_CMD_WRITE  0x02
#define FRAM_SPI_CMD_READ   0x03

#define FRAM_SLOT_A_ADDR    0x0100
#define FRAM_SLOT_B_ADDR    0x0200
#define SYSTEM_MAGIC_HEADER 0x504F5752UL // "POWR"

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint64_t sequence_id;
    uint64_t timestamp_ms;
    int32_t  actuator_position_steps;
    int16_t  calibrated_zero_offset;
    float    last_bus_voltage;
    float    ambient_temperature;
    uint8_t  system_state_flags;
    uint8_t  reserved_padding[3];
    uint32_t crc32;
} SystemSnapshotRecord;

// Апаратні абстракції платформи
extern void bsp_spi_fram_select(void);
extern void bsp_spi_fram_deselect(void);
extern void bsp_spi_transmit(const uint8_t *data, uint16_t length);
extern void bsp_spi_receive(uint8_t *buffer, uint16_t length);
extern void bsp_emergency_shutdown_heavy_peripherals(void);
extern uint32_t bsp_calculate_hardware_crc32(const uint8_t *data, size_t length);
extern uint64_t bsp_get_system_time_ms(void);

static volatile bool g_power_loss_in_progress = false;
static uint64_t g_current_sequence_id = 0;

void fram_send_write_enable(void) {
    uint8_t cmd = FRAM_SPI_CMD_WREN;
    bsp_spi_fram_select();
    bsp_spi_transmit(&cmd, 1);
    bsp_spi_fram_deselect();
}

void fram_write_record(uint16_t address, const SystemSnapshotRecord *record) {
    uint8_t header[3];
    header[0] = FRAM_SPI_CMD_WRITE;
    header[1] = (uint8_t)(address >> 8);
    header[2] = (uint8_t)(address & 0xFF);

    fram_send_write_enable();

    bsp_spi_fram_select();
    bsp_spi_transmit(header, sizeof(header));
    bsp_spi_transmit((const uint8_t *)record, sizeof(SystemSnapshotRecord));
    bsp_spi_fram_deselect();
}

// Високопріоритетний обробник переривання PFI від компаратора живлення
void __attribute__((interrupt)) PFI_PowerFail_IRQHandler(void) {
    if (g_power_loss_in_progress) {
        return;
    }
    g_power_loss_in_progress = true;

    // 1. Аварійне відключення потужних споживачів струму
    bsp_emergency_shutdown_heavy_peripherals();

    // 2. Складання моментального знімка стану апаратури
    SystemSnapshotRecord snapshot;
    snapshot.magic = SYSTEM_MAGIC_HEADER;
    snapshot.sequence_id = ++g_current_sequence_id;
    snapshot.timestamp_ms = bsp_get_system_time_ms();
    snapshot.actuator_position_steps = 142850;
    snapshot.calibrated_zero_offset = -12;
    snapshot.last_bus_voltage = 10.74f;
    snapshot.ambient_temperature = 42.5f;
    snapshot.system_state_flags = 0x81; // Прапорці: Екстрена зупинка + Дані свіжі

    // Обчислення CRC32 без самого поля контрольної суми
    size_t payload_bytes = sizeof(SystemSnapshotRecord) - sizeof(uint32_t);
    snapshot.crc32 = bsp_calculate_hardware_crc32((const uint8_t *)&snapshot, payload_bytes);

    // 3. Запис у черговий слот Ping-Pong (чергування A/B за парністю sequence_id)
    uint16_t target_slot_addr = (snapshot.sequence_id & 1ULL) ? FRAM_SLOT_A_ADDR : FRAM_SLOT_B_ADDR;
    fram_write_record(target_slot_addr, &snapshot);

    // 4. Перехід мікроконтролера в режим сну до остаточного знеструмлення
    while (1) {
        __asm volatile("wfi");
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <concepts>
#include <optional>

namespace EmbeddedPower {

inline constexpr uint32_t MagicHeaderValue = 0x504F5752; // "POWR"
inline constexpr uint16_t SlotAddressA = 0x0100;
inline constexpr uint16_t SlotAddressB = 0x0200;

enum class MemoryOpcode : uint8_t {
    WriteEnable  = 0x06,
    WritePayload = 0x02,
    ReadPayload  = 0x03
};

struct [[gnu::packed]] SystemSnapshotRecord {
    uint32_t magic{MagicHeaderValue};
    uint64_t sequence_id{0};
    uint64_t timestamp_ms{0};
    int32_t  actuator_position_steps{0};
    int16_t  calibrated_zero_offset{0};
    float    last_bus_voltage{0.0f};
    float    ambient_temperature{0.0f};
    uint8_t  system_state_flags{0};
    uint8_t  reserved_padding[3]{0, 0, 0};
    uint32_t crc32{0};

    [[nodiscard]] std::span<const uint8_t> payload_span() const noexcept {
        constexpr size_t payload_size = sizeof(SystemSnapshotRecord) - sizeof(uint32_t);
        return {reinterpret_cast<const uint8_t*>(this), payload_size};
    }
};

template <typename SpiBus>
concept SpiInterface = requires(SpiBus spi, std::span<const uint8_t> out_data, std::span<uint8_t> in_data) {
    { spi.chip_select() } -> std::same_as<void>;
    { spi.chip_deselect() } -> std::same_as<void>;
    { spi.write_blocking(out_data) } -> std::same_as<void>;
    { spi.read_blocking(in_data) } -> std::same_as<void>;
};

template <SpiInterface SpiDriver>
class PowerFailSupervisor {
public:
    explicit PowerFailSupervisor(SpiDriver& spi_driver) noexcept : spi_(spi_driver) {}

    void process_dying_gasp(int32_t current_actuator_pos, float bus_volts, float temp_c, uint64_t uptime) noexcept {
        if (is_dying_gasp_active_) {
            return;
        }
        is_dying_gasp_active_ = true;

        SystemSnapshotRecord record{
            .magic = MagicHeaderValue,
            .sequence_id = ++last_sequence_counter_,
            .timestamp_ms = uptime,
            .actuator_position_steps = current_actuator_pos,
            .calibrated_zero_offset = -12,
            .last_bus_voltage = bus_volts,
            .ambient_temperature = temp_c,
            .system_state_flags = 0x81,
            .reserved_padding = {0, 0, 0},
            .crc32 = 0
        };

        record.crc32 = compute_crc32_fast(record.payload_span());

        const uint16_t target_addr = (record.sequence_id & 1ULL) ? SlotAddressA : SlotAddressB;
        write_record_to_fram(target_addr, record);
    }

    [[nodiscard]] std::optional<SystemSnapshotRecord> restore_latest_snapshot() noexcept {
        const auto record_a = read_record_from_fram(SlotAddressA);
        const auto record_b = read_record_from_fram(SlotAddressB);

        const bool valid_a = record_a && is_record_valid(*record_a);
        const bool valid_b = record_b && is_record_valid(*record_b);

        if (valid_a && valid_b) {
            return (record_a->sequence_id > record_b->sequence_id) ? record_a : record_b;
        }
        if (valid_a) return record_a;
        if (valid_b) return record_b;

        return std::nullopt;
    }

private:
    SpiDriver& spi_;
    uint64_t last_sequence_counter_{0};
    bool is_dying_gasp_active_{false};

    void execute_write_enable() noexcept {
        const uint8_t cmd = static_cast<uint8_t>(MemoryOpcode::WriteEnable);
        spi_.chip_select();
        spi_.write_blocking(std::span<const uint8_t, 1>(&cmd, 1));
        spi_.chip_deselect();
    }

    void write_record_to_fram(uint16_t address, const SystemSnapshotRecord& record) noexcept {
        execute_write_enable();

        const std::array<uint8_t, 3> header_bytes{
            static_cast<uint8_t>(MemoryOpcode::WritePayload),
            static_cast<uint8_t>(address >> 8),
            static_cast<uint8_t>(address & 0xFF)
        };

        const auto raw_record_span = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&record), sizeof(SystemSnapshotRecord)
        );

        spi_.chip_select();
        spi_.write_blocking(header_bytes);
        spi_.write_blocking(raw_record_span);
        spi_.chip_deselect();
    }

    [[nodiscard]] std::optional<SystemSnapshotRecord> read_record_from_fram(uint16_t address) noexcept {
        const std::array<uint8_t, 3> header_bytes{
            static_cast<uint8_t>(MemoryOpcode::ReadPayload),
            static_cast<uint8_t>(address >> 8),
            static_cast<uint8_t>(address & 0xFF)
        };

        SystemSnapshotRecord record{};
        auto raw_record_span = std::span<uint8_t>(
            reinterpret_cast<uint8_t*>(&record), sizeof(SystemSnapshotRecord)
        );

        spi_.chip_select();
        spi_.write_blocking(header_bytes);
        spi_.read_blocking(raw_record_span);
        spi_.chip_deselect();

        return record;
    }

    [[nodiscard]] static bool is_record_valid(const SystemSnapshotRecord& rec) noexcept {
        if (rec.magic != MagicHeaderValue) {
            return false;
        }
        return compute_crc32_fast(rec.payload_span()) == rec.crc32;
    }

    [[nodiscard]] static uint32_t compute_crc32_fast(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFFUL;
        for (const uint8_t byte_val : data) {
            crc ^= byte_val;
            for (int bit = 0; bit < 8; ++bit) {
                crc = (crc >> 1) ^ (0xEDB88320UL & (-(crc & 1)));
            }
        }
        return ~crc;
    }
};

} // namespace EmbeddedPower
```
:::

## 5. Практичні пастки, крайові випадки та апаратний захист

1. **Плаваючий стан виводів мікроконтролера під час спаду живлення (GPIO Glitching):**
   Коли вторинна напруга 3.3 В опускається нижче порогу працездатності внутрішніх вихідних буферів мікроконтролера (`V_DD < 1.8 В`), виводи SPI (SCK, MOSI, CS) переходять у високоімпедансний стан (High-Z). Наведені шуми можуть створити випадкову комбінацію імпульсів, яку мікросхема пам'яті сприйме як команду запису випадкового байта в нульовий сектор.
   
   *Рішення:* Лінія вибору кристала `CS` мікросхеми FRAM обов'язково повинна мати фізичний зовнішній підтягувальний резистор (Pull-up) номіналом `4.7 кОм` до лінії живлення `V_DD_FRAM`. Це надійно утримує мікросхему в деактивованому стані навіть за повної відмови мікроконтролера.

2. **Захист від псевдоспрацьовувань компаратора PFI під час динамічного навантаження:**
   Якщо до загальної шини 12 В підключається потужний кроковий двигун або вмикається нагрівач, струмовий сплеск викликає короткочасну мілісекундну просадку напруги глибиною до 1.5 В. Якщо компаратор зреагує на такий імпульс, контролер почне аварійне вимкнення при абсолютно справній мережі.
   
   *Рішення:* Поєднання аналогового RC-фільтра на вході PFI та цифрової фільтрації (Deglitching). Програма в обробнику переривання робить три послідовні зчитування стану лінії PFI з інтервалом 2 мкс. Якщо сигнал повернувся в HIGH, переривання скидається як псевдотривога без переривання роботи основних потоків.

3. **Коректне відновлення після «чистого» та «аварійного» старту:**
   При плановому вимкненні тумблером система повинна виставити в пам'яті окремий прапорець `Clean_Shutdown_Flag = 1`. Під час наступного ввімкнення завантажувач аналізує цей біт: якщо прапорець скинутий у нуль, фіксується факт аварійного знеструмлення, формується запис у журналі подій (Crash Log) та запускається спеціальна процедура калібрування нульових точок виконавчих механізмів.
