# ⚙️ Реалізація драйвера матриці Чарліплексингу: безперервне сканування, керування яскравістю та захист від артефактів

Цей проект реалізує закінчений, апаратно незалежний драйвер світлодіодної матриці Чарліплексингу для мікроконтролерів різних архітектур. Програмне забезпечення розв'язує три обов'язкові інженерні задачі комерційної схемотехніки:
1. **Повне звільнення головного циклу обчислень**. Сканування матриці винесене в періодичний обробник апаратного переривання таймера, що забезпечує стабільну частоту розгортки кадру без дрижання яскравості незалежно від складності основної програми.
2. **Апаратний захист від артефактів перемикання (Glitch Protection)**. У драйвер вбудовано фазу мертвого часу (dead-time), яка вимикає всі лінії перед кожною зміною стану й запобігає виникненню короткочасних наскрізних струмів через паразитні ємності друкованої плати.
3. **Плавне багаторівневе регулювання яскравості (Software PWM)**. Кожен світлодіод матриці має індивідуальне значення яскравості в кадровому буфері, яке модулюється програмним таймерним лічильником.

---

### 1. Архітектура керування станами виводів та апаратна абстракція

Для коректної роботи матриці Чарліплексингу кожна цифрова лінія мікроконтролера повинна мати змогу швидко й надійно перемикатися між трьома фізичними станами. У мікроконтролерах сімейств AVR (ATmega, ATtiny), ARM Cortex-M (STM32, NXP) та Espressif (ESP32) ці стани конфігуруються через регістри напрямку (Direction) та регістри вихідних даних (Output Data):

- **Стан `HIGH`**: Вивід налаштовано як вихід (`OUTPUT`), у вихідний регістр записано 1 (`V[CC]`). Вивід віддає струм у коло світлодіода (працює як current source).
- **Стан `LOW`**: Вивід налаштовано як вихід (`OUTPUT`), у вихідний регістр записано 0 (`0 В`). Вивід забирає струм із кола в землю (працює як current sink).
- **Стан `Hi-Z`**: Вивід налаштовано як вхід (`INPUT`), а внутрішні підтягувальні резистори (`Pull-Up` та `Pull-Down`) **примусово вимкнені**. У цьому режимі вивід має надвисокий власний опір (понад сотні мегаом), практично від'єднуючись від діодної сітки.

Кожен окремий світлодіод у коді описується компактною структурою, яка зберігає індекс виводу-анода та індекс виводу-катода. Для `N = 4` ліній зв'язку матриця містить `4 · (4 − 1) = 12` світлодіодних слотів.

---

### 2. Реалізація драйвера на C та ідіоматичному C++

Нижче наведено закінчений модуль сканування. Реалізація мовою C побудована на структурованому контексті з передачею покажчиків на апаратний рівень (HAL). Реалізація на C++ використовує шаблонний клас із параметризацією кількості виводів під час компіляції (`constexpr`), що усуває накладні витрати на динамічне виділення пам'яті й гарантує повну типобезпеку та інкапсуляцію стану.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CHARLIE_PINS_COUNT 4
#define CHARLIE_LEDS_COUNT (CHARLIE_PINS_COUNT * (CHARLIE_PINS_COUNT - 1))
#define CHARLIE_PWM_LEVELS 8

typedef struct {
    uint8_t anode_pin;
    uint8_t cathode_pin;
} CharlieLed;

/* Статична таблиця відповідності індексів світлодіодів і пар виводів */
static const CharlieLed LED_MAP[CHARLIE_LEDS_COUNT] = {
    {0, 1}, {1, 0}, {0, 2}, {2, 0},
    {0, 3}, {3, 0}, {1, 2}, {2, 1},
    {1, 3}, {3, 1}, {2, 3}, {3, 2}
};

/* Таблиця апаратних функцій зворотного виклику */
typedef struct {
    void (*set_output_high)(uint8_t pin_idx);
    void (*set_output_low)(uint8_t pin_idx);
    void (*set_input_hiz)(uint8_t pin_idx);
} CharlieHal;

typedef struct {
    uint8_t brightness[CHARLIE_LEDS_COUNT];
    uint8_t current_led;
    uint8_t pwm_cycle;
    const CharlieHal *hal;
} CharlieDriver;

void charlie_init(CharlieDriver *drv, const CharlieHal *hal) {
    drv->hal = hal;
    drv->current_led = 0;
    drv->pwm_cycle = 0;
    memset(drv->brightness, 0, sizeof(drv->brightness));
    
    /* Усі лінії за замовчуванням переводимо у безпечний стан Hi-Z */
    for (uint8_t i = 0; i < CHARLIE_PINS_COUNT; ++i) {
        drv->hal->set_input_hiz(i);
    }
}

void charlie_set_brightness(CharlieDriver *drv, uint8_t led_idx, uint8_t val) {
    if (led_idx < CHARLIE_LEDS_COUNT) {
        if (val >= CHARLIE_PWM_LEVELS) val = CHARLIE_PWM_LEVELS - 1;
        drv->brightness[led_idx] = val;
    }
}

/* Обробник кроку сканування (викликається в перериванні таймера з частотою 5–10 кГц) */
void charlie_step(CharlieDriver *drv) {
    /* 1. Фаза мертвого часу (Dead-time): гасимо всі лінії перед новою комутацією */
    for (uint8_t i = 0; i < CHARLIE_PINS_COUNT; ++i) {
        drv->hal->set_input_hiz(i);
    }

    uint8_t led = drv->current_led;
    
    /* 2. Порівняння з порогом ШІМ: запалюємо діод лише при перевищенні лічильника */
    if (drv->brightness[led] > drv->pwm_cycle) {
        const CharlieLed *pair = &LED_MAP[led];
        drv->hal->set_output_high(pair->anode_pin);
        drv->hal->set_output_low(pair->cathode_pin);
    }

    /* 3. Циклічний інкремент індексу світлодіода та фази ШІМ */
    drv->current_led++;
    if (drv->current_led >= CHARLIE_LEDS_COUNT) {
        drv->current_led = 0;
        drv->pwm_cycle = (drv->pwm_cycle + 1) % CHARLIE_PWM_LEVELS;
    }
}
```
```cpp
#include <array>
#include <span>
#include <cstdint>
#include <algorithm>

template <size_t PinCount>
class CharlieplexMatrix {
public:
    static constexpr size_t LedCount = PinCount * (PinCount - 1);
    static constexpr uint8_t MaxBrightness = 7;

    struct LedPinPair {
        uint8_t anode;
        uint8_t cathode;
    };

    struct HardwarePort {
        void (*setHigh)(uint8_t pin);
        void (*setLow)(uint8_t pin);
        void (*setHiZ)(uint8_t pin);
    };

    explicit constexpr CharlieplexMatrix(HardwarePort hal) noexcept
        : hal_(hal), currentLed_(0), pwmCounter_(0), brightness_{} {}

    void init() const noexcept {
        for (uint8_t i = 0; i < PinCount; ++i) {
            hal_.setHiZ(i);
        }
    }

    void setBrightness(size_t ledIndex, uint8_t level) noexcept {
        if (ledIndex < LedCount) {
            brightness_[ledIndex] = std::min(level, MaxBrightness);
        }
    }

    void fill(uint8_t level) noexcept {
        brightness_.fill(std::min(level, MaxBrightness));
    }

    /* Виклик у періодичному перериванні таймера */
    void tick() noexcept {
        /* Фаза мертвого часу (dead-time): гарантовано ізолюємо всі виводи */
        for (uint8_t i = 0; i < PinCount; ++i) {
            hal_.setHiZ(i);
        }

        const size_t led = currentLed_;
        if (brightness_[led] > pwmCounter_) {
            const auto pair = computeLedPair(led);
            hal_.setHigh(pair.anode);
            hal_.setLow(pair.cathode);
        }

        currentLed_ = (currentLed_ + 1) % LedCount;
        if (currentLed_ == 0) {
            pwmCounter_ = (pwmCounter_ + 1) % (MaxBrightness + 1);
        }
    }

    [[nodiscard]] static constexpr LedPinPair computeLedPair(size_t index) noexcept {
        size_t count = 0;
        for (uint8_t a = 0; a < PinCount; ++a) {
            for (uint8_t c = 0; c < PinCount; ++c) {
                if (a != c) {
                    if (count == index) return {a, c};
                    count++;
                }
            }
        }
        return {0, 0};
    }

private:
    HardwarePort hal_;
    size_t currentLed_;
    uint8_t pwmCounter_;
    std::array<uint8_t, LedCount> brightness_;
};
```
:::

---

### 3. Інтеграція з апаратними таймерами на різних платформах

Для забезпечення стабільної кадрової частоти без видимого оком мерехтіння функція сканування повинна викликатися з суворою періодичністю. Необхідна частота спрацьовування апаратного таймера розраховується за формулою:

```
f[timer] = f[frame] · L · N[pwm]
```

Де:
- `f[frame]` — бажана частота оновлення повного зображення (не менше 100 Гц для виключення втоми очей).
- `L = N · (N − 1)` — загальна кількість світлодіодів у матриці.
- `N[pwm]` — кількість дискретних градацій яскравості (наприклад, 8 рівнів).

Для `N = 4` виводів (`L = 12` діодів), `f[frame] = 100 Гц` та `N[pwm] = 8` частота переривань таймера дорівнює `100 · 12 · 8 = 9600 Гц` (період таймера близько `104 мкс`).

Нижче наведено приклади платформно-залежних адаптерів апаратного рівня (HAL) для Arduino (AVR), STM32 (HAL/LL) та ESP-IDF (ESP32):

:::tabs
```arduino
#include <Arduino.h>

static const uint8_t PINS[4] = {2, 3, 4, 5};

void halSetHigh(uint8_t pin) {
    uint8_t p = PINS[pin];
    pinMode(p, OUTPUT);
    digitalWrite(p, HIGH);
}

void halSetLow(uint8_t pin) {
    uint8_t p = PINS[pin];
    pinMode(p, OUTPUT);
    digitalWrite(p, LOW);
}

void halSetHiZ(uint8_t pin) {
    uint8_t p = PINS[pin];
    pinMode(p, INPUT);
    digitalWrite(p, LOW); // Примусово вимикаємо внутрішній Pull-Up резистор
}
```
```stm32
#include "stm32f4xx_hal.h"

static GPIO_TypeDef* const PORTS[4] = {GPIOA, GPIOA, GPIOA, GPIOA};
static const uint16_t PINS[4] = {GPIO_PIN_0, GPIO_PIN_1, GPIO_PIN_2, GPIO_PIN_3};

void hal_set_high(uint8_t pin) {
    GPIO_InitTypeDef g = {0};
    g.Pin = PINS[pin];
    g.Mode = GPIO_MODE_OUTPUT_PP;
    g.Pull = GPIO_NOPULL;
    g.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(PORTS[pin], &g);
    HAL_GPIO_WritePin(PORTS[pin], PINS[pin], GPIO_PIN_SET);
}

void hal_set_low(uint8_t pin) {
    GPIO_InitTypeDef g = {0};
    g.Pin = PINS[pin];
    g.Mode = GPIO_MODE_OUTPUT_PP;
    g.Pull = GPIO_NOPULL;
    g.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(PORTS[pin], &g);
    HAL_GPIO_WritePin(PORTS[pin], PINS[pin], GPIO_PIN_RESET);
}

void hal_set_hiz(uint8_t pin) {
    GPIO_InitTypeDef g = {0};
    g.Pin = PINS[pin];
    g.Mode = GPIO_MODE_INPUT;
    g.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(PORTS[pin], &g);
}
```
```esp-idf
#include "driver/gpio.h"

static const gpio_num_t PINS[4] = {GPIO_NUM_16, GPIO_NUM_17, GPIO_NUM_18, GPIO_NUM_19};

void hal_esp_high(uint8_t pin) {
    gpio_num_t p = PINS[pin];
    gpio_set_direction(p, GPIO_MODE_OUTPUT);
    gpio_set_level(p, 1);
}

void hal_esp_low(uint8_t pin) {
    gpio_num_t p = PINS[pin];
    gpio_set_direction(p, GPIO_MODE_OUTPUT);
    gpio_set_level(p, 0);
}

void hal_esp_hiz(uint8_t pin) {
    gpio_num_t p = PINS[pin];
    gpio_set_direction(p, GPIO_MODE_INPUT);
    gpio_set_pull_mode(p, GPIO_FLOATING);
}
```
:::

---

### 4. Діагностика типових проблем та інженерні пастки

Під час практичного запуску матриць Чарліплексингу розробники найчастіше стикаються з трьома схемотехнічними дефектами:

1. **Паразитне підсвічування діодів у темряві через залишковий Pull-Up.** Якщо при переході в стан `Hi-Z` мікроконтролер переводиться в режим входу (`INPUT`), але у вихідному регістрі залишається одиниця, апаратна логіка підключає внутрішній підтягувальний резистор (номіналом 20–50 кОм). Струм витоку через цей резистор (`~0.1 мА`) є достатнім, щоб високочутливі сучасні світлодіоди ледь помітно світилися. Для перевірки на вимкненому індикаторі вимірюють напругу на виводах відносно землі: якщо вона відмінна від нуля й становить 1.5–2.5 В, це свідчить про активну підтяжку. Рішення: завжди скидати вихідний біт у 0 або явно вимикати підтяжки (`GPIO_NOPULL` чи `GPIO_FLOATING`).
2. **Артефакти перемикання каналів (комутаційні спалахи).** Якщо новий активний канал вмикається раніше, ніж відключається старий, на часовий інтервал у кілька десятків наносекунд виникає хибна конфігурація виходів. Це викликає видимі спалахи випадкових діодів по всій платі. Рішення: обов'язкове дотримання правила мертвого часу (усі піни перевести в `Hi-Z` перед конфігурацією нової пари). На високочастотних мікроконтролерах (STM32, ESP32) між фазою вимкнення та увімкнення рекомендується вставляти 1–2 апаратні інструкції `NOP` (No Operation).
3. **Просідання живлення через пікові імпульсні струми.** Оскільки в імпульсі діод споживає від 15 до 30 мА, синхронне перемикання ліній викликає високочастотний шум по шині живлення `V[CC]`. Якщо плата не має достатньої локальної ємності, короткочасне падіння напруги може викликати збій тактового генератора або перезавантаження ядра мікроконтролера через спрацьовування детектора коричневого згасання (Brown-Out Detector, BOD). Безпосередньо біля виводів живлення мікроконтролера необхідно встановлювати блокувальний керамічний конденсатор ємністю 0.1–1.0 мкФ із низьким еквівалентним послідовним опором (Low ESR).
4. **Осцилографічна перевірка форми сигналів.** При підключенні щупа осцилографа до лінії Чарліплексингу в нормі спостерігається трирівневий ступінчастий сигнал: вершина імпульсу `+V[CC]` (фаза джерела), полиця `0 В` (фаза стоку) та середня зона `V[CC] / 2` у моменти, коли лінія перебуває у `Hi-Z` і ділить напругу через закриті діоди. Будь-яка асиметрія чи спотворення форми полиці свідчать про пробитий діод або порушення контакту.
