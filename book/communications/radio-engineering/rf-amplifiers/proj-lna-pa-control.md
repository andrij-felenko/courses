# ⚙️ Керування ВЧ-переднім кінцем: перемикання T/R, байпас LNA та контроль потужності PA

Цей практичний проєкт розглядає розробку та реалізацію низькорівневого програмного драйвера для мікроконтролера, який здійснює керування радіочастотним переднім кінцем (RF Front-End Module, FEM). Розглянуто апаратно-програмну архітектуру керування, алгоритми часового узгодження перемикання приймання/передачі (T/R), автоматичний байпас малошумного підсилювача (LNA) при появі завад високої потужності, а також систему моніторингу телеметрії та аварійного захисту підсилювача потужності (PA) від перегріву та високого коефіцієнта стоячої хвилі (VSWR).

---

### 1. Фізика перехідних процесів та часовий регламент T/R

При керуванні високочастотними підсилювачами та перемикачами критично дотримуватися строгої часової послідовності подачі керуючих сигналів. Порушення послідовності перемикання всього на 1–2 мікросекунди може призвести до незворотного виходу з ладу малошумного підсилювача чи пробою перемикальних діодів.

```
                      Хронограма переходу RX -> TX
                      
  RX_EN   ----\________________________________________ (Вимкнення LNA)
              |<- t1 ->|
  T/R_SW  -------------\_______________________________ (Перемикання на TX)
                       |<- t2 ->|
  PA_BIAS ______________________/---------------------- (Подача зсуву PA)
                                |<- t3 ->|
  RF_OUT  _______________________________/============= (Подача ВЧ-сигналу)
```

#### Небезпека «гарячого перемикання» (Hot Switching)

Перемикання радіочастотних ключів (на PIN-діодах або SOI-транзисторах) при наявності потужного ВЧ-сигналу називається «гарячим перемиканням». Якщо T/R-перемикач почне переходити зі стану RX у стан TX у той момент, коли передавач вже генерує потужність (наприклад, +30 dBm), на контактах або p-n переходах ключа виникнуть високовольтні дугові розряди чи пробій діелектрика. Крім того, на часовому проміжку, коли ключ перебуває у проміжному стані, ізоляція між портами падає з 40 dB до 6–10 dB, і вихідна потужність PA спрямовується прямо на чутливий вхід LNA, випалюючи тонкий затвор pHEMT-транзистора.

Для усунення цієї загрози драйвер реалізує строгий часовий регламент:

1. **Послідовність переходу RX → TX**:
   - **Крок 1**: Знімаємо сигнал `RX_EN` (вимикаємо LNA) і витримуємо паузу `t1 = 2 мкс` для повного розряду розв'язувальних ємностей та згасання струму каналу.
   - **Крок 2**: Перемикаємо T/R-ключ у стан `TX` і витримуємо паузу `t2 = 5 мкс`, необхідну для перезаряду ємностей PIN-діодів чи затворів SOI-перемикача.
   - **Крок 3**: Подаємо напругу зсуву `PA_BIAS` на затвор/базу підсилювача потужності та витримуємо паузу `t3 = 5 мкс` для стабілізації струму спокою PA.
   - **Крок 4**: Дозволяємо цифровому модему або синтезатору частоти випромінювати ВЧ-сигнал.

2. **Послідовність переходу TX → RX**:
   - **Крок 1**: Припиняємо генерацію ВЧ-сигналу на рівні модулятора/синтезатора.
   - **Крок 2**: Знімаємо напругу зсуву `PA_BIAS` (вимикаємо PA) і витримуємо паузу `5 мкс` для виведення транзистора в режим відсічки.
   - **Крок 3**: Перемикаємо T/R-ключ у стан `RX` та чекаємо `2 мкс`.
   - **Крок 4**: Подаємо сигнал `RX_EN` для увімкнення малошумного підсилювача LNA.

Для забезпечення точності паузи порядку кількох мікросекунд у системному програмному забезпеченні не використовують затримки на базі RTOS фреймворків (оскільки квант системного таймера `SysTick` зазвичай становить 1 мс). Замість цього застосовують апаратні таймери мікроконтролера або лічильник циклів ядра ARM Cortex-M (`DWT->CYCCNT` — Data Watchpoint and Trace Cycle Count Register). При конфігуруванні GPIO виводів мікроконтролера суворо рекомендовано встановлювати зовнішні підтягуючі резистори (Pull-Down на `TX_EN` та `PA_BIAS`), щоб під час скидання мікроконтролера або оновлення прошивки каскади передавача залишалися гарантовано вимкненими.

Вбудований цифровий інтерфейс керування може бути реалізований як через паралельні виводи GPIO, так і через послідовні шини керування ВЧ-компонентами SPI або MIPI RFFE (*Radio Frequency Front End*). Стандарт MIPI RFFE виділяє окремий 2-провідний серійний протокол із частотою до 52 МГц для програмування регістрів зсуву, ступенів атенюатора та режимів підсилювачів у мобільних телефонах та модемах 5G.

---

### 2. Алгоритми байпасу LNA та телеметрія

При роботі радіостанції на близьких відстанях або при наявності потужної завади від сусідньої базової станції вхідна потужність сигналу від антени може досягати 0...+5 dBm. Подача такого сигналу на вход LNA викликає глибоку компресію підсилення (`P1dB`) та інтермодуляційне блокування приймача.

Для захисту приймача драйвер підтримує режим **LNA Bypass**. За допомогою вбудованого обхідного ключа LNA вимикається з тракту, а ВЧ-сигнал прямує на змішувач через пасивний атенюатор з нульовим підсиленням (~0...−2 dB). Перемикання в режим Bypass виконується автоматично за сигналом від індикатора рівня прийнятого сигналу (RSSI, *Received Signal Strength Indicator*) трансивера, коли вхідна потужність перевищує поріг −20 dBm. Для запобігання частим коливанням режиму на межі спрацьовування алгоритм застосовує гістерезис шириною 5 dB.

#### Аварійний моніторинг PA (Температура та VSWR)

Під час передачі драйвер у циклі реального часу (з періодом 1–10 мс) вимірює аналогові параметри телеметрії через АЦП мікроконтролера:
- **Температура PA**: Датчик температури (NTC-термістор або термодіод), розміщений на фланці PA. Перетворення напруги АЦП на температуру у Кельвінах/Цельсіях виконується за рівнянням Стейнхарта-Харта: `1/T = A + B·ln(R) + C·(ln(R))^3`. При перевищенні критичного порогу (+85 °C) драйвер миттєво знімає зсув `PA_BIAS`, запобігаючи тепловому розгону кристала.
- **Спрямований відгалужувач падаючої та відбитої хвиль**: Двоканальний ВЧ-детектор (наприклад, логарифмічний детектор AD8318) вимірює напругу падаючої хвилі `V_fwd` та відбитої хвилі `V_rev`. Напруга логарифмічного детектора прямо пропорційна потужності у dBm: `P_dbm = (V_adc - V_0) / Slope`. Калібрувальні коефіцієнти `V_0` та `Slope` обчислюються під час фабричного калібрування плати за двома еталонними точками потужності (+10 dBm та +30 dBm).
- **Розрахунок коефіцієнта відбиття та VSWR**:
  З виміряних потужностей `P_fwd_dbm` та `P_rev_dbm` драйвер обчислює зворотні втрати `Return_Loss_dB = P_fwd_dbm - P_rev_dbm`.
  Модуль коефіцієнта відбиття за напругою: `Gamma = 10^(-Return_Loss_dB / 20)`.
  Коефіцієнт стоячої хвилі: `VSWR = (1 + Gamma) / (1 - Gamma)`.

При виявленні зростання VSWR понад 3.0 (що свідчить про обрив кабелю чи відсутність антени) драйвер спочатку намагається зменшити вихідну потужність PA (*Power Foldback*), а у випадку катастрофічного неузгодження (VSWR > 5.0) виконує негайне аварійне вимкнення зсуву.

Вбудована система автоматичного регулювання потужності (ALC — Automatic Level Control) підтримує стабільний рівень вихідної ВЧ-потужності незалежно від зміни температури корпусу та коливань напруги живлення акумулятора. Для зменшення навантаження на процесор зчитування каналів АЦП виконується у фоновому режимі за допомогою прямого доступу до пам'яті (DMA) з прив'язкою до апаратного таймера.

---

### 3. Двомовний приклад реалізації драйвера (C та C++)

Нижче наведено повний вихідний код драйвера ВЧ-переднього кінця, написаний двома мовами: ідіоматичною C (з використанням структур та явних обробників) та сучасній C++20 (з використанням RAII, строгих типів `enum class`, шаблону `std::expected` для безвиняткової обробки помилок та з нульовим динамічним виділенням пам'яті).

:::tabs
```c
/* rf_frontend.h — Драйвер ВЧ-переднього кінця мовою C */
#ifndef RF_FRONTEND_H
#define RF_FRONTEND_H

#include <stdint.h>
#include <stdbool.h>

typedef enum {
    RF_MODE_SHUTDOWN = 0,
    RF_MODE_RX_HIGH_GAIN,
    RF_MODE_RX_BYPASS,
    RF_MODE_TX
} rf_mode_t;

typedef enum {
    RF_OK = 0,
    RF_ERR_INVALID_MODE,
    RF_ERR_OVERTEMP,
    RF_ERR_HIGH_VSWR,
    RF_ERR_NULL_PTR
} rf_status_t;

typedef struct {
    float temp_celsius;
    float forward_power_dbm;
    float reverse_power_dbm;
    float vswr;
} rf_telemetry_t;

/* Конфігураційні межі захисту */
#define RF_MAX_TEMP_C      85.0f
#define RF_MAX_VSWR        3.0f

void rf_frontend_init(void);
rf_status_t rf_frontend_set_mode(rf_mode_t new_mode);
rf_mode_t rf_frontend_get_mode(void);
rf_status_t rf_frontend_read_telemetry(rf_telemetry_t *telemetry);

#endif /* RF_FRONTEND_H */
```
```c
/* rf_frontend.c — Імплементація драйвера мовою C */
#include "rf_frontend.h"

/* Зовнішні залежності від Hardware Abstraction Layer (HAL) МК */
extern void hw_gpio_write_tx_en(bool level);
extern void hw_gpio_write_rx_en(bool level);
extern void hw_gpio_write_lna_bypass(bool level);
extern void hw_gpio_write_pa_bias(bool level);
extern void hw_delay_us(uint32_t us);
extern float hw_adc_read_pa_temp(void);
extern float hw_adc_read_fwd_pwr_dbm(void);
extern float hw_adc_read_rev_pwr_dbm(void);

static rf_mode_t g_current_mode = RF_MODE_SHUTDOWN;

void rf_frontend_init(void) {
    hw_gpio_write_pa_bias(false);
    hw_gpio_write_tx_en(false);
    hw_gpio_write_rx_en(false);
    hw_gpio_write_lna_bypass(true);
    g_current_mode = RF_MODE_SHUTDOWN;
}

rf_status_t rf_frontend_set_mode(rf_mode_t new_mode) {
    if (new_mode == g_current_mode) {
        return RF_OK;
    }

    /* 1. Перевірка температурного захисту перед увімкненням TX */
    if (new_mode == RF_MODE_TX) {
        float t = hw_adc_read_pa_temp();
        if (t > RF_MAX_TEMP_C) {
            rf_frontend_init(); /* Аварійний скид */
            return RF_ERR_OVERTEMP;
        }
    }

    /* 2. Безпечна послідовність перемикання режимів */
    if (g_current_mode == RF_MODE_TX) {
        /* Послідовність вимкнення TX -> RX / Shutdown */
        hw_gpio_write_pa_bias(false);  /* Спочатку знімаємо зсув PA */
        hw_delay_us(5);                /* Пауза для розряду ємності затвора */
        hw_gpio_write_tx_en(false);   /* Вимикаємо TX ключ */
        hw_delay_us(2);
    } else if (g_current_mode == RF_MODE_RX_HIGH_GAIN || g_current_mode == RF_MODE_RX_BYPASS) {
        /* Вимикаємо RX каскади */
        hw_gpio_write_rx_en(false);
        hw_delay_us(2);
    }

    /* 3. Встановлення нового стану мікросхеми */
    switch (new_mode) {
        case RF_MODE_SHUTDOWN:
            hw_gpio_write_lna_bypass(true);
            break;

        case RF_MODE_RX_HIGH_GAIN:
            hw_gpio_write_lna_bypass(false);
            hw_gpio_write_rx_en(true);
            break;

        case RF_MODE_RX_BYPASS:
            hw_gpio_write_lna_bypass(true);
            hw_gpio_write_rx_en(true);
            break;

        case RF_MODE_TX:
            hw_gpio_write_tx_en(true);
            hw_delay_us(5);               /* Даємо ключю час для стабілізації */
            hw_gpio_write_pa_bias(true);  /* Лише тепер вмикаємо PA */
            break;

        default:
            return RF_ERR_INVALID_MODE;
    }

    g_current_mode = new_mode;
    return RF_OK;
}

rf_mode_t rf_frontend_get_mode(void) {
    return g_current_mode;
}

rf_status_t rf_frontend_read_telemetry(rf_telemetry_t *telemetry) {
    if (!telemetry) return RF_ERR_NULL_PTR;

    telemetry->temp_celsius = hw_adc_read_pa_temp();
    telemetry->forward_power_dbm = hw_adc_read_fwd_pwr_dbm();
    telemetry->reverse_power_dbm = hw_adc_read_rev_pwr_dbm();

    /* Спрощений розрахунок VSWR з виміряної потужності */
    float p_fwd_mw = 0.001f * (telemetry->forward_power_dbm);
    float p_rev_mw = 0.001f * (telemetry->reverse_power_dbm);

    if (p_fwd_mw > 0.001f && p_rev_mw >= 0.0f) {
        float gamma = 0.0f;
        if (p_rev_mw < p_fwd_mw) {
            gamma = p_rev_mw / p_fwd_mw; /* Коефіцієнт відбиття за потужністю */
        } else {
            gamma = 0.99f;
        }
        float gamma_mag = (gamma > 0.0f) ? gamma : 0.0f;
        telemetry->vswr = (1.0f + gamma_mag) / (1.0f - gamma_mag + 0.0001f);
    } else {
        telemetry->vswr = 1.0f;
    }

    /* Перевірка аварії за VSWR під час передачі */
    if (g_current_mode == RF_MODE_TX && telemetry->vswr > RF_MAX_VSWR) {
        rf_frontend_init(); /* Аварійно вимикаємо передавач */
        return RF_ERR_HIGH_VSWR;
    }

    return RF_OK;
}
```
```cpp
// rf_frontend.hpp — Драйвер ВЧ-переднього кінця мовою C++20
#pragma once

#include <cstdint>
#include <expected>
#include <optional>

namespace rf {

enum class Mode : uint8_t {
    Shutdown,
    RxHighGain,
    RxBypass,
    Tx
};

enum class Error : uint8_t {
    InvalidMode,
    Overtemperature,
    HighVswr,
    HardwareFault
};

struct Telemetry {
    float temp_celsius{0.0f};
    float forward_power_dbm{0.0f};
    float reverse_power_dbm{0.0f};
    float vswr{1.0f};
};

class FrontEndModule {
public:
    static constexpr float MaxTempCelsius = 85.0f;
    static constexpr float MaxVswr = 3.0f;

    FrontEndModule() noexcept = default;
    ~FrontEndModule() { (void)shutdown(); }

    // Заборона копіювання (RAII керування апаратним ресурсом)
    FrontEndModule(const FrontEndModule&) = delete;
    FrontEndModule& operator=(const FrontEndModule&) = delete;
    FrontEndModule(FrontEndModule&&) noexcept = default;
    FrontEndModule& operator=(FrontEndModule&&) noexcept = default;

    [[nodiscard]] std::expected<void, Error> set_mode(Mode new_mode) noexcept;
    [[nodiscard]] Mode current_mode() const noexcept { return mode_; }
    [[nodiscard]] std::expected<Telemetry, Error> update_telemetry() noexcept;
    [[nodiscard]] std::expected<void, Error> shutdown() noexcept;

private:
    Mode mode_{Mode::Shutdown};

    void apply_gpio_pins(bool tx_en, bool rx_en, bool bypass, bool pa_bias) noexcept;
    float read_adc_pa_temp() const noexcept;
    float read_adc_fwd_pwr() const noexcept;
    float read_adc_rev_pwr() const noexcept;
    void delay_us(uint32_t us) const noexcept;
};

inline std::expected<void, Error> FrontEndModule::shutdown() noexcept {
    apply_gpio_pins(false, false, true, false);
    mode_ = Mode::Shutdown;
    return {};
}

inline std::expected<void, Error> FrontEndModule::set_mode(Mode new_mode) noexcept {
    if (new_mode == mode_) {
        return {};
    }

    if (new_mode == Mode::Tx) {
        if (read_adc_pa_temp() > MaxTempCelsius) {
            (void)shutdown();
            return std::unexpected(Error::Overtemperature);
        }
    }

    // Безпечна деактивація попереднього режиму
    if (mode_ == Mode::Tx) {
        apply_gpio_pins(true, false, true, false); // Знімаємо bias
        delay_us(5);
        apply_gpio_pins(false, false, true, false); // Вимикаємо TX ключ
        delay_us(2);
    } else if (mode_ == Mode::RxHighGain || mode_ == Mode::RxBypass) {
        apply_gpio_pins(false, false, true, false); // Вимикаємо RX
        delay_us(2);
    }

    // Активація нового режиму
    switch (new_mode) {
        case Mode::Shutdown:
            return shutdown();

        case Mode::RxHighGain:
            apply_gpio_pins(false, true, false, false);
            break;

        case Mode::RxBypass:
            apply_gpio_pins(false, true, true, false);
            break;

        case Mode::Tx:
            apply_gpio_pins(true, false, true, false);
            delay_us(5);
            apply_gpio_pins(true, false, true, true); // Подаємо bias на PA
            break;
    }

    mode_ = new_mode;
    return {};
}

inline std::expected<Telemetry, Error> FrontEndModule::update_telemetry() noexcept {
    Telemetry t{};
    t.temp_celsius = read_adc_pa_temp();
    t.forward_power_dbm = read_adc_fwd_pwr();
    t.reverse_power_dbm = read_adc_rev_pwr();

    float p_fwd_mw = 0.001f * t.forward_power_dbm;
    float p_rev_mw = 0.001f * t.reverse_power_dbm;

    if (p_fwd_mw > 0.001f) {
        float gamma = (p_rev_mw < p_fwd_mw) ? (p_rev_mw / p_fwd_mw) : 0.99f;
        t.vswr = (1.0f + gamma) / (1.0f - gamma + 0.0001f);
    }

    if (mode_ == Mode::Tx && t.vswr > MaxVswr) {
        (void)shutdown();
        return std::unexpected(Error::HighVswr);
    }

    return t;
}

inline void FrontEndModule::apply_gpio_pins(bool tx_en, bool rx_en, bool bypass, bool pa_bias) noexcept {
    // Взаємодія з HAL МК
    (void)tx_en; (void)rx_en; (void)bypass; (void)pa_bias;
}
inline float FrontEndModule::read_adc_pa_temp() const noexcept { return 45.0f; }
inline float FrontEndModule::read_adc_fwd_pwr() const noexcept { return 30.0f; }
inline float FrontEndModule::read_adc_rev_pwr() const noexcept { return 0.5f; }
inline void FrontEndModule::delay_us(uint32_t us) const noexcept { (void)us; }

} // namespace rf
```
:::

---

### 4. Зіставлення архітектур C та C++

Порівнюючи дві реалізації драйвера, слід зазначити такі мовні та архітектурні особливості:

1. **Гарантія безпеки ресурсів (RAII)**: У C-версії якщо програміст забудь викликати `rf_frontend_init()`, або якщо функція поверне код помилки до відновлення станів GPIO, каскади підсилювача можуть залишитися під напругою зсуву при вимкненому перемикачі. У C++-версії деструктор `~FrontEndModule()` гарантує автоматичне вимкнення PA та переведення модуля в `Shutdown` при виході з області видимості об'єкта.
2. **Типобезпека станів**: C++ `enum class Mode` унеможливлює випадкове передавання цілочисельного сміття замість сталого режиму або плутанину між кодами помилок і режимами на етапі компіляції.
3. **Безвиняткова обробка помилок**: Шаблон `std::expected<void, Error>` у C++20 дозволяє явно вимагати від викликаючого коду перевірки результату виконання без використання винятків (`exceptions`), що є критичним для систем реального часу з жорсткими часовими рамками.
4. **Нульові витрати на виконання (Zero-Overhead Abstraction)**: Інкапсуляція класів та `inline` методи у C++20 після оптимізації компілятором `g++ -O2` генерують інструкції асемблера, ідентичні до жорстко написаного C-коду, забезпечуючи максимальну детермінованість часу виконання.
5. **Багатопотокова безпека у RTOS**: У середовищах FreeRTOS чи Zephyr OS доступ до об'єкта `FrontEndModule` між задачею обробки пакетів та задачею розрахунку телеметрії захищають за допомогою м'ютекса або атомарних прапорців стану (`std::atomic<Mode>`), запобігаючи стану гонки при одночасному перемиканні режимів.
6. **Тестування та заглушки (Mocking)**: Шаблонна структура C++-класу дозволяє легко підміняти апаратний HAL тестовими емуляторами у юніт-тестах без модифікації бінарного коду прошивки.
