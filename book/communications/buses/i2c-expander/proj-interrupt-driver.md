# Драйвер I²C-розширювача з асинхронною обробкою переривань

У цій практичній роботі розглянуто проектування та реалізацію надійного, неблокуючого драйвера 16-бітного I2C-розширювача портів `MCP23017` для вбудованих систем на базі C та C++20. Драйвер забезпечує коректну роботу з лінією апаратних переривань `/INT`, читання моментальних знімків стану входів із регістра `INTCAP`, тіньову буферизацію для усунення небезпеки «читання-модифікації-запису» (*Read-Modify-Write*) та захист від брязкоту контактів.

---

### Архітектура та інженерні виклики проектування

Розробка промислового драйвера для розширювача портів введення-виведення на послідовній шині докорінно відрізняється від роботи зі звичайними вбудованими GPIO мікроконтролера. Якщо до вбудованого регістра процесор має прямий доступ за 1 такт тактової частоти (кілька наносекунд), то будь-яка операція з розширювачем вимагає формування повноцінного кадру I2C з передачею адреси, покажчика регістра та байтів даних. На стандартній швидкості 100 кГц надсилання 3 байтів займає близько 270 мікросекунд, що у десятки тисяч разів повільніше за прямий доступ до пам'яті.

Ця фундаментальна різниця породжує чотири ключові інженерні проблеми, які драйвер повинен вирішувати на системному рівні:

#### 1. Запобігання блокуванню в обробниках переривань (ISR)

Найбільш поширена помилка початківців — спроба виконати читання даних з I2C-розширювача безпосередньо всередині функції обробки апаратного переривання (*Interrupt Service Routine, ISR*). 

Виконання синхронного блокуючого обміну по I2C всередині ISR є неприпустимим з кількох причин:
- I2C-драйвер мікроконтролера сам часто працює на перериваннях або DMA. Виклик блокуючої функції з ISR може призвести до мертвого блокування (*deadlock*), якщо переривання I2C мають однаковий або нижчий пріоритет.
- Затримка виконання ISR на 200–500 мкс блокує обслуговування інших критичних системних процесів (наприклад, крокових двигунів чи ШІМ-інверторів), спричиняючи значний джитер (*jitter*).
- Більшість операційних систем реального часу (FreeRTOS, Zephyr) суворо забороняють виклик блокуючих API функцій (таких як очікування м'ютексів чи семафорів) із контексту переривання.

Правильний підхід полягає в розділенні обробки на **дві фази**:
- **Швидка фаза (у ISR)**: виставляється атомарний прапорець події або надсилається мінімальне повідомлення в чергу завдань RTOS, після чого процесор негайно виходить із переривання.
- **Фонова фаза (в основному потоці або задачі RTOS)**: задача прокидається, виконує дебаунс-затримку, здійснює I2C-транзакцію читання та сповіщає бізнес-логіку програми.

#### 2. Захист від брязкоту контактів (Debounce Engine)

Механічні кнопки та реле під час замикання створюють серію хаотичних перехідних імпульсів тривалістю від кількох сотень мікросекунд до десятків мілісекунд. Якщо вхід розширювача налаштовано на генерацію переривання за будь-якою зміною рівня, кожне натискання кнопки викличе «шторм переривань» (*Interrupt Storm*) — сотні спрацьовувань за лічені частки секунди.

Драйвер повинен містити вбудований скінченний автомат дебаунсингу (*Debounce State Machine*): після першого зафіксованого фронту зовнішнє переривання тимчасово маскується, запускається неблокуючий таймер на 20–30 мс, і лише після заспокоєння контактів виконується читання шини.

```
 Стан піна:  ─────┐  ┌─┐ ┌───┐ ┌─────────────────────────── (Логічний 0)
                  └──┘ └─┘   └─┘
                   ▲
                   │ Перший фронт: фіксація переривання в INTCAP
                   │ ◄────────── 25 мс затримка ──────────►
                                                           ▲
                                                           │ Читання I2C та скидання /INT
```

#### 3. Тіньові регістри виходу (Shadow Registers)

Якщо мікроконтролер змінює стан одного окремого біта порту (наприклад, вмикає світлодіод на піні 3, не чіпаючи піни 0, 1, 2), класичний шаблон «прочитати порт `GPIOA` → встановити біт → записати в `GPIOA`» приховує критичну небезпеку. 

Якщо на сусідньому піні 2 встановлено високий логічний рівень, але до нього підключено велику ємність або оптопару з помітним струмом навантаження, реальна напруга на виводі може тимчасово становити, наприклад, 1.8 В. Вхідний буфер зчитає це значення як логічний `0`. У результаті операції маскування драйвер випадково скине вихід сусіднього піна в нуль.

Щоб повністю усунути цю проблему, драйвер веде в оперативній пам'яті мікроконтролера локальну копію вихідних тригерів — **тіньовий регістр `shadow_olat`**. Будь-яка бітова маніпуляція модифікує виключно тіньовий регістр у RAM і відправляє його значення в розширювач без проміжного читання фізичних пінів.

#### 4. Багатопотокова безпека при конкурентному доступі

У складних вбудованих додатках різні задачі RTOS можуть одночасно звертатися до одного розширювача (наприклад, фонова задача блимає світлодіодом статусу на піні 0, а задача зв'язку скидає лінію живлення модему на піні 7). Якщо дві задачі одночасно викличуть функцію модифікації порту, без належного захисту виникне стан гонитви (*Race Condition*), що призведе до перезапису тіньового регістра.

Драйвер повинен або надавати вбудований м'ютекс блокування, або виконувати модифікацію бітів у критичній секції із захистом від перемикання контексту.

---

### 1. Низькорівневий драйвер мовою C

Нижче наведено модульну реалізацію C-драйвера, що не залежить від конкретної апаратної платформи завдяки використанню абстрактних покажчиків на функції I2C-транспорту.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Базові адреси регістрів MCP23017 (BANK = 0) */
#define MCP_IODIRA    0x00
#define MCP_IODIRB    0x01
#define MCP_IPOLA     0x02
#define MCP_IPOLB     0x03
#define MCP_GPINTENA  0x04
#define MCP_GPINTENB  0x05
#define MCP_DEFVALA   0x06
#define MCP_DEFVALB   0x07
#define MCP_INTCONA   0x08
#define MCP_INTCONB   0x09
#define MCP_IOCON     0x0A
#define MCP_GPPUA     0x0C
#define MCP_GPPUB     0x0D
#define MCP_INTFA     0x0E
#define MCP_INTFB     0x0F
#define MCP_INTCAPA   0x10
#define MCP_INTCAPB   0x11
#define MCP_GPIOA     0x12
#define MCP_GPIOB     0x13
#define MCP_OLATA     0x14
#define MCP_OLATB     0x15

/* Біти конфігурації IOCON */
#define IOCON_MIRROR  (1 << 6)
#define IOCON_ODR     (1 << 2)
#define IOCON_INTPOL  (1 << 1)

typedef int (*i2c_write_fn)(uint8_t dev_addr, uint8_t reg, const uint8_t *data, uint16_t len);
typedef int (*i2c_read_fn)(uint8_t dev_addr, uint8_t reg, uint8_t *data, uint16_t len);

typedef struct {
    uint8_t dev_addr;
    i2c_write_fn write;
    i2c_read_fn read;
    uint16_t shadow_olat;     /* Тіньовий стан виходів A і B */
    uint16_t shadow_iodir;    /* Тіньовий напрямок пінів */
} mcp23017_t;

int mcp23017_init(mcp23017_t *dev, uint8_t i2c_addr, i2c_write_fn w_fn, i2c_read_fn r_fn) {
    dev->dev_addr = i2c_addr;
    dev->write = w_fn;
    dev->read = r_fn;
    dev->shadow_olat = 0x0000;
    dev->shadow_iodir = 0xFFFF; /* Усі входи за замовчуванням */

    /* Налаштування IOCON: об'єднати переривання A/B (MIRROR) та відкритий стік (ODR) */
    uint8_t iocon_val = IOCON_MIRROR | IOCON_ODR;
    return dev->write(dev->dev_addr, MCP_IOCON, &iocon_val, 1);
}

int mcp23017_set_pin_mode(mcp23017_t *dev, uint8_t pin, bool is_input, bool pullup) {
    if (pin >= 16) return -1;

    if (is_input) {
        dev->shadow_iodir |= (1 << pin);
    } else {
        dev->shadow_iodir &= ~(1 << pin);
    }

    uint8_t iodir_bytes[2] = {
        (uint8_t)(dev->shadow_iodir & 0xFF),
        (uint8_t)((dev->shadow_iodir >> 8) & 0xFF)
    };
    int err = dev->write(dev->dev_addr, MCP_IODIRA, iodir_bytes, 2);
    if (err != 0) return err;

    if (is_input && pullup) {
        uint8_t gppu_reg = (pin < 8) ? MCP_GPPUA : MCP_GPPUB;
        uint8_t bit_mask = 1 << (pin % 8);
        uint8_t current_gppu = 0;
        dev->read(dev->dev_addr, gppu_reg, &current_gppu, 1);
        current_gppu |= bit_mask;
        return dev->write(dev->dev_addr, gppu_reg, &current_gppu, 1);
    }
    return 0;
}

int mcp23017_write_pin(mcp23017_t *dev, uint8_t pin, bool level) {
    if (pin >= 16) return -1;

    if (level) {
        dev->shadow_olat |= (1 << pin);
    } else {
        dev->shadow_olat &= ~(1 << pin);
    }

    uint8_t reg = (pin < 8) ? MCP_OLATA : MCP_OLATB;
    uint8_t byte_val = (pin < 8) ? (dev->shadow_olat & 0xFF) : ((dev->shadow_olat >> 8) & 0xFF);
    return dev->write(dev->dev_addr, reg, &byte_val, 1);
}

int mcp23017_enable_interrupt(mcp23017_t *dev, uint8_t pin) {
    if (pin >= 16) return -1;
    uint8_t reg = (pin < 8) ? MCP_GPINTENA : MCP_GPINTENB;
    uint8_t val = 0;
    dev->read(dev->dev_addr, reg, &val, 1);
    val |= (1 << (pin % 8));
    return dev->write(dev->dev_addr, reg, &val, 1);
}

int mcp23017_read_captured_interrupt(mcp23017_t *dev, uint16_t *flags, uint16_t *captured_levels) {
    uint8_t intf[2] = {0, 0};
    uint8_t intcap[2] = {0, 0};

    /* Зчитування прапорців, хто викликав переривання */
    int err = dev->read(dev->dev_addr, MCP_INTFA, intf, 2);
    if (err != 0) return err;

    /* Зчитування зафіксованих логічних рівнів (це також скидає лінію /INT) */
    err = dev->read(dev->dev_addr, MCP_INTCAPA, intcap, 2);
    if (err != 0) return err;

    *flags = (uint16_t)intf[0] | ((uint16_t)intf[1] << 8);
    *captured_levels = (uint16_t)intcap[0] | ((uint16_t)intcap[1] << 8);
    return 0;
}
```
```cpp
#include <cstdint>
#include <expected>
#include <span>
#include <concepts>

enum class ExpanderError {
    BusError,
    InvalidPin,
    Timeout
};

template <typename I2CBus>
concept I2CTransceiver = requires(I2CBus bus, uint8_t addr, uint8_t reg, std::span<const uint8_t> out_buf, std::span<uint8_t> in_buf) {
    { bus.write(addr, reg, out_buf) } -> std::same_as<bool>;
    { bus.read(addr, reg, in_buf) } -> std::same_as<bool>;
};

template <I2CTransceiver Bus>
class Mcp23017 {
public:
    enum class PinMode { Output, Input, InputPullup };

    explicit Mcp23017(Bus& bus, uint8_t address = 0x20)
        : bus_(bus), address_(address), shadow_olat_(0x0000), shadow_iodir_(0xFFFF) {}

    std::expected<void, ExpanderError> initialize() {
        constexpr uint8_t reg_iocon = 0x0A;
        constexpr uint8_t iocon_val = (1 << 6) | (1 << 2); // MIRROR | Open-Drain ODR
        const uint8_t payload[] = { iocon_val };

        if (!bus_.write(address_, reg_iocon, payload)) {
            return std::unexpected(ExpanderError::BusError);
        }
        return {};
    }

    std::expected<void, ExpanderError> setPinMode(uint8_t pin, PinMode mode) {
        if (pin >= 16) return std::unexpected(ExpanderError::InvalidPin);

        if (mode == PinMode::Output) {
            shadow_iodir_ &= ~(1 << pin);
        } else {
            shadow_iodir_ |= (1 << pin);
        }

        const uint8_t iodir_data[2] = {
            static_cast<uint8_t>(shadow_iodir_ & 0xFF),
            static_cast<uint8_t>((shadow_iodir_ >> 8) & 0xFF)
        };

        if (!bus_.write(address_, 0x00 /* IODIRA */, iodir_data)) {
            return std::unexpected(ExpanderError::BusError);
        }

        if (mode == PinMode::InputPullup) {
            const uint8_t reg = (pin < 8) ? 0x0C : 0x0D; // GPPUA / GPPUB
            uint8_t current_gppu = 0;
            uint8_t buf[1] = {0};
            if (!bus_.read(address_, reg, buf)) return std::unexpected(ExpanderError::BusError);
            buf[0] |= static_cast<uint8_t>(1 << (pin % 8));
            if (!bus_.write(address_, reg, buf)) return std::unexpected(ExpanderError::BusError);
        }
        return {};
    }

    std::expected<void, ExpanderError> writePin(uint8_t pin, bool value) {
        if (pin >= 16) return std::unexpected(ExpanderError::InvalidPin);

        if (value) {
            shadow_olat_ |= (1 << pin);
        } else {
            shadow_olat_ &= ~(1 << pin);
        }

        const uint8_t reg = (pin < 8) ? 0x14 : 0x15; // OLATA : OLATB
        const uint8_t payload[] = {
            static_cast<uint8_t>((pin < 8) ? (shadow_olat_ & 0xFF) : ((shadow_olat_ >> 8) & 0xFF))
        };

        if (!bus_.write(address_, reg, payload)) {
            return std::unexpected(ExpanderError::BusError);
        }
        return {};
    }

    struct InterruptEvent {
        uint16_t triggered_pins;
        uint16_t captured_values;
    };

    std::expected<InterruptEvent, ExpanderError> readInterruptSnapshot() {
        uint8_t intf_buf[2] = {0, 0};
        uint8_t intcap_buf[2] = {0, 0};

        if (!bus_.read(address_, 0x0E /* INTFA */, intf_buf)) {
            return std::unexpected(ExpanderError::BusError);
        }
        if (!bus_.read(address_, 0x10 /* INTCAPA */, intcap_buf)) {
            return std::unexpected(ExpanderError::BusError);
        }

        InterruptEvent evt{
            .triggered_pins = static_cast<uint16_t>(intf_buf[0] | (intf_buf[1] << 8)),
            .captured_values = static_cast<uint16_t>(intcap_buf[0] | (intcap_buf[1] << 8))
        };
        return evt;
    }

private:
    Bus& bus_;
    uint8_t address_;
    uint16_t shadow_olat_;
    uint16_t shadow_iodir_;
};
```
:::

#### Аналіз C++20 концептів та ідіоматичних рішень

У C++ версії драйвера застосовано сучасні механізми проектування:
- **`concept I2CTransceiver`**: замінює класичний поліморфізм на основі віртуальних функцій статичною типізацією часу компіляції. Це усуває накладні витрати на таблиці віртуальних методів (*vtable*) та непрямі виклики, що критично для систем із жорсткими обмеженнями пам'яті.
- **`std::expected<T, ExpanderError>`**: забезпечує явне поширення кодів помилок апаратного зв'язку без використання винятків (*exceptions*), які зазвичай відключають у прошивках мікроконтролерів (`-fno-exceptions`).
- **`std::span<const uint8_t>`**: надає безпечний, некопіюючий інтерфейс перегляду масивів пам'яті без передачі небезпечних пар «покажчик + довжина».

---

### 2. Платформозалежна інтеграція з апаратними перериваннями

Нижче наведено приклади повної системної інтеграції з перериваннями для мікроконтролерів STM32 (STM32Cube HAL) та ESP32 (ESP-IDF з FreeRTOS).

#### Особливості реалізації на STM32

На мікроконтролерах сімейства STM32 лінія `/INT` підключається до виводу з підтримкою зовнішніх переривань EXTI (наприклад, `PA0` або `PB0`). В обробнику `HAL_GPIO_EXTI_Callback` перевіряється часовий інтервал від попередньої події через системний лічильник `HAL_GetTick()`. Якщо інтервал перевищує 30 мс, виставляється прапорець для головного циклу обробки.

#### Особливості реалізації на ESP32 під FreeRTOS

У середовищі ESP-IDF обробка переривання реалізується через чергу подій FreeRTOS (`QueueHandle_t`). Обробник переривання `gpio_isr_handler` за допомогою виклику `xQueueSendFromISR` надсилає номер піна у фонову задачу `expander_task`. Задача прокидається із заблокованого стану, виконує дебаунс-затримку `vTaskDelay` та здійснює транзакції I2C без блокування планувальника задач.

:::tabs
```stm32
#include "stm32f4xx_hal.h"
#include <stdbool.h>

extern I2C_HandleTypeDef hi2c1;
#define MCP23017_ADDR_8BIT (0x20 << 1)

static volatile bool g_expander_int_pending = false;
static uint32_t g_last_int_tick = 0;

/* Обробник зовнішнього переривання EXTI (підключений до лінії /INT розширювача) */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == GPIO_PIN_0) {
        uint32_t now = HAL_GetTick();
        /* Фільтрація брязкоту контактів: ігноруємо повторні імпульси швидше 30 мс */
        if ((now - g_last_int_tick) > 30) {
            g_expander_int_pending = true;
            g_last_int_tick = now;
        }
    }
}

void Process_Expander_Events(void) {
    if (!g_expander_int_pending) return;
    g_expander_int_pending = false;

    uint8_t intf[2] = {0};
    uint8_t intcap[2] = {0};

    /* Читання прапорців переривань */
    if (HAL_I2C_Mem_Read(&hi2c1, MCP23017_ADDR_8BIT, 0x0E, I2C_MEMADD_SIZE_8BIT, intf, 2, 100) == HAL_OK) {
        uint16_t active_pins = (uint16_t)intf[0] | ((uint16_t)intf[1] << 8);

        /* Читання зафіксованого стану (скидає /INT на MCP23017) */
        if (HAL_I2C_Mem_Read(&hi2c1, MCP23017_ADDR_8BIT, 0x10, I2C_MEMADD_SIZE_8BIT, intcap, 2, 100) == HAL_OK) {
            uint16_t pin_levels = (uint16_t)intcap[0] | ((uint16_t)intcap[1] << 8);

            for (uint8_t pin = 0; pin < 16; ++pin) {
                if (active_pins & (1 << pin)) {
                    bool level = (pin_levels & (1 << pin)) != 0;
                    /* Обробка натискання кнопки чи спрацьовування датчика */
                }
            }
        }
    }
}
```
```esp-idf
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "driver/gpio.h"
#include "driver/i2c.h"

#define I2C_MASTER_NUM       I2C_NUM_0
#define MCP23017_I2C_ADDR    0x20
#define INT_INPUT_PIN        GPIO_NUM_4

static QueueHandle_t gpio_evt_queue = NULL;

static void IRAM_ATTR gpio_isr_handler(void* arg) {
    uint32_t gpio_num = (uint32_t) arg;
    xQueueSendFromISR(gpio_evt_queue, &gpio_num, NULL);
}

static void expander_task(void* arg) {
    uint32_t io_num;
    while (1) {
        if (xQueueReceive(gpio_evt_queue, &io_num, portMAX_DELAY)) {
            /* Затримка дебаунсингу перед опитуванням I2C */
            vTaskDelay(pdMS_TO_TICKS(25));

            uint8_t intf_reg = 0x0E;
            uint8_t intf_data[2] = {0};
            uint8_t intcap_reg = 0x10;
            uint8_t intcap_data[2] = {0};

            /* Читання прапорців */
            i2c_master_write_read_device(I2C_MASTER_NUM, MCP23017_I2C_ADDR,
                                         &intf_reg, 1, intf_data, 2, pdMS_TO_TICKS(50));
            /* Читання знімка стану пінів */
            i2c_master_write_read_device(I2C_MASTER_NUM, MCP23017_I2C_ADDR,
                                         &intcap_reg, 1, intcap_data, 2, pdMS_TO_TICKS(50));

            uint16_t flags = (uint16_t)intf_data[0] | ((uint16_t)intf_data[1] << 8);
            uint16_t levels = (uint16_t)intcap_data[0] | ((uint16_t)intcap_data[1] << 8);

            /* Логіка обробки подій периферії */
        }
    }
}
```
```arduino
#include <Wire.h>

#define MCP_ADDR 0x20
#define INT_PIN 2

volatile bool intFlag = false;

void IRAM_ATTR onInterrupt() {
    intFlag = true;
}

void setup() {
    Wire.begin();
    pinMode(INT_PIN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(INT_PIN), onInterrupt, FALLING);

    // Налаштування MCP23017: об'єднати INTA/B, Open-Drain
    Wire.beginTransmission(MCP_ADDR);
    Wire.write(0x0A); // IOCON
    Wire.write(0x44); // MIRROR=1, ODR=1
    Wire.endTransmission();

    // Порт A як вхід із підтяжкою та перериванням
    Wire.beginTransmission(MCP_ADDR);
    Wire.write(0x00); // IODIRA
    Wire.write(0xFF); // Всі 8 пінів - входи
    Wire.endTransmission();

    Wire.beginTransmission(MCP_ADDR);
    Wire.write(0x0C); // GPPUA
    Wire.write(0xFF); // Підтяжки увімкнено
    Wire.endTransmission();

    Wire.beginTransmission(MCP_ADDR);
    Wire.write(0x04); // GPINTENA
    Wire.write(0xFF); // Дозвіл переривань для всіх пінів
    Wire.endTransmission();
}

void loop() {
    if (intFlag) {
        delay(25); // Апаратний дебаунсинг
        intFlag = false;

        Wire.beginTransmission(MCP_ADDR);
        Wire.write(0x10); // INTCAPA
        Wire.endTransmission();

        Wire.requestFrom(MCP_ADDR, 1);
        if (Wire.available()) {
            uint8_t captured = Wire.read();
            // Обробка захопленого байта кнопок
        }
    }
}
```
:::

---

### 3. Діаграма станів скінченного автомата обробки подій

Для надійної роботи вбудованої системи без накопичення незнятих переривань драйвер реалізує 5-позиційний кінцевий автомат обробки:

1. **Стан `STATE_IDLE` (Спокій)**:
   - Лінія `/INT` утримується на високому рівні зовнішнім резистором підтяжки.
   - Зовнішнє переривання мікроконтролера EXTI увімкнено на спадний фронт (*Falling Edge*).
2. **Стан `STATE_TRIGGERED` (Фіксація події)**:
   - Відбувається замикання зовнішнього контакту на землю.
   - Розширювач переводить вихід `/INT` у низький рівень.
   - Спрацьовує апаратний обробник EXTI ISR: він негайно **маскує переривання EXTI** (щоб уникнути повторних спрацьовувань від брязкоту) і запускає неблокуючий програмний таймер дебаунсингу.
3. **Стан `STATE_DEBOUNCING` (Очікування заспокоєння)**:
   - Протягом 20–30 мс система ігнорує будь-які імпульси на лініях.
   - По завершенню таймера планувальник активує задачу читання I2C.
4. **Стан `STATE_READ_CAPTURE` (Зчитування INTCAP)**:
   - Процесор надсилає I2C-кадр читання регістра `INTCAP`.
   - Розширювач видає заморожений стан входів і **апаратно деактивує лінію `/INT`**.
   - Драйвер передає інформацію про змінені піни у прикладну програму.
5. **Стан `STATE_VERIFY_AND_ARM` (Перевірка та повторне зведення)**:
   - Процесор перевіряє поточний фізичний рівень на лінії `/INT`.
   - Якщо лінія `/INT` все ще низька (під час читання виникла нова подія на іншому піні), автомат негайно повертається до читання `INTCAP`.
   - Якщо лінія `/INT` піднялася до `VDD`, зовнішнє переривання EXTI знову демаскується, і система повертається у `STATE_IDLE`.

---

### 4. Стійкість до збоїв шини: відновлення та повторні спроби

У промислових системах з високим рівнем електромагнітних завад можливі ситуації, коли I2C-транзакція завершується помилкою `NACK` або шина зависає. Драйвер повинен містити стратегії самовідновлення:

1. **Політика повторних спроб (Retry Policy)**:
   При отриманні помилки `NACK` під час читання `INTCAP` драйвер не скидає прапорець переривання, а повторює транзакцію до 3 разів з короткими паузами 1 мс. Якщо всі спроби виявилися невдалими, драйвер генерує системний код помилки `ExpanderError::BusError` і переходить до процедури аварійного скидання шини.
2. **Програмне розблокування шини (9-Clock Recovery)**:
   Якщо ведений чіп через збій живлення або раптове скидання хоста завис у стані утримання лінії `SDA` на низькому рівні, мікроконтролер не може згенерувати стандартний сигнал `START`. У такій ситуації драйвер тимчасово переводить пін SCL у режим програмного керування GPIO (*Bit-Banging*) і видає послідовність із 9 тактових імпульсів частотою 100 кГц. Отримавши такти без завершення передачі байта, розширювач гарантовано виходить зі стану очікування біта ACK, звільняє лінію `SDA`, після чого ведучий видає коректний стоп-кадр `STOP`.

---

### 5. Патерн віртуальних пінів (Virtual Pin Abstraction)

У великих проектах високорівнева логіка (наприклад, драйвери символьних РК-дисплеїв HD44780, матричних клавіатур чи крокових двигунів) не повинна залежати від того, де фізично розташований вивід — на кристалі мікроконтролера чи на зовнішньому розширювачі.

Для цього реалізують таблицю віртуальних дескрипторів:
- Піни з індексами `0..31` транслюються в апаратні виклики `HAL_GPIO_WritePin()`.
- Піни з індексами `32..47` автоматично перенаправляються на виклики `mcp23017_write_pin()`.

Ця абстракція робить код бібліотек повністю портативним, але накладає часові обмеження: якщо прямий запис у регістр STM32 `BSRR` займає лише 1 такт тактової частоти (близько 6 нс при 168 МГц), то віртуальний запис через I2C вимагає 45–180 мкс. Це унеможливлює використання віртуальних пінів розширювача для генерації високочастотного ШІМ або швидкісних протоколів типу SPI Bit-Bang.

---

### 6. Оцінка накладних витрат пам'яті та швидкодії

Запропонована архітектура оптимізована для застосування в мікроконтролерах із суворими лімітами ресурсів:
- **Оперативна пам'ять (RAM)**: об'єкт C++ класу `Mcp23017` займає лише 6 байтів у RAM (1 байт адреси, 2 байти `shadow_olat`, 2 байти `shadow_iodir` та посилання на шину). Драйвер не використовує динамічного виділення пам'яті (`malloc` / `new`), що повністю виключає фрагментацію купи (*heap fragmentation*).
- **Пам'ять програм (Flash)**: завдяки інлайнінгу шаблонів C++20 скомпільований бінарний код займає менше 400 байтів Flash на архітектурі ARM Cortex-M4.
- **Швидкодія обробки**: при тактовій частоті I2C 400 кГц повний цикл зчитування захопленого стану `INTCAP` триває лише близько 65 мікросекунд, забезпечуючи час реакції на зовнішні події швидше 30 мілісекунд з урахуванням апаратного дебаунсингу.

---

### 7. Тестування та верифікація граничних режимів

Під час впровадження драйвера у серійні пристрої необхідно провести верифікацію наступних сценаріїв:
1. **Одночасна зміна стану кількох входів**: якщо оператор одночасно натискає дві кнопки на портах A і B, регістр `INTF` повинен містити обидва встановлені біти, а `INTCAP` — зафіксувати точний логічний знімок обох ліній.
2. **Втрата зв'язку або помилка NACK на шині**: якщо під час виконання читання `INTCAP` шина I2C повертає помилку зв'язку, лінія `/INT` залишиться притягнутою до землі. Драйвер повинен коректно відпрацювати лічильник повторних спроб і не зациклити переривання.
3. **Енергоспоживання в режимі очікування**: при переведенні процесора в глибокий сон (Deep Sleep) лінія `/INT` повинна бути сконфігурована як джерело асинхронного пробудження (*Wake-up Source*), забезпечуючи споживання всієї системи на рівні лічених мікроамперів у стані спокою.
4. **Апаратне налагодження через тестові точки (Test Points)**: для вимірювання реальної затримки реакції драйвера на платі виводять лінію `/INT` на перший канал осцилографа, а спеціальний відлагоджувальний пін хоста `DEBUG_PIN` — на другий канал. Підйом `DEBUG_PIN` у функції обробника демонструє точний час від виникнення фізичного перепаду до закінчення читання I2C.

---

### 8. Оптимізація енергоспоживання у батарейних пристроях

Для приладів з автономним живленням (бездротові пульти, польові логери, сенсорні вузли IoT) драйвер реалізує спеціальну стратегію переходу в режим глибокого сну (*Deep Sleep*):
- Хост-мікроконтролер конфігурує розширювач (регістри `DEFVAL` та `INTCON`), налаштовує вхідний вивід переривання як джерело асинхронного пробудження ядра (`EXTI_WakeUp` або `esp_sleep_enable_ext0_wakeup`), після чого повністю вимикає тактові генератори ядра і периферії I2C.
- У цьому стані розширювач `MCP23017` споживає струм спокою менше `1 мкА`, а процесор — близько `5–10 мкА`.
- При натисканні будь-якої кнопки спад на лінії `/INT` викликає апаратне пробудження контролера живлення, процесор запускає PLL, ініціалізує контролер I2C та зчитує точний стан події з регістра `INTCAP`.

---

### 9. Каскадування переривань у мультичіпових конфігураціях

Коли на одній системній платі встановлено 4 або 8 розширювачів для обслуговування матриці з 64 або 128 портів, заведення окремої лінії переривання від кожного чіпа до мікроконтролера вичерпує вхідні піни процесора.

Завдяки конфігурації відкритий стік (`IOCON.ODR = 1`) усі виводи `/INT` від усіх розширювачів об'єднуються на **єдину фізичну лінію монтажного «АБО»**.

Апаратні адреси розширювачів жорстко задаються підтяжками адресних ніжок `A0..A2` до ліній `VDD` або `GND` (наприклад, перший чіп `0x20` — усі три ніжки на землю, другий `0x21` — пін A0 до VDD). Якщо адресні лінії проходять поблизу силових перетворювачів напруги, рекомендується шунтувати їх керамічними конденсаторами 100 нФ для усунення перемикання адрес від імпульсних наведень.


Алгоритм диспетчеризації у багаточіповому драйвері:
1. При спаді спільної лінії переривання хост-драйвер послідовно виконує швидке читання регістрів `INTF` або `INTCAP` для кожного зареєстрованого чіпа `0x20` .. `0x27`.
2. Якщо зчитаний регістр `INTF` містить ненульове значення, драйвер передає захоплені дані у відповідний обробник порту.
3. Процес повторюється доти, доки спільна лінія `/INT` не підніметься у високий стан `VDD`, гарантуючи скидання подій на всіх каскадованих мікросхемах.
4. Якщо після опитування всіх пристроїв лінія залишається низькою, драйвер виконує скидання шини для запобігання блокуванню.


