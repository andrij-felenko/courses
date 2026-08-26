# ⚙️ Прошивка контролера вітроустановки: скінченний автомат, MPPT та ступінчасте гальмування

Керування силовою електронікою малої вітроустановки вимагає суворого узгодження кількох нелінійних контурів регулювання. На відміну від сонячних контролерів, мікроконтролер вітрогенератора безперервно відстежує механічну швидкість ротора, запобігає динамічному зриву вітроколеса через інерцію, дозує струм баластного навантаження та виконує послідовне безпечне гальмування генератора при штормових поривах.

### Архітектура станів автомата керування (FSM)

Скінченний автомат прошивки (FSM, Finite State Machine) оперує шістьма станами безпеки та перетворення енергії:

1. **`STATE_PARKED_BRAKED` (Запарковано / Фази закорочені):** Аварійне трифазне реле увімкнене (фази генератора замкнені накоротко), ключі MPPT та баласту вимкнені. Ротор утримується в нерухомому або повільно повзучому стані.
2. **`STATE_STARTUP_RELEASE` (Розгальмування та вільний розгін):** Реле короткого замикання розімкнене, силове навантаження повністю відімкнене (`Duty = 0`). Контролер очікує, поки лопаті розженуться слабким вітром до швидкості початку генерації `RPM_CUT_IN`.
3. **`STATE_MPPT_TRACKING` (Оптимальний відбір енергії):** Швидкість ротора перевищила поріг старту, напруга акумулятора перебуває в безпечних межах. DC-DC перетворювач регулює коефіцієнт заповнення ШІМ відповідно до кубічного закону оптимальної потужності `P_opt = k_opt · ω³` з урахуванням механічної постійної часу ротора.
4. **`STATE_POWER_LIMIT_DUMP` (Стабілізація напруги та баластний скид):** Акумулятор набрав напругу стабілізації `VBAT_FLOAT_TARGET` або потужність генератора перевищила номінальну. Контролер вмикає ШІМ баластного резистора, утилізуючи надлишок енергії у тепло та утримуючи оберти ротора від розгону.
5. **`STATE_HIGH_WIND_BRAKING` (Двоетапне штормове гальмування):** Швидкість вітру або оберти ротора перевищили аварійний поріг `RPM_OVERSPEED_LIMIT`. Контролер не може миттєво закоротити фази, щоб не спалити статор індуктивними струмами. Спочатку баласт відкривається на 100% ШІМ для скидання кінетичної енергії обертання до безпечного порогу `RPM_SAFE_BRAKE`, після чого спрацьовує реле повного короткого замикання.
6. **`STATE_FAULT_LATCH` (Аварійне блокування):** Спрацював термодатчик радіатора баласту, зафіксовано обрив батареї або апаратну аварію перенапруги. Перетворювач ізолює коло та вмикає гальма до ручного скидання.

### Апаратні вимоги та вимірювальні ланцюги

Для надійної роботи скінченного автомата апаратна частина повинна забезпечувати роботу чотирьох обов'язкових вимірювальних каналів:
- **Вимірювання частоти фази генератора `f_gen`:** сигнал однієї з фаз статора через дільник напруги та швидкісний компаратор із гістерезисом (тригер Шмітта) подається на вхід апаратного таймера мікроконтролера в режимі захоплення імпульсів (Input Capture). Це дає абсолютну швидкість обертання `ω` без необхідності встановлення ненадійних оптичних або магнітних енкодерів на щоглі.
- **Диференційне вимірювання струму:** шунти в колах випрямляча та батареї з операційними підсилювачами зі зсувом нуля для вимірювання як прямого струму заряду, так і струму баласту.
- **Аналогова фільтрація напруги:** вхідні дільники напруги `U_dc` та `U_bat` повинні містити RC-фільтри низьких частот із частотою зрізу 50–100 Гц для придушення шестипульсних пульсацій випрямляча.

### Програмна реалізація модуля керування

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Пороги напруги в мілівольтах (мВ) */
#define VBAT_NOMINAL_MV          48000U
#define VBAT_FLOAT_TARGET_MV     54400U  /* Напруга підтримувального заряду */
#define VBAT_ABSORPTION_MAX_MV   57600U  /* Верхня межа заряду */
#define VBAT_OVERVOLTAGE_ALARM_MV 60000U /* Аварійний поріг відсічки */

/* Механічні пороги обертів ротора (об/хв) */
#define RPM_CUT_IN                 120U  /* Оберти початку заряду */
#define RPM_RATED                  450U  /* Номінальні оберти */
#define RPM_OVERSPEED_LIMIT        550U  /* Поріг штормової аварії */
#define RPM_SAFE_BRAKE             200U  /* Безпечні оберти для замикання реле */

/* Часові константи (мілісекунди) */
#define MPPT_UPDATE_INTERVAL_MS    100UL /* Крок адаптації згладженого MPPT */
#define BRAKE_DUMP_TIMEOUT_MS     5000UL /* Максимальний час здуття обертів баластом */

typedef enum {
    WIND_STATE_PARKED_BRAKED = 0,
    WIND_STATE_STARTUP_RELEASE,
    WIND_STATE_MPPT_TRACKING,
    WIND_STATE_POWER_LIMIT_DUMP,
    WIND_STATE_HIGH_WIND_BRAKING,
    WIND_STATE_FAULT_LATCH
} wind_state_t;

typedef enum {
    WIND_FAULT_NONE = 0,
    WIND_FAULT_BATTERY_OVERVOLTAGE,
    WIND_FAULT_ROTOR_OVERSPEED,
    WIND_FAULT_HEATSINK_OVERTEMP
} wind_fault_t;

typedef struct {
    wind_state_t state;
    wind_fault_t fault;
    uint32_t state_entry_time_ms;
    uint32_t last_mppt_tick_ms;
    uint16_t rpm_filtered;
    uint16_t vbat_mv;
    uint16_t vgen_mv;
    uint16_t igen_ma;
    uint16_t mppt_pwm_permille;  /* ШІМ MPPT (0..1000) */
    uint16_t dump_pwm_permille;  /* ШІМ баласту (0..1000) */
    bool brake_relay_closed;
} wind_controller_t;

/* Апаратні функції драйверів (HAL) */
extern void hw_set_mppt_pwm(uint16_t permille);
extern void hw_set_dump_pwm(uint16_t permille);
extern void hw_set_brake_relay(bool close_short_circuit);
extern uint32_t hw_get_time_ms(void);

void wind_controller_init(wind_controller_t *ctrl)
{
    if (!ctrl) return;
    ctrl->state = WIND_STATE_PARKED_BRAKED;
    ctrl->fault = WIND_FAULT_NONE;
    ctrl->state_entry_time_ms = hw_get_time_ms();
    ctrl->last_mppt_tick_ms = ctrl->state_entry_time_ms;
    ctrl->rpm_filtered = 0;
    ctrl->vbat_mv = 0;
    ctrl->vgen_mv = 0;
    ctrl->igen_ma = 0;
    ctrl->mppt_pwm_permille = 0;
    ctrl->dump_pwm_permille = 0;
    ctrl->brake_relay_closed = true;

    /* За замовчуванням генератор надійно закорочений */
    hw_set_mppt_pwm(0);
    hw_set_dump_pwm(0);
    hw_set_brake_relay(true);
}

static void wind_transition_to(wind_controller_t *ctrl, wind_state_t new_state)
{
    ctrl->state = new_state;
    ctrl->state_entry_time_ms = hw_get_time_ms();

    switch (new_state) {
    case WIND_STATE_PARKED_BRAKED:
    case WIND_STATE_FAULT_LATCH:
        hw_set_mppt_pwm(0);
        hw_set_dump_pwm(1000); /* Баласт паралельно реле */
        hw_set_brake_relay(true);
        ctrl->brake_relay_closed = true;
        ctrl->mppt_pwm_permille = 0;
        ctrl->dump_pwm_permille = 1000;
        break;

    case WIND_STATE_STARTUP_RELEASE:
        hw_set_brake_relay(false);
        hw_set_mppt_pwm(0);
        hw_set_dump_pwm(0);
        ctrl->brake_relay_closed = false;
        ctrl->mppt_pwm_permille = 0;
        ctrl->dump_pwm_permille = 0;
        break;

    case WIND_STATE_MPPT_TRACKING:
        hw_set_brake_relay(false);
        hw_set_dump_pwm(0);
        ctrl->brake_relay_closed = false;
        ctrl->dump_pwm_permille = 0;
        break;

    case WIND_STATE_POWER_LIMIT_DUMP:
        hw_set_brake_relay(false);
        ctrl->brake_relay_closed = false;
        break;

    case WIND_STATE_HIGH_WIND_BRAKING:
        /* Спочатку 100% баласт для здуття швидкості, реле ще не замикаємо */
        hw_set_mppt_pwm(0);
        hw_set_dump_pwm(1000);
        hw_set_brake_relay(false);
        ctrl->brake_relay_closed = false;
        ctrl->mppt_pwm_permille = 0;
        ctrl->dump_pwm_permille = 1000;
        break;
    }
}

/* Обчислення цільової потужності за кубічною характеристикою P_opt = k * w^3 */
static uint16_t calculate_optimal_mppt_pwm(uint16_t rpm, uint16_t vgen_mv)
{
    if (rpm < RPM_CUT_IN || vgen_mv < 10000U) return 0;
    
    /* Спрощена кубічна апроксимація шпаруватості від обертів */
    uint32_t norm_rpm = (uint32_t)(rpm - RPM_CUT_IN);
    uint32_t max_span = (uint32_t)(RPM_RATED - RPM_CUT_IN);
    if (norm_rpm > max_span) norm_rpm = max_span;

    uint32_t target = (norm_rpm * norm_rpm * norm_rpm) / (max_span * max_span / 1000U);
    if (target > 1000U) target = 1000U;
    return (uint16_t)target;
}

void wind_controller_process(wind_controller_t *ctrl,
                             uint16_t raw_rpm,
                             uint16_t raw_vbat_mv,
                             uint16_t raw_vgen_mv,
                             uint16_t raw_igen_ma,
                             bool temp_ok)
{
    uint32_t now = hw_get_time_ms();

    /* Фільтрація вимірювань ковзним середнім (експоненційний IIR) */
    ctrl->rpm_filtered = (uint16_t)(((uint32_t)ctrl->rpm_filtered * 3U + raw_rpm) / 4U);
    ctrl->vbat_mv      = (uint16_t)(((uint32_t)ctrl->vbat_mv * 3U + raw_vbat_mv) / 4U);
    ctrl->vgen_mv      = (uint16_t)(((uint32_t)ctrl->vgen_mv * 3U + raw_vgen_mv) / 4U);
    ctrl->igen_ma      = raw_igen_ma;

    /* Глобальні аварійні перевірки */
    if (!temp_ok) {
        ctrl->fault = WIND_FAULT_HEATSINK_OVERTEMP;
        wind_transition_to(ctrl, WIND_STATE_FAULT_LATCH);
        return;
    }
    if (ctrl->vbat_mv > VBAT_OVERVOLTAGE_ALARM_MV) {
        ctrl->fault = WIND_FAULT_BATTERY_OVERVOLTAGE;
        wind_transition_to(ctrl, WIND_STATE_FAULT_LATCH);
        return;
    }
    if (ctrl->rpm_filtered > RPM_OVERSPEED_LIMIT && ctrl->state != WIND_STATE_HIGH_WIND_BRAKING) {
        ctrl->fault = WIND_FAULT_ROTOR_OVERSPEED;
        wind_transition_to(ctrl, WIND_STATE_HIGH_WIND_BRAKING);
        return;
    }

    switch (ctrl->state) {
    case WIND_STATE_PARKED_BRAKED:
        /* Вихід із паркування за командою оператора або після перезапуску */
        break;

    case WIND_STATE_STARTUP_RELEASE:
        if (ctrl->rpm_filtered >= RPM_CUT_IN) {
            wind_transition_to(ctrl, WIND_STATE_MPPT_TRACKING);
        }
        break;

    case WIND_STATE_MPPT_TRACKING:
        if (ctrl->rpm_filtered < (RPM_CUT_IN - 20U)) {
            wind_transition_to(ctrl, WIND_STATE_STARTUP_RELEASE);
            break;
        }

        /* Перехід у захист баластом при наборі повної ємності АКБ */
        if (ctrl->vbat_mv >= VBAT_FLOAT_TARGET_MV || ctrl->rpm_filtered >= RPM_RATED) {
            wind_transition_to(ctrl, WIND_STATE_POWER_LIMIT_DUMP);
            break;
        }

        /* Періодичне оновлення MPPT */
        if ((now - ctrl->last_mppt_tick_ms) >= MPPT_UPDATE_INTERVAL_MS) {
            ctrl->last_mppt_tick_ms = now;
            ctrl->mppt_pwm_permille = calculate_optimal_mppt_pwm(ctrl->rpm_filtered, ctrl->vgen_mv);
            hw_set_mppt_pwm(ctrl->mppt_pwm_permille);
        }
        break;

    case WIND_STATE_POWER_LIMIT_DUMP:
        /* П-регулятор баласту для утримання цільової напруги */
        if (ctrl->vbat_mv > VBAT_FLOAT_TARGET_MV) {
            uint32_t err = (uint32_t)(ctrl->vbat_mv - VBAT_FLOAT_TARGET_MV);
            uint32_t duty = (err * 1000U) / (VBAT_ABSORPTION_MAX_MV - VBAT_FLOAT_TARGET_MV);
            if (duty > 1000U) duty = 1000U;
            ctrl->dump_pwm_permille = (uint16_t)duty;
        } else {
            ctrl->dump_pwm_permille = 0;
            if (ctrl->rpm_filtered < (RPM_RATED - 30U)) {
                wind_transition_to(ctrl, WIND_STATE_MPPT_TRACKING);
            }
        }
        hw_set_dump_pwm(ctrl->dump_pwm_permille);
        break;

    case WIND_STATE_HIGH_WIND_BRAKING:
        /* Очікування зниження обертів баластом перед фіксацією реле */
        if (ctrl->rpm_filtered <= RPM_SAFE_BRAKE || (now - ctrl->state_entry_time_ms) > BRAKE_DUMP_TIMEOUT_MS) {
            hw_set_brake_relay(true);
            ctrl->brake_relay_closed = true;
            wind_transition_to(ctrl, WIND_STATE_PARKED_BRAKED);
        }
        break;

    case WIND_STATE_FAULT_LATCH:
        /* Блокування до зняття живлення або очищення помилки */
        break;
    }
}
```
```cpp
#include <chrono>
#include <cstdint>
#include <concepts>
#include <algorithm>
#include <optional>

namespace wind {

using namespace std::chrono_literals;

/* Суворо типізовані одиниці фізичних величин */
struct Millivolts {
    uint16_t value{0};
    constexpr auto operator<=>(const Millivolts&) const = default;
};

struct Milliamps {
    uint16_t value{0};
    constexpr auto operator<=>(const Milliamps&) const = default;
};

struct RotationsPerMinute {
    uint16_t value{0};
    constexpr auto operator<=>(const RotationsPerMinute&) const = default;
};

struct Permille {
    uint16_t value{0}; // 0 .. 1000 (0.0% .. 100.0%)
    constexpr auto operator<=>(const Permille&) const = default;
};

enum class WindState : uint8_t {
    ParkedBraked = 0,
    StartupRelease,
    MpptTracking,
    PowerLimitDump,
    HighWindBraking,
    FaultLatch
};

enum class WindFault : uint8_t {
    None = 0,
    BatteryOvervoltage,
    RotorOverspeed,
    HeatsinkOvertemp
};

struct TurbineLimits {
    Millivolts vbat_nominal{48000};
    Millivolts vbat_float_target{54400};
    Millivolts vbat_absorption_max{57600};
    Millivolts vbat_alarm_cutoff{60000};

    RotationsPerMinute rpm_cut_in{120};
    RotationsPerMinute rpm_rated{450};
    RotationsPerMinute rpm_overspeed{550};
    RotationsPerMinute rpm_safe_brake{200};
};

struct IWindHardware {
    virtual ~IWindHardware() = default;
    virtual void set_mppt_pwm(Permille duty) = 0;
    virtual void set_dump_pwm(Permille duty) = 0;
    virtual void set_short_circuit_relay(bool closed) = 0;
};

class WindTurbineController {
public:
    explicit WindTurbineController(IWindHardware& hw, TurbineLimits limits = {})
        : hw_(hw), limits_(limits)
    {
        apply_hardware_outputs();
    }

    void process(RotationsPerMinute raw_rpm,
                 Millivolts raw_vbat,
                 Millivolts raw_vgen,
                 Milliamps raw_igen,
                 bool heatsink_temp_ok,
                 std::chrono::milliseconds now)
    {
        // IIR-фільтрація вимірювань
        filtered_rpm_.value  = static_cast<uint16_t>((static_cast<uint32_t>(filtered_rpm_.value) * 3U + raw_rpm.value) / 4U);
        filtered_vbat_.value = static_cast<uint16_t>((static_cast<uint32_t>(filtered_vbat_.value) * 3U + raw_vbat.value) / 4U);
        filtered_vgen_.value = static_cast<uint16_t>((static_cast<uint32_t>(filtered_vgen_.value) * 3U + raw_vgen.value) / 4U);

        // Перевірка аварійних умов
        if (!heatsink_temp_ok) {
            trigger_fault(WindFault::HeatsinkOvertemp, now);
            return;
        }
        if (filtered_vbat_ > limits_.vbat_alarm_cutoff) {
            trigger_fault(WindFault::BatteryOvervoltage, now);
            return;
        }
        if (filtered_rpm_ > limits_.rpm_overspeed && state_ != WindState::HighWindBraking) {
            transition_to(WindState::HighWindBraking, now);
            return;
        }

        switch (state_) {
        case WindState::ParkedBraked:
            break;

        case WindState::StartupRelease:
            if (filtered_rpm_ >= limits_.rpm_cut_in) {
                transition_to(WindState::MpptTracking, now);
            }
            break;

        case WindState::MpptTracking:
            if (filtered_rpm_ < RotationsPerMinute{static_cast<uint16_t>(limits_.rpm_cut_in.value - 20U)}) {
                transition_to(WindState::StartupRelease, now);
                break;
            }

            if (filtered_vbat_ >= limits_.vbat_float_target || filtered_rpm_ >= limits_.rpm_rated) {
                transition_to(WindState::PowerLimitDump, now);
                break;
            }

            if ((now - last_mppt_time_) >= 100ms) {
                last_mppt_time_ = now;
                update_cubic_mppt();
            }
            break;

        case WindState::PowerLimitDump:
            update_dump_regulation();
            break;

        case WindState::HighWindBraking:
            if (filtered_rpm_ <= limits_.rpm_safe_brake || (now - state_entry_time_) > 5000ms) {
                hw_.set_short_circuit_relay(true);
                transition_to(WindState::ParkedBraked, now);
            }
            break;

        case WindState::FaultLatch:
            break;
        }
    }

    [[nodiscard]] WindState state() const noexcept { return state_; }
    [[nodiscard]] WindFault fault() const noexcept { return fault_; }
    [[nodiscard]] RotationsPerMinute filtered_rpm() const noexcept { return filtered_rpm_; }
    [[nodiscard]] Millivolts filtered_vbat() const noexcept { return filtered_vbat_; }

private:
    void transition_to(WindState new_state, std::chrono::milliseconds now)
    {
        state_ = new_state;
        state_entry_time_ = now;
        apply_hardware_outputs();
    }

    void trigger_fault(WindFault fault, std::chrono::milliseconds now)
    {
        fault_ = fault;
        transition_to(WindState::FaultLatch, now);
    }

    void apply_hardware_outputs()
    {
        switch (state_) {
        case WindState::ParkedBraked:
        case WindState::FaultLatch:
            mppt_duty_ = Permille{0};
            dump_duty_ = Permille{1000};
            hw_.set_mppt_pwm(mppt_duty_);
            hw_.set_dump_pwm(dump_duty_);
            hw_.set_short_circuit_relay(true);
            break;

        case WindState::StartupRelease:
            mppt_duty_ = Permille{0};
            dump_duty_ = Permille{0};
            hw_.set_mppt_pwm(mppt_duty_);
            hw_.set_dump_pwm(dump_duty_);
            hw_.set_short_circuit_relay(false);
            break;

        case WindState::MpptTracking:
            dump_duty_ = Permille{0};
            hw_.set_dump_pwm(dump_duty_);
            hw_.set_short_circuit_relay(false);
            break;

        case WindState::PowerLimitDump:
            hw_.set_short_circuit_relay(false);
            break;

        case WindState::HighWindBraking:
            mppt_duty_ = Permille{0};
            dump_duty_ = Permille{1000};
            hw_.set_mppt_pwm(mppt_duty_);
            hw_.set_dump_pwm(dump_duty_);
            hw_.set_short_circuit_relay(false);
            break;
        }
    }

    void update_cubic_mppt()
    {
        if (filtered_rpm_ < limits_.rpm_cut_in) {
            mppt_duty_ = Permille{0};
        } else {
            const auto span = static_cast<uint32_t>(limits_.rpm_rated.value - limits_.rpm_cut_in.value);
            auto delta = static_cast<uint32_t>(filtered_rpm_.value - limits_.rpm_cut_in.value);
            delta = std::min(delta, span);
            const uint32_t target = (delta * delta * delta) / (span * span / 1000U);
            mppt_duty_ = Permille{static_cast<uint16_t>(std::min(target, 1000U))};
        }
        hw_.set_mppt_pwm(mppt_duty_);
    }

    void update_dump_regulation()
    {
        if (filtered_vbat_ > limits_.vbat_float_target) {
            const auto err = static_cast<uint32_t>(filtered_vbat_.value - limits_.vbat_float_target.value);
            const auto range = static_cast<uint32_t>(limits_.vbat_absorption_max.value - limits_.vbat_float_target.value);
            const uint32_t duty = (err * 1000U) / range;
            dump_duty_ = Permille{static_cast<uint16_t>(std::min(duty, 1000U))};
        } else {
            dump_duty_ = Permille{0};
            if (filtered_rpm_ < RotationsPerMinute{static_cast<uint16_t>(limits_.rpm_rated.value - 30U)}) {
                transition_to(WindState::MpptTracking, state_entry_time_);
            }
        }
        hw_.set_dump_pwm(dump_duty_);
    }

    IWindHardware& hw_;
    TurbineLimits limits_;
    WindState state_{WindState::ParkedBraked};
    WindFault fault_{WindFault::None};
    std::chrono::milliseconds state_entry_time_{0};
    std::chrono::milliseconds last_mppt_time_{0};

    RotationsPerMinute filtered_rpm_{0};
    Millivolts filtered_vbat_{0};
    Millivolts filtered_vgen_{0};
    Permille mppt_duty_{0};
    Permille dump_duty_{0};
};

} // namespace wind
```
:::

### Інженерні пастки при розробці прошивки вітрогенератора

1. **Інерційний зрив ротора (Rotor Stall Trap):**
   Якщо алгоритм MPPT змінює коефіцієнт заповнення ШІМ із частотою сонячного трекера (наприклад, 100–500 Гц), швидке збільшення відбору потужності створює електромагнітний гальмівний момент `T_em`, який у рази перевищує аеродинамічний момент лопатей `T_aero`. Кінетична енергія важкого вітроколеса миттєво здувається, оберти падають нижче точки зриву потоку, і турбіна зупиняється на повному вітрі. Програмний контур MPPT обов'язково повинен містити цифрову фільтрацію швидкості обертання та адаптаційні паузи тривалістю не менше 0.5–1.5 секунди.

2. **Залипання реле в аварійному режимі (Relay Arc & Contact Welding):**
   Пряме замикання трифазного електромеханічного реле на повних штормових обертах (500–700 об/хв) призводить до виникнення пускового змінного струму амплітудою в сотні ампер. Електрична дуга миттєво зварює контакти реле, роблячи його нездатним розімкнутися після закінчення шторму. Тому прошивка реалізує **двоетапне гальмування**: спочатку відкривається твердотільний баласт (Dump Load) на 100% ШІМ, збиває оберти нижче `RPM_SAFE_BRAKE`, і лише після цього замикаються силові сухі контакти реле.

3. **Брязкіт перемикання при граничних швидкостях вітру (Hunting Oscillation):**
   Коли швидкість вітру коливається навколо порогу початку генерації `RPM_CUT_IN`, спрощене порогове керування викликає безперервне вмикання та вимикання силового перетворювача (явище «полювання» регулятора). Це створює акустичний шум, зношує комутаційні вузли та розігріває ключі. Скінченний автомат усуває цю проблему введенням програмного гістерезису (наприклад, відключення відбору відбувається лише при падінні обертів нижче `RPM_CUT_IN - 20 об/хв`) та затримки дебаунсу при переході між станами.

4. **Теплове накопичення у баластному каскаді:**
   При тривалому штормовому вітрі баластні резистори можуть безперервно розсіювати кіловати тепла протягом кількох годин. Якщо температура радіатора перевищує критичний поріг (наприклад, 85 °C), прошивка не має права просто вимкнути баласт, оскільки це призведе до миттєвого розносу вітроколеса. Контролер переходить у режим аварійного штормового гальмування (`HIGH_WIND_BRAKING`), скидає оберти ротора до мінімуму і замикає реле короткого замикання, повністю зупиняючи приплив енергії.
