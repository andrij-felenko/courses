# ⚙️ Апаратний драйвер енерголічильника ADE7953 на SPI

Цей проектний модуль містить повну реалізацію низькорівневого апаратного драйвера для метрологічної мікросхеми ADE7953 з інтерфейсом SPI. Драйвер реалізує протокол 16-бітної адресації, апаратну процедуру фіксації SPI-режиму (`SPI Lock`), конфігурацію вхідних підсилювачів PGA, запис метрологічних калібрувальних коефіцієнтів (Gain, Offset, Phase), неперервне зчитування діючих значень (True RMS V/I, P, Q, S, PF, Energy) та обробку апаратного переривання дисбалансу струмів (Anti-Tamper).

## 1. Архітектура драйвера та часові діаграми SPI

Драйвер взаємодіє з мікросхемою ADE7953 по 4-провідній шині SPI в режимі Mode 3 (CPOL = 1, CPHA = 1) або Mode 0 (CPOL = 0, CPHA = 0) на тактовій частоті до 5 МГц. Для надійної роботи в умовах сильних електромагнітних завад мережі високої напруги драйвер виконує такі критичні кроки:

1. **Апаратне та програмне скидання:** Після подачі живлення або виклику функції ініціалізації генерується програмне скидання записом біта `SWRST` у регістр `CONFIG` (`0x0102`), після чого драйвер витримує паузу 15 мс для стабілізації внутрішнього джерела опорної напруги (1.2 В bandgap) та цифрового ядра.
2. **Фіксація режиму SPI (SPI Lock):** Запис байта `0xAD` у регістр `0x00FE` вимикає автодетекцію інтерфейсу I2C, захищаючи шину від випадкового перемикання під час сплесків напруги.
3. **Завантаження конфігурації та калібрування:** Налаштування коефіцієнтів підсилення PGA (наприклад, 16× для шунта 250 мкОм та 1× для високовольтного дільника напруги), увімкнення цифрового фільтра високих частот HPF та запис коефіцієнтів `AIGAIN`, `AVGAIN`, `AIRMSOS`, `APHCAL` з енергонезалежної пам'яті (Flash/EEPROM).
4. **Періодичний збір метрик або обробка переривань:** Читання миттєвих і середньоквадратичних значень та перевірка прапорця `MISMTCH` у регістрі статусу `IRQSTATA`.

### Особливості розширення знаку для 24-бітних регістрів

Метрологічні регістри потужності (`AWATT`, `AVAR`, `AVA`) передають дані у форматі 24-бітного двійкового додаткового коду (signed 2's complement). Оскільки стандартні типи мікроконтролера оперують 32-бітними числами (`int32_t`), драйвер виконує обов'язкове знаково-розширене приведення типів: якщо старший 23-й біт дорівнює одиниці (від'ємне число), старший байт 32-бітного слова заповнюється одиницями (`0xFF000000`). Нехтування цією операцією призводить до того, що від'ємна потужність (генерація енергії в мережу або зворотне підключення) інтерпретується як величезне додатне число.

## 2. Реалізація драйвера на C та C++

Нижче наведено вихідний код драйвера у двох варіантах: процедурному C для вбудованих мікроконтролерів (ARM Cortex-M, ESP-IDF) та об'єктно-орієнтованому ідіоматичному C++20 з використанням типізованих регістрів, структур метрик та безпечної обробки помилок.

:::tabs

@tab C

```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Адреси регістрів ADE7953 */
#define ADE7953_REG_CONFIG2      0x00FE  /* 8-bit: SPI lock register */
#define ADE7953_REG_PGA_IA       0x0080  /* 8-bit: PGA IA gain */
#define ADE7953_REG_PGA_IB       0x0081  /* 8-bit: PGA IB gain */
#define ADE7953_REG_PGA_V        0x0082  /* 8-bit: PGA Voltage gain */
#define ADE7953_REG_CONFIG       0x0102  /* 16-bit: System config */
#define ADE7953_REG_ACCMODE      0x0103  /* 16-bit: Accumulation & Tamper mode */
#define ADE7953_REG_CF1DEN       0x0105  /* 16-bit: CF1 pulse denominator */
#define ADE7953_REG_APHCAL       0x0108  /* 10-bit: Channel A phase calibration */
#define ADE7953_REG_PFA          0x010A  /* 16-bit: Power factor IA */
#define ADE7953_REG_AWATT        0x0212  /* 24-bit: Active power IA */
#define ADE7953_REG_AVAR         0x0214  /* 24-bit: Reactive power IA */
#define ADE7953_REG_AVA          0x0216  /* 24-bit: Apparent power IA */
#define ADE7953_REG_ISUMLVL      0x0218  /* 24-bit: Tamper current threshold */
#define ADE7953_REG_AIRMS        0x021A  /* 24-bit: RMS Current IA */
#define ADE7953_REG_BIRMS        0x0219  /* 24-bit: RMS Current IB */
#define ADE7953_REG_VRMS         0x021B  /* 24-bit: RMS Voltage */
#define ADE7953_REG_AIGAIN       0x021C  /* 24-bit: Current Gain IA */
#define ADE7953_REG_AVGAIN       0x021E  /* 24-bit: Voltage Gain */
#define ADE7953_REG_AIRMSOS      0x0223  /* 24-bit: RMS Current Offset IA */
#define ADE7953_REG_AVRMSOS      0x0225  /* 24-bit: RMS Voltage Offset */
#define ADE7953_REG_IRQENA       0x022C  /* 24-bit: Interrupt enable A */
#define ADE7953_REG_IRQSTATA     0x022D  /* 24-bit: Interrupt status A */
#define ADE7953_REG_RSTIRQSTATA  0x032D  /* 24-bit: Read with reset status A */
#define ADE7953_REG_AENERGYA     0x031E  /* 32-bit: Active energy IA */
#define ADE7953_REG_AENERGYB     0x031F  /* 32-bit: Active energy IB */

/* Біти переривань */
#define ADE7953_IRQ_MISMTCH      (1UL << 14)
#define ADE7953_IRQ_ZX           (1UL << 3)

/* Структура конфігурації та калібрувальних коефіцієнтів */
typedef struct {
    uint8_t pga_ia;         /* 0=1x, 1=2x, 2=4x, 3=8x, 4=16x, 5=22x */
    uint8_t pga_ib;
    uint8_t pga_v;
    int32_t aigain;         /* 24-bit підсилення струму */
    int32_t avgain;         /* 24-bit підсилення напруги */
    int32_t airmsos;        /* 24-bit зріз шуму RMS */
    int16_t aphcal;         /* 10-bit калібрування фази */
    uint16_t cf1den;        /* Дільник імпульсів CF1 */
    float v_scale;          /* Коефіцієнт перерахунку LSB -> Вольт */
    float i_scale;          /* Коефіцієнт перерахунку LSB -> Ампер */
    float p_scale;          /* Коефіцієнт перерахунку LSB -> Ват */
} ade7953_calib_t;

/* Структура виміряних метрик мережі */
typedef struct {
    float voltage_rms;      /* Напруга, В */
    float current_a_rms;    /* Струм фази, А */
    float current_b_rms;    /* Струм нейтралі, А */
    float active_power;     /* Активна потужність, Вт */
    float reactive_power;   /* Реактивна потужність, вар */
    float apparent_power;   /* Повна потужність, ВА */
    float power_factor;     /* Коефіцієнт потужності cos phi */
    int32_t energy_a_raw;   /* Сире значення активної енергії фази */
    bool tamper_detected;   /* Прапорець виявлення розкрадання */
} ade7953_metrics_t;

/* Платформозалежний інтерфейс SPI (надається користувачем) */
typedef struct {
    void (*cs_low)(void);
    void (*cs_high)(void);
    void (*spi_transfer)(const uint8_t *tx, uint8_t *rx, uint16_t len);
    void (*delay_ms)(uint32_t ms);
} ade7953_hal_t;

/* Контекст драйвера */
typedef struct {
    ade7953_hal_t hal;
    ade7953_calib_t calib;
} ade7953_dev_t;

/* Низькорівневий запис регістрів різної розрядності */
static void ade7953_write_reg(ade7953_dev_t *dev, uint16_t reg, uint32_t val, uint8_t bytes) {
    uint8_t tx[7];
    tx[0] = (uint8_t)(reg >> 8);
    tx[1] = (uint8_t)(reg & 0xFF);
    tx[2] = 0x00; /* Команда запису */

    for (int i = 0; i < bytes; i++) {
        tx[3 + i] = (uint8_t)(val >> ((bytes - 1 - i) * 8));
    }

    dev->hal.cs_low();
    dev->hal.spi_transfer(tx, NULL, 3 + bytes);
    dev->hal.cs_high();
}

/* Низькорівневе читання регістрів */
static uint32_t ade7953_read_reg(ade7953_dev_t *dev, uint16_t reg, uint8_t bytes) {
    uint8_t tx[7] = {0};
    uint8_t rx[7] = {0};
    tx[0] = (uint8_t)(reg >> 8);
    tx[1] = (uint8_t)(reg & 0xFF);
    tx[2] = 0x80; /* Команда читання */

    dev->hal.cs_low();
    dev->hal.spi_transfer(tx, rx, 3 + bytes);
    dev->hal.cs_high();

    uint32_t result = 0;
    for (int i = 0; i < bytes; i++) {
        result = (result << 8) | rx[3 + i];
    }
    return result;
}

/* Читання регістра зі знаком (двійковий додатковий код) */
static int32_t ade7953_read_signed(ade7953_dev_t *dev, uint16_t reg, uint8_t bytes) {
    uint32_t raw = ade7953_read_reg(dev, reg, bytes);
    if (bytes == 3) {
        if (raw & 0x800000) raw |= 0xFF000000; /* Розширення знакового біта 24 -> 32 */
    } else if (bytes == 2) {
        if (raw & 0x8000) raw |= 0xFFFF0000;
    }
    return (int32_t)raw;
}

/* Ініціалізація та блокування SPI */
bool ade7953_init(ade7953_dev_t *dev, const ade7953_hal_t *hal, const ade7953_calib_t *calib) {
    dev->hal = *hal;
    dev->calib = *calib;

    /* Програмне скидання */
    ade7953_write_reg(dev, ADE7953_REG_CONFIG, 0x0080, 2);
    dev->hal.delay_ms(15);

    /* Фіксація режиму SPI: запис 0xAD у регістр 0x00FE */
    ade7953_write_reg(dev, ADE7953_REG_CONFIG2, 0xAD, 1);

    /* Налаштування вхідних підсилювачів PGA */
    ade7953_write_reg(dev, ADE7953_REG_PGA_IA, dev->calib.pga_ia, 1);
    ade7953_write_reg(dev, ADE7953_REG_PGA_IB, dev->calib.pga_ib, 1);
    ade7953_write_reg(dev, ADE7953_REG_PGA_V, dev->calib.pga_v, 1);

    /* Завантаження калібрувальних коефіцієнтів */
    ade7953_write_reg(dev, ADE7953_REG_AIGAIN, (uint32_t)dev->calib.aigain, 3);
    ade7953_write_reg(dev, ADE7953_REG_AVGAIN, (uint32_t)dev->calib.avgain, 3);
    ade7953_write_reg(dev, ADE7953_REG_AIRMSOS, (uint32_t)dev->calib.airmsos, 3);
    ade7953_write_reg(dev, ADE7953_REG_APHCAL, (uint32_t)dev->calib.aphcal, 2);
    ade7953_write_reg(dev, ADE7953_REG_CF1DEN, dev->calib.cf1den, 2);

    /* Увімкнення режиму автоматичного обліку Anti-Tamper (біти в ACCMODE) */
    ade7953_write_reg(dev, ADE7953_REG_ACCMODE, 0x0008, 2);

    /* Дозвіл переривання виявлення дисбалансу струмів */
    ade7953_write_reg(dev, ADE7953_REG_IRQENA, ADE7953_IRQ_MISMTCH, 3);

    return true;
}

/* Зчитування поточних метрологічних параметрів */
void ade7953_read_metrics(ade7953_dev_t *dev, ade7953_metrics_t *metrics) {
    uint32_t v_raw = ade7953_read_reg(dev, ADE7953_REG_VRMS, 3);
    uint32_t ia_raw = ade7953_read_reg(dev, ADE7953_REG_AIRMS, 3);
    uint32_t ib_raw = ade7953_read_reg(dev, ADE7953_REG_BIRMS, 3);
    int32_t p_raw = ade7953_read_signed(dev, ADE7953_REG_AWATT, 3);
    int32_t q_raw = ade7953_read_signed(dev, ADE7953_REG_AVAR, 3);
    int32_t s_raw = ade7953_read_signed(dev, ADE7953_REG_AVA, 3);
    int16_t pf_raw = (int16_t)ade7953_read_reg(dev, ADE7953_REG_PFA, 2);
    int32_t energy_raw = (int32_t)ade7953_read_reg(dev, ADE7953_REG_AENERGYA, 4);

    uint32_t irq_stat = ade7953_read_reg(dev, ADE7953_REG_RSTIRQSTATA, 3);

    metrics->voltage_rms = (float)v_raw * dev->calib.v_scale;
    metrics->current_a_rms = (float)ia_raw * dev->calib.i_scale;
    metrics->current_b_rms = (float)ib_raw * dev->calib.i_scale;
    metrics->active_power = (float)p_raw * dev->calib.p_scale;
    metrics->reactive_power = (float)q_raw * dev->calib.p_scale;
    metrics->apparent_power = (float)s_raw * dev->calib.p_scale;
    metrics->power_factor = (float)pf_raw / 32768.0f;
    metrics->energy_a_raw = energy_raw;
    metrics->tamper_detected = (irq_stat & ADE7953_IRQ_MISMTCH) != 0;
}
```

@tab C++

```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>
#include <expected>
#include <chrono>

namespace metrology {

/* Типізовані 16-бітні адреси регістрів ADE7953 */
enum class Register : uint16_t {
    Config2      = 0x00FE,
    PgaIa        = 0x0080,
    PgaIb        = 0x0081,
    PgaV         = 0x0082,
    Config       = 0x0102,
    AccMode      = 0x0103,
    Cf1Den       = 0x0105,
    ApHCAL       = 0x0108,
    PfA          = 0x010A,
    AWatt        = 0x0212,
    AVar         = 0x0214,
    AVa          = 0x0216,
    ISumLvl      = 0x0218,
    AIrms        = 0x021A,
    BIrms        = 0x0219,
    VRms         = 0x021B,
    AIGain       = 0x021C,
    AVGain       = 0x021E,
    AIrmsOs      = 0x0223,
    AVRmsOs      = 0x0225,
    IrqEnA       = 0x022C,
    IrqStatA     = 0x022D,
    RstIrqStatA  = 0x032D,
    AEnergyA     = 0x031E,
    AEnergyB     = 0x031F
};

/* Коди помилок драйвера */
enum class MeterError {
    BusFailure,
    Timeout,
    InvalidParameter
};

/* Концепт апаратної шини SPI */
template <typename T>
concept SpiBus = requires(T bus, std::span<const uint8_t> tx, std::span<uint8_t> rx) {
    { bus.select() } -> std::same_as<void>;
    { bus.deselect() } -> std::same_as<void>;
    { bus.transfer(tx, rx) } -> std::same_as<bool>;
    { bus.delay_ms(uint32_t{}) } -> std::same_as<void>;
};

/* Налаштування коефіцієнтів та масштабів */
struct CalibrationData {
    uint8_t pga_ia{4};       // 16x для струмового шунта
    uint8_t pga_ib{4};
    uint8_t pga_v{0};        // 1x для високовольтного дільника
    int32_t aigain{0};
    int32_t avgain{0};
    int32_t airmsos{0};
    int16_t aphcal{0};
    uint16_t cf1den{63};
    float v_scale{0.000254f}; // Вольт / LSB
    float i_scale{0.000012f}; // Ампер / LSB
    float p_scale{0.003050f}; // Ват / LSB
};

/* Структура комплексних показів лічильника */
struct MeterReading {
    float voltage_rms{0.0f};
    float current_phase_rms{0.0f};
    float current_neutral_rms{0.0f};
    float active_power{0.0f};
    float reactive_power{0.0f};
    float apparent_power{0.0f};
    float power_factor{1.0f};
    int32_t energy_raw{0};
    bool tamper_alert{false};
};

/* RAII-обгортка вибору чіпа Chip Select */
template <SpiBus Spi>
class SpiGuard {
public:
    explicit SpiGuard(Spi& bus) : bus_(bus) { bus_.select(); }
    ~SpiGuard() { bus_.deselect(); }
    SpiGuard(const SpiGuard&) = delete;
    SpiGuard& operator=(const SpiGuard&) = delete;
private:
    Spi& bus_;
};

/* Шаблонний клас драйвера ADE7953 */
template <SpiBus Spi>
class Ade7953Driver {
public:
    explicit Ade7953Driver(Spi& bus, CalibrationData calib)
        : bus_(bus), calib_(calib) {}

    std::expected<void, MeterError> init() {
        // Програмне скидання мікросхеми
        if (!write_register(Register::Config, 0x0080, 2)) return std::unexpected(MeterError::BusFailure);
        bus_.delay_ms(15);

        // Блокування режиму SPI: запис 0xAD у регістр 0x00FE
        if (!write_register(Register::Config2, 0xAD, 1)) return std::unexpected(MeterError::BusFailure);

        // Конфігурація вхідних PGA
        write_register(Register::PgaIa, calib_.pga_ia, 1);
        write_register(Register::PgaIb, calib_.pga_ib, 1);
        write_register(Register::PgaV, calib_.pga_v, 1);

        // Завантаження калібрувальних регістрів
        write_register(Register::AIGain, static_cast<uint32_t>(calib_.aigain), 3);
        write_register(Register::AVGain, static_cast<uint32_t>(calib_.avgain), 3);
        write_register(Register::AIrmsOs, static_cast<uint32_t>(calib_.airmsos), 3);
        write_register(Register::ApHCAL, static_cast<uint32_t>(calib_.aphcal), 2);
        write_register(Register::Cf1Den, calib_.cf1den, 2);

        // Увімкнення режиму захисту від розкрадання: облік за max(IA, IB)
        write_register(Register::AccMode, 0x0008, 2);

        // Дозвіл переривання на вивід IRQ_A при фіксації дисбалансу
        write_register(Register::IrqEnA, (1UL << 14), 3);

        return {};
    }

    std::expected<MeterReading, MeterError> read_metrics() {
        auto v_raw = read_register(Register::VRms, 3);
        auto ia_raw = read_register(Register::AIrms, 3);
        auto ib_raw = read_register(Register::BIrms, 3);
        auto p_raw = read_signed_register(Register::AWatt, 3);
        auto q_raw = read_signed_register(Register::AVar, 3);
        auto s_raw = read_signed_register(Register::AVa, 3);
        auto pf_raw = read_signed_register(Register::PfA, 2);
        auto energy_raw = read_signed_register(Register::AEnergyA, 4);
        auto irq_stat = read_register(Register::RstIrqStatA, 3);

        if (!v_raw || !ia_raw || !p_raw || !irq_stat) {
            return std::unexpected(MeterError::BusFailure);
        }

        MeterReading reading{};
        reading.voltage_rms = static_cast<float>(*v_raw) * calib_.v_scale;
        reading.current_phase_rms = static_cast<float>(*ia_raw) * calib_.i_scale;
        reading.current_neutral_rms = static_cast<float>(*ib_raw) * calib_.i_scale;
        reading.active_power = static_cast<float>(*p_raw) * calib_.p_scale;
        reading.reactive_power = static_cast<float>(*q_raw) * calib_.p_scale;
        reading.apparent_power = static_cast<float>(*s_raw) * calib_.p_scale;
        reading.power_factor = static_cast<float>(*pf_raw) / 32768.0f;
        reading.energy_raw = *energy_raw;
        reading.tamper_alert = (*irq_stat & (1UL << 14)) != 0;

        return reading;
    }

private:
    bool write_register(Register reg, uint32_t value, size_t bytes) {
        uint8_t buffer[7];
        const uint16_t addr = static_cast<uint16_t>(reg);
        buffer[0] = static_cast<uint8_t>(addr >> 8);
        buffer[1] = static_cast<uint8_t>(addr & 0xFF);
        buffer[2] = 0x00; // Write command

        for (size_t i = 0; i < bytes; ++i) {
            buffer[3 + i] = static_cast<uint8_t>(value >> ((bytes - 1 - i) * 8));
        }

        SpiGuard<Spi> guard(bus_);
        return bus_.transfer(std::span<const uint8_t>(buffer, 3 + bytes), {});
    }

    std::expected<uint32_t, MeterError> read_register(Register reg, size_t bytes) {
        uint8_t tx[7]{};
        uint8_t rx[7]{};
        const uint16_t addr = static_cast<uint16_t>(reg);
        tx[0] = static_cast<uint8_t>(addr >> 8);
        tx[1] = static_cast<uint8_t>(addr & 0xFF);
        tx[2] = 0x80; // Read command

        {
            SpiGuard<Spi> guard(bus_);
            if (!bus_.transfer(std::span<const uint8_t>(tx, 3 + bytes), std::span<uint8_t>(rx, 3 + bytes))) {
                return std::unexpected(MeterError::BusFailure);
            }
        }

        uint32_t result = 0;
        for (size_t i = 0; i < bytes; ++i) {
            result = (result << 8) | rx[3 + i];
        }
        return result;
    }

    std::expected<int32_t, MeterError> read_signed_register(Register reg, size_t bytes) {
        auto val = read_register(reg, bytes);
        if (!val) return std::unexpected(val.error());

        uint32_t raw = *val;
        if (bytes == 3 && (raw & 0x800000)) raw |= 0xFF000000;
        else if (bytes == 2 && (raw & 0x8000)) raw |= 0xFFFF0000;

        return static_cast<int32_t>(raw);
    }

    Spi& bus_;
    CalibrationData calib_;
};

} // namespace metrology
```

:::

## 3. Гальванічна розв'язка та апаратне узгодження шини

Оскільки вимірювальний шунт фази під'єднується безпосередньо до силового фазного проводу 230 В, «земляний» полігон мікросхеми (GND) перебуває під високим потенціалом електричної мережі (так звана «гаряча земля»). Пряме з'єднання ліній SPI між ADE7953 та хост-контролером або комп'ютером є неприпустимим, оскільки це призведе до миттєвого короткого замикання, виходу обладнання з ладу та загрози ураження електричним струмом.

Для безпечного сполучення між метрологічною частиною та керуючим мікроконтролером (наприклад, STM32 чи ESP32) на платі встановлюють 4-канальний високошвидкісний цифровий ізолятор (ADuM1401, ISO7741 або Si8641). Живлення гарячої сторони забезпечується ізольованим DC/DC-перетворювачем або безтрансформаторним конденсаторним блоком живлення зі стабілітроном. Усі лінії SPI (SCK, MOSI, MISO, CS), а також лінія апаратного переривання IRQ проходять крізь бар'єр ізоляції з витримуваною напругою не менше 2.5–5.0 кВ.

## 4. Практичне застосування та алгоритм калібрування

Для отримання метрологічного класу точності (похибка < 0.5% у діапазоні струмів від 50 мА до 100 А) після монтажу плати виконується послідовна процедура заводського калібрування на калібрувальному стенді:

1. **Калібрування нульового зміщення (Offset Calibration):** При повністю відключеному навантаженні (I = 0.0 А) зчитується середній рівень шуму в регістрі `AIRMS`. Значення зміщення розраховується та записується в регістр `AIRMSOS`. Це усуває штучне завищення виміряного струму на холостому ході.
2. **Калібрування коефіцієнта напруги (VGAIN):** Від еталонного калібратора подається чиста синусоїдна напруга 230.0 В (50 Гц). Обчислюється відносна похибка між показами `VRMS` та дійсним значенням, після чого результат записується в регістр `AVGAIN`.
3. **Калібрування коефіцієнта струму (IGAIN):** Подається номінальний струм 5.0 А при чисто активному навантаженні (cos φ = 1.000). Коригується підсилення струмового каналу через регістр `AIGAIN`.
4. **Калібрування фазового кута (PHCAL):** Подається номінальний струм 5.0 А з фазовим зсувом cos φ = 0.500 (індуктивний характер, кут 60.0°). З регістра фази `ANGLE_A` зчитується залишкова кутова похибка трансформатора струму або RC-ланцюгів і записується в регістр `APHCAL`.
5. **Фіксація імпульсної константи CF:** Розраховане значення знаменника імпульсів записується в регістр `CF1DEN` для видачі 3200 імп/кВт·год на повірочний світлодіод.
