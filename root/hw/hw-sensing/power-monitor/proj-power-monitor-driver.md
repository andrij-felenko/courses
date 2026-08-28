# ⚙️ Драйвер цифрового монітора живлення для вбудованих систем

Монітори живлення на кшталт INA226 та INA219 передають результати вимірювання струму, напруги та потужності через послідовну шину I2C у формі 16-розрядних цілих чисел. Щоб мікроконтролер отримував фізичні значення у мілівольтах, міліамперах та міліватах без повільних операцій із рухомою комою, мікросхема містить внутрішній апаратний помножувач і калібрувальний регістр масштабування. Цей проект реалізує надійний виробничий драйвер монітора живлення з конфігурацією апаратного усереднення, розрахунком коефіцієнтів калібрування та обробкою переривань тривоги (ALERT) мовами C та C++.

### 1. Фізичний рівень I2C та адресація

Мікросхема INA226 підтримує стандартний (100 кГц), швидкий (400 кГц) та високошвидкісний (до 2.94 МГц) режими шини I2C. Для запобігання затягуванню фронтів через паразитну ємність ліній SDA та SCL підтягувальні резистори розраховуються виходячи з сумарної ємності шини `C_bus`:

```text
R_pullup_min = (VCC - 0.4 В) / 3 мА
R_pullup_max = t_r / (0.8473 · C_bus)
```

де для режиму Fast Mode (400 кГц) максимальний час наростання фронту `t_r = 300 нс`. При типовій ємності шини 50 пФ оптимальний номінал підтяжки становить `2.2–4.7 кОм`.

Мікросхема має два виводи вибору адреси (`A0` та `A1`), кожен з яких можна підключити до однієї з чотирьох ліній: `GND`, `VS+`, `SDA` або `SCL`. Це формує матрицю з 16 унікальних 7-розрядних адрес I2C (від `0x40` до `0x4F`), що дозволяє моніторити до 16 незалежних ліній живлення на одній спільній шині без мультиплексорів.

### 2. Карта регістрів та арифметика калібрування

Мікросхема INA226 адресує 16-розрядні регістри через 8-розрядний покажчик. Усі дані на шині I2C передаються у форматі Big-Endian (старший байт вичитується або записується першим):

| Адреса | Назва регістра | Опис та розрядність | Крок шкали (LSB) |
|---|---|---|---|
| `0x00` | `CONFIG` | Режим роботи, час вибірки, усереднення | Бітові поля |
| `0x01` | `SHUNT_VOLTAGE` | Диференційний спад напруги на шунті | `2.5 мкВ / LSB` (знакове 16 біт, доповняльний код) |
| `0x02` | `BUS_VOLTAGE` | Напруга шини живлення VBUS відносно GND | `1.25 мВ / LSB` (беззнакове 16 біт) |
| `0x03` | `POWER` | Обчислена апаратна потужність | `25 · Current_LSB` |
| `0x04` | `CURRENT` | Обчислений апаратний струм навантаження | `Current_LSB` (програмований) |
| `0x05` | `CALIBRATION` | Масштабний коефіцієнт помножувача | Ціле число 16 біт |
| `0x06` | `MASK_ENABLE` | Налаштування компаратора виводу ALERT | Бітові прапорці |
| `0x07` | `ALERT_LIMIT` | Поріг спрацьовування апаратної тривоги | Формат обраного вимірювання |

Внутрішній апаратний помножувач чіпа обчислює струм за формулою:

```text
Current = (Shunt_Voltage_Raw · Calibration_Register) / 2048
```

Щоб значення в регістрі `CURRENT` безпосередньо дорівнювало струму з обраною ціною молодшого розряду `Current_LSB` (у амперах на біт), значення калібрувального регістра `CAL` розраховується за формулою:

```text
CAL = trunc(0.00512 / (Current_LSB · R_shunt))
```

де `0.00512` — внутрішній фіксований коефіцієнт мікросхеми, `R_shunt` — опір шунта в омах. Крок регістра потужності `Power_LSB` автоматично стає рівним `25 · Current_LSB` (у ватах на біт).

Для збереження максимальної динамічної роздільності АЦП крок `Current_LSB` обирають як:

```text
Current_LSB = Max_Expected_Current / 32768
```

Значення округлюють вгору до зручної круглої величини (наприклад, 1 мА/LSB або 0.1 мА/LSB), щоб уникнути втрати точності через цілочисельне усічення константи `CAL`.

### 3. Архітектура опитування: протокол ARA та переривання ALERT

Драйвер підтримує три альтернативних сценарії отримання даних та обробки аварійних ситуацій:

1. **Синхронне переривання за готовністю перетворення (Conversion Ready)**: вивід `ALERT` налаштовується на генерацію імпульсу щоразу, коли АЦП завершує цикл інтегрування та усереднення. Мікроконтролер отримує апаратне переривання (EXTI) і вичитує регістри через I2C DMA, не витрачаючи процесорний час на очікування.
2. **Асинхронний аварійний моніторинг (Overcurrent Watchdog)**: мікроконтролер не опитує чіп постійно. Вивід `ALERT` підключається до лінії відключення силового ключа (Enable pin DC-DC перетворювача або затвору аварійного P-MOSFET). Якщо струм перевищує поріг `ALERT_LIMIT`, монітор апаратно садить лінію ALERT на нуль менш ніж за один цикл перетворення (до 140 мкс), вимикаючи живлення ще до того, як мікроконтролер встигне зреагувати програмно.
3. **Групове опитування через протокол SMBus Alert Response Address (ARA, адреса `0x0C`)**: коли кілька моніторів живлення підключені до однієї спільної лінії переривання ALERT, мікроконтролер після виникнення сигналу надсилає читання за спеціальною широкомовною адресою `0x0C`. Чіп, який згенерував переривання, відповідає власною 7-розрядною адресою на шині I2C та автоматично скидає свій вивід ALERT. Це усуває необхідність по черзі опитувати всі 16 мікросхем для пошуку джерела аварії.

### 4. Режими енергозбереження: Single-Shot проти Continuous

У постійно ввімкненому режимі (Continuous Mode) мікросхема споживає струм спокою близько `330 мкА`. Для пристроїв з батарейним живленням (IoT-маяки, автономні трекери), де середнє споживання системи не повинно перевищувати десятки мікроамперів, драйвер переводить монітор у режим **Single-Shot (Triggered Mode)** або **Power-Down**.

У режимі Power-Down аналоговий тракт, генератор опорної напруги та дельта-сигма модулятор вимикаються, а струм споживання падає нижче `0.5 мкА`. Коли мікроконтролеру потрібно зробити разовий вимір, він записує в регістр `CONFIG` код одиночного запуску (`Mode = 0x03` для шунта або `0x07` для обох каналів). Мікросхема прокидається, виконує один цикл інтегрування, виставляє прапорець готовності `Conversion Ready` і автоматично повертається в режим сну з мікроамперним споживанням.

### 5. Реалізація драйвера мовами C та C++

Нижче наведено повну реалізацію виробничого драйвера мовами C та ідіоматичним C++20. Драйвер містить апаратну ініціалізацію, перевірку сигнатури кристала, автоматичний розрахунок константи масштабування та роботу з апаратними перериваннями.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define INA226_I2C_ADDR_DEFAULT  0x40

/* Адреси внутрішніх регістрів */
#define INA226_REG_CONFIG        0x00
#define INA226_REG_SHUNTVOLTAGE  0x01
#define INA226_REG_BUSVOLTAGE    0x02
#define INA226_REG_POWER         0x03
#define INA226_REG_CURRENT       0x04
#define INA226_REG_CALIBRATION   0x05
#define INA226_REG_MASKENABLE    0x06
#define INA226_REG_ALERTLIMIT    0x07
#define INA226_REG_MANUF_ID      0xFE
#define INA226_REG_DIE_ID        0xFF

/* Бітові маски конфігурації */
#define INA226_RESET_BIT         0x8000
#define INA226_AVG_16            (0x02 << 9)
#define INA226_VBUS_CT_1100US    (0x04 << 6)
#define INA226_VSH_CT_1100US     (0x04 << 3)
#define INA226_MODE_CONTINUOUS   0x07
#define INA226_MODE_POWERDOWN    0x00
#define INA226_MODE_TRIGGERED    0x03

/* Бітові маски регістра переривань (MASK_ENABLE) */
#define INA226_ALERT_SHUNT_OVER  (1 << 15)
#define INA226_ALERT_BUS_OVER    (1 << 12)
#define INA226_ALERT_BUS_UNDER   (1 << 11)
#define INA226_ALERT_POWER_OVER  (1 << 10)
#define INA226_ALERT_CONV_READY  (1 << 14)

/* Абстракція платформного рівня I2C */
typedef bool (*ina226_i2c_write_fn)(uint8_t dev_addr, uint8_t reg, const uint8_t *data, uint16_t len);
typedef bool (*ina226_i2c_read_fn)(uint8_t dev_addr, uint8_t reg, uint8_t *data, uint16_t len);

typedef struct {
    uint8_t dev_addr;
    ina226_i2c_write_fn i2c_write;
    ina226_i2c_read_fn i2c_read;
    double current_lsb_a;    /* Ціна молодшого розряду струму в амперах */
    double power_lsb_w;      /* Ціна молодшого розряду потужності у ватах */
    uint16_t cal_val;        /* Розраховане значення регістра калібрування */
} ina226_handle_t;

static bool ina226_write_reg(ina226_handle_t *dev, uint8_t reg, uint16_t val) {
    uint8_t buf[2];
    buf[0] = (uint8_t)(val >> 8);    /* Старший байт (Big-Endian) */
    buf[1] = (uint8_t)(val & 0xFF);  /* Молодший байт */
    return dev->i2c_write(dev->dev_addr, reg, buf, 2);
}

static bool ina226_read_reg(ina226_handle_t *dev, uint8_t reg, uint16_t *val) {
    uint8_t buf[2];
    if (!dev->i2c_read(dev->dev_addr, reg, buf, 2)) {
        return false;
    }
    *val = ((uint16_t)buf[0] << 8) | buf[1];
    return true;
}

bool ina226_init(ina226_handle_t *dev, uint8_t addr, double r_shunt_ohms, double max_expected_current_a,
                 ina226_i2c_write_fn write_fn, ina226_i2c_read_fn read_fn) {
    dev->dev_addr = addr;
    dev->i2c_write = write_fn;
    dev->i2c_read = read_fn;

    /* Перевірка ідентифікатора виробника (TI = 0x5449) */
    uint16_t manuf_id = 0;
    if (!ina226_read_reg(dev, INA226_REG_MANUF_ID, &manuf_id) || manuf_id != 0x5449) {
        return false;
    }

    /* Програмне скидання мікросхеми */
    ina226_write_reg(dev, INA226_REG_CONFIG, INA226_RESET_BIT);

    /* Розрахунок ціни молодшого розряду: Current_LSB = Max_Current / 32768 */
    dev->current_lsb_a = max_expected_current_a / 32768.0;
    dev->power_lsb_w = 25.0 * dev->current_lsb_a;

    /* Розрахунок калібрувального коефіцієнта CAL = trunc(0.00512 / (Current_LSB * R_shunt)) */
    double cal = 0.00512 / (dev->current_lsb_a * r_shunt_ohms);
    dev->cal_val = (uint16_t)cal;

    /* Запис калібрувального значення у чіп */
    if (!ina226_write_reg(dev, INA226_REG_CALIBRATION, dev->cal_val)) {
        return false;
    }

    /* Налаштування режиму: усереднення на 16 вибірок, час перетворення 1.1 мс */
    uint16_t config = INA226_AVG_16 | INA226_VBUS_CT_1100US | INA226_VSH_CT_1100US | INA226_MODE_CONTINUOUS;
    return ina226_write_reg(dev, INA226_REG_CONFIG, config);
}

bool ina226_read_bus_voltage_mv(ina226_handle_t *dev, uint32_t *voltage_mv) {
    uint16_t raw = 0;
    if (!ina226_read_reg(dev, INA226_REG_BUSVOLTAGE, &raw)) {
        return false;
    }
    /* Крок напруги шини фіксований: 1.25 мВ / LSB */
    *voltage_mv = (uint32_t)((raw * 1250ULL) / 1000ULL);
    return true;
}

bool ina226_read_current_ma(ina226_handle_t *dev, int32_t *current_ma) {
    uint16_t raw = 0;
    if (!ina226_read_reg(dev, INA226_REG_CURRENT, &raw)) {
        return false;
    }
    int16_t signed_raw = (int16_t)raw;
    *current_ma = (int32_t)(signed_raw * dev->current_lsb_a * 1000.0);
    return true;
}

bool ina226_read_power_mw(ina226_handle_t *dev, uint32_t *power_mw) {
    uint16_t raw = 0;
    if (!ina226_read_reg(dev, INA226_REG_POWER, &raw)) {
        return false;
    }
    *power_mw = (uint32_t)(raw * dev->power_lsb_w * 1000.0);
    return true;
}

bool ina226_set_overcurrent_alert(ina226_handle_t *dev, double r_shunt_ohms, double limit_current_a) {
    /* Спад напруги на шунті для порогу струму: V_shunt_limit = I_limit * R_shunt */
    double v_shunt_v = limit_current_a * r_shunt_ohms;
    /* Крок регістра напруги шунта фіксований: 2.5 мкВ / LSB */
    int16_t limit_raw = (int16_t)(v_shunt_v / 0.0000025);

    if (!ina226_write_reg(dev, INA226_REG_ALERTLIMIT, (uint16_t)limit_raw)) {
        return false;
    }
    return ina226_write_reg(dev, INA226_REG_MASKENABLE, INA226_ALERT_SHUNT_OVER);
}
```
```cpp
#include <cstdint>
#include <concepts>
#include <expected>
#include <span>
#include <cmath>

namespace sensors {

enum class PowerMonitorError {
    DeviceNotFound,
    BusError,
    InvalidParameter,
    CalibrationFailed
};

struct PowerReadings {
    uint32_t bus_voltage_mv{0};
    int32_t current_ma{0};
    uint32_t power_mw{0};
    int32_t shunt_voltage_uv{0};
};

template <typename I2cBus>
concept I2cMaster = requires(I2cBus& bus, uint8_t addr, uint8_t reg, std::span<const uint8_t> out_buf, std::span<uint8_t> in_buf) {
    { bus.write(addr, reg, out_buf) } -> std::same_as<bool>;
    { bus.read(addr, reg, in_buf) }   -> std::same_as<bool>;
};

template <I2cMaster Bus>
class Ina226PowerMonitor {
public:
    static constexpr uint8_t DefaultAddress = 0x40;
    static constexpr uint16_t ManufacturerIdExpected = 0x5449;

    enum class Averaging : uint16_t {
        Avg1    = (0x00 << 9),
        Avg4    = (0x01 << 9),
        Avg16   = (0x02 << 9),
        Avg64   = (0x03 << 9),
        Avg128  = (0x04 << 9),
        Avg1024 = (0x07 << 9)
    };

    enum class OperatingMode : uint16_t {
        PowerDown  = 0x00,
        Triggered  = 0x03,
        Continuous = 0x07
    };

    explicit Ina226PowerMonitor(Bus& i2c_bus, uint8_t address = DefaultAddress)
        : bus_{i2c_bus}, address_{address} {}

    std::expected<void, PowerMonitorError> initialize(double shunt_resistance_ohms,
                                                     double max_expected_current_amps,
                                                     Averaging averaging = Averaging::Avg16,
                                                     OperatingMode mode = OperatingMode::Continuous) {
        if (shunt_resistance_ohms <= 0.0 || max_expected_current_amps <= 0.0) {
            return std::unexpected(PowerMonitorError::InvalidParameter);
        }

        // Перевірка Manufacture ID
        auto manuf_id = readRegister(Register::ManufId);
        if (!manuf_id || *manuf_id != ManufacturerIdExpected) {
            return std::unexpected(PowerMonitorError::DeviceNotFound);
        }

        // Скидання мікросхеми
        if (!writeRegister(Register::Config, 0x8000)) {
            return std::unexpected(PowerMonitorError::BusError);
        }

        // Розрахунок LSB струму та калібрувального значення
        current_lsb_a_ = max_expected_current_amps / 32768.0;
        power_lsb_w_   = 25.0 * current_lsb_a_;

        double cal_val = 0.00512 / (current_lsb_a_ * shunt_resistance_ohms);
        if (cal_val > 65535.0 || cal_val < 1.0) {
            return std::unexpected(PowerMonitorError::CalibrationFailed);
        }
        calibration_reg_ = static_cast<uint16_t>(cal_val);

        if (!writeRegister(Register::Calibration, calibration_reg_)) {
            return std::unexpected(PowerMonitorError::BusError);
        }

        // Налаштування режиму вимірювання (час конверсії 1.1 мс)
        constexpr uint16_t VbusCt1100us = (0x04 << 6);
        constexpr uint16_t VshCt1100us  = (0x04 << 3);

        uint16_t config = static_cast<uint16_t>(averaging) | VbusCt1100us | VshCt1100us | static_cast<uint16_t>(mode);
        if (!writeRegister(Register::Config, config)) {
            return std::unexpected(PowerMonitorError::BusError);
        }

        return {};
    }

    std::expected<PowerReadings, PowerMonitorError> readAll() {
        PowerReadings readings;

        // Зчитування напруги шини (LSB = 1.25 мВ)
        auto vbus_raw = readRegister(Register::BusVoltage);
        if (!vbus_raw) return std::unexpected(vbus_raw.error());
        readings.bus_voltage_mv = static_cast<uint32_t>((*vbus_raw * 1250ULL) / 1000ULL);

        // Зчитування напруги шунта (LSB = 2.5 мкВ)
        auto vsh_raw = readRegister(Register::ShuntVoltage);
        if (!vsh_raw) return std::unexpected(vsh_raw.error());
        readings.shunt_voltage_uv = static_cast<int32_t>(static_cast<int16_t>(*vsh_raw) * 2.5);

        // Зчитування струму
        auto curr_raw = readRegister(Register::Current);
        if (!curr_raw) return std::unexpected(curr_raw.error());
        readings.current_ma = static_cast<int32_t>(static_cast<int16_t>(*curr_raw) * current_lsb_a_ * 1000.0);

        // Зчитування потужності
        auto pwr_raw = readRegister(Register::Power);
        if (!pwr_raw) return std::unexpected(pwr_raw.error());
        readings.power_mw = static_cast<uint32_t>(*pwr_raw * power_lsb_w_ * 1000.0);

        return readings;
    }

    std::expected<void, PowerMonitorError> setOvercurrentThreshold(double shunt_resistance_ohms, double limit_amps) {
        double v_shunt_limit_v = limit_amps * shunt_resistance_ohms;
        int16_t limit_raw = static_cast<int16_t>(v_shunt_limit_v / 0.0000025);

        if (!writeRegister(Register::AlertLimit, static_cast<uint16_t>(limit_raw))) {
            return std::unexpected(PowerMonitorError::BusError);
        }
        constexpr uint16_t ShuntOverLimitMask = (1 << 15);
        if (!writeRegister(Register::MaskEnable, ShuntOverLimitMask)) {
            return std::unexpected(PowerMonitorError::BusError);
        }
        return {};
    }

private:
    enum class Register : uint8_t {
        Config       = 0x00,
        ShuntVoltage = 0x01,
        BusVoltage   = 0x02,
        Power        = 0x03,
        Current      = 0x04,
        Calibration  = 0x05,
        MaskEnable   = 0x06,
        AlertLimit   = 0x07,
        ManufId      = 0xFE,
        DieId        = 0xFF
    };

    Bus& bus_;
    uint8_t address_;
    double current_lsb_a_{0.001};
    double power_lsb_w_{0.025};
    uint16_t calibration_reg_{0};

    std::expected<uint16_t, PowerMonitorError> readRegister(Register reg) {
        uint8_t buffer[2]{0, 0};
        if (!bus_.read(address_, static_cast<uint8_t>(reg), buffer)) {
            return std::unexpected(PowerMonitorError::BusError);
        }
        return static_cast<uint16_t>((buffer[0] << 8) | buffer[1]);
    }

    bool writeRegister(Register reg, uint16_t value) {
        const uint8_t buffer[2]{
            static_cast<uint8_t>(value >> 8),
            static_cast<uint8_t>(value & 0xFF)
        };
        return bus_.write(address_, static_cast<uint8_t>(reg), buffer);
    }
};

} // namespace sensors
```
:::

### 6. Типові пастки інтеграції та їх розв'язання

1. **Втрата калібрування після скидання живлення**: якщо мікроконтролер переініціалізує перифірію або на спільній шині стається короткочасне просідання напруги `VCC`, внутрішній регістр `CALIBRATION` автоматично скидається в `0`. За нульового значення `CAL` апаратний помножувач вимикається, і регістри `CURRENT` та `POWER` повертатимуть виключно нулі, хоча регістри `SHUNT_VOLTAGE` та `BUS_VOLTAGE` продовжуватимуть оновлюватися в штатному режимі. Драйвер завжди має верифікувати ненульовий вміст регістра калібрування під час циклічного самотестування.
2. **Переповнення апаратного помножувача (Math Overflow)**: якщо фактичний струм через шунт перевищує `32767 · Current_LSB`, регістр струму затискається на максимальному значенні `0x7FFF`, а біт переповнення `OVF` у регістрі `MASK_ENABLE` виставляється в `1`. Для усунення переповнення слід збільшити розрахунковий масштаб `Current_LSB` та перерахувати константу `CAL`.
3. **Електричний шум від імпульсних перетворювачів DC-DC**: при прямому підключенні входів `IN+` та `IN-` до силової шини комутаційні викиди (100 кГц – 2 МГц) можуть викликати паразитну передискретизацію в дельта-сигма модуляторі. Встановлення симетричного RC-фільтра (`R = 10 Ом`, `C = 100 нФ`) безпосередньо перед виводами мікросхеми усуває наведення завад без спотворення точності вимірювання.
4. **Зависання шини I2C через збій Slave-пристрою**: при збої тактування під час передачі байта монітор може утримувати лінію SDA на нулі. Драйвер повинен підтримувати процедуру відновлення шини (I2C Bus Recovery), генеруючи до 9 імпульсів тактування на лінії SCL з подальшим формуванням сигналу STOP для примусового звільнення шини.
