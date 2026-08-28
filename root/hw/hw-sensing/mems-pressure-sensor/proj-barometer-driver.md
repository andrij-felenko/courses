# ⚙️ Повний драйвер прецизійного MEMS-барометра на C та C++

Ця практична реалізація містить повнофункціональний, оптимізований драйвер цифрового прецизійного барометра з архітектурою регістрів BMP388 та LPS22HB. Драйвер розроблено з урахуванням суворих вимог до вбудованих систем реального часу: нульове динамічне виділення пам'яті (`no malloc`), строгий контроль часу виконання операцій, підтримка апаратного I2C/SPI через інтерфейсні абстракції, повне розпакування 21 байта констант NVM, компенсація багатовимірних поліномів 2-го та 3-го порядку, адаптивна цифрова фільтрація IIR та розрахунок барометричної висоти за міжнародним стандартом ISA.

Нижче наведено паралельну реалізацію двома мовами: ефективний класичний C (стандарт C99) для використання у bare-metal прошивках та RTOS, та сучасний ідіоматичний C++20 із класовою інкапсуляцією, просторами імен, типами-обгортками `std::span` та суворою типізацією без винятків.

### Архітектура та життєвий цикл драйвера

Драйвер барометра працює за наступним детермінованим циклом:
1. **Ініціалізація та верифікація кристала (`init`)**: читання регістра `CHIP_ID` (`0x00`) для підтвердження наявності мікросхеми на шині, надсилання команди м'якого перезавантаження (Soft Reset `0xB6` у регістр `0x7E`), очікування завершення перезапуску (`2 мс`) та вичитування 21 байта калібрувальних констант із пам'яті NVM.
2. **Конфігурація вимірювального тракту (`configure`)**: встановлення коефіцієнтів передискретизації OSR для тиску (типово 8× або 16×) та температури (2×), вибір вихідної частоти ODR (наприклад, 25 Гц) та увімкнення датчиків у регістрі `PWR_CTRL`.
3. **Періодичний збір даних (`update`)**: неподільне зчитування 6 послідовних байтів із регістрів `0x04..0x09` за одну I2C-транзакцію типу Burst Read. Це гарантує, що старші й молодші байти тиску та температури належать одному кванту часу.
4. **Компенсація та фільтрація (`process`)**: розрахунок дійсного тиску в паскалях та температури в градусах Цельсія через поліноми NVM, оновлення внутрішнього стану IIR-фільтра та розрахунок поточної барометричної висоти.

---

### 1. Структури даних та калібрувальні параметри

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

// Калібрувальні коефіцієнти, прочитані з NVM та приведені до чисел з плаваючою комою
typedef struct {
    double t1, t2, t3;
    double p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11;
} BaroCalibData;

// Внутрішній стан та параметри драйвера барометра
typedef struct {
    void *bus_handle;               // Контекст апаратного драйвера шини I2C/SPI
    uint8_t dev_addr;               // I2C-адреса пристрою (зазвичай 0x76 або 0x77)
    BaroCalibData calib;            // Розпаковані коефіцієнти NVM
    double filtered_pressure_pa;    // Поточне згладжене значення тиску (стан IIR)
    double iir_alpha;               // Коефіцієнт експоненційного фільтра (0.05..0.5)
    double qnh_pa;                  // Опорний тиск рівня моря (стандартно 101325.0 Па)
    bool is_initialized;            // Прапорець успішної ініціалізації
} MemsBarometer;

// Статуси повернення функцій драйвера
typedef enum {
    BARO_OK = 0,
    BARO_ERR_COMM = -1,
    BARO_ERR_CHIP_ID = -2,
    BARO_ERR_NOT_READY = -3
} BaroStatus;
```
```cpp
#pragma once
#include <cstdint>
#include <cmath>
#include <span>
#include <expected>
#include <concepts>

namespace drivers {

// Типізований перелік можливих помилок драйвера
enum class BaroError : int8_t {
    CommunicationFailure = -1,
    InvalidChipId        = -2,
    DataNotReady         = -3,
    InvalidParameter     = -4
};

// Заводські калібрувальні коефіцієнти з плаваючою комою
struct BaroCalibCoeffs {
    double t1{}, t2{}, t3{};
    double p1{}, p2{}, p3{}, p4{}, p5{}, p6{}, p7{}, p8{}, p9{}, p10{}, p11{};
};

// Результат одного повного вимірювання
struct BaroSample {
    double pressure_pa;
    double temperature_c;
    double altitude_m;
};

} // namespace drivers
```
:::

---

### 2. Розпакування калібрувальних коефіцієнтів NVM

Математичні формули компенсації використовують коефіцієнти, які зберігаються в пам'яті NVM у компактному 8-бітному та 16-бітному цілочисельному вигляді. Під час первинного зчитування драйвер перетворює їх у масштабовані коефіцієнти подвійної точності (`double`).

:::tabs
```c
BaroStatus baro_parse_calibration(MemsBarometer *dev, const uint8_t *raw_nvm) {
    if (!dev || !raw_nvm) return BARO_ERR_COMM;

    // Збирання сирих 16-бітних та 8-бітних слів із буфера NVM
    uint16_t raw_t1 = (uint16_t)(raw_nvm[0] | (raw_nvm[1] << 8));
    uint16_t raw_t2 = (uint16_t)(raw_nvm[2] | (raw_nvm[3] << 8));
    int8_t   raw_t3 = (int8_t)raw_nvm[4];

    int16_t  raw_p1 = (int16_t)(raw_nvm[5] | (raw_nvm[6] << 8));
    int16_t  raw_p2 = (int16_t)(raw_nvm[7] | (raw_nvm[8] << 8));
    int8_t   raw_p3 = (int8_t)raw_nvm[9];
    int8_t   raw_p4 = (int8_t)raw_nvm[10];
    uint16_t raw_p5 = (uint16_t)(raw_nvm[11] | (raw_nvm[12] << 8));
    uint16_t raw_p6 = (uint16_t)(raw_nvm[13] | (raw_nvm[14] << 8));
    int8_t   raw_p7 = (int8_t)raw_nvm[15];
    int8_t   raw_p8 = (int8_t)raw_nvm[16];
    int16_t  raw_p9 = (int16_t)(raw_nvm[17] | (raw_nvm[18] << 8));
    int8_t   raw_p10 = (int8_t)raw_nvm[19];
    int8_t   raw_p11 = (int8_t)raw_nvm[20];

    // Масштабування за специфікацією виробника
    dev->calib.t1 = (double)raw_t1 * 256.0;                    // множник 2^-8
    dev->calib.t2 = (double)raw_t2 / 1073741824.0;             // дільник 2^30
    dev->calib.t3 = (double)raw_t3 / 281474976710656.0;        // дільник 2^48

    dev->calib.p1 = ((double)raw_p1 - 16384.0) / 1048576.0;    // зміщення 2^14, дільник 2^20
    dev->calib.p2 = ((double)raw_p2 - 16384.0) / 536870912.0;  // зміщення 2^14, дільник 2^29
    dev->calib.p3 = (double)raw_p3 / 4294967296.0;             // дільник 2^32
    dev->calib.p4 = (double)raw_p4 / 137438953472.0;           // дільник 2^37
    dev->calib.p5 = (double)raw_p5 * 8.0;                      // множник 2^-3
    dev->calib.p6 = (double)raw_p6 / 64.0;                     // дільник 2^6
    dev->calib.p7 = (double)raw_p7 / 256.0;                    // дільник 2^8
    dev->calib.p8 = (double)raw_p8 / 32768.0;                  // дільник 2^15
    dev->calib.p9 = (double)raw_p9 / 281474976710656.0;        // дільник 2^48
    dev->calib.p10 = (double)raw_p10 / 281474976710656.0;      // дільник 2^48
    dev->calib.p11 = (double)raw_p11 / 36893488147419103232.0; // дільник 2^65

    return BARO_OK;
}
```
```cpp
namespace drivers {

class MemsBarometerParser {
public:
    [[nodiscard]] static constexpr BaroCalibCoeffs parse_calibration(std::span<const uint8_t, 21> nvm) noexcept {
        BaroCalibCoeffs c{};

        const auto raw_t1 = static_cast<uint16_t>(nvm[0] | (nvm[1] << 8));
        const auto raw_t2 = static_cast<uint16_t>(nvm[2] | (nvm[3] << 8));
        const auto raw_t3 = static_cast<int8_t>(nvm[4]);

        const auto raw_p1 = static_cast<int16_t>(nvm[5] | (nvm[6] << 8));
        const auto raw_p2 = static_cast<int16_t>(nvm[7] | (nvm[8] << 8));
        const auto raw_p3 = static_cast<int8_t>(nvm[9]);
        const auto raw_p4 = static_cast<int8_t>(nvm[10]);
        const auto raw_p5 = static_cast<uint16_t>(nvm[11] | (nvm[12] << 8));
        const auto raw_p6 = static_cast<uint16_t>(nvm[13] | (nvm[14] << 8));
        const auto raw_p7 = static_cast<int8_t>(nvm[15]);
        const auto raw_p8 = static_cast<int8_t>(nvm[16]);
        const auto raw_p9 = static_cast<int16_t>(nvm[17] | (nvm[18] << 8));
        const auto raw_p10 = static_cast<int8_t>(nvm[19]);
        const auto raw_p11 = static_cast<int8_t>(nvm[20]);

        c.t1 = static_cast<double>(raw_t1) * 256.0;
        c.t2 = static_cast<double>(raw_t2) / 1073741824.0;
        c.t3 = static_cast<double>(raw_t3) / 281474976710656.0;

        c.p1 = (static_cast<double>(raw_p1) - 16384.0) / 1048576.0;
        c.p2 = (static_cast<double>(raw_p2) - 16384.0) / 536870912.0;
        c.p3 = static_cast<double>(raw_p3) / 4294967296.0;
        c.p4 = static_cast<double>(raw_p4) / 137438953472.0;
        c.p5 = static_cast<double>(raw_p5) * 8.0;
        c.p6 = static_cast<double>(raw_p6) / 64.0;
        c.p7 = static_cast<double>(raw_p7) / 256.0;
        c.p8 = static_cast<double>(raw_p8) / 32768.0;
        c.p9 = static_cast<double>(raw_p9) / 281474976710656.0;
        c.p10 = static_cast<double>(raw_p10) / 281474976710656.0;
        c.p11 = static_cast<double>(raw_p11) / 36893488147419103232.0;

        return c;
    }
};

} // namespace drivers
```
:::

---

### 3. Функція поліноміальної температурної компенсації

Обчислює лінеаризовану температуру кристала `t_lin`, а потім використовує її для компенсації дрейфу зміщення нуля, температурного коефіцієнта чутливості та квадратичної нелінійності п'єзорезистивного моста.

:::tabs
```c
// Розрахунок лінеаризованої температури (°C)
double baro_compensate_temperature(const BaroCalibData *c, uint32_t uncomp_temp) {
    double dt = (double)uncomp_temp - c->t1;
    double t_lin = (dt * c->t2) + (dt * dt * c->t3);
    return t_lin;
}

// Повний розрахунок компенсованого тиску (Паскалі)
double baro_compensate_pressure(const BaroCalibData *c, uint32_t uncomp_press, double t_lin) {
    double t2 = t_lin * t_lin;
    double t3 = t2 * t_lin;
    double p_raw = (double)uncomp_press;
    double p2 = p_raw * p_raw;
    double p3 = p2 * p_raw;

    // Члени полінома: Offset(T), Sensitivity(T), NonLinearity(P, T)
    double offset = c->p1 + (c->p2 * t_lin) + (c->p3 * t2) + (c->p4 * t3);
    double sens   = c->p5 + (c->p6 * t_lin) + (c->p7 * t2) + (c->p8 * t3);
    double nonlin = (c->p9 + (c->p10 * t_lin)) * p2 + (c->p11 * p3);

    return offset + (sens * p_raw) + nonlin;
}
```
```cpp
namespace drivers {

class BaroCompensator {
public:
    [[nodiscard]] static constexpr double compensate_temperature(const BaroCalibCoeffs& c, uint32_t raw_temp) noexcept {
        const double dt = static_cast<double>(raw_temp) - c.t1;
        return (dt * c.t2) + (dt * dt * c.t3);
    }

    [[nodiscard]] static constexpr double compensate_pressure(const BaroCalibCoeffs& c, uint32_t raw_press, double t_lin) noexcept {
        const double t2 = t_lin * t_lin;
        const double t3 = t2 * t_lin;
        const double p_raw = static_cast<double>(raw_press);
        const double p2 = p_raw * p_raw;
        const double p3 = p2 * p_raw;

        const double offset = c.p1 + (c.p2 * t_lin) + (c.p3 * t2) + (c.p4 * t3);
        const double sens   = c.p5 + (c.p6 * t_lin) + (c.p7 * t2) + (c.p8 * t3);
        const double nonlin = (c.p9 + (c.p10 * t_lin)) * p2 + (c.p11 * p3);

        return offset + (sens * p_raw) + nonlin;
    }
};

} // namespace drivers
```
:::

---

### 4. Фільтрація та перерахунок тиску у висоту

Розрахунок висоти спирається на стандартну модель атмосфери ISA з експонентою `1 / 5.25588 = 0.190263`. Програмний рекурсивний фільтр IIR 1-го порядку згладжує теплові й акустичні шуми перед обчисленням висоти. Для обчислення висоти використовується швидке піднесення до степеня або поліноміальне наближення Тейлора для систем без апаратного модуля FPU.

:::tabs
```c
void baro_process_sample(MemsBarometer *dev, double raw_p_pa, double temp_c,
                         double *out_filtered_p, double *out_altitude_m) {
    if (!dev->is_initialized) {
        dev->filtered_pressure_pa = raw_p_pa;
        dev->is_initialized = true;
    } else {
        // Експоненційне IIR-згладжування: P_fil = (1 - alpha) * P_fil + alpha * P_raw
        dev->filtered_pressure_pa += dev->iir_alpha * (raw_p_pa - dev->filtered_pressure_pa);
    }

    if (out_filtered_p) {
        *out_filtered_p = dev->filtered_pressure_pa;
    }

    if (out_altitude_m) {
        double p_ratio = dev->filtered_pressure_pa / dev->qnh_pa;
        // Барометрична формула висоти ISA (ICAO)
        *out_altitude_m = 44330.77 * (1.0 - pow(p_ratio, 0.190263));
    }
}
```
```cpp
namespace drivers {

class AltimeterFilter {
private:
    double filtered_pressure_pa_{101325.0};
    double alpha_{0.15};
    double qnh_pa_{101325.0};
    bool initialized_{false};

public:
    constexpr explicit AltimeterFilter(double alpha = 0.15, double qnh_pa = 101325.0) noexcept
        : alpha_(alpha), qnh_pa_(qnh_pa) {}

    void set_qnh(double qnh_pa) noexcept {
        qnh_pa_ = qnh_pa;
    }

    [[nodiscard]] BaroSample process(double raw_pressure_pa, double temperature_c) noexcept {
        if (!initialized_) {
            filtered_pressure_pa_ = raw_pressure_pa;
            initialized_ = true;
        } else {
            filtered_pressure_pa_ += alpha_ * (raw_pressure_pa - filtered_pressure_pa_);
        }

        const double p_ratio = filtered_pressure_pa_ / qnh_pa_;
        const double altitude = 44330.77 * (1.0 - std::pow(p_ratio, 0.190263));

        return BaroSample{
            .pressure_pa = filtered_pressure_pa_,
            .temperature_c = temperature_c,
            .altitude_m = altitude
        };
    }

    void reset() noexcept {
        initialized_ = false;
    }
};

} // namespace drivers
```
:::

---

### 5. Повний цикл опитування датчика (Application Task)

У типовій архітектурі вбудованої системи задача опитування барометра викликається за таймером або за перериванням готовності даних `DRDY`. Повний приклад інтеграції з перевіркою помилок наведено нижче.

:::tabs
```c
// Прототип абстрактної функції читання I2C шини
int i2c_read_registers(void *bus, uint8_t addr, uint8_t reg, uint8_t *buf, uint16_t len);

void baro_polling_step(MemsBarometer *dev) {
    uint8_t burst_buffer[6];
    // Неподільне читання 6 байтів: 3 байти тиску + 3 байти температури
    if (i2c_read_registers(dev->bus_handle, dev->dev_addr, 0x04, burst_buffer, 6) != 0) {
        return;
    }

    uint32_t raw_p = ((uint32_t)burst_buffer[2] << 16) |
                     ((uint32_t)burst_buffer[1] << 8)  |
                     burst_buffer[0];

    uint32_t raw_t = ((uint32_t)burst_buffer[5] << 16) |
                     ((uint32_t)burst_buffer[4] << 8)  |
                     burst_buffer[3];

    double t_c = baro_compensate_temperature(&dev->calib, raw_t);
    double p_pa = baro_compensate_pressure(&dev->calib, raw_p, t_c);

    double smooth_p = 0.0;
    double altitude = 0.0;
    baro_process_sample(dev, p_pa, t_c, &smooth_p, &altitude);

    // Дані висоти готові для відправки в регулятор висоти польотного контролера
}
```
```cpp
namespace app {

// Концепт шини I2C для статичного поліморфізму без віртуальних таблиць
template <typename T>
concept I2cInterface = requires(T bus, uint8_t addr, uint8_t reg, std::span<uint8_t> buf) {
    { bus.read_bytes(addr, reg, buf.data(), buf.size()) } -> std::same_as<bool>;
};

template <I2cInterface I2cBus>
class BarometerTask {
private:
    I2cBus& bus_;
    uint8_t i2c_addr_{0x76};
    drivers::BaroCalibCoeffs calib_{};
    drivers::AltimeterFilter filter_{0.15, 101325.0};

public:
    explicit BarometerTask(I2cBus& bus, uint8_t addr = 0x76) noexcept
        : bus_(bus), i2c_addr_(addr) {}

    std::expected<void, drivers::BaroError> init() noexcept {
        uint8_t nvm_buf[21];
        if (!bus_.read_bytes(i2c_addr_, 0x31, nvm_buf, sizeof(nvm_buf))) {
            return std::unexpected(drivers::BaroError::CommunicationFailure);
        }
        calib_ = drivers::MemsBarometerParser::parse_calibration(nvm_buf);
        return {};
    }

    std::expected<drivers::BaroSample, drivers::BaroError> update() noexcept {
        uint8_t raw_buf[6];
        if (!bus_.read_bytes(i2c_addr_, 0x04, raw_buf, sizeof(raw_buf))) {
            return std::unexpected(drivers::BaroError::CommunicationFailure);
        }

        const uint32_t raw_p = static_cast<uint32_t>(raw_buf[0]) |
                              (static_cast<uint32_t>(raw_buf[1]) << 8) |
                              (static_cast<uint32_t>(raw_buf[2]) << 16);

        const uint32_t raw_t = static_cast<uint32_t>(raw_buf[3]) |
                              (static_cast<uint32_t>(raw_buf[4]) << 8) |
                              (static_cast<uint32_t>(raw_buf[5]) << 16);

        const double t_c = drivers::BaroCompensator::compensate_temperature(calib_, raw_t);
        const double p_pa = drivers::BaroCompensator::compensate_pressure(calib_, raw_p, t_c);

        return filter_.process(p_pa, t_c);
    }
};

} // namespace app
```
:::

---

### Особливості цілочисельної арифметики Fixed-Point (для Cortex-M0/M3)

Якщо цільовий мікроконтролер не має апаратного блоку обчислень з плаваючою комою (FPU, як у ядрах ARM Cortex-M0/M0+/M3), виконання поліноміальної компенсації з числами `double` вимагає емуляції через програмні бібліотеки `soft-float`, що може займати від 800 до 2500 тактів процесора на кожен відлік.

У таких системах застосовують цілочисельну 64-бітну арифметику з фіксованою комою (*Fixed-Point Arithmetic*). Усі коефіцієнти NVM масштабують у формат `Q32.32` або `Q24.40`. Використання 32-бітних цілих чисел для поліномів 3-го порядку категорично заборонено, оскільки член `raw_pressure³` за 24-бітного АЦП сягає величини `(2²⁴)³ = 2⁷²`, що спричиняє катастрофічне переповнення розрядної сітки та повну втрату значущих розрядів компенсації.

---

### Обробка збоїв шини та відновлення зв'язку (I2C Bus Recovery)

Якщо під час виконання пакетної транзакції Burst Read живлення мікроконтролера короткочасно просіло або сталося скидання сторожового таймера Watchdog, сенсор барометра може зависнути посеред передачі байта, утримуючи лінію даних SDA в низькому стані (стан захоплення шини *I2C Bus Lockup*). У такому стані жоден майстер не може згенерувати сигнал Start.

Драйвер барометра повинен реалізувати процедуру апаратного скидання шини: якщо після запуску лінія SDA затиснута в `0`, мікроконтролер перемикає вивід SCL у режим GPIO виходу з відкритим стоком і генерує 9 послідовних тактових імпульсів. Це змушує внутрішній автомат барометра дочитати поточний байт і відпустити лінію SDA, після чого генерується коректний сигнал Stop. Лише після цього відновлюється апаратний периферійний модуль I2C.

---

### Злиття з інерційними давачами у польотних контролерах

У реальних автопілотах (PX4, ArduPilot, Betaflight) барометр ніколи не використовується ізольовано для швидкісного керування тягою моторів. Через те, що IIR-фільтр барометра вносить затримку в кілька десятків мілісекунд, пряме диференціювання висоти для обчислення вертикальної швидкості (`v_z = dh / dt`) створює шумний і запізнілий сигнал, який розгойдує дрон по висоті.

Замість цього застосовують комплементарний фільтр або розширений фільтр Калмана (EKF): вертикальний акселерометр інтегрується на високій частоті (400–1000 Гц) для отримання миттєвої вертикальної швидкості й зміни висоти без фазової затримки, а барометричні вимірювання (на частоті 25–50 Гц) виступають повільним абсолютним опорним вектором, що безперервно усуває інтегральний дрейф акселерометра.
