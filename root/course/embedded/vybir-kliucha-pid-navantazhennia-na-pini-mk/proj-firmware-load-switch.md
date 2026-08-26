# ⚙️ Програмне керування силовими ключами та захист каналів

Керування силовими ключами з боку вбудованого програмного забезпечення вимагає суворого дотримання трьох правил безпеки: виключення паразитних імпульсів *(Glitch)* під час старту мікроконтролера, плавне наростання шпаруватості ШІМ для обмеження пускового струму холодного навантаження *(Soft-Start)* та апаратне вимкнення каналу за таймаутом чи аварійним сигналом. Цей проєкт розбирає архітектуру надійного драйвера комутації навантаження та надає готові реалізації мовами C та C++.

---

## 1. Апаратні передумови та ризики вбудованого ПЗ

Коли мікроконтролер комутує навантаження зі струмом у кілька ампер, помилка в одному рядку коду ініціалізації виводу може призвести до фізичного руйнування транзистора або механічної аварії приводу.

### 1.1. Стан виводів під час завантаження та апаратного скидання (Reset)

Під час подачі живлення або апаратного скидання мікроконтролера апаратні регістри конфігурації портів повертаються у початковий стан: усі виводи GPIO перемикаються в режим високоімпедансного входу *(Input Floating / High-Z)*.
- Внутрішні стягувальні резистори процесора *(Internal Pull-Down)* за замовчуванням вимкнені або мають занадто високий опір (30–50 кОм).
- Якщо на платі відсутній зовнішній резистор підтяжки до землі номіналом 10–20 кОм, затвор силового MOSFET залишається ізольованим у повітрі.
- Наведені електромагнітні завади від сусідніх ліній живлення або струми витоку друкованої плати можуть зарядити вхідну ємність затвора, через що транзистор самовільно відкриється ще до виконання першої інструкції функції `main()`.

### 1.2. Проблема пускового струму (Inrush Current)

Більшість силових споживачів мають нелінійний опір у момент запуску:
1. **Холодні лампи розжарення та нагрівачі:** опір холодної вольфрамової або ніхромової нитки в 10–14 разів нижчий за опір у розжареному стані. Подача 100% напруги викликає 10-кратний струмовий удар.
2. **Електродвигуни постійного струму:** у момент пуску якір нерухомий, протиелектрорушійна сила *(Back-EMF)* дорівнює нулю, а струм обмежується виключно омічним опором обмотки (`I_start = V_supply / R_armature`), перевищуючи номінальний робочий струм у 5–8 разів.
3. **Ємнісні вхідні фільтри світлодіодних драйверів:** розряджені електролітичні конденсатори під час увімкнення еквівалентні короткому замиканню.

Програмний плавний пуск *(Soft-Start)* поступово нарощує коефіцієнт заповнення ШІМ від 0% до 100% за 50–200 мілісекунд, утримуючи піковий струм у безпечних межах.

### 1.3. Аварійні зависання та захисний таймаут (Watchdog Cutoff)

Якщо мікроконтролер потрапляє в нескінченний цикл, зависає в обробнику помилки `HardFault_Handler` або втрачає зв'язок із головним процесором по шині CAN чи UART, силове навантаження (наприклад, нагрівальний елемент екструдера 3D-принтера або котушка соленоїдного замка) не повинно залишатися увімкненим. Програмний драйвер повинен вимагати періодичного підтвердження активності *(Heartbeat)* і автоматично знеструмлювати канал при перевищенні таймауту безпеки.

### 1.4. Апаратний захист від перевантаження за струмом (Break Input)

Програмне виявлення короткого замикання через регулярне опитування АЦП займає від десятків мікросекунд до кількох мілісекунд через час перетворення та затримку обробки переривань. Для захисту кристала польового транзистора цього часу недостатньо: при прямому короткому замиканні струм наростає до сотень ампер за частки мікросекунди.

Для миттєвого знеструмлення використовують апаратний вхід аварійної зупинки таймера *(Break Input, TIMx_BKIN)*:
1. Силовий шунт у витоку транзистора підключається до вбудованого аналогового компаратора мікроконтролера.
2. Опорна напруга компаратора виставляється внутрішнім ЦАП або резистивним дільником на рівень аварійного струму (наприклад, 10 А).
3. При перевищенні порогу вихід компаратора апаратно збуджує вхід `BKIN` таймера ШІМ.
4. Таймер апаратно переводить вихідні канали у неактивний стан за **15–30 наносекунд**, повністю ігноруючи програмний стек і стан ядра процесора.

---

## 2. Реалізація драйвера: C проти C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Структура конфігурації та стану силового каналу */
typedef struct {
    volatile uint32_t *port_bsrr;  /* Регістр атомарного встановлення/скидання порту (GPIOx->BSRR) */
    uint32_t pin_mask;             /* Бітова маска піна (1 << PIN) */
    volatile uint32_t *timer_ccr;  /* Регістр порівняння таймера ШІМ (TIMx->CCRx) */
    uint32_t timer_arr;            /* Максимальне значення лічильника таймера (TIMx->ARR) */
    uint32_t current_duty;         /* Поточне заповнення (0..1000 = 0.0..100.0%) */
    uint32_t target_duty;          /* Цільове значення заповнення */
    uint32_t step_increment;       /* Крок зміни шпаруватості за 1 мс */
    uint32_t safety_timeout_ms;    /* Залишок часу безпечної роботи каналу */
    bool is_enabled;               /* Прапорець дозволу роботи */
} load_switch_t;

/* Безпечна ініціалізація каналу: скидаємо вихід перед конфігурацією порту */
void load_switch_init(load_switch_t *sw, volatile uint32_t *bsrr, uint32_t pin, 
                      volatile uint32_t *ccr, uint32_t arr, uint32_t step) {
    sw->port_bsrr = bsrr;
    sw->pin_mask = (1UL << pin);
    sw->timer_ccr = ccr;
    sw->timer_arr = arr;
    sw->current_duty = 0;
    sw->target_duty = 0;
    sw->step_increment = (step > 0) ? step : 10;
    sw->safety_timeout_ms = 0;
    sw->is_enabled = false;

    /* Атомарно записуємо логічний нуль у регістр скидання BSRR (старші 16 біт) */
    *(sw->port_bsrr) = (sw->pin_mask << 16U);
    if (sw->timer_ccr != 0) {
        *(sw->timer_ccr) = 0;
    }
}

/* Встановлення цільової потужності з таймаутом безпеки */
void load_switch_set_power(load_switch_t *sw, uint32_t duty_permille, uint32_t timeout_ms) {
    if (duty_permille > 1000) {
        duty_permille = 1000;
    }
    sw->target_duty = duty_permille;
    sw->safety_timeout_ms = timeout_ms;
    sw->is_enabled = (duty_permille > 0);
}

/* Аварійне миттєве знеструмлення каналу */
void load_switch_emergency_stop(load_switch_t *sw) {
    sw->target_duty = 0;
    sw->current_duty = 0;
    sw->is_enabled = false;
    sw->safety_timeout_ms = 0;

    if (sw->timer_ccr != 0) {
        *(sw->timer_ccr) = 0;
    }
    *(sw->port_bsrr) = (sw->pin_mask << 16U);
}

/* Періодичний обробник (викликається щомілісекунди з SysTick або таймера) */
void load_switch_tick_1ms(load_switch_t *sw) {
    /* Перевірка таймауту безпеки */
    if (sw->safety_timeout_ms > 0) {
        sw->safety_timeout_ms--;
        if (sw->safety_timeout_ms == 0) {
            load_switch_emergency_stop(sw);
            return;
        }
    }

    /* Алгоритм плавного пуску та гальмування (Soft-Start / Soft-Stop) */
    if (sw->current_duty < sw->target_duty) {
        sw->current_duty += sw->step_increment;
        if (sw->current_duty > sw->target_duty) {
            sw->current_duty = sw->target_duty;
        }
    } else if (sw->current_duty > sw->target_duty) {
        if (sw->current_duty <= sw->step_increment) {
            sw->current_duty = 0;
        } else {
            sw->current_duty -= sw->step_increment;
        }
    }

    /* Запис нового значення шпаруватості в апаратний регістр порівняння */
    if (sw->timer_ccr != 0) {
        uint32_t compare_val = (sw->current_duty * sw->timer_arr) / 1000U;
        *(sw->timer_ccr) = compare_val;
    }
}
```
```cpp
#include <cstdint>
#include <algorithm>
#include <concepts>

namespace embedded::power {

enum class SwitchState : uint8_t {
    Off = 0,
    RampingUp,
    Running,
    RampingDown,
    FaultTimeout
};

/* Концепт для апаратного рівня доступу до портів введення-виведення */
template <typename T>
concept HardwarePortPolicy = requires(T policy, uint32_t val) {
    { policy.force_low() } noexcept;
    { policy.write_pwm(val) } noexcept;
};

/* Ідіоматичний RAII-драйвер силового ключа */
template <HardwarePortPolicy Policy>
class LoadSwitch {
public:
    constexpr LoadSwitch(Policy port_policy, uint32_t timer_arr, uint32_t step_ramp = 15) noexcept
        : policy_(port_policy), timer_arr_(timer_arr), step_increment_(step_ramp) {
        /* При створенні об'єкта RAII гарантує безпечне вимкнення затвора */
        policy_.force_low();
        policy_.write_pwm(0);
    }

    /* Деструктор RAII: гарантовано знеструмлює навантаження при виході з області видимості */
    ~LoadSwitch() noexcept {
        emergency_stop();
    }

    LoadSwitch(const LoadSwitch&) = delete;
    LoadSwitch& operator=(const LoadSwitch&) = delete;
    LoadSwitch(LoadSwitch&&) noexcept = default;
    LoadSwitch& operator=(LoadSwitch&&) noexcept = default;

    /* Встановлення цільової потужності (0..1000 проміле) та таймауту безпеки в мс */
    void set_target(uint16_t permille, uint32_t timeout_ms) noexcept {
        target_duty_ = std::min<uint16_t>(permille, 1000);
        remaining_timeout_ms_ = timeout_ms;
        if (target_duty_ == 0) {
            state_ = SwitchState::RampingDown;
        } else {
            state_ = (current_duty_ < target_duty_) ? SwitchState::RampingUp : SwitchState::RampingDown;
        }
    }

    /* Миттєва зупинка каналу */
    void emergency_stop() noexcept {
        target_duty_ = 0;
        current_duty_ = 0;
        remaining_timeout_ms_ = 0;
        state_ = SwitchState::Off;
        policy_.write_pwm(0);
        policy_.force_low();
    }

    /* Обробник тику системного таймера (1 мс) */
    void update_1ms() noexcept {
        if (remaining_timeout_ms_ > 0) {
            if (--remaining_timeout_ms_ == 0 && target_duty_ > 0) {
                emergency_stop();
                state_ = SwitchState::FaultTimeout;
                return;
            }
        }

        if (current_duty_ != target_duty_) {
            if (current_duty_ < target_duty_) {
                current_duty_ = std::min<uint16_t>(current_duty_ + step_increment_, target_duty_);
            } else {
                current_duty_ = (current_duty_ > step_increment_) ? (current_duty_ - step_increment_) : target_duty_;
            }

            const uint32_t compare_val = (static_cast<uint64_t>(current_duty_) * timer_arr_) / 1000U;
            policy_.write_pwm(compare_val);

            if (current_duty_ == target_duty_) {
                state_ = (target_duty_ > 0) ? SwitchState::Running : SwitchState::Off;
            }
        }
    }

    [[nodiscard]] SwitchState state() const noexcept { return state_; }
    [[nodiscard]] uint16_t current_duty() const noexcept { return current_duty_; }

private:
    Policy policy_;
    const uint32_t timer_arr_;
    const uint32_t step_increment_;
    uint16_t current_duty_{0};
    uint16_t target_duty_{0};
    uint32_t remaining_timeout_ms_{0};
    SwitchState state_{SwitchState::Off};
};

/* Приклад політики керування для апаратного таймера STM32 */
struct Stm32GpioPwmPolicy {
    volatile uint32_t* const bsrr_reg;
    const uint32_t pin_mask;
    volatile uint32_t* const ccr_reg;

    void force_low() const noexcept {
        *bsrr_reg = (pin_mask << 16U);
    }

    void write_pwm(uint32_t compare_val) const noexcept {
        if (ccr_reg != nullptr) {
            *ccr_reg = compare_val;
        }
    }
};

} // namespace embedded::power
```
:::

---

## 3. Практичні пастки прошивки та налагодження

1. **Зависання ШІМ під час налагодження через SWD/JTAG:**
   Коли розробник зупиняє ядро процесора точкою зупину *(Breakpoint)* у середовищі GDB або Keil, лічильники базових таймерів за замовчуванням продовжують тактуватися або застигають у стані логічної 1. Якщо вихід застиг у високому рівні, через навантаження починає текти безперервний постійний струм, що призводить до перегріву ключа чи соленоїда прямо на робочому столі. Для запобігання цій аварії в контролерах STM32 необхідно сконфігурувати регістр заморожування периферії `DBGMCU_APB1_FZ` (або `DBGMCU_APB2_FZ`), увімкнувши біт `DBG_TIMx_STOP`.

2. **Вибір швидкості наростання фронту GPIO (Slew Rate):**
   При конфігурації виводу мікроконтролера, підключеного до затвора MOSFET через резистор або до входу драйвера затвора, часто помилково обирають максимальну швидкість наростання `GPIO_SPEED_FREQ_VERY_HIGH` (100 МГц). Це створює надвисоку швидкість зміни струму `di/dt` на фронтах і генерує сильні високочастотні електромагнітні завади (EMI) по шині живлення. Для ліній керування силовими ключами з частотами ШІМ до 50 кГц оптимально використовувати режим `GPIO_SPEED_FREQ_LOW` або `GPIO_SPEED_FREQ_MEDIUM` (2–10 МГц).

3. **Розділення сигнальної та силової землі на друкованій платі:**
   Ніколи не з'єднуйте витік силового транзистора із цифровою землею мікроконтролера однією тонкою доріжкою. Струм навантаження в кілька ампер створює імпульсний спад напруги на опорі міді `V = I · R_trace`, що призводить до явища стрибка землі *(Ground Bounce)*. Цей стрибок може змістити логічний нуль на вході драйвера затвора вище порогу перемикання або викликати збій у роботі АЦП. Завжди застосовуйте топологію «зірка» або розділяйте цифрову (AGND/DGND) та силову (PGND) землі з єдиною точкою з'єднання біля конденсатора фільтра живлення.
