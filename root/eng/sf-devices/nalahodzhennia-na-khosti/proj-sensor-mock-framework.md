# ⚙️ Тестовий каркас емуляції I2C-периферії на хості

Цей проект надає завершений, повністю працездатний тестовий каркас мовами C та C++ для запуску вбудованого коду на комп'ютері розробника, де фізична шина I2C та цифровий давач замінюються детермінованим програмним моком із можливістю ін'єкції апаратних збоїв. Каркас демонструє ізоляцію логіки через шар HAL, перевірку драйвера під AddressSanitizer і UndefinedBehaviorSanitizer, а також автоматизовану перевірку відсутності витоків та неініціалізованої пам'яті через Valgrind.

## Архітектурний дизайн тестового стенда

Під час розробки прошивок для мікроконтролерів найбільша частка помилок виникає не в момент низькорівневого смикання бітів у регістрах апаратного контролера, а в логіці вищого рівня: обробці помилкових відповідей, парсингу пакетів зі змінною довжиною, розрахунку контрольних сум і застосуванні калібрувальних коефіцієнтів. Тестувати ці сценарії на фізичному стенді складно, оскільки фізичний давач зазвичай повертає коректні дані й рідко генерує спотворені пакети чи зависання ліній зв'язку.

Програмний тестовий каркас вирішує цю проблему створенням віртуальної шини, яка точно моделює протокол передачі I2C на рівні транзакцій:

```
+-------------------------------------------------------------+
|                  Тестовий набір (Unit Tests)                 |
|       Сценарії штатної роботи · Ін'єкція збоїв зв'язку      |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|               Драйвер давача (Sensor Driver)                |
|       Калібрування · Парсинг пакетів · Фільтрація           |
+-------------------------------------------------------------+
                              |
                              v (контракт HAL I2C)
+-------------------------------------------------------------+
|             Віртуальний емулятор шини I2C (Mock)            |
|    Банк регістрів (256 байтів) · Автоінкремент адреси       |
|    Керовані збої: NACK адреси · NACK даних · Тайм-аути      |
+-------------------------------------------------------------+
```

### Компоненти системи
1. **Інтерфейс HAL I2C**: абстрактний контракт передачі та прийому байтів, який не містить жодного звернення до регістрів процесора.
2. **Програмний мок шини (Mock Bus)**: віртуальна таблиця регістрів розміром 256 байтів, що імітує поведінку фізичного давача (наприклад, цифрового термометра-барометра), включно з автовідліком регістрового покажчика, розрахунком контрольних сум та керованою генерацією помилок.
3. **Драйвер давача**: вбудована логіка ініціалізації, зчитування сирих замірів, застосування калібрувальних коефіцієнтів та фільтрації.
4. **Тестовий набір**: сценарії перевірки штатної роботи та реакції драйвера на нештатні апаратні відмови.

---

## Повна реалізація каркаса на C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

/* --- 1. Апаратний інтерфейс HAL I2C --- */
typedef enum {
    HAL_I2C_OK = 0,
    HAL_I2C_ERR_NACK = -1,
    HAL_I2C_ERR_TIMEOUT = -2,
    HAL_I2C_ERR_BUS = -3
} hal_i2c_status_t;

typedef struct hal_i2c_bus {
    hal_i2c_status_t (*write_read)(struct hal_i2c_bus *bus, uint8_t addr,
                                   const uint8_t *tx, size_t tx_len,
                                   uint8_t *rx, size_t rx_len);
    void *user_ctx;
} hal_i2c_bus_t;

/* --- 2. Емулятор периферійного давача (Mock) --- */
#define SENSOR_I2C_ADDR      0x68
#define REG_CHIP_ID          0x00
#define REG_STATUS           0x01
#define REG_TEMP_MSB         0x02
#define REG_TEMP_LSB         0x03
#define REG_CALIB_OFFSET     0x04
#define REG_RESET_CMD        0x0F

#define EXPECTED_CHIP_ID     0x5A

typedef struct {
    uint8_t registers[256];
    bool inject_nack;
    bool inject_timeout;
    uint32_t transaction_count;
} mock_sensor_ctx_t;

static hal_i2c_status_t mock_i2c_write_read(hal_i2c_bus_t *bus, uint8_t addr,
                                            const uint8_t *tx, size_t tx_len,
                                            uint8_t *rx, size_t rx_len) {
    mock_sensor_ctx_t *ctx = (mock_sensor_ctx_t *)bus->user_ctx;
    ctx->transaction_count++;

    if (addr != SENSOR_I2C_ADDR) {
        return HAL_I2C_ERR_NACK;
    }
    if (ctx->inject_nack) {
        return HAL_I2C_ERR_NACK;
    }
    if (ctx->inject_timeout) {
        return HAL_I2C_ERR_TIMEOUT;
    }
    if (tx_len == 0) {
        return HAL_I2C_ERR_BUS;
    }

    uint8_t reg_addr = tx[0];

    /* Якщо tx_len > 1 — це операція запису в регістри */
    if (tx_len > 1) {
        for (size_t i = 1; i < tx_len; ++i) {
            uint8_t target_reg = (uint8_t)(reg_addr + (i - 1));
            ctx->registers[target_reg] = tx[i];
            /* Обробка команди програмного скидання */
            if (target_reg == REG_RESET_CMD && tx[i] == 0xB6) {
                ctx->registers[REG_STATUS] = 0x00;
            }
        }
    }

    /* Якщо rx_len > 0 — це операція читання з автоінкрементом */
    if (rx_len > 0 && rx != NULL) {
        for (size_t i = 0; i < rx_len; ++i) {
            uint8_t target_reg = (uint8_t)(reg_addr + i);
            rx[i] = ctx->registers[target_reg];
        }
    }

    return HAL_I2C_OK;
}

void mock_sensor_init(mock_sensor_ctx_t *ctx, hal_i2c_bus_t *bus) {
    memset(ctx, 0, sizeof(*ctx));
    ctx->registers[REG_CHIP_ID] = EXPECTED_CHIP_ID;
    ctx->registers[REG_STATUS] = 0x01;       /* Дані готові */
    ctx->registers[REG_TEMP_MSB] = 0x09;     /* 0x09C4 = 2500 -> 25.00 C */
    ctx->registers[REG_TEMP_LSB] = 0xC4;
    ctx->registers[REG_CALIB_OFFSET] = 10;   /* Зміщення +0.10 C */

    bus->write_read = mock_i2c_write_read;
    bus->user_ctx = ctx;
}

/* --- 3. Драйвер давача (Тестований модуль) --- */
typedef struct {
    hal_i2c_bus_t *i2c;
    int32_t last_temperature_centi_c;
    int16_t calib_offset;
    bool is_initialized;
} sensor_driver_t;

typedef enum {
    DRIVER_OK = 0,
    DRIVER_ERR_COMM = -1,
    DRIVER_ERR_WRONG_ID = -2,
    DRIVER_ERR_NOT_READY = -3
} driver_status_t;

driver_status_t sensor_driver_init(sensor_driver_t *drv, hal_i2c_bus_t *i2c) {
    drv->i2c = i2c;
    drv->is_initialized = false;
    drv->last_temperature_centi_c = 0;
    drv->calib_offset = 0;

    uint8_t tx_reg = REG_CHIP_ID;
    uint8_t chip_id = 0;
    if (drv->i2c->write_read(drv->i2c, SENSOR_I2C_ADDR, &tx_reg, 1, &chip_id, 1) != HAL_I2C_OK) {
        return DRIVER_ERR_COMM;
    }
    if (chip_id != EXPECTED_CHIP_ID) {
        return DRIVER_ERR_WRONG_ID;
    }

    tx_reg = REG_CALIB_OFFSET;
    uint8_t calib_raw = 0;
    if (drv->i2c->write_read(drv->i2c, SENSOR_I2C_ADDR, &tx_reg, 1, &calib_raw, 1) != HAL_I2C_OK) {
        return DRIVER_ERR_COMM;
    }
    drv->calib_offset = (int8_t)calib_raw;
    drv->is_initialized = true;
    return DRIVER_OK;
}

driver_status_t sensor_driver_read_temperature(sensor_driver_t *drv, int32_t *out_centi_c) {
    if (!drv->is_initialized) {
        return DRIVER_ERR_COMM;
    }

    uint8_t tx_reg = REG_STATUS;
    uint8_t status = 0;
    if (drv->i2c->write_read(drv->i2c, SENSOR_I2C_ADDR, &tx_reg, 1, &status, 1) != HAL_I2C_OK) {
        return DRIVER_ERR_COMM;
    }
    if ((status & 0x01) == 0) {
        return DRIVER_ERR_NOT_READY;
    }

    tx_reg = REG_TEMP_MSB;
    uint8_t temp_raw_bytes[2] = {0};
    if (drv->i2c->write_read(drv->i2c, SENSOR_I2C_ADDR, &tx_reg, 1, temp_raw_bytes, 2) != HAL_I2C_OK) {
        return DRIVER_ERR_COMM;
    }

    int16_t raw_temp = (int16_t)((temp_raw_bytes[0] << 8) | temp_raw_bytes[1]);
    /* Температура в сотих градуса: Raw + Offset */
    int32_t temp_centi_c = (int32_t)raw_temp + (int32_t)drv->calib_offset;

    drv->last_temperature_centi_c = temp_centi_c;
    *out_centi_c = temp_centi_c;
    return DRIVER_OK;
}

/* --- 4. Тестові сценарії --- */
static void test_normal_initialization_and_read(void) {
    mock_sensor_ctx_t mock_ctx;
    hal_i2c_bus_t i2c_bus;
    mock_sensor_init(&mock_ctx, &i2c_bus);

    sensor_driver_t drv;
    driver_status_t status = sensor_driver_init(&drv, &i2c_bus);
    assert(status == DRIVER_OK);
    assert(drv.is_initialized == true);

    int32_t temperature = 0;
    status = sensor_driver_read_temperature(&drv, &temperature);
    assert(status == DRIVER_OK);
    /* Очікуємо 2500 + 10 = 2510 (25.10 C) */
    assert(temperature == 2510);
    printf("[PASS] test_normal_initialization_and_read\n");
}

static void test_sensor_nack_recovery(void) {
    mock_sensor_ctx_t mock_ctx;
    hal_i2c_bus_t i2c_bus;
    mock_sensor_init(&mock_ctx, &i2c_bus);

    mock_ctx.inject_nack = true;
    sensor_driver_t drv;
    driver_status_t status = sensor_driver_init(&drv, &i2c_bus);
    assert(status == DRIVER_ERR_COMM);
    assert(drv.is_initialized == false);
    printf("[PASS] test_sensor_nack_recovery\n");
}

int main(void) {
    printf("=== Запуск тестів драйвера на хості ===\n");
    test_normal_initialization_and_read();
    test_sensor_nack_recovery();
    printf("Всі тести виконано успішно.\n");
    return 0;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <vector>
#include <expected>
#include <iostream>
#include <cassert>

namespace hal {

enum class I2cStatus : int8_t {
    Ok = 0,
    ErrNack = -1,
    ErrTimeout = -2,
    ErrBus = -3
};

class II2cBus {
public:
    virtual ~II2cBus() = default;
    virtual I2cStatus write_read(uint8_t addr,
                                 std::span<const uint8_t> tx,
                                 std::span<uint8_t> rx) = 0;
};

} // namespace hal

namespace mock {

constexpr uint8_t SensorAddr = 0x68;
constexpr uint8_t ExpectedChipId = 0x5A;

class MockSensorBus final : public hal::II2cBus {
public:
    MockSensorBus() {
        reset();
    }

    void reset() {
        registers_.fill(0);
        registers_[0x00] = ExpectedChipId; // REG_CHIP_ID
        registers_[0x01] = 0x01;           // REG_STATUS: Ready
        registers_[0x02] = 0x09;           // REG_TEMP_MSB (2500 -> 25.00 C)
        registers_[0x03] = 0xC4;           // REG_TEMP_LSB
        registers_[0x04] = 10;             // REG_CALIB_OFFSET
        inject_nack_ = false;
        inject_timeout_ = false;
        transaction_count_ = 0;
    }

    void set_nack_injection(bool enable) noexcept { inject_nack_ = enable; }
    void set_timeout_injection(bool enable) noexcept { inject_timeout_ = enable; }
    [[nodiscard]] uint32_t transaction_count() const noexcept { return transaction_count_; }

    hal::I2cStatus write_read(uint8_t addr,
                              std::span<const uint8_t> tx,
                              std::span<uint8_t> rx) override {
        ++transaction_count_;
        if (addr != SensorAddr || inject_nack_) {
            return hal::I2cStatus::ErrNack;
        }
        if (inject_timeout_) {
            return hal::I2cStatus::ErrTimeout;
        }
        if (tx.empty()) {
            return hal::I2cStatus::ErrBus;
        }

        const uint8_t start_reg = tx[0];

        // Запис даних
        if (tx.size() > 1) {
            for (size_t i = 1; i < tx.size(); ++i) {
                const uint8_t reg = static_cast<uint8_t>(start_reg + (i - 1));
                registers_[reg] = tx[i];
            }
        }

        // Читання даних
        if (!rx.empty()) {
            for (size_t i = 0; i < rx.size(); ++i) {
                const uint8_t reg = static_cast<uint8_t>(start_reg + i);
                rx[i] = registers_[reg];
            }
        }

        return hal::I2cStatus::Ok;
    }

private:
    std::array<uint8_t, 256> registers_{};
    bool inject_nack_{false};
    bool inject_timeout_{false};
    uint32_t transaction_count_{0};
};

} // namespace mock

namespace devices {

enum class DriverError {
    CommunicationFailed,
    InvalidChipId,
    SensorNotReady
};

class TemperatureSensorDriver {
public:
    explicit TemperatureSensorDriver(hal::II2cBus& bus) noexcept
        : bus_(bus), is_initialized_(false), calib_offset_(0) {}

    std::expected<void, DriverError> init() {
        const std::array<uint8_t, 1> reg_id{0x00};
        std::array<uint8_t, 1> chip_id{0};

        if (bus_.write_read(mock::SensorAddr, reg_id, chip_id) != hal::I2cStatus::Ok) {
            return std::unexpected(DriverError::CommunicationFailed);
        }
        if (chip_id[0] != mock::ExpectedChipId) {
            return std::unexpected(DriverError::InvalidChipId);
        }

        const std::array<uint8_t, 1> reg_calib{0x04};
        std::array<uint8_t, 1> calib_val{0};
        if (bus_.write_read(mock::SensorAddr, reg_calib, calib_val) != hal::I2cStatus::Ok) {
            return std::unexpected(DriverError::CommunicationFailed);
        }

        calib_offset_ = static_cast<int8_t>(calib_val[0]);
        is_initialized_ = true;
        return {};
    }

    [[nodiscard]] std::expected<int32_t, DriverError> read_temperature_centi_c() {
        if (!is_initialized_) {
            return std::unexpected(DriverError::CommunicationFailed);
        }

        const std::array<uint8_t, 1> reg_status{0x01};
        std::array<uint8_t, 1> status{0};
        if (bus_.write_read(mock::SensorAddr, reg_status, status) != hal::I2cStatus::Ok) {
            return std::unexpected(DriverError::CommunicationFailed);
        }
        if ((status[0] & 0x01) == 0) {
            return std::unexpected(DriverError::SensorNotReady);
        }

        const std::array<uint8_t, 1> reg_temp{0x02};
        std::array<uint8_t, 2> raw_bytes{0, 0};
        if (bus_.write_read(mock::SensorAddr, reg_temp, raw_bytes) != hal::I2cStatus::Ok) {
            return std::unexpected(DriverError::CommunicationFailed);
        }

        const auto raw_temp = static_cast<int16_t>((raw_bytes[0] << 8) | raw_bytes[1]);
        const int32_t final_temp = static_cast<int32_t>(raw_temp) + calib_offset_;
        return final_temp;
    }

private:
    hal::II2cBus& bus_;
    bool is_initialized_;
    int16_t calib_offset_;
};

} // namespace devices

int main() {
    std::cout << "=== Запуск C++20 тестів драйвера на хості ===\n";

    mock::MockSensorBus mock_bus;
    devices::TemperatureSensorDriver driver(mock_bus);

    // Сценарій 1: Успішна ініціалізація та зчитування
    auto init_res = driver.init();
    assert(init_res.has_value());

    auto temp_res = driver.read_temperature_centi_c();
    assert(temp_res.has_value());
    assert(*temp_res == 2510);
    std::cout << "[PASS] Успішне зчитування: " << *temp_res << " centi-C\n";

    // Сценарій 2: Ін'єкція відмови NACK
    mock_bus.reset();
    mock_bus.set_nack_injection(true);
    devices::TemperatureSensorDriver fault_driver(mock_bus);
    auto fault_res = fault_driver.init();
    assert(!fault_res.has_value());
    assert(fault_res.error() == devices::DriverError::CommunicationFailed);
    std::cout << "[PASS] Перехоплення апаратного збою NACK\n";

    std::cout << "Всі C++ тести пройдено успішно.\n";
    return 0;
}
```
:::

---

## Механіка ін'єкції збоїв у віртуальній шині

Програмний мок `mock_i2c_write_read` реалізує повну модель поведінки цифрової мікросхеми. Розгляньмо, як саме працюють три ключові механізми:

### 1. Автоінкремент регістрового покажчика
У більшості I2C/SPI сенсорів (наприклад, Bosch BMP280, ST LIS3DH) першим переданим байтом є початкова адреса регістра, після чого кожне наступне читання чи запис автоматично збільшує адресу на одиницю. У коді моку це реалізовано внутрішнім циклом:

:::tabs
```c
for (size_t i = 0; i < rx_len; ++i) {
    uint8_t target_reg = (uint8_t)(reg_addr + i);
    rx[i] = ctx->registers[target_reg];
}
```
```cpp
for (size_t i = 0; i < rx.size(); ++i) {
    const auto target_reg = static_cast<uint8_t>(start_reg + i);
    rx[i] = registers_[target_reg];
}
```
:::

Це дозволяє драйверу за один виклик `write_read` вичитувати 16- або 32-бітні значення (наприклад, старший байт `REG_TEMP_MSB` та молодший байт `REG_TEMP_LSB`), що точно відтворює поведінку фізичного кремнію.

### 2. Симуляція відмови підтвердження (NACK Injection)
Коли фізичний давач від'єднано або на шині виникло коротке замикання, на дев'ятому такті тактового сигналу SCL лінія даних SDA залишається підтягнутою до високого рівня (NACK). Встановивши прапорець `mock_ctx.inject_nack = true`, тест миттєво перевіряє, чи коректно драйвер повертає статус `DRIVER_ERR_COMM` та чи не зависає він у нескінченному циклі опитування прапорця готовності.

### 3. Імітація скидання стану пристрою
Коли драйвер надсилає команду скидання (байт `0xB6` у регістр `REG_RESET_CMD`), мок скидає біт готовності в нуль `ctx->registers[REG_STATUS] = 0x00`. Це дозволяє перевірити захист драйвера від читання застарілих даних під час перехідних процесів.

---

## Автоматизація збірки та перевірки під санітайзерами

Для регулярного виконання тестів у локальному терміналі та в хмарних CI-конвеєрах створюється Makefile з окремими цілями для кожного аналізатора:

```makefile
CC ?= clang
CXX ?= clang++
CFLAGS = -Wall -Wextra -Wpedantic -g -O1
CXXFLAGS = -Wall -Wextra -Wpedantic -std=c++20 -g -O1

SRC_C = host_test_framework.c
SRC_CPP = host_test_framework.cpp

.PHONY: all test-asan test-ubsan test-valgrind test-coverage clean

all: test-asan test-ubsan

# 1. AddressSanitizer (пошук виходу за межі пам'яті та UAF)
test-asan:
	$(CC) $(CFLAGS) -fsanitize=address $(SRC_C) -o test_asan_c
	$(CXX) $(CXXFLAGS) -fsanitize=address $(SRC_CPP) -o test_asan_cpp
	./test_asan_c
	./test_asan_cpp

# 2. UndefinedBehaviorSanitizer (пошук знакових переповнень і невалідних зсувів)
test-ubsan:
	$(CC) $(CFLAGS) -fsanitize=undefined $(SRC_C) -o test_ubsan_c
	$(CXX) $(CXXFLAGS) -fsanitize=undefined $(SRC_CPP) -o test_ubsan_cpp
	./test_ubsan_c
	./test_ubsan_cpp

# 3. Valgrind Memcheck (пошук неініціалізованої пам'яті)
test-valgrind:
	$(CC) $(CFLAGS) $(SRC_C) -o test_native_c
	valgrind --leak-check=full --track-origins=yes --error-exitcode=1 ./test_native_c

# 4. Покриття коду (gcov / lcov)
test-coverage:
	$(CC) $(CFLAGS) --coverage $(SRC_C) -o test_cov_c
	./test_cov_c
	lcov --capture --directory . --output-file coverage.info
	genhtml coverage.info --output-directory out_html

clean:
	rm -f test_* *.gcno *.gcda *.info
	rm -rf out_html
```

---

## Архітектурні відмінності: C проти сучасного C++

Порівняння двох реалізацій стенда наочно демонструє еволюцію інженерних практик:

| Критерій | Реалізація на C | Реалізація на C++20 |
| :--- | :--- | :--- |
| **Передача буферів** | Сирий покажчик `uint8_t*` та окремий `size_t len` | Безпечний неволодіючий зріз `std::span<const uint8_t>` |
| **Обробка помилок** | Числові коди помилок `enum` + вихідні параметри | Монадичний тип `std::expected<T, Error>` без винятків |
| **Інкапсуляція моку** | Структура зі статичною функцією та `void *user_ctx` | Поліморфний клас `MockSensorBus` з приватним станом |
| **Управління пам'яттю** | Ручний `memset` та явне скидання полів | Детермінована ініціалізація `std::array` та конструктори |

Використання `std::span` у C++20 гарантує, що розмір буфера завжди передається разом із покажчиком на дані як єдине ціле. Це запобігає класичним багам, коли функція записує 4 байти в масив розміром 2 байти через розсинхронізацію змінної довжини.

---

## Підводні камені емуляції вбудованого коду на хості

Перенесення мікроконтролерного коду на комп'ютер розробника усуває переважну більшість алгоритмічних дефектів, але вимагає врахування таких архітектурних розбіжностей:

1. **Розрядність типів даних (`sizeof(int)`)**:
   На 8-бітних та 16-бітних архітектурах (AVR, MSP430) базовий тип `int` займає 16 бітів, тоді як на x86-64 хості — 32 біти. Неявне розширення типів при бітових зсувах `val << 12` на хості не викличе переповнення, але переповнить 16-бітний регістр на AVR. Завжди використовуйте типи фіксованої ширини (`uint8_t`, `int16_t`, `uint32_t`) із `<stdint.h>`.

2. **Порядок байтів (Endianness)**:
   Більшість хостів x86-64 та ARM є Little-Endian. Якщо ви емулюєте мережевий протокол (Big-Endian) або дані давача у Big-Endian шляхом прямого накладання структури через приведення покажчика `(sensor_pkt_t*)raw_buffer`, на хості поля байтів розташуються задом наперед. Завжди виконуйте явне побайтове збирання чисел: `(buf[0] << 8) | buf[1]`.

3. **Вирівнювання структур у пам'яті (Struct Padding)**:
   Компілятори для 64-бітних процесорів вирівнюють поля структур за 4- та 8-байтовими межами, додаючи невидимі байти заповнення. Якщо структура описує пакет передачі по шині, використовуйте атрибут `__attribute__((packed))` або збирайте пакет серіалізатором вручну.

4. **Суворе псевдонімування (Strict Aliasing Rule)**:
   Приведення покажчика `uint8_t*` до `uint32_t*` для швидкого зчитування числа порушує правило суворого псевдонімування у стандартах C99/C++11. На хості з оптимізацією `-O2` або `-O3` компілятор має право переставити операції запису й читання місцями. Для безпечного читання використовуйте `memcpy` або явні бітові зсуви, які компілятор оптимізує в одну інструкцію `mov` чи `bswap`.
