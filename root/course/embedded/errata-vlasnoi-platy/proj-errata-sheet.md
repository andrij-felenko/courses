# ⚙️ Шаблон Hardware Errata Sheet та реалізація програмних обхідних шляхів

Під час переходу від перших зібраних зразків друкованої плати до повноцінного тестування пристрою інженер стикається з фізичними дефектами схемотехніки й трасування, які неможливо миттєво виправити повторним перезамовленням плати. Щоб лабораторія та програмісти не втрачали тижні на хаотичні спроби змусити пристрій працювати, уся інформація про знайдені аномалії зводиться в єдиний нормативний документ — **Hardware Errata Sheet** (інженерний листок дефектів апаратного забезпечення). Цей документ стандартизує опис помилок, визначає технологію лабораторних доробок (англ. *rework*) та надає точні програмні обхідні шляхи (англ. *software workarounds*) для драйверів мікроконтролера.

Нижче наведено практичний інженерний шаблон Errata Sheet для ревізії Rev 1.0 (Rev A) та повну реалізацію драйверів програмного обходу типових апаратних помилок на мовах C та C++.

---

## 1. Інженерний шаблон Hardware Errata Sheet

У виробничій практиці документ Errata оформлюється у вигляді версійного опису зведеної таблиці та детальних карток для кожного знайденого дефекту.

### Зведена таблиця статусу ревізії

| ID дефекту | Вузол схеми | Симптом / Прояв | Критичність | Стратегія порятунку | Статус у Rev B |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ERR-HW-001` | Давач IMU (`U3`) | Зависання шини I2C; SDA затиснуто в 0 В при просіданні живлення | Висока | **Software Workaround:** Ізоляція шини в High-Z + GPIO Power-cycle | Виділений LDO з сигналом EN |
| `ERR-HW-002` | Інтерфейс UART (`J2`) | Відсутній зв'язок із хостом; нульові байти в терміналі | Блокуюча | **Hardware Rework:** Перерізання трас TX/RX та монтаж перемичок 30 AWG | Виправлено перехресне трасування |
| `ERR-HW-003` | Кнопка User (`SW1`) | Шторм переривань EXTI (до 2500 переривань/с); зависання ядра | Середня | **Software Workaround:** Відключення EXTI, таймерний фільтр 10 мс | Додано RC-ланцюг (10 кОм + 100 нФ) |
| `ERR-HW-004` | Шина пам'яті SPI (`U5`) | Помилки CRC на частоті 20 МГц через високу ємність траси | Середня | **Software Workaround:** Зниження частоти до 5 МГц + Low Slew Rate | Оптимізація трасування й узгодження |

---

### Детальні картки дефектів

#### `ERR-HW-001`: Зависання давача IMU та блокування шини I2C

* **Ревізія плати:** Rev 1.0 (Rev A).
* **Симптом:** Під час тестування перехідних процесів або просідання напруги живлення нижче 2.9 В цифровий 6-осьовий давач `U3` переходить у некерований стан і затискає лінію даних SDA в логічний нуль (0.08 В). Шинні команди скидання (генерація 9 тактів SCL) не повертають давач до тями.
* **Першопричина (Root Cause):** Внутрішній кінцевий автомат (FSM) контролера I2C всередині чипа давача не має апаратного тайм-ауту шини. Спроба знеструмити давач простим вимиканням піна GPIO живлення зазнає невдачі через явище «живлення з чорного ходу» (англ. *back-powering*): струм від підтягнутих сигнальних ліній SDA/SCL протікає через внутрішні захисні ESD-діоди давача на його внутрішню шину VDD, утримуючи там напругу близько 2.4 В.
* **Вплив (Impact):** Повне блокування всієї шини I2C, неможливість опитування решти давачів на платі.
* **Тимчасовий обхід (Workaround for Rev A):** Застосувати спеціалізовану функцію скидання `sensor_power_cycle_safe()`: перед вимиканням живлення VDD мікроконтролер програмно переводить сигнальні піни SDA та SCL у стан високого імпедансу (High-Z) без підтяжок, знеструмлює датчик на 30 мс (час гарантованого розряду блокувального конденсатора 100 нФ через внутрішній опір витоку), після чого відновлює живлення, очікує 10 мс стабілізації POR та повторно ініціалізує шину.
* **Остаточне виправлення в Rev B:** Живлення датчика завести через окремий LDO-стабілізатор з виводом Enable (Power-Gating) або комутований P-MOSFET із захистом від зворотного струму.

---

#### `ERR-HW-002`: Переплутані лінії передавача та приймача UART

* **Ревізія плати:** Rev 1.0 (Rev A).
* **Симптом:** Налагоджувальний мікроконтролер не приймає жодного байта з консолі хоста, вивід логів відсутній.
* **Першопричина (Root Cause):** Помилка в схемі: вивід `TX` мікроконтролера підключено до контакту `TX` зовнішнього роз'єму замість `RX` (відсутнє перехресне з'єднання Null-Modem).
* **Вплив (Impact):** Блокуюча помилка апаратного зв'язку. Програмний обхід неможливий (піни не підтримують внутрішнє програмне перепризначення матриці I/O).
* **Тимчасовий обхід (Workaround for Rev A):** Виконати лабораторне доопрацювання (Rework):
  1. Під мікроскопом за допомогою скальпеля перерізати дві друковані доріжки між `R14`/`R15` та роз'ємом `J2`, створивши зазор ізоляції ≥ 0.5 мм.
  2. Перевірити опір ізоляції мультиметром (переконатися, що `R > 10 МОм`).
  3. Змонтувати дві дротяні перемички з емальованого дроту 30 AWG (Kynar), з'єднавши `TX` МК з `RX` роз'єму і навпаки.
  4. Зафіксувати перемички краплями фотополімерної ультрафіолетової паяльної маски.
* **Остаточне виправлення в Rev B:** Виправити трасування зв'язків у схемі та на платі.

---

#### `ERR-HW-003`: Шторм переривань на лінії користувацької кнопки

* **Ревізія плати:** Rev 1.0 (Rev A).
* **Симптом:** Одноразове натискання тактової кнопки викликає від 10 до 80 спрацьовувань переривання за 5 мс, завантажуючи центральний процесор до 100% та викликаючи спрацьовування сторожового таймера Watchdog.
* **Першопричина (Root Cause):** На схемі не передбачено апаратний RC-фільтр низьких частот для гасіння брязкоту контактів, а кнопка розведена паралельно лінії живлення сервоприводу.
* **Вплив (Impact):** Помилкові події в інтерфейсі користувача, нестабільність планувальника задач RTOS.
* **Тимчасовий обхід (Workaround for Rev A):** Повністю відключити обробку апаратних зовнішніх переривань (EXTI) для цієї лінії. Запустити періодичну системну задачу опитування входу з частотою 100 Гц (період 10 мс) із застосуванням 8-бітного зсувного регістра фільтрації стабільного вікна.
* **Остаточне виправлення в Rev B:** Встановити паралельно контактам кнопки керамічний конденсатор 100 нФ та послідовний резистор 1 кОм.

---

## 2. Реалізація драйверів програмного обходу (Software Workarounds)

Нижче наведено модулі прошивки, які реалізують безпечний перезапуск підвислого давача та таймерний антидребезг контактів без використання апаратних переривань.

Код підтримує автоматичну адаптацію залежно від прочитаної апаратної ревізії плати (`BOARD_REV_A` vs `BOARD_REV_B`).

:::tabs
```c
/* errata_workarounds.c — Реалізація програмних обхідних шляхів для Rev A (C99) */
#include <stdint.h>
#include <stdbool.h>

/* Визначення ревізій плати */
typedef enum {
    BOARD_REV_UNKNOWN = 0,
    BOARD_REV_A       = 1,
    BOARD_REV_B       = 2
} board_rev_t;

/* Емуляція регістрового доступу до апаратних пінів */
typedef enum {
    PIN_MODE_INPUT_FLOATING,
    PIN_MODE_OUTPUT_PP,
    PIN_MODE_AF_OD
} pin_mode_t;

typedef enum {
    PIN_STATE_LOW  = 0,
    PIN_STATE_HIGH = 1
} pin_state_t;

/* Прототипи платформних функцій введення/виведення */
extern void hal_gpio_set_mode(uint8_t port, uint8_t pin, pin_mode_t mode);
extern void hal_gpio_write(uint8_t port, uint8_t pin, pin_state_t state);
extern pin_state_t hal_gpio_read(uint8_t port, uint8_t pin);
extern void hal_delay_ms(uint32_t ms);
extern bool hal_i2c_init_bus(void);
extern void hal_i2c_deinit_bus(void);

/* Призначення апаратних виводів */
#define PORT_PWR   0
#define PIN_PWR    4   /* Керування VDD давача */
#define PORT_I2C   1
#define PIN_SDA    7   /* Лінія даних */
#define PIN_SCL    6   /* Лінія такту */

/* =========================================================================
 * 1. Безпечний Power-Cycle давача з ізоляцією шини (ERR-HW-001)
 * ========================================================================= */

/**
 * @brief Повний цикл безпечного скидання живлення давача.
 * Усуває паразитно підживлене блокування через ESD-діоди.
 */
bool errata_sensor_safe_power_cycle(board_rev_t rev) {
    if (rev == BOARD_REV_A) {
        /* КРОК 1: Деініціалізація апаратного контролера I2C */
        hal_i2c_deinit_bus();

        /* КРОК 2: Ізоляція шини — переведення SDA та SCL у High-Z без підтяжок */
        hal_gpio_set_mode(PORT_I2C, PIN_SDA, PIN_MODE_INPUT_FLOATING);
        hal_gpio_set_mode(PORT_I2C, PIN_SCL, PIN_MODE_INPUT_FLOATING);

        /* КРОК 3: Зняття живлення з лінії VDD */
        hal_gpio_set_mode(PORT_PWR, PIN_PWR, PIN_MODE_OUTPUT_PP);
        hal_gpio_write(PORT_PWR, PIN_PWR, PIN_STATE_LOW);

        /* КРОК 4: Витримка паузи розряджання блокувальних конденсаторів */
        hal_delay_ms(30);

        /* КРОК 5: Подача живлення */
        hal_gpio_write(PORT_PWR, PIN_PWR, PIN_STATE_HIGH);

        /* КРОК 6: Пауза стабілізації джерела живлення та внутрішнього POR давача */
        hal_delay_ms(15);

        /* КРОК 7: Повторна ініціалізація шини I2C */
        hal_gpio_set_mode(PORT_I2C, PIN_SDA, PIN_MODE_AF_OD);
        hal_gpio_set_mode(PORT_I2C, PIN_SCL, PIN_MODE_AF_OD);

        return hal_i2c_init_bus();
    } else {
        /* У ревізії B є апаратний вивід скидання RESET */
        hal_gpio_write(PORT_PWR, PIN_PWR, PIN_STATE_LOW);
        hal_delay_ms(2);
        hal_gpio_write(PORT_PWR, PIN_PWR, PIN_STATE_HIGH);
        hal_delay_ms(5);
        return true;
    }
}

/* =========================================================================
 * 2. Періодичний таймерний фільтр брязкоту контактів (ERR-HW-003)
 * ========================================================================= */

typedef struct {
    uint8_t port;
    uint8_t pin;
    uint8_t history;     /* Зсувний регістр історії вибірок */
    bool    stable_state;/* Відфільтрований стабільний стан */
} debouncer_t;

void debouncer_init(debouncer_t *deb, uint8_t port, uint8_t pin) {
    deb->port = port;
    deb->pin = pin;
    deb->history = 0xFF;
    deb->stable_state = true;
    hal_gpio_set_mode(port, pin, PIN_MODE_INPUT_FLOATING);
}

/**
 * @brief Викликається щостійно в системному таймері (наприклад, кожні 10 мс).
 * @return true, якщо зафіксовано подію натискання (перехід у LOW).
 */
bool debouncer_update(debouncer_t *deb) {
    pin_state_t raw = hal_gpio_read(deb->port, deb->pin);

    /* Зсуваємо історію та додаємо новий відлік */
    deb->history = (uint8_t)((deb->history << 1) | (raw == PIN_STATE_HIGH ? 1 : 0));

    /* Якщо всі останні 8 відліків (80 мс) стабільно нулі, фіксуємо натискання */
    if (deb->history == 0x00 && deb->stable_state == true) {
        deb->stable_state = false;
        return true; /* Подія: Кнопку натиснуто */
    }

    /* Якщо всі останні 8 відліків стабільно одиниці, фіксуємо відпускання */
    if (deb->history == 0xFF && deb->stable_state == false) {
        deb->stable_state = true;
    }

    return false;
}
```
```cpp
/* errata_workarounds.hpp — Ідіоматична обгортка обхідних шляхів (C++20) */
#pragma once
#include <cstdint>
#include <concepts>
#include <span>

enum class BoardRevision : uint8_t {
    Unknown = 0,
    RevA    = 1,
    RevB    = 2
};

enum class PinMode {
    InputFloating,
    OutputPushPull,
    AlternateOpenDrain
};

enum class PinState : bool {
    Low  = false,
    High = true
};

/* Апаратний інтерфейс абстракції */
class IGpioController {
public:
    virtual ~IGpioController() = default;
    virtual void setMode(uint8_t port, uint8_t pin, PinMode mode) = 0;
    virtual void write(uint8_t port, uint8_t pin, PinState state) = 0;
    virtual PinState read(uint8_t port, uint8_t pin) = 0;
    virtual void delayMs(uint32_t ms) = 0;
    virtual bool initI2c() = 0;
    virtual void deinitI2c() = 0;
};

/* =========================================================================
 * 1. RAII-керування живленням давача з обходом ERR-HW-001
 * ========================================================================= */
class SensorPowerManager {
public:
    SensorPowerManager(IGpioController& gpio, BoardRevision rev)
        : m_gpio(gpio), m_rev(rev) {}

    [[nodiscard]] bool safePowerCycle() noexcept {
        if (m_rev == BoardRevision::RevA) {
            // КРОК 1: Деініціалізація периферії I2C
            m_gpio.deinitI2c();

            // КРОК 2: Ізоляція сигнальних ліній (High-Z)
            m_gpio.setMode(kPortI2c, kPinSda, PinMode::InputFloating);
            m_gpio.setMode(kPortI2c, kPinScl, PinMode::InputFloating);

            // КРОК 3: Знеструмлення VDD
            m_gpio.setMode(kPortPwr, kPinPwr, PinMode::OutputPushPull);
            m_gpio.write(kPortPwr, kPinPwr, PinState::Low);

            // КРОК 4: Пауза для гарантованого розряджання ємностей
            m_gpio.delayMs(30);

            // КРОК 5: Подача VDD
            m_gpio.write(kPortPwr, kPinPwr, PinState::High);
            m_gpio.delayMs(15);

            // КРОК 6: Відновлення конфігурації шини I2C
            m_gpio.setMode(kPortI2c, kPinSda, PinMode::AlternateOpenDrain);
            m_gpio.setMode(kPortI2c, kPinScl, PinMode::AlternateOpenDrain);

            return m_gpio.initI2c();
        } else {
            // У Rev B використовується нативне апаратне скидання
            m_gpio.write(kPortPwr, kPinPwr, PinState::Low);
            m_gpio.delayMs(2);
            m_gpio.write(kPortPwr, kPinPwr, PinState::High);
            m_gpio.delayMs(5);
            return true;
        }
    }

private:
    static constexpr uint8_t kPortPwr = 0;
    static constexpr uint8_t kPinPwr  = 4;
    static constexpr uint8_t kPortI2c = 1;
    static constexpr uint8_t kPinSda  = 7;
    static constexpr uint8_t kPinScl  = 6;

    IGpioController& m_gpio;
    BoardRevision    m_rev;
};

/* =========================================================================
 * 2. Шаблонний антидребезговий фільтр стабільного вікна (ERR-HW-003)
 * ========================================================================= */
template <size_t HistoryDepth = 8>
class SoftwareDebouncer {
    static_assert(HistoryDepth <= 32, "History depth must fit in uint32_t");

public:
    constexpr SoftwareDebouncer(uint8_t port, uint8_t pin) noexcept
        : m_port(port), m_pin(pin), m_history(kMaskAllOnes), m_stableState(true) {}

    void init(IGpioController& gpio) noexcept {
        gpio.setMode(m_port, m_pin, PinMode::InputFloating);
    }

    [[nodiscard]] bool update(IGpioController& gpio) noexcept {
        const auto raw = gpio.read(m_port, m_pin);
        const uint32_t bit = (raw == PinState::High) ? 1U : 0U;

        m_history = ((m_history << 1) | bit) & kMaskAllOnes;

        // Перевірка стабільного натискання (усі нулі)
        if (m_history == 0 && m_stableState) {
            m_stableState = false;
            return true; // Подія: натиснуто
        }

        // Перевірка стабільного відпускання (усі одиниці)
        if (m_history == kMaskAllOnes && !m_stableState) {
            m_stableState = true;
        }

        return false;
    }

    [[nodiscard]] bool isPressed() const noexcept {
        return !m_stableState;
    }

private:
    static constexpr uint32_t kMaskAllOnes = (1ULL << HistoryDepth) - 1ULL;

    uint8_t  m_port;
    uint8_t  m_pin;
    uint32_t m_history;
    bool     m_stableState;
};
```
:::
