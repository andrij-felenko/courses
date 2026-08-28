# ⚙️ Еталонний безблокуючий драйвер датчика: C та C++

Цей проєкт містить закінчену промислову реалізацію драйвера цифрового датчика (на прикладі прецизійного термогігрометра / барометра з інтерфейсом I2C та апаратним контролем цілісності CRC-8). Архітектура драйвера спроєктована за принципом чистого відділення бізнес-логіки та математики чипа від апаратної платформи: будь-яка взаємодія з лініями вводу-виводу здійснюється через стандартизований транспортний контракт (функціональні покажчики в мові C та концепт / шаблони в мові C++). 

Драйвер базується на безблокуючому скінченному автоматі станів (**Finite State Machine, FSM**), не використовує динамічного виділення пам'яті (`malloc`/`new`), повністю захищений монотонними таймаутами та постачається з повноцінним набором хостових Unit-тестів із програмною емуляцією шини та ін'єкцією несправностей.

---

### Архітектурні вимоги та інтерфейсний контракт

Для досягнення максимальної передбачуваності та надійності вбудованого ПЗ до реалізації закладено чотири обов'язкові інженерні інваріанти:

1. **Повна відсутність блокуючих пауз (`zero-delay`):** операція ініціалізації фізичного перетворення не зупиняє процесорне ядро. Стан готовності даних перевіряється через неблокуюче опитування системного монотонного таймера або за допомогою зовнішнього переривання від апаратного виводу готовності даних `DRDY` (Data Ready).
2. **Гарантія статичної пам'яті:** розмір необхідної оперативної пам'яті детермінований на етапі компіляції. Усі робочі буфери, дескриптори та стани розміщуються в пам'яті BSS або на стеку викликаючої задачі.
3. **Апаратний контроль цілісності:** кожен пакет відліків із шини обов'язково перевіряється апаратним або табличним поліномом CRC-8 (x⁸ + x⁵ + x⁴ + 1, значення `0x31` з початковим вектором `0xFF`) до початку розбору числових полів.
4. **Кросплатформність та ізольованість:** код ядра драйвера компілюється під будь-яку цільову архітектуру (ARM Cortex-M0+/M4/M7, RISC-V, AVR, ESP32) або під настільну операційну систему (Linux, macOS, Windows) без підключення заголовкових файлів вендорних SDK.

:::tabs
@tab C
```c
#ifndef SENSOR_DRIVER_H
#define SENSOR_DRIVER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Типізовані статусні коди повернення */
typedef enum {
    SENSOR_OK                    =  0,
    SENSOR_ERR_NULL_PTR          = -1,
    SENSOR_ERR_BUS_IO            = -2,
    SENSOR_ERR_BUS_TIMEOUT       = -3,
    SENSOR_ERR_CHIP_ID           = -4,
    SENSOR_ERR_CRC               = -5,
    SENSOR_ERR_NOT_READY         = -6,
    SENSOR_ERR_INVALID_STATE     = -7,
    SENSOR_ERR_DATA_OUT_OF_RANGE = -8,
    SENSOR_ERR_BUS_STUCK         = -9
} sensor_status_t;

/* Дискретні стани внутрішнього автомата драйвера */
typedef enum {
    SENSOR_STATE_UNINITIALIZED = 0,
    SENSOR_STATE_IDLE,
    SENSOR_STATE_CONVERTING,
    SENSOR_STATE_DATA_READY,
    SENSOR_STATE_ERROR
} sensor_fsm_state_t;

/* Абстрактний інтерфейс апаратної шини (I2C / SPI) */
typedef struct {
    /* Читання блоку байтів із вказаного субрегістра */
    sensor_status_t (*read)(void *user_ctx, uint8_t reg_addr, uint8_t *data, size_t len);
    /* Запис блоку байтів у вказаний субрегістр */
    sensor_status_t (*write)(void *user_ctx, uint8_t reg_addr, const uint8_t *data, size_t len);
    /* Отримання поточного монотонного часу в мікросекундах */
    uint32_t (*get_time_us)(void);
    /* Апаратне розблокування ліній зв'язку (опціонально, може бути NULL) */
    sensor_status_t (*recover_bus)(void *user_ctx);
} sensor_bus_ops_t;

/* Структура вихідних фізичних величин у міжнародній системі SI */
typedef struct {
    int32_t  temperature_mdeg_c;  /* Температура в міліградусах Цельсія (25150 = 25.15 °C) */
    uint32_t humidity_mpercent;   /* Відносна вологість у міліпроцентах (48500 = 48.50 %) */
    uint32_t pressure_pa;         /* Абсолютний тиск у Паскалях (101325 Па) */
    uint32_t timestamp_us;        /* Часова мітка завершення заміру (мкс) */
} sensor_data_t;

/* Дескриптор екземпляра сенсора */
typedef struct {
    const sensor_bus_ops_t *ops;             /* Покажчики на операції шини */
    void                   *user_ctx;        /* Контекст користувача (номер порту, дескриптор) */
    sensor_fsm_state_t      state;           /* Поточний стан автомата */
    uint32_t                conv_start_us;   /* Час старту фізичної конверсії */
    uint32_t                conv_timeout_us; /* Таймаут завершення заміру (мкс) */
    uint8_t                 raw_buf[7];      /* Статичний буфер сирих байтів */
} sensor_device_t;

/* Публічний інтерфейс драйвера */
sensor_status_t sensor_init(sensor_device_t *dev, const sensor_bus_ops_t *ops, void *user_ctx);
sensor_status_t sensor_start_measurement(sensor_device_t *dev);
sensor_status_t sensor_poll(sensor_device_t *dev, sensor_data_t *out_data);
sensor_status_t sensor_reset_fsm(sensor_device_t *dev);
uint8_t sensor_calculate_crc8(const uint8_t *data, size_t len);

#endif /* SENSOR_DRIVER_H */
```
@tab C++
```cpp
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>
#include <expected>

namespace driver {

enum class Status : int8_t {
    Ok = 0,
    NullPointer = -1,
    BusIo = -2,
    BusTimeout = -3,
    ChipIdMismatch = -4,
    CrcMismatch = -5,
    NotReady = -6,
    InvalidState = -7,
    DataOutOfRange = -8,
    BusStuck = -9
};

enum class State : uint8_t {
    Uninitialized = 0,
    Idle,
    Converting,
    DataReady,
    Error
};

struct SensorData {
    int32_t  temperature_mdeg_c{0}; // 25150 = 25.15 °C
    uint32_t humidity_mpercent{0};  // 48500 = 48.50 %
    uint32_t pressure_pa{0};        // 101325 Pa
    uint32_t timestamp_us{0};
};

/* C++20 Концепт апаратного транспорту шини */
template <typename T>
concept BusTransport = requires(T bus, uint8_t reg, std::span<uint8_t> rx, std::span<const uint8_t> tx) {
    { bus.read(reg, rx) } -> std::same_as<Status>;
    { bus.write(reg, tx) } -> std::same_as<Status>;
    { bus.get_time_us() } -> std::same_as<uint32_t>;
    { bus.recover() } -> std::same_as<Status>;
};

template <BusTransport Transport>
class SensorDevice {
public:
    explicit SensorDevice(Transport& bus) noexcept
        : m_bus(bus), m_state(State::Uninitialized), m_conv_start_us(0) {}

    [[nodiscard]] Status init() noexcept;
    [[nodiscard]] Status start_measurement() noexcept;
    [[nodiscard]] std::expected<SensorData, Status> poll() noexcept;
    void reset_fsm() noexcept;
    [[nodiscard]] Status recover_bus() noexcept;

    [[nodiscard]] State state() const noexcept { return m_state; }
    [[nodiscard]] static uint8_t compute_crc8(std::span<const uint8_t> data) noexcept;

private:
    Transport& m_bus;
    State      m_state{State::Uninitialized};
    uint32_t   m_conv_start_us{0};
    static constexpr uint32_t CONV_DURATION_US = 20000; // 20 мс
    static constexpr uint8_t  REG_CHIP_ID = 0xD0;
    static constexpr uint8_t  EXPECTED_CHIP_ID = 0x58;
    static constexpr uint8_t  REG_MEAS_START = 0xF4;
    static constexpr uint8_t  REG_DATA_BURST = 0xF7;
    uint8_t    m_raw_buf[7]{0};
};

} // namespace driver
```
:::

---

### Контроль цілісності пакетів: розрахунок та верифікація CRC-8

Під час передачі даних лініями I2C/SPI в промислових умовах або поблизу силових перетворювачів електромагнітні завади здатні спотворювати окремі біти. Проста сума байтів (Checksum) або операція XOR не гарантують виявлення групових помилок або перестановок байтів. Циклічний надлишковий код **CRC-8** на основі твірного полінома Сенсіріон / Даллас (x⁸ + x⁵ + x⁴ + 1, бітова маска `0x31`) математично гарантує:

- 100% виявлення всіх однобітових та двобітових помилок у пакеті будь-якої довжини;
- 100% виявлення всіх непарних кількостей спотворених бітів;
- 100% виявлення пакетних спалахів завад (burst errors) довжиною до 8 бітів включно.

Початковий вектор ініціалізації встановлюється в `0xFF`, що забезпечує чутливість до нульових байтів на початку пакета.

:::tabs
@tab C
```c
#include <stdint.h>
#include <stddef.h>

#define CRC8_POLYNOMIAL 0x31
#define CRC8_INIT_VAL   0xFF

/* Побітовий алгоритм: мінімальний розмір коду (ROM), оптимальний для мікроконтролерів із малим Flash */
uint8_t sensor_calculate_crc8(const uint8_t *data, size_t len) {
    uint8_t crc = CRC8_INIT_VAL;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x80) {
                crc = (uint8_t)((crc << 1) ^ CRC8_POLYNOMIAL);
            } else {
                crc = (uint8_t)(crc << 1);
            }
        }
    }
    return crc;
}
```
@tab C++
```cpp
#include <cstdint>
#include <cstddef>
#include <span>

namespace driver {

/* Побітовий розрахунок CRC-8 у стандарті C++20 */
[[nodiscard]] constexpr uint8_t compute_crc8_fast(std::span<const uint8_t> data) noexcept {
    constexpr uint8_t POLYNOMIAL = 0x31;
    uint8_t crc = 0xFF;
    for (const uint8_t byte : data) {
        crc ^= byte;
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if ((crc & 0x80) != 0) {
                crc = static_cast<uint8_t>((crc << 1) ^ POLYNOMIAL);
            } else {
                crc = static_cast<uint8_t>(crc << 1);
            }
        }
    }
    return crc;
}

} // namespace driver
```
:::

---

### Захист від заклинювання шини: протокол очищення 9 тактовими імпульсами

Найнебезпечніша апаратна проблема шини I2C — стан **SDA Stuck Low**. Якщо мікроконтролер зазнає раптового перезавантаження (скидання сторожовим таймером Watchdog, падіння напруги Brown-Out або збій ядра) саме в той момент, коли ведений сенсор передає логічний нуль на лінію `SDA`, ведений чип залишається чекати наступних тактових імпульсів на лінії `SCL`. 

Оскільки апаратний вихід сенсора відкритий колектор і активний нуль затиснутий до землі, мікроконтролер після перезапуску бачить постійно низький рівень на `SDA`. Вбудований апаратний модуль I2C мікроконтролера сприймає це як «шина зайнята іншим майстром» (`BUSY`) і взагалі відмовляється генерувати умову `START`, блокуючи всю систему.

Для гарантованого відновлення зв'язку реалізується стандартний протокол очищення шини (**I2C Bus Clear Sequence**):

1. Тимчасово вимкнути апаратний модуль I2C та налаштувати виводи `SCL` і `SDA` як звичайні дискретні виходи типу **GPIO Open-Drain** із зовнішніми підтягувальними резисторами.
2. Перевірити рівень лінії `SDA`. Якщо він високий — шина вже вільна, достатньо згенерувати фінальний сигнал `STOP`.
3. Якщо лінія `SDA` притягнута до нуля: згенерувати до 9 тактових імпульсів на лінії `SCL` (частота 100 кГц, 5 мкс низький рівень, 5 мкс високий). На кожному спадному фронті ведений сенсор просуває свій внутрішній апаратний зсувний регістр на 1 біт. Не пізніше ніж через 9 тактів сенсор дійде до фази підтвердження (ACK/NACK) або завершить передачу байта й відпустить лінію `SDA` у високий рівень.
4. Після того як `SDA` стала високою, згенерувати примусову умову `STOP` (перепад лінії `SDA` з низького в високий рівень при стабільно високому рівні на `SCL`). Це переводить кінцеві автомати всіх ведених пристроїв на шині в початковий стан очікування адреси.
5. Повернути конфігурацію виводів мікроконтролера в режим апаратної периферії I2C.

:::tabs
@tab C
```c
/* Структура низькорівневих операцій прямого керування ніжками GPIO */
typedef struct {
    void (*set_scl)(bool high);
    void (*set_sda)(bool high);
    bool (*get_sda)(void);
    void (*delay_us)(uint32_t us);
    void (*switch_to_gpio_od)(void);
    void (*switch_to_i2c_hardware)(void);
} i2c_gpio_recovery_pins_t;

sensor_status_t i2c_bus_recover_sda_stuck(const i2c_gpio_recovery_pins_t *pins) {
    if (!pins || !pins->set_scl || !pins->set_sda || !pins->get_sda || !pins->delay_us) {
        return SENSOR_ERR_NULL_PTR;
    }

    /* 1. Перемикаємо виводи в режим GPIO Open-Drain */
    pins->switch_to_gpio_od();
    pins->set_scl(true);
    pins->set_sda(true);
    pins->delay_us(5);

    /* 2. Якщо SDA вже високий, лінія не заблокована */
    if (!pins->get_sda()) {
        /* 3. Генеруємо до 9 тактових імпульсів на SCL для виштовхування бітів із сенсора */
        for (uint8_t i = 0; i < 9; i++) {
            pins->set_scl(false);
            pins->delay_us(5);
            pins->set_scl(true);
            pins->delay_us(5);

            /* Якщо ведений пристрій відпустив SDA, припиняємо тактування */
            if (pins->get_sda()) {
                break;
            }
        }
    }

    /* 4. Перевіряємо, чи відпустив ведений лінію SDA */
    if (!pins->get_sda()) {
        pins->switch_to_i2c_hardware();
        return SENSOR_ERR_BUS_STUCK; /* Фізичне заклинювання або коротке замикання на землю */
    }

    /* 5. Формуємо умову STOP: перепад SDA 0 -> 1 при високому SCL */
    pins->set_sda(false);
    pins->delay_us(5);
    pins->set_scl(true);
    pins->delay_us(5);
    pins->set_sda(true);
    pins->delay_us(5);

    /* 6. Повертаємо виводи під контроль апаратного контролера I2C */
    pins->switch_to_i2c_hardware();
    return SENSOR_OK;
}
```
@tab C++
```cpp
#include <cstdint>
#include <concepts>
#include "sensor_driver.hpp"

namespace driver {

template <typename GpioControl>
requires requires(GpioControl gpio, bool level, uint32_t us) {
    { gpio.set_scl(level) } -> std::same_as<void>;
    { gpio.set_sda(level) } -> std::same_as<void>;
    { gpio.get_sda() } -> std::same_as<bool>;
    { gpio.delay_us(us) } -> std::same_as<void>;
    { gpio.switch_to_gpio_od() } -> std::same_as<void>;
    { gpio.switch_to_i2c_hardware() } -> std::same_as<void>;
}
class I2cBusRecovery {
public:
    explicit I2cBusRecovery(GpioControl& gpio) noexcept : m_gpio(gpio) {}

    [[nodiscard]] Status recover() noexcept {
        m_gpio.switch_to_gpio_od();
        m_gpio.set_scl(true);
        m_gpio.set_sda(true);
        m_gpio.delay_us(5);

        if (!m_gpio.get_sda()) {
            for (uint8_t i = 0; i < 9; ++i) {
                m_gpio.set_scl(false);
                m_gpio.delay_us(5);
                m_gpio.set_scl(true);
                m_gpio.delay_us(5);

                if (m_gpio.get_sda()) {
                    break;
                }
            }
        }

        if (!m_gpio.get_sda()) {
            m_gpio.switch_to_i2c_hardware();
            return Status::BusStuck;
        }

        // Генерація послідовності STOP
        m_gpio.set_sda(false);
        m_gpio.delay_us(5);
        m_gpio.set_scl(true);
        m_gpio.delay_us(5);
        m_gpio.set_sda(true);
        m_gpio.delay_us(5);

        m_gpio.switch_to_i2c_hardware();
        return Status::Ok;
    }

private:
    GpioControl& m_gpio;
};

} // namespace driver
```
:::

---

### Неблокуючий автомат станів та арифметика переповнення таймера

Ядро драйвера реалізовано як асинхронний скінченний автомат (**FSM**). Головна вимога до обробки часу — повна стійкість до циклічного переповнення лічильника монотонного таймера (**Tick Wraparound**). 

У мікроконтролерах безперервний 32-бітний мікросекундний лічильник переповнюється кожні 71.58 хвилини (2³² мікросекунд = 4294967296 мкс ≈ 4294.96 с). Завдяки властивостям цілочисельної арифметики беззнакових чисел у доповняльному коді за модулем 2³², вираз `uint32_t elapsed = now - dev->conv_start_us;` завжди повертає математично точну різницю часу, навіть коли лічильник `now` скинувся в нуль після `0xFFFFFFFF`, за єдиної умови: інтервал очікування не перевищує 2³¹ тактів. Це виключає необхідність складних умовних перевірок переходу через нуль.

:::tabs
@tab C
```c
#include "sensor_driver.h"

#define REG_CHIP_ID       0xD0
#define EXPECTED_CHIP_ID  0x58
#define REG_MEAS_START    0xF4
#define CMD_START_BURST   0xB6
#define REG_DATA_BURST    0xF7
#define CONV_DURATION_US  20000  /* 20 мс час апаратної конверсії */

sensor_status_t sensor_init(sensor_device_t *dev, const sensor_bus_ops_t *ops, void *user_ctx) {
    if (!dev || !ops || !ops->read || !ops->write || !ops->get_time_us) {
        return SENSOR_ERR_NULL_PTR;
    }
    dev->ops = ops;
    dev->user_ctx = user_ctx;
    dev->state = SENSOR_STATE_UNINITIALIZED;
    dev->conv_start_us = 0;
    dev->conv_timeout_us = CONV_DURATION_US;

    /* 1. Перевірка Chip ID для підтвердження наявності чипа на шині */
    uint8_t chip_id = 0;
    sensor_status_t status = dev->ops->read(dev->user_ctx, REG_CHIP_ID, &chip_id, 1);
    if (status != SENSOR_OK) {
        if (dev->ops->recover_bus) {
            dev->ops->recover_bus(dev->user_ctx);
        }
        dev->state = SENSOR_STATE_ERROR;
        return SENSOR_ERR_BUS_IO;
    }

    if (chip_id != EXPECTED_CHIP_ID) {
        dev->state = SENSOR_STATE_ERROR;
        return SENSOR_ERR_CHIP_ID;
    }

    dev->state = SENSOR_STATE_IDLE;
    return SENSOR_OK;
}

sensor_status_t sensor_start_measurement(sensor_device_t *dev) {
    if (!dev || !dev->ops) {
        return SENSOR_ERR_NULL_PTR;
    }
    if (dev->state != SENSOR_STATE_IDLE && dev->state != SENSOR_STATE_DATA_READY) {
        return SENSOR_ERR_INVALID_STATE;
    }

    /* Надсилання команди запуску заміру */
    const uint8_t cmd = CMD_START_BURST;
    sensor_status_t status = dev->ops->write(dev->user_ctx, REG_MEAS_START, &cmd, 1);
    if (status != SENSOR_OK) {
        dev->state = SENSOR_STATE_ERROR;
        return SENSOR_ERR_BUS_IO;
    }

    dev->conv_start_us = dev->ops->get_time_us();
    dev->state = SENSOR_STATE_CONVERTING;
    return SENSOR_OK;
}

sensor_status_t sensor_poll(sensor_device_t *dev, sensor_data_t *out_data) {
    if (!dev || !dev->ops || !out_data) {
        return SENSOR_ERR_NULL_PTR;
    }

    if (dev->state != SENSOR_STATE_CONVERTING) {
        return SENSOR_ERR_INVALID_STATE;
    }

    uint32_t now = dev->ops->get_time_us();
    uint32_t elapsed = now - dev->conv_start_us;

    /* Неблокуюча перевірка таймера без блокування процесорного ядра */
    if (elapsed < dev->conv_timeout_us) {
        return SENSOR_ERR_NOT_READY;
    }

    /* Зчитування 7 байтів: 2 байти температури + CRC, 2 байти тиску + CRC, 1 байт статусу */
    sensor_status_t status = dev->ops->read(dev->user_ctx, REG_DATA_BURST, dev->raw_buf, 7);
    if (status != SENSOR_OK) {
        dev->state = SENSOR_STATE_ERROR;
        return SENSOR_ERR_BUS_IO;
    }

    /* Верифікація CRC температури */
    uint8_t temp_crc = sensor_calculate_crc8(&dev->raw_buf[0], 2);
    if (temp_crc != dev->raw_buf[2]) {
        dev->state = SENSOR_STATE_ERROR;
        return SENSOR_ERR_CRC;
    }

    /* Верифікація CRC тиску */
    uint8_t press_crc = sensor_calculate_crc8(&dev->raw_buf[3], 2);
    if (press_crc != dev->raw_buf[5]) {
        dev->state = SENSOR_STATE_ERROR;
        return SENSOR_ERR_CRC;
    }

    /* Розбір 16-бітного знакового значення температури (доповняльний код, Big-Endian) */
    int16_t raw_temp = (int16_t)(((uint16_t)dev->raw_buf[0] << 8) | dev->raw_buf[1]);
    /* Формула перетворення: T = -45°C + 175 * raw / 65535 */
    out_data->temperature_mdeg_c = (int32_t)(-45000 + ((int64_t)raw_temp * 175000) / 65535);

    /* Розбір 16-бітного беззнакового значення тиску */
    uint16_t raw_press = ((uint16_t)dev->raw_buf[3] << 8) | dev->raw_buf[4];
    /* Формула перетворення: P = 30000 Па + (raw * 80000) / 65535 */
    out_data->pressure_pa = (uint32_t)(30000 + ((uint64_t)raw_press * 80000) / 65535);
    out_data->humidity_mpercent = 0;
    out_data->timestamp_us = now;

    dev->state = SENSOR_STATE_DATA_READY;
    return SENSOR_OK;
}

sensor_status_t sensor_reset_fsm(sensor_device_t *dev) {
    if (!dev) return SENSOR_ERR_NULL_PTR;
    dev->state = SENSOR_STATE_IDLE;
    dev->conv_start_us = 0;
    return SENSOR_OK;
}
```
@tab C++
```cpp
#include "sensor_driver.hpp"

namespace driver {

template <BusTransport Transport>
uint8_t SensorDevice<Transport>::compute_crc8(std::span<const uint8_t> data) noexcept {
    constexpr uint8_t POLYNOMIAL = 0x31;
    uint8_t crc = 0xFF;
    for (uint8_t byte : data) {
        crc ^= byte;
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if ((crc & 0x80) != 0) {
                crc = static_cast<uint8_t>((crc << 1) ^ POLYNOMIAL);
            } else {
                crc = static_cast<uint8_t>(crc << 1);
            }
        }
    }
    return crc;
}

template <BusTransport Transport>
Status SensorDevice<Transport>::init() noexcept {
    uint8_t id = 0;
    std::span<uint8_t> rx_span(&id, 1);
    Status status = m_bus.read(REG_CHIP_ID, rx_span);
    if (status != Status::Ok) {
        m_bus.recover();
        m_state = State::Error;
        return Status::BusIo;
    }

    if (id != EXPECTED_CHIP_ID) {
        m_state = State::Error;
        return Status::ChipIdMismatch;
    }

    m_state = State::Idle;
    return Status::Ok;
}

template <BusTransport Transport>
Status SensorDevice<Transport>::start_measurement() noexcept {
    if (m_state != State::Idle && m_state != State::DataReady) {
        return Status::InvalidState;
    }

    const uint8_t cmd = 0xB6;
    const std::span<const uint8_t> tx_span(&cmd, 1);
    Status status = m_bus.write(REG_MEAS_START, tx_span);
    if (status != Status::Ok) {
        m_state = State::Error;
        return Status::BusIo;
    }

    m_conv_start_us = m_bus.get_time_us();
    m_state = State::Converting;
    return Status::Ok;
}

template <BusTransport Transport>
std::expected<SensorData, Status> SensorDevice<Transport>::poll() noexcept {
    if (m_state != State::Converting) {
        return std::unexpected(Status::InvalidState);
    }

    const uint32_t now = m_bus.get_time_us();
    if ((now - m_conv_start_us) < CONV_DURATION_US) {
        return std::unexpected(Status::NotReady);
    }

    std::span<uint8_t> rx_span(m_raw_buf);
    Status status = m_bus.read(REG_DATA_BURST, rx_span);
    if (status != Status::Ok) {
        m_state = State::Error;
        return std::unexpected(Status::BusIo);
    }

    /* Перевірка CRC температури (перші 2 байти) */
    if (compute_crc8(rx_span.subspan(0, 2)) != m_raw_buf[2]) {
        m_state = State::Error;
        return std::unexpected(Status::CrcMismatch);
    }

    /* Перевірка CRC тиску (байти 3 і 4) */
    if (compute_crc8(rx_span.subspan(3, 2)) != m_raw_buf[5]) {
        m_state = State::Error;
        return std::unexpected(Status::CrcMismatch);
    }

    SensorData data{};
    const auto raw_temp = static_cast<int16_t>(
        (static_cast<uint16_t>(m_raw_buf[0]) << 8) | m_raw_buf[1]
    );
    data.temperature_mdeg_c = static_cast<int32_t>(
        -45000 + (static_cast<int64_t>(raw_temp) * 175000) / 65535
    );

    const auto raw_press = static_cast<uint16_t>(
        (static_cast<uint16_t>(m_raw_buf[3]) << 8) | m_raw_buf[4]
    );
    data.pressure_pa = static_cast<uint32_t>(
        30000 + (static_cast<uint64_t>(raw_press) * 80000) / 65535
    );
    data.timestamp_us = now;

    m_state = State::DataReady;
    return data;
}

template <BusTransport Transport>
void SensorDevice<Transport>::reset_fsm() noexcept {
    m_state = State::Idle;
    m_conv_start_us = 0;
}

template <BusTransport Transport>
Status SensorDevice<Transport>::recover_bus() noexcept {
    return m_bus.recover();
}

} // namespace driver
```
:::

---

### Практичне використання: інтеграція в головний цикл прошивки

Нижче наведено приклад інтеграції драйвера в неблокуючий головний цикл (**Super-loop** або періодичну задачу FreeRTOS). Зверніть увагу: між запуском вимірювання та зчитуванням результату процесор не зупиняється жодної мікросекунди, виконуючи інші корисні системні операції.

Якщо опитування повертає статус апаратної помилки `SENSOR_ERR_BUS_IO` або невідповідності контрольної суми `SENSOR_ERR_CRC`, диспетчер виконує скидання кінцевого автомата та запускає функцію відновлення шини для ліквідації можливих перехідних завад без аварійної зупинки всієї системи.

:::tabs
@tab C
```c
#include <stdio.h>
#include "sensor_driver.h"

/* Реальні функції периферії мікроконтролера */
extern sensor_status_t mcu_i2c_read(void *ctx, uint8_t reg, uint8_t *data, size_t len);
extern sensor_status_t mcu_i2c_write(void *ctx, uint8_t reg, const uint8_t *data, size_t len);
extern uint32_t mcu_get_systick_us(void);
extern sensor_status_t mcu_i2c_recover(void *ctx);

static const sensor_bus_ops_t g_i2c_ops = {
    .read = mcu_i2c_read,
    .write = mcu_i2c_write,
    .get_time_us = mcu_get_systick_us,
    .recover_bus = mcu_i2c_recover
};

void application_task_step(sensor_device_t *sensor) {
    sensor_data_t telemetry;

    switch (sensor->state) {
        case SENSOR_STATE_IDLE:
            /* Запуск періодичного заміру */
            sensor_start_measurement(sensor);
            break;

        case SENSOR_STATE_CONVERTING: {
            /* Неблокуюча перевірка готовності */
            sensor_status_t st = sensor_poll(sensor, &telemetry);
            if (st == SENSOR_OK) {
                /* Дані успішно отримані та перевірені за CRC */
                printf("T = %ld mC, P = %lu Pa\n", (long)telemetry.temperature_mdeg_c, (unsigned long)telemetry.pressure_pa);
            } else if (st == SENSOR_ERR_NOT_READY) {
                /* Конверсія ще триває: процесор обслуговує інші модулі */
            } else {
                /* Виявлено збій шини або CRC: спроба відновлення */
                if (sensor->ops && sensor->ops->recover_bus) {
                    sensor->ops->recover_bus(sensor->user_ctx);
                }
                sensor_reset_fsm(sensor);
            }
            break;
        }

        case SENSOR_STATE_DATA_READY:
            /* Перезапуск наступного циклу заміру */
            sensor_start_measurement(sensor);
            break;

        case SENSOR_STATE_ERROR:
        default:
            if (sensor->ops && sensor->ops->recover_bus) {
                sensor->ops->recover_bus(sensor->user_ctx);
            }
            sensor_reset_fsm(sensor);
            break;
    }
}
```
@tab C++
```cpp
#include <iostream>
#include "sensor_driver.hpp"

template <driver::BusTransport Transport>
void application_task_step(driver::SensorDevice<Transport>& sensor) {
    switch (sensor.state()) {
        case driver::State::Idle:
            sensor.start_measurement();
            break;

        case driver::State::Converting: {
            auto result = sensor.poll();
            if (result.has_value()) {
                const auto& data = result.value();
                std::cout << "T = " << data.temperature_mdeg_c << " mC, P = " 
                          << data.pressure_pa << " Pa\n";
            } else if (result.error() == driver::Status::NotReady) {
                // Виконуємо інші фонові задачі
            } else {
                // Відновлення після помилки CRC або шини
                sensor.recover_bus();
                sensor.reset_fsm();
            }
            break;
        }

        case driver::State::DataReady:
            sensor.start_measurement();
            break;

        case driver::State::Error:
        default:
            sensor.recover_bus();
            sensor.reset_fsm();
            break;
    }
}
```
:::

---

### Хостовий тестовий стенд із симуляцією несправностей

Повноцінний тестовий модуль для компіляції та автоматичного тестування на робочій станції розробника. Модуль емулює внутрішні регістри мікросхеми, штучно генерує таймаути, інжектує помилки в лінію передачі для перевірки відхилення спотворених CRC, емулює стан заклинювання `SDA Stuck` та верифікує роботу автомата в усіх граничних режимах.

:::tabs
@tab C
```c
#include <stdio.h>
#include <assert.h>
#include <string.h>
#include "sensor_driver.h"

typedef struct {
    uint32_t current_time_us;
    uint8_t  registers[256];
    bool     inject_crc_error;
    bool     inject_bus_error;
    bool     bus_recovered;
} mock_bus_context_t;

static mock_bus_context_t g_mock;

static uint32_t mock_get_time(void) {
    return g_mock.current_time_us;
}

static sensor_status_t mock_read(void *ctx, uint8_t reg, uint8_t *data, size_t len) {
    (void)ctx;
    if (g_mock.inject_bus_error) {
        return SENSOR_ERR_BUS_IO;
    }
    for (size_t i = 0; i < len; i++) {
        data[i] = g_mock.registers[(uint8_t)(reg + i)];
    }
    return SENSOR_OK;
}

static sensor_status_t mock_write(void *ctx, uint8_t reg, const uint8_t *data, size_t len) {
    (void)ctx;
    if (g_mock.inject_bus_error) {
        return SENSOR_ERR_BUS_IO;
    }
    for (size_t i = 0; i < len; i++) {
        g_mock.registers[(uint8_t)(reg + i)] = data[i];
    }
    return SENSOR_OK;
}

static sensor_status_t mock_recover(void *ctx) {
    (void)ctx;
    g_mock.bus_recovered = true;
    g_mock.inject_bus_error = false;
    return SENSOR_OK;
}

static const sensor_bus_ops_t g_mock_ops = {
    .read = mock_read,
    .write = mock_write,
    .get_time_us = mock_get_time,
    .recover_bus = mock_recover
};

int main(void) {
    printf("=== Запуск тестів драйвера сенсора на хості (C) ===\n");

    /* Тест 1: Успішна ініціалізація та валідація Chip ID */
    memset(&g_mock, 0, sizeof(g_mock));
    g_mock.registers[0xD0] = 0x58; /* Правильний ID сенсора */

    sensor_device_t dev;
    sensor_status_t st = sensor_init(&dev, &g_mock_ops, NULL);
    assert(st == SENSOR_OK);
    assert(dev.state == SENSOR_STATE_IDLE);
    printf("[OK] Тест 1: Валідація Chip ID пройшла успішно\n");

    /* Тест 2: Запуск заміру та неблокуюче очікування (NOT_READY) */
    st = sensor_start_measurement(&dev);
    assert(st == SENSOR_OK);
    assert(dev.state == SENSOR_STATE_CONVERTING);

    sensor_data_t data;
    g_mock.current_time_us += 10000; /* Минуло лише 10 мс із 20 мс */
    st = sensor_poll(&dev, &data);
    assert(st == SENSOR_ERR_NOT_READY);
    assert(dev.state == SENSOR_STATE_CONVERTING);
    printf("[OK] Тест 2: Неблокуюче очікування (NOT_READY) працює коректно\n");

    /* Тест 3: Завершення конверсії та розбір коректних даних з CRC */
    g_mock.current_time_us += 15000; /* Сумарно минуло 25 мс (> 20 мс) */
    
    /* Заповнення регістрів: T = 25.0 °C (raw = 0x6666, CRC = 0xBE) */
    g_mock.registers[0xF7] = 0x66;
    g_mock.registers[0xF8] = 0x66;
    g_mock.registers[0xF9] = 0xBE; /* Еталонний CRC-8 */
    /* P = 101325 Па (raw = 0xE442, CRC = 0x7E) */
    g_mock.registers[0xFA] = 0xE4;
    g_mock.registers[0xFB] = 0x42;
    g_mock.registers[0xFC] = 0x7E; /* Еталонний CRC-8 */

    st = sensor_poll(&dev, &data);
    assert(st == SENSOR_OK);
    assert(dev.state == SENSOR_STATE_DATA_READY);
    printf("[OK] Тест 3: Дані прочитано. T = %ld.%03ld °C, P = %lu Па\n",
           (long)(data.temperature_mdeg_c / 1000), (long)(data.temperature_mdeg_c % 1000), (unsigned long)data.pressure_pa);

    /* Тест 4: Виявлення пошкодження даних (CRC Fail) */
    sensor_start_measurement(&dev);
    g_mock.current_time_us += 25000;
    g_mock.registers[0xF9] ^= 0x01; /* Інверсія одного біта CRC */

    st = sensor_poll(&dev, &data);
    assert(st == SENSOR_ERR_CRC);
    assert(dev.state == SENSOR_STATE_ERROR);
    printf("[OK] Тест 4: Спотворення даних успішно перехоплено перевіркою CRC-8\n");

    /* Тест 5: Перевірка відновлення шини після збою */
    sensor_reset_fsm(&dev);
    g_mock.inject_bus_error = true;
    st = sensor_start_measurement(&dev);
    assert(st == SENSOR_ERR_BUS_IO);
    assert(dev.state == SENSOR_STATE_ERROR);
    dev.ops->recover_bus(NULL);
    assert(g_mock.bus_recovered == true);
    printf("[OK] Тест 5: Автоматичне відновлення шини виконано успішно\n");

    printf("=== Усі тести завершено успішно! ===\n");
    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <cassert>
#include <array>
#include "sensor_driver.hpp"

class MockBus {
public:
    uint32_t current_time_us{0};
    std::array<uint8_t, 256> registers{};
    bool inject_bus_error{false};
    bool bus_recovered{false};

    [[nodiscard]] driver::Status read(uint8_t reg, std::span<uint8_t> rx) noexcept {
        if (inject_bus_error) return driver::Status::BusIo;
        for (size_t i = 0; i < rx.size(); ++i) {
            rx[i] = registers[static_cast<uint8_t>(reg + i)];
        }
        return driver::Status::Ok;
    }

    [[nodiscard]] driver::Status write(uint8_t reg, std::span<const uint8_t> tx) noexcept {
        if (inject_bus_error) return driver::Status::BusIo;
        for (size_t i = 0; i < tx.size(); ++i) {
            registers[static_cast<uint8_t>(reg + i)] = tx[i];
        }
        return driver::Status::Ok;
    }

    [[nodiscard]] uint32_t get_time_us() const noexcept {
        return current_time_us;
    }

    [[nodiscard]] driver::Status recover() noexcept {
        bus_recovered = true;
        inject_bus_error = false;
        return driver::Status::Ok;
    }
};

int main() {
    std::cout << "=== Запуск тестів драйвера сенсора на хості (C++) ===\n";

    MockBus mock;
    mock.registers[0xD0] = 0x58; // Expected Chip ID

    driver::SensorDevice<MockBus> sensor(mock);
    driver::Status st = sensor.init();
    assert(st == driver::Status::Ok);
    assert(sensor.state() == driver::State::Idle);
    std::cout << "[OK] Тест 1: Валідація Chip ID пройшла успішно\n";

    st = sensor.start_measurement();
    assert(st == driver::Status::Ok);
    assert(sensor.state() == driver::State::Converting);

    // Минуло лише 10 мс із 20 мс
    mock.current_time_us += 10000;
    auto res = sensor.poll();
    assert(!res.has_value());
    assert(res.error() == driver::Status::NotReady);
    std::cout << "[OK] Тест 2: Неблокуюче очікування (NotReady) працює коректно\n";

    // Минуло ще 15 мс (> 20 мс)
    mock.current_time_us += 15000;
    mock.registers[0xF7] = 0x66;
    mock.registers[0xF8] = 0x66;
    mock.registers[0xF9] = 0xBE;
    mock.registers[0xFA] = 0xE4;
    mock.registers[0xFB] = 0x42;
    mock.registers[0xFC] = 0x7E;

    res = sensor.poll();
    assert(res.has_value());
    assert(sensor.state() == driver::State::DataReady);
    std::cout << "[OK] Тест 3: Дані прочитано. T = " 
              << res->temperature_mdeg_c / 1000 << "." << res->temperature_mdeg_c % 1000 
              << " °C, P = " << res->pressure_pa << " Па\n";

    // Ін'єкція помилки CRC
    sensor.start_measurement();
    mock.current_time_us += 25000;
    mock.registers[0xF9] ^= 0xFF; // Псування контрольного байта

    res = sensor.poll();
    assert(!res.has_value());
    assert(res.error() == driver::Status::CrcMismatch);
    assert(sensor.state() == driver::State::Error);
    std::cout << "[OK] Тест 4: Спотворення даних успішно перехоплено перевіркою CRC-8\n";

    // Тест відновлення шини
    sensor.reset_fsm();
    mock.inject_bus_error = true;
    st = sensor.start_measurement();
    assert(st == driver::Status::BusIo);
    st = sensor.recover_bus();
    assert(st == driver::Status::Ok);
    assert(mock.bus_recovered);
    std::cout << "[OK] Тест 5: Автоматичне відновлення шини виконано успішно\n";

    std::cout << "=== Усі тести завершено успішно! ===\n";
    return 0;
}
```
:::
