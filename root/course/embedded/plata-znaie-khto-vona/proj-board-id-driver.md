# ⚙️ Драйвер визначення ревізії плати на АЦП та GPIO

Цей модуль реалізує апаратне розпізнавання версії друкованої плати (Board ID) на етапі завантаження мікроконтролера та динамічну прив'язку драйверів периферії без перекомпіляції бінарного файлу.

У серійних виробах підтримка кількох апаратних ревізій в єдиному бінарному образі спирається на надійний механізм ідентифікації заліза в перші мілісекунди після скидання. Драйвер розпізнавання розв'язує два взаємопов'язані інженерні завдання: фізично вимірює конфігураційні ланцюги на платі з відсіканням шумів і наведень та транслює отримане числове значення у відповідний дескриптор платформи.

Система підтримує два взаємодоповнюючі механізми вимірювання:
1. **Аналоговий канал (ADC-based ID)**: зчитування напруги прецизійного резистивного дільника з фільтрацією шумів і порівнянням із каліброваними вікнами допусків.
2. **Цифрова матриця (GPIO Strapping)**: опитування конфігураційних виводів із тристабільним детектуванням (стан високого імпедансу Hi-Z, підтяжка до VDD або GND) та переведенням пінів у режим енергозбереження після опитування.

---

## Архітектура драйвера та структури даних

Драйвер розділено на дві логічні частини:
- **Апаратний детектор (`board_id_detector`)**: зчитує фізичні рівні з виводів, виконує усереднення вибірок та повертає цілочисельний ідентифікатор ревізії (`board_rev_t`).
- **Диспетчер конфігурацій (`bsp_manager`)**: зіставляє числовий ID із таблицею дескрипторів плат, ініціалізує відповідні виводи [GPIO](root:hw-digital/gpio) та повертає покажчики на абстрактні інтерфейси драйверів.

```
+-------------------------------------------------------------------+
|                        Етап завантаження                          |
|                                                                   |
|   +-----------------------+           +-----------------------+   |
|   |  ADC-дільник (1 пін)  |           | GPIO Strapping (2-3)  |   |
|   +-----------+-----------+           +-----------+-----------+   |
|               |                                   |               |
|               +-----------------+-----------------+               |
|                                 |                                 |
|                                 v                                 |
|               +-----------------------------------+               |
|               |  Детектор ревізії (Board ID Core) |               |
|               |  - Медіанна фільтрація АЦП        |               |
|               |  - Тристабільний аналіз GPIO      |               |
|               +-----------------+-----------------+               |
|                                 |                                 |
|                                 v                                 |
|               +-----------------------------------+               |
|               |   Таблиця дескрипторів (ROM Table)|               |
|               |   - Карта пінів периферії         |               |
|               |   - Фабрика драйверів (VMT)       |               |
|               |   - Калібрувальні матриці         |               |
|               +-----------------+-----------------+               |
|                                 |                                 |
|                                 v                                 |
|               +-----------------------------------+               |
|               |    Уніфікований HAL / Додаток     |               |
|               +-----------------------------------+               |
+-------------------------------------------------------------------+
```

---

## Алгоритмічний аналіз методів вимірювання

### Медіанна фільтрація аналогового каналу

Зчитування напруги дільника на етапі запуску стикається з нестабільністю шин живлення в момент перехідного процесу (Power-On Reset). У перші мілісекунди після ввімкнення імпульсні перетворювачі виходять на стабільний режим, а зарядні струми конденсаторів створюють сплески в земляній площині.

Просте одиничне перетворення [АЦП](root:hw-analog/adc) може зафіксувати випадковий шумовий викид і хибно віднести плату до сусіднього діапазону. Щоб усунути цей ризик, драйвер реалізує послідовну вибірку з `N = 16` відліків із часовим інтервалом у `50 мкс`. Отриманий масив сортується, після чого обирається медіанний елемент (значення в центрі відсортованого списку). Медіанний фільтр повністю відкидає короткі поодинокі викиди будь-якої амплітуди, на відміну від середнього арифметичного, яке зміщується під дією навіть одного аномального відліку.

### Тристабільне зондування ліній GPIO

При використанні цифрових виводів перевірка тристабільного стану лінії вимагає двох послідовних кроків активного впливу з боку внутрішньої периферії мікроконтролера. 

Коли на платі розпаяно зовнішній резистор опором `10 кОм` на `GND`, увімкнення слабкої внутрішньої підтяжки `Pull-Up` (`40..50 кОм`) утворює [дільник напруги](root:hw-analog/voltage-divider). Напруга на вході не піднімається вище `0.55 В` (для живлення `3.3 В`), що вхідний тригер Шмітта впевнено інтерпретує як логічний нуль `LOW`. Якщо ж зовнішній резистор підтягнутий до `VDD`, то при ввімкненні внутрішнього `Pull-Down` напруга на вході залишається вище `2.75 В`, формуючи стійку логічну одиницю `HIGH`.

Якщо ж вивід на платі залишений непід'єднаним (Hi-Z), вхідний потенціал слухняно слідує за внутрішнім комутованим резистором: під час тесту з `Pull-Up` зчитується `1`, а під час тесту з `Pull-Down` — `0`. Така зміна стану сигналізує драйверу про відсутність зовнішнього монтажу на цій контактній площинці.

---

## Реалізація на C та C++

У наведених лістингах реалізовано:
1. Опитування [аналогово-цифрового перетворювача](root:hw-analog/adc) з відкиданням екстремумів і захистом від шумів опорної напруги.
2. Тристабільне опитування цифрових пінів за алгоритмом подвійної внутрішньої підтяжки (`Pull-Up` / `Pull-Down`).
3. Фабрику драйверів, яка динамічно призначає таблицю віртуальних методів для давача руху (наприклад, Bosch BMI270 для Rev A та ST LSM6DSO для Rev B).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Перелік підтримуваних ревізій плати */
typedef enum {
    BOARD_REV_UNKNOWN = 0x00,
    BOARD_REV_A       = 0x01, /* Прототип: BMI270 на SPI1, Display ST7789  */
    BOARD_REV_B       = 0x02, /* Серія: LSM6DSO на SPI2, Display ILI9341   */
    BOARD_REV_C       = 0x03, /* Оптимізована: ICM42688 на SPI1, ST7789V3  */
    BOARD_REV_COUNT
} board_rev_t;

/* Тристабільний стан конфігураційного піна */
typedef enum {
    PIN_STATE_PULL_DOWN = 0, /* Зовнішній резистор на GND */
    PIN_STATE_PULL_UP   = 1, /* Зовнішній резистор на VDD */
    PIN_STATE_FLOATING  = 2  /* Вивід не підключений (Hi-Z) */
} pin_tristate_t;

/* Діапазон напруг для АЦП-селектора ревізії (12-бітний АЦП, Vref = 3300 мВ) */
typedef struct {
    uint16_t    raw_min;   /* Нижній поріг коду АЦП */
    uint16_t    raw_max;   /* Верхній поріг коду АЦП */
    board_rev_t revision;  /* Відповідна ревізія */
} adc_rev_window_t;

/* Абстрактний інтерфейс давача інерції (IMU) */
typedef struct imu_driver_s imu_driver_t;
struct imu_driver_s {
    bool (*init)(void);
    bool (*read_accel)(float *x, float *y, float *z);
    bool (*read_gyro)(float *x, float *y, float *z);
    void (*sleep)(void);
};

/* Дескриптор апаратної конфігурації конкретної плати */
typedef struct {
    board_rev_t         revision;
    const char         *board_name;
    uint8_t             spi_bus_index;
    uint16_t            cs_pin_mask;
    float               accel_gain_correction;
    const imu_driver_t *imu_driver;
} board_descriptor_t;

/* Апаратно-залежні заглушки периферії */
extern uint16_t hal_adc_read_raw(uint8_t channel);
extern void     hal_gpio_set_mode_input(uint8_t pin);
extern void     hal_gpio_set_pullup(uint8_t pin);
extern void     hal_gpio_set_pulldown(uint8_t pin);
extern void     hal_gpio_set_floating(uint8_t pin);
extern bool     hal_gpio_read(uint8_t pin);
extern void     hal_delay_us(uint32_t us);

/* Таблиця вікон напруг для 4 можливих ревізій на 1 піні АЦП */
static const adc_rev_window_t g_adc_rev_windows[] = {
    { .raw_min = 0,    .raw_max = 500,  .revision = BOARD_REV_A }, /* ~0.2 В: дільник 100k/6.8k */
    { .raw_min = 800,  .raw_max = 1400, .revision = BOARD_REV_B }, /* ~0.9 В: дільник 100k/39k  */
    { .raw_min = 1700, .raw_max = 2300, .revision = BOARD_REV_C }, /* ~1.65 В: дільник 100k/100k */
};

#define ADC_WINDOW_COUNT (sizeof(g_adc_rev_windows) / sizeof(g_adc_rev_windows[0]))
#define ADC_OVERSAMPLE_COUNT 16

/* Сортування масиву для обчислення медіани */
static void sort_u16(uint16_t *buf, size_t len) {
    for (size_t i = 0; i < len - 1; ++i) {
        for (size_t j = i + 1; j < len; ++j) {
            if (buf[i] > buf[j]) {
                uint16_t tmp = buf[i];
                buf[i] = buf[j];
                buf[j] = tmp;
            }
        }
    }
}

/* Зчитування ревізії через резистивний дільник АЦП */
board_rev_t board_id_read_adc(uint8_t adc_channel) {
    uint16_t samples[ADC_OVERSAMPLE_COUNT];

    for (size_t i = 0; i < ADC_OVERSAMPLE_COUNT; ++i) {
        samples[i] = hal_adc_read_raw(adc_channel);
        hal_delay_us(50);
    }

    sort_u16(samples, ADC_OVERSAMPLE_COUNT);
    /* Беремо медіану для відкидання імпульсних наведень */
    uint16_t median_val = samples[ADC_OVERSAMPLE_COUNT / 2];

    for (size_t i = 0; i < ADC_WINDOW_COUNT; ++i) {
        if (median_val >= g_adc_rev_windows[i].raw_min &&
            median_val <= g_adc_rev_windows[i].raw_max) {
            return g_adc_rev_windows[i].revision;
        }
    }
    return BOARD_REV_UNKNOWN;
}

/* Тристабільне детектування стану одного цифрового піна */
pin_tristate_t board_id_detect_pin_tristate(uint8_t pin) {
    hal_gpio_set_mode_input(pin);

    /* Тест 1: вмикаємо внутрішню підтяжку до живлення */
    hal_gpio_set_pullup(pin);
    hal_delay_us(100);
    bool read_with_pullup = hal_gpio_read(pin);

    /* Тест 2: вмикаємо внутрішню підтяжку до землі */
    hal_gpio_set_pulldown(pin);
    hal_delay_us(100);
    bool read_with_pulldown = hal_gpio_read(pin);

    /* Відключаємо підтяжки для запобігання витоку струму */
    hal_gpio_set_floating(pin);

    if (read_with_pullup && !read_with_pulldown) {
        /* Лінія повторила внутрішню підтяжку -> зовнішнього резистора немає */
        return PIN_STATE_FLOATING;
    } else if (read_with_pullup && read_with_pulldown) {
        /* Лінія завжди HIGH -> зовнішній резистор до VDD переміг внутрішній pull-down */
        return PIN_STATE_PULL_UP;
    } else {
        /* Лінія завжди LOW -> зовнішній резистор до GND переміг внутрішній pull-up */
        return PIN_STATE_PULL_DOWN;
    }
}

/* Реалізації драйверів IMU для різних ревізій */
static bool bmi270_init(void) { /* Ініціалізація BMI270 */ return true; }
static bool bmi270_read_acc(float *x, float *y, float *z) { *x = 0.0f; *y = 0.0f; *z = 1.0f; return true; }
static bool bmi270_read_gyr(float *x, float *y, float *z) { *x = 0.0f; *y = 0.0f; *z = 0.0f; return true; }
static void bmi270_sleep(void) {}

static const imu_driver_t g_bmi270_driver = {
    .init = bmi270_init, .read_accel = bmi270_read_acc,
    .read_gyro = bmi270_read_gyr, .sleep = bmi270_sleep
};

static bool lsm6dso_init(void) { /* Ініціалізація LSM6DSO */ return true; }
static bool lsm6dso_read_acc(float *x, float *y, float *z) { *x = 0.01f; *y = -0.02f; *z = 0.99f; return true; }
static bool lsm6dso_read_gyr(float *x, float *y, float *z) { *x = 0.0f; *y = 0.0f; *z = 0.0f; return true; }
static void lsm6dso_sleep(void) {}

static const imu_driver_t g_lsm6dso_driver = {
    .init = lsm6dso_init, .read_accel = lsm6dso_read_acc,
    .read_gyro = lsm6dso_read_gyr, .sleep = lsm6dso_sleep
};

/* Статична таблиця дескрипторів плат у Flash-пам'яті */
static const board_descriptor_t g_board_descriptors[] = {
    {
        .revision              = BOARD_REV_A,
        .board_name            = "SensorNode-v1.2-RevA",
        .spi_bus_index         = 1,
        .cs_pin_mask           = (1u << 4),
        .accel_gain_correction = 1.002f,
        .imu_driver            = &g_bmi270_driver,
    },
    {
        .revision              = BOARD_REV_B,
        .board_name            = "SensorNode-v2.0-RevB",
        .spi_bus_index         = 2,
        .cs_pin_mask           = (1u << 12),
        .accel_gain_correction = 0.995f,
        .imu_driver            = &g_lsm6dso_driver,
    }
};

#define DESCRIPTORS_COUNT (sizeof(g_board_descriptors) / sizeof(g_board_descriptors[0]))

/* Пошук дескриптора за ревізією */
const board_descriptor_t *bsp_get_descriptor(board_rev_t rev) {
    for (size_t i = 0; i < DESCRIPTORS_COUNT; ++i) {
        if (g_board_descriptors[i].revision == rev) {
            return &g_board_descriptors[i];
        }
    }
    return NULL;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <algorithm>
#include <optional>
#include <string_view>

enum class BoardRev : uint8_t {
    Unknown = 0x00,
    RevA    = 0x01,
    RevB    = 0x02,
    RevC    = 0x03
};

enum class PinTristate : uint8_t {
    PullDown = 0,
    PullUp   = 1,
    Floating = 2
};

struct AdcRevWindow {
    uint16_t raw_min;
    uint16_t raw_max;
    BoardRev revision;
};

/* Чистий інтерфейс давача */
class IImuDriver {
public:
    virtual ~IImuDriver() = default;
    virtual bool init() = 0;
    virtual bool read_accel(float& x, float& y, float& z) = 0;
    virtual bool read_gyro(float& x, float& y, float& z) = 0;
    virtual void sleep() = 0;
};

struct BoardDescriptor {
    BoardRev         revision;
    std::string_view board_name;
    uint8_t          spi_bus_index;
    uint16_t         cs_pin_mask;
    float            accel_gain_correction;
    IImuDriver*      imu_driver;
};

/* Апаратні абстракції */
extern "C" {
    uint16_t hal_adc_read_raw(uint8_t channel);
    void     hal_gpio_set_mode_input(uint8_t pin);
    void     hal_gpio_set_pullup(uint8_t pin);
    void     hal_gpio_set_pulldown(uint8_t pin);
    void     hal_gpio_set_floating(uint8_t pin);
    bool     hal_gpio_read(uint8_t pin);
    void     hal_delay_us(uint32_t us);
}

class BoardIdDetector {
public:
    static constexpr std::array<AdcRevWindow, 3> kAdcWindows{{
        { 0,    500,  BoardRev::RevA },
        { 800,  1400, BoardRev::RevB },
        { 1700, 2300, BoardRev::RevC },
    }};

    static BoardRev read_from_adc(uint8_t adc_channel) {
        std::array<uint16_t, 16> samples{};
        for (auto& s : samples) {
            s = hal_adc_read_raw(adc_channel);
            hal_delay_us(50);
        }

        std::sort(samples.begin(), samples.end());
        const uint16_t median = samples[samples.size() / 2];

        for (const auto& w : kAdcWindows) {
            if (median >= w.raw_min && median <= w.raw_max) {
                return w.revision;
            }
        }
        return BoardRev::Unknown;
    }

    static PinTristate detect_tristate(uint8_t pin) {
        hal_gpio_set_mode_input(pin);

        hal_gpio_set_pullup(pin);
        hal_delay_us(100);
        const bool with_up = hal_gpio_read(pin);

        hal_gpio_set_pulldown(pin);
        hal_delay_us(100);
        const bool with_down = hal_gpio_read(pin);

        hal_gpio_set_floating(pin);

        if (with_up && !with_down) {
            return PinTristate::Floating;
        } else if (with_up && with_down) {
            return PinTristate::PullUp;
        } else {
            return PinTristate::PullDown;
        }
    }
};

/* Конкретні класи драйверів */
class Bmi270Driver final : public IImuDriver {
public:
    bool init() override { return true; }
    bool read_accel(float& x, float& y, float& z) override {
        x = 0.0f; y = 0.0f; z = 1.0f;
        return true;
    }
    bool read_gyro(float& x, float& y, float& z) override {
        x = 0.0f; y = 0.0f; z = 0.0f;
        return true;
    }
    void sleep() override {}
};

class Lsm6dsoDriver final : public IImuDriver {
public:
    bool init() override { return true; }
    bool read_accel(float& x, float& y, float& z) override {
        x = 0.01f; y = -0.02f; z = 0.99f;
        return true;
    }
    bool read_gyro(float& x, float& y, float& z) override {
        x = 0.0f; y = 0.0f; z = 0.0f;
        return true;
    }
    void sleep() override {}
};

class BspManager {
private:
    static inline Bmi270Driver  s_bmi270{};
    static inline Lsm6dsoDriver s_lsm6dso{};

    static constexpr size_t kMaxBoards = 2;
    static inline const std::array<BoardDescriptor, kMaxBoards> s_descriptors{{
        {
            BoardRev::RevA,
            "SensorNode-v1.2-RevA",
            1,
            (1u << 4),
            1.002f,
            &s_bmi270
        },
        {
            BoardRev::RevB,
            "SensorNode-v2.0-RevB",
            2,
            (1u << 12),
            0.995f,
            &s_lsm6dso
        }
    }};

public:
    static std::optional<BoardDescriptor> get_descriptor(BoardRev rev) {
        for (const auto& desc : s_descriptors) {
            if (desc.revision == rev) {
                return desc;
            }
        }
        return std::nullopt;
    }
};
```
:::

---

## Детальний розбір інженерних нюансів реалізації

### 1. Час стабілізації при комутації внутрішніх підтяжок

При опитуванні тристабільного стану вхідна лінія володіє власною паразитною ємністю друкованого провідника та виводу мікроконтролера (`C_pin ≈ 5..15 пФ`). Коли програма викликає `hal_gpio_set_pullup(pin)`, внутрішній резистор `50 кОм` починає заряджати цю ємність. Постійна часу перехідного процесу становить:

```
τ = R_internal · C_pin = 50 кОм · 15 пФ = 0.75 мкс
```

Щоб гарантувати повне завершення заряду до 99.9% від кінцевого значення (`5 · τ ≈ 3.75 мкс`), у коді закладено консервативну затримку `hal_delay_us(100)`. Це повністю виключає зчитування проміжного потенціалу, коли на платі присутні довгі траси або додаткові захисні діоди ESD із підвищеною власною ємністю.

### 2. Стан високого опору (Hi-Z) після опитування

Зверніть увагу на обов'язковий виклик `hal_gpio_set_floating(pin)` наприкінці функції `board_id_detect_pin_tristate()`. Якщо залишити внутрішню підтяжку `Pull-Up` увімкненою для піна, який на платі замкнено на `GND` через зовнішній резистор `10 кОм`, через це коло буде безперервно протікати струм:

```
I = 3.3 В / (50 кОм + 10 кОм) = 55 мкА
```

Для трьох конфігураційних виводів постійний витік сягне `165 мкА`. Вимикання внутрішніх підтяжок повертає вхідний буфер у режим високого імпедансу, зводячи струм споживання до лічених наноамперів.

### 3. Відкидання невідомої ревізії (Fail-Safe Strategy)

Якщо плата повернула `BOARD_REV_UNKNOWN` (наприклад, через обрив резистора дільника або коротке замикання на лінії), функція `bsp_get_descriptor()` повертає `NULL` (`std::nullopt` у C++). 

У серійній прошивці це обробляється за правилом безумовної безпеки:
- Забороняється подача живлення на силові ключі та двигуни.
- Вимикаються всі високошвидкісні шини зв'язку.
- Світлодіод статусу переводиться в режим аварійного блимання (SOS-код).
- У налагоджувальний порт UART видається детальний звіт із сирим значенням АЦП та станами бітів GPIO для діагностики на сервісному стенді.
