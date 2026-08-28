# ⚙️ Розрахунок бюджету дерева живлення та керування секвенсером

Проєктування підсистеми живлення власної плати вимагає двох взаємопов'язаних інженерних кроків: математичного розрахунку балансу струмів, втрат потужності й перегріву напівпровідників та написання надійного вбудованого коду для покрокового вмикання рейок і контролю сигналів готовності живлення (`PGOOD`). Помилка в тепловому розрахунку призводить до термічного вимкнення стабілізаторів під час пікових навантажень, а відсутність контролю послідовності — до апаратного блокування мікроконтролера через паразитне живлення периферії.

Нижче наведено повний інженерний розрахунок для типового промислового вузла з автономним радіоканалом і керуванням навантаженням (живлення від шини 12 В чи акумулятора), а також робочий програмний модуль секвенсера живлення на C та C++.

---

## 1. Специфікація вузлів та бюджет струмів

Розглянемо типовий вбудований пристрій телеметрії та автоматики. Пристрій живиться від зовнішньої промислової шини постійного струму з номінальною напругою 12 В (робочий діапазон 9…28 В).

Система містить такі функціональні споживачі:
1. **Цифрове ядро MCU (STM32 / ESP32-P4)**: напруга ядра `VCORE = 1.2 В`, струм у режимі обчислень `I_core = 120 мА`.
2. **Головна цифрова периферія та флеш-пам'ять (`DVDD`)**: напруга `3.3 В`, середній струм `I_io = 60 мА`, піковий струм `I_io_peak = 150 мА`.
3. **Радіомодуль Wi-Fi / LoRa**: напруга `3.3 В`, струм у режимі сну `I_rf_sleep = 15 мкА`, струм прийому `I_rf_rx = 20 мА`, піковий імпульсний струм передачі `I_rf_tx_peak = 350 мА` (тривалість пакету 10 мс).
4. **Прецизійний аналоговий тракт (`AVDD`)**: 24-бітний АЦП з інтегрованим підсилювачем PGA, напруга `3.3 В`, струм `I_analog = 15 мА` (вимагає шуму пульсацій менше 10 мкВ RMS).
5. **Зовнішні датчики I2C/SPI та дисплей**: напруга `3.3 В`, сумарний струм `I_periph = 80 мА` (комутуються через керований силовий ключ Load Switch).

---

## 2. Розрахунок першого та другого ступенів перетворення

Якщо живити всю схему 3.3 В безпосередньо від 12 В за допомогою лінійного регулятора (LDO), сумарний максимальний струм становитиме:

```
I_total_peak = I_io_peak + I_rf_tx_peak + I_analog + I_periph + I_core_input
I_total_peak = 150 + 350 + 15 + 80 + 120 = 715 мА = 0.715 А
```

Падіння напруги на лінійному стабілізаторі:

```
V_drop = V_in - V_out = 12.0 - 3.3 = 8.7 В
```

Потужність теплових втрат на кристалі LDO:

```
P_loss = V_drop · I_total_peak = 8.7 В · 0.715 А = 6.22 Вт
```

Для тепловідведення 6.22 Вт знадобився б масивний алюмінієвий радіатор вагою понад 100 грамів. У закритому корпусі плата розігрілася б вище 150 °C за лічені секунди.

Тому архітектура будується у два ступені:
- **I ступінь**: синхронний імпульсний понижувальний перетворювач (Step-Down Buck), що знижує напругу з 12 В до проміжної шини `3.3 В` з ККД `η = 91%`.
- **II ступінь**:
  - Лінійний LDO з високим PSRR для аналогової шини `AVDD` (`3.3 В -> 3.3 В` через фільтр або від виділеного виходу з падінням 200 мВ).
  - Малопотужний LDO/Buck для ядра `VCORE` (`3.3 В -> 1.2 В`).

Розрахунок теплових втрат синхронного Step-Down Buck при середньому навантаженні (`I_out_avg = 350 мА`):

```
P_out = V_out · I_out_avg = 3.3 В · 0.35 А = 1.155 Вт
P_in = P_out / η = 1.155 / 0.91 = 1.269 Вт
P_buck_loss = P_in - P_out = 1.269 - 1.155 = 0.114 Вт = 114 мВт
```

Втрати 114 мВт розсіюються стандартним корпусом QFN-16 або SOT-23-6 на мідні полігони друкованої плати без відчутного нагріву (перегрів `ΔT ≈ 114 мВт · 45 °C/Вт ≈ 5.1 °C`).

---

## 3. Розрахунок буферних конденсаторів для пікових струмів

Під час передачі пакету Wi-Fi або LoRa струм шини 3.3 В стрибкоподібно зростає на `ΔI = 350 мА` за час наростання фронту передавача `Δt_edge ≈ 5 мкс`. Контур зворотного зв'язку імпульсного Buck-перетворювача має смугу пропускання `f_BW ≈ 50 кГц`, що відповідає часу реакції петлі регулювання:

```
t_response ≈ 1 / (2 · π · f_BW) ≈ 1 / (6.28 · 50000) ≈ 3.18 мкс
```

Поки перетворювач відкриває верхній силовий ключ і накачує енергію в індуктивність, весь струм навантаження мусить віддати вихідний конденсаторний банк `C_out`. Якщо допустиме просідання напруги логіки `ΔV_max = 100 мВ` (3.0% від 3.3 В), необхідна ємність становить:

```
C_out ≥ (ΔI · t_response) / ΔV_max
C_out ≥ (0.350 А · 3.18 · 10⁻⁶ с) / 0.100 В = 11.13 · 10⁻⁶ Ф = 11.13 мкФ
```

З урахуванням ефекту DC-Bias (падіння реальної ємності керамічних конденсаторів X5R/X7R під дією постійної напруги на 40–60%) обираємо:
- Два керамічних конденсатори 22 мкФ 10 В (типорозмір 0805, X7R) паралельно (еквівалентна ємність під напругою 3.3 В становить приблизно `2 × 12 мкФ = 24 мкФ`).
- Один танталовий або полімерний конденсатор 47 мкФ з низьким ESR (`ESR < 50 мОм`) для демпфування добротності вхідних кіл.
- Локальні блокувальні конденсатори 0.1 мкФ (0402) безпосередньо біля кожного виводу живлення мікроконтролера та радіомодуля.

---

## 4. Програмний модуль керування секвенсером живлення

Для запобігання паразитній зачитці (phantom powering) та тиристорному замиканню процесор повинен керувати послідовністю вмикання периферійних вузлів:
1. Контроль вхідної напруги та сигналу `PGOOD` первинного Buck-перетворювача ядра.
2. Подача живлення на головну шину вводу-виводу (`DVDD`).
3. Пауза стабілізації перехідних процесів і зняття апаратного сигналу скидання (`NRST`).
4. Подача напруги на зовнішню периферію та сенсори через силовий ключ (Load Switch) лише після повної ініціалізації внутрішніх портів GPIO у вихідний безпечний стан (високоомний вхід або пуш-пул низького рівня).
5. Постійний моніторинг сигналу аварії (Power Fault) та миттєве вимкнення периферії при виявленні просідання вхідної напруги.

Нижче наведено реалізацію кінцевого автомата секвенсера живлення на C та C++.

:::tabs
```c
/* power_sequencer.h - C99 embedded HAL implementation */
#ifndef POWER_SEQUENCER_H
#define POWER_SEQUENCER_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    PWR_STATE_OFF = 0,
    PWR_STATE_WAIT_CORE_PG,
    PWR_STATE_ENABLE_IO,
    PWR_STATE_WAIT_IO_PG,
    PWR_STATE_ENABLE_PERIPH,
    PWR_STATE_READY,
    PWR_STATE_FAULT
} pwr_state_t;

typedef enum {
    PWR_ERR_NONE = 0,
    PWR_ERR_CORE_TIMEOUT,
    PWR_ERR_IO_TIMEOUT,
    PWR_ERR_BROWNOUT,
    PWR_ERR_OVERCURRENT
} pwr_error_t;

typedef struct {
    uint32_t core_pg_timeout_ms;
    uint32_t io_pg_timeout_ms;
    uint32_t periph_stabilize_ms;
} pwr_config_t;

typedef struct {
    pwr_state_t state;
    pwr_error_t last_error;
    uint32_t state_timer_ms;
    pwr_config_t config;
    bool core_pg_pin_state;
    bool io_pg_pin_state;
    bool fault_pin_state;
} power_sequencer_t;

void pwr_seq_init(power_sequencer_t *seq, const pwr_config_t *cfg);
void pwr_seq_start_powerup(power_sequencer_t *seq);
void pwr_seq_start_shutdown(power_sequencer_t *seq);
void pwr_seq_process_tick(power_sequencer_t *seq, uint32_t elapsed_ms);

/* Низькорівневі апаратні виклики керування ключами */
void hw_set_core_regulator_en(bool enable);
void hw_set_io_regulator_en(bool enable);
void hw_set_periph_load_switch_en(bool enable);
bool hw_read_core_pgood(void);
bool hw_read_io_pgood(void);
bool hw_read_fault_irq(void);

#endif /* POWER_SEQUENCER_H */
```
```cpp
// power_sequencer.hpp - C++20 modern embedded implementation
#pragma once

#include <cstdint>
#include <concepts>
#include <expected>
#include <chrono>

namespace power {

enum class State : uint8_t {
    Off = 0,
    WaitCorePgood,
    EnableIo,
    WaitIoPgood,
    EnablePeriph,
    Ready,
    Fault
};

enum class Error : uint8_t {
    None = 0,
    CoreTimeout,
    IoTimeout,
    BrownoutDetected,
    OvercurrentFault
};

struct Config {
    std::chrono::milliseconds core_pg_timeout{50};
    std::chrono::milliseconds io_pg_timeout{50};
    std::chrono::milliseconds periph_stabilize_delay{10};
};

template <typename HardwareInterface>
concept PowerHardware = requires(HardwareInterface hw, bool en) {
    { hw.set_core_en(en) } -> std::same_as<void>;
    { hw.set_io_en(en) } -> std::same_as<void>;
    { hw.set_periph_en(en) } -> std::same_as<void>;
    { hw.read_core_pgood() } -> std::same_as<bool>;
    { hw.read_io_pgood() } -> std::same_as<bool>;
    { hw.read_fault_status() } -> std::same_as<bool>;
};

template <PowerHardware Hw>
class PowerSequencer {
public:
    explicit PowerSequencer(Hw& hardware, Config config = {})
        : hw_{hardware}, cfg_{config}, state_{State::Off}, error_{Error::None}, timer_ms_{0} {}

    void start_power_up() noexcept {
        if (state_ == State::Off || state_ == State::Fault) {
            error_ = Error::None;
            timer_ms_ = 0;
            hw_.set_periph_en(false);
            hw_.set_io_en(false);
            hw_.set_core_en(true);
            state_ = State::WaitCorePgood;
        }
    }

    void shutdown() noexcept {
        hw_.set_periph_en(false);
        hw_.set_io_en(false);
        hw_.set_core_en(false);
        state_ = State::Off;
    }

    void process_tick(std::chrono::milliseconds elapsed) noexcept {
        timer_ms_ += elapsed.count();

        if (hw_.read_fault_status() && state_ != State::Fault && state_ != State::Off) {
            trigger_fault(Error::OvercurrentFault);
            return;
        }

        switch (state_) {
            case State::WaitCorePgood:
                if (hw_.read_core_pgood()) {
                    hw_.set_io_en(true);
                    timer_ms_ = 0;
                    state_ = State::WaitIoPgood;
                } else if (timer_ms_ >= cfg_.core_pg_timeout.count()) {
                    trigger_fault(Error::CoreTimeout);
                }
                break;

            case State::WaitIoPgood:
                if (hw_.read_io_pgood()) {
                    timer_ms_ = 0;
                    state_ = State::EnablePeriph;
                } else if (timer_ms_ >= cfg_.io_pg_timeout.count()) {
                    trigger_fault(Error::IoTimeout);
                }
                break;

            case State::EnablePeriph:
                if (timer_ms_ >= cfg_.periph_stabilize_delay.count()) {
                    hw_.set_periph_en(true);
                    state_ = State::Ready;
                }
                break;

            case State::Ready:
                if (!hw_.read_core_pgood() || !hw_.read_io_pgood()) {
                    trigger_fault(Error::BrownoutDetected);
                }
                break;

            case State::Off:
            case State::Fault:
            default:
                break;
        }
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] Error error() const noexcept { return error_; }
    [[nodiscard]] bool is_ready() const noexcept { return state_ == State::Ready; }

private:
    void trigger_fault(Error err) noexcept {
        error_ = err;
        state_ = State::Fault;
        shutdown();
    }

    Hw& hw_;
    Config cfg_;
    State state_;
    Error error_;
    uint32_t timer_ms_;
};

} // namespace power
```
:::

---

## 5. Типові підводні камені при реалізації

1. **Ігнорування витоку струму під час вимкнення периферії**: якщо силовий ключ вимикає шину `VCC` зовнішнього датчика, але лінії інтерфейсу I2C (SDA, SCL) мають зовнішні підтягувальні резистори до головної невимкненої шини 3.3 В, датчик живитиметься струмом витоку через підтяжки та вхідні ESD-діоди. Керуючи живленням навантаження, необхідно або перемикати піни GPIO мікроконтролера в режим аналогового входу (`GPIO_MODE_ANALOG` / High-Z), або використовувати перемикачі зі зворотним ізолятором шин.
2. **Ємнісний удар під час увімкнення ключа**: при вмиканні периферійної шини з великою сумарною ємністю (`C_load > 100 мкФ`) миттєве відкриття ключа без обмеження швидкості наростання фронту (`dV/dt`) викликає різке просідання напруги на виході головного Buck-перетворювача. Для запобігання перезавантаженню мікроконтролера слід використовувати ключі з керованим часом наростання (наприклад, TPS22918 із часом наростання `t_r ≈ 1…5 мс`).
3. **Теплове розсіювання при повільному наростанні**: під час лінійного наростання напруги на конденсаторі регулювальний транзистор розсіює енергію `E = 0.5 · C_load · V_out²`. Для ємностей до 1000 мкФ ця енергія безпечна для корпусів SOT-23 / DFN, проте повторні часті цикли комутації можуть спричинити термоциклювання кристала.
