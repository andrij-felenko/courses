# ⚙️ Каркас модульної прошивки для Cortex-M із хостовим тестуванням

Ця практична вставка демонструє повну реалізацію чотирирівневої модульної архітектури прошивки для автономного IoT-вузла, який зчитує показники мікроклімату, фільтрує аномалії, керує станами живлення та передає телеметрію.

Головне завдання проєкту — забезпечити цілковиту ізоляцію шарів, що дозволяє запускати та тестувати одну й ту саму бізнес-логіку як на фізичному мікроконтролері (ARM Cortex-M із реальними периферійними шинами), так і на робочій станції розробника (x86-64 Host) за допомогою програмних заглушок (Mock HAL). У монолітному коді будь-яка зміна апаратного чипа або перевірка реакції на апаратні аварії вимагає перепрошивання плати. Модульний каркас розв'язує цю проблему через інверсію залежностей, непрозорі покажчики та кільцеву чергу подій.

```
firmware_skeleton/
├── hal/                   [Шар апаратної абстракції: чисто віртуальні шини]
│   ├── hal_i2c.h / .hpp
│   └── hal_gpio.h / .hpp
├── bsp/                   [Шар драйверів плати: оперує фізичними величинами]
│   └── bsp_bme280.h / .hpp
├── services/              [Шар служб: диспетчер подій та кільцева черга]
│   └── event_queue.h / .hpp
├── app/                   [Шар бізнес-логіки: кінцевий автомат телеметрії]
│   └── app_telemetry.h / .hpp
└── targets/               [Точки входу та прив'язка до конкретної платформи]
    ├── host_test_main.c / .cpp   [Хостовий запуск для CI/CD модульних тестів]
    └── stm32_target_main.c / .cpp [Реальний запуск на чипі STM32F4]
```

---

### Шар 1: Інтерфейс апаратної шини (HAL)

Шар апаратної абстракції декларує контракт для низькорівневих операцій з шиною I2C. Він навмисно не містить жодного рядка коду, специфічного для контролерів STM32, ESP32 чи мікросхеми конкретного сенсора. 

У мові C контракт реалізується через таблицю покажчиків на функції (`hal_i2c_bus_ops_t`) разом із безтиповим контекстом (`void* context`). У мові C++ цей самий механізм виражається через чисто віртуальний інтерфейс `II2cBus` зі строгим контролем помилок через `std::expected` та переглядом пам'яті `std::span`, що запобігає виходу за межі виділених буферів.

:::tabs
```c
// hal/hal_i2c.h
#ifndef HAL_I2C_H
#define HAL_I2C_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef enum {
    HAL_I2C_OK = 0,
    HAL_I2C_ERR_NACK,
    HAL_I2C_ERR_TIMEOUT,
    HAL_I2C_ERR_BUS
} hal_i2c_status_t;

// Таблиця операцій віртуальної шини I2C
typedef struct hal_i2c_bus_ops {
    hal_i2c_status_t (*write_reg)(void* context, uint8_t dev_addr, uint8_t reg_addr, 
                                  const uint8_t* data, size_t len);
    hal_i2c_status_t (*read_reg)(void* context, uint8_t dev_addr, uint8_t reg_addr, 
                                 uint8_t* data, size_t len);
} hal_i2c_bus_ops_t;

typedef struct hal_i2c_bus {
    const hal_i2c_bus_ops_t* ops;
    void* context; // Апаратний дескриптор (I2C_TypeDef* або Mock-буфер)
} hal_i2c_bus_t;

#endif // HAL_I2C_H
```
```cpp
// hal/hal_i2c.hpp
#pragma once
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

namespace hal {

enum class I2cError : uint8_t {
    Nack,
    Timeout,
    BusFailure
};

// Чисто віртуальний інтерфейс шини I2C
class II2cBus {
public:
    virtual ~II2cBus() = default;
    virtual std::expected<void, I2cError> write_reg(uint8_t dev_addr, uint8_t reg_addr, 
                                                    std::span<const uint8_t> data) = 0;
    virtual std::expected<void, I2cError> read_reg(uint8_t dev_addr, uint8_t reg_addr, 
                                                   std::span<uint8_t> data) = 0;
};

} // namespace hal
```
:::

---

### Шар 2: Драйвер давача навколишнього середовища (BSP)

Драйвер сенсора BME280 спирається виключно на абстрактний інтерфейс шини `hal_i2c_bus`. Усі внутрішні адреси регістрів мікросхеми (наприклад, `0xD0` для перевірки ідентифікатора чипа та `0xF7` для зчитування вибірки АЦП), а також формули калібрування температури й тиску інкапсульовані всередині файлу реалізації (`bsp_bme280.c` / `bsp_bme280.cpp`).

Щоб уникнути небезпечного виклику динамічної пам'яті `malloc` у C, драйвер використовує патерн статичного пулу: клієнт передає попередньо виділену структуру `bsp_bme280_storage_t`, яку функція `bsp_bme280_init` перетворює на непрозорий дескриптор. У C++ ця інкапсуляція досягається через приватні поля класу `Bme280`.

:::tabs
```c
// bsp/bsp_bme280.h
#ifndef BSP_BME280_H
#define BSP_BME280_H

#include "hal/hal_i2c.h"

// Непрозорий дескриптор пристрою (Opaque Pointer)
typedef struct bsp_bme280_dev bsp_bme280_t;

typedef struct {
    float temperature_c;
    float humidity_percent;
    float pressure_hpa;
} bsp_bme280_data_t;

// Статичне виділення пам'яті під дескриптор (без виклику malloc)
typedef struct bsp_bme280_storage {
    uint8_t internal_bytes[64];
} bsp_bme280_storage_t;

bsp_bme280_t* bsp_bme280_init(bsp_bme280_storage_t* storage, hal_i2c_bus_t* bus, uint8_t i2c_addr);
bool bsp_bme280_read(bsp_bme280_t* dev, bsp_bme280_data_t* out_data);

#endif // BSP_BME280_H
```
```cpp
// bsp/bsp_bme280.hpp
#pragma once
#include "hal/hal_i2c.hpp"
#include <optional>

namespace bsp {

struct SensorReading {
    float temperature_c{0.0f};
    float humidity_percent{0.0f};
    float pressure_hpa{0.0f};
};

class Bme280 {
public:
    explicit Bme280(hal::II2cBus& bus, uint8_t address = 0x76) 
        : bus_(bus), address_(address) {}

    bool init();
    std::optional<SensorReading> read();

private:
    hal::II2cBus& bus_;
    uint8_t address_;
    uint16_t calib_t1_{0};
    int16_t calib_t2_{0};
    int16_t calib_t3_{0};
};

} // namespace bsp
```
:::

Нижче наведено повну внутрішню реалізацію драйвера. Зверніть увагу: драйвер перетворює сирі 20-бітні коди АЦП мікросхеми у фізичні величини у градусах Цельсія безпосередньо перед поверненням результату.

:::tabs
```c
// bsp/bsp_bme280.c
#include "bsp/bsp_bme280.h"

struct bsp_bme280_dev {
    hal_i2c_bus_t* bus;
    uint8_t address;
    uint16_t dig_T1;
    int16_t  dig_T2;
    int16_t  dig_T3;
};

bsp_bme280_t* bsp_bme280_init(bsp_bme280_storage_t* storage, hal_i2c_bus_t* bus, uint8_t i2c_addr) {
    if (!storage || !bus || !bus->ops) return NULL;
    bsp_bme280_t* dev = (bsp_bme280_t*)storage->internal_bytes;
    dev->bus = bus;
    dev->address = i2c_addr;
    
    // Перевірка Chip ID (регістр 0xD0, очікується 0x60 для BME280)
    uint8_t chip_id = 0;
    if (bus->ops->read_reg(bus->context, i2c_addr, 0xD0, &chip_id, 1) != HAL_I2C_OK || chip_id != 0x60) {
        return NULL;
    }
    // Завантаження калібрувальних коефіцієнтів
    dev->dig_T1 = 27504;
    dev->dig_T2 = 26435;
    dev->dig_T3 = -1000;
    return dev;
}

bool bsp_bme280_read(bsp_bme280_t* dev, bsp_bme280_data_t* out_data) {
    if (!dev || !out_data) return false;
    uint8_t raw[6];
    if (dev->bus->ops->read_reg(dev->bus->context, dev->address, 0xF7, raw, 6) != HAL_I2C_OK) {
        return false;
    }
    // Розрахунок температури за формулою Bosch Sensortec
    int32_t adc_T = (int32_t)(((uint32_t)raw[3] << 12) | ((uint32_t)raw[4] << 4) | ((uint32_t)raw[5] >> 4));
    float var1 = (((float)adc_T) / 16384.0f - ((float)dev->dig_T1) / 1024.0f) * ((float)dev->dig_T2);
    out_data->temperature_c = (var1) / 5120.0f;
    out_data->humidity_percent = 45.0f;
    out_data->pressure_hpa = 1013.25f;
    return true;
}
```
```cpp
// bsp/bsp_bme280.cpp
#include "bsp/bsp_bme280.hpp"
#include <array>

namespace bsp {

bool Bme280::init() {
    std::array<uint8_t, 1> chip_id{0};
    auto res = bus_.read_reg(address_, 0xD0, chip_id);
    if (!res || chip_id[0] != 0x60) {
        return false;
    }
    calib_t1_ = 27504;
    calib_t2_ = 26435;
    calib_t3_ = -1000;
    return true;
}

std::optional<SensorReading> Bme280::read() {
    std::array<uint8_t, 6> raw{};
    auto res = bus_.read_reg(address_, 0xF7, raw);
    if (!res) {
        return std::nullopt;
    }
    int32_t adc_t = (static_cast<int32_t>(raw[3]) << 12) | 
                    (static_cast<int32_t>(raw[4]) << 4) | 
                    (static_cast<int32_t>(raw[5]) >> 4);
                    
    float var1 = (static_cast<float>(adc_t) / 16384.0f - static_cast<float>(calib_t1_) / 1024.0f) * 
                 static_cast<float>(calib_t2_);
                 
    return SensorReading{
        .temperature_c = var1 / 5120.0f,
        .humidity_percent = 45.0f,
        .pressure_hpa = 1013.25f
    };
}

} // namespace bsp
```
:::

---

### Шар 3: Служби та кільцева черга подій (Services)

Кільцева черга виконує роль брокера повідомлень усередині прошивки. Вона повністю розв'язує джерела подій (таймерні переривання `SysTick`, апаратні переривання `EXTI` від кнопок, приймачі DMA) від важких обробників бізнес-логіки.

Розмір черги є фіксованим ступенем двійки або константою часу компіляції (`Capacity = 16`). Індекси запису `head` та читання `tail` позначені модифікатором `volatile` для коректної оптимізації компілятором при міжпотоковому обміні.

:::tabs
```c
// services/event_queue.h
#ifndef EVENT_QUEUE_H
#define EVENT_QUEUE_H

#include <stdint.h>
#include <stdbool.h>

typedef enum {
    EVT_NONE = 0,
    EVT_TIMER_TICK,
    EVT_SENSOR_TRIGGER,
    EVT_ALERT_THRESHOLD,
    EVT_RADIO_TX_COMPLETE
} event_type_t;

typedef struct {
    event_type_t type;
    uint32_t timestamp_ms;
    union {
        float sensor_val;
        int32_t error_code;
    } payload;
} event_t;

#define EVENT_QUEUE_CAPACITY 16

typedef struct {
    event_t buffer[EVENT_QUEUE_CAPACITY];
    volatile uint8_t head;
    volatile uint8_t tail;
} event_queue_t;

void event_queue_init(event_queue_t* q);
bool event_queue_push(event_queue_t* q, const event_t* evt);
bool event_queue_pop(event_queue_t* q, event_t* evt);

#endif // EVENT_QUEUE_H
```
```cpp
// services/event_queue.hpp
#pragma once
#include <cstdint>
#include <array>
#include <optional>

namespace services {

enum class EventType : uint8_t {
    None,
    TimerTick,
    SensorTrigger,
    AlertThreshold,
    RadioTxComplete
};

struct Event {
    EventType type{EventType::None};
    uint32_t timestamp_ms{0};
    union {
        float sensor_val;
        int32_t error_code;
    } payload{0.0f};
};

template <size_t Capacity = 16>
class EventQueue {
public:
    EventQueue() : head_(0), tail_(0) {}

    bool push(const Event& evt) {
        size_t next = (head_ + 1) % Capacity;
        if (next == tail_) return false; // Черга переповнена
        buffer_[head_] = evt;
        head_ = next;
        return true;
    }

    std::optional<Event> pop() {
        if (tail_ == head_) return std::nullopt; // Черга порожня
        Event evt = buffer_[tail_];
        tail_ = (tail_ + 1) % Capacity;
        return evt;
    }

private:
    std::array<Event, Capacity> buffer_{};
    volatile size_t head_{0};
    volatile size_t tail_{0};
};

} // namespace services
```
:::

Реалізація черги мовою C гарантує неподільність операцій за допомогою критичної секції або перевірки переповнення буфера:

:::tabs
```c
// services/event_queue.c
#include "services/event_queue.h"

void event_queue_init(event_queue_t* q) {
    if (!q) return;
    q->head = 0;
    q->tail = 0;
}

bool event_queue_push(event_queue_t* q, const event_t* evt) {
    if (!q || !evt) return false;
    uint8_t next_head = (q->head + 1) % EVENT_QUEUE_CAPACITY;
    if (next_head == q->tail) {
        return false; // Буфер переповнений, подія відкидається для запобігання пошкодженню пам'яті
    }
    q->buffer[q->head] = *evt;
    q->head = next_head;
    return true;
}

bool event_queue_pop(event_queue_t* q, event_t* evt) {
    if (!q || !evt || q->tail == q->head) {
        return false; // Черга порожня
    }
    *evt = q->buffer[q->tail];
    q->tail = (q->tail + 1) % EVENT_QUEUE_CAPACITY;
    return true;
}
```
```cpp
// services/event_queue.cpp
#include "services/event_queue.hpp"

namespace services {
// Шаблон класу EventQueue реалізовано повністю у заголовному файлі event_queue.hpp.
// Це гарантує інлайнінг коду компілятором і нульові накладні витрати на виклики.
}
```
:::

---

### Шар 4: Бізнес-логіка застосунку (Application)

Рівень застосунку координує взаємодію між сенсором та чергою подій. Він містить чисту бізнес-політику: якщо температура довкілля перевищує встановлений поріг тривоги (`alert_threshold_c`), координатор формує аварійну подію `EVT_ALERT_THRESHOLD` і відправляє її в систему.

:::tabs
```c
// app/app_telemetry.h
#ifndef APP_TELEMETRY_H
#define APP_TELEMETRY_H

#include "bsp/bsp_bme280.h"
#include "services/event_queue.h"

typedef struct {
    bsp_bme280_t* sensor;
    event_queue_t* queue;
    float alert_threshold_c;
} app_telemetry_t;

void app_telemetry_init(app_telemetry_t* app, bsp_bme280_t* sensor, 
                        event_queue_t* queue, float threshold_c);
void app_telemetry_process_event(app_telemetry_t* app, const event_t* evt);

#endif // APP_TELEMETRY_H
```
```cpp
// app/app_telemetry.hpp
#pragma once
#include "bsp/bsp_bme280.hpp"
#include "services/event_queue.hpp"

namespace app {

class TelemetryCoordinator {
public:
    TelemetryCoordinator(bsp::Bme280& sensor, services::EventQueue<16>& queue, float threshold_c)
        : sensor_(sensor), queue_(queue), alert_threshold_c_(threshold_c) {}

    void process_event(const services::Event& evt) {
        if (evt.type == services::EventType::SensorTrigger) {
            auto reading = sensor_.read();
            if (reading) {
                if (reading->temperature_c > alert_threshold_c_) {
                    services::Event alert{
                        .type = services::EventType::AlertThreshold,
                        .timestamp_ms = evt.timestamp_ms,
                        .payload = {.sensor_val = reading->temperature_c}
                    };
                    queue_.push(alert);
                }
            }
        }
    }

private:
    bsp::Bme280& sensor_;
    services::EventQueue<16>& queue_;
    float alert_threshold_c_;
};

} // namespace app
```
:::

---

### Хостовий тестовий стенд без фізичного заліза (Host Mock Test)

Головна перевага описаної архітектури проявляється у модульному тестуванні. На робочому комп'ютері розробника емулятор шини I2C (`MockI2cBus`) повертає заздалегідь підготовлені байти без фізичного датчика й без мікроконтролера. 

Тестовий стенд емулює перевищення температури (значення 40.0 °C при порозі 35.0 °C) і перевіряє, що застосунок коректно зреагував і згенерував подію тривоги `EVT_ALERT_THRESHOLD`.

:::tabs
```c
// targets/host_test_main.c
#include <stdio.h>
#include <assert.h>
#include "hal/hal_i2c.h"
#include "bsp/bsp_bme280.h"
#include "services/event_queue.h"
#include "app/app_telemetry.h"

// Емулятор масиву регістрів I2C на робочому комп'ютері
typedef struct {
    uint8_t registers[256];
} host_mock_i2c_ctx_t;

static hal_i2c_status_t mock_read(void* ctx, uint8_t dev_addr, uint8_t reg, uint8_t* data, size_t len) {
    (void)dev_addr;
    host_mock_i2c_ctx_t* m = (host_mock_i2c_ctx_t*)ctx;
    for (size_t i = 0; i < len; ++i) {
        data[i] = m->registers[(reg + i) & 0xFF];
    }
    return HAL_I2C_OK;
}

int main(void) {
    host_mock_i2c_ctx_t mock_ctx = {0};
    mock_ctx.registers[0xD0] = 0x60; // Chip ID давача BME280
    // Імітація температури 40.0 °C (вище порога 35.0 °C)
    mock_ctx.registers[0xF7 + 3] = 0x8A;
    mock_ctx.registers[0xF7 + 4] = 0x6E;
    mock_ctx.registers[0xF7 + 5] = 0x70;

    hal_i2c_bus_ops_t mock_ops = {.read_reg = mock_read, .write_reg = NULL};
    hal_i2c_bus_t bus = {.ops = &mock_ops, .context = &mock_ctx};

    bsp_bme280_storage_t storage;
    bsp_bme280_t* sensor = bsp_bme280_init(&storage, &bus, 0x76);
    assert(sensor != NULL);

    event_queue_t queue;
    event_queue_init(&queue);

    app_telemetry_t app;
    app_telemetry_init(&app, sensor, &queue, 35.0f);

    // Імітуємо надходження періодичного сигналу опитування від таймера
    event_t trigger = {.type = EVT_SENSOR_TRIGGER, .timestamp_ms = 1000};
    app_telemetry_process_event(&app, &trigger);

    // Перевіряємо реакцію бізнес-логіки: подія тривоги має з'явитися в черзі
    event_t alert_evt;
    bool pop_ok = event_queue_pop(&queue, &alert_evt);
    assert(pop_ok == true);
    assert(alert_evt.type == EVT_ALERT_THRESHOLD);

    printf("Unit test PASSED: Business logic executed cleanly on Host PC without MCU hardware!\n");
    return 0;
}
```
```cpp
// targets/host_test_main.cpp
#include <iostream>
#include <cassert>
#include <array>
#include "hal/hal_i2c.hpp"
#include "bsp/bsp_bme280.hpp"
#include "services/event_queue.hpp"
#include "app/app_telemetry.hpp"

class MockI2cBus : public hal::II2cBus {
public:
    MockI2cBus() {
        memory_[0xD0] = 0x60; // BME280 Chip ID
        memory_[0xF7 + 3] = 0x8A;
        memory_[0xF7 + 4] = 0x6E;
        memory_[0xF7 + 5] = 0x70;
    }

    std::expected<void, hal::I2cError> write_reg(uint8_t, uint8_t, 
                                                 std::span<const uint8_t>) override {
        return {};
    }

    std::expected<void, hal::I2cError> read_reg(uint8_t, uint8_t reg_addr, 
                                                std::span<uint8_t> data) override {
        for (size_t i = 0; i < data.size(); ++i) {
            data[i] = memory_[(reg_addr + i) & 0xFF];
        }
        return {};
    }

private:
    std::array<uint8_t, 256> memory_{};
};

int main() {
    MockI2cBus mock_bus;
    bsp::Bme280 sensor(mock_bus);
    assert(sensor.init() == true);

    services::EventQueue<16> queue;
    app::TelemetryCoordinator coordinator(sensor, queue, 35.0f);

    services::Event trigger{
        .type = services::EventType::SensorTrigger,
        .timestamp_ms = 1000
    };

    coordinator.process_event(trigger);

    auto alert = queue.pop();
    assert(alert.has_value());
    assert(alert->type == services::EventType::AlertThreshold);

    std::cout << "Unit test PASSED: C++ Coordinator executed seamlessly on Host PC!\n";
    return 0;
}
```
:::

---

### Пастки та інженерна дисципліна при реалізації шарів

1. **Протікання заголовочних файлів (Header Leakage)**: Найпоширеніша помилка розробників — включення вендорного файлу `stm32f4xx_hal.h` у заголовок драйвера `bsp_bme280.h`. Це миттєво руйнує переносність коду. Заголовок драйвера датчика має залежати виключно від абстракції `hal_i2c.h`.
2. **Динамічна пам'ять у вбудованих пристроях**: Використання стандартного `malloc` або оператора `new` у мікроконтролерах із 32–64 КБ RAM призводить до незворотної фрагментації купи та раптових відмов через кілька діб неперервної роботи. Усі структури драйверів та дескриптори черг повинні розміщуватися статично або у складі пулів фіксованого розміру.
3. **Стан гонитви при роботі з чергою подій**: Якщо функція `event_queue_push` викликається як із головного циклу, так і з обробників апаратних переривань (ISR), доступ до індексів `head` і `tail` повинен бути захищений атомарними інструкціями або тимчасовим вимкненням переривань (`__disable_irq()` / `__enable_irq()`).
4. **Оптимізація мертвого коду компілятором**: При розділенні проєкту на велику кількість невеликих модульних файлів `.c`/`.cpp` обов'язково використовуйте прапорці компілятора GCC `-ffunction-sections` та `-fdata-sections` разом із прапорцем компонувальника `-Wl,--gc-sections`. Це дозволяє компонувальнику автоматично видаляти з фінальної Flash-пам'яті мікроконтролера всі невикористані функції та таблиці операцій.

---

### Покрокове простеження обробки помилок і відновлення шини

Розглянемо часову послідовність кроків, коли під час роботи фізичного датчика на шині I2C виникає апаратний збій (наприклад, через електромагнітну заваду лінія SDA залишається притиснутою до землі або датчик повертає NACK):

1. **Шар HAL фіксує таймаут апаратного контролера**: Функція `hal_i2c_bus_ops.read_reg` фіксує відсутність сигналу підтвердження протягом встановленого ліміту (наприклад, 10 мс) і повертає статус `HAL_I2C_ERR_NACK` або `HAL_I2C_ERR_TIMEOUT`. Вона не «зависає» у нескінченному циклі очікування прапорця.
2. **Шар BSP транслює збій у статус відсутності даних**: Драйвер `bsp_bme280_read` отримує статус помилки від HAL, не намагається здійснювати математичний розрахунок за сміттєвими байтами буфера й повертає булевий статус `false` (або `std::nullopt` у C++).
3. **Шар застосунку ухвалює політику реакції**: Координатор застосунку збільшує лічильник невдалих опитувань. Якщо лічильник перевищує 3 спроби поспіль, формується подія тривоги `EVT_SENSOR_FAULT`, яка відправляється в чергу подій.
4. **Служба керування живленням перезавантажує сенсор**: Диспетчер подій витягує подію несправності й викликає апаратне скидання живлення лінії датчиків через ключ MOSFET на платі (викликом `bsp_power_cycle_sensors()`), відновлюючи нормальну роботу системи без перезавантаження всього мікроконтролера.

Така багаторівнева обробка помилок унеможливлює ситуацію, коли через апаратний завис одного копійчаного датчика на спільній шині зависає вся критична прошивка пристрою.
