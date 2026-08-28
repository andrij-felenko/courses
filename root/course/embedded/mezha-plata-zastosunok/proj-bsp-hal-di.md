# ⚙️ Впровадження залежностей (Dependency Injection) для тестування вбудованої логіки на хості

Головна перешкода для автоматизованого тестування вбудованих програм — це жорстка прив'язка коду до регістрів мікроконтролера та вендорних заголовних файлів (`stm32f4xx.h`, `esp_system.h`). Коли логіка ухвалення рішень (наприклад, аварійне вимкнення при розряді батареї) містить прямі виклики апаратного коду, скомпілювати та протестувати її на комп'ютері розробника (x86-64 або ARM64) неможливо. Шаблон **впровадження залежностей** (*Dependency Injection*, DI) розв'язує цю проблему: бізнес-модуль отримує абстрактний інтерфейс плати під час створення, що дозволяє в цільовій прошивці підключати реальні драйвери чипа, а в тестовому середовищі — легковажні мок-об'єкти (*Mock Objects*).

Нижче наведено практичну реалізацію шаблону DI мовами C та C++, порівняння цільової та хостової реалізацій, аналіз асемблерного виклику через покажчик, конфігурацію системи збірки CMake для подвійного таргету (MCU проти хоста) і робочий модульний тест логіки супервізора живлення.

---

### Архітектура завдання: супервізор живлення та сенсорів

Розглянемо типовий модуль автономного реєстратора — `SystemSupervisor`. Його завдання:
1. Опитувати сенсори середовища з періодичністю раз на хвилину.
2. Перевіряти напругу акумуляторної батареї:
   - Якщо `V_bat < 3300 мВ` — увімкнути індикатор тривоги `BOARD_LED_ID_WARNING` та заблокувати роботу радіомодуля.
   - Якщо `V_bat < 3000 мВ` — примусово знеструмити всі сенсори та перевести плату в режим глибокого сну `BOARD_SLEEP_MODE_DEEP` на 1 годину.
3. Якщо напруга в нормі — блимнути системним світлодіодом `BOARD_LED_ID_SYSTEM_STATUS` та зчитати дані давачів.

Модуль супервізора не повинен містити жодного рядка, специфічного для STM32, ESP32 чи будь-якого іншого мікроконтролера.

---

### Реалізація на C: поліморфізм через таблицю функцій (Vtable DI)

У мові C впровадження залежностей реалізується через передачу структури з покажчиками на функції (*Driver Interface Table*). Конструктор модуля `supervisor_init` приймає покажчик на константну таблицю методів і зберігає його в контексті модуля.

:::tabs
```c
/* --- supervisor.h: Бізнес-логіка (100% переносний код) --- */
#ifndef SUPERVISOR_H
#define SUPERVISOR_H

#include "bsp_interface.h"

typedef struct {
    bsp_status_t (*led_set)(board_led_id_t led, board_led_state_t state);
    bsp_status_t (*power_domain_set)(board_power_domain_t domain, bool enable);
    bsp_status_t (*get_battery_metrics)(board_battery_metrics_t *metrics);
    bsp_status_t (*read_environment)(board_env_metrics_t *env);
    bsp_status_t (*enter_low_power)(board_sleep_mode_t mode, uint32_t timeout_ms);
} bsp_driver_t;

typedef struct {
    const bsp_driver_t *bsp;
    bool is_low_power_warning;
    bool is_critical_shutdown;
} supervisor_t;

void supervisor_init(supervisor_t *ctx, const bsp_driver_t *bsp);
void supervisor_run_cycle(supervisor_t *ctx);

#endif /* SUPERVISOR_H */
```
```cpp
// --- supervisor.hpp: Бізнес-логіка (100% переносний код) ---
#ifndef SUPERVISOR_HPP
#define SUPERVISOR_HPP

#include "bsp_interface.hpp"

namespace app {

class SystemSupervisor {
public:
    explicit SystemSupervisor(bsp::IBoardSupport& bsp) noexcept
        : bsp_(bsp), is_low_power_warning_(false), is_critical_shutdown_(false) {}

    void run_cycle() noexcept;

    [[nodiscard]] bool is_low_power_warning() const noexcept { return is_low_power_warning_; }
    [[nodiscard]] bool is_critical_shutdown() const noexcept { return is_critical_shutdown_; }

private:
    bsp::IBoardSupport& bsp_;
    bool is_low_power_warning_;
    bool is_critical_shutdown_;
};

} // namespace app

#endif /* SUPERVISOR_HPP */
```
:::

Реалізація логіки супервізора використовує виключно наданий інтерфейс:

:::tabs
```c
/* --- supervisor.c --- */
#include "supervisor.h"

void supervisor_init(supervisor_t *ctx, const bsp_driver_t *bsp) {
    ctx->bsp = bsp;
    ctx->is_low_power_warning = false;
    ctx->is_critical_shutdown = false;
}

void supervisor_run_cycle(supervisor_t *ctx) {
    if (!ctx || !ctx->bsp) return;

    board_battery_metrics_t bat = {0};
    bsp_status_t st = ctx->bsp->get_battery_metrics(&bat);
    if (st != BSP_STATUS_OK) {
        ctx->bsp->led_set(BOARD_LED_ID_WARNING, BOARD_LED_STATE_ON);
        return;
    }

    // Критичний поріг розряду (3000 мВ): аварійний сон
    if (bat.voltage_mv < 3000) {
        ctx->is_critical_shutdown = true;
        ctx->bsp->led_set(BOARD_LED_ID_SYSTEM_STATUS, BOARD_LED_STATE_OFF);
        ctx->bsp->led_set(BOARD_LED_ID_WARNING, BOARD_LED_STATE_ON);
        ctx->bsp->power_domain_set(BOARD_POWER_DOMAIN_SENSORS, false);
        ctx->bsp->enter_low_power(BOARD_SLEEP_MODE_DEEP, 3600000); // 1 година
        return;
    }

    // Попереджувальний поріг розряду (3300 мВ)
    if (bat.voltage_mv < 3300) {
        ctx->is_low_power_warning = true;
        ctx->bsp->led_set(BOARD_LED_ID_WARNING, BOARD_LED_STATE_ON);
    } else {
        ctx->is_low_power_warning = false;
        ctx->bsp->led_set(BOARD_LED_ID_WARNING, BOARD_LED_STATE_OFF);
    }

    // Штатний цикл збору даних
    ctx->bsp->led_set(BOARD_LED_ID_SYSTEM_STATUS, BOARD_LED_STATE_ON);
    ctx->bsp->power_domain_set(BOARD_POWER_DOMAIN_SENSORS, true);

    board_env_metrics_t env = {0};
    ctx->bsp->read_environment(&env);

    ctx->bsp->power_domain_set(BOARD_POWER_DOMAIN_SENSORS, false);
    ctx->bsp->led_set(BOARD_LED_ID_SYSTEM_STATUS, BOARD_LED_STATE_OFF);
}
```
```cpp
// --- supervisor.cpp ---
#include "supervisor.hpp"

namespace app {

void SystemSupervisor::run_cycle() noexcept {
    auto bat_res = bsp_.get_battery_metrics();
    if (!bat_res.has_value()) {
        bsp_.led_set(bsp::LedId::Warning, bsp::LedState::On);
        return;
    }

    const auto& bat = bat_res.value();

    // Критичний поріг розряду (3000 мВ): аварійний сон
    if (bat.voltage_mv < 3000) {
        is_critical_shutdown_ = true;
        bsp_.led_set(bsp::LedId::SystemStatus, bsp::LedState::Off);
        bsp_.led_set(bsp::LedId::Warning, bsp::LedState::On);
        bsp_.power_domain_set(bsp::PowerDomain::Sensors, false);
        bsp_.enter_low_power(bsp::SleepMode::Deep, std::chrono::hours(1));
        return;
    }

    // Попереджувальний поріг розряду (3300 мВ)
    if (bat.voltage_mv < 3300) {
        is_low_power_warning_ = true;
        bsp_.led_set(bsp::LedId::Warning, bsp::LedState::On);
    } else {
        is_low_power_warning_ = false;
        bsp_.led_set(bsp::LedId::Warning, bsp::LedState::Off);
    }

    // Штатний цикл вимірювання з використанням RAII-гарантії живлення
    bsp_.led_set(bsp::LedId::SystemStatus, bsp::LedState::On);
    {
        bsp::PowerDomainGuard sensor_power(bsp_, bsp::PowerDomain::Sensors);
        if (sensor_power.is_active()) {
            auto env_res = bsp_.read_environment();
            // Обробка отриманих даних env_res...
        }
    }
    bsp_.led_set(bsp::LedId::SystemStatus, bsp::LedState::Off);
}

} // namespace app
```
:::

#### Асемблерний аналіз непрямого виклику на ARM Cortex-M

Звернення до методу через покажчик `ctx->bsp->led_set(...)` компілюється в компактну послідовність із чотирьох інструкцій архітектури ARM Thumb-2:
1. `LDR r3, [r0, #0]`: Завантаження покажчика на структуру `bsp_driver_t` із контексту `supervisor_t`.
2. `LDR r3, [r3, #0]`: Завантаження адреси функції `led_set` із таблиці методів.
3. `MOVS r1, #1`: Підготовка аргументу стану світлодіода у регістрі `r1`.
4. `BLX r3`: Непрямий перехід із збереженням адреси повернення (*Branch with Link and Exchange*).

Ця операція виконується за 3–4 такти процесора (близько 40 наносекунд при частоті ядра 84 МГц), що є абсолютно непомітним на тлі будь-якої взаємодії з апаратурою, де часові масштаби вимірюються мікросекундами або мілісекундами.

---

### Цільова реалізація для мікроконтролера STM32

У цільовій збірці для реального заліза створюється екземпляр драйвера, який транслює виклики у реальні функції периферійного рівня STM32 HAL.

:::tabs
```c
/* --- bsp_target_stm32.c: Реалізація для цільового мікроконтролера --- */
#include "supervisor.h"
#include "stm32f4xx_hal.h"

extern ADC_HandleTypeDef hadc1;
extern I2C_HandleTypeDef hi2c1;

static bsp_status_t target_led_set(board_led_id_t led, board_led_state_t state) {
    GPIO_PinState ps = (state == BOARD_LED_STATE_ON) ? GPIO_PIN_SET : GPIO_PIN_RESET;
    if (led == BOARD_LED_ID_SYSTEM_STATUS) {
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, ps);
        return BSP_STATUS_OK;
    } else if (led == BOARD_LED_ID_WARNING) {
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, ps);
        return BSP_STATUS_OK;
    }
    return BSP_STATUS_ERR_INVALID_PARAM;
}

static bsp_status_t target_power_set(board_power_domain_t domain, bool enable) {
    if (domain == BOARD_POWER_DOMAIN_SENSORS) {
        // P-MOSFET ключ (Active-Low): 0 — увімкнено, 1 — знеструмлено
        HAL_GPIO_WritePin(GPIOE, GPIO_PIN_3, enable ? GPIO_PIN_RESET : GPIO_PIN_SET);
        if (enable) {
            HAL_Delay(15); // Затримка заряду фільтрів
        }
        return BSP_STATUS_OK;
    }
    return BSP_STATUS_ERR_UNSUPPORTED;
}

static bsp_status_t target_get_battery(board_battery_metrics_t *m) {
    HAL_ADC_Start(&hadc1);
    if (HAL_ADC_PollForConversion(&hadc1, 10) == HAL_OK) {
        uint32_t raw = HAL_ADC_GetValue(&hadc1);
        // Дільник R1=100кОм, R2=200кОм -> V_bat = V_pin * 1.5
        uint32_t v_pin_mv = (raw * 3300) / 4095;
        m->voltage_mv = (uint16_t)((v_pin_mv * 3) / 2);
        m->charge_percent = (m->voltage_mv > 4200) ? 100 : (m->voltage_mv < 3000 ? 0 : (m->voltage_mv - 3000) / 12);
        return BSP_STATUS_OK;
    }
    return BSP_STATUS_ERR_TIMEOUT;
}

static bsp_status_t target_read_env(board_env_metrics_t *env) {
    uint8_t raw[6] = {0};
    // Читання BME280 за адресою 0x76
    if (HAL_I2C_Mem_Read(&hi2c1, 0x76 << 1, 0xF7, 1, raw, 6, 50) == HAL_OK) {
        int32_t temp_raw = (raw[3] << 12) | (raw[4] << 4) | (raw[5] >> 4);
        env->temperature_centi_c = (int16_t)((temp_raw * 100) / 5120);
        return BSP_STATUS_OK;
    }
    return BSP_STATUS_ERR_BUS_FAULT;
}

static bsp_status_t target_enter_sleep(board_sleep_mode_t m, uint32_t ms) {
    (void)ms;
    if (m == BOARD_SLEEP_MODE_DEEP) {
        HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
        return BSP_STATUS_OK;
    }
    return BSP_STATUS_ERR_UNSUPPORTED;
}

const bsp_driver_t stm32_bsp_driver = {
    .led_set = target_led_set,
    .power_domain_set = target_power_set,
    .get_battery_metrics = target_get_battery,
    .read_environment = target_read_env,
    .enter_low_power = target_enter_sleep
};
```
```cpp
// --- bsp_target_stm32.cpp: Реалізація IBoardSupport для STM32 ---
#include "supervisor.hpp"
#include "stm32f4xx_hal.h"

extern ADC_HandleTypeDef hadc1;
extern I2C_HandleTypeDef hi2c1;

namespace bsp {

class Stm32TargetBoard final : public IBoardSupport {
public:
    Status init() noexcept override { return Status::Ok; }
    Status deinit() noexcept override { return Status::Ok; }

    Status led_set(LedId led, LedState state) noexcept override {
        const auto pin_state = (state == LedState::On) ? GPIO_PIN_SET : GPIO_PIN_RESET;
        if (led == LedId::SystemStatus) {
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, pin_state);
            return Status::Ok;
        } else if (led == LedId::Warning) {
            HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, pin_state);
            return Status::Ok;
        }
        return Status::InvalidParam;
    }

    Status led_toggle(LedId led) noexcept override {
        if (led == LedId::SystemStatus) {
            HAL_GPIO_TogglePin(GPIOB, GPIO_PIN_12);
            return Status::Ok;
        }
        return Status::InvalidParam;
    }

    Status power_domain_set(PowerDomain domain, bool enable) noexcept override {
        if (domain == PowerDomain::Sensors) {
            HAL_GPIO_WritePin(GPIOE, GPIO_PIN_3, enable ? GPIO_PIN_RESET : GPIO_PIN_SET);
            if (enable) {
                HAL_Delay(15);
            }
            return Status::Ok;
        }
        return Status::Unsupported;
    }

    std::expected<BatteryMetrics, Status> get_battery_metrics() noexcept override {
        HAL_ADC_Start(&hadc1);
        if (HAL_ADC_PollForConversion(&hadc1, 10) == HAL_OK) {
            const uint32_t raw = HAL_ADC_GetValue(&hadc1);
            const uint32_t v_pin = (raw * 3300) / 4095;
            BatteryMetrics m;
            m.voltage_mv = static_cast<uint16_t>((v_pin * 3) / 2);
            m.is_critical_low = (m.voltage_mv < 3000);
            return m;
        }
        return std::unexpected(Status::Timeout);
    }

    std::expected<EnvironmentMetrics, Status> read_environment() noexcept override {
        uint8_t raw[6] = {0};
        if (HAL_I2C_Mem_Read(&hi2c1, 0x76 << 1, 0xF7, 1, raw, 6, 50) == HAL_OK) {
            const int32_t temp_raw = (raw[3] << 12) | (raw[4] << 4) | (raw[5] >> 4);
            EnvironmentMetrics env;
            env.temperature_centi_c = static_cast<int16_t>((temp_raw * 100) / 5120);
            return env;
        }
        return std::unexpected(Status::BusFault);
    }

    Status enter_low_power(SleepMode mode, std::chrono::milliseconds) noexcept override {
        if (mode == SleepMode::Deep) {
            HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
            return Status::Ok;
        }
        return Status::Unsupported;
    }

    std::chrono::milliseconds get_uptime() const noexcept override {
        return std::chrono::milliseconds(HAL_GetTick());
    }

    void delay(std::chrono::microseconds us) const noexcept override {
        uint32_t ticks = (SystemCoreClock / 1000000) * static_cast<uint32_t>(us.count());
        uint32_t start = DWT->CYCCNT;
        while ((DWT->CYCCNT - start) < ticks);
    }
};

} // namespace bsp
```
:::

---

### Хостовий мок-об'єкт та модульне тестування (Unit Tests)

Для перевірки логіки на комп'ютері розробника створюється тестовий мок, що записує всі виклики у внутрішній стан і дозволяє налаштовувати фіктивну напругу батареї та імітувати збої.

:::tabs
```c
/* --- test_supervisor_host.c: Тестування на комп'ютері розробника --- */
#include "supervisor.h"
#include <stdio.h>
#include <assert.h>

// Стан тестового оточення
static uint16_t mock_voltage_mv = 3800;
static board_led_state_t mock_warn_led = BOARD_LED_STATE_OFF;
static bool mock_sensors_powered = false;
static bool mock_sleep_entered = false;

static bsp_status_t mock_led_set(board_led_id_t led, board_led_state_t state) {
    if (led == BOARD_LED_ID_WARNING) mock_warn_led = state;
    return BSP_STATUS_OK;
}

static bsp_status_t mock_power_set(board_power_domain_t domain, bool enable) {
    if (domain == BOARD_POWER_DOMAIN_SENSORS) mock_sensors_powered = enable;
    return BSP_STATUS_OK;
}

static bsp_status_t mock_get_bat(board_battery_metrics_t *m) {
    m->voltage_mv = mock_voltage_mv;
    return BSP_STATUS_OK;
}

static bsp_status_t mock_read_env(board_env_metrics_t *e) {
    e->temperature_centi_c = 2250;
    return BSP_STATUS_OK;
}

static bsp_status_t mock_enter_sleep(board_sleep_mode_t m, uint32_t ms) {
    (void)m; (void)ms;
    mock_sleep_entered = true;
    return BSP_STATUS_OK;
}

static const bsp_driver_t mock_bsp = {
    .led_set = mock_led_set,
    .power_domain_set = mock_power_set,
    .get_battery_metrics = mock_get_bat,
    .read_environment = mock_read_env,
    .enter_low_power = mock_enter_sleep
};

int main(void) {
    supervisor_t sup;
    supervisor_init(&sup, &mock_bsp);

    // Тест 1: Нормальна напруга (3800 мВ)
    mock_voltage_mv = 3800;
    supervisor_run_cycle(&sup);
    assert(sup.is_low_power_warning == false);
    assert(mock_warn_led == BOARD_LED_STATE_OFF);
    assert(mock_sleep_entered == false);
    printf("[PASS] Test Normal Voltage 3800mV\n");

    // Тест 2: Попередження про розряд (3200 мВ)
    mock_voltage_mv = 3200;
    supervisor_run_cycle(&sup);
    assert(sup.is_low_power_warning == true);
    assert(mock_warn_led == BOARD_LED_STATE_ON);
    assert(mock_sleep_entered == false);
    printf("[PASS] Test Warning Voltage 3200mV\n");

    // Тест 3: Аварійне вимкнення (2900 мВ)
    mock_voltage_mv = 2900;
    supervisor_run_cycle(&sup);
    assert(sup.is_critical_shutdown == true);
    assert(mock_sensors_powered == false);
    assert(mock_sleep_entered == true);
    printf("[PASS] Test Critical Shutdown 2900mV\n");

    printf("\nУсі 3 модульні тести успішно пройшли на хості x86-64 за 0.001 с!\n");
    return 0;
}
```
```cpp
// --- test_supervisor_host.cpp: GoogleTest сумісний набір тестів ---
#include "supervisor.hpp"
#include <iostream>
#include <cassert>

namespace bsp {

class MockBoardSupport final : public IBoardSupport {
public:
    uint16_t voltage_mv{3800};
    LedState warn_led{LedState::Off};
    LedState status_led{LedState::Off};
    bool sensors_powered{false};
    bool sleep_entered{false};

    Status init() noexcept override { return Status::Ok; }
    Status deinit() noexcept override { return Status::Ok; }

    Status led_set(LedId led, LedState state) noexcept override {
        if (led == LedId::Warning) warn_led = state;
        if (led == LedId::SystemStatus) status_led = state;
        return Status::Ok;
    }
    Status led_toggle(LedId led) noexcept override {
        if (led == LedId::Warning) warn_led = (warn_led == LedState::On ? LedState::Off : LedState::On);
        return Status::Ok;
    }

    Status power_domain_set(PowerDomain domain, bool enable) noexcept override {
        if (domain == PowerDomain::Sensors) sensors_powered = enable;
        return Status::Ok;
    }

    std::expected<BatteryMetrics, Status> get_battery_metrics() noexcept override {
        BatteryMetrics m;
        m.voltage_mv = voltage_mv;
        return m;
    }

    std::expected<EnvironmentMetrics, Status> read_environment() noexcept override {
        EnvironmentMetrics e;
        e.temperature_centi_c = 2250;
        return e;
    }

    Status enter_low_power(SleepMode, std::chrono::milliseconds) noexcept override {
        sleep_entered = true;
        return Status::Ok;
    }

    std::chrono::milliseconds get_uptime() const noexcept override {
        return std::chrono::milliseconds(1000);
    }
    void delay(std::chrono::microseconds) const noexcept override {}
};

} // namespace bsp

int main() {
    bsp::MockBoardSupport mock;
    app::SystemSupervisor supervisor(mock);

    // Сценарій 1: Нормальна робота
    mock.voltage_mv = 3700;
    supervisor.run_cycle();
    assert(!supervisor.is_low_power_warning());
    assert(mock.warn_led == bsp::LedState::Off);
    assert(!mock.sleep_entered);
    std::cout << "[PASS] C++ Supervisor: Normal Mode\n";

    // Сценарій 2: Попередження про низький заряд
    mock.voltage_mv = 3150;
    supervisor.run_cycle();
    assert(supervisor.is_low_power_warning());
    assert(mock.warn_led == bsp::LedState::On);
    assert(!mock.sleep_entered);
    std::cout << "[PASS] C++ Supervisor: Low Power Warning\n";

    // Сценарій 3: Критичний розряд та глибокий сон
    mock.voltage_mv = 2850;
    supervisor.run_cycle();
    assert(supervisor.is_critical_shutdown());
    assert(!mock.sensors_powered);
    assert(mock.sleep_entered);
    std::cout << "[PASS] C++ Supervisor: Critical Deep Sleep\n";

    std::cout << "\nУсі тести C++ успішно виконано на хостовому ПК!\n";
    return 0;
}
```
:::

#### Переваги мок-об'єктів для виявлення прихованих дефектів

Використання мок-об'єктів дозволяє виявити помилки проектування задовго до виготовлення перших зразків друкованих плат:
1. **Інжекція збоїв комунікації (*Fault Injection*)**: Мок можна налаштувати так, щоб він повертав `BSP_STATUS_ERR_BUS_FAULT` на кожен третій виклик. Це дозволяє перевірити, чи коректно супервізор перезапускає цикл вимірювання без зависання в нескінченному циклі очікування.
2. **Перевірка часових інваріантів**: Мок записує історію викликів разом із мітками часу. Тест може автоматично перевірити, що між викликом `power_domain_set(Sensors, true)` та `read_environment()` обов'язково минуло не менше 15 мілісекунд стабілізації.
3. **Контроль витоків пам'яті та стану**: На хостовому ПК тести запускаються під діагностичними інструментами `AddressSanitizer` (ASan) та `Valgrind`, що миттєво ловлять виходи за межі масивів або розіменування нульових покажчиків, які на мікроконтролері призвели б до мовчазного HardFault.

---

### Налаштування системи збірки CMake для подвійного таргету

Головна практична цінність шаблону Dependency Injection полягає в тому, що система збірки (CMake) може формувати два незалежні бінарні файли з однієї кодової бази:
1. **Цільовий ELF-файл для прошивки мікроконтролера** (компілятор `arm-none-eabi-gcc`): лінкує спільний `supervisor.c` із файлом `bsp_target_stm32.c` та бібліотеками STM32Cube.
2. **Виконуваний файл юніт-тестів для хоста** (нативний компілятор `gcc` або `clang` на комп'ютері розробника чи в CI): лінкує той самий `supervisor.c` із файлом `test_supervisor_host.c`.

```cmake
# CMakeLists.txt: Подвійна збірка (Target Firmware vs Host Unit Tests)
cmake_minimum_required(VERSION 3.22)
project(FirmwareProject C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 23)

# Спільне ядро бізнес-логіки (100% переносний код)
add_library(app_core STATIC
    supervisor.c
)
target_include_directories(app_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

# 1. Якщо компілюємо під цільовий мікроконтролер ARM
if(CMAKE_CROSSCOMPILING)
    add_executable(firmware.elf
        main.c
        bsp_target_stm32.c
    )
    target_link_libraries(firmware.elf PRIVATE app_core stm32_hal)
else()
    # 2. Якщо компілюємо під хостовий ПК для CI/CD
    enable_testing()
    add_executable(unit_tests
        test_supervisor_host.c
    )
    target_link_libraries(unit_tests PRIVATE app_core)
    add_test(NAME SupervisorTests COMMAND unit_tests)
endif()
```

Запуск тестів у консолі розробника або в автоматизованому пайплайні GitHub Actions виконується двома командами:
```bash
cmake -B build_host -S .
cmake --build build_host
ctest --test-dir build_host --output-on-failure
```

---

### Порівняльний аналіз поліморфізму у вбудованих системах

Розробники мають у розпорядженні три альтернативні техніки реалізації поліморфізму для межі BSP, кожна з яких має свій баланс гнучкості та накладних витрат:

| Метод реалізації | Накладні витрати Flash/RAM | Швидкодія виклику | Гнучкість підміни | Сфера застосування |
| :--- | :--- | :--- | :--- | :--- |
| **Лінкувальний поліморфізм** (Link-time Selection) | **0 байтів** (абсолютний нуль) | Прямий виклик функції `BL` (1 такт) | Тільки під час збірки (статичний вибір `.c` файлу в CMake) | Прості проєкти з єдиною ревізією плати у кожній збірці |
| **Таблиця покажчиків / Vtable** (Runtime DI) | 24–40 байтів Flash, 4 байти покажчика в RAM | Непрямий виклик `LDR + BLX` (3–4 такти) | Динамічна підміна в рантаймі, моки в тестах | Універсальні комерційні прошивки, модульні тести |
| **Шаблони / CRTP** (C++ Static Polymorphism) | **0 байтів** RAM, можливий дубляж Flash | Повна інлайнізація `inline` (0 тактів) | Статична типізація під час компіляції | Високочастотні контури керування двигунами, DSP фільтри |

Для переважної більшості задач керування платою (опитування сенсорів з частотою 1–100 Гц, моніторинг батареї, керування світлодіодами та реле) час виконання операцій становить від сотень мікросекунд до десятків мілісекунд. На цьому фоні 3 додаткові такти процесора на розіменування покажчика таблиці методів є мізерною ціною за повну переносимість та можливість безперервного автоматичного тестування кодової бази.
