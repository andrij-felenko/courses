# ⚙️ Контролер транспортного режиму (Ship Mode Driver)

При серійному виробництві пристроїв із незнімними літієвими акумуляторами виникає критична інженерна суперечність між нормами транспортної безпеки та фізикою тривалого зберігання хімічних джерел живлення. З одного боку, норми міжнародної авіаційної логістики (ICAO / IATA DGR) вимагають, щоб рівень заряду акумулятора при відвантаженні окремо або в комплекті не перевищував 30% номінальної ємності (близько 3.70–3.75 В на комірку для систем NMC/LCO). З іншого боку, транспортування морем та перебування на складах регіональних дистриб'юторів нерідко триває від 6 до 18 місяців. Якщо пристрій у вимкненому стані споживає типовий струм сну мікроконтролера, підтяжок шин I2C та лінійних стабілізаторів у 20–50 мкА, акумулятор неминуче розрядиться нижче критичної межі 2.0 В.

При падінні напруги нижче 2.0 В на графітовому аноді починається необоротне анодне розчинення мідного струмознімача: іони міді переходять в електроліт і під час першої ж спроби заряду осідають у вигляді голчастих металевих дендритів, що протикають полімерний сепаратор і викликають глухе внутрішнє коротке замикання.

Для вирішення цієї проблеми застосовується апаратно-програмний механізм **транспортного режиму** (англ. *Ship Mode* / *Storage Mode*). У цьому стані силовий ключ інтегрованої мікросхеми керування живленням (PMIC) або дискретний електронний ізолятор (Load Switch на базі P-канального MOSFET) фізично відсікає внутрішній акумулятор від системної шини живлення `V_SYS`, знижуючи сумарний струм витоку до величини `I_q ≤ 0.5 мкА` (наноамперний діапазон), а вихід із режиму блокується до моменту підключення зовнішнього зарядного кабелю або тривалого утримання кнопки живлення.

## 1. Схемотехнічна архітектура та баланс струмів споживання

У звичайному режимі очікування (Standby / Deep Sleep) мікроконтролер живиться через LDO або понижувальний DC-DC конвертер. Навіть якщо ядро MCU перебуває у стані глибокого сну зі споживанням 1.5 мкА, паразитичні витоки через зворотний струм діодів захисту від переполюсовки, власний струм споживання мікросхем захисту BMS (2–4 мкА), дільники вимірювання напруги АЦП (10–20 мкА) та струм спокою перетворювачів (5–15 мкА) сумарно створюють постійне навантаження близько 30–50 мкА.

У схемі з контролером Ship Mode (наприклад, на базі спеціалізованих PMIC класів Texas Instruments BQ25120, Analog Devices / Maxim MAX77650 або дискретних ключів TPS22918) силова шина системи `V_SYS` повністю знеструмлюється:
- Силовий P-MOSFET закривається з опором ізоляції понад `100 МОм`.
- Активною залишається лише надмалопотужна схема детекції зовнішніх подій (Ship Mode Latch), струм якої становить від 20 до 200 нА.
- При ємності батареї 500 мА·год та струмі витоку 0.2 мкА щорічний саморозряд схеми становить менше `1.75 мА·год` (менше 0.35% номінальної ємності на рік), що гарантує збереження робочого стану виробу протягом 5–10 років зберігання.

## 2. Алгоритм підготовки та переведення пристрою в Ship Mode

Процес переходу в транспортний стан виконується на фінальному етапі заводського тестування (End-of-Line Testing, EOL) за допомогою автоматизованого стенда:

1. **Верифікація безпечного SoC:** Зчитування регістрів кулонівського лічильника (Fuel Gauge) та вимірювання напруги розімкненого кола (OCV). Якщо рівень заряду перевищує 30% або напруга вища за 3.80 В, прошивка повертає помилку `ERR_VOLTAGE_TOO_HIGH` і блокує пакування до примусового розряду на каліброване навантаження.
2. **Фіксація стану в незалежній пам'яті:** Запис мітки переходу в EEPROM/Flash для фіксації дати, серійного номера партії та параметрів калібрування.
3. **Конфігурація умов пробудження (Wake-up Conditions):** Налаштування тривалості апаратного дебаунсу кнопки ввімкнення (не менше 3 секунд для захисту від вібраційних замикань при перевезенні) або конфігурація пробудження виключно за сигналом `V_BUS` (підключення USB-живлення кінцевим користувачем).
4. **Надсилання команди ізоляції:** Запис спеціальної бітової маски в регістр PMIC через I2C та очікування вимкнення тактування.

## 3. Реалізація драйвера мовами C та C++

:::tabs
```c
/* ship_mode_controller.h - Реалізація контролера транспортного режиму на C */
#ifndef SHIP_MODE_CONTROLLER_H
#define SHIP_MODE_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>

#define SHIP_MODE_MAX_VOLTAGE_MV   3800  /* Максимальна напруга 30% SoC (3.80 В) */
#define SHIP_MODE_MIN_VOLTAGE_MV   3500  /* Мінімальна напруга для консервації */
#define PMIC_REG_POWER_CONFIG      0x05  /* Регістр конфігурації живлення PMIC */
#define PMIC_BIT_SHIP_MODE_ENTER   (1 << 6)
#define PMIC_BIT_WAKE_PRESS_TIME_3S (1 << 4)

typedef enum {
    SHIP_MODE_OK = 0,
    SHIP_MODE_ERR_VOLTAGE_TOO_HIGH,
    SHIP_MODE_ERR_VOLTAGE_TOO_LOW,
    SHIP_MODE_ERR_I2C_COMM,
    SHIP_MODE_ERR_VBUS_CONNECTED
} ship_mode_status_t;

typedef struct {
    uint8_t i2c_address;
    uint32_t (*read_battery_mv)(void);
    bool (*is_vbus_present)(void);
    bool (*i2c_write)(uint8_t dev_addr, uint8_t reg_addr, uint8_t value);
    bool (*i2c_read)(uint8_t dev_addr, uint8_t reg_addr, uint8_t *value);
} ship_mode_driver_t;

ship_mode_status_t ship_mode_verify_safety(const ship_mode_driver_t *drv);
ship_mode_status_t ship_mode_enter(const ship_mode_driver_t *drv);

#endif /* SHIP_MODE_CONTROLLER_H */
```
```c
/* ship_mode_controller.c */
#include "ship_mode_controller.h"

ship_mode_status_t ship_mode_verify_safety(const ship_mode_driver_t *drv) {
    if (!drv || !drv->read_battery_mv || !drv->is_vbus_present) {
        return SHIP_MODE_ERR_I2C_COMM;
    }

    if (drv->is_vbus_present()) {
        return SHIP_MODE_ERR_VBUS_CONNECTED; /* Не можна вимикати при підключеній зарядці */
    }

    uint32_t v_batt = drv->read_battery_mv();
    if (v_batt > SHIP_MODE_MAX_VOLTAGE_MV) {
        return SHIP_MODE_ERR_VOLTAGE_TOO_HIGH; /* Перевищує 30% SoC для UN 3480 */
    }
    if (v_batt < SHIP_MODE_MIN_VOLTAGE_MV) {
        return SHIP_MODE_ERR_VOLTAGE_TOO_LOW;  /* Ризик глибокого розряду на складі */
    }

    return SHIP_MODE_OK;
}

ship_mode_status_t ship_mode_enter(const ship_mode_driver_t *drv) {
    ship_mode_status_t check = ship_mode_verify_safety(drv);
    if (check != SHIP_MODE_OK) {
        return check;
    }

    uint8_t reg_val = 0;
    if (!drv->i2c_read(drv->i2c_address, PMIC_REG_POWER_CONFIG, &reg_val)) {
        return SHIP_MODE_ERR_I2C_COMM;
    }

    /* Налаштовуємо 3-секундний дебаунс на кнопці для захисту від вібрації */
    reg_val |= PMIC_BIT_WAKE_PRESS_TIME_3S;
    /* Встановлюємо біт переходу в Ship Mode */
    reg_val |= PMIC_BIT_SHIP_MODE_ENTER;

    if (!drv->i2c_write(drv->i2c_address, PMIC_REG_POWER_CONFIG, reg_val)) {
        return SHIP_MODE_ERR_I2C_COMM;
    }

    /* Очікування вимкнення живлення ключем PMIC */
    while (1) {
        __asm volatile("wfi"); /* Sleep до знеструмлення */
    }

    return SHIP_MODE_OK;
}
```
```cpp
// ship_mode_controller.hpp - Ідіоматична реалізація мовою C++20
#pragma once

#include <cstdint>
#include <concepts>
#include <expected>
#include <chrono>

namespace power::transport {

enum class ErrorCode : uint8_t {
    VoltageTooHigh,     // Перевищує нормативні 30% SoC (UN 3480)
    VoltageTooLow,      // Загроза мідного розчинення (< 3.50 В)
    VBusActive,         // Зарядний пристрій підключено
    HardwareBusError    // Помилка шини зв'язку PMIC
};

template <typename HardwareInterface>
concept PowerManager = requires(HardwareInterface hw, uint8_t addr, uint8_t reg, uint8_t val) {
    { hw.readVoltageMillivolts() } -> std::same_as<uint32_t>;
    { hw.isExternalPowerConnected() } -> std::same_as<bool>;
    { hw.writeRegister(addr, reg, val) } -> std::same_as<bool>;
    { hw.readRegister(addr, reg) } -> std::same_as<std::expected<uint8_t, ErrorCode>>;
};

class ShipModeController {
public:
    static constexpr uint32_t kMaxTransportVoltageMv = 3800; // 30% SoC limit
    static constexpr uint32_t kMinTransportVoltageMv = 3500; // Critical floor
    static constexpr uint8_t  kPmicPowerConfigReg    = 0x05;
    static constexpr uint8_t  kBitEnterShipMode      = 1 << 6;
    static constexpr uint8_t  kBitWakeDebounce3s     = 1 << 4;

    explicit constexpr ShipModeController(uint8_t pmicI2cAddress) noexcept
        : pmicAddress_{pmicI2cAddress} {}

    template <PowerManager Interface>
    [[nodiscard]] std::expected<void, ErrorCode> verifyPreconditions(Interface& hw) const noexcept {
        if (hw.isExternalPowerConnected()) {
            return std::unexpected(ErrorCode::VBusActive);
        }

        const uint32_t voltage = hw.readVoltageMillivolts();
        if (voltage > kMaxTransportVoltageMv) {
            return std::unexpected(ErrorCode::VoltageTooHigh);
        }
        if (voltage < kMinTransportVoltageMv) {
            return std::unexpected(ErrorCode::VoltageTooLow);
        }

        return {};
    }

    template <PowerManager Interface>
    [[nodiscard]] std::expected<void, ErrorCode> executeShipMode(Interface& hw) const noexcept {
        auto check = verifyPreconditions(hw);
        if (!check) {
            return check;
        }

        auto currentReg = hw.readRegister(pmicAddress_, kPmicPowerConfigReg);
        if (!currentReg) {
            return std::unexpected(ErrorCode::HardwareBusError);
        }

        uint8_t newConfig = *currentReg | kBitWakeDebounce3s | kBitEnterShipMode;
        if (!hw.writeRegister(pmicAddress_, kPmicPowerConfigReg, newConfig)) {
            return std::unexpected(ErrorCode::HardwareBusError);
        }

        // Чекаємо апаратного знеструмлення контролером PMIC
        while (true) {
            // Low-power sleep barrier
        }

        return {};
    }

private:
    uint8_t pmicAddress_;
};

} // namespace power::transport
```
:::

## 4. Захист від випадкового ввімкнення під час вібраційних випробувань (T.3)

Під час транспортування вантажу в літаках і вантажівках (а також під час лабораторного тестування за стандартом UN 38.3 T.3) пристрій зазнає вібраційного навантаження з прискоренням до `8 gn`. Якщо кнопка живлення виробу має слабку поворотну пружину або корпус згинається під тиском сусідніх коробок, контакти можуть замикатися з частотою вібрації.

Апаратний дебаунс у контролері Ship Mode (встановлений бітом `kBitWakeDebounce3s`) вимагає безперервного замикання кнопки протягом щонайменше 3000 мс. Короткочасні вібраційні імпульси тривалістю 10–50 мс скидають внутрішній таймер PMIC, гарантуючи, що прилад не ввімкне радіомодулі та не розрядить батарею в закритій коробці.

## 5. Інтеграція з автоматизованими стендами заводського контролю (ATE)

На автоматизованій виробничій лінії переведення в Ship Mode є фінальною командою, яку тестовий стенд надсилає через інтерфейс pogo-pin або діагностичний порт UART/USB. Після надсилання команди стенд відключає зовнішнє живлення і за допомогою прецизійного мікроамперметра вимірює залишковий струм витоку на клемах батареї. Якщо струм перевищує `1.0 мкА`, виріб відбраковується за критерієм прихованого витоку (наприклад, флюс між виводами конденсаторів або дефектний захисний діод).
