# ⚙️ Прецизійний вимір температури з RTD PT100 на 24-бітному АЦП ADS1220

<preknowlist>
- [Вибірка і зберігання в АЦП](root:hw-analog/adc-sample-hold) — процес фіксації вхідної напруги на ємнісному модулі.
- [ENOB: скільки розрядів справді працюють](root:hw-analog/enob) — ефективна роздільна здатність з урахуванням шуму квантування.
- [Джерела опорної напруги](root:hw-analog/voltage-reference-sources) — стабільність опорної напруги та логометричний принцип.
- [SPI: швидкість і лінії](root:com-devices/spi-lines) — протокол синхронної послідовної передачі даних.
</preknowlist>

Вимірювання температури за допомогою платинового терморезистора (англ. *Resistance Temperature Detector*, RTD) PT100 вимагає виняткової роздільної здатності. Опір датчика PT100 при 0 °C становить рівно 100.00 Ом, а температурний коефіцієнт платини дорівнює близько 0.385 Ом/°C. Якщо необхідно вимірювати температуру з точністю до 0.01 °C, вимірювальний тракт повинен надійно розрізняти зміну опору в 0.00385 Ом. При вимірювальному струмі 500 мкА ця зміна опору створює корисний сигнал напруги величиною лише:

```
ΔV = I_ex · ΔR
ΔV = 500·10⁻⁶ А · 0.00385 Ом = 1.925·10⁻⁶ В = 1.925 мкВ
```

Вбудований 12-бітний АЦП мікроконтролера з кроком квантування ~800 мкВ повністю сліпий до таких величин: один мінімальний крок його перетворення перекриває діапазон у понад 400 градусів Цельсія.

Для вирішення цієї задачі застосовується спеціалізований 24-бітний дельта-сигма АЦП ADS1220 (Texas Instruments). Цей перетворювач інтегрує малошумний програмований підсилювач ([PGA](root:hw-analog/instrumentation-amp)), два узгоджені генератори струму збудження (IDAC1, IDAC2) та гнучкий мультиплексор. Розгляньмо повну схемотехніку 3-провідного підключення PT100, логометричний розрахунок, обробку переривань та закінчену програмну реалізацію драйвера.

## 1. Схемотехніка: 3-провідне підключення та компенсація опору дротів

У промислових установках датчик температури часто віддалений від плати на десятки метрів. Опір з'єднувальних мідних дротів `R_lead` може становити від 0.5 до 5 Ом на лінію, що без компенсації дає похибку вимірювання від 1.3 °C до 13 °C.

3-провідна схема усуває цей вплив завдяки двом однаковим струмам збудження `I_idac1 = I_idac2 = 500 мкА`:

1. Струм `I_idac1` виходить із виводу `AIN0` і тече крізь перший дріт `R_lead1`, платиновий сенсор `R_pt100`, третій дріт `R_lead3` та еталонний резистор `R_ref = 3.3 кОм (0.01%, 5 ppm/°C)` на землю.
2. Струм `I_idac2` виходить із виводу `AIN1` і тече крізь другий дріт `R_lead2`, третій дріт `R_lead3` та `R_ref` на землю.
3. Диференційний вхід АЦП підключається між виводами `AIN1` (плюс) та `AIN2` (мінус).

Напруга на вході АЦП становить:

```
V_in = (I_idac1 · (R_lead1 + R_pt100) + (I_idac1 + I_idac2) · R_lead3) - (I_idac2 · R_lead2 + (I_idac1 + I_idac2) · R_lead3)
```

Якщо дроти однакові (`R_lead1 = R_lead2`), а генератори струму точно збігаються (`I_idac1 = I_idac2 = I`), члени з опором дротів взаємно віднімаються:

```
V_in = I · R_lead1 + I · R_pt100 - I · R_lead2
V_in = I · R_pt100    [при R_lead1 = R_lead2]
```

## 2. Логометричний принцип: усунення дрейфу струму

Опорна напруга `V_ref` для АЦП формується спадом напруги на еталонному прецизійному резисторі `R_ref`, крізь який протікає сумарний струм обох генераторів:

```
V_ref = (I_idac1 + I_idac2) · R_ref = 2 · I · R_ref
```

Вихідний цифровий код 24-бітного АЦП для диференційного входу з коефіцієнтом підсилення `Gain` визначається відношенням:

```
Code = 2²³ · (V_in · Gain) / V_ref
Code = 2²³ · (I · R_pt100 · Gain) / (2 · I · R_ref)
Code = 2²³ · (R_pt100 · Gain) / (2 · R_ref)
```

Струм збудження `I` повністю скорочується в чисельнику та знаменнику. Температурний дрейф та абсолютна похибка струмів IDAC не впливають на результат вимірювання — точність залежить винятково від стабільності резистора `R_ref`.

Опір платинового термометра вираховується з коду:

```
R_pt100 = (Code · 2 · R_ref) / (2²³ · Gain)
```

## 3. Лінеаризація: рівняння Каллендара-Ван Дюзена

Залежність електричного опору платини від температури описується рівнянням Каллендара-Ван Дюзена (англ. *Callendar-Van Dusen equation*).

Для температур вище 0 °C (`0 °C <= T <= 850 °C`) рівняння є квадратичним:

```
R(T) = R_0 · (1 + A·T + B·T²)
```

де стандартні коефіцієнти для платини з характеристикою DIN/IEC 60751 становлять:
- `R_0 = 100.00 Ом` (опір при 0 °C);
- `A = 3.9083·10⁻³ °C⁻¹`;
- `B = -5.7750·10⁻⁷ °C⁻²`.

Аналітичний розв'язок квадратного рівняння відносно температури `T` має вигляд:

```
T = (-A + √(A² - 4·B·(1 - R_pt100 / R_0))) / (2·B)
```

Для від'ємних температур (`-200 °C <= T < 0 °C`) додається кубічний член з коефіцієнтом `C = -4.1830·10⁻¹² °C⁻⁴`:

```
R(T) = R_0 · (1 + A·T + B·T² + C·(T - 100)·T³)
```

У мікроконтролері для від'ємного діапазону застосовують ітераційний метод Ньютона-Рафсона (англ. *Newton-Raphson method*), який за 2–3 ітерації сходиться до істинного значення з похибкою менше ніж 0.001 °C.

## 4. Драйвер ADS1220: конфігурація та апаратне переривання DRDY

ADS1220 має чотири 8-бітні конфігураційні регістри (`WREG` / `RREG`), які визначають режим мультиплексора, коефіцієнт підсилення PGA, швидкість вибірки, підключення струмів IDAC та вибір джерела опорної напруги.

Для нашої схеми записуються такі значення:
- **Регістр 0 (0x00):** `MUX = AIN1-AIN2 (0x30)`, `Gain = 16 (0x08)`, `PGA Enabled (0x00)` → `0x38`.
- **Регістр 1 (0x01):** `DR = 20 SPS (0x00)`, `Mode = Normal (0x00)`, `CM = Single-shot (0x00)`, `TS = Off (0x00)`, `BC = Off (0x00)` → `0x00`.
- **Регістр 2 (0x02):** `VREF = External REFP0/REFN0 (0x40)`, `FIR = 50/60 Hz simultaneous rejection (0x30)`, `PSW = Off (0x00)`, `IDAC = 500 uA (0x06)` → `0x76`.
- **Регістр 3 (0x03):** `I1MUX = AIN0 (0x20)`, `I2MUX = AIN1 (0x40)`, `DRDY mode = dedicated (0x00)` → `0x60`.

Замість блокуючих затримок процесора опитуванням завершення перетворення слугує апаратний вивід `DRDY` (Data Ready). Коли перетворення закінчено, АЦП притискає лінію `DRDY` до низького логічного рівня, генеруючи зовнішнє переривання мікроконтролера.

Нижче наведено закінчену реалізацію драйвера мовами C та сучасним C++ (C++20).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Команди ADS1220 */
#define ADS1220_CMD_RESET    0x06
#define ADS1220_CMD_START    0x08
#define ADS1220_CMD_RDATA    0x10
#define ADS1220_CMD_RREG     0x20
#define ADS1220_CMD_WREG     0x40

/* Конфігураційні константи */
#define PT100_R0             100.0f
#define PT100_A              3.9083e-3f
#define PT100_B              -5.7750e-7f
#define PT100_C              -4.1830e-12f
#define R_REF_NOMINAL        3300.0f
#define PGA_GAIN             16.0f

typedef struct {
    void (*spi_cs_low)(void);
    void (*spi_cs_high)(void);
    void (*spi_transfer)(const uint8_t *tx, uint8_t *rx, uint16_t len);
    bool (*wait_drdy_low)(uint32_t timeout_ms);
} ads1220_hal_t;

typedef struct {
    ads1220_hal_t hal;
    float r_ref;
    float gain;
    int32_t offset_code;
} ads1220_t;

/* Ініціалізація та налаштування регістрів ADS1220 для 3-провідного PT100 */
bool ads1220_init(ads1220_t *dev, const ads1220_hal_t *hal) {
    if (!dev || !hal) return false;
    dev->hal = *hal;
    dev->r_ref = R_REF_NOMINAL;
    dev->gain = PGA_GAIN;
    dev->offset_code = 0;

    /* Скидання мікросхеми */
    uint8_t cmd_reset = ADS1220_CMD_RESET;
    dev->hal.spi_cs_low();
    dev->hal.spi_transfer(&cmd_reset, NULL, 1);
    dev->hal.spi_cs_high();

    /* Запис 4 конфігураційних регістрів */
    uint8_t config[5];
    config[0] = ADS1220_CMD_WREG | 0x03; /* Запис 4 байтів починаючи з регістру 0 */
    config[1] = 0x38; /* AIN1-AIN2, Gain=16, PGA on */
    config[2] = 0x00; /* 20 SPS, Normal mode, Single-shot */
    config[3] = 0x76; /* Зовнішня опора REFP0/REFN0, фільтр 50/60 Гц, IDAC=500 мкА */
    config[4] = 0x60; /* IDAC1 -> AIN0, IDAC2 -> AIN1 */

    dev->hal.spi_cs_low();
    dev->hal.spi_transfer(config, NULL, 5);
    dev->hal.spi_cs_high();

    return true;
}

/* Калібрування внутрішнього зсуву нуля АЦП через тестове замикання входів */
bool ads1220_calibrate_offset(ads1220_t *dev) {
    if (!dev) return false;

    /* Вмикання режиму (AVDD + AVSS)/2 на обох входах для виміру зміщення */
    uint8_t reg0_cal = 0xE8; /* MUX = (AVDD-AVSS)/2, Gain=16 */
    uint8_t cmd[2] = { (uint8_t)(ADS1220_CMD_WREG | 0x00), reg0_cal };
    
    dev->hal.spi_cs_low();
    dev->hal.spi_transfer(cmd, NULL, 2);
    dev->hal.spi_cs_high();

    /* Запуск та читання тестового відліку */
    uint8_t cmd_start = ADS1220_CMD_START;
    dev->hal.spi_cs_low();
    dev->hal.spi_transfer(&cmd_start, NULL, 1);
    dev->hal.spi_cs_high();

    if (!dev->hal.wait_drdy_low(60)) return false;

    uint8_t tx_buf[4] = { ADS1220_CMD_RDATA, 0x00, 0x00, 0x00 };
    uint8_t rx_buf[4] = { 0 };

    dev->hal.spi_cs_low();
    dev->hal.spi_transfer(tx_buf, rx_buf, 4);
    dev->hal.spi_cs_high();

    int32_t offset = ((int32_t)rx_buf[1] << 16) |
                     ((int32_t)rx_buf[2] << 8)  |
                     ((int32_t)rx_buf[3]);
    if (offset & 0x00800000) offset |= 0xFF000000;
    dev->offset_code = offset;

    /* Відновлення робочої конфігурації входу */
    cmd[1] = 0x38;
    dev->hal.spi_cs_low();
    dev->hal.spi_transfer(cmd, NULL, 2);
    dev->hal.spi_cs_high();

    return true;
}

/* Запуск вимірювання та зчитування 24-бітного результату */
bool ads1220_read_raw(ads1220_t *dev, int32_t *raw_code) {
    if (!dev || !raw_code) return false;

    uint8_t cmd_start = ADS1220_CMD_START;
    dev->hal.spi_cs_low();
    dev->hal.spi_transfer(&cmd_start, NULL, 1);
    dev->hal.spi_cs_high();

    /* Очікування сигналу DRDY за апаратним перериванням або тайм-аутом */
    if (!dev->hal.wait_drdy_low(60)) {
        return false;
    }

    uint8_t tx_buf[4] = { ADS1220_CMD_RDATA, 0x00, 0x00, 0x00 };
    uint8_t rx_buf[4] = { 0 };

    dev->hal.spi_cs_low();
    dev->hal.spi_transfer(tx_buf, rx_buf, 4);
    dev->hal.spi_cs_high();

    /* Збирання 24-бітного числа зі знаком */
    int32_t code = ((int32_t)rx_buf[1] << 16) |
                   ((int32_t)rx_buf[2] << 8)  |
                   ((int32_t)rx_buf[3]);

    /* Доповнення знакового розряду для 24-бітного значення */
    if (code & 0x00800000) {
        code |= 0xFF000000;
    }

    /* Компенсація каліброваного апаратного зміщення */
    *raw_code = code - dev->offset_code;
    return true;
}

/* Перерахунок коду в опір та температуру за рівнянням Каллендара-Ван Дюзена */
bool ads1220_read_temperature(ads1220_t *dev, float *temp_celsius) {
    int32_t raw_code = 0;
    if (!ads1220_read_raw(dev, &raw_code)) return false;

    /* Логометричний розрахунок опору RTD */
    float r_pt100 = ((float)raw_code * 2.0f * dev->r_ref) / (8388608.0f * dev->gain);

    /* Розрахунок температури для T >= 0 °C */
    float z = 1.0f - (r_pt100 / PT100_R0);
    float discriminant = (PT100_A * PT100_A) - (4.0f * PT100_B * z);

    if (discriminant < 0.0f) {
        return false; /* Неприпустиме значення опору */
    }

    float t = (-PT100_A + sqrtf(discriminant)) / (2.0f * PT100_B);

    /* Ітеративне уточнення для діапазону від'ємних температур T < 0 °C */
    if (t < 0.0f) {
        for (int i = 0; i < 3; i++) {
            float t2 = t * t;
            float t3 = t2 * t;
            float r_calc = PT100_R0 * (1.0f + PT100_A * t + PT100_B * t2 + PT100_C * (t - 100.0f) * t3);
            float r_diff = PT100_R0 * (PT100_A + 2.0f * PT100_B * t - 300.0f * PT100_C * t2 + 4.0f * PT100_C * t3);
            t = t - (r_calc - r_pt100) / r_diff;
        }
    }

    *temp_celsius = t;
    return true;
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <expected>
#include <optional>
#include <span>

namespace embedded {

enum class AdcError {
    HardwareTimeout,
    SpiCommunicationFailure,
    CalculationOutOfRange
};

class Ads1220Rtd {
public:
    struct SpiInterface {
        void (*cs_assert)();
        void (*cs_deassert)();
        void (*transfer)(std::span<const uint8_t> tx, std::span<uint8_t> rx);
        bool (*wait_drdy_low)(uint32_t timeout_ms);
    };

    static constexpr float Pt100R0 = 100.0f;
    static constexpr float Pt100A  = 3.9083e-3f;
    static constexpr float Pt100B  = -5.7750e-7f;
    static constexpr float Pt100C  = -4.1830e-12f;

    explicit Ads1220Rtd(SpiInterface bus, float r_ref = 3300.0f, float gain = 16.0f)
        : bus_(bus), r_ref_(r_ref), gain_(gain), offset_code_(0) {}

    bool init() {
        // Скидання мікросхеми
        const uint8_t cmd_reset = 0x06;
        execute_transaction(std::span(&cmd_reset, 1), {});

        // Конфігурація регістрів 0..3
        const uint8_t config[5] = {
            0x43, // WREG starting from register 0, length = 4
            0x38, // AIN1-AIN2 diff, Gain=16, PGA on
            0x00, // 20 SPS, Single-shot, Normal mode
            0x76, // External Vref REFP0/REFN0, FIR 50/60Hz, IDAC=500 uA
            0x60  // IDAC1 -> AIN0, IDAC2 -> AIN1
        };

        execute_transaction(std::span(config, 5), {});
        return true;
    }

    bool calibrate_offset() {
        const uint8_t cal_cfg[2] = { 0x40, 0xE8 }; // MUX = (AVDD-AVSS)/2, Gain=16
        execute_transaction(std::span(cal_cfg, 2), {});

        const uint8_t cmd_start = 0x08;
        execute_transaction(std::span(&cmd_start, 1), {});

        if (!bus_.wait_drdy_low(60)) return false;

        const uint8_t tx[4] = { 0x10, 0x00, 0x00, 0x00 };
        uint8_t rx[4] = { 0 };
        execute_transaction(std::span(tx, 4), std::span(rx, 4));

        int32_t offset = (static_cast<int32_t>(rx[1]) << 16) |
                         (static_cast<int32_t>(rx[2]) << 8)  |
                         (static_cast<int32_t>(rx[3]));
        if (offset & 0x00800000) offset |= 0xFF000000;
        offset_code_ = offset;

        // Повернення в робочий режим
        const uint8_t restore_cfg[2] = { 0x40, 0x38 };
        execute_transaction(std::span(restore_cfg, 2), {});
        return true;
    }

    std::expected<int32_t, AdcError> read_raw() const {
        const uint8_t cmd_start = 0x08;
        execute_transaction(std::span(&cmd_start, 1), {});

        if (!bus_.wait_drdy_low(60)) {
            return std::unexpected(AdcError::HardwareTimeout);
        }

        const uint8_t tx[4] = { 0x10, 0x00, 0x00, 0x00 };
        uint8_t rx[4] = { 0 };
        execute_transaction(std::span(tx, 4), std::span(rx, 4));

        int32_t code = (static_cast<int32_t>(rx[1]) << 16) |
                       (static_cast<int32_t>(rx[2]) << 8)  |
                       (static_cast<int32_t>(rx[3]));

        if (code & 0x00800000) {
            code |= 0xFF000000;
        }

        return code - offset_code_;
    }

    std::expected<float, AdcError> read_temperature() const {
        auto raw = read_raw();
        if (!raw) return std::unexpected(raw.error());

        // Логометричний перерахунок опору
        const float r_pt100 = (static_cast<float>(*raw) * 2.0f * r_ref_) / (8388608.0f * gain_);

        // Розв'язання рівняння Каллендара-Ван Дюзена для T >= 0 °C
        const float z = 1.0f - (r_pt100 / Pt100R0);
        const float discriminant = (Pt100A * Pt100A) - (4.0f * Pt100B * z);

        if (discriminant < 0.0f) {
            return std::unexpected(AdcError::CalculationOutOfRange);
        }

        float temp = (-Pt100A + std::sqrt(discriminant)) / (2.0f * Pt100B);

        // Уточнення за методом Ньютона для від'ємного діапазону
        if (temp < 0.0f) {
            for (int i = 0; i < 3; ++i) {
                const float t2 = temp * temp;
                const float t3 = t2 * temp;
                const float r_calc = Pt100R0 * (1.0f + Pt100A * temp + Pt100B * t2 + Pt100C * (temp - 100.0f) * t3);
                const float r_diff = Pt100R0 * (Pt100A + 2.0f * Pt100B * temp - 300.0f * Pt100C * t2 + 4.0f * Pt100C * t3);
                temp = temp - (r_calc - r_pt100) / r_diff;
            }
        }

        return temp;
    }

private:
    void execute_transaction(std::span<const uint8_t> tx, std::span<uint8_t> rx) const {
        bus_.cs_assert();
        bus_.transfer(tx, rx);
        bus_.cs_deassert();
    }

    SpiInterface bus_;
    float r_ref_;
    float gain_;
    int32_t offset_code_;
};

} // namespace embedded
```
:::

## 5. Пастки та інженерні крайові випадки

1. **Діапазон синфазної напруги PGA.** Вбудований підсилювач PGA вимагає, щоб абсолютна напруга на будь-якому з входів `AIN1` та `AIN2` не виходила за межі `[AVSS + 0.2 В; AVDD - 0.2 В]`. Спад напруги на резисторі `R_ref` зміщує потенціал датчика вгору від землі:
   ```
   V_cm = (I_idac1 + I_idac2) · R_ref = 1.0 мА · 3.3 кОм = 3.3 В
   ```
   При напрузі живлення `AVDD = 5.0 В` це забезпечує ідеальне попадання в лінійну зону PGA. Якщо зменшити `R_ref` нижче 200 Ом, вхідна напруга впаде нижче 0.2 В, і вхідні транзистори підсилювача увійдуть у режим насичення.
2. **Незбалансованість опору з'єднувальних проводів.** Схема повної компенсації базується на припущенні, що опір першого та другого дротів однаковий (`R_lead1 = R_lead2`). Якщо монтаж виконано дротами різного перерізу або неякісно затиснуто клемник, різниця опорів `ΔR_lead = 0.1 Ом` створить систематичну похибку:
   ```
   ΔT = ΔR_lead / 0.385 Ом/°C = 0.1 / 0.385 ≈ 0.26 °C
   ```
   У метрологічних установках з екстремальними вимогами застосовують 4-провідне підключення Кельвіна (Kelvin 4-wire connection), де струм збудження подається окремою парою проводів, а вимірювальні входи АЦП споживають мізерний вхідний струм менше ніж 1 нА.
3. **Саморозігрів датчика струмом збудження.** Струм `I_ex = 500 мкА` розсіює на датчику потужність `P = I² · R = (500·10⁻⁶)² · 100 ≈ 25 мкВт`. Для мініатюрних датчиків у нерухомому повітрі коефіцієнт саморозігріву становить близько 1 мВт/°C, що створює систематичний зсув на `+0.025 °C`. Для усунення цього ефекту АЦП переводять у режим одиничного перетворення (англ. *Single-shot mode*), вмикаючи струми лише на 50 мс вимірювання.
4. **Придушення мережевих завад 50/60 Гц.** На частоті вибірки 20 SPS цифровий фільтр ADS1220 має глибокі нулі передавальної характеристики на частотах 50 Гц та 60 Гц (придушення > 80 дБ), що повністю ліквідує наведення від промислової електромережі без громіздких аналогових LC-фільтрів.
