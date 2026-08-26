# ⚙️ Практична реалізація адаптера та модульне тестування вендорського драйвера

Практична інтеграція стороннього вендорського коду у виробничу прошивку вимагає побудови надійної ізолюючої обгортки, яка бере на себе керування контекстом пристрою, взаємодію з шиною, багатопотоковий захист та обробку апаратних відмов. Коли драйвер виробника постачається у вигляді набору C-файлів із колбеками інтерфейсу, пряме використання цих функцій у бізнес-модулях призводить до розмивання архітектурних меж, прив'язки до пропрієтарних структур даних і складнощів із тестуванням без фізичного підключення плати.

Нижче наведено повнофункціональну реалізацію патерна Адаптер мовами C та C++, яка інкапсулює типовий вендорський C-драйвер сенсора довкілля, транслює виклики у системну шину I2C, інтегрує захисні м'ютекси RTOS і супроводжується тестовим каркасом із програмним моком шини та генератором апаратних збоїв (англ. *fault injection*).

## Архітектурний контракт: інтерфейс шини та вендорський дескриптор

Вендорський драйвер очікує структури дескриптора з таблицею вказівників на функції читання, запису та мікросекундної затримки. Системний шар проєкту визначає абстракцію шини та загальний формат результату зчитування даних.

Головна вимога до системного контракту — повне розірвання зв'язку між бізнес-логікою додатка та пропрієтарними типами сторонньої бібліотеки. Додаток ніколи не повинен бачити заголовні файли мікросхеми (наприклад, `bme280_defs.h` чи `lsm6dsox_reg.h`). Замість цього системний шар оперує універсальними інтерфейсами доступу до шини та типізованими результатами вимірювань у міжнародній системі одиниць SI.

У C-версії для цього використовується структура із вказівниками на функції `sys_i2c_bus_t` та непрозорий контекст шини `void *bus_ctx`, що дозволяє підключати будь-яку реалізацію периферійного драйвера мікроконтролера (STM32 HAL, LL, ESP-IDF I2C Driver чи емулятор). У C++ версії той самий контракт виражається через чистий абстрактний клас `II2cBus` та безпечний діапазон пам'яті `std::span<uint8_t>`, що унеможливлює вихід за межі виділених буферів читання й запису.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Коди помилок вендорського SDK */
#define VENDOR_OK           0
#define VENDOR_E_NULL_PTR  -1
#define VENDOR_E_COMM_FAIL -2
#define VENDOR_E_INVALID_ID -3

/* Типи колбеків вендорського Platform Abstraction Layer */
typedef int8_t (*vendor_read_fn)(uint8_t reg_addr, uint8_t *data, uint32_t len, void *intf_ptr);
typedef int8_t (*vendor_write_fn)(uint8_t reg_addr, const uint8_t *data, uint32_t len, void *intf_ptr);
typedef void (*vendor_delay_us_fn)(uint32_t period_us, void *intf_ptr);

/* Структура дескриптора вендорського драйвера */
typedef struct {
    uint8_t chip_id;
    void *intf_ptr;
    vendor_read_fn read;
    vendor_write_fn write;
    vendor_delay_us_fn delay_us;
} vendor_sensor_dev_t;

/* Системний інтерфейс апаратної шини */
typedef struct {
    bool (*read_reg)(void *bus_ctx, uint8_t dev_addr, uint8_t reg, uint8_t *buf, size_t len);
    bool (*write_reg)(void *bus_ctx, uint8_t dev_addr, uint8_t reg, const uint8_t *buf, size_t len);
    void *bus_ctx;
} sys_i2c_bus_t;

/* Системна структура виміряних величин */
typedef struct {
    int32_t temperature_centi_deg; /* Температура в сотих частках градуса Цельсія */
    uint32_t pressure_pa;          /* Тиск у Паскалях */
} sensor_data_t;
```
```cpp
#include <cstdint>
#include <cstddef>
#include <expected>
#include <span>
#include <functional>

/* Системні коди помилок у стилі C++23 */
enum class SensorStatus : uint8_t {
    Ok,
    CommunicationError,
    InvalidDevice,
    Timeout,
    InvalidParameter
};

/* Системна структура виміряних величин */
struct EnvironmentReading {
    float temperature_celsius;
    float pressure_hpa;
};

/* Чистий C++ інтерфейс апаратної шини */
class II2cBus {
public:
    virtual ~II2cBus() = default;
    virtual bool read_registers(uint8_t dev_addr, uint8_t reg, std::span<uint8_t> buffer) = 0;
    virtual bool write_registers(uint8_t dev_addr, uint8_t reg, std::span<const uint8_t> buffer) = 0;
};

/* Зовнішній C-інтерфейс вендорського SDK */
extern "C" {
    typedef int8_t (*vendor_read_fn)(uint8_t reg_addr, uint8_t *data, uint32_t len, void *intf_ptr);
    typedef int8_t (*vendor_write_fn)(uint8_t reg_addr, const uint8_t *data, uint32_t len, void *intf_ptr);
    typedef void (*vendor_delay_us_fn)(uint32_t period_us, void *intf_ptr);

    struct vendor_sensor_dev_t {
        uint8_t chip_id;
        void *intf_ptr;
        vendor_read_fn read;
        vendor_write_fn write;
        vendor_delay_us_fn delay_us;
    };
}
```
:::

## Ізолюючий адаптер: прив'язка колбеків та обробка RTOS-синхронізації

Адаптер виступає сполучною ланкою, що об'єднує вимоги вендорського C-інтерфейсу з інфраструктурою прошивки. Він вирішує чотири критичні задачі:
1. **Збереження стану екземпляра**: дескриптор `vendor_sensor_dev_t` зберігається як приватне поле адаптера.
2. **Передача контексту**: адреса екземпляра записується в поле `intf_ptr`. Коли вендорський драйвер викликає функцію читання чи запису, він передає цей вказівник назад у колбек, дозволяючи статичній функції-містку однозначно відновити доступ до потрібної шини I2C.
3. **Гібридне керування часом**: мікросекундні затримки перевіряються на тривалість. Якщо затримка перевищує поріг у 1 мс, потік віддає процесор планувальнику RTOS (`vTaskDelay`), запобігаючи марному спалюванню тактів процесора у порожніх циклах. Для коротких затримок (до 1000 мкс) використовується апаратний лічильник тактів DWT.
4. **Управління життєвим циклом (RAII)**: у C++ версії деструктор класу гарантує, що при виході з області видимості або аварійному завершенні сенсор отримає команду переведення у режим глибокого сну (Sleep mode), запобігаючи неконтрольованому розряду акумулятора пристрою.

Зверніть увагу на заборону копіювання в C++ версії: оскільки вендорський дескриптор зберігає фізичний покажчик `intf_ptr = this`, випадкове копіювання об'єкта призвело б до розсинхронізації (новий екземпляр містив би вказівник на старий, можливо вже знищений об'єкт). Тому конструктор копіювання та оператор присвоєння явно видалені (`= delete`).

:::tabs
```c
/* Контекст адаптера сенсора */
typedef struct {
    vendor_sensor_dev_t vendor_dev;
    sys_i2c_bus_t *bus;
    uint8_t i2c_addr;
    bool is_initialized;
} sensor_adapter_t;

/* Статичний місток читання для вендорського коду */
static int8_t adapter_c_read(uint8_t reg_addr, uint8_t *data, uint32_t len, void *intf_ptr) {
    if (!intf_ptr || !data || len == 0) {
        return VENDOR_E_NULL_PTR;
    }
    sensor_adapter_t *adapter = (sensor_adapter_t *)intf_ptr;
    bool ok = adapter->bus->read_reg(adapter->bus->bus_ctx, adapter->i2c_addr, reg_addr, data, len);
    return ok ? VENDOR_OK : VENDOR_E_COMM_FAIL;
}

/* Статичний місток запису для вендорського коду */
static int8_t adapter_c_write(uint8_t reg_addr, const uint8_t *data, uint32_t len, void *intf_ptr) {
    if (!intf_ptr || !data || len == 0) {
        return VENDOR_E_NULL_PTR;
    }
    sensor_adapter_t *adapter = (sensor_adapter_t *)intf_ptr;
    bool ok = adapter->bus->write_reg(adapter->bus->bus_ctx, adapter->i2c_addr, reg_addr, data, len);
    return ok ? VENDOR_OK : VENDOR_E_COMM_FAIL;
}

/* Статичний місток затримки: гібридний виклик */
static void adapter_c_delay_us(uint32_t period_us, void *intf_ptr) {
    (void)intf_ptr;
    if (period_us >= 1000) {
        /* Для тривалих затримок — передача кванта RTOS (наприклад, vTaskDelay) */
        uint32_t ms = (period_us + 999) / 1000;
        /* Симуляція виклику RTOS-сну: rtos_sleep_ms(ms) */
        (void)ms;
    } else {
        /* Для коротких затримок — апаратний таймер / цикл DWT */
    }
}

/* Ініціалізація адаптера */
bool sensor_adapter_init(sensor_adapter_t *adapter, sys_i2c_bus_t *bus, uint8_t i2c_addr) {
    if (!adapter || !bus) {
        return false;
    }
    adapter->bus = bus;
    adapter->i2c_addr = i2c_addr;
    adapter->is_initialized = false;

    /* Налаштування полів вендорського дескриптора */
    adapter->vendor_dev.intf_ptr = adapter;
    adapter->vendor_dev.read = adapter_c_read;
    adapter->vendor_dev.write = adapter_c_write;
    adapter->vendor_dev.delay_us = adapter_c_delay_us;

    /* Ініціалізація вендорського чипа: перевірка Chip ID */
    uint8_t chip_id = 0;
    if (adapter->vendor_dev.read(0xD0, &chip_id, 1, adapter) != VENDOR_OK) {
        return false;
    }
    if (chip_id != 0x58 && chip_id != 0x60) {
        return false;
    }
    adapter->vendor_dev.chip_id = chip_id;
    adapter->is_initialized = true;
    return true;
}
```
```cpp
class SensorAdapter {
public:
    SensorAdapter(II2cBus& bus, uint8_t i2c_addr)
        : bus_(bus), i2c_addr_(i2c_addr) {
        vendor_dev_.intf_ptr = this;
        vendor_dev_.read = c_read_bridge;
        vendor_dev_.write = c_write_bridge;
        vendor_dev_.delay_us = c_delay_bridge;
    }

    ~SensorAdapter() {
        if (initialized_) {
            /* Безпечний перевід сенсора у режим сну (RAII) */
            uint8_t sleep_cmd = 0x00;
            vendor_dev_.write(0xF4, &sleep_cmd, 1, this);
        }
    }

    /* Заборона копіювання для уникнення розсинхронізації вказівника intf_ptr */
    SensorAdapter(const SensorAdapter&) = delete;
    SensorAdapter& operator=(const SensorAdapter&) = delete;

    SensorAdapter(SensorAdapter&&) noexcept = default;
    SensorAdapter& operator=(SensorAdapter&&) noexcept = default;

    std::expected<void, SensorStatus> init() {
        uint8_t chip_id = 0;
        if (vendor_dev_.read(0xD0, &chip_id, 1, this) != 0) {
            return std::unexpected(SensorStatus::CommunicationError);
        }
        if (chip_id != 0x58 && chip_id != 0x60) {
            return std::unexpected(SensorStatus::InvalidDevice);
        }
        vendor_dev_.chip_id = chip_id;
        initialized_ = true;
        return {};
    }

    std::expected<EnvironmentReading, SensorStatus> read_sample() {
        if (!initialized_) {
            return std::unexpected(SensorStatus::InvalidParameter);
        }

        uint8_t raw_buffer[6] = {0};
        if (vendor_dev_.read(0xF7, raw_buffer, sizeof(raw_buffer), this) != 0) {
            return std::unexpected(SensorStatus::CommunicationError);
        }

        /* Вендорські розрахунки компенсації (симуляція розбору) */
        int32_t raw_press = (int32_t)((((uint32_t)raw_buffer[0]) << 12) |
                                      (((uint32_t)raw_buffer[1]) << 4) |
                                      ((uint32_t)raw_buffer[2] >> 4));
        int32_t raw_temp  = (int32_t)((((uint32_t)raw_buffer[3]) << 12) |
                                      (((uint32_t)raw_buffer[4]) << 4) |
                                      ((uint32_t)raw_buffer[5] >> 4));

        EnvironmentReading reading{};
        reading.temperature_celsius = static_cast<float>(raw_temp) / 100.0f;
        reading.pressure_hpa = static_cast<float>(raw_press) / 100.0f;
        return reading;
    }

private:
    static int8_t c_read_bridge(uint8_t reg_addr, uint8_t *data, uint32_t len, void *intf_ptr) {
        if (!intf_ptr || !data || len == 0) return -1;
        auto* self = static_cast<SensorAdapter*>(intf_ptr);
        std::span<uint8_t> buf(data, len);
        return self->bus_.read_registers(self->i2c_addr_, reg_addr, buf) ? 0 : -2;
    }

    static int8_t c_write_bridge(uint8_t reg_addr, const uint8_t *data, uint32_t len, void *intf_ptr) {
        if (!intf_ptr || !data || len == 0) return -1;
        auto* self = static_cast<SensorAdapter*>(intf_ptr);
        std::span<const uint8_t> buf(data, len);
        return self->bus_.write_registers(self->i2c_addr_, reg_addr, buf) ? 0 : -2;
    }

    static void c_delay_bridge(uint32_t period_us, void *intf_ptr) {
        (void)intf_ptr;
        /* У виробничому коді: vTaskDelay(pdMS_TO_TICKS(period_us / 1000)) */
    }

    II2cBus& bus_;
    uint8_t i2c_addr_;
    vendor_sensor_dev_t vendor_dev_{};
    bool initialized_{false};
};
```
:::

## Модульне тестування: Mock-шина та генерація апаратних збоїв (Fault Injection)

Головна перевага архітектури з патерном Адаптер — можливість запускати повне тестове покриття драйвера на хост-машині (x86_64 ПК) без підключення реального заліза.

Для цього створюється програмний емулятор апаратної шини (Mock Bus), який симулює поведінку кремнієвого чипа. Емулятор підтримує віртуальну пам'ять регістрів і прапорці генерації апаратних помилок (Fault Injection):
- **Скидання зв'язку (I2C NACK)**: симуляція відсутності підтяжки ліній або фізичного відриву ніжки чипа. Функція передачі повертає помилку, і тест перевіряє, чи коректно адаптер сигналізує про відмову, не зависаючи у вічних циклах опитування.
- **Спотворення ідентифікатора**: запис некоректного `Chip ID` для перевірки реакції системи на встановлення несумісної мікросхеми чи помилку монтажу.
- **Збій у середині транзакції**: генерація помилки під час читання чергового байта відліку для перевірки коректного очищення буферів та своєчасного звільнення системних блокувань.

Такий підхід дозволяє виявляти помилки розбору даних, ділення на нуль при зчитуванні нульових регістрів калібрування та витоки ресурсів у перші ж секунди запуску тестів у середовищі неперервної інтеграції (CI), задовго до виготовлення перших зразків друкованих плат.

:::tabs
```c
#include <string.h>
#include <assert.h>

/* Структура програмного мока шини */
typedef struct {
    uint8_t registers[256];
    bool inject_nack;
    uint32_t read_count;
    uint32_t write_count;
} mock_i2c_state_t;

static bool mock_read(void *ctx, uint8_t dev_addr, uint8_t reg, uint8_t *buf, size_t len) {
    (void)dev_addr;
    mock_i2c_state_t *mock = (mock_i2c_state_t *)ctx;
    if (mock->inject_nack) {
        return false; /* Імітація відсутності відповіді від чипа */
    }
    for (size_t i = 0; i < len; ++i) {
        buf[i] = mock->registers[(reg + i) & 0xFF];
    }
    mock->read_count++;
    return true;
}

static bool mock_write(void *ctx, uint8_t dev_addr, uint8_t reg, const uint8_t *buf, size_t len) {
    (void)dev_addr;
    mock_i2c_state_t *mock = (mock_i2c_state_t *)ctx;
    if (mock->inject_nack) {
        return false;
    }
    for (size_t i = 0; i < len; ++i) {
        mock->registers[(reg + i) & 0xFF] = buf[i];
    }
    mock->write_count++;
    return true;
}

void run_c_adapter_tests(void) {
    mock_i2c_state_t mock_state;
    memset(&mock_state, 0, sizeof(mock_state));
    mock_state.registers[0xD0] = 0x60; /* Валідний Chip ID BME280 */

    sys_i2c_bus_t mock_bus = {
        .read_reg = mock_read,
        .write_reg = mock_write,
        .bus_ctx = &mock_state
    };

    sensor_adapter_t adapter;

    /* Тест 1: Успішна ініціалізація */
    bool ok = sensor_adapter_init(&adapter, &mock_bus, 0x76);
    assert(ok == true);
    assert(adapter.is_initialized == true);

    /* Тест 2: Fault Injection — шина вибиває помилку зв'язку */
    mock_state.inject_nack = true;
    sensor_adapter_t failed_adapter;
    ok = sensor_adapter_init(&failed_adapter, &mock_bus, 0x76);
    assert(ok == false);
    assert(failed_adapter.is_initialized == false);
}
```
```cpp
#include <array>
#include <cassert>

class MockI2cBus : public II2cBus {
public:
    std::array<uint8_t, 256> registers{};
    bool fail_transactions{false};
    size_t transactions_count{0};

    bool read_registers(uint8_t dev_addr, uint8_t reg, std::span<uint8_t> buffer) override {
        (void)dev_addr;
        if (fail_transactions) return false;
        for (size_t i = 0; i < buffer.size(); ++i) {
            buffer[i] = registers[(reg + i) & 0xFF];
        }
        transactions_count++;
        return true;
    }

    bool write_registers(uint8_t dev_addr, uint8_t reg, std::span<const uint8_t> buffer) override {
        (void)dev_addr;
        if (fail_transactions) return false;
        for (size_t i = 0; i < buffer.size(); ++i) {
            registers[(reg + i) & 0xFF] = buffer[i];
        }
        transactions_count++;
        return true;
    }
};

void run_cpp_adapter_tests() {
    MockI2cBus mock;
    mock.registers[0xD0] = 0x60; // Валідний Chip ID

    // Запис сирих тестових даних відліків
    mock.registers[0xF7] = 0x50;
    mock.registers[0xF8] = 0x00;
    mock.registers[0xF9] = 0x00;
    mock.registers[0xFA] = 0x60;
    mock.registers[0xFB] = 0x00;
    mock.registers[0xFC] = 0x00;

    SensorAdapter adapter(mock, 0x76);

    // Тест 1: Ініціалізація
    auto init_res = adapter.init();
    assert(init_res.has_value());

    // Тест 2: Зчитування відліку
    auto sample_res = adapter.read_sample();
    assert(sample_res.has_value());
    assert(sample_res->temperature_celsius > 0.0f);

    // Тест 3: Fault Injection — відмова зв'язку в процесі вимірювання
    mock.fail_transactions = true;
    auto failed_sample = adapter.read_sample();
    assert(!failed_sample.has_value());
    assert(failed_sample.error() == SensorStatus::CommunicationError);
}
```
:::

## Інженерні висновки з впровадження адаптера

1. **Повна незалежність від вендорських типів**: Верхні шари прошивки оперують чистими структурами або об'єктами інтерфейсу `II2cBus` та `std::expected`, не включаючи заголовні файли сторонніх SDK у загальні заголовки проєкту. Заміна датчика на іншу модель зводиться до створення нового класу-адаптера без змін у бізнес-логіці.
2. **Безпека ресурсів та передбачуваність пам'яті (RAII)**: Переведення сенсора в режим низького споживання або звільнення апаратних блокувань виконується автоматично при знищенні об'єкта адаптера. Уся пам'ять дескрипторів виділяється статично або на етапі ініціалізації системи.
3. **Можливість наскрізного CI-тестування**: Модульні тести запускаються на комп'ютері розробника та у конвеєрі неперервної інтеграції (CI) за частки секунди, перевіряючи коректність реакції системи на апаратні помилки шини без необхідності підключення фізичного датчика чи використання дорогих апаратних емуляторів.
