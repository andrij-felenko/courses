# 📋 Контракт та інтерфейси для мокування Hardware Abstraction Layer (HAL)

Рівень апаратної абстракції (англ. *Hardware Abstraction Layer*, HAL) є головною архітектурною межею між переносним прикладним кодом і специфічними для мікроконтролера регістрами пам'яті. Якщо прикладний модуль безпосередньо звертається до апаратних регістрів (наприклад, записує байти у `SPI1->DR` або читає біти з `GPIOA->IDR`), його неможливо скомпілювати та протестувати на робочому комп'ютері (x86-64 або ARM64) без доступу до фізичного чипа.

Щоб забезпечити ізольоване модульне тестування на хості, взаємодія з периферією оформлюється у вигляді формального інтерфейсного контракту. При компіляції для цільового мікроконтролера цей контракт реалізується низькорівневим драйвером периферії, а при компіляції модульних тестів для робочої станції розробника — спеціальним програмним дублером (моком).

Нижче наведено специфікацію стандартного транзакційного контракту для шин SPI, I2C та GPIO, включаючи синхронні та асинхронні виклики, коди помилок, інваріанти поведінки та реалізацію повнофункціонального мок-об'єкта з інжекцією збоїв.

## 1. Специфікація статусів та кодів помилок

Кожна операція периферійного рівня повертає статус із фіксованого переліку помилок:

| Код статусу | Опис | Умови виникнення |
|---|---|---|
| `HAL_STATUS_OK` | Успішне завершення транзакції | Усі байти передано й прийнято відповідно до протоколу |
| `HAL_STATUS_ERR_PARAM` | Некоректні параметри виклику | Вказівник `NULL`, нульова довжина буфера або неприпустима адреса |
| `HAL_STATUS_ERR_BUSY` | Периферійний модуль зайнятий | Попередня асинхронна транзакція (DMA/IT) ще не завершилася |
| `HAL_STATUS_ERR_TIMEOUT` | Перевищено час очікування | Відповідач не відпустив лінію шини або не виставив прапорець готовності |
| `HAL_STATUS_ERR_NACK` | Відсутнє підтвердження (I2C) | Адресований пристрій не притягнув лінію `SDA` до нуля |
| `HAL_STATUS_ERR_HARDWARE` | Апаратний збій шини | Помилка арбітражу, виявлено замикання або переповнення буфера FIFO |

## 2. Контракт інтерфейсів SPI, I2C та GPIO (C та C++)

Інтерфейс описує повнодуплексні (Full-Duplex) транзакції SPI, операції читання/запису I2C та керування дискретними виводами GPIO.

:::tabs
```c
#ifndef HAL_INTERFACES_CONTRACT_H
#define HAL_INTERFACES_CONTRACT_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef enum {
    HAL_STATUS_OK = 0,
    HAL_STATUS_ERR_PARAM,
    HAL_STATUS_ERR_BUSY,
    HAL_STATUS_ERR_TIMEOUT,
    HAL_STATUS_ERR_NACK,
    HAL_STATUS_ERR_HARDWARE
} hal_status_t;

/* --- Інтерфейс драйвера GPIO --- */
typedef enum {
    HAL_GPIO_PIN_RESET = 0,
    HAL_GPIO_PIN_SET   = 1
} hal_gpio_state_t;

typedef struct hal_gpio_driver {
    void *ctx;
    hal_status_t (*write_pin)(void *ctx, uint16_t pin, hal_gpio_state_t state);
    hal_status_t (*read_pin)(void *ctx, uint16_t pin, hal_gpio_state_t *out_state);
    hal_status_t (*toggle_pin)(void *ctx, uint16_t pin);
} hal_gpio_driver_t;

/* --- Інтерфейс драйвера SPI --- */
typedef struct hal_spi_bus hal_spi_bus_t;
typedef void (*hal_spi_callback_t)(hal_spi_bus_t *bus, hal_status_t status, void *user_ctx);

struct hal_spi_bus {
    void *ctx;
    hal_status_t (*transfer_blocking)(void *ctx,
                                      const uint8_t *tx_buf,
                                      uint8_t *rx_buf,
                                      size_t length,
                                      uint32_t timeout_ms);
    hal_status_t (*transfer_async)(void *ctx,
                                   const uint8_t *tx_buf,
                                   uint8_t *rx_buf,
                                   size_t length,
                                   hal_spi_callback_t callback,
                                   void *user_ctx);
};

/* --- Інтерфейс драйвера I2C --- */
typedef struct hal_i2c_driver {
    void *ctx;
    hal_status_t (*mem_read)(void *ctx,
                             uint16_t dev_addr,
                             uint16_t mem_addr,
                             size_t mem_addr_size,
                             uint8_t *data,
                             size_t length,
                             uint32_t timeout_ms);
    hal_status_t (*master_transmit)(void *ctx,
                                    uint16_t dev_addr,
                                    const uint8_t *data,
                                    size_t length,
                                    uint32_t timeout_ms);
} hal_i2c_driver_t;

#endif /* HAL_INTERFACES_CONTRACT_H */
```
```cpp
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <functional>
#include <chrono>

namespace embedded::hal {

enum class Status : uint8_t {
    Ok = 0,
    InvalidParameter,
    Busy,
    Timeout,
    Nack,
    HardwareFault
};

enum class PinState : uint8_t {
    Reset = 0,
    Set   = 1
};

/* --- Інтерфейс драйвера GPIO --- */
class IGpioDriver {
public:
    virtual ~IGpioDriver() = default;
    virtual Status writePin(uint16_t pin, PinState state) noexcept = 0;
    virtual std::expected<PinState, Status> readPin(uint16_t pin) noexcept = 0;
    virtual Status togglePin(uint16_t pin) noexcept = 0;
};

/* --- Інтерфейс драйвера SPI --- */
using SpiTransferCallback = std::function<void(Status status)>;

class ISpiBus {
public:
    virtual ~ISpiBus() = default;
    virtual Status transferBlocking(std::span<const uint8_t> tx_buf,
                                    std::span<uint8_t> rx_buf,
                                    std::chrono::milliseconds timeout) noexcept = 0;
    virtual Status transferAsync(std::span<const uint8_t> tx_buf,
                                  std::span<uint8_t> rx_buf,
                                  SpiTransferCallback callback) noexcept = 0;
};

/* --- Інтерфейс драйвера I2C --- */
class II2cDriver {
public:
    virtual ~II2cDriver() = default;
    virtual Status memRead(uint16_t dev_addr,
                           uint16_t mem_addr,
                           size_t mem_addr_size,
                           std::span<uint8_t> data,
                           std::chrono::milliseconds timeout) noexcept = 0;
    virtual Status masterTransmit(uint16_t dev_addr,
                                  std::span<const uint8_t> data,
                                  std::chrono::milliseconds timeout) noexcept = 0;
};

} // namespace embedded::hal
```
:::

## 3. Контракт мок-об'єкта: стан, верифікація та інжекція несправностей

Повноцінний мок-об'єкт периферійного драйвера для модульного тестування на хості містить три обов'язкові інженерні механізми:
1. **Журнал транзакцій (Call Record Log):** збереження всіх переданих байтів, адрес та послідовності перемикання ліній для подальшої верифікації в тестових твердженнях.
2. **Емуляція регістрової карти датчика (Stateful Register Emulation):** внутрішній масив або структура, де запис у регістр конфігурації реально змінює стан віртуального пристрою.
3. **Двигун інжекції несправностей (Fault Injection Engine):** можливість налаштувати генерацію помилки на конкретному виклику чи після передачі заданої кількості байтів.

Нижче наведено приклад розумного мок-об'єкта шини I2C для перевірки драйвера барометра BMP280.

:::tabs
```c
#include "hal_interfaces_contract.h"
#include <string.h>

#define MOCK_I2C_MAX_REGS 256

typedef struct {
    uint8_t registers[MOCK_I2C_MAX_REGS];
    uint16_t expected_dev_addr;
    hal_status_t injected_status;
    size_t call_count;
    uint8_t last_written_reg;
    uint8_t last_written_val;
} mock_i2c_context_t;

static hal_status_t mock_i2c_mem_read(void *ctx,
                                      uint16_t dev_addr,
                                      uint16_t mem_addr,
                                      size_t mem_addr_size,
                                      uint8_t *data,
                                      size_t length,
                                      uint32_t timeout_ms) {
    (void)mem_addr_size;
    (void)timeout_ms;
    mock_i2c_context_t *mock = (mock_i2c_context_t *)ctx;
    mock->call_count++;

    if (mock->injected_status != HAL_STATUS_OK) {
        hal_status_t status = mock->injected_status;
        mock->injected_status = HAL_STATUS_OK;
        return status;
    }

    if (dev_addr != mock->expected_dev_addr) {
        return HAL_STATUS_ERR_NACK;
    }

    for (size_t i = 0; i < length; ++i) {
        uint16_t reg_idx = (mem_addr + i) % MOCK_I2C_MAX_REGS;
        data[i] = mock->registers[reg_idx];
    }

    return HAL_STATUS_OK;
}

static hal_status_t mock_i2c_master_transmit(void *ctx,
                                             uint16_t dev_addr,
                                             const uint8_t *data,
                                             size_t length,
                                             uint32_t timeout_ms) {
    (void)timeout_ms;
    mock_i2c_context_t *mock = (mock_i2c_context_t *)ctx;
    mock->call_count++;

    if (mock->injected_status != HAL_STATUS_OK) {
        return mock->injected_status;
    }

    if (dev_addr != mock->expected_dev_addr) {
        return HAL_STATUS_ERR_NACK;
    }

    if (length >= 2) {
        uint8_t reg_addr = data[0];
        uint8_t reg_val = data[1];
        mock->registers[reg_addr] = reg_val;
        mock->last_written_reg = reg_addr;
        mock->last_written_val = reg_val;
    }

    return HAL_STATUS_OK;
}

void mock_i2c_init(mock_i2c_context_t *mock, uint16_t dev_addr, hal_i2c_driver_t *out_driver) {
    memset(mock, 0, sizeof(mock_i2c_context_t));
    mock->expected_dev_addr = dev_addr;
    mock->injected_status = HAL_STATUS_OK;

    out_driver->ctx = mock;
    out_driver->mem_read = mock_i2c_mem_read;
    out_driver->master_transmit = mock_i2c_master_transmit;
}
```
```cpp
#include <vector>
#include <array>

namespace embedded::hal::testing {

class I2cDriverMock final : public II2cDriver {
public:
    explicit I2cDriverMock(uint16_t expected_dev_addr)
        : expected_addr_(expected_dev_addr) {
        registers_.fill(0x00);
    }

    void setRegister(uint8_t reg, uint8_t val) noexcept {
        registers_[reg] = val;
    }

    uint8_t getRegister(uint8_t reg) const noexcept {
        return registers_[reg];
    }

    void injectStatus(Status status) noexcept {
        injected_status_ = status;
    }

    size_t getCallCount() const noexcept { return call_count_; }

    Status memRead(uint16_t dev_addr,
                   uint16_t mem_addr,
                   size_t mem_addr_size,
                   std::span<uint8_t> data,
                   std::chrono::milliseconds timeout) noexcept override {
        (void)mem_addr_size;
        (void)timeout;
        ++call_count_;

        if (injected_status_ != Status::Ok) {
            Status s = injected_status_;
            injected_status_ = Status::Ok;
            return s;
        }

        if (dev_addr != expected_addr_) {
            return Status::Nack;
        }

        for (size_t i = 0; i < data.size(); ++i) {
            uint8_t reg = static_cast<uint8_t>((mem_addr + i) % registers_.size());
            data[i] = registers_[reg];
        }
        return Status::Ok;
    }

    Status masterTransmit(uint16_t dev_addr,
                          std::span<const uint8_t> data,
                          std::chrono::milliseconds timeout) noexcept override {
        (void)timeout;
        ++call_count_;

        if (injected_status_ != Status::Ok) {
            return injected_status_;
        }

        if (dev_addr != expected_addr_) {
            return Status::Nack;
        }

        if (data.size() >= 2) {
            uint8_t reg = data[0];
            uint8_t val = data[1];
            registers_[reg] = val;
        }
        return Status::Ok;
    }

private:
    uint16_t expected_addr_;
    Status injected_status_{Status::Ok};
    size_t call_count_{0};
    std::array<uint8_t, 256> registers_{};
};

} // namespace embedded::hal::testing
```
:::

## 4. Інваріанти та крайові випадки життєвого циклу

При проектуванні абстракцій та роботі з моками на хості необхідно суворо дотримуватися контрактних інваріантів:

1. **Дисципліна керування лінією Chip Select (CS):**
   Під час передачі даних по шині SPI лінія вибору чипа CS переводиться в низький рівень строго перед першим тактовим імпульсом і повертається у високий рівень після завершення транзакції. Якщо функція передачі повертає статус помилки (таймаут або збій шини), мок-об'єкт зобов'язаний переконатися, що лінія CS була коректно звільнена.

2. **Асинхронні зворотні виклики та захист від реентрабельності:**
   У реальному мікроконтролері переривання DMA виникає асинхронно відносно основного коду. Мок-об'єкт на хості не повинен викликати callback-функцію безпосередньо всередині функції `transferAsync`, якщо викликаючий код ще утримує внутрішні м'ютекси або не завершив налаштування дескриптора. Для симуляції асинхронності мок може поміщати виклик у чергу подій або виконувати його за викликом спеціального тестового методу `triggerInterrupt()`.

3. **Гарантії володіння пам'яттю (Buffer Lifetime):**
   Буфери передачі та прийому `tx_buf` і `rx_buf` залишаються заблокованими викликачем до моменту завершення транзакції (повернення з блокуючої функції або виклику асинхронного callback). Драйвер не має права звертатися до буферів після повернення статусу, а викликач не має права змінювати буфери під час активного обміну.

4. **Правила проектування інтерфейсів:**
   - Жодного включення регістрових заголовних файлів мікроконтролера у файлах абстракції.
   - Обов'язкова передача покажчика контексту `void *ctx` у мові C або використання абстрактних інтерфейсних класів у C++ для підтримки кількох однакових пристроїв та повної потокобезпечності.
   - Відсутність динамічного виділення пам'яті (`malloc`/`new`) всередині функцій передачі даних.

## 5. Архітектурні шаблони абстракції: статичний проти динамічного поліморфізму

При реалізації контрактів HAL у вбудованих системах застосовують два принципові підходи до відокремлення апаратури:

1. **Динамічний поліморфізм (Virtual Methods / Function Pointers):**
   Використовує структури з покажчиками на функції в C або абстрактні класи з віртуальними методами в C++.
   - *Переваги:* Дозволяє динамічно підміняти реальний драйвер мок-об'єктом під час виконання без перекомпіляції клієнтського коду. Дозволяє підключати кілька екземплярів пристроїв до різних шин через єдиний покажчик інтерфейсу.
   - *Накладні витрати:* Кожен виклик здійснюється непрямо через таблицю покажчиків (накладні витрати 2–4 такти процесора на ARM Cortex-M), а кожен об'єкт зберігає покажчик на таблицю методів у пам'яті SRAM.

2. **Статичний поліморфізм (C++ Templates / Concepts / C Preprocessor Inlining):**
   Прикладний клас приймає тип драйвера шини як параметр шаблону (`template <typename BusDriver> class SensorDriver`).
   - *Переваги:* Компілятор повністю інлайнить виклики драйвера, усуваючи непрямі переходи та таблиці `vtable`. Витрати пам'яті SRAM дорівнюють нулю. При компіляції під хост передається тип `MockBusDriver`, а під мікроконтролер — `HardwareBusDriver`.
   - *Накладні витрати:* Збільшення розміру коду у Flash-пам'яті при інстанціюванні для різних типів шин та необхідність опису інтерфейсів у заголовних файлах.

## 6. Приклад повного тестового сценарію на базі мок-об'єкта

Нижче наведено приклад модульного тесту на хості, який демонструє перевірку стійкості драйвера барометра BMP280 при інжекції помилки шини I2C.

:::tabs
```c
#include "hal_interfaces_contract.h"
#include <assert.h>
#include <stdio.h>

/* Тестований драйвер барометра */
bool bmp280_read_temperature(hal_i2c_driver_t *i2c, uint16_t addr, int32_t *out_temp) {
    uint8_t raw_data[3] = {0};
    hal_status_t status = i2c->mem_read(i2c->ctx, addr, 0xFA, 1, raw_data, 3, 100);
    if (status != HAL_STATUS_OK) {
        return false;
    }
    *out_temp = ((int32_t)raw_data[0] << 12) | ((int32_t)raw_data[1] << 4) | (raw_data[2] >> 4);
    return true;
}

void test_bmp280_read_success_and_fault_injection(void) {
    mock_i2c_context_t mock_ctx;
    hal_i2c_driver_t i2c_driver;
    mock_i2c_init(&mock_ctx, 0x76, &i2c_driver);

    /* Заповнюємо регістри 0xFA, 0xFB, 0xFC значеннями температури */
    mock_ctx.registers[0xFA] = 0x80;
    mock_ctx.registers[0xFB] = 0x00;
    mock_ctx.registers[0xFC] = 0x00;

    int32_t temperature = 0;
    bool ok = bmp280_read_temperature(&i2c_driver, 0x76, &temperature);
    assert(ok == true);
    assert(temperature == (0x80 << 12));

    /* Інжектуємо апаратний збій таймауту */
    mock_ctx.injected_status = HAL_STATUS_ERR_TIMEOUT;
    ok = bmp280_read_temperature(&i2c_driver, 0x76, &temperature);
    assert(ok == false);
}
```
```cpp
#include "hal_interfaces_contract.hpp"
#include <cassert>

class Bmp280Sensor {
public:
    explicit Bmp280Sensor(embedded::hal::II2cDriver& i2c, uint16_t address)
        : i2c_(i2c), address_(address) {}

    std::expected<int32_t, embedded::hal::Status> readTemperature() {
        std::array<uint8_t, 3> raw_data{};
        auto status = i2c_.memRead(address_, 0xFA, 1, raw_data, std::chrono::milliseconds(100));
        if (status != embedded::hal::Status::Ok) {
            return std::unexpected(status);
        }
        int32_t temp = (static_cast<int32_t>(raw_data[0]) << 12) |
                       (static_cast<int32_t>(raw_data[1]) << 4) |
                       (raw_data[2] >> 4);
        return temp;
    }

private:
    embedded::hal::II2cDriver& i2c_;
    uint16_t address_;
};

void runBmp280Test() {
    embedded::hal::testing::I2cDriverMock mock(0x76);
    mock.setRegister(0xFA, 0x80);
    mock.setRegister(0xFB, 0x00);
    mock.setRegister(0xFC, 0x00);

    Bmp280Sensor sensor(mock, 0x76);

    auto result = sensor.readTemperature();
    assert(result.has_value());
    assert(*result == (0x80 << 12));

    /* Інжектуємо помилку відсутності відповіді NACK */
    mock.injectStatus(embedded::hal::Status::Nack);
    auto failed_result = sensor.readTemperature();
    assert(!failed_result.has_value());
    assert(failed_result.error() == embedded::hal::Status::Nack);
}
```
:::

## 7. Контракт для асинхронного кільцевого буфера DMA та помилок UART

Окрему складність при створенні моків становлять потокові інтерфейси UART, де дані надходять безперервно через апаратний кільцевий буфер DMA (Circular Buffer).

Контракт такого драйвера зобов'язаний регламентувати:
1. **Обробку переривання простою лінії (IDLE Line Interrupt):** Мок повинен надавати метод емуляції паузи в потоці байтів, що спонукає драйвер зчитати накопичені байти без очікування повного заповнення DMA-буфера.
2. **Інжекцію помилок переповнення (Overrun Error, ORE):** Якщо прикладний код не встигає вичитувати кільцевий буфер, мок фіксує переповнення та повертає статус `HAL_STATUS_ERR_HARDWARE`, змушуючи драйвер скинути покажчики голови й хвоста буфера.
3. **Дисципліну бар'єрів пам'яті (Memory Barriers):** При оновленні покажчика запису контролером DMA на реальному чипі потрібна інструкція синхронізації пам'яті `__DMB()`. У хостових тестах правильність черговості оновлення перевіряється потокобезпечними атомарними змінними (`std::atomic<size_t>`).



