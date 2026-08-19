# ⚙️ Алгоритм ультразвукового затиску та гістерезисного керування режимом пачки

При переході імпульсного перетворювача в режим пачки (Burst Mode) на струмах від 200 мкА до 10 мА частота проходження пакетів імпульсів `f_burst` природним чином потрапляє в діапазон від 1 до 18 кГц. Оскільки вихідні керамічні конденсатори класу II (типаж X5R, X7R на основі кристалічного титанату барію BaTiO₃) мають виражені п'єзоелектричні властивості, змінна напруга розмахом 30–100 мВ викликає їхнє періодичне стискання й розтяг. Ці мікродеформації передаються через паяні виводи на склотекстоліт друкованої плати, яка починає працювати як акустична мембрана, створюючи виразний неприємний свист або писк. Для усунення цього дефекту в цифрових та змішаних контролерах живлення застосовують алгоритм ультразвукового затиску (Ultrasonic Clamping), що утримує частоту повторення пачок вище порогу людського сприйняття (понад 25 кГц) або переводить систему в інфразвукову зону (менше 20 Гц) при глибокому сні.

### Фізична природа та акустика явища

Керамічні конденсатори багатошарової структури (MLCC) високої питомої ємності виготовляються з діелектричної кераміки на основі сегнетоелектричного титанату барію. При температурах нижче точки Кюрі (близько +125 °C) кристалічна ґратка титанату барію має тетрагональну структуру без центральної симетрії, що обумовлює наявність спонтанної поляризації.

Під дією прикладеної змінної електричної напруги `V(t)` у кристалі виникає механічна деформація внаслідок двох фізичних ефектів:
1. **Зворотний п'єзоелектричний ефект:** лінійна деформація `Δx = d₃₃ · V(t)`, де `d₃₃` — п'єзоелектричний модуль матеріалу (зазвичай від 100 до 400 пм/В).
2. **Електрострикція:** квадратична деформація `Δx = M · E²(t)`, пропорційна квадрату напруженості електричного поля в тонких шарах діелектрика.

Коли перетворювач працює в режимі пачки, вихідний конденсатор циклічно заряджається серією імпульсів до напруги `V_high` і повільно розряджається струмом навантаження до напруги `V_low`. Напруга на обкладках являє собою пилкоподібну функцію часу з розмахом пульсацій `ΔV_burst = 30..100 мВ` і періодом `T_burst = t_burst + t_sleep`.

Хоча абсолютна амплітуда деформації монолітного корпусу розміру 0805 або 1206 становить лише кілька нанометрів, конденсатор жорстко зафіксований на платі олов'яно-свинцевим або безсвинцевим припоєм. Друкована плата зі склотекстоліту FR-4 товщиною 1.0–1.6 мм має високу пружність і площу в десятки або сотні квадратних сантиметрів. Змінні механічні зусилля на контактних майданчиках згинають плату, змушуючи її коливатися як повноцінний плоский дифузор електродинамічного гучномовця.

Згідно з кривими рівної гучності Флетчера-Менсона (стандарт ISO 226), людське вухо має найвищу чутливість у діапазоні від 2 до 5 кГц. Якщо частота повторення пачок потрапляє в цей спектр, навіть мізерний рівень звукового тиску (SPL понад 20–25 дБ) сприймається користувачем як дратівливий високочастотний писк. У портативній електроніці (смартфони, бездротові навушники, медичні датчики) такий акустичний шум є неприпустимим дефектом якості.

### Принцип та архітектура ультразвукового затиску

Алгоритм ультразвукового затиску усуває акустичний шум за рахунок штучного зміщення спектра механічних коливань за межі чутного діапазону.

Людський слух фізично обмежений верхньою межею близько 20 кГц (для більшості дорослих людей поріг становить 16–18 кГц). Якщо період повторення комутаційних подій гарантовано не перевищує 40 мікросекунд, частота повторення становить:

```
f_clamp_min = 1 / 40 мкс = 25 кГц
```

Усі механічні вібрації кристалічної ґратки та вигин друкованої плати переходять в ультразвукову область, де вони є абсолютно нечутними для людини.

Алгоритм реалізує гібридну адаптивну систему з трьома робочими режимами:

```
                                    Струм навантаження I_out
     0 мкА                    20 мкА                       50 мА                      2 А
       ├────────────────────────┼────────────────────────────┼─────────────────────────┤
       │ MODE_BURST_DEEP_SLEEP  │   MODE_BURST_ULTRASONIC    │   MODE_PWM_CONTINUOUS   │
       │ (Інфразвуковий сон,    │ (Ультразвуковий затиск,    │ (Неперервна ШІМ,        │
       │  f_burst < 20 Гц,      │  f_burst ≥ 26 кГц,         │  f_sw = 1.5 МГц,        │
       │  I_q = 2 мкА)          │  I_q = 50 мкА)             │  I_q = 1.5 мА)          │
```

#### 1. Режим повної неперервної ШІМ (`MODE_PWM_CONTINUOUS`)
Активується при важкому навантаженні (`I_out > 50 мА`). Контролер працює з неперервним струмом дроселя на фіксованій мегагерцовій частоті (1.5 МГц). Втрати провідності домінують, пульсації мінімальні, акустичний шум відсутній, оскільки робоча частота лежить далеко за межами слуху.

#### 2. Режим ультразвукового затиску (`MODE_BURST_ULTRASONIC`)
Активується в діапазоні помірно-малого навантаження (від 50 мкА до 50 мА). Контролер працює за гістерезисним принципом, але з активним таймером обмеження максимальної паузи:
- Після формування робочої пачки напруга сягає `V_high`, і силові ключі вимикаються.
- Одночасно запускається апаратний таймер зворотного відліку з періодом `t_clamp_max = 38 мкс` (`f = 26.3 кГц`).
- Якщо навантаження розрядило вихідний конденсатор до `V_low` раніше ніж за 38 мкс, контролер формує чергову пачку природним шляхом.
- Якщо за 38 мкс напруга ще не опустилася до нижнього порогу, таймер генерує переривання примусового затиску (Clamping Timeout). Контролер примусово вмикає верхній ключ на один ультракороткий такт, підкачуючи мінімальну порцію енергії. Це перезапускає таймер і гарантує, що пауза між механічними імпульсами ніколи не перевищить 38 мкс.

#### 3. Режим інфразвукового глибокого сну (`MODE_BURST_DEEP_SLEEP`)
Коли пристрій переходить в екстремально мале споживання (`I_out < 20 мкА`), утримання ультразвукової частоти 26 кГц стає невигідним: примусові підкачування енергії призведуть до перезаряду вихідного конденсатора вище допустимого порогу безпеки та марно спалюватимуть заряд батареї.
При таких надмалих струмах природний час розряду конденсатора `t_sleep` перевищує 50 мілісекунд, що відповідає частотам пачок менше 20 Гц:

```
f_burst = 1 / 50 мс = 20 Гц
```

Коливання з частотою нижче 20 Гц відносяться до інфразвуку. Людське вухо не здатне сприймати їх як тон чи писк, а енергія одиничного імпульсу занадто мала, щоб викликати відчутну вібрацію. Тому алгоритм безпечно вимикає ультразвуковий таймер і переводить контролер у режим ультраглибокого сну з вимкненням усіх тактових генераторів та струмом спокою `I_q = 1..3 мкА`.

---

### Апаратна периферія для реалізації алгоритму

Для апаратної реалізації супервізора в сучасних мікроконтролерах змішаного сигналу (наприклад, STM32G4 / STM32U5 або спеціалізованих цифрових контролерах живлення TI C2000 / Piccolo) використовуються такі блоки:

1. **Компаратор з програмованим гістерезисом (COMP):** швидкісний аналоговий компаратор із часом затримки менше 20 нс, підключений до дільника вихідної напруги. Внутрішній 12-бітний ЦАП (DAC) динамічно формує опорні рівні `V_high` та `V_low`.
2. **Таймер ультразвукового затиску (HRTIM або LPTIM):** таймер високої роздільної здатності, що скидається по кожному циклу комутації та генерує апаратний тригер затиску при досягненні 38 мкс.
3. **Логіка виявлення перетину нуля (ZCD):** вхідний компаратор, що відстежує потенціал комутаційного вузла для миттєвого вимкнення нижнього ключа при переході струму через нуль.

---

### Програмна реалізація контролера на мовах C та C++

Нижче наведено повну програмну реалізацію супервізора керування режимами живлення з ультразвуковим затиском. Модуль розрахований на роботу в циклі керування цифрового перетворювача або як обробник подій системного таймера.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

#define FREQ_CLAMP_MIN_HZ       26300U                      /* Мінімальна частота затиску */
#define CLAMP_TIMEOUT_US        (1000000U / FREQ_CLAMP_MIN_HZ) /* 38 мкс */
#define INFRASONIC_TIMEOUT_US   50000U                      /* 50 мс (поріг 20 Гц) */
#define CURRENT_PWM_THRESH_UA   50000U                      /* 50 мА - поріг переходу в ШІМ */
#define CURRENT_SLEEP_THRESH_UA 20U                         /* 20 мкА - поріг глибокого сну */
#define V_OVP_OFFSET_MV         120U                        /* Поріг захисту від перенапруги */

typedef enum {
    MODE_PWM_CONTINUOUS,
    MODE_BURST_ULTRASONIC,
    MODE_BURST_DEEP_SLEEP
} power_mode_t;

typedef struct {
    uint32_t v_target_mv;
    uint32_t v_hysteresis_mv;
    uint32_t peak_current_limit_ma;
    uint32_t sleep_timer_us;
    power_mode_t current_mode;
    uint32_t pulses_to_fire;
    bool gate_driver_active;
    bool ovp_alert;
} power_supervisor_t;

void power_supervisor_init(power_supervisor_t *ctx, uint32_t v_target_mv) {
    ctx->v_target_mv = v_target_mv;
    ctx->v_hysteresis_mv = 30; /* ±30 мВ навколо номіналу */
    ctx->peak_current_limit_ma = 400;
    ctx->sleep_timer_us = 0;
    ctx->current_mode = MODE_PWM_CONTINUOUS;
    ctx->pulses_to_fire = 0;
    ctx->gate_driver_active = true;
    ctx->ovp_alert = false;
}

void power_supervisor_update(power_supervisor_t *ctx, uint32_t v_out_mv, uint32_t i_load_ua, uint32_t dt_us) {
    uint32_t v_high = ctx->v_target_mv + ctx->v_hysteresis_mv;
    uint32_t v_low  = ctx->v_target_mv - ctx->v_hysteresis_mv;
    uint32_t v_ovp  = ctx->v_target_mv + V_OVP_OFFSET_MV;

    /* Захист від перенапруги при нульовому навантаженні з активним затиском */
    if (v_out_mv >= v_ovp) {
        ctx->gate_driver_active = false;
        ctx->pulses_to_fire = 0;
        ctx->ovp_alert = true;
        ctx->sleep_timer_us = 0;
        return;
    }
    ctx->ovp_alert = false;

    /* Визначення глобального режиму за струмом навантаження */
    if (i_load_ua > CURRENT_PWM_THRESH_UA) {
        ctx->current_mode = MODE_PWM_CONTINUOUS;
        ctx->gate_driver_active = true;
        ctx->pulses_to_fire = 1;
        ctx->peak_current_limit_ma = 1200;
        ctx->sleep_timer_us = 0;
        return;
    }

    if (i_load_ua < CURRENT_SLEEP_THRESH_UA) {
        ctx->current_mode = MODE_BURST_DEEP_SLEEP;
    } else {
        ctx->current_mode = MODE_BURST_ULTRASONIC;
    }

    /* Логіка гістерезисного автомата станів */
    if (v_out_mv >= v_high) {
        /* Досягнуто верхнього порогу: відключаємо драйвери та нарощуємо таймер сну */
        ctx->gate_driver_active = false;
        ctx->pulses_to_fire = 0;
        ctx->sleep_timer_us += dt_us;

        /* Перевірка умови ультразвукового затиску */
        if (ctx->current_mode == MODE_BURST_ULTRASONIC && ctx->sleep_timer_us >= CLAMP_TIMEOUT_US) {
            ctx->gate_driver_active = true;
            ctx->pulses_to_fire = 1;              /* Поодинокий імпульс затиску */
            ctx->peak_current_limit_ma = 180;     /* Знижений струм для захисту від сплеску */
            ctx->sleep_timer_us = 0;
        }
    } else if (v_out_mv <= v_low) {
        /* Напруга впала нижче порогу: видаємо повноцінну пачку підзарядки */
        ctx->gate_driver_active = true;
        ctx->pulses_to_fire = (ctx->current_mode == MODE_BURST_DEEP_SLEEP) ? 10 : 4;
        ctx->peak_current_limit_ma = 450;
        ctx->sleep_timer_us = 0;
    } else {
        /* Поточна напруга всередині вікна між V_low та V_high */
        if (!ctx->gate_driver_active) {
            ctx->sleep_timer_us += dt_us;
            if (ctx->current_mode == MODE_BURST_ULTRASONIC && ctx->sleep_timer_us >= CLAMP_TIMEOUT_US) {
                ctx->gate_driver_active = true;
                ctx->pulses_to_fire = 1;
                ctx->peak_current_limit_ma = 180;
                ctx->sleep_timer_us = 0;
            }
        }
    }
}
```
```cpp
#include <cstdint>
#include <span>
#include <concepts>
#include <algorithm>

enum class PowerMode : uint8_t {
    PwmContinuous,
    BurstUltrasonic,
    BurstDeepSleep
};

struct SupervisorConfig {
    uint32_t target_voltage_mv{3300};
    uint32_t hysteresis_mv{30};
    uint32_t min_clamp_freq_hz{26300};
    uint32_t clamp_timeout_us{1000000 / min_clamp_freq_hz}; /* 38 мкс */
    uint32_t pwm_threshold_ua{50000};                       /* 50 мА */
    uint32_t deep_sleep_threshold_ua{20};                   /* 20 мкА */
    uint32_t ovp_offset_mv{120};                            /* Поріг OVP */
};

class UltrasonicPowerSupervisor {
public:
    explicit constexpr UltrasonicPowerSupervisor(SupervisorConfig cfg) noexcept
        : config_(cfg) {}

    struct StepAction {
        bool enable_gate_drivers{false};
        uint8_t pulses_to_dispatch{0};
        uint32_t peak_current_target_ma{0};
        PowerMode current_mode{PowerMode::PwmContinuous};
        bool ovp_triggered{false};
    };

    [[nodiscard]] StepAction process_cycle(uint32_t v_out_mv, uint32_t i_load_ua, uint32_t dt_us) noexcept {
        const uint32_t v_high = config_.target_voltage_mv + config_.hysteresis_mv;
        const uint32_t v_low  = config_.target_voltage_mv - config_.hysteresis_mv;
        const uint32_t v_ovp  = config_.target_voltage_mv + config_.ovp_offset_mv;

        /* Захист від перевищення напруги (OVP) */
        if (v_out_mv >= v_ovp) {
            sleep_timer_us_ = 0;
            return {.enable_gate_drivers = false, .pulses_to_dispatch = 0,
                    .peak_current_target_ma = 0, .current_mode = mode_, .ovp_triggered = true};
        }

        /* Автоматичний вибір макрорежиму */
        if (i_load_ua > config_.pwm_threshold_ua) {
            mode_ = PowerMode::PwmContinuous;
            sleep_timer_us_ = 0;
            return {.enable_gate_drivers = true, .pulses_to_dispatch = 1,
                    .peak_current_target_ma = 1200, .current_mode = mode_, .ovp_triggered = false};
        }

        mode_ = (i_load_ua < config_.deep_sleep_threshold_ua)
                ? PowerMode::BurstDeepSleep
                : PowerMode::BurstUltrasonic;

        /* Перевірка стану компаратора */
        if (v_out_mv >= v_high) {
            sleep_timer_us_ += dt_us;
            if (mode_ == PowerMode::BurstUltrasonic && sleep_timer_us_ >= config_.clamp_timeout_us) {
                sleep_timer_us_ = 0;
                return {.enable_gate_drivers = true, .pulses_to_dispatch = 1,
                        .peak_current_target_ma = 180, .current_mode = mode_, .ovp_triggered = false};
            }
            return {.enable_gate_drivers = false, .pulses_to_dispatch = 0,
                    .peak_current_target_ma = 0, .current_mode = mode_, .ovp_triggered = false};
        }

        if (v_out_mv <= v_low) {
            sleep_timer_us_ = 0;
            const uint8_t pulse_count = (mode_ == PowerMode::BurstDeepSleep) ? 10 : 4;
            return {.enable_gate_drivers = true, .pulses_to_dispatch = pulse_count,
                    .peak_current_target_ma = 450, .current_mode = mode_, .ovp_triggered = false};
        }

        /* Напруга всередині вікна регулювання */
        sleep_timer_us_ += dt_us;
        if (mode_ == PowerMode::BurstUltrasonic && sleep_timer_us_ >= config_.clamp_timeout_us) {
            sleep_timer_us_ = 0;
            return {.enable_gate_drivers = true, .pulses_to_dispatch = 1,
                    .peak_current_target_ma = 180, .current_mode = mode_, .ovp_triggered = false};
        }

        return {.enable_gate_drivers = false, .pulses_to_dispatch = 0,
                .peak_current_target_ma = 0, .current_mode = mode_, .ovp_triggered = false};
    }

    [[nodiscard]] constexpr PowerMode active_mode() const noexcept { return mode_; }

private:
    SupervisorConfig config_;
    PowerMode mode_{PowerMode::PwmContinuous};
    uint32_t sleep_timer_us_{0};
};
```
:::

---

### Тонкощі налагодження та схемотехнічні пастки

Під час практичного впровадження ультразвукового затиску розробники стикаються з чотирма типовими підводними каменями:

1. **Фазовий джитер та акустичні бічні смуги (Sideband Spurious Noise):**
   Якщо період затиску коливається навколо 38 мкс із випадковою похибкою (наприклад, через нестабільність внутрішнього RC-генератора або накладання шуму на компаратор), у спектрі виникає низькочастотна амплітудна модуляція. Хоча середня частота становить 26 кГц, спектральні складові огинаючої можуть потрапляти в діапазон 2–8 кГц, викликаючи ледь чутне шурхотіння або шипіння. Лікування полягає у використанні кварцової стабілізації таймера та додаванні цифрового фільтра дребезгу на вході компаратора.

2. **Розряд бутстрепного конденсатора (Bootstrap Refresh):**
   У синхронних перетворювачах драйвер верхнього N-канального MOSFET живиться від бутстрепного конденсатора `C_boot`, який підзаряджається лише тоді, коли нижній ключ відкритий, а комутаційний вузол притягнутий до землі. Під час тривалої фази сну в режимі Burst Mode струм власного витоку діода та драйвера поступово розряджає `C_boot`. Якщо напруга на ньому впаде нижче порогу блокування (UVLO), верхній ключ не зможе відкритися під час пробудження. Алгоритм ультразвукового затиску автоматично вирішує цю проблему: кожен примусовий імпульс із періодом 38 мкс комутує нижній ключ і гарантовано підтримує повний заряд бутстрепної ємності.

3. **Динамічний викид напруги при нульовому навантаженні:**
   Якщо навантаження раптово відключається повністю (`I_out = 0`), примусове впорскування імпульсів ультразвукового затиску накачує магнітну енергію `0.5 · L · I_pk²` у вихідну ємність швидше, ніж конденсатор розряджається через дільник зворотного зв'язку. Напруга `V_out` починає невпинно зростати. Реалізований у коді поріг OVP (`v_ovp`) блокує затиск, дозволяючи напрузі залишатися стабільною ціною короткочасного переходу в безпечний інтервал тиші.
