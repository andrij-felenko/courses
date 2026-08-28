# ⚙️ Переносимий HAL інтерфейс шин I2C, SPI та GPIO на C99 та C++20

Коли вбудована прошивка починає залежати від конкретного мікроконтролера, вартість будь-якої зміни апаратної платформи стає катастрофічною. Якщо драйвер датчика температури або чипа пам'яті всередині викликає специфічні функції вендорної бібліотеки, наприклад `HAL_I2C_Master_Transmit` від одного виробника, такий драйвер неможливо скомпілювати для чипа іншого виробника без повного переписування або захаращення кодової бази директивами препроцесора `#ifdef`. Проєктування незалежного від заліза інтерфейсу вимагає побудови чіткої межі абстракції для базових периферійних шин: цифрових ліній вводу-виводу (GPIO), послідовної міжмікросхемної шини (I2C) та послідовного периферійного інтерфейсу (SPI).

У цій практичній роботі реалізовано повноцінну, функціональну підсистему апаратного абстрагування у двох парадигмах: динамічного поліморфізму мовою C99 (через таблиці покажчиків на функції та непрозорі контексти) та статичного поліморфізму нульової вартості мовою C++20 (на основі концептів, шаблонів та семантики часу компіляції). Кожна з реалізацій містить інтерфейсні контракти шин, конкретні драйвери для різних сімейств мікроконтролерів, програмний імітатор (mock) для автономного модульного тестування на хост-системі без реального заліза, а також універсальні драйвери цифрових сенсорів та чипів пам'яті, що працюють виключно через абстрактний шар.

## Архітектурний контракт шинних інтерфейсів

Шар абстракції периферії повинен вирішувати чотири ключові задачі: уніфікацію кодів помилок, абстрагування дескрипторів ліній та шин, ізоляцію синхронізації й тайм-аутів та підтримку складених транзакцій (таких як повторний старт у протоколі I2C або утримання вибору чипа Chip Select у SPI).

Усі операції повертають строго типізований статус виконання. Використання цілочисельних кодів повернення без єдиного переліку призводить до ситуацій, коли код `-1` в одному драйвері означає тайм-аут, а в іншому — помилку підтвердження адреси (NACK). Інтерфейс стандартизує перелік станів: успіх, помилка шини, відсутність відповіді веденого пристрою, переповнення буфера, некоректні аргументи та перевищення ліміту часу очікування.

Для ліній GPIO контракт передбачає базові операції встановлення високого та низького логічного рівня, перемикання стану (toggle) та зчитування поточного рівня. Для шини I2C критично важливою є операція комбінованого запису з наступним зчитуванням (`write_read`) без виставлення сигналу Stop на шині між фазами, що є обов'язковою вимогою для опитування регістрів практично всіх сучасних цифрових сенсорів. Для шини SPI контракт охоплює повнодуплексний одночасний обмін (`transfer`), а також роздільні операції блокового передавання та приймання з апаратним або програмним керуванням лінією Chip Select.

## Повний заголовок інтерфейсів на C99 та C++20

Нижче наведено заголовкові файли, що визначають інтерфейсні контракти. У C99 використовується структура операцій `ops` та непрозорий контекст `ctx`. У C++20 застосовуються концептуальні обмеження `requires`, `std::span` для безпечної передачі масивів даних без динамічного виділення пам'яті та строгі переліки типів `enum class`.

:::tabs
```c
#ifndef PORTABLE_HAL_C99_H
#define PORTABLE_HAL_C99_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Уніфіковані коди помилок периферійного шару */
typedef enum {
    HAL_STATUS_OK              =  0,
    HAL_STATUS_ERROR           = -1,
    HAL_STATUS_TIMEOUT         = -2,
    HAL_STATUS_BUSY            = -3,
    HAL_STATUS_NACK            = -4,
    HAL_STATUS_INVALID_ARG     = -5,
    HAL_STATUS_NOT_SUPPORTED   = -6
} hal_status_t;

/* Логічний рівень цифрової лінії */
typedef enum {
    HAL_GPIO_LEVEL_LOW  = 0,
    HAL_GPIO_LEVEL_HIGH = 1
} hal_gpio_level_t;

/* Режим роботи цифрової лінії */
typedef enum {
    HAL_GPIO_MODE_INPUT,
    HAL_GPIO_MODE_OUTPUT_PP,
    HAL_GPIO_MODE_OUTPUT_OD
} hal_gpio_mode_t;

/* Підтяжка цифрової лінії */
typedef enum {
    HAL_GPIO_PULL_NONE,
    HAL_GPIO_PULL_UP,
    HAL_GPIO_PULL_DOWN
} hal_gpio_pull_t;

/* Конфігурація лінії GPIO */
typedef struct {
    hal_gpio_mode_t mode;
    hal_gpio_pull_t pull;
} hal_gpio_config_t;

/* Таблиця операцій GPIO */
struct hal_gpio_pin;
typedef struct {
    hal_status_t (*init)(const struct hal_gpio_pin *pin, const hal_gpio_config_t *cfg);
    hal_status_t (*set_level)(const struct hal_gpio_pin *pin, hal_gpio_level_t level);
    hal_status_t (*get_level)(const struct hal_gpio_pin *pin, hal_gpio_level_t *out_level);
    hal_status_t (*toggle)(const struct hal_gpio_pin *pin);
} hal_gpio_ops_t;

/* Дескриптор лінії GPIO */
typedef struct hal_gpio_pin {
    const hal_gpio_ops_t *ops;
    void *ctx;
} hal_gpio_pin_t;

/* Зручні функції-обгортки для клієнтського коду */
static inline hal_status_t hal_gpio_init(const hal_gpio_pin_t *pin, const hal_gpio_config_t *cfg) {
    if (!pin || !pin->ops || !pin->ops->init) return HAL_STATUS_INVALID_ARG;
    return pin->ops->init(pin, cfg);
}

static inline hal_status_t hal_gpio_set(const hal_gpio_pin_t *pin, hal_gpio_level_t level) {
    if (!pin || !pin->ops || !pin->ops->set_level) return HAL_STATUS_INVALID_ARG;
    return pin->ops->set_level(pin, level);
}

static inline hal_status_t hal_gpio_get(const hal_gpio_pin_t *pin, hal_gpio_level_t *out_level) {
    if (!pin || !pin->ops || !pin->ops->get_level || !out_level) return HAL_STATUS_INVALID_ARG;
    return pin->ops->get_level(pin, out_level);
}

static inline hal_status_t hal_gpio_toggle(const hal_gpio_pin_t *pin) {
    if (!pin || !pin->ops || !pin->ops->toggle) return HAL_STATUS_INVALID_ARG;
    return pin->ops->toggle(pin);
}

/* Інтерфейс магістралі I2C */
struct hal_i2c_bus;
typedef struct {
    hal_status_t (*write)(const struct hal_i2c_bus *bus, uint8_t addr_7bit,
                          const uint8_t *tx_data, size_t len, uint32_t timeout_ms);
    hal_status_t (*read)(const struct hal_i2c_bus *bus, uint8_t addr_7bit,
                         uint8_t *rx_data, size_t len, uint32_t timeout_ms);
    hal_status_t (*write_read)(const struct hal_i2c_bus *bus, uint8_t addr_7bit,
                              const uint8_t *tx_data, size_t tx_len,
                              uint8_t *rx_data, size_t rx_len, uint32_t timeout_ms);
} hal_i2c_ops_t;

typedef struct hal_i2c_bus {
    const hal_i2c_ops_t *ops;
    void *ctx;
} hal_i2c_bus_t;

static inline hal_status_t hal_i2c_write(const hal_i2c_bus_t *bus, uint8_t addr,
                                         const uint8_t *data, size_t len, uint32_t timeout_ms) {
    if (!bus || !bus->ops || !bus->ops->write) return HAL_STATUS_INVALID_ARG;
    return bus->ops->write(bus, addr, data, len, timeout_ms);
}

static inline hal_status_t hal_i2c_read(const hal_i2c_bus_t *bus, uint8_t addr,
                                        uint8_t *data, size_t len, uint32_t timeout_ms) {
    if (!bus || !bus->ops || !bus->ops->read) return HAL_STATUS_INVALID_ARG;
    return bus->ops->read(bus, addr, data, len, timeout_ms);
}

static inline hal_status_t hal_i2c_write_read(const hal_i2c_bus_t *bus, uint8_t addr,
                                              const uint8_t *tx, size_t tx_len,
                                              uint8_t *rx, size_t rx_len, uint32_t timeout_ms) {
    if (!bus || !bus->ops || !bus->ops->write_read) return HAL_STATUS_INVALID_ARG;
    return bus->ops->write_read(bus, addr, tx, tx_len, rx, rx_len, timeout_ms);
}

/* Інтерфейс магістралі SPI */
struct hal_spi_bus;
typedef struct {
    hal_status_t (*transfer)(const struct hal_spi_bus *bus,
                            const uint8_t *tx_buf, uint8_t *rx_buf,
                            size_t len, uint32_t timeout_ms);
    hal_status_t (*write)(const struct hal_spi_bus *bus,
                          const uint8_t *tx_buf, size_t len, uint32_t timeout_ms);
    hal_status_t (*read)(const struct hal_spi_bus *bus,
                         uint8_t *rx_buf, size_t len, uint32_t timeout_ms);
} hal_spi_ops_t;

typedef struct hal_spi_bus {
    const hal_spi_ops_t *ops;
    void *ctx;
} hal_spi_bus_t;

static inline hal_status_t hal_spi_transfer(const hal_spi_bus_t *bus,
                                            const uint8_t *tx, uint8_t *rx,
                                            size_t len, uint32_t timeout_ms) {
    if (!bus || !bus->ops || !bus->ops->transfer) return HAL_STATUS_INVALID_ARG;
    return bus->ops->transfer(bus, tx, rx, len, timeout_ms);
}

static inline hal_status_t hal_spi_write(const hal_spi_bus_t *bus,
                                         const uint8_t *tx, size_t len, uint32_t timeout_ms) {
    if (!bus || !bus->ops || !bus->ops->write) return HAL_STATUS_INVALID_ARG;
    return bus->ops->write(bus, tx, len, timeout_ms);
}

static inline hal_status_t hal_spi_read(const hal_spi_bus_t *bus,
                                        uint8_t *rx, size_t len, uint32_t timeout_ms) {
    if (!bus || !bus->ops || !bus->ops->read) return HAL_STATUS_INVALID_ARG;
    return bus->ops->read(bus, rx, len, timeout_ms);
}

#endif /* PORTABLE_HAL_C99_H */
```
```cpp
#ifndef PORTABLE_HAL_CXX20_H
#define PORTABLE_HAL_CXX20_H

#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>
#include <system_error>

namespace hal {

/* Перелік уніфікованих статусів виконання операцій */
enum class Status : int8_t {
    Ok             =  0,
    Error          = -1,
    Timeout        = -2,
    Busy           = -3,
    Nack           = -4,
    InvalidArg     = -5,
    NotSupported   = -6
};

/* Допоміжний метод перевірки успіху */
constexpr bool is_ok(Status s) noexcept { return s == Status::Ok; }

enum class PinLevel : uint8_t {
    Low  = 0,
    High = 1
};

enum class PinMode : uint8_t {
    Input,
    OutputPushPull,
    OutputOpenDrain
};

enum class PinPull : uint8_t {
    None,
    Up,
    Down
};

struct PinConfig {
    PinMode mode{PinMode::OutputPushPull};
    PinPull pull{PinPull::None};
};

/* C++20 Концепт цифрової лінії вводу-виводу (GPIO) */
template <typename T>
concept GpioPin = requires(T pin, PinLevel lvl, const PinConfig& cfg) {
    { pin.init(cfg) } -> std::same_as<Status>;
    { pin.set_level(lvl) } -> std::same_as<Status>;
    { pin.get_level() } -> std::same_as<PinLevel>;
    { pin.toggle() } -> std::same_as<Status>;
};

/* C++20 Концепт шини I2C Master */
template <typename T>
concept I2cMaster = requires(T bus, uint8_t addr, std::span<const uint8_t> tx,
                             std::span<uint8_t> rx, uint32_t timeout_ms) {
    { bus.write(addr, tx, timeout_ms) } -> std::same_as<Status>;
    { bus.read(addr, rx, timeout_ms) } -> std::same_as<Status>;
    { bus.write_read(addr, tx, rx, timeout_ms) } -> std::same_as<Status>;
};

/* C++20 Концепт шини SPI Master */
template <typename T>
concept SpiMaster = requires(T bus, std::span<const uint8_t> tx,
                             std::span<uint8_t> rx, uint32_t timeout_ms) {
    { bus.transfer(tx, rx, timeout_ms) } -> std::same_as<Status>;
    { bus.write(tx, timeout_ms) } -> std::same_as<Status>;
    { bus.read(rx, timeout_ms) } -> std::same_as<Status>;
};

} // namespace hal

#endif /* PORTABLE_HAL_CXX20_H */
```
:::

## Реалізація бекендів: Mock, STM32 та RP2040

Розглянемо практичну реалізацію драйверів трьох категорій:
1. **Mock-бекенд**: програмна симуляція апаратних ліній і шин I2C/SPI у пам'яті комп'ютера. Вона записує зміну станів і відповідає даними з внутрішнього масиву байтів, імітуючи карту регістрів пристрою.
2. **STM32-бекенд**: пряме мапування на регістри порту вводу-виводу (BSRR, ODR, IDR, MODER, PUPDR) для мікроконтролерів сімейства Cortex-M.
3. **RP2040-бекенд**: мапування на апаратний блок швидкісного однотактного вводу-виводу (SIO) Raspberry Pi RP2040.

:::tabs
```c
#include "portable_hal_c99.h"
#include <string.h>

/* ========================================================================= */
/* 1. MOCK БЕКЕНД: Емуляція шин у пам'яті для модульного тестування           */
/* ========================================================================= */

#define MOCK_I2C_MEM_SIZE 256
#define MOCK_SPI_MEM_SIZE 1024

typedef struct {
    hal_gpio_level_t current_level;
    uint32_t toggle_count;
} mock_gpio_ctx_t;

static hal_status_t mock_gpio_init(const hal_gpio_pin_t *pin, const hal_gpio_config_t *cfg) {
    (void)cfg;
    mock_gpio_ctx_t *ctx = (mock_gpio_ctx_t *)pin->ctx;
    ctx->current_level = HAL_GPIO_LEVEL_LOW;
    ctx->toggle_count = 0;
    return HAL_STATUS_OK;
}

static hal_status_t mock_gpio_set(const hal_gpio_pin_t *pin, hal_gpio_level_t level) {
    mock_gpio_ctx_t *ctx = (mock_gpio_ctx_t *)pin->ctx;
    ctx->current_level = level;
    return HAL_STATUS_OK;
}

static hal_status_t mock_gpio_get(const hal_gpio_pin_t *pin, hal_gpio_level_t *out_level) {
    mock_gpio_ctx_t *ctx = (mock_gpio_ctx_t *)pin->ctx;
    *out_level = ctx->current_level;
    return HAL_STATUS_OK;
}

static hal_status_t mock_gpio_toggle(const hal_gpio_pin_t *pin) {
    mock_gpio_ctx_t *ctx = (mock_gpio_ctx_t *)pin->ctx;
    ctx->current_level = (ctx->current_level == HAL_GPIO_LEVEL_LOW) ? HAL_GPIO_LEVEL_HIGH : HAL_GPIO_LEVEL_LOW;
    ctx->toggle_count++;
    return HAL_STATUS_OK;
}

static const hal_gpio_ops_t mock_gpio_ops = {
    .init = mock_gpio_init,
    .set_level = mock_gpio_set,
    .get_level = mock_gpio_get,
    .toggle = mock_gpio_toggle
};

typedef struct {
    uint8_t registers[MOCK_I2C_MEM_SIZE];
    uint8_t expected_addr;
    bool force_nack;
} mock_i2c_ctx_t;

static hal_status_t mock_i2c_write(const hal_i2c_bus_t *bus, uint8_t addr,
                                   const uint8_t *tx, size_t len, uint32_t timeout_ms) {
    (void)timeout_ms;
    mock_i2c_ctx_t *ctx = (mock_i2c_ctx_t *)bus->ctx;
    if (ctx->force_nack || addr != ctx->expected_addr) return HAL_STATUS_NACK;
    if (len < 1) return HAL_STATUS_INVALID_ARG;

    uint8_t reg = tx[0];
    for (size_t i = 1; i < len; ++i) {
        if ((size_t)(reg + i - 1) < MOCK_I2C_MEM_SIZE) {
            ctx->registers[reg + i - 1] = tx[i];
        }
    }
    return HAL_STATUS_OK;
}

static hal_status_t mock_i2c_read(const hal_i2c_bus_t *bus, uint8_t addr,
                                  uint8_t *rx, size_t len, uint32_t timeout_ms) {
    (void)timeout_ms;
    mock_i2c_ctx_t *ctx = (mock_i2c_ctx_t *)bus->ctx;
    if (ctx->force_nack || addr != ctx->expected_addr) return HAL_STATUS_NACK;

    for (size_t i = 0; i < len; ++i) {
        rx[i] = (i < MOCK_I2C_MEM_SIZE) ? ctx->registers[i] : 0xFF;
    }
    return HAL_STATUS_OK;
}

static hal_status_t mock_i2c_write_read(const hal_i2c_bus_t *bus, uint8_t addr,
                                        const uint8_t *tx, size_t tx_len,
                                        uint8_t *rx, size_t rx_len, uint32_t timeout_ms) {
    (void)timeout_ms;
    mock_i2c_ctx_t *ctx = (mock_i2c_ctx_t *)bus->ctx;
    if (ctx->force_nack || addr != ctx->expected_addr) return HAL_STATUS_NACK;
    if (tx_len < 1) return HAL_STATUS_INVALID_ARG;

    uint8_t start_reg = tx[0];
    for (size_t i = 0; i < rx_len; ++i) {
        size_t idx = start_reg + i;
        rx[i] = (idx < MOCK_I2C_MEM_SIZE) ? ctx->registers[idx] : 0x00;
    }
    return HAL_STATUS_OK;
}

static const hal_i2c_ops_t mock_i2c_ops = {
    .write = mock_i2c_write,
    .read = mock_i2c_read,
    .write_read = mock_i2c_write_read
};

typedef struct {
    uint8_t flash_memory[MOCK_SPI_MEM_SIZE];
} mock_spi_ctx_t;

static hal_status_t mock_spi_transfer(const hal_spi_bus_t *bus,
                                      const uint8_t *tx, uint8_t *rx,
                                      size_t len, uint32_t timeout_ms) {
    (void)bus; (void)timeout_ms;
    for (size_t i = 0; i < len; ++i) {
        uint8_t byte_in = tx ? tx[i] : 0xFF;
        if (rx) rx[i] = byte_in;
    }
    return HAL_STATUS_OK;
}

static hal_status_t mock_spi_write(const hal_spi_bus_t *bus,
                                   const uint8_t *tx, size_t len, uint32_t timeout_ms) {
    return mock_spi_transfer(bus, tx, NULL, len, timeout_ms);
}

static hal_status_t mock_spi_read(const hal_spi_bus_t *bus,
                                  uint8_t *rx, size_t len, uint32_t timeout_ms) {
    return mock_spi_transfer(bus, NULL, rx, len, timeout_ms);
}

static const hal_spi_ops_t mock_spi_ops = {
    .transfer = mock_spi_transfer,
    .write = mock_spi_write,
    .read = mock_spi_read
};

/* ========================================================================= */
/* 2. STM32 БЕКЕНД: Пряма робота з регістрами Cortex-M (BSRR, ODR, IDR, I2C) */
/* ========================================================================= */

typedef struct {
    volatile uint32_t MODER;
    volatile uint32_t OTYPER;
    volatile uint32_t OSPEEDR;
    volatile uint32_t PUPDR;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t LCKR;
    volatile uint32_t AFR[2];
} stm32_gpio_reg_t;

typedef struct {
    stm32_gpio_reg_t *port;
    uint8_t pin_num;
} stm32_gpio_ctx_t;

static hal_status_t stm32_gpio_init(const hal_gpio_pin_t *pin, const hal_gpio_config_t *cfg) {
    stm32_gpio_ctx_t *ctx = (stm32_gpio_ctx_t *)pin->ctx;
    if (!ctx || !ctx->port || ctx->pin_num > 15) return HAL_STATUS_INVALID_ARG;

    uint32_t pin_idx = ctx->pin_num;
    stm32_gpio_reg_t *port = ctx->port;

    port->MODER &= ~(3U << (pin_idx * 2));
    if (cfg->mode == HAL_GPIO_MODE_OUTPUT_PP || cfg->mode == HAL_GPIO_MODE_OUTPUT_OD) {
        port->MODER |= (1U << (pin_idx * 2));
    }

    if (cfg->mode == HAL_GPIO_MODE_OUTPUT_OD) {
        port->OTYPER |= (1U << pin_idx);
    } else {
        port->OTYPER &= ~(1U << pin_idx);
    }

    port->PUPDR &= ~(3U << (pin_idx * 2));
    if (cfg->pull == HAL_GPIO_PULL_UP) {
        port->PUPDR |= (1U << (pin_idx * 2));
    } else if (cfg->pull == HAL_GPIO_PULL_DOWN) {
        port->PUPDR |= (2U << (pin_idx * 2));
    }

    return HAL_STATUS_OK;
}

static hal_status_t stm32_gpio_set(const hal_gpio_pin_t *pin, hal_gpio_level_t level) {
    stm32_gpio_ctx_t *ctx = (stm32_gpio_ctx_t *)pin->ctx;
    if (level == HAL_GPIO_LEVEL_HIGH) {
        ctx->port->BSRR = (1U << ctx->pin_num);
    } else {
        ctx->port->BSRR = (1U << (ctx->pin_num + 16));
    }
    return HAL_STATUS_OK;
}

static hal_status_t stm32_gpio_get(const hal_gpio_pin_t *pin, hal_gpio_level_t *out_level) {
    stm32_gpio_ctx_t *ctx = (stm32_gpio_ctx_t *)pin->ctx;
    *out_level = (ctx->port->IDR & (1U << ctx->pin_num)) ? HAL_GPIO_LEVEL_HIGH : HAL_GPIO_LEVEL_LOW;
    return HAL_STATUS_OK;
}

static hal_status_t stm32_gpio_toggle(const hal_gpio_pin_t *pin) {
    stm32_gpio_ctx_t *ctx = (stm32_gpio_ctx_t *)pin->ctx;
    ctx->port->ODR ^= (1U << ctx->pin_num);
    return HAL_STATUS_OK;
}

static const hal_gpio_ops_t stm32_gpio_ops = {
    .init = stm32_gpio_init,
    .set_level = stm32_gpio_set,
    .get_level = stm32_gpio_get,
    .toggle = stm32_gpio_toggle
};

/* ========================================================================= */
/* 3. RP2040 БЕКЕНД: Робота з атомарними апаратними регістрами SIO / GPIO    */
/* ========================================================================= */

typedef struct {
    volatile uint32_t GPIO_IN;
    volatile uint32_t GPIO_IN_HI;
    volatile uint32_t GPIO_OUT;
    volatile uint32_t GPIO_OUT_SET;
    volatile uint32_t GPIO_OUT_CLR;
    volatile uint32_t GPIO_OUT_XOR;
    volatile uint32_t GPIO_OE;
    volatile uint32_t GPIO_OE_SET;
    volatile uint32_t GPIO_OE_CLR;
    volatile uint32_t GPIO_OE_XOR;
} rp2040_sio_reg_t;

typedef struct {
    rp2040_sio_reg_t *sio;
    uint8_t pin_num;
} rp2040_gpio_ctx_t;

static hal_status_t rp2040_gpio_init(const hal_gpio_pin_t *pin, const hal_gpio_config_t *cfg) {
    rp2040_gpio_ctx_t *ctx = (rp2040_gpio_ctx_t *)pin->ctx;
    if (!ctx || !ctx->sio || ctx->pin_num > 29) return HAL_STATUS_INVALID_ARG;

    uint32_t mask = (1U << ctx->pin_num);
    if (cfg->mode == HAL_GPIO_MODE_OUTPUT_PP || cfg->mode == HAL_GPIO_MODE_OUTPUT_OD) {
        ctx->sio->GPIO_OE_SET = mask;
    } else {
        ctx->sio->GPIO_OE_CLR = mask;
    }
    return HAL_STATUS_OK;
}

static hal_status_t rp2040_gpio_set(const hal_gpio_pin_t *pin, hal_gpio_level_t level) {
    rp2040_gpio_ctx_t *ctx = (rp2040_gpio_ctx_t *)pin->ctx;
    uint32_t mask = (1U << ctx->pin_num);
    if (level == HAL_GPIO_LEVEL_HIGH) {
        ctx->sio->GPIO_OUT_SET = mask;
    } else {
        ctx->sio->GPIO_OUT_CLR = mask;
    }
    return HAL_STATUS_OK;
}

static hal_status_t rp2040_gpio_get(const hal_gpio_pin_t *pin, hal_gpio_level_t *out_level) {
    rp2040_gpio_ctx_t *ctx = (rp2040_gpio_ctx_t *)pin->ctx;
    *out_level = (ctx->sio->GPIO_IN & (1U << ctx->pin_num)) ? HAL_GPIO_LEVEL_HIGH : HAL_GPIO_LEVEL_LOW;
    return HAL_STATUS_OK;
}

static hal_status_t rp2040_gpio_toggle(const hal_gpio_pin_t *pin) {
    rp2040_gpio_ctx_t *ctx = (rp2040_gpio_ctx_t *)pin->ctx;
    ctx->sio->GPIO_OUT_XOR = (1U << ctx->pin_num);
    return HAL_STATUS_OK;
}

static const hal_gpio_ops_t rp2040_gpio_ops = {
    .init = rp2040_gpio_init,
    .set_level = rp2040_gpio_set,
    .get_level = rp2040_gpio_get,
    .toggle = rp2040_gpio_toggle
};
```
```cpp
#include "portable_hal_cxx20.h"
#include <array>
#include <algorithm>

namespace hal::mock {

class MockGpioPin {
public:
    Status init(const PinConfig& cfg) noexcept {
        mode_ = cfg.mode;
        level_ = PinLevel::Low;
        toggle_count_ = 0;
        return Status::Ok;
    }

    Status set_level(PinLevel lvl) noexcept {
        level_ = lvl;
        return Status::Ok;
    }

    [[nodiscard]] PinLevel get_level() const noexcept {
        return level_;
    }

    Status toggle() noexcept {
        level_ = (level_ == PinLevel::Low) ? PinLevel::High : PinLevel::Low;
        ++toggle_count_;
        return Status::Ok;
    }

    [[nodiscard]] uint32_t toggle_count() const noexcept { return toggle_count_; }

private:
    PinMode mode_{PinMode::OutputPushPull};
    PinLevel level_{PinLevel::Low};
    uint32_t toggle_count_{0};
};
static_assert(GpioPin<MockGpioPin>, "MockGpioPin must satisfy GpioPin concept");

template <size_t MemSize = 256>
class MockI2cBus {
public:
    explicit MockI2cBus(uint8_t target_addr) noexcept : expected_addr_(target_addr) {
        registers_.fill(0x00);
    }

    Status write(uint8_t addr, std::span<const uint8_t> tx, uint32_t) noexcept {
        if (force_nack_ || addr != expected_addr_) return Status::Nack;
        if (tx.empty()) return Status::InvalidArg;

        uint8_t reg = tx[0];
        for (size_t i = 1; i < tx.size(); ++i) {
            if (reg + i - 1 < MemSize) {
                registers_[reg + i - 1] = tx[i];
            }
        }
        return Status::Ok;
    }

    Status read(uint8_t addr, std::span<uint8_t> rx, uint32_t) noexcept {
        if (force_nack_ || addr != expected_addr_) return Status::Nack;

        for (size_t i = 0; i < rx.size(); ++i) {
            rx[i] = (i < MemSize) ? registers_[i] : 0xFF;
        }
        return Status::Ok;
    }

    Status write_read(uint8_t addr, std::span<const uint8_t> tx,
                       std::span<uint8_t> rx, uint32_t) noexcept {
        if (force_nack_ || addr != expected_addr_) return Status::Nack;
        if (tx.empty()) return Status::InvalidArg;

        uint8_t start_reg = tx[0];
        for (size_t i = 0; i < rx.size(); ++i) {
            size_t idx = start_reg + i;
            rx[i] = (idx < MemSize) ? registers_[idx] : 0x00;
        }
        return Status::Ok;
    }

    void set_reg(uint8_t reg, uint8_t val) noexcept { registers_[reg] = val; }
    [[nodiscard]] uint8_t get_reg(uint8_t reg) const noexcept { return registers_[reg]; }
    void set_force_nack(bool nack) noexcept { force_nack_ = nack; }

private:
    std::array<uint8_t, MemSize> registers_{};
    uint8_t expected_addr_{0x00};
    bool force_nack_{false};
};
static_assert(I2cMaster<MockI2cBus<256>>, "MockI2cBus must satisfy I2cMaster concept");

template <size_t MemSize = 1024>
class MockSpiBus {
public:
    Status transfer(std::span<const uint8_t> tx, std::span<uint8_t> rx, uint32_t) noexcept {
        size_t len = std::max(tx.size(), rx.size());
        for (size_t i = 0; i < len; ++i) {
            uint8_t b = (i < tx.size()) ? tx[i] : 0xFF;
            if (i < rx.size()) rx[i] = b;
        }
        return Status::Ok;
    }

    Status write(std::span<const uint8_t> tx, uint32_t timeout) noexcept {
        return transfer(tx, {}, timeout);
    }

    Status read(std::span<uint8_t> rx, uint32_t timeout) noexcept {
        return transfer({}, rx, timeout);
    }
};
static_assert(SpiMaster<MockSpiBus<1024>>, "MockSpiBus must satisfy SpiMaster concept");

} // namespace hal::mock

namespace hal::stm32 {

struct GpioRegisters {
    volatile uint32_t MODER;
    volatile uint32_t OTYPER;
    volatile uint32_t OSPEEDR;
    volatile uint32_t PUPDR;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t LCKR;
    volatile uint32_t AFR[2];
};

template <uintptr_t PortBase, uint8_t PinIndex>
requires (PinIndex <= 15)
class StaticGpioPin {
public:
    static inline GpioRegisters* const Port = reinterpret_cast<GpioRegisters*>(PortBase);

    static Status init(const PinConfig& cfg) noexcept {
        Port->MODER &= ~(3U << (PinIndex * 2));
        if (cfg.mode == PinMode::OutputPushPull || cfg.mode == PinMode::OutputOpenDrain) {
            Port->MODER |= (1U << (PinIndex * 2));
        }

        if (cfg.mode == PinMode::OutputOpenDrain) {
            Port->OTYPER |= (1U << PinIndex);
        } else {
            Port->OTYPER &= ~(1U << PinIndex);
        }

        Port->PUPDR &= ~(3U << (PinIndex * 2));
        if (cfg.pull == PinPull::Up) {
            Port->PUPDR |= (1U << (PinIndex * 2));
        } else if (cfg.pull == PinPull::Down) {
            Port->PUPDR |= (2U << (PinIndex * 2));
        }
        return Status::Ok;
    }

    static Status set_level(PinLevel lvl) noexcept {
        if (lvl == PinLevel::High) {
            Port->BSRR = (1U << PinIndex);
        } else {
            Port->BSRR = (1U << (PinIndex + 16));
        }
        return Status::Ok;
    }

    [[nodiscard]] static PinLevel get_level() noexcept {
        return (Port->IDR & (1U << PinIndex)) ? PinLevel::High : PinLevel::Low;
    }

    static Status toggle() noexcept {
        Port->ODR ^= (1U << PinIndex);
        return Status::Ok;
    }
};

} // namespace hal::stm32
```
:::

## Універсальний драйвер цифрового датчика (BME280) над HAL

Щоб продемонструвати повну незалежність логіки роботи з пристроєм від апаратного забезпечення, розробимо драйвер цифрового датчика температури та тиску. Драйвер містить логіку ініціалізації, зчитування ідентифікатора чипа (`WHO_AM_I` / `CHIP_ID`), калібрувальних коефіцієнтів та сирих даних вимірювання.

:::tabs
```c
/* ========================================================================= */
/* Драйвер датчика BME280 на C99, що працює суто через hal_i2c_bus_t         */
/* ========================================================================= */

#define BME280_I2C_ADDR_PRIM   0x76
#define BME280_I2C_ADDR_SEC    0x77
#define BME280_REG_CHIP_ID     0xD0
#define BME280_REG_RESET       0xE0
#define BME280_REG_CTRL_HUM    0xF2
#define BME280_REG_STATUS      0xF3
#define BME280_REG_CTRL_MEAS   0xF4
#define BME280_REG_CONFIG      0xF5
#define BME280_REG_PRESS_MSB   0xF7
#define BME280_REG_TEMP_MSB    0xFA
#define BME280_REG_CALIB00     0x88

#define BME280_CHIP_ID_VAL     0x60

typedef struct {
    uint16_t dig_T1;
    int16_t  dig_T2;
    int16_t  dig_T3;
} bme280_calib_t;

typedef struct {
    const hal_i2c_bus_t *bus;
    uint8_t i2c_addr;
    bme280_calib_t calib;
    int32_t t_fine;
} bme280_driver_t;

hal_status_t bme280_init(bme280_driver_t *dev, const hal_i2c_bus_t *bus, uint8_t addr) {
    if (!dev || !bus) return HAL_STATUS_INVALID_ARG;
    dev->bus = bus;
    dev->i2c_addr = addr;
    dev->t_fine = 0;

    /* 1. Перевірка Chip ID */
    uint8_t reg = BME280_REG_CHIP_ID;
    uint8_t chip_id = 0;
    hal_status_t status = hal_i2c_write_read(dev->bus, dev->i2c_addr,
                                             &reg, 1, &chip_id, 1, 100);
    if (status != HAL_STATUS_OK) return status;
    if (chip_id != BME280_CHIP_ID_VAL) return HAL_STATUS_ERROR;

    /* 2. Зчитування калібрувальних коефіцієнтів температури */
    uint8_t calib_reg = BME280_REG_CALIB00;
    uint8_t calib_buf[6];
    status = hal_i2c_write_read(dev->bus, dev->i2c_addr,
                                &calib_reg, 1, calib_buf, 6, 100);
    if (status != HAL_STATUS_OK) return status;

    dev->calib.dig_T1 = (uint16_t)(calib_buf[0] | (calib_buf[1] << 8));
    dev->calib.dig_T2 = (int16_t)(calib_buf[2] | (calib_buf[3] << 8));
    dev->calib.dig_T3 = (int16_t)(calib_buf[4] | (calib_buf[5] << 8));

    /* 3. Конфігурація: режим Normal, Oversampling x1 */
    uint8_t cfg_data[2];
    cfg_data[0] = BME280_REG_CTRL_MEAS;
    cfg_data[1] = (1U << 5) | (1U << 2) | (3U); /* osrs_t x1, osrs_p x1, mode Normal */
    return hal_i2c_write(dev->bus, dev->i2c_addr, cfg_data, 2, 100);
}

hal_status_t bme280_read_temperature(bme280_driver_t *dev, int32_t *out_temp_c_x100) {
    if (!dev || !dev->bus || !out_temp_c_x100) return HAL_STATUS_INVALID_ARG;

    uint8_t reg = BME280_REG_TEMP_MSB;
    uint8_t raw[3];
    hal_status_t status = hal_i2c_write_read(dev->bus, dev->i2c_addr, &reg, 1, raw, 3, 100);
    if (status != HAL_STATUS_OK) return status;

    int32_t adc_T = (int32_t)(((uint32_t)raw[0] << 12) | ((uint32_t)raw[1] << 4) | ((uint32_t)raw[2] >> 4));

    /* Формула компенсації за даташитом Bosch BME280 */
    int32_t var1 = ((((adc_T >> 3) - ((int32_t)dev->calib.dig_T1 << 1))) * ((int32_t)dev->calib.dig_T2)) >> 11;
    int32_t var2 = (((((adc_T >> 4) - ((int32_t)dev->calib.dig_T1)) *
                      ((adc_T >> 4) - ((int32_t)dev->calib.dig_T1))) >> 12) *
                    ((int32_t)dev->calib.dig_T3)) >> 14;

    dev->t_fine = var1 + var2;
    *out_temp_c_x100 = (dev->t_fine * 5 + 128) >> 8;
    return HAL_STATUS_OK;
}
```
```cpp
/* ========================================================================= */
/* Шаблонний драйвер датчика BME280 на C++20 над концептом I2cMaster        */
/* ========================================================================= */

namespace sensors {

template <hal::I2cMaster Bus>
class Bme280 {
public:
    static constexpr uint8_t DefaultAddress = 0x76;
    static constexpr uint8_t ChipIdRegister = 0xD0;
    static constexpr uint8_t ExpectedChipId = 0x60;
    static constexpr uint8_t CalibRegister  = 0x88;
    static constexpr uint8_t CtrlMeasReg    = 0xF4;
    static constexpr uint8_t TempMsbReg     = 0xFA;

    struct CalibrationData {
        uint16_t dig_T1{0};
        int16_t  dig_T2{0};
        int16_t  dig_T3{0};
    };

    explicit Bme280(Bus& bus, uint8_t address = DefaultAddress) noexcept
        : bus_(bus), address_(address) {}

    hal::Status init() noexcept {
        /* 1. Перевірка ідентифікатора чипа */
        const std::array<uint8_t, 1> reg_tx{ChipIdRegister};
        std::array<uint8_t, 1> id_rx{0};

        auto status = bus_.write_read(address_, reg_tx, id_rx, 100);
        if (!hal::is_ok(status)) return status;
        if (id_rx[0] != ExpectedChipId) return hal::Status::Error;

        /* 2. Зчитування калібрувальної таблиці */
        const std::array<uint8_t, 1> calib_tx{CalibRegister};
        std::array<uint8_t, 6> calib_rx{};
        status = bus_.write_read(address_, calib_tx, calib_rx, 100);
        if (!hal::is_ok(status)) return status;

        calib_.dig_T1 = static_cast<uint16_t>(calib_rx[0] | (calib_rx[1] << 8));
        calib_.dig_T2 = static_cast<int16_t>(calib_rx[2] | (calib_rx[3] << 8));
        calib_.dig_T3 = static_cast<int16_t>(calib_rx[4] | (calib_rx[5] << 8));

        /* 3. Налаштування вимірювань */
        const std::array<uint8_t, 2> cfg_tx{CtrlMeasReg, (1U << 5) | (1U << 2) | (3U)};
        return bus_.write(address_, cfg_tx, 100);
    }

    [[nodiscard]] std::pair<hal::Status, int32_t> read_temperature_c_x100() noexcept {
        const std::array<uint8_t, 1> reg_tx{TempMsbReg};
        std::array<uint8_t, 3> raw_rx{};

        auto status = bus_.write_read(address_, reg_tx, raw_rx, 100);
        if (!hal::is_ok(status)) return {status, 0};

        int32_t adc_T = static_cast<int32_t>(
            (static_cast<uint32_t>(raw_rx[0]) << 12) |
            (static_cast<uint32_t>(raw_rx[1]) << 4) |
            (static_cast<uint32_t>(raw_rx[2]) >> 4)
        );

        int32_t var1 = ((((adc_T >> 3) - (static_cast<int32_t>(calib_.dig_T1) << 1))) *
                        static_cast<int32_t>(calib_.dig_T2)) >> 11;
        int32_t var2 = (((((adc_T >> 4) - static_cast<int32_t>(calib_.dig_T1)) *
                          ((adc_T >> 4) - static_cast<int32_t>(calib_.dig_T1))) >> 12) *
                        static_cast<int32_t>(calib_.dig_T3)) >> 14;

        int32_t t_fine = var1 + var2;
        int32_t temp_c_x100 = (t_fine * 5 + 128) >> 8;
        return {hal::Status::Ok, temp_c_x100};
    }

private:
    Bus& bus_;
    uint8_t address_;
    CalibrationData calib_{};
};

} // namespace sensors
```
:::

## Універсальний драйвер енергонезалежної пам'яті SPI Flash (W25Q128)

Шина SPI часто використовується для взаємодії з швидкісними чипами пам'яті NOR Flash. Драйвер містить логіку керування лінією вибору кристала (Chip Select), перевірки статусного регістра (готовність до запису, завершення стирання), читання ідентифікатора JEDEC ID та блокового запису сторінок.

:::tabs
```c
/* ========================================================================= */
/* Драйвер SPI Flash W25Q128 на C99 над абстракціями hal_spi_bus / gpio_pin */
/* ========================================================================= */

#define W25Q_CMD_WRITE_ENABLE    0x06
#define W25Q_CMD_WRITE_DISABLE   0x04
#define W25Q_CMD_READ_STATUS_1   0x05
#define W25Q_CMD_READ_DATA       0x03
#define W25Q_CMD_PAGE_PROGRAM    0x02
#define W25Q_CMD_SECTOR_ERASE    0x20
#define W25Q_CMD_JEDEC_ID        0x9F

#define W25Q_STATUS_BUSY_MASK    0x01
#define W25Q_PAGE_SIZE           256

typedef struct {
    const hal_spi_bus_t *spi;
    const hal_gpio_pin_t *cs_pin;
} w25q_driver_t;

static inline void w25q_cs_assert(const w25q_driver_t *dev) {
    hal_gpio_set(dev->cs_pin, HAL_GPIO_LEVEL_LOW);
}

static inline void w25q_cs_deassert(const w25q_driver_t *dev) {
    hal_gpio_set(dev->cs_pin, HAL_GPIO_LEVEL_HIGH);
}

hal_status_t w25q_init(w25q_driver_t *dev, const hal_spi_bus_t *spi, const hal_gpio_pin_t *cs) {
    if (!dev || !spi || !cs) return HAL_STATUS_INVALID_ARG;
    dev->spi = spi;
    dev->cs_pin = cs;

    /* Деактивація CS під час старту */
    w25q_cs_deassert(dev);

    /* Зчитування JEDEC ID: Winbond Manufacturer ID = 0xEF */
    uint8_t cmd = W25Q_CMD_JEDEC_ID;
    uint8_t id[3] = {0};

    w25q_cs_assert(dev);
    hal_status_t s = hal_spi_write(dev->spi, &cmd, 1, 100);
    if (s == HAL_STATUS_OK) {
        s = hal_spi_read(dev->spi, id, 3, 100);
    }
    w25q_cs_deassert(dev);

    if (s != HAL_STATUS_OK) return s;
    if (id[0] != 0xEF) return HAL_STATUS_ERROR; /* Некоректний виробник */

    return HAL_STATUS_OK;
}

static hal_status_t w25q_wait_busy(const w25q_driver_t *dev, uint32_t timeout_ms) {
    uint8_t cmd = W25Q_CMD_READ_STATUS_1;
    uint8_t status = 0;

    for (uint32_t i = 0; i < timeout_ms; ++i) {
        w25q_cs_assert(dev);
        hal_spi_write(dev->spi, &cmd, 1, 10);
        hal_spi_read(dev->spi, &status, 1, 10);
        w25q_cs_deassert(dev);

        if (!(status & W25Q_STATUS_BUSY_MASK)) {
            return HAL_STATUS_OK;
        }
    }
    return HAL_STATUS_TIMEOUT;
}

hal_status_t w25q_read(const w25q_driver_t *dev, uint32_t addr, uint8_t *buf, size_t len) {
    if (!dev || !buf || len == 0) return HAL_STATUS_INVALID_ARG;

    hal_status_t s = w25q_wait_busy(dev, 1000);
    if (s != HAL_STATUS_OK) return s;

    uint8_t cmd_buf[4] = {
        W25Q_CMD_READ_DATA,
        (uint8_t)((addr >> 16) & 0xFF),
        (uint8_t)((addr >> 8) & 0xFF),
        (uint8_t)(addr & 0xFF)
    };

    w25q_cs_assert(dev);
    s = hal_spi_write(dev->spi, cmd_buf, 4, 100);
    if (s == HAL_STATUS_OK) {
        s = hal_spi_read(dev->spi, buf, len, 1000);
    }
    w25q_cs_deassert(dev);

    return s;
}

hal_status_t w25q_write_page(const w25q_driver_t *dev, uint32_t addr, const uint8_t *data, size_t len) {
    if (!dev || !data || len == 0 || len > W25Q_PAGE_SIZE) return HAL_STATUS_INVALID_ARG;

    /* 1. Дозвіл запису (Write Enable) */
    uint8_t cmd_we = W25Q_CMD_WRITE_ENABLE;
    w25q_cs_assert(dev);
    hal_status_t s = hal_spi_write(dev->spi, &cmd_we, 1, 100);
    w25q_cs_deassert(dev);
    if (s != HAL_STATUS_OK) return s;

    /* 2. Команда програмування сторінки + 24-бітний адрес */
    uint8_t cmd_buf[4] = {
        W25Q_CMD_PAGE_PROGRAM,
        (uint8_t)((addr >> 16) & 0xFF),
        (uint8_t)((addr >> 8) & 0xFF),
        (uint8_t)(addr & 0xFF)
    };

    w25q_cs_assert(dev);
    s = hal_spi_write(dev->spi, cmd_buf, 4, 100);
    if (s == HAL_STATUS_OK) {
        s = hal_spi_write(dev->spi, data, len, 500);
    }
    w25q_cs_deassert(dev);
    if (s != HAL_STATUS_OK) return s;

    /* 3. Очікування завершення запису флеш-матриці */
    return w25q_wait_busy(dev, 100);
}
```
```cpp
/* ========================================================================= */
/* Шаблонний драйвер SPI Flash W25Q128 на C++20                             */
/* ========================================================================= */

namespace storage {

template <hal::SpiMaster Spi, hal::GpioPin CsPin>
class W25qFlash {
public:
    static constexpr uint8_t CmdWriteEnable  = 0x06;
    static constexpr uint8_t CmdReadStatus1  = 0x05;
    static constexpr uint8_t CmdReadData     = 0x03;
    static constexpr uint8_t CmdPageProgram  = 0x02;
    static constexpr uint8_t CmdJedecId      = 0x9F;
    static constexpr uint8_t StatusBusyMask  = 0x01;
    static constexpr size_t  PageSize        = 256;

    W25qFlash(Spi& spi, CsPin cs) noexcept : spi_(spi), cs_(cs) {}

    hal::Status init() noexcept {
        cs_.set_level(hal::PinLevel::High);

        const std::array<uint8_t, 1> cmd{CmdJedecId};
        std::array<uint8_t, 3> id{};

        cs_.set_level(hal::PinLevel::Low);
        auto s = spi_.write(cmd, 100);
        if (hal::is_ok(s)) {
            s = spi_.read(id, 100);
        }
        cs_.set_level(hal::PinLevel::High);

        if (!hal::is_ok(s)) return s;
        if (id[0] != 0xEF) return hal::Status::Error;

        return hal::Status::Ok;
    }

    hal::Status read(uint32_t addr, std::span<uint8_t> buf) noexcept {
        if (buf.empty()) return hal::Status::InvalidArg;

        auto s = wait_busy(1000);
        if (!hal::is_ok(s)) return s;

        const std::array<uint8_t, 4> cmd_buf{
            CmdReadData,
            static_cast<uint8_t>((addr >> 16) & 0xFF),
            static_cast<uint8_t>((addr >> 8) & 0xFF),
            static_cast<uint8_t>(addr & 0xFF)
        };

        cs_.set_level(hal::PinLevel::Low);
        s = spi_.write(cmd_buf, 100);
        if (hal::is_ok(s)) {
            s = spi_.read(buf, 1000);
        }
        cs_.set_level(hal::PinLevel::High);
        return s;
    }

    hal::Status write_page(uint32_t addr, std::span<const uint8_t> data) noexcept {
        if (data.empty() || data.size() > PageSize) return hal::Status::InvalidArg;

        const std::array<uint8_t, 1> cmd_we{CmdWriteEnable};
        cs_.set_level(hal::PinLevel::Low);
        auto s = spi_.write(cmd_we, 100);
        cs_.set_level(hal::PinLevel::High);
        if (!hal::is_ok(s)) return s;

        const std::array<uint8_t, 4> cmd_buf{
            CmdPageProgram,
            static_cast<uint8_t>((addr >> 16) & 0xFF),
            static_cast<uint8_t>((addr >> 8) & 0xFF),
            static_cast<uint8_t>(addr & 0xFF)
        };

        cs_.set_level(hal::PinLevel::Low);
        s = spi_.write(cmd_buf, 100);
        if (hal::is_ok(s)) {
            s = spi_.write(data, 500);
        }
        cs_.set_level(hal::PinLevel::High);
        if (!hal::is_ok(s)) return s;

        return wait_busy(100);
    }

private:
    hal::Status wait_busy(uint32_t timeout_ms) noexcept {
        const std::array<uint8_t, 1> cmd{CmdReadStatus1};
        std::array<uint8_t, 1> status{0};

        for (uint32_t i = 0; i < timeout_ms; ++i) {
            cs_.set_level(hal::PinLevel::Low);
            spi_.write(cmd, 10);
            spi_.read(status, 10);
            cs_.set_level(hal::PinLevel::High);

            if (!(status[0] & StatusBusyMask)) {
                return hal::Status::Ok;
            }
        }
        return hal::Status::Timeout;
    }

    Spi& spi_;
    CsPin cs_;
};

} // namespace storage
```
:::

## Модульне тестування драйверів на хост-системі

Завдяки відокремленню периферійного інтерфейсу від заліза, повний набір модульних тестів (Unit Tests) для логіки ініціалізації, парсингу калібрувальних коефіцієнтів та математичної компенсації температури може виконуватися на комп'ютері розробника або в системі неперервної інтеграції (CI) за частки мілісекунди без наявності фізичної мікросхеми.

:::tabs
```c
#include <stdio.h>
#include <assert.h>

int main(void) {
    printf("[C99 Mock Test] Початок тестування драйвера BME280...\n");

    /* Створення контексту та ініціалізація пам'яті Mock I2C */
    mock_i2c_ctx_t i2c_ctx;
    memset(&i2c_ctx, 0, sizeof(i2c_ctx));
    i2c_ctx.expected_addr = BME280_I2C_ADDR_PRIM;

    /* Запис очікуваного Chip ID */
    i2c_ctx.registers[BME280_REG_CHIP_ID] = BME280_CHIP_ID_VAL;

    /* Запис тестових калібрувальних коефіцієнтів: dig_T1=27504, dig_T2=26435, dig_T3=-1000 */
    i2c_ctx.registers[BME280_REG_CALIB00 + 0] = 0x70;
    i2c_ctx.registers[BME280_REG_CALIB00 + 1] = 0x6B;
    i2c_ctx.registers[BME280_REG_CALIB00 + 2] = 0x43;
    i2c_ctx.registers[BME280_REG_CALIB00 + 3] = 0x67;
    i2c_ctx.registers[BME280_REG_CALIB00 + 4] = 0x18;
    i2c_ctx.registers[BME280_REG_CALIB00 + 5] = 0xFC;

    /* Запис сирих даних температури: adc_T = 519888 */
    i2c_ctx.registers[BME280_REG_TEMP_MSB + 0] = 0x7E;
    i2c_ctx.registers[BME280_REG_TEMP_MSB + 1] = 0xEC;
    i2c_ctx.registers[BME280_REG_TEMP_MSB + 2] = 0x00;

    /* Збирання екземпляра HAL */
    hal_i2c_bus_t mock_bus = {
        .ops = &mock_i2c_ops,
        .ctx = &i2c_ctx
    };

    /* Ініціалізація драйвера датчика */
    bme280_driver_t sensor;
    hal_status_t status = bme280_init(&sensor, &mock_bus, BME280_I2C_ADDR_PRIM);
    assert(status == HAL_STATUS_OK);
    printf(" -> Ініціалізація датчика успішна, Chip ID валідний (0x%02X)\n", BME280_CHIP_ID_VAL);

    /* Зчитування та перевірка обчисленої температури */
    int32_t temp_c_x100 = 0;
    status = bme280_read_temperature(&sensor, &temp_c_x100);
    assert(status == HAL_STATUS_OK);
    printf(" -> Температура: %d.%02d °C (очікувалось ~25.08 °C)\n", temp_c_x100 / 100, temp_c_x100 % 100);
    assert(temp_c_x100 >= 2400 && temp_c_x100 <= 2600);

    /* Перевірка обробки помилки NACK */
    i2c_ctx.force_nack = true;
    status = bme280_read_temperature(&sensor, &temp_c_x100);
    assert(status == HAL_STATUS_NACK);
    printf(" -> Тест реакції на відсутність відповіді (NACK) пройдено успішно.\n");

    printf("[C99 Mock Test] Усі перевірки завершено успішно!\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "[C++20 Mock Test] Початок тестування концептуального драйвера BME280...\n";

    using MockBus = hal::mock::MockI2cBus<256>;
    MockBus mock_bus{sensors::Bme280<MockBus>::DefaultAddress};

    /* Налаштування регістрів емулятора */
    mock_bus.set_reg(sensors::Bme280<MockBus>::ChipIdRegister, sensors::Bme280<MockBus>::ExpectedChipId);
    mock_bus.set_reg(sensors::Bme280<MockBus>::CalibRegister + 0, 0x70);
    mock_bus.set_reg(sensors::Bme280<MockBus>::CalibRegister + 1, 0x6B);
    mock_bus.set_reg(sensors::Bme280<MockBus>::CalibRegister + 2, 0x43);
    mock_bus.set_reg(sensors::Bme280<MockBus>::CalibRegister + 3, 0x67);
    mock_bus.set_reg(sensors::Bme280<MockBus>::CalibRegister + 4, 0x18);
    mock_bus.set_reg(sensors::Bme280<MockBus>::CalibRegister + 5, 0xFC);

    mock_bus.set_reg(sensors::Bme280<MockBus>::TempMsbReg + 0, 0x7E);
    mock_bus.set_reg(sensors::Bme280<MockBus>::TempMsbReg + 1, 0xEC);
    mock_bus.set_reg(sensors::Bme280<MockBus>::TempMsbReg + 2, 0x00);

    /* Створення екземпляра шаблонного драйвера */
    sensors::Bme280<MockBus> sensor{mock_bus};

    auto status = sensor.init();
    assert(hal::is_ok(status));
    std::cout << " -> C++20 сенсор успішно ініціалізовано.\n";

    auto [read_status, temp] = sensor.read_temperature_c_x100();
    assert(hal::is_ok(read_status));
    std::cout << " -> Зчитана температура: " << (temp / 100) << "." << (temp % 100) << " °C\n";
    assert(temp >= 2400 && temp <= 2600);

    mock_bus.set_force_nack(true);
    auto [err_status, _] = sensor.read_temperature_c_x100();
    assert(err_status == hal::Status::Nack);
    std::cout << " -> Перевірка відмови зв'язку NACK успішна.\n";

    std::cout << "[C++20 Mock Test] Усі концептуальні перевірки пройдено!\n";
    return 0;
}
```
:::

## Фізичні особливості шинних протоколів та схемотехнічні обмеження

### Фізичний рівень I2C: ємність ліній, фронти сигналів та розрахунок підтягувальних резисторів

Протокол I2C функціонує за схемою «відкритий колектор / відкритий стік» (Open-Drain). Це означає, що активні вихідні каскади мікроконтролера та підключених мікросхем здатні лише притискати лінії SDA та SCL до землі (активний низький рівень). Повернення ліній у високий логічний стан здійснюється виключно зовнішніми підтягувальними резисторами `R_p`, підключеними до шини живлення `V_DD`.

Головним фізичним ворогом шини є паразитна ємність монтажу, друкованих провідників та вхідних каскадів мікросхем `C_b` (Bus Capacitance). Специфікація стандарту I2C обмежує максимальну сумарну ємність шини значенням 400 пФ для стандартного режиму (Standard Mode, 100 кбіт/с) та швидкісного режиму (Fast Mode, 400 кбіт/с).

Тривалість наростання фронту сигналу (Rise Time, `t_r`) визначається часом заряджання паразитної ємності через підтягувальний резистор за класичним експоненційним законом RC-ланцюга від рівня 0.3 `V_DD` до 0.7 `V_DD`:
```
t_r = 0.8473 * R_p * C_b
```

Звідси випливає верхня межа опору резистора: для режиму Fast Mode специфікація вимагає `t_r ≤ 300 нс`. При ємності шини `C_b = 200 пФ` максимальний опір підтяжки становить:
```
R_p_max = 300e-9 / (0.8473 * 200e-12) ≈ 1770 Ом
```

Нижня межа опору `R_p_min` визначається максимально допустимим вхідним струмом стіка транзистора (Sink Current, зазвичай 3 мА при `V_OL = 0.4 В`):
```
R_p_min = (V_DD - V_OL) / I_OL = (3.3 - 0.4) / 0.003 ≈ 966 Ом
```

Якщо підтягувальний резистор вибрано занадто великим (наприклад, типові внутрішні підтяжки мікроконтролера 40-50 кОм), фронт сигналу стає пологим, лінія не встигає піднятися до рівня логічної одиниці за час половини тактового періоду, і зв'язок руйнується помилками синхронізації.

### Фізичний рівень SPI: режими CPOL/CPHA та топології підключення

На відміну від I2C, лінії шини SPI працюють за схемою Push-Pull (двотактний активний вихід), що дозволяє досягати швидкостей передачі даних у десятки мегагерц. Однак інтерфейс SPI не має єдиного стандарту фази тактування. Існує 4 комбінації полярності тактового сигналу (CPOL) та фази фіксації даних (CPHA):

1. **Mode 0 (CPOL=0, CPHA=0)**: Лінія SCK неактивна у низькому рівні. Дані фіксуються веденим пристроєм по наростаючому фронту (Rising Edge) і змінюються по спадаючому (Falling Edge). Це найпоширеніший режим для Flash-пам'яті та датчиків.
2. **Mode 1 (CPOL=0, CPHA=1)**: Лінія SCK неактивна у низькому рівні. Дані змінюються по наростаючому фронту і фіксуються по спадаючому.
3. **Mode 2 (CPOL=1, CPHA=0)**: Лінія SCK неактивна у високому рівні. Дані фіксуються по спадаючому фронту і змінюються по наростаючому.
4. **Mode 3 (CPOL=1, CPHA=1)**: Лінія SCK неактивна у високому рівні. Дані змінюються по спадаючому фронту і фіксуються по наростаючому.

Драйвер HAL зобов'язаний гарантувати дотримання часових інтервалів між переведенням лінії CS у низький стан (CS Assert) та першим тактовим імпульсом SCK (Setup Time `t_CSS`), а також між останнім імпульсом і підняттям CS (Hold Time `t_CSH`). При високих тактових частотах процесора пряме перемикання GPIO безпосередньо перед записом у регістр SPI може порушити `t_CSS` (який для деяких датчиків становить від 50 до 100 нс), спричиняючи втрату першого біта команди.

## Глибокий аналіз реалізації та інженерні пастки

### 1. Апаратний арбітраж шин та синхронізація у багатозадачних ОС (RTOS)

Шина I2C або SPI часто є спільним ресурсом для десятка різних мікросхем на платі (акселерометр, барометр, чип енергонезалежної пам'яті EEPROM, годинник реального часу RTC). Якщо два потоки RTOS (наприклад, потік опитування сенсорів і потік збереження конфігурації у флеш) спробують одночасно надіслати транзакцію до апаратного I2C контролера, виникне стан гонитви (race condition), що призведе до спотворення даних та аварійного зависання шини.

Існує дві архітектурні стратегії вирішення цієї проблеми на рівні HAL:

1. **Блокування на рівні шини (Bus Locking Mutex)**: Екземпляр дескриптора шини містить м'ютекс RTOS. Кожна функція `write`, `read` або `write_read` захоплює м'ютекс перед стартом транзакції та звільняє його після видачі сигналу Stop.
2. **Транзакційне володіння (Acquire / Release семантика)**: Якщо пристрій вимагає серії транзакцій з утриманням лінії Chip Select (наприклад, запис сторінки SPI Flash з перевіркою статусного регістра), клієнтський код явно викликає `hal_spi_acquire_bus()` та `hal_spi_release_bus()`.

Слід пам'ятати про строгу заборону виклику блокуючих функцій HAL з обробників переривань (ISR). Якщо виклик периферії потрібен всередині переривання, шар HAL повинен надавати окремий неблокуючий асинхронний інтерфейс на основі черг повідомлень або кільцевих буферів (Ring Buffers).

### 2. Зависання шини I2C (I2C Bus Lockup) та механізм відновлення

Найпоширеніша апаратна пастка шини I2C полягає у зависанні лінії даних SDA у низькому логічному рівні. Це відбувається, коли мікроконтролер скидається (через Watchdog або просідання живлення) прямо під час читання байта від веденого пристрою. Ведений пристрій у цей момент передавав логічний '0' і продовжує утримувати лінію SDA притиснутою до землі, чекаючи тактових імпульсів SCL.

Оскільки SDA притиснута до землі, апаратний I2C контролер мікроконтролера вважає, що шина постійно зайнята (`HAL_STATUS_BUSY`), і не може згенерувати сигнал Start.

Стандартний алгоритм відновлення (Bus Recovery Routine), який повинен реалізовувати шар HAL або BSP під час ініціалізації шини:
1. Перемкнути піни I2C (SCL і SDA) у режим звичайного виводу GPIO Open-Drain.
2. Перевірити стан лінії SDA. Якщо SDA знаходиться у високому рівні — шина вільна, відновлення не потрібне.
3. Якщо SDA у низькому рівні — згенерувати програмно до 9 тактових імпульсів на лінії SCL (перемиканням піна GPIO з інтервалом ~5 мкс).
4. На кожному тактовому імпульсі ведений пристрій виштовхує черговий біт свого внутрішнього зсувного регістра. Як тільки ведений пристрій передасть усі 8 бітів і отримає 9-й імпульс без підтвердження, він відпустить лінію SDA.
5. Після звільнення SDA згенерувати коректну послідовність сигналів Stop: опустити SCL, опустити SDA, підняти SCL, підняти SDA.
6. Повернути піни у режим роботи периферійного блока I2C.

### 3. Порівняння асемблерного коду: C Vtable проти C++20 Concepts

При компіляції для архітектури ARM Cortex-M4 з оптимізацією `-O2` або `-Os` різниця у згенерованому машинному коді є наочною:

У випадку **динамічного C99 HAL**:
```asm
/* Виклик hal_gpio_set(pin, HAL_GPIO_LEVEL_HIGH) */
ldr   r3, [r0, #0]       /* Завантажити покажчик на ops з дескриптора pin */
ldr   r3, [r3, #4]       /* Завантажити адресу функції set_level з ops */
ldr   r0, [r0, #4]       /* Завантажити покажчик на ctx */
movs  r1, #1             /* Аргумент: рівень HIGH */
blx   r3                 /* Непрямий перехід на функцію драйвера */
```
Цей фрагмент вимагає 5 інструкцій, здійснює 2 звернення до оперативної пам'яті (RAM), виконує непрямий перехід `blx`, що спричиняє скидання конвеєра інструкцій процесора, і вимагає прологу та епілогу (`push {r4, lr} / pop {r4, pc}`) у викликаній функції. Загальний час виконання — від 15 до 30 тактів CPU.

У випадку **статичного C++20 HAL**:
```asm
/* Виклик StaticGpioPin<GPIOA_BASE, 5>::set_level(PinLevel::High) */
movs  r1, #32            /* Бітова маска (1 << 5), обчислена компілятором */
ldr   r0, =0x48000000    /* Базова адреса регістрів GPIOA */
str   r1, [r0, #24]      /* Прямий запис у регістр BSRR (зсув 24) */
```
Цей фрагмент повністю вбудовується (inlined) на місці виклику. Компільований код не містить виклику підпрограми, не використовує стек, не містить таблиць у RAM і виконується за 1-2 такти процесора.

### 4. Вирівнювання пам'яті та когерентність кешу для DMA-транзакцій

При проєктуванні високоефективних версій HAL, що використовують контролери прямого доступу до пам'яті (DMA) для передачі великих блоків даних через SPI або I2C, виникають дві критичні вимоги:
* **Вирівнювання буферів**: Буфери передачі та приймання повинні бути вирівняні по межі 4 або 32 байтів (залежно від розрядності шини DMA та розміру рядка процесорного кешу даних D-Cache на ядрах Cortex-M7).
* **Очищення та інвалідація кешу (Cache Invalidation)**: Якщо ядро процесора має D-Cache, перед запуском DMA передачі необхідно виконати операцію `Clean Data Cache`, щоб виштовхнути змінені процесором дані з кешу в основну RAM. Після завершення DMA приймання необхідно виконати операцію `Invalidate Data Cache`, щоб наступне читання процесором гарантовано завантажило свіжі дані з RAM, а не застарілі значення з кешу.

Якщо шар HAL не враховує когерентність кешу, прикладний код отримуватиме випадкові пошкодження даних, які вкрай важко локалізувати звичайним налагодженням.

### 5. Асинхронні переривання та безблокувальні черги (Ring Buffer)

Для високошвидкісних інтерфейсів (наприклад, UART або SPI у безперервному потоковому режимі) синхронний блокуючий HAL стає пляшковим горлом системи. Замість очікування кожного байта у циклі polling, HAL проектується як асинхронний автомат станів:

1. **Кільцевий буфер без блокувань (Lock-Free Single-Producer Single-Consumer Queue)**: Драйвер зберігає індекси `head` та `tail`. Переривання від периферії інкрементує `head` після запису байта, а прикладний потік зчитує байти та інкрементує `tail`. Оскільки кожен покажчик модифікується лише однією стороною, операція є потокобезпечною без використання м'ютексів та заборони переривань.
2. **Подвійна буферизація DMA (Ping-Pong Buffering)**: Контролер DMA налаштовується у циклічному режимі з генерацією двох переривань: `Half-Transfer Complete` (заповнено першу половину великого буфера) та `Transfer Complete` (заповнено другу половину). Поки процесор обробляє першу половину даних, апаратний блок DMA паралельно заповнює другу, що гарантує безперервний потік без втрати жодного байта.

Правильно спроєктований шар HAL інкапсулює цю складність: прикладний код підписується на події готовності пакетів через зворотні виклики (callbacks) або події RTOS Event Flags, не знаючи, який саме контролер DMA або вектор переривань задіяно у поточному кремнії.

### 6. Енергоспоживання та координація сплячих режимів (Low-Power Coordination)

Сучасні пристрої з батарейним живленням проводять понад 99% свого життєвого циклу у стані глибокого сну (Deep Sleep або Stop Mode). Коли прикладний рівень вирішує перевести процесор у режим сну, шар HAL повинен виконати скоординовану підготовку всієї задіяної периферії:

1. **Переведення виводів у стан високого імпедансу (High-Z Floating / Analog Input)**: Залишення активного цифрового виходу Push-Pull у стані High при наявності зовнішнього підтягувального резистора або заземленого навантаження створює постійний витік струму силою від кількох сотень мікроампер до десятків міліампер. Це здатне розрядити літієвий акумулятор за лічені дні. Перед сном HAL перемикає невикористовувані цифрові виводи в аналоговий режим (у якому вимикаються вхідні тригери Шмітта та вихідні драйвери польових транзисторів).
2. **Зупинка тактування шинних периферійних модулів (Clock Gating)**: Вимкнення бітів тактування у регістрах вендора (наприклад, `RCC->APB1ENR` у STM32 або `DPORT_PERIP_CLK_EN_REG` у ESP32) зупиняє динамічне перезаряджання ємностей логічних вентилів контролера шини, знижуючи струм споживання мікроконтролера з десятків міліампер до одиниць мікроампер.
3. **Збереження та відновлення контексту регістрів**: При переході у найглибші режими енергозбереження (Standby / Deep Sleep) живлення периферійних блоків повністю вимикається, і вміст конфігураційних регістрів (швидкість передачі бодрейту UART, переддільники I2C, налаштування фільтрації шумів) повністю втрачається. Після пробудження шар HAL або BSP зобов'язаний автоматично відновити конфігурацію кремнію, перш ніж передати керування прикладному коду.

### 7. Порядок байтів (Endianness) та вирівнювання некратних структур

При обміні даними через послідовні шини виникає конфлікт між порядком передачі байтів протоколом та внутрішнім форматом представлення багатобайтових чисел процесором.

Більшість протоколів датчиків I2C та SPI (включно з BME280 та MPU6050) передають старший байт першим (Big-Endian / Network Byte Order), тоді як ядра мікроконтролерів ARM Cortex-M та RISC-V зберігають цілі числа у пам'яті у форматі Little-Endian (молодший байт за меншою адресою).

Якщо розробник драйвера намагається прочитати 16-бітне або 32-бітне значення регістра прямим приведенням покажчика на буфер приймання (`uint16_t *val = (uint16_t*)&rx_buf[0]`), виникають дві критичні помилки:
1. **Спотворення значення числа**: Старший і молодший байти поміняються місцями, внаслідок чого число `0x1234` буде інтерпретовано процесором як `0x3412`.
2. **Апаратний збій невирівняного доступу (Unaligned Access Fault)**: Ядра ARM Cortex-M0 та Cortex-M0+ апаратно не підтримують доступ до 16-бітних та 32-бітних слів за непарними адресами пам'яті. Якщо `rx_buf[1]` має непарну адресу, спроба читання `*(uint16_t*)&rx_buf[1]` викличе негайне апаратне виключення процесора `HardFault`.

Правильне інженерне рішення, реалізоване у шарі HAL, полягає у явному побайтовому конструюванні чисел за допомогою бітових зсувів:
:::tabs
```c
uint16_t val_be = (uint16_t)(((uint16_t)rx_buf[0] << 8) | (uint16_t)rx_buf[1]);
int16_t  val_le = (int16_t)(((uint16_t)rx_buf[1] << 8) | (uint16_t)rx_buf[0]);
```
```cpp
auto val_be = static_cast<uint16_t>((static_cast<uint16_t>(rx_buf[0]) << 8) | static_cast<uint16_t>(rx_buf[1]));
auto val_le = static_cast<int16_t>((static_cast<uint16_t>(rx_buf[1]) << 8) | static_cast<uint16_t>(rx_buf[0]));
```
:::
Цей код є 100% переносимим, не залежить від порядку байтів процесора архітектури хоста чи таргета, не викликає збоїв невирівняного доступу і ефективно компілюється оптимізатором у спеціальні процесорні інструкції реверсу байтів (такі як `REV` та `REV16` у системі команд ARM Thumb-2).

### 8. Обробка помилок та стратегія експоненційного відкату (Exponential Backoff)

У реальних індустріальних умовах послідовні шини піддаються впливу електромагнітних завад від електродвигунів, реле та імпульсних джерел живлення. Короткочасний сплеск напруги на лінії SCK може призвести до хибного тактового імпульсу, через що ведений пристрій відповість NACK або пропустить байт.

Примітивний драйвер при першій же помилці зв'язку повертає код помилки у вищий рівень, що нерідко призводить до перезавантаження всього пристрою або зупинки технологічного процесу.

Надійний шар HAL підтримує багаторівневу стратегію відновлення:
* **Миттєва спроба повтору (Immediate Retry)**: Для швидких транзакцій I2C виконується до 2-3 повторних спроб надсилання пакета з попередньою перевіркою стану лінії.
* **Експоненційна затримка (Exponential Backoff)**: Якщо шина відповідає зайнятістю (`HAL_STATUS_BUSY`), драйвер робить паузу тривалістю `T`, яка з кожною невдалою спробою подвоюється (`2T`, `4T`, `8T`), даючи можливість веденому пристрою завершити внутрішній цикл аналогово-цифрового перетворення або запису в пам'ять.
* **Апаратне скидання веденого пристрою (Target Hardware Reset)**: Якщо всі спроби відновити зв'язок програмними засобами зазнали невдачі, драйвер через BSP перемикає лінію апаратного скидання (NRST / Power Enable) завислої мікросхеми, після чого ініціалізує її карту регістрів наново.

### 9. Абстракція апаратних таймерів та широтно-імпульсної модуляції (PWM)

Апаратні таймери становлять основу планування подій реального часу та генерації аналогових керуючих впливів для силової електроніки. На відміну від простих ліній вводу-виводу, таймерний блок містить складну конфігураційну матрицю: базовий дільник частоти (Prescaler), регістр автоматичного перезавантаження періоду (Auto-Reload Register, ARR) та набір каналів захоплення/порівняння (Capture/Compare Channels, CCR).

Шар абстракції таймерів вирішує наступні ключові інженерні задачі:
1. **Нормалізація часових інтервалів**: Прикладний код оперує мікросекундами, мілісекундами або герцами, тоді як апаратний регістр приймає цілочисельну кількість тактів внутрішньої тактової шини (наприклад, 84 МГц на APB1 або 168 МГц на APB2). HAL обчислює коефіцієнти переддільника автоматично, зважаючи на поточну частоту ядра із системного блоку тактування (System Core Clock).
2. **Абстракція генерації ШІМ (PWM Generation)**: Інтерфейс надає уніфіковані методи `hal_pwm_set_frequency(timer, hz)` та `hal_pwm_set_duty_cycle(timer, channel, permille)`, де шпаруватість задається у проміле (від 0 до 1000) або у відсотках з плаваючою/фіксованою точкою. Це повністю ізолює бізнес-логіку керування сервоприводами чи яскравістю світлодіодів від розрядності лічильника (16-бітний таймер з максимальним рахунком 65535 проти 32-бітного з рахунком 4294967295).
3. **Генерація комплементарних сигналів із мертвою зоною (Dead-Time Insertion)**: У задачах керування безколекторними двигунами (BLDC) або напівмостовими перетворювачами напруги неможливо одночасно відкривати верхній і нижній силові транзистори плеча, оскільки це спричиняє коротке замикання шини живлення (Shoot-Through Current). HAL дозволяє конфігурувати параметр мертвого часу (Dead-Time) у наносекундах, перекладаючи його у специфічні регістри вендора (наприклад, `TIMx->BDTR` у STM32).

### 10. Аналогово-цифрове перетворення (ADC) та компенсація внутрішніх джерел опорної напруги

Зчитування аналогових сигналів вимагає врахування метрологічних характеристик конкретного кремнію. Напруга живлення мікроконтролера `V_DD` у батарейних системах постійно змінюється у процесі розряду від 3.3 В до 2.0 В, через що пряме переведення коду АЦП у напругу за формулою `V_in = ADC_RAW * 3.3 / 4095` дає неприпустимо високу похибку вимірювань.

Професійний шар HAL для АЦП підтримує калібрувальний механізм на основі внутрішнього джерела опорної напруги (Internal Voltage Reference, `V_REFINT`, номінальне значення зазвичай 1.20 В або 1.224 В):
* Під час виробництва чипа на заводі виконується калібрувальне вимірювання `V_REFINT` при строго фіксованій напрузі живлення 3.3 В та температурі 25 °C, а результат записується в захищену системну пам'ять (System Memory Flash, наприклад регістр `VREFINT_CAL_ADDR`).
* Перед початком сесії вимірювань HAL вимірює поточний сирий код внутрішнього каналу `V_REFINT`.
* Поточна реальна напруга живлення `V_DDA` обчислюється аналітично:
```
V_DDA = 3.3 * (VREFINT_CAL / VREFINT_DATA)
```
* Будь-яке наступне вимірювання на довільному зовнішньому аналоговому каналі коригується з урахуванням обчисленого `V_DDA`, що забезпечує стабільну абсолютну точність вимірювання напруги з точністю до десятих часток відсотка протягом усього життєвого циклу батареї.

Крім того, шар HAL контролює час вибірки сигналу (Sampling Time). Якщо вихідний опір аналогового сенсора `R_src` є високим (наприклад, резистивний дільник напруги з резисторами по 100 кОм), внутрішня ємність вибірки АЦП `C_adc` (зазвичай 4-8 пФ) не встигає повністю зарядитися за мінімальний час тактування. HAL забезпечує обчислення мінімально допустимого часу вибірки та автоматично налаштовує регістри переддільника АЦП, захищаючи розробника від систематичних помилок вимірювання.

### 11. Асинхронний інтерфейс послідовного порту UART та детекція пауз (Idle Line Detection)

Послідовний інтерфейс UART традиційно використовується як для виводу налагоджувальних журналів (Logging), так і для прийому бінарних протоколів змінного розміру (наприклад, пакетів зв'язку з GNSS-приймачами, модемами стільникового зв'язку або промисловими датчиками RS-485).

Головна архітектурна проблема реалізації UART у шарі HAL полягає в тому, що довжина вхідного пакета заздалегідь невідома. Якщо налаштувати прийом через блокуючий виклик `hal_uart_read(buf, 64, timeout)`, функція зависне до отримання повних 64 байтів або до завершення тайм-ауту, що руйнує взаємодію реального часу.

Сучасний шар HAL вирішує цю проблему за допомогою апаратної детекції лінії спокою (Idle Line Detection) у поєднанні з контролером прямого доступу до пам'яті (DMA):
1. Контролер DMA налаштовується на автоматичне безперервне перенесення вхідних байтів з регістра даних UART у циклічний буфер у пам'яті (Circular DMA Buffer).
2. Периферійний блок UART налаштовується на генерацію переривання `IDLE Interrupt`, яке виникає рівно тоді, коли після прийому чергового байта лінія зв'язку RX залишається у високому рівні протягом тривалості одного повного кадру (10-11 бітових інтервалів при передачі 8N1).
3. В обробнику переривання IDLE шар HAL зчитує поточне значення лічильника залишку байтів DMA (`NDTR` у STM32), обчислює точну кількість фактично прийнятих байтів пакета та генерує зворотний виклик або подію RTOS із вказівкою зміщення та довжини нових даних.
4. Такий підхід повністю звільняє ядро мікроконтролера від побайтової обробки переривань на високих швидкостях зв'язку (наприклад, 921600 бод або 3 Мбод) і зводить накладні витрати до одного короткого переривання на весь прийнятий пакет, повністю ізолюючи прикладну програму від особливостей контролера DMA конкретного мікроконтролера.

### 12. Валідація драйверів і конфігурацій периферії концептами C++20 на етапі компіляції

У традиційній практиці розробки вбудованих систем мовою C несумісність драйвера периферії з інтерфейсом виявляється виключно під час виконання: пропущений покажчик у таблиці операцій `ops->write_read == NULL` спричиняє розіменування нульового покажчика та виклик апаратного виключення `HardFault`, а передача невідповідного дескриптора викликає спотворення оперативної пам'яті через неконтрольоване приведення `(void*)ctx`. Використання концептів мови C++20 кардинально змінює архітектурну модель надійності, переносячи повну верифікацію апаратних контрактів на етап компіляції без додавання жодного байта накладних витрат у бінарний образ прошивки.

Концепти C++20 вирішують чотири критичні задачі в архітектурі вбудованого HAL:

1. **Миттєва діагностика несумісності інтерфейсів (Compile-Time Interface Verification)**: Застосування виразу `static_assert(hal::I2cMaster<DriverType>)` у тілі тесту або використання обмеження `template <hal::I2cMaster Bus>` у визначенні класу драйвера сенсора гарантує, що будь-яка невідповідність сигнатури (наприклад, повернення цілого числа `int` замість строго типізованого переліку `hal::Status`, відсутність специфікатора `noexcept` чи передача сирого покажчика замість безпечного діапазону `std::span`) зупиняє компіляцію з точним і локалізованим повідомленням про помилку ще до першого прошивання мікроконтролера.

2. **Ієрархічна композиція апаратних можливостей (Subsumption)**: Периферійні блоки одного класу в різних мікроконтролерах часто мають різний набір можливостей (наприклад, базова шина SPI з побайтовим опитуванням проти розширеної шини з апаратною підтримкою DMA). Замість роздування таблиці vtable порожніми покажчиками або використання прапорців конфігурації під час виконання, у C++20 створюються спеціалізовані концепти через уточнення базових контрактів:
```cpp
template <typename T>
concept DmaCapableSpi = hal::SpiMaster<T> && requires(T bus, std::span<const uint8_t> tx, std::span<uint8_t> rx) {
    { bus.transfer_dma(tx, rx) } noexcept -> std::same_as<hal::Status>;
};
```
Завдяки цьому драйвер дисплея чи зовнішньої пам'яті за допомогою конструкції `if constexpr (DmaCapableSpi<Bus>)` на етапі компіляції обирає високошвидкісний асинхронний DMA-обмін для цільових платформ, де він доступний, або синхронний обмін для простіших чипів, генеруючи оптимальний машинний код під конкретний кремній.

3. **Статична верифікація апаратних ресурсів та мультиплексування виводів**: Концепти та обмеження `requires` здатні валідувати нетипові параметри шаблонів (Non-Type Template Parameters). Це дозволяє контролювати коректність конфігурації заліза (наприклад, перевірку `requires (PinIndex <= 15)` для портів GPIO Cortex-M або перевірку належності адреси регістрів периферії до системної шини APB) безпосередньо при генерації коду. Спроба створити екземпляр драйвера SPI на ніжках, які фізично не з'єднані з блоком мультиплексора (Alternate Function), відкидається компілятором як синтаксично неприпустима.

4. **Нульова вартість абстракції (Zero-Cost Abstraction)**: На відміну від класичного динамічного поліморфізму, концептуальні обмеження C++20 усувають потребу в таблицях віртуальних функцій (`vtable`) та покажчиках (`vptr`) в оперативній пам'яті. Компілятор виконує пряме агресивне вбудовування (inlining) викликів регістрового рівня, транслюючи виклики методів концептуального драйвера в поодинокі машинні інструкції без викликів підпрограм, збереження регістрів у стек або скидання конвеєра процесора.

