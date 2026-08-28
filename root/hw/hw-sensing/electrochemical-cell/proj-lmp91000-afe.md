# Драйвер аналогового інтерфейсу потенціостата LMP91000

Для зчитування наноамперних струмів електрохімічних газових комірок потрібен спеціалізований аналоговий фронтенд (AFE), який інтегрує підсилювач керування електродами, трансімпедансний підсилювач із регульованим коефіцієнтом підсилення, програмоване джерело зміщення та комутатор режимів низького споживання. Мікросхема Texas Instruments LMP91000 є індустріальним стандартом такого AFE з керуванням через цифрову шину I²C.

Нижче наведено повний модульний драйвер для конфігурації, калібрування нульової точки, опитування вбудованого температурного діода та розрахунку концентрації газу в частинах на мільйон (ppm) мовами C та C++.

### Архітектура програмного інтерфейсу та карта регістрів

Керування мікросхемою LMP91000 здійснюється через стандартну шину I²C на 7-бітній фіксованій адресі `0x48`. Внутрішній простір пам'яті містить п'ять ключових регістрів:

1. **Регістр статусу готовності `STATUS` (`0x00`, тільки читання):**
   * Біт 0 (`READY`): прапорець готовності внутрішніх джерел опорної напруги та аналогових каскадів. Значення `0` означає, що прилад перебуває у процесі запуску або стабілізації; значення `1` сигналізує про повну готовність аналогового тракту до вимірювань.
2. **Регістр блокування запису `LOCK` (`0x01`, читання/запис):**
   * Біт 0 (`LOCK`): апаратний захист від випадкового спотворення конфігурації через збої на шині I²C. За замовчуванням після скидання регістри підсилення та зміщення заблоковані (`LOCK = 1`). Для запису конфігурації необхідно попередньо записати `0x00`, а після завершення транзакції — повернути `0x01`.
3. **Регістр підсилювача `TIACN` (`0x10`, читання/запис):**
   * Біти `[4:2]` (`TIA_GAIN`): вибір опору зворотного зв'язку трансімпедансного підсилювача `R_TIA`. Доступні сім фіксованих номіналів: 2.75 кОм, 3.5 кОм, 7 кОм, 14 кОм, 35 кОм, 120 кОм, 350 кОм або підключення зовнішнього прецизійного резистора через вивід `R_EXT`.
   * Біти `[1:0]` (`RLOAD`): вибір внутрішнього навантажувального опору на вході робочого електрода (10 Ом, 33 Ом, 50 Ом, 100 Ом) для демпфування високочастотного шуму та узгодження імпедансу.
4. **Регістр опорної напруги та зміщення `REFCN` (`0x11`, читання/запис):**
   * Біт 7 (`REF_SOURCE`): вибір джерела опорної напруги (`0` — внутрішня напруга живлення `V_DD`, `1` — зовнішнє джерело опорної напруги на виводі `V_REF`).
   * Біти `[6:5]` (`INT_Z`): вибір рівня віртуального нуля робочого електрода: 20%, 50% або 67% від опорної напруги `V_REF` (або прямий обхід буфера).
   * Біт 4 (`BIAS_SIGN`): полярність напруги зміщення між робочим електродом та електродом порівняння (`0` — негативне зміщення для відновлюваних газів, `1` — позитивне зміщення).
   * Біти `[3:0]` (`BIAS`): амплітуда зміщення з дискретним кроком від 0% до 24% від опорної напруги.
5. **Регістр вибору режиму `MODECN` (`0x12`, читання/запис):**
   * Біт 7 (`FET_SHORT`): керування внутрішнім польовим транзистором швидкого відновлення. Значення `1` закорочує електроди WE та RE, утримуючи подвійний шар розрядженим у паузах між вимірюваннями.
   * Біти `[2:0]` (`MODE`): вибір режиму функціонування (глибокий сон Deep Sleep, 2-електродний гальванічний режим, режим очікування Standby, активне 3-електродне амперометричне вимірювання та два режими вимірювання температури кристала).

### Послідовність ініціалізації та вимірювального циклу

Для мінімізації енергоспоживання у бездротових та портативних пристроях рекомендується реалізовувати періодичний вимірювальний цикл за таким алгоритмом:

1. **Прокидання мікроконтролера:** переведення ліній шини I²C у робочий стан.
2. **Вихід із режиму Deep Sleep:** запис у регістр `MODECN` команди переходу в активний 3-електродний режим (`MODE = 0x03`) зі зняттям закорочування (`FET_SHORT = 0`).
3. **Очікування стабілізації:** пауза 50–150 мс для виходу аналогових буферів та електрохімічної комірки на квазістаціонарний режим.
4. **Вимірювання температури:** перемикання режиму в `MODECN = 0x06` (вимірювання внутрішнього діода), оцифрування напруги `V_TEMP` на виводі `VOUT` за допомогою АЦП мікроконтролера та перерахунок у градуси Цельсія.
5. **Повернення в 3-електродний режим:** повторне ввімкнення `MODECN = 0x03`, очікування 10–20 мс та оцифрування вихідної напруги газового сигналу `VOUT`.
6. **Математична компенсація:** розрахунок струму `I_WE`, віднімання фонового струму базової лінії з урахуванням виміряної температури та розрахунок фінальної концентрації в ppm.
7. **Перехід у глибокий сон:** запис `MODECN = 0x80` (глибокий сон із ввімкненим закорочувальним FET) для збереження заряду батареї та утримання електродів у розрядженому стані.

### Реалізація драйвера: C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define LMP91000_I2C_ADDR_7BIT        0x48

#define LMP91000_REG_STATUS           0x00
#define LMP91000_REG_LOCK             0x01
#define LMP91000_REG_TIACN            0x10
#define LMP91000_REG_REFCN            0x11
#define LMP91000_REG_MODECN           0x12

typedef enum {
    LMP91000_TIA_GAIN_EXT     = 0x00,
    LMP91000_TIA_GAIN_2K75    = 0x04,
    LMP91000_TIA_GAIN_3K5     = 0x08,
    LMP91000_TIA_GAIN_7K      = 0x0C,
    LMP91000_TIA_GAIN_14K     = 0x10,
    LMP91000_TIA_GAIN_35K     = 0x14,
    LMP91000_TIA_GAIN_120K    = 0x18,
    LMP91000_TIA_GAIN_350K    = 0x1C
} lmp91000_tia_gain_t;

typedef enum {
    LMP91000_RLOAD_10OHM      = 0x00,
    LMP91000_RLOAD_33OHM      = 0x01,
    LMP91000_RLOAD_50OHM      = 0x02,
    LMP91000_RLOAD_100OHM     = 0x03
} lmp91000_rload_t;

typedef enum {
    LMP91000_INT_ZERO_20PCT   = 0x00,
    LMP91000_INT_ZERO_50PCT   = 0x20,
    LMP91000_INT_ZERO_67PCT   = 0x40,
    LMP91000_INT_ZERO_BYPASS  = 0x60
} lmp91000_int_zero_t;

typedef enum {
    LMP91000_BIAS_SIGN_NEG    = 0x00,
    LMP91000_BIAS_SIGN_POS    = 0x10
} lmp91000_bias_sign_t;

typedef enum {
    LMP91000_BIAS_0PCT        = 0x00,
    LMP91000_BIAS_1PCT        = 0x01,
    LMP91000_BIAS_2PCT        = 0x02,
    LMP91000_BIAS_4PCT        = 0x03,
    LMP91000_BIAS_6PCT        = 0x04,
    LMP91000_BIAS_8PCT        = 0x05,
    LMP91000_BIAS_10PCT       = 0x06,
    LMP91000_BIAS_12PCT       = 0x07,
    LMP91000_BIAS_14PCT       = 0x08,
    LMP91000_BIAS_16PCT       = 0x09,
    LMP91000_BIAS_18PCT       = 0x0A,
    LMP91000_BIAS_20PCT       = 0x0B,
    LMP91000_BIAS_22PCT       = 0x0C,
    LMP91000_BIAS_24PCT       = 0x0D
} lmp91000_bias_mag_t;

typedef enum {
    LMP91000_OP_MODE_DEEP_SLEEP = 0x00,
    LMP91000_OP_MODE_2LEAD_GALV = 0x01,
    LMP91000_OP_MODE_STANDBY    = 0x02,
    LMP91000_OP_MODE_3LEAD_AMP  = 0x03,
    LMP91000_OP_MODE_TEMP_TIAON = 0x06,
    LMP91000_OP_MODE_TEMP_TIAOFF= 0x07
} lmp91000_op_mode_t;

typedef struct {
    lmp91000_tia_gain_t gain;
    lmp91000_rload_t rload;
    lmp91000_int_zero_t int_zero;
    lmp91000_bias_sign_t bias_sign;
    lmp91000_bias_mag_t bias_mag;
    float vref_volts;
    float sensitivity_na_per_ppm;
    float baseline_current_na;
} lmp91000_config_t;

typedef struct {
    lmp91000_config_t cfg;
    bool (*i2c_write)(uint8_t reg, uint8_t val);
    bool (*i2c_read)(uint8_t reg, uint8_t *val);
} lmp91000_t;

static float lmp91000_get_rtia_value(lmp91000_tia_gain_t gain) {
    switch (gain) {
        case LMP91000_TIA_GAIN_2K75:  return 2750.0f;
        case LMP91000_TIA_GAIN_3K5:   return 3500.0f;
        case LMP91000_TIA_GAIN_7K:    return 7000.0f;
        case LMP91000_TIA_GAIN_14K:   return 14000.0f;
        case LMP91000_TIA_GAIN_35K:   return 35000.0f;
        case LMP91000_TIA_GAIN_120K:  return 120000.0f;
        case LMP91000_TIA_GAIN_350K:  return 350000.0f;
        default:                      return 0.0f;
    }
}

static float lmp91000_get_zero_fraction(lmp91000_int_zero_t zero) {
    switch (zero) {
        case LMP91000_INT_ZERO_20PCT: return 0.20f;
        case LMP91000_INT_ZERO_50PCT: return 0.50f;
        case LMP91000_INT_ZERO_67PCT: return 0.67f;
        default:                      return 0.50f;
    }
}

bool lmp91000_init(lmp91000_t *dev, const lmp91000_config_t *cfg,
                   bool (*write_fn)(uint8_t, uint8_t),
                   bool (*read_fn)(uint8_t, uint8_t*)) {
    if (!dev || !cfg || !write_fn || !read_fn) return false;
    dev->cfg = *cfg;
    dev->i2c_write = write_fn;
    dev->i2c_read = read_fn;

    uint8_t status = 0;
    if (!dev->i2c_read(LMP91000_REG_STATUS, &status)) return false;

    if (!dev->i2c_write(LMP91000_REG_LOCK, 0x00)) return false;

    uint8_t tiacn = (uint8_t)dev->cfg.gain | (uint8_t)dev->cfg.rload;
    if (!dev->i2c_write(LMP91000_REG_TIACN, tiacn)) return false;

    uint8_t refcn = (uint8_t)dev->cfg.int_zero | (uint8_t)dev->cfg.bias_sign | (uint8_t)dev->cfg.bias_mag;
    if (!dev->i2c_write(LMP91000_REG_REFCN, refcn)) return false;

    if (!dev->i2c_write(LMP91000_REG_LOCK, 0x01)) return false;

    uint8_t modecn = (uint8_t)LMP91000_OP_MODE_3LEAD_AMP;
    return dev->i2c_write(LMP91000_REG_MODECN, modecn);
}

bool lmp91000_set_mode(lmp91000_t *dev, lmp91000_op_mode_t mode, bool shorting_fet_en) {
    if (!dev || !dev->i2c_write) return false;
    uint8_t modecn = (uint8_t)mode;
    if (shorting_fet_en) {
        modecn |= 0x80;
    }
    return dev->i2c_write(LMP91000_REG_MODECN, modecn);
}

float lmp91000_voltage_to_current_na(const lmp91000_t *dev, float vout_volts) {
    if (!dev) return 0.0f;
    float rtia = lmp91000_get_rtia_value(dev->cfg.gain);
    if (rtia <= 0.0f) return 0.0f;

    float v_zero = dev->cfg.vref_volts * lmp91000_get_zero_fraction(dev->cfg.int_zero);
    float delta_v = vout_volts - v_zero;

    float current_amps = delta_v / rtia;
    return current_amps * 1.0e9f;
}

float lmp91000_calculate_ppm(const lmp91000_t *dev, float vout_volts, float temperature_c) {
    if (!dev || dev->cfg.sensitivity_na_per_ppm <= 0.0f) return 0.0f;

    float current_na = lmp91000_voltage_to_current_na(dev, vout_volts);

    float temp_drift_factor = 1.0f + 0.003f * (temperature_c - 20.0f);
    float baseline_t = dev->cfg.baseline_current_na * temp_drift_factor;

    float net_gas_current_na = current_na - baseline_t;
    if (net_gas_current_na < 0.0f) {
        net_gas_current_na = 0.0f;
    }

    float sensitivity_t = dev->cfg.sensitivity_na_per_ppm * temp_drift_factor;
    return net_gas_current_na / sensitivity_t;
}

float lmp91000_raw_voltage_to_temperature(float vout_volts) {
    const float v_at_0c = 1.632f;
    const float tc_volts_per_deg = -0.0082f;
    return (vout_volts - v_at_0c) / tc_volts_per_deg;
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <concepts>
#include <expected>
#include <optional>
#include <algorithm>

namespace sensing {

enum class TIA_Gain : uint8_t {
    External = 0x00,
    Gain_2k75 = 0x04,
    Gain_3k5  = 0x08,
    Gain_7k   = 0x0C,
    Gain_14k  = 0x10,
    Gain_35k  = 0x14,
    Gain_120k = 0x18,
    Gain_350k = 0x1C
};

enum class RLoad : uint8_t {
    R_10Ohm  = 0x00,
    R_33Ohm  = 0x01,
    R_50Ohm  = 0x02,
    R_100Ohm = 0x03
};

enum class InternalZero : uint8_t {
    Zero_20Pct = 0x00,
    Zero_50Pct = 0x20,
    Zero_67Pct = 0x40,
    Bypassed   = 0x60
};

enum class BiasSign : uint8_t {
    Negative = 0x00,
    Positive = 0x10
};

enum class BiasMagnitude : uint8_t {
    Bias_0Pct  = 0x00,
    Bias_1Pct  = 0x01,
    Bias_2Pct  = 0x02,
    Bias_4Pct  = 0x03,
    Bias_6Pct  = 0x04,
    Bias_8Pct  = 0x05,
    Bias_10Pct = 0x06,
    Bias_12Pct = 0x07,
    Bias_14Pct = 0x08,
    Bias_16Pct = 0x09,
    Bias_18Pct = 0x0A,
    Bias_20Pct = 0x0B,
    Bias_22Pct = 0x0C,
    Bias_24Pct = 0x0D
};

enum class OperationMode : uint8_t {
    DeepSleep           = 0x00,
    Galvanic2Lead       = 0x01,
    Standby             = 0x02,
    Amperometric3Lead   = 0x03,
    TemperatureTiaOn    = 0x06,
    TemperatureTiaOff   = 0x07
};

enum class AfeError {
    I2cCommunicationFailure,
    DeviceNotReady,
    InvalidConfiguration,
    UnlockFailed,
    GainNotConfigured
};

struct SensorParameters {
    TIA_Gain gain{TIA_Gain::Gain_350k};
    RLoad rload{RLoad::R_10Ohm};
    InternalZero internalZero{InternalZero::Zero_50Pct};
    BiasSign biasSign{BiasSign::Negative};
    BiasMagnitude biasMag{BiasMagnitude::Bias_0Pct};
    float vrefVolts{3.3f};
    float sensitivityNaPerPpm{70.0f};
    float baselineCurrentNa{0.0f};
};

template <typename I2cBus>
requires requires(I2cBus bus, uint8_t reg, uint8_t val, uint8_t* read_buf) {
    { bus.write_register(reg, val) } -> std::same_as<bool>;
    { bus.read_register(reg, read_buf) } -> std::same_as<bool>;
}
class LMP91000 {
public:
    constexpr explicit LMP91000(I2cBus& bus, const SensorParameters& params) noexcept
        : bus_(bus), params_(params) {}

    std::expected<void, AfeError> initialize() noexcept {
        uint8_t status = 0;
        if (!bus_.read_register(RegStatus, &status)) {
            return std::unexpected(AfeError::I2cCommunicationFailure);
        }
        if ((status & 0x01) == 0) {
            return std::unexpected(AfeError::DeviceNotReady);
        }

        if (!bus_.write_register(RegLock, 0x00)) {
            return std::unexpected(AfeError::UnlockFailed);
        }

        uint8_t tiacn = static_cast<uint8_t>(params_.gain) | static_cast<uint8_t>(params_.rload);
        if (!bus_.write_register(RegTiacn, tiacn)) {
            return std::unexpected(AfeError::I2cCommunicationFailure);
        }

        uint8_t refcn = static_cast<uint8_t>(params_.internalZero) |
                        static_cast<uint8_t>(params_.biasSign) |
                        static_cast<uint8_t>(params_.biasMag);
        if (!bus_.write_register(RegRefcn, refcn)) {
            return std::unexpected(AfeError::I2cCommunicationFailure);
        }

        if (!bus_.write_register(RegLock, 0x01)) {
            return std::unexpected(AfeError::I2cCommunicationFailure);
        }

        return setMode(OperationMode::Amperometric3Lead, false);
    }

    std::expected<void, AfeError> setMode(OperationMode mode, bool shortingFet) noexcept {
        uint8_t modecn = static_cast<uint8_t>(mode);
        if (shortingFet) {
            modecn |= 0x80;
        }
        if (!bus_.write_register(RegModecn, modecn)) {
            return std::unexpected(AfeError::I2cCommunicationFailure);
        }
        return {};
    }

    [[nodiscard]] constexpr float voltageToCurrentNanoamps(float voutVolts) const noexcept {
        float rtia = rtiaOhms();
        if (rtia <= 0.0f) return 0.0f;

        float zeroVoltage = params_.vrefVolts * zeroFraction();
        float deltaVoltage = voutVolts - zeroVoltage;

        return (deltaVoltage / rtia) * 1.0e9f;
    }

    [[nodiscard]] constexpr float calculateGasPpm(float voutVolts, float temperatureCelsius) const noexcept {
        if (params_.sensitivityNaPerPpm <= 0.0f) return 0.0f;

        float currentNa = voltageToCurrentNanoamps(voutVolts);

        float tempCorrection = 1.0f + 0.003f * (temperatureCelsius - 20.0f);
        float baselineAtTemp = params_.baselineCurrentNa * tempCorrection;

        float netCurrentNa = std::max(0.0f, currentNa - baselineAtTemp);
        float correctedSensitivity = params_.sensitivityNaPerPpm * tempCorrection;

        return netCurrentNa / correctedSensitivity;
    }

    [[nodiscard]] static constexpr float rawToTemperature(float voutVolts) noexcept {
        constexpr float V0 = 1.632f;
        constexpr float Slope = -0.0082f;
        return (voutVolts - V0) / Slope;
    }

private:
    static constexpr uint8_t RegStatus = 0x00;
    static constexpr uint8_t RegLock   = 0x01;
    static constexpr uint8_t RegTiacn  = 0x10;
    static constexpr uint8_t RegRefcn  = 0x11;
    static constexpr uint8_t RegModecn = 0x12;

    I2cBus& bus_;
    SensorParameters params_;

    [[nodiscard]] constexpr float rtiaOhms() const noexcept {
        switch (params_.gain) {
            case TIA_Gain::Gain_2k75: return 2750.0f;
            case TIA_Gain::Gain_3k5:  return 3500.0f;
            case TIA_Gain::Gain_7k:   return 7000.0f;
            case TIA_Gain::Gain_14k:  return 14000.0f;
            case TIA_Gain::Gain_35k:  return 35000.0f;
            case TIA_Gain::Gain_120k: return 120000.0f;
            case TIA_Gain::Gain_350k: return 350000.0f;
            default:                  return 0.0f;
        }
    }

    [[nodiscard]] constexpr float zeroFraction() const noexcept {
        switch (params_.internalZero) {
            case InternalZero::Zero_20Pct: return 0.20f;
            case InternalZero::Zero_50Pct: return 0.50f;
            case InternalZero::Zero_67Pct: return 0.67f;
            default:                       return 0.50f;
        }
    }
};

} // namespace sensing
```
:::

### Повний приклад використання у мікроконтролерній системі

Для демонстрації інтеграції драйвера в реальний цикл опитування нижче наведено типовий фрагмент прошивки мовами C та C++, де мікроконтролер періодично прокидається, зчитує показання температури, виконує аналогове вимірювання струму газу, обчислює концентрацію та переходить у режим ультранизького енергоспоживання.

:::tabs
```c
#include <stdio.h>
#include <unistd.h>

extern bool platform_i2c_write(uint8_t reg, uint8_t val);
extern bool platform_i2c_read(uint8_t reg, uint8_t *val);
extern float platform_adc_read_voltage(void);
extern void platform_delay_ms(uint32_t ms);
extern void platform_enter_sleep_mode(uint32_t seconds);

void run_gas_detector_task(void) {
    lmp91000_config_t co_config = {
        .gain = LMP91000_TIA_GAIN_120K,
        .rload = LMP91000_RLOAD_10OHM,
        .int_zero = LMP91000_INT_ZERO_20PCT,
        .bias_sign = LMP91000_BIAS_SIGN_NEG,
        .bias_mag = LMP91000_BIAS_0PCT,
        .vref_volts = 3.30f,
        .sensitivity_na_per_ppm = 70.0f,
        .baseline_current_na = 2.5f
    };

    lmp91000_t co_sensor;
    if (!lmp91000_init(&co_sensor, &co_config, platform_i2c_write, platform_i2c_read)) {
        return;
    }

    while (1) {
        lmp91000_set_mode(&co_sensor, LMP91000_OP_MODE_TEMP_TIAON, false);
        platform_delay_ms(20);
        float v_temp = platform_adc_read_voltage();
        float current_temp_c = lmp91000_raw_voltage_to_temperature(v_temp);

        lmp91000_set_mode(&co_sensor, LMP91000_OP_MODE_3LEAD_AMP, false);
        platform_delay_ms(50);
        float v_gas = platform_adc_read_voltage();

        float co_ppm = lmp91000_calculate_ppm(&co_sensor, v_gas, current_temp_c);

        if (co_ppm > 35.0f) {
            /* Поріг тривоги перевищено */
        }

        lmp91000_set_mode(&co_sensor, LMP91000_OP_MODE_DEEP_SLEEP, true);
        platform_enter_sleep_mode(5);
    }
}
```
```cpp
#include <chrono>
#include <thread>
#include <iostream>

struct HardwareI2cAdapter {
    bool write_register(uint8_t reg, uint8_t val) noexcept {
        return true;
    }
    bool read_register(uint8_t reg, uint8_t* val) noexcept {
        *val = 0x01;
        return true;
    }
};

extern float readAdcVoltageFromChannel() noexcept;

void runGasMonitorApplication() {
    using namespace sensing;
    HardwareI2cAdapter i2cBus;

    SensorParameters coParams{
        .gain = TIA_Gain::Gain_120k,
        .rload = RLoad::R_10Ohm,
        .internalZero = InternalZero::Zero_20Pct,
        .biasSign = BiasSign::Negative,
        .biasMag = BiasMagnitude::Bias_0Pct,
        .vrefVolts = 3.30f,
        .sensitivityNaPerPpm = 70.0f,
        .baselineCurrentNa = 2.5f
    };

    LMP91000 sensor(i2cBus, coParams);

    auto initResult = sensor.initialize();
    if (!initResult.has_value()) {
        return;
    }

    while (true) {
        sensor.setMode(OperationMode::TemperatureTiaOn, false);
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
        float vTemp = readAdcVoltageFromChannel();
        float currentTemp = LMP91000<HardwareI2cAdapter>::rawToTemperature(vTemp);

        sensor.setMode(OperationMode::Amperometric3Lead, false);
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
        float vGas = readAdcVoltageFromChannel();

        float coConcentrationPpm = sensor.calculateGasPpm(vGas, currentTemp);

        if (coConcentrationPpm > 35.0f) {
            /* Обробка небезпечної концентрації CO */
        }

        sensor.setMode(OperationMode::DeepSleep, true);
        std::this_thread::sleep_for(std::chrono::seconds(5));
    }
}
```
:::

### Типові апаратні пастки та діагностика шини I²C

1. **Забуте розблокування регістрів:** За замовчуванням регістри `TIACN` та `REFCN` захищені від випадкового перезапису бітом у регістрі `LOCK`. Запис значень без попереднього скидання `LOCK = 0x00` ігнорується мікросхемою без формування помилки на шині I²C (NACK), через що аналоговий тракт залишається у заводському дефолтному стані.
2. **Неузгодженість полярності сигналу:** При вимірюванні окиснюваних газів (CO, `H₂S`) струм витікає з робочого електрода у віртуальну землю, тому вихідна напруга `V_OUT` зростає вище віртуального нуля. Для цих газів віртуальний нуль встановлюють на рівень 20% від `V_ref`, щоб забезпечити максимальний динамічний діапазон вгору (80% шкали АЦП). Для відновлюваних газів (`O₂`, `NO₂`), де струм втікає в електрод, а `V_OUT` падає, нуль встановлюють на рівні 67% або 50%, забезпечуючи запас шкали вниз.
3. **Час виходу з режиму Deep Sleep:** Після відкриття закорочувального FET-ключа вимірювальному підсилювачу потрібно від 50 до 150 мс для заряду паразитних ємностей та стабілізації вихідної напруги перед запуском перетворення АЦП. Передчасне зчитування призводить до фіксації стрибка перехідного струму заряду подвійного шару.
4. **Висячий вивід MENB (Module Enable):** Мікросхема LMP91000 має апаратний вивід дозволу `MENB` (активний низький рівень). Якщо цей вивід підключено до GPIO мікроконтролера і залишено у плаваючому стані (Hi-Z), цифрова частина мікросхеми відключається від шини I²C і не відповідає на запити ACK. Цей вивід слід жорстко підтягувати до землі або контролювати логічним рівнем `0`.
