# 📋 Еталонний контракт інтерфейсу BSP (Board Support Package API)

Пакет підтримки плати (*Board Support Package*, BSP) є програмним шаром, який ізолює топологію конкретної друкованої плати, схему підключення мікросхем та вендорні бібліотеки мікроконтролера від чистої бізнес-логіки застосунку. Цей контракт визначає відкритий інтерфейс взаємодії: структури даних фізичних величин, коди помилок, функції керування життєвим циклом, комутації живлення периферійних доменів, індикації та зчитування аналогових параметрів без витоку апаратних адрес чи номерів виводів.

Нижче наведено формальну специфікацію інтерфейсу на мовах C та C++, вимоги до потокобезпечності, обмеження контексту переривань, часові бюджети та правила обробки нештатних станів.

---

### Модель станів та коди помилок (Status Codes)

Кожна функція контракту BSP, яка виконує операції введення-виведення або змінює стан платформи, повертає статус виконання `bsp_status_t`. Використання єдиного переліку кодів помилок гарантує, що застосунок отримує однозначну інформацію про причину збою (таймаут шини, некоректний аргумент, відсутність живлення) без необхідності аналізувати вендорозалежні регістри помилок мікроконтролера.

:::tabs
```c
#ifndef BSP_STATUS_H
#define BSP_STATUS_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Статуси повернення функцій BSP.
 */
typedef enum {
    BSP_STATUS_OK                 =  0, /**< Операцію виконано успішно */
    BSP_STATUS_ERR_INVALID_PARAM  = -1, /**< Некоректний покажчик або значення аргументу */
    BSP_STATUS_ERR_NOT_INIT       = -2, /**< Периферію або домен не було ініціалізовано */
    BSP_STATUS_ERR_BUSY           = -3, /**< Апаратна шина зайнята іншою транзакцією */
    BSP_STATUS_ERR_TIMEOUT        = -4, /**< Закінчився час очікування апаратної відповіді */
    BSP_STATUS_ERR_BUS_FAULT      = -5, /**< Апаратна помилка шини (NACK, лінія затиснута в 0) */
    BSP_STATUS_ERR_POWER_FAULT    = -6, /**< Збій живлення або неприпустима просадка напруги */
    BSP_STATUS_ERR_UNSUPPORTED    = -7  /**< Операція не підтримується поточною ревізією плати */
} bsp_status_t;

#endif /* BSP_STATUS_H */
```
```cpp
#ifndef BSP_STATUS_HPP
#define BSP_STATUS_HPP

#include <cstdint>
#include <string_view>

namespace bsp {

/**
 * @brief Сильно типізований перелік статусів помилок BSP.
 */
enum class Status : int32_t {
    Ok               =  0,
    InvalidParam     = -1,
    NotInitialized   = -2,
    Busy             = -3,
    Timeout          = -4,
    BusFault         = -5,
    PowerFault       = -6,
    Unsupported      = -7
};

[[nodiscard]] constexpr std::string_view status_to_string(Status s) noexcept {
    switch (s) {
        case Status::Ok:             return "OK";
        case Status::InvalidParam:   return "Invalid parameter";
        case Status::NotInitialized: return "Subsystem not initialized";
        case Status::Busy:           return "Hardware bus busy";
        case Status::Timeout:        return "Hardware timeout";
        case Status::BusFault:       return "Bus transaction fault";
        case Status::PowerFault:     return "Power rail fault";
        case Status::Unsupported:    return "Operation unsupported";
    }
    return "Unknown status";
}

} // namespace bsp

#endif /* BSP_STATUS_HPP */
```
:::

#### Механізм диференціації та обробки помилок

Застосунок використовує коди помилок BSP для ухвалення рішень щодо стратегії відновлення:
1. `BSP_STATUS_ERR_INVALID_PARAM`: Помилка програмування (передано `NULL` або неіснуючий ідентифікатор). Застосунок фіксує аварію через системний логер і не виконує повторних спроб.
2. `BSP_STATUS_ERR_BUSY`: Тимчасовий стан блокування ресурсу іншою задачею. Застосунок робить коротку паузу (наприклад, 1–5 мс) та повторює запит.
3. `BSP_STATUS_ERR_TIMEOUT`: Сенсор або мікросхема пам'яті не відповіли у відведений інтервал часу. Свідчить про тимчасову перешкоду на лінії зв'язку; вимагає обмеженої кількості повторів (до 3 спроб).
4. `BSP_STATUS_ERR_BUS_FAULT`: Апаратний збій шини (відсутність сигналу підтвердження ACK, затискання лінії SDA на землю). BSP всередині запускає апаратну процедуру відновлення (генерація 9 імпульсів SCL), після чого повертає помилку застосунку.
5. `BSP_STATUS_ERR_POWER_FAULT`: Критичне падіння напруги живлення під час вимірювання (просадка батареї). Сигнал для негайного аварійного збереження стану у незалежну пам'ять та переходу в режим глибокого сну.

---

### Типи даних та структури фізичних величин

Контракт BSP оперує стандартизованими структурами у загальноприйнятих фізичних одиницях вимірювання (мілівольти, соті частки градуса Цельсія, паскалі, відсотки заряду). Це повністю усуває необхідність передавати у високорівневі алгоритми «сирі» 12-бітні значення кодів АЦП чи невідкалібровані байти регістрів сенсорів.

:::tabs
```c
#ifndef BSP_TYPES_H
#define BSP_TYPES_H

#include "bsp_status.h"

/**
 * @brief Логічні ідентифікатори індикаторів плати.
 */
typedef enum {
    BOARD_LED_ID_SYSTEM_STATUS = 0, /**< Системний світлодіод стану (Heartbeat) */
    BOARD_LED_ID_WARNING       = 1, /**< Індикатор попередження / аварії */
    BOARD_LED_ID_COMMS         = 2, /**< Індикатор активності бездротового зв'язку */
    BOARD_LED_ID_MAX
} board_led_id_t;

/**
 * @brief Логічний стан індикатора.
 */
typedef enum {
    BOARD_LED_STATE_OFF = 0,
    BOARD_LED_STATE_ON  = 1
} board_led_state_t;

/**
 * @brief Керовані домени живлення плати.
 */
typedef enum {
    BOARD_POWER_DOMAIN_SENSORS  = 0, /**< Лінія живлення зовнішніх давачів (I2C/SPI) */
    BOARD_POWER_DOMAIN_RADIO    = 1, /**< Модуль радіозв'язку (LoRa/BLE) */
    BOARD_POWER_DOMAIN_DISPLAY  = 2, /**< РК/OLED дисплей та його підсвітка */
    BOARD_POWER_DOMAIN_MAX
} board_power_domain_t;

/**
 * @brief Режими енергозбереження мікроконтролера.
 */
typedef enum {
    BOARD_SLEEP_MODE_LIGHT = 0, /**< Сон зі швидким пробудженням від таймера */
    BOARD_SLEEP_MODE_DEEP  = 1  /**< Глибокий сон з мінімальним струмом споживання */
} board_sleep_mode_t;

/**
 * @brief Метрики стану акумуляторної батареї.
 */
typedef struct {
    uint16_t voltage_mv;       /**< Напруга батареї в мілівольтах (наприклад, 3850 мВ) */
    uint8_t  charge_percent;   /**< Розрахований залишковий заряд у відсотках (0..100) */
    bool     is_charging;      /**< Прапорець підключення зовнішнього зарядного пристрою */
    bool     is_critical_low;  /**< Прапорець падіння напруги нижче безпечного порогу */
} board_battery_metrics_t;

/**
 * @brief Метрики навколишнього середовища.
 */
typedef struct {
    int16_t  temperature_centi_c; /**< Температура в сотих частках °C (2450 = 24.50 °C) */
    uint32_t pressure_pa;         /**< Атмосферний тиск у паскалях (101325 Па) */
    uint16_t humidity_centi_pct;  /**< Відносна вологість у сотих частках % (6540 = 65.40%) */
} board_env_metrics_t;

#endif /* BSP_TYPES_H */
```
```cpp
#ifndef BSP_TYPES_HPP
#define BSP_TYPES_HPP

#include "bsp_status.hpp"
#include <cstdint>

namespace bsp {

enum class LedId : uint8_t {
    SystemStatus = 0,
    Warning      = 1,
    Comms        = 2
};

enum class LedState : uint8_t {
    Off = 0,
    On  = 1
};

enum class PowerDomain : uint8_t {
    Sensors = 0,
    Radio   = 1,
    Display = 2
};

enum class SleepMode : uint8_t {
    Light = 0,
    Deep  = 1
};

struct BatteryMetrics {
    uint16_t voltage_mv{0};
    uint8_t  charge_percent{0};
    bool     is_charging{false};
    bool     is_critical_low{false};
};

struct EnvironmentMetrics {
    int16_t  temperature_centi_c{0};
    uint32_t pressure_pa{0};
    uint16_t humidity_centi_pct{0};

    [[nodiscard]] constexpr float temperature_celsius() const noexcept {
        return static_cast<float>(temperature_centi_c) / 100.0f;
    }

    [[nodiscard]] constexpr float humidity_percent() const noexcept {
        return static_cast<float>(humidity_centi_pct) / 100.0f;
    }
};

} // namespace bsp

#endif /* BSP_TYPES_HPP */
```
:::

#### Обґрунтування цілочисельного формату з фіксованою комою

Для передачі температури та вологості контракт BSP свідомо використовує цілочисельні типи з фіксованим масштабом:
- `temperature_centi_c`: значення в сотих частках градуса Цельсія (`int16_t`). Діапазон від `-327.68 °C` до `+327.67 °C` повністю перекриває промисловий діапазон давачів (`-40 °C .. +125 °C`).
- `humidity_centi_pct`: вологість у сотих частках відсотка (`uint16_t`). Значення `6540` відповідає `65.40%` відносної вологості.

Цей вибір зумовлений двома інженерними факторами:
1. **Відсутність апаратного блоку FPU на молодших ядрах**: На мікроконтролерах ARM Cortex-M0, Cortex-M0+ або RISC-V RV32EC операції з числами з плаваючою комою `float` емулюються програмно через бібліотеку `libgcc`, що збільшує розмір прошивки на 4–8 КБ та сповільнює обчислення в 20–50 разів.
2. **Точність та детермінізм**: Цілочисельні дані не мають проблем із накопиченням похибки округлення двійкових дробів IEEE 754, легко пакуються у бінарні мережеві пакети (CBOR, Protocol Buffers) без потреби у платформозалежній серіалізації.

---

### Специфікація функцій контракту BSP

Контракт описує повний набір сервісів платформи: керування життєвим циклом, конфігурація периферії, комутація живлення, читання фізичних параметрів та переведення в енергоощадний сон.

:::tabs
```c
#ifndef BSP_INTERFACE_H
#define BSP_INTERFACE_H

#include "bsp_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Повна ініціалізація апаратної плати.
 * 
 * Конфігурує системне тактування мікроконтролера, налаштовує стандартні стани
 * ліній GPIO, ініціалізує шини I2C/SPI, вимикає невикористані силові ключі.
 * 
 * @return BSP_STATUS_OK у разі успіху, або код помилки периферії.
 */
bsp_status_t board_init(void);

/**
 * @brief Деініціалізація та повернення плати у вихідний безпечний стан.
 */
bsp_status_t board_deinit(void);

/**
 * @brief Керування станом системного світлодіода.
 * 
 * Автоматично враховує схемотехнічну полярність (Active-High / Active-Low)
 * та режим виводу (Push-Pull / Open-Drain).
 * 
 * @param led   Ідентифікатор світлодіода.
 * @param state Бажаний логічний стан (ON / OFF).
 */
bsp_status_t board_led_set(board_led_id_t led, board_led_state_t state);

/**
 * @brief Перемикання стану світлодіода на протилежний.
 */
bsp_status_t board_led_toggle(board_led_id_t led);

/**
 * @brief Комутація живлення визначеного периферійного домену.
 * 
 * Керує затвором силового ключа (P-MOSFET / перемикач навантаження), витримує
 * обов'язкову затримку заряду блокувальних конденсаторів та переводить лінії
 * комунікаційних шин у високоімпедансний стан при вимкненні (для захисту від витоків).
 * 
 * @param domain Ідентифікатор домену живлення.
 * @param enable true — увімкнути живлення, false — знеструмити домен.
 */
bsp_status_t board_power_domain_set(board_power_domain_t domain, bool enable);

/**
 * @brief Зчитування поточних метрик акумуляторної батареї.
 * 
 * Запускає вимірювання АЦП, калібрує результат за внутрішнім джерелом опорної напруги
 * Vrefint, перераховує коефіцієнт резистивного дільника та обчислює залишковий відсоток.
 * 
 * @param[out] out_metrics Покажчик на вихідну структуру метрик.
 */
bsp_status_t board_get_battery_metrics(board_battery_metrics_t *out_metrics);

/**
 * @brief Отримання комплексних кліматичних метрик від сенсорів плати.
 * 
 * Виконує опитування фізичних мікросхем сенсорів (наприклад, BME280 / SHT30)
 * через шину I2C, обробляє та перевіряє контрольні суми і повертає готові фізичні дані.
 * 
 * @param[out] out_env Покажчик на структуру кліматичних вимірювань.
 */
bsp_status_t board_read_environment(board_env_metrics_t *out_env);

/**
 * @brief Переведення плати у режим глибокого сну.
 * 
 * Вимикає живлення зовнішніх сенсорів, конфігурує виводи в аналоговий режим (Hi-Z),
 * налаштовує джерело пробудження (RTC таймер або зовнішня кнопка) та зупиняє ядро MCU.
 * 
 * @param mode       Режим сну (Light / Deep).
 * @param timeout_ms Час сну в мілісекундах (0 — сон до зовнішнього переривання).
 */
bsp_status_t board_enter_low_power(board_sleep_mode_t mode, uint32_t timeout_ms);

/**
 * @brief Отримання монотонного системного часу від старту плати.
 * @return Час у мілісекундах.
 */
uint32_t board_get_tick_ms(void);

/**
 * @brief Блокуюча калібрована мікросекундна затримка.
 */
void board_delay_us(uint32_t us);

#ifdef __cplusplus
}
#endif

#endif /* BSP_INTERFACE_H */
```
```cpp
#ifndef BSP_INTERFACE_HPP
#define BSP_INTERFACE_HPP

#include "bsp_types.hpp"
#include <expected>
#include <chrono>

namespace bsp {

/**
 * @brief Абстрактний інтерфейс пакету підтримки плати для C++.
 */
class IBoardSupport {
public:
    virtual ~IBoardSupport() = default;

    [[nodiscard]] virtual Status init() noexcept = 0;
    [[nodiscard]] virtual Status deinit() noexcept = 0;

    [[nodiscard]] virtual Status led_set(LedId led, LedState state) noexcept = 0;
    [[nodiscard]] virtual Status led_toggle(LedId led) noexcept = 0;

    [[nodiscard]] virtual Status power_domain_set(PowerDomain domain, bool enable) noexcept = 0;

    [[nodiscard]] virtual std::expected<BatteryMetrics, Status> get_battery_metrics() noexcept = 0;
    [[nodiscard]] virtual std::expected<EnvironmentMetrics, Status> read_environment() noexcept = 0;

    [[nodiscard]] virtual Status enter_low_power(SleepMode mode, std::chrono::milliseconds timeout) noexcept = 0;
    [[nodiscard]] virtual std::chrono::milliseconds get_uptime() const noexcept = 0;
    virtual void delay(std::chrono::microseconds us) const noexcept = 0;
};

/**
 * @brief RAII-обгортка для автоматичного знеструмлення периферійного домену.
 */
class [[nodiscard]] PowerDomainGuard {
public:
    PowerDomainGuard(IBoardSupport& bsp, PowerDomain domain)
        : bsp_(bsp), domain_(domain), active_(false) {
        if (bsp_.power_domain_set(domain_, true) == Status::Ok) {
            active_ = true;
        }
    }

    ~PowerDomainGuard() {
        if (active_) {
            bsp_.power_domain_set(domain_, false);
        }
    }

    [[nodiscard]] bool is_active() const noexcept { return active_; }

    PowerDomainGuard(const PowerDomainGuard&) = delete;
    PowerDomainGuard& operator=(const PowerDomainGuard&) = delete;
    PowerDomainGuard(PowerDomainGuard&&) noexcept = default;

private:
    IBoardSupport& bsp_;
    PowerDomain domain_;
    bool active_;
};

} // namespace bsp

#endif /* BSP_INTERFACE_HPP */
```
:::

---

### Детальні контракти та часові бюджети функцій

Кожна функція інтерфейсу накладає строгі зобов'язання на реалізацію та визначає межі допустимого часу виконання.

#### 1. Функція `board_init()`
- **Передумови (*Preconditions*)**: Напруга живлення мікроконтролера стабілізувалася вище порогу BOR (зазвичай > 2.0 В).
- **Постумови (*Postconditions*)**: Усі лінії GPIO приведені до безпечного початкового стану (силові ключі гарантовано розімкнені, лінії світлодіодів вимкнені, вільні виводи переведені в аналоговий режим Hi-Z). Системні шини I2C/SPI налаштовані на робочі частоти.
- **Часовий бюджет**: Не більше 50 мс для повного виходу на штатну тактову частоту з урахуванням часу стабілізації кварцового резонатора HSE.

#### 2. Функція `board_power_domain_set()`
- **Передумови**: Плату ініціалізовано викликом `board_init()`.
- **Постумови**: При ввімкненні (`enable = true`) живлення на лініях VDD сенсорів стабілізувалося, а лінії шини переведені в режим передачі даних. При вимкненні (`enable = false`) цифрові виводи попередньо переведені в стан високого імпедансу для запобігання паразитарному живленню через ESD-діоди мікросхем.
- **Часовий бюджет**: При ввімкненні функція блокує виконання на 10–20 мс для плавного заряду блокувальних конденсаторів домену та уникнення просадки шини живлення.

#### 3. Функція `board_get_battery_metrics()`
- **Передумови**: Аналого-цифровий перетворювач мікроконтролера сконфігуровано.
- **Постумови**: Структура заповнена значенням напруги, скоригованим за калібрувальною константою Vrefint. Повертається `is_critical_low = true`, якщо напруга впала нижче 3000 мВ (для стандартних літій-іонних елементів).
- **Часовий бюджет**: Не більше 1.5 мс на повний цикл оцифрування каналів АЦП з апаратним усередненням 16 вибірок.

#### 4. Функція `board_read_environment()`
- **Передумови**: Домен `BOARD_POWER_DOMAIN_SENSORS` попередньо увімкнено щонайменше за 15 мс до виклику.
- **Постумови**: Повертаються валідовані фізичні дані. У разі апаратного збою шини I2C повертається статус `BSP_STATUS_ERR_BUS_FAULT`, при цьому BSP виконує спробу апаратного скидання шини генерацією 9 тактів SCL.
- **Часовий бюджет**: Не більше 25 мс при роботі шини I2C на швидкості 100 кГц (з урахуванням часу перетворення внутрішнього АЦП сенсора).

---

### Інваріанти, потокобезпечність та контекстні обмеження

1. **Ізоляція викликів переривань**: Усі функції контракту, які виконують блокуючий обмін даними по шинах I2C/SPI (`board_read_environment()`) або містять затримки стабілізації живлення (`board_power_domain_set()`), мають викликатися **виключно з потокового контексту (Thread Context / Super-loop / RTOS Task)**. Виклик таких функцій з обробників переривань (ISR) заборонений, оскільки це призводить до блокування пріоритетних переривань та порушення вимог реального часу. Єдиний виняток — функції атомарного опитування `board_get_tick_ms()` та швидкі операції `board_led_set()`, які можуть бути безпечно викликані з ISR, якщо вони реалізовані через атомарні бітові операції (наприклад, регістри `BSRR` у Cortex-M).
2. **Потокобезпечність у багатозадачному середовищі (RTOS)**: Якщо одна фізична шина I2C або SPI спільно використовується кількома драйверами в різних задачах FreeRTOS чи Zephyr, реалізація BSP зобов'язана захищати транзакції шини внутрішнім м'ютексом (*Mutex*) із підтримкою успадкування пріоритетів (*Priority Inheritance*). Застосунок звільняється від необхідності синхронізувати доступ до апаратних шин вручну.
3. **Гарантія безпечного засинання**: Функція `board_enter_low_power()` гарантує, що перед відключенням системного генератора тактової частоти всі активні транзакції DMA та UART завершені, черги передачі спустошені, а лінії GPIO приведені до стану, який унеможливлює виникнення витоків струму через зовнішні підтягувальні резистори.
