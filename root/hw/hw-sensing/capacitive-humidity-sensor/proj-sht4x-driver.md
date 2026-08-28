# ⚙️ Драйвер сенсора вологості й температури SHT4x із розрахунком точки роси

Мікросхеми серії Sensirion SHT4x (SHT40, SHT41, SHT45) представляють четверте покоління прецизійних ємнісних давачів відносної вологості й температури з цифровим інтерфейсом I²C. Кристал інтегрує вологочутливу полімерну ємнісну комірку, термометр на забороненій зоні кремнію (bandgap PTAT), 16-бітний АЦП з перемиканими конденсаторами, енергонезалежну пам'ять із заводськими коефіцієнтами лінеаризації та мікронагрівач потужністю до 200 мВт для випаровування конденсату.

Нижче наведено виробничий драйвер сенсора мовами C та C++, оптимізований для вбудованих систем на базі мікроконтролерів ARM Cortex-M та RISC-V. Драйвер містить перевірку контрольної суми CRC-8, коректні часові інтервали вимірювання, керування імпульсним нагрівачем, захист від апаратного блокування шини та обчислення точки роси й абсолютної вологості.

### Архітектура протоколу та формати слів

Сенсор підтримує стандартну 7-бітну I²C-адресу `0x44` (доступні також фабричні модифікації з адресою `0x45`). На відміну від класичних мікросхем із внутрішніми регістрами, протокол SHT4x не використовує покажчики регістрів. Будь-яка операція ініціюється відправкою однобайтної команди:
- `0xFD` — вимірювання температури й вологості з найвищою роздільною здатністю (час інтегрування АЦП до 8.2 мс);
- `0xF6` — вимірювання із середньою точністю (час вимірювання до 4.5 мс);
- `0xE0` — швидке вимірювання з низькою роздільною здатністю (до 1.7 мс);
- `0x89` — зчитування 32-бітного унікального серійного номера кристала (Serial Number);
- `0x94` — програмне скидання чипа (Soft Reset, час ініціалізації 1.0 мс);
- `0x39` — запуск нагрівача на максимальній потужності (200 мВт на 1.0 с) із наступним вимірюванням;
- `0x32` — імпульс нагрівача 200 мВт тривалістю 0.1 с;
- `0x2F` / `0x24` — нагрівач середньої потужності (110 мВт на 1.0 с / 0.1 с);
- `0x1E` / `0x15` — нагрівач низької потужності (20 мВт на 1.0 с / 0.1 с).

Після передачі команди вимірювання хост-контролер повинен витримати затримку, еквівалентну максимальному часу перетворення, або опитувати шину (ACK polling). Під час вимірювання сенсор не розтягує лінію тактування (Clock Stretching відсутній), а відповідає сигналом NACK на спроби передчасного читання.

У відповідь на успішне зчитування чип повертає 6 байтів даних:
`[Temp MSB, Temp LSB, Temp CRC, RH MSB, RH LSB, RH CRC]`.

Поліном контрольної суми CRC-8 описується виразом:
`P(x) = x^8 + x^5 + x^4 + 1` (поліном `0x31`, ініціалізаційний вектор `0xFF`).

Фізичні значення обчислюються з 16-бітних слів за калібрувальними рівняннями виробника:

```
T_celsius = -45.0 + 175.0 · (S_T / 65535.0)
RH_percent = -6.0 + 125.0 · (S_RH / 65535.0)       [з обмеженням у діапазон 0..100 %]
```

### Реалізація драйвера

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define SHT4X_I2C_ADDR_DEFAULT  0x44

typedef enum {
    SHT4X_CMD_MEASURE_HIGH_PREC     = 0xFD,
    SHT4X_CMD_MEASURE_MED_PREC      = 0xF6,
    SHT4X_CMD_MEASURE_LOW_PREC      = 0xE0,
    SHT4X_CMD_READ_SERIAL           = 0x89,
    SHT4X_CMD_SOFT_RESET            = 0x94,
    SHT4X_CMD_HEATER_200MW_1SEC     = 0x39,
    SHT4X_CMD_HEATER_200MW_0P1SEC   = 0x32,
    SHT4X_CMD_HEATER_110MW_1SEC     = 0x2F,
    SHT4X_CMD_HEATER_110MW_0P1SEC   = 0x24,
    SHT4X_CMD_HEATER_20MW_1SEC      = 0x1E,
    SHT4X_CMD_HEATER_20MW_0P1SEC    = 0x15
} sht4x_command_t;

typedef enum {
    SHT4X_OK = 0,
    SHT4X_ERR_I2C = -1,
    SHT4X_ERR_CRC_TEMP = -2,
    SHT4X_ERR_CRC_RH = -3,
    SHT4X_ERR_PARAM = -4
} sht4x_status_t;

typedef struct {
    float temperature_c;     // Температура повітря, °C
    float relative_humidity; // Відносна вологість, % RH (0.0 .. 100.0)
    float dew_point_c;       // Точка роси, °C
    float absolute_hum_gm3;  // Абсолютна вологість, г/м³
} sht4x_data_t;

// Інтерфейс апаратного рівня (Hardware Abstraction Layer)
typedef struct {
    int (*i2c_write)(uint8_t addr, const uint8_t *data, uint16_t len);
    int (*i2c_read)(uint8_t addr, uint8_t *data, uint16_t len);
    void (*delay_ms)(uint32_t ms);
} sht4x_hal_t;

// Обчислення CRC-8 (поліном 0x31, ініціалізація 0xFF)
static uint8_t sht4x_crc8(const uint8_t *data, uint16_t len) {
    uint8_t crc = 0xFF;
    for (uint16_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x80) {
                crc = (uint8_t)((crc << 1) ^ 0x31);
            } else {
                crc = (uint8_t)(crc << 1);
            }
        }
    }
    return crc;
}

// Розрахунок точки роси та абсолютної вологості за формулою Магнуса
static void sht4x_compute_psychrometrics(sht4x_data_t *res) {
    const float b = 17.62f;
    const float c = 243.12f;
    
    float rh_clamped = res->relative_humidity;
    if (rh_clamped < 0.1f) rh_clamped = 0.1f;
    if (rh_clamped > 100.0f) rh_clamped = 100.0f;
    
    float gamma = logf(rh_clamped / 100.0f) + (b * res->temperature_c) / (c + res->temperature_c);
    res->dew_point_c = (c * gamma) / (b - gamma);
    
    // Парціальний тиск водяної пари (гПа) та абсолютна вологість (г/м³)
    float p_sat = 6.112f * expf((b * res->temperature_c) / (c + res->temperature_c));
    float p_actual = (rh_clamped / 100.0f) * p_sat;
    res->absolute_hum_gm3 = 216.7f * p_actual / (res->temperature_c + 273.15f);
}

sht4x_status_t sht4x_read_sample(const sht4x_hal_t *hal, uint8_t addr, 
                                 sht4x_command_t cmd, sht4x_data_t *result) {
    if (!hal || !hal->i2c_write || !hal->i2c_read || !hal->delay_ms || !result) {
        return SHT4X_ERR_PARAM;
    }

    uint8_t cmd_byte = (uint8_t)cmd;
    if (hal->i2c_write(addr, &cmd_byte, 1) != 0) {
        return SHT4X_ERR_I2C;
    }

    // Затримка на вимірювання згідно зі специфікацією
    uint32_t delay_time = 10;
    if (cmd == SHT4X_CMD_MEASURE_LOW_PREC) delay_time = 2;
    else if (cmd == SHT4X_CMD_MEASURE_MED_PREC) delay_time = 5;
    else if (cmd == SHT4X_CMD_HEATER_200MW_1SEC || cmd == SHT4X_CMD_HEATER_110MW_1SEC || 
             cmd == SHT4X_CMD_HEATER_20MW_1SEC) delay_time = 1100;
    else if (cmd == SHT4X_CMD_HEATER_200MW_0P1SEC || cmd == SHT4X_CMD_HEATER_110MW_0P1SEC || 
             cmd == SHT4X_CMD_HEATER_20MW_0P1SEC) delay_time = 120;
    
    hal->delay_ms(delay_time);

    uint8_t buf[6];
    if (hal->i2c_read(addr, buf, 6) != 0) {
        return SHT4X_ERR_I2C;
    }

    // Перевірка контрольних сум для температури й вологості
    if (sht4x_crc8(&buf[0], 2) != buf[2]) {
        return SHT4X_ERR_CRC_TEMP;
    }
    if (sht4x_crc8(&buf[3], 2) != buf[5]) {
        return SHT4X_ERR_CRC_RH;
    }

    uint16_t raw_temp = ((uint16_t)buf[0] << 8) | buf[1];
    uint16_t raw_rh   = ((uint16_t)buf[3] << 8) | buf[4];

    result->temperature_c = -45.0f + 175.0f * ((float)raw_temp / 65535.0f);
    float rh = -6.0f + 125.0f * ((float)raw_rh / 65535.0f);
    if (rh < 0.0f) rh = 0.0f;
    if (rh > 100.0f) rh = 100.0f;
    result->relative_humidity = rh;

    sht4x_compute_psychrometrics(result);
    return SHT4X_OK;
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <algorithm>
#include <span>
#include <concepts>
#include <expected>
#include <chrono>

namespace sht4x {

enum class Error : int8_t {
    I2cTransport = -1,
    CrcTemperature = -2,
    CrcHumidity = -3,
    InvalidParameter = -4,
    Timeout = -5
};

enum class Precision : uint8_t {
    High = 0xFD,
    Medium = 0xF6,
    Low = 0xE0
};

enum class HeaterMode : uint8_t {
    HighPower1s   = 0x39, // 200 mW, 1.0 s
    HighPower01s  = 0x32, // 200 mW, 0.1 s
    MedPower1s    = 0x2F, // 110 mW, 1.0 s
    MedPower01s   = 0x24, // 110 mW, 0.1 s
    LowPower1s    = 0x1E, //  20 mW, 1.0 s
    LowPower01s   = 0x15  //  20 mW, 0.1 s
};

struct Metrics {
    float temperature_c;     // °C
    float relative_humidity; // % RH [0..100]
    float dew_point_c;       // °C
    float absolute_hum_gm3;  // г/м³
};

// Концепт апаратної шини I2C
template <typename T>
concept I2cBus = requires(T bus, uint8_t addr, std::span<const uint8_t> wr, std::span<uint8_t> rd) {
    { bus.write(addr, wr) } -> std::same_as<bool>;
    { bus.read(addr, rd) } -> std::same_as<bool>;
    { bus.delay_ms(uint32_t{}) } -> std::same_as<void>;
};

template <I2cBus Bus>
class Sht4xDriver {
public:
    static constexpr uint8_t DefaultAddress = 0x44;

    explicit constexpr Sht4xDriver(Bus& bus, uint8_t address = DefaultAddress) noexcept
        : m_bus(bus), m_address(address) {}

    std::expected<Metrics, Error> sample(Precision prec = Precision::High) {
        return execute_measurement(static_cast<uint8_t>(prec), duration_for_precision(prec));
    }

    std::expected<Metrics, Error> trigger_heater(HeaterMode mode) {
        return execute_measurement(static_cast<uint8_t>(mode), duration_for_heater(mode));
    }

    std::expected<void, Error> reset() {
        constexpr uint8_t cmd = 0x94;
        if (!m_bus.write(m_address, std::span<const uint8_t, 1>{&cmd, 1})) {
            return std::unexpected(Error::I2cTransport);
        }
        m_bus.delay_ms(1);
        return {};
    }

private:
    Bus& m_bus;
    uint8_t m_address;

    static constexpr uint8_t calculate_crc8(std::span<const uint8_t> data) noexcept {
        uint8_t crc = 0xFF;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                crc = (crc & 0x80) ? static_cast<uint8_t>((crc << 1) ^ 0x31) 
                                   : static_cast<uint8_t>(crc << 1);
            }
        }
        return crc;
    }

    static constexpr uint32_t duration_for_precision(Precision p) noexcept {
        switch (p) {
            case Precision::Low:    return 2;
            case Precision::Medium: return 5;
            case Precision::High:
            default:                return 10;
        }
    }

    static constexpr uint32_t duration_for_heater(HeaterMode h) noexcept {
        switch (h) {
            case HeaterMode::HighPower1s:
            case HeaterMode::MedPower1s:
            case HeaterMode::LowPower1s:  return 1100;
            default:                      return 120;
        }
    }

    std::expected<Metrics, Error> execute_measurement(uint8_t cmd, uint32_t delay_ms) {
        if (!m_bus.write(m_address, std::span<const uint8_t, 1>{&cmd, 1})) {
            return std::unexpected(Error::I2cTransport);
        }

        m_bus.delay_ms(delay_ms);

        std::array<uint8_t, 6> raw_buf{};
        if (!m_bus.read(m_address, std::span<uint8_t, 6>{raw_buf})) {
            return std::unexpected(Error::I2cTransport);
        }

        if (calculate_crc8(std::span<const uint8_t>{raw_buf.data(), 2}) != raw_buf[2]) {
            return std::unexpected(Error::CrcTemperature);
        }
        if (calculate_crc8(std::span<const uint8_t>{raw_buf.data() + 3, 2}) != raw_buf[5]) {
            return std::unexpected(Error::CrcHumidity);
        }

        const uint16_t raw_t = (static_cast<uint16_t>(raw_buf[0]) << 8) | raw_buf[1];
        const uint16_t raw_rh = (static_cast<uint16_t>(raw_buf[3]) << 8) | raw_buf[4];

        const float temp = -45.0f + 175.0f * (static_cast<float>(raw_t) / 65535.0f);
        const float rh_raw = -6.0f + 125.0f * (static_cast<float>(raw_rh) / 65535.0f);
        const float rh = std::clamp(rh_raw, 0.0f, 100.0f);

        return compute_metrics(temp, rh);
    }

    static Metrics compute_metrics(float temp_c, float rh_pct) noexcept {
        constexpr float b = 17.62f;
        constexpr float c = 243.12f;

        const float rh_safe = std::max(rh_pct, 0.1f);
        const float gamma = std::log(rh_safe / 100.0f) + (b * temp_c) / (c + temp_c);
        const float dew_point = (c * gamma) / (b - gamma);

        const float p_sat = 6.112f * std::exp((b * temp_c) / (c + temp_c));
        const float p_actual = (rh_safe / 100.0f) * p_sat;
        const float abs_hum = 216.7f * p_actual / (temp_c + 273.15f);

        return Metrics{
            .temperature_c = temp_c,
            .relative_humidity = rh_pct,
            .dew_point_c = dew_point,
            .absolute_hum_gm3 = abs_hum
        };
    }
};

} // namespace sht4x
```
:::

### Інженерні аспекти інтеграції та типові помилки

#### 1. Трасування друкованої плати (PCB Layout) та теплові бар'єри
Кристал SHT4x має малу масу і високу теплопровідність кремнію. Будь-який тепловий потік по мідних доріжках від процесора, радіомодуля (Wi-Fi, Bluetooth, LTE) чи імпульсного перетворювача DC-DC нагріває кристал сенсора вище температури навколишнього повітря. Навіть нагрів на 0.5 °C спричиняє заниження показів відносної вологості приблизно на 3 % RH.

Для забезпечення термодинамічної рівноваги застосовують правила топології:
- Розміщуйте сенсор на окремому ізольованому «язичку» (виступі) друкованої плати або якомога далі від гарячих силових компонентів;
- Прорізайте фрезерувальні пази (термобар'єри) у склотекстоліті з трьох сторін навколо корпусу сенсора, щоб перервати теплопровідність склотекстоліту FR4;
- Зменшуйте ширину мідних провідників живлення та сигнальних ліній I²C (не використовуйте суцільні полігони GND безпосередньо під корпусом давача);
- Забезпечте вільну циркуляцію повітря крізь вентиляційні отвори приладового корпусу безпосередньо в зоні сенсорної апертури.

#### 2. Захист від хімічного отруєння та відмивання флюсу
Полімерний діелектрик відкритий для атмосфери через мікропори верхнього електрода. У процесі виробництва електроніки пари каніфолі, леткі компоненти безвідмивних флюсів (No-Clean) та випаровування силіконових герметиків (силоксани) можуть необоротно забруднити полімер, створивши незворотний зсув базової лінії вологості на 5–10 % RH.

Правила виробничого циклу:
- Використовуйте захисну версію сенсора з вбудованою політетрафторетиленовою (ePTFE) мембраною (наприклад, SHT40-AD1B) або заклеюйте вентиляційний отвір захисною термостійкою стрічкою Kapton перед пайкою оплавленням (Reflow soldering);
- Категорично заборонено наносити захисні вологозахисні лаки (Conformal Coating) методом розпилення поверх встановленого сенсора — лакування плати вимагає індивідуального маскування корпусу;
- Після паяння рекомендовано витримати плати в чистому приміщенні протягом 24 годин при відносній вологості 50–70 % RH для природної регідратації полімерної плівки.

#### 3. Відновлення завислої шини I²C (Bus Recovery)
Якщо мікроконтролер перезавантажується під час виконання транзакції зчитування, коли сенсор передає логічний нуль на лінії SDA, шина I²C може заблокуватися: сенсор тримає лінію SDA притиснутою до землі, очікуючи чергових тактових імпульсів SCL.

Для надійного виходу з цього стану в ініціалізацію драйвера вбудовують процедуру примусового відновлення шини (Bus Clear):
1. Налаштувати вивід SCL як вихід із відкритим стоком (Open-Drain), а лінію SDA — як вхід;
2. Згенерувати від 9 до 16 імпульсів тактування на лінії SCL з частотою близько 100 кГц;
3. Перевірити, чи відпустив сенсор лінію SDA (рівень повинен піднятися до логічної одиниці через резистор підтяжки Pull-Up);
4. Згенерувати сигнал аварійної зупинки I²C STOP condition (перепад SDA з низького рівня на високий при високому рівні SCL);
5. Переініціалізувати апаратний блок I²C мікроконтролера та надіслати команду програмного скидання чипа `0x94`.

#### 4. Енергоспоживання та самонагрів в автономних вузлах
У режимі сну (Idle/Sleep) сенсор споживає лише 80 нА при напрузі 3.3 В. Енергія одного 16-бітного вимірювання становить близько 1.5 мкДж. При опитуванні один раз на хвилину середній струм споживання не перевищує 0.4 мкА, що забезпечує понад 10 років безперервної роботи від однієї літієвої дискової батарейки CR2032.

Самонагрів сенсора при частоті опитування 1 вимірювання/хвилину складає менше `0.001 °C`, що повністю усуває теплову похибку вимірювання вологості. Якщо ж прилад працює в режимі безперервного моніторингу (наприклад, 10 вимірювань за секунду), внутрішнє розсіювання потужності викликає самонагрів кристала на 0.15–0.3 °C, що вимагає програмного коригування температури в прошивці.
