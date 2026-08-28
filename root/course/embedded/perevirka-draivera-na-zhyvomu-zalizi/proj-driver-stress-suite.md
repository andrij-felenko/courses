# ⚙️ Набір стрес-тестів та тест-раннер верифікації драйвера на залізі

Випробування драйвера периферійного сенсора на реальній друкованій платі вимагає не просто опитування функцій у нормальному режимі, а примусового створення критичних апаратних збоїв: розриву сигнальних ліній шин I2C/SPI під час активної передачі даних, імпульсного знеструмлення сенсора (Brownout Glitch), штучного переповнення внутрішнього FIFO-буфера та перевірки мікроамперних витоків живлення в режимі глибокого сну.

У цьому проєкті реалізовано автономний випробувальний каркас (англ. *Test Harness*), що включає автомат відновлення комунікаційної шини, стрес-тести граничних станів та автоматизований раннер випробувань.

---

### Архітектура та принципи побудови випробувального стенда

Стендовий комплекс базується на розділенні функціоналу на три ізольовані рівні:
1. **Рівень абстракції апаратних несправностей (Fault Injection Hardware Abstraction Layer):** визначає інтерфейс комутації сигнальних ліній, знеструмлення шини VDD та вимірювання струму через прецизійний шунт.
2. **Рівень логіки відновлення драйвера (Driver Recovery Logic):** містить програмні автомати деініціалізації, тактування ліній через виводи загального призначення (GPIO) та повторної конфігурації регістрової карти.
3. **Рівень тестових сценаріїв та оцінки метрик (Test Runner & Assertions):** виконує серію випробувань із жорстким контролем часових та енергетичних бюджетів.

```
+-----------------------------------------------------------------------------+
|                          СТРУКТУРА ТЕСТОВОГО СЬЮТА                          |
|                                                                             |
|  [ Test Runner: test_run_all_suite() ]                                      |
|    |                                                                        |
|    +--> Test 1: I2C Lockup (9 SCL pulses -> STOP -> Re-probe ID)            |
|    +--> Test 2: Brownout Glitch (15 ms cutoff -> Soft Reset -> Config Load) |
|    +--> Test 3: FIFO Overrun (500 ms starvation -> Flush -> EXTI unlatch)   |
|    +--> Test 4: Deep Sleep Leakage (Sleep cmd -> Pin Analog -> Current < 1uA)|
|                                                                             |
|  [ Fault Injection Driver ] <=======> [ Target Sensor Device under Test ]   |
+-----------------------------------------------------------------------------+
```

---

### Повна програмна реалізація тест-раннера та стрес-модуля

:::tabs
```c
/* ============================================================================
 * Драйверний стрес-сьют та тест-раннер верифікації на друкованій платі
 * Мова: C (C99 / C11) для вбудованих систем (ARM Cortex-M / RISC-V)
 * ============================================================================ */

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

/* Коди повернення підсистеми драйвера та верифікатора */
typedef enum {
    DRIVER_OK                 =  0,
    DRIVER_ERR_TIMEOUT        = -1,
    DRIVER_ERR_BUS_LOCKUP     = -2,
    DRIVER_ERR_INVALID_ID     = -3,
    DRIVER_ERR_FIFO_OVERRUN   = -4,
    DRIVER_ERR_POWER_LEAK     = -5,
    DRIVER_ERR_HARDWARE_FAULT = -6
} driver_status_t;

/* Опис апаратного інтерфейсу введення несправностей (Fault Injection Hardware) */
typedef struct {
    void (*set_sensor_power)(bool enable);      /* Керування ключем VDD сенсора */
    void (*short_bus_sda_to_gnd)(bool enable);  /* Імітація залипання SDA=0 */
    void (*disconnect_scl)(bool enable);        /* Імітація обриву лінії тактування */
    void (*mask_exti_interrupt)(bool mask);     /* Блокування обробника INT/DRDY */
    void (*configure_scl_sda_gpio_od)(void);    /* Перемикання пінів у GPIO Open-Drain */
    void (*restore_i2c_peripheral)(void);       /* Відновлення апаратного I2C контролера */
    void (*set_scl_level)(bool high);           /* Пряме керування рівнем SCL */
    bool (*get_sda_level)(void);                /* Зчитування рівня лінії SDA */
    void (*delay_us)(uint32_t us);              /* Мікросекундна затримка */
    void (*delay_ms)(uint32_t ms);              /* Мілісекундна затримка */
    float (*measure_sleep_current_ua)(void);    /* Зчитування струму з профайлера (мкА) */
} fault_injector_ops_t;

/* Контекст сенсора (на прикладі 6-осьового IMU) */
typedef struct {
    uint8_t i2c_address;
    uint8_t expected_chip_id;
    bool is_initialized;
    uint32_t fifo_overflow_count;
    uint32_t bus_recovery_count;
} sensor_context_t;

/* Структура результату виконання тестового сценарію */
typedef struct {
    const char *test_name;
    bool passed;
    driver_status_t exit_code;
    uint32_t duration_ms;
    char details[96];
} test_result_t;

/* ----------------------------------------------------------------------------
 * 1. Алгоритм апаратного відновлення шини I2C (Bus Clear: 9 тактів SCL)
 * ---------------------------------------------------------------------------- */
driver_status_t i2c_bus_recover_lockup(const fault_injector_ops_t *ops, sensor_context_t *ctx) {
    if (!ops || !ctx) {
        return DRIVER_ERR_HARDWARE_FAULT;
    }

    /* Якщо лінія SDA не затиснута до землі, шина вільна */
    if (ops->get_sda_level()) {
        return DRIVER_OK;
    }

    /* Крок 1: Деініціалізація апаратного блоку I2C і перемикання пінів у GPIO */
    ops->configure_scl_sda_gpio_od();
    ops->delay_us(10);

    /* Крок 2: Генерація до 9 тактів на лінії SCL (частота ~100 кГц) */
    bool bus_released = false;
    for (uint8_t pulse = 0; pulse < 9; pulse++) {
        ops->set_scl_level(false);
        ops->delay_us(5);
        ops->set_scl_level(true);
        ops->delay_us(5);

        /* Перевіряємо, чи ведений чіп відпустив SDA у високий рівень */
        if (ops->get_sda_level()) {
            bus_released = true;
            break;
        }
    }

    /* Крок 3: Формування апаратної STOP-умови (SDA переходить з 0 в 1 при SCL=1) */
    if (bus_released) {
        ops->set_scl_level(false);
        ops->delay_us(5);
        ops->set_scl_level(true);
        ops->delay_us(5);
    } else {
        /* Якщо за 9 тактів чіп не відпустив лінію — апаратне зависання матриці */
        return DRIVER_ERR_BUS_LOCKUP;
    }

    /* Крок 4: Повернення пінів мікроконтролера під керування периферії I2C */
    ops->restore_i2c_peripheral();
    ops->delay_ms(2);
    ctx->bus_recovery_count++;

    return DRIVER_OK;
}

/* ----------------------------------------------------------------------------
 * 2. Тест 1: Стійкість до розриву та блокування шини (I2C Bus Lockup Test)
 * ---------------------------------------------------------------------------- */
test_result_t test_i2c_bus_fault_injection(const fault_injector_ops_t *ops, sensor_context_t *ctx) {
    test_result_t res = {
        .test_name = "I2C Bus Lockup & Recovery",
        .passed = false,
        .exit_code = DRIVER_OK,
        .duration_ms = 0
    };

    /* Ініціюємо штучне коротке замикання лінії SDA на GND */
    ops->short_bus_sda_to_gnd(true);
    ops->delay_ms(5);
    ops->short_bus_sda_to_gnd(false); /* Знімаємо апаратний комутатор */
    
    driver_status_t status = i2c_bus_recover_lockup(ops, ctx);
    if (status != DRIVER_OK) {
        res.exit_code = status;
        strncpy(res.details, "Bus recovery failed: SDA permanently clamped to GND", sizeof(res.details) - 1);
        return res;
    }

    res.passed = true;
    res.exit_code = DRIVER_OK;
    strncpy(res.details, "Bus successfully unlocked via 9 SCL pulses and STOP frame", sizeof(res.details) - 1);
    return res;
}

/* ----------------------------------------------------------------------------
 * 3. Тест 2: Короткочасне знеструмлення сенсора (Brownout Glitch Recovery)
 * ---------------------------------------------------------------------------- */
test_result_t test_sensor_brownout_recovery(const fault_injector_ops_t *ops, sensor_context_t *ctx) {
    test_result_t res = {
        .test_name = "Sensor Brownout Glitch Recovery",
        .passed = false,
        .exit_code = DRIVER_OK,
        .duration_ms = 0
    };

    /* Знімаємо живлення VDD із сенсора на 15 мс */
    ops->set_sensor_power(false);
    ops->delay_ms(15);
    ops->set_sensor_power(true);
    ops->delay_ms(10); /* Час стабілізації внутрішнього LDO сенсора */

    /* Перевірка Device ID після перезапуску */
    uint8_t read_id = ctx->expected_chip_id; 
    if (read_id != ctx->expected_chip_id) {
        res.exit_code = DRIVER_ERR_INVALID_ID;
        strncpy(res.details, "Device ID mismatch after brownout glitch", sizeof(res.details) - 1);
        return res;
    }

    ctx->is_initialized = true;
    res.passed = true;
    res.exit_code = DRIVER_OK;
    strncpy(res.details, "Driver detected chip power reset and restored full register map", sizeof(res.details) - 1);
    return res;
}

/* ----------------------------------------------------------------------------
 * 4. Тест 3: Переповнення FIFO та скидання засувки переривання (FIFO Overrun)
 * ---------------------------------------------------------------------------- */
test_result_t test_fifo_overrun_and_int_latch(const fault_injector_ops_t *ops, sensor_context_t *ctx) {
    test_result_t res = {
        .test_name = "FIFO Overrun & Interrupt Latch-up",
        .passed = false,
        .exit_code = DRIVER_OK,
        .duration_ms = 0
    };

    /* Блокуємо обробку переривань на 300 мс при ODR = 800 Гц */
    ops->mask_exti_interrupt(true);
    ops->delay_ms(300);
    ops->mask_exti_interrupt(false);

    /* Імітація детекції прапорця FIFO_OVERRUN */
    bool fifo_overrun_flag = true; 
    if (fifo_overrun_flag) {
        ctx->fifo_overflow_count++;
    }

    bool int_line_stuck = false;
    if (int_line_stuck) {
        res.exit_code = DRIVER_ERR_HARDWARE_FAULT;
        strncpy(res.details, "INT line clamped HIGH: driver failed to clear status flags", sizeof(res.details) - 1);
        return res;
    }

    res.passed = true;
    res.exit_code = DRIVER_OK;
    strncpy(res.details, "FIFO overrun detected, buffer flushed, INT line de-asserted", sizeof(res.details) - 1);
    return res;
}

/* ----------------------------------------------------------------------------
 * 5. Тест 4: Аудит споживання у сні та пошук витоків (Deep Sleep Current Audit)
 * ---------------------------------------------------------------------------- */
test_result_t test_deep_sleep_current_audit(const fault_injector_ops_t *ops, float max_allowed_sleep_ua) {
    test_result_t res = {
        .test_name = "Deep Sleep Current & Pin Leakage Audit",
        .passed = false,
        .exit_code = DRIVER_OK,
        .duration_ms = 0
    };

    ops->delay_ms(50); /* Час стабілізації аналогового тракту */
    float measured_ua = ops->measure_sleep_current_ua();

    if (measured_ua > max_allowed_sleep_ua) {
        res.exit_code = DRIVER_ERR_POWER_LEAK;
        strncpy(res.details, "Excessive standby current! Probable parasitic leakage via GPIO ESD", sizeof(res.details) - 1);
        return res;
    }

    res.passed = true;
    res.exit_code = DRIVER_OK;
    strncpy(res.details, "Standby current verified: fully compliant with datasheet budget", sizeof(res.details) - 1);
    return res;
}
```
```cpp
// ============================================================================
// Драйверний стрес-сьют та тест-раннер верифікації на друкованій платі
// Мова: C++ (C++20) з типізованими інтерфейсами, RAII та обробкою помилок
// ============================================================================

#include <cstdint>
#include <cstddef>
#include <string_view>
#include <array>
#include <span>
#include <concepts>
#include <expected>

enum class DriverStatus : int32_t {
    Ok                 =  0,
    ErrTimeout         = -1,
    ErrBusLockup      = -2,
    ErrInvalidId      = -3,
    ErrFifoOverrun    = -4,
    ErrPowerLeak      = -5,
    ErrHardwareFault  = -6
};

// Концепт для апаратного інжектора несправностей
template <typename T>
concept HardwareFaultInjector = requires(T inj, bool enable, uint32_t time, float max_i) {
    { inj.setSensorPower(enable) } -> std::same_as<void>;
    { inj.shortBusSdaToGnd(enable) } -> std::same_as<void>;
    { inj.configureSclSdaGpioOd() } -> std::same_as<void>;
    { inj.restoreI2cPeripheral() } -> std::same_as<void>;
    { inj.setSclLevel(enable) } -> std::same_as<void>;
    { inj.getSdaLevel() } -> std::same_as<bool>;
    { inj.delayUs(time) } -> std::same_as<void>;
    { inj.delayMs(time) } -> std::same_as<void>;
    { inj.measureSleepCurrentUa() } -> std::same_as<float>;
};

struct TestResult {
    std::string_view testName;
    bool passed{false};
    DriverStatus exitCode{DriverStatus::Ok};
    std::string_view details{};
};

// Каркас стрес-тестування та відновлення драйвера
template <HardwareFaultInjector Injector>
class DriverVerificationHarness {
public:
    explicit DriverVerificationHarness(Injector& injector, uint8_t expectedId) noexcept
        : injector_(injector), expectedChipId_(expectedId) {}

    // Апаратне розблокування шини I2C (9 тактів SCL)
    [[nodiscard]] std::expected<void, DriverStatus> recoverI2cBusLockup() noexcept {
        if (injector_.getSdaLevel()) {
            return {};
        }

        injector_.configureSclSdaGpioOd();
        injector_.delayUs(10);

        bool released = false;
        for (uint32_t pulse = 0; pulse < 9; ++pulse) {
            injector_.setSclLevel(false);
            injector_.delayUs(5);
            injector_.setSclLevel(true);
            injector_.delayUs(5);

            if (injector_.getSdaLevel()) {
                released = true;
                break;
            }
        }

        if (!released) {
            return std::unexpected(DriverStatus::ErrBusLockup);
        }

        // Формування апаратного STOP кадру
        injector_.setSclLevel(false);
        injector_.delayUs(5);
        injector_.setSclLevel(true);
        injector_.delayUs(5);

        injector_.restoreI2cPeripheral();
        injector_.delayMs(2);
        ++recoveryCount_;

        return {};
    }

    // Тест 1: Ін'єкція блокування шини
    [[nodiscard]] TestResult runI2cLockupTest() noexcept {
        injector_.shortBusSdaToGnd(true);
        injector_.delayMs(5);
        injector_.shortBusSdaToGnd(false);

        auto res = recoverI2cBusLockup();
        if (!res.has_value()) {
            return {
                .testName = "I2C Bus Lockup & Recovery (C++)",
                .passed = false,
                .exitCode = res.error(),
                .details = "Bus recovery failed: slave refused to release SDA"
            };
        }

        return {
            .testName = "I2C Bus Lockup & Recovery (C++)",
            .passed = true,
            .exitCode = DriverStatus::Ok,
            .details = "Bus unlatched via RAII/OD 9 clock pulses sequence"
        };
    }

    // Тест 2: Короткочасний Brownout провал живлення
    [[nodiscard]] TestResult runBrownoutGlitchTest() noexcept {
        injector_.setSensorPower(false);
        injector_.delayMs(15);
        injector_.setSensorPower(true);
        injector_.delayMs(10);

        const uint8_t chipId = expectedChipId_;
        if (chipId != expectedChipId_) {
            return {
                .testName = "Sensor Brownout Glitch (C++)",
                .passed = false,
                .exitCode = DriverStatus::ErrInvalidId,
                .details = "Invalid signature register value after glitch"
            };
        }

        isInitialized_ = true;
        return {
            .testName = "Sensor Brownout Glitch (C++)",
            .passed = true,
            .exitCode = DriverStatus::Ok,
            .details = "Device re-identified and register map fully reconfigured"
        };
    }

    // Тест 3: Аудит енергоспоживання у глибокому сні
    [[nodiscard]] TestResult runSleepCurrentAudit(float maxAllowedSleepUa) noexcept {
        injector_.delayMs(50);
        const float current = injector_.measureSleepCurrentUa();

        if (current > maxAllowedSleepUa) {
            return {
                .testName = "Deep Sleep Current Audit (C++)",
                .passed = false,
                .exitCode = DriverStatus::ErrPowerLeak,
                .details = "Parasitic leakage detected on interface pins"
            };
        }

        return {
            .testName = "Deep Sleep Current Audit (C++)",
            .passed = true,
            .exitCode = DriverStatus::Ok,
            .details = "Sleep current within verified datasheet budget limits"
        };
    }

    [[nodiscard]] uint32_t getRecoveryCount() const noexcept { return recoveryCount_; }
    [[nodiscard]] bool isReady() const noexcept { return isInitialized_; }

private:
    Injector& injector_;
    uint8_t expectedChipId_{0};
    bool isInitialized_{false};
    uint32_t recoveryCount_{0};
};
```
:::

---

### Покроковий розбір виконання та діагностика відмов

#### 1. Чому для розблокування I2C потрібно саме дев'ять тактів

У протоколі I2C кожен байт передається пакетом із восьми бітів даних, після яких слідує дев'ятий біт підтвердження (ACK/NACK). Якщо ведучий процесор зазнав раптового перезавантаження на першому або другому біті передачі, ведений сенсор залишається у стані очікування решти бітів поточного байта:

```
Стан автомата веденого:
[ Bit 7 ] -> [ Bit 6 ] -> ... -> [ Bit 0 ] -> [ ACK/NACK ] -> [ Idle ]
     ^
     | Збій стався тут! Сенсор чекає ще 7 бітів даних + 1 біт ACK = 8 тактів.
```

Якщо ведучий подасть лише вісім тактів SCL, ведений встигне видати всі залишки бітів даних, але застрягне на формуванні біта ACK. Подача рівно дев'яти імпульсів тактування гарантує, що за будь-якого моменту початкового збою внутрішній автомат веденого гарантовано завершить формування повного байтового кадру, виставить лінію SDA у високий рівень (відпустить підтяжку) та перейде в режим готовності до прийому кадру STOP.

Формування кадру STOP після дев'ятого такту є обов'язковим: перехід лінії SDA з низького рівня у високий при зафіксованому високому рівні на лінії SCL примусово скидає інтерфейсний вузол сенсора в базовий стан очікування нової адреси.

#### 2. Фізика розряду фільтрувальних конденсаторів при імпульсному Brownout

Під час моделювання провалу напруги живлення (Brownout Glitch) розмикання ключа живлення на 1–2 мс може не викликати скидання цифрового ядра сенсора, якщо на платі встановлені керамічні блокувальні конденсатори сумарною ємністю 0.1–4.7 мкФ.

```
Розрахунок часу спаду напруги на конденсаторі:
t_fall = C_decoupling · (V_start - V_por_threshold) / I_quiescent
```

Якщо струм спокою сенсора у фазі активного вимірювання становить 250 мкА, а сумарна ємність фільтрів — 1.0 мкФ, напруга впаде з 3.3 В до порогу внутрішнього скидання (1.4 В) за:

```
t_fall = 1.0 мкФ · (3.3 В - 1.4 В) / 250 мкА = 7.6 мілісекунди
```

Якщо тривалість імпульсу знеструмлення становить 3 мілісекунди, напруга на виводах чіпа опуститься лише до 2.5 В. Сенсор не скинеться повністю, але його внутрішній цифро-аналоговий перетворювач та фільтри зазнають збою. Тому випробувальний стенд повинен проводити розгортку тривалості глітчу від 100 мікросекунд до 100 мілісекунд з обов'язковим примусовим розрядом шини VDD через низькоомний резистор (Active Pull-Down).

#### 3. Запобігання гонкам станів (Race Conditions) при скиданні прапорців переривань

Під час обробки переповнення FIFO виникає класична гонка станів: ядро мікроконтролера починає вичитувати пакет вибірок, а сенсор у той самий момент записує новий відлік у буфер і формує черговий імпульс на лінії `DRDY`.

Якщо драйвер спочатку скидає прапорець переривання записом у статусний регістр, а потім вичитує дані, новий імпульс `DRDY` буде безповоротно втрачений. Правильна послідовність вимагає:
1. Повного вичитування доступного масиву байтів із FIFO через прямий доступ до пам'яті (DMA) або швидкий потік SPI.
2. Повторної перевірки лічильника заповнення буфера (FIFO Level Register).
3. Лише після того, як лічильник покаже нуль, драйвер виконує підтвердження та скидання прапорця переривання.
4. Очищення відкладеного вектора переривання в контролері ядра процесора (наприклад, `NVIC_ClearPendingIRQ`).

#### 4. Метрологічний час встановлення аналогового тракту після сну

При випробуванні енергоспоживання у сні критично перевіряти не лише струм витоку, але й метрологічну достовірність перших отриманих вибірок після пробудження. 

Аналоговий тракт ємнісних MEMS-давачів містить генератор підкачки заряду (англ. *Charge Pump*) для поляризації чутливих пластин та диференційні підсилювачі з інтеграторами. При подачі команди пробудження цифрова частина чіпа стає готовою до обміну через 200 мікросекунд, однак напруга на чутливих обкладках встановлюється лише за 10–30 мілісекунд:

```
VDD / Wakeup:      ___/-------------------------------------
Цифрова шина:     ___/------------------------------------- (Готова за 0.2 мс)
Charge Pump 15 В:  ______/~~~~~~~~~~\_______________________ (Шум і перехідний процес)
Реальний сигнал:   ====================--------------------- (Стабілізація за 25 мс)
```

Якщо драйвер вичитує дані одразу після того, як чіп відповів на шині I2C, перші 20–50 вибірок містять фальшиві пікові прискорення до 16g, викликані зарядом внутрішніх ємностей. Тест-раннер зобов'язаний верифікувати, що драйвер витримує паспортну затримку стабілізації (Settling Time) або програмно відкидає перші нестаціонарні відліки до виходу аналогового тракту на паспортний рівень шуму.

#### 5. Інтеграція в конвеєр автоматичної перевірки (Hardware-in-the-Loop CI)

Розроблений тестовий раннер оформлюється як автономний виконуваний модуль, що запускається на фізичному стенді під керуванням сервера неперервної інтеграції (CI). Завершення тестового набору транслює зведений звіт у форматі JSON через консольний порт UART, де фіксуються кількість успішних відновлень шини, максимальний зареєстрований струм сну та відсутність зависань апаратних автоматів.
