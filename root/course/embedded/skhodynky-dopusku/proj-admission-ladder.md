# ⚙️ Скінченний автомат допуску та арбітр уставок

Скінченний автомат допуску керує передачею повноважень між людиною та бортовим алгоритмом і запобігає аваріям під час польотних випробувань нової логіки. Цей модуль реалізує детерміновану систему перемикання чотирьох рівнів допуску (тінь, порадник, під наглядом, вузький домен), перевіряє активність пілота через апаратний перемикач безпеки, плавно змішує уставки для уникнення аеродинамічного удару (безривкове перемикання або *англ.* bumpless transfer) та автоматично переводить борт у захисний стан у разі виходу за обмеження середовища.

## Призначення та місце в системі керування

У системі керування безпілотним апаратом арбітр допуску розташовується між високорівневим планувальником місії (який виконується на супутньому комп'ютері або у нитці штучного інтелекту) та низькорівневим контуром стабілізації польотного контролера (Attitude Controller / Rate PID).

```
   ┌──────────────────────┐              ┌──────────────────────┐
   │  Приймач RC пульта   │              │  Супутній комп'ютер  │
   │  (Стіки пілота, CH7) │              │  (Модель автономії)  │
   └──────────┬───────────┘              └──────────┬───────────┘
              │                                     │
              │ U_pilot(t)                          │ U_algo(t)
              ▼                                     ▼
      ┌─────────────────────────────────────────────────────┐
      │             Арбітр допуску та уставок               │
      │  - Фільтрація брязкоту кнопки безпеки (Debounce)    │
      │  - Моніторинг відхилення стіків (Deadband / Thr)    │
      │  - Розрахунок метрик розбіжності (Shadow Error)     │
      │  - Керування вікном життя порад (TTL Watchdog)      │
      │  - Безривкове змішування уставок (Cross-fading)     │
      └──────────────────────────┬──────────────────────────┘
                                 │
                                 │ U_actuator(t)
                                 ▼
                     ┌───────────────────────┐
                     │ Змішувач моторів /    │
                     │ Сервоприводи елеронів │
                     └───────────────────────┘
```

Головне завдання арбітра — гарантувати абсолютний детермінізм поведінки. Код не використовує динамічного виділення пам'яті (`malloc`, `new`), не містить блокуючих очікувань і виконується за фіксований час `O(1)` у кожному такті польотного циклу (частота 50–200 Гц).

## Математична модель безривкового перемикання

Коли арбітр фіксує перехоплення керування або зміну режиму, різка ступінчаста зміна уставки призводить до стрибка кутового прискорення. Для усунення цього ефекту арбітр виконує часову інтерполяцію між попередньою активною уставкою `U_from` та цільовою уставкою `U_to`:

```
U(t) = (1 − α(t)) · U_from + α(t) · U_to

α(t) = sat_{[0, 1]} ((t − t_event) / T_blend)
```

де функція насичення `sat_{[0, 1]}(x)` обмежує коефіцієнт змішування в діапазоні від 0 до 1, а `T_blend` задає тривалість перехідного вікна (зазвичай 150–250 мс). Інтерполяція застосовується незалежно до всіх компонентів вектора керування: кута крену (`roll`), кута тангажу (`pitch`), кутової швидкості рискання (`yaw_rate`) та нормалізованої тяги моторів (`throttle`).

## Переходи скінченного автомата

Скінченний автомат підтримує шість станів і суворо контролює дозволені шляхи ескалації та деградації повноважень:

```
                  ┌──────────────────────┐
                  │    1. MODE_SHADOW    │
                  └──────────┬───────────┘
                             │  [Перевірено стабільність обчислень]
                             ▼
                  ┌──────────────────────┐
                  │   2. MODE_ADVISORY   │
                  └──────────┬───────────┘
                             │  [Узгоджено рішення з пілотом]
                             ▼
 ┌──────────────┐ [Перехоплення] ┌──────────────────────┐
 │ MODE_MANUAL_ │◄───────────────┤ 3. MODE_SUPERVISED   │
 │ OVERRIDE     │───────────────►└──────────┬───────────┘
 └──────▲───────┘ [Dead Man OK]             │  [Нуль ручних перехоплень]
        │                                   ▼
        │ [Порушення меж ODD]    ┌──────────────────────┐
        └────────────────────────┤4. MODE_BOUNDED_AUTO  │
                                 └──────────┬───────────┘
                                            │  [Критичний збій сенсорів]
                                            ▼
                                 ┌──────────────────────┐
                                 │ 5. MODE_FAILSAFE_RTH │
                                 └──────────────────────┘
```

1. **MODE_SHADOW (Тінь):** Усі виходи закріплені за пілотом (`U_pilot`). Уставки алгоритму передаються в блок обчислення евклідової розбіжності `ΔU = ||U_pilot − U_algo||` та накопичуються у статистичному лічильнику.
2. **MODE_ADVISORY (Порадник):** Керує людина. Алгоритм може виставити прапорець підказки (`submit_suggestion`). Якщо оператор натискає кнопку підтвердження до вичерпання таймера `kSuggestionTtlMs` (1.5 с), борт разово виконує запропонований маневр, після чого автоматично повертається до очікування.
3. **MODE_SUPERVISED (Під наглядом):** Алгоритм безпосередньо керує виконавчими органами. Оператор зобов'язаний безперервно утримувати кнопку безпеки (*англ.* dead man's switch). Якщо кнопка відпускається або пілот відхиляє стіки понад 15% від нейтралі, автомат миттєво ініціює перехід у ручний режим із безривковим змішуванням.
4. **MODE_BOUNDED_AUTO (Вузький домен):** Повна автономія в межах робочого домену (ODD). Арбітр контролює просторові межі (дистанція до геозони > 15 м), швидкість вітру (≤ 12 м/с), розмиття точності фільтра Калмана (≤ 2.5 м) та наявність сигналу радіолінка. У разі порушення будь-якої межі автомат самостійно активує процедуру аварійного повернення додому (`MODE_FAILSAFE_RTH`).

## Реалізація на C та C++

Нижче наведено паралельні реалізації арбітра. Варіант на мові C орієнтований на чисті структури та вбудовані RTOS-системи, а варіант на C++ використовує строго типізовані переліки `enum class`, простори імен, статичні методи перевірки та нульові накладні витрати на абстракції (*англ.* zero-cost abstractions).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define ADMISSION_BLEND_TIME_MS      200
#define ADMISSION_DEADMAN_TIMEOUT_MS 300
#define ADMISSION_SUGGESTION_TTL_MS  1500
#define ADMISSION_STICK_TAKEOVER_THR 0.15f

typedef enum {
    MODE_SHADOW = 0,
    MODE_ADVISORY,
    MODE_SUPERVISED,
    MODE_BOUNDED_AUTONOMOUS,
    MODE_MANUAL_OVERRIDE,
    MODE_FAILSAFE_RTH
} admission_mode_t;

typedef struct {
    float roll_deg;      /* Крен: -45.0 .. +45.0 */
    float pitch_deg;     /* Тангаж: -45.0 .. +45.0 */
    float yaw_rate_dps;  /* Кутова швидкість рискання: град/с */
    float throttle_norm; /* Тяга: 0.0 .. 1.0 */
} setpoint_t;

typedef struct {
    float distance_to_fence_m;
    float wind_speed_mps;
    float ekf_pos_uncertainty_m;
    bool  link_alive;
    bool  deadman_pressed;
    bool  suggestion_ack_button;
} telemetry_state_t;

typedef struct {
    admission_mode_t current_mode;
    admission_mode_t target_mode;
    setpoint_t       last_active_setpoint;
    uint32_t         mode_enter_timestamp_ms;
    uint32_t         last_deadman_ping_ms;
    uint32_t         suggestion_timestamp_ms;
    bool             has_pending_suggestion;
    float            blend_progress; /* 0.0 -> 1.0 */
    float            shadow_divergence_accum;
    uint32_t         shadow_sample_count;
} admission_arbiter_t;

void arbiter_init(admission_arbiter_t *arb, admission_mode_t initial_mode) {
    arb->current_mode = initial_mode;
    arb->target_mode = initial_mode;
    arb->last_active_setpoint = (setpoint_t){0.0f, 0.0f, 0.0f, 0.0f};
    arb->mode_enter_timestamp_ms = 0;
    arb->last_deadman_ping_ms = 0;
    arb->suggestion_timestamp_ms = 0;
    arb->has_pending_suggestion = false;
    arb->blend_progress = 1.0f;
    arb->shadow_divergence_accum = 0.0f;
    arb->shadow_sample_count = 0;
}

static bool check_stick_deflection(const setpoint_t *pilot) {
    return (fabsf(pilot->roll_deg) > ADMISSION_STICK_TAKEOVER_THR * 45.0f) ||
           (fabsf(pilot->pitch_deg) > ADMISSION_STICK_TAKEOVER_THR * 45.0f);
}

static setpoint_t blend_setpoints(const setpoint_t *from, const setpoint_t *to, float alpha) {
    if (alpha >= 1.0f) return *to;
    if (alpha <= 0.0f) return *from;
    
    setpoint_t res;
    res.roll_deg      = from->roll_deg      + alpha * (to->roll_deg      - from->roll_deg);
    res.pitch_deg     = from->pitch_deg     + alpha * (to->pitch_deg     - from->pitch_deg);
    res.yaw_rate_dps  = from->yaw_rate_dps  + alpha * (to->yaw_rate_dps  - from->yaw_rate_dps);
    res.throttle_norm = from->throttle_norm + alpha * (to->throttle_norm - from->throttle_norm);
    return res;
}

setpoint_t arbiter_update(admission_arbiter_t *arb,
                          const setpoint_t *pilot_sp,
                          const setpoint_t *algo_sp,
                          const telemetry_state_t *telem,
                          uint32_t now_ms)
{
    setpoint_t target_sp;

    /* 1. Оновлення таймера утримання кнопки аварійного переривання */
    if (telem->deadman_pressed) {
        arb->last_deadman_ping_ms = now_ms;
    }

    /* 2. Обробка переходів скінченного автомата */
    switch (arb->current_mode) {
        case MODE_SHADOW:
            /* Повне керування у пілота; уставка алгоритму йде в аналізатор */
            target_sp = *pilot_sp;
            {
                float d_roll = pilot_sp->roll_deg - algo_sp->roll_deg;
                float d_pitch = pilot_sp->pitch_deg - algo_sp->pitch_deg;
                float err = sqrtf(d_roll * d_roll + d_pitch * d_pitch);
                arb->shadow_divergence_accum += err;
                arb->shadow_sample_count++;
            }
            break;

        case MODE_ADVISORY:
            target_sp = *pilot_sp;
            if (arb->has_pending_suggestion) {
                if (now_ms - arb->suggestion_timestamp_ms > ADMISSION_SUGGESTION_TTL_MS) {
                    /* Застаріла підказка анулюється */
                    arb->has_pending_suggestion = false;
                } else if (telem->suggestion_ack_button) {
                    /* Оператор підтвердив маневр */
                    target_sp = *algo_sp;
                    arb->has_pending_suggestion = false;
                }
            }
            break;

        case MODE_SUPERVISED:
            /* Перевірка сигналу перехоплення або відпускання dead man's switch */
            if (!telem->deadman_pressed || check_stick_deflection(pilot_sp)) {
                arb->current_mode = MODE_MANUAL_OVERRIDE;
                arb->blend_progress = 0.0f;
                target_sp = *pilot_sp;
            } else {
                target_sp = *algo_sp;
            }
            break;

        case MODE_BOUNDED_AUTONOMOUS:
            /* Перевірка виходу за межі робочого домену (ODD) */
            if (telem->distance_to_fence_m < 15.0f ||
                telem->wind_speed_mps > 12.0f ||
                telem->ekf_pos_uncertainty_m > 2.5f ||
                !telem->link_alive)
            {
                arb->current_mode = MODE_FAILSAFE_RTH;
                arb->blend_progress = 0.0f;
                target_sp = *pilot_sp; /* RTH логіка підмінить уставку */
            } else if (check_stick_deflection(pilot_sp)) {
                /* Екстрене перехоплення стіком пілота */
                arb->current_mode = MODE_MANUAL_OVERRIDE;
                arb->blend_progress = 0.0f;
                target_sp = *pilot_sp;
            } else {
                target_sp = *algo_sp;
            }
            break;

        case MODE_MANUAL_OVERRIDE:
            target_sp = *pilot_sp;
            break;

        case MODE_FAILSAFE_RTH:
        default:
            target_sp = *pilot_sp;
            break;
    }

    /* 3. Безривкове змішування уставок (Bumpless Transfer) */
    if (arb->blend_progress < 1.0f) {
        float dt_ratio = 20.0f / (float)ADMISSION_BLEND_TIME_MS; /* Крок 20 мс */
        arb->blend_progress += dt_ratio;
        if (arb->blend_progress > 1.0f) arb->blend_progress = 1.0f;
        
        target_sp = blend_setpoints(&arb->last_active_setpoint, &target_sp, arb->blend_progress);
    }

    arb->last_active_setpoint = target_sp;
    return target_sp;
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <optional>
#include <span>
#include <algorithm>

namespace embedded::autonomy {

enum class AdmissionMode : uint8_t {
    Shadow = 0,
    Advisory,
    Supervised,
    BoundedAutonomous,
    ManualOverride,
    FailsafeRth
};

struct Setpoint {
    float roll_deg{0.0f};      // [-45.0 .. +45.0]
    float pitch_deg{0.0f};     // [-45.0 .. +45.0]
    float yaw_rate_dps{0.0f};  // [deg/s]
    float throttle_norm{0.0f}; // [0.0 .. 1.0]

    [[nodiscard]] constexpr Setpoint blend_to(const Setpoint& target, float alpha) const noexcept {
        if (alpha >= 1.0f) return target;
        if (alpha <= 0.0f) return *this;

        return Setpoint{
            roll_deg      + alpha * (target.roll_deg      - roll_deg),
            pitch_deg     + alpha * (target.pitch_deg     - pitch_deg),
            yaw_rate_dps  + alpha * (target.yaw_rate_dps  - yaw_rate_dps),
            throttle_norm + alpha * (target.throttle_norm - throttle_norm)
        };
    }
};

struct TelemetrySnapshot {
    float distance_to_fence_m{100.0f};
    float wind_speed_mps{0.0f};
    float ekf_uncertainty_m{0.2f};
    bool  link_alive{true};
    bool  deadman_switch{false};
    bool  confirm_button{false};
};

class AdmissionArbiter {
public:
    static constexpr uint32_t kBlendDurationMs      = 200;
    static constexpr uint32_t kDeadmanTimeoutMs     = 300;
    static constexpr uint32_t kSuggestionTtlMs      = 1500;
    static constexpr float    kStickTakeoverRatio   = 0.15f;

    explicit constexpr AdmissionArbiter(AdmissionMode initial_mode) noexcept
        : current_mode_(initial_mode),
          target_mode_(initial_mode) {}

    [[nodiscard]] AdmissionMode current_mode() const noexcept { return current_mode_; }
    [[nodiscard]] float average_divergence() const noexcept {
        return sample_count_ > 0 ? (divergence_sum_ / static_cast<float>(sample_count_)) : 0.0f;
    }

    void submit_suggestion(uint32_t timestamp_ms) noexcept {
        suggestion_time_ms_ = timestamp_ms;
        pending_suggestion_ = true;
    }

    Setpoint update(const Setpoint& pilot_sp,
                    const Setpoint& algo_sp,
                    const TelemetrySnapshot& telem,
                    uint32_t now_ms) noexcept
    {
        Setpoint target_sp = pilot_sp;

        if (telem.deadman_switch) {
            last_deadman_ping_ms_ = now_ms;
        }

        switch (current_mode_) {
            case AdmissionMode::Shadow:
                target_sp = pilot_sp;
                accumulate_shadow_divergence(pilot_sp, algo_sp);
                break;

            case AdmissionMode::Advisory:
                target_sp = pilot_sp;
                if (pending_suggestion_) {
                    if (now_ms - suggestion_time_ms_ > kSuggestionTtlMs) {
                        pending_suggestion_ = false; // Вичерпано TTL
                    } else if (telem.confirm_button) {
                        target_sp = algo_sp;
                        pending_suggestion_ = false;
                    }
                }
                break;

            case AdmissionMode::Supervised:
                if (!telem.deadman_switch || is_stick_deflected(pilot_sp)) {
                    trigger_override(pilot_sp);
                    target_sp = pilot_sp;
                } else {
                    target_sp = algo_sp;
                }
                break;

            case AdmissionMode::BoundedAutonomous:
                if (is_outside_odd(telem)) {
                    current_mode_ = AdmissionMode::FailsafeRth;
                    blend_progress_ = 0.0f;
                    target_sp = pilot_sp;
                } else if (is_stick_deflected(pilot_sp)) {
                    trigger_override(pilot_sp);
                    target_sp = pilot_sp;
                } else {
                    target_sp = algo_sp;
                }
                break;

            case AdmissionMode::ManualOverride:
            case AdmissionMode::FailsafeRth:
            default:
                target_sp = pilot_sp;
                break;
        }

        return apply_bumpless_blending(target_sp);
    }

private:
    AdmissionMode current_mode_;
    AdmissionMode target_mode_;
    Setpoint      last_output_sp_{};
    uint32_t      last_deadman_ping_ms_{0};
    uint32_t      suggestion_time_ms_{0};
    bool          pending_suggestion_{false};
    float         blend_progress_{1.0f};

    float         divergence_sum_{0.0f};
    uint32_t      sample_count_{0};

    [[nodiscard]] static bool is_stick_deflected(const Setpoint& sp) noexcept {
        return (std::abs(sp.roll_deg) > kStickTakeoverRatio * 45.0f) ||
               (std::abs(sp.pitch_deg) > kStickTakeoverRatio * 45.0f);
    }

    [[nodiscard]] static bool is_outside_odd(const TelemetrySnapshot& telem) noexcept {
        return (telem.distance_to_fence_m < 15.0f) ||
               (telem.wind_speed_mps > 12.0f) ||
               (telem.ekf_uncertainty_m > 2.5f) ||
               (!telem.link_alive);
    }

    void trigger_override(const Setpoint& pilot_sp) noexcept {
        current_mode_ = AdmissionMode::ManualOverride;
        blend_progress_ = 0.0f;
        last_output_sp_ = pilot_sp;
    }

    void accumulate_shadow_divergence(const Setpoint& pilot_sp, const Setpoint& algo_sp) noexcept {
        const float d_roll = pilot_sp.roll_deg - algo_sp.roll_deg;
        const float d_pitch = pilot_sp.pitch_deg - algo_sp.pitch_deg;
        divergence_sum_ += std::sqrt(d_roll * d_roll + d_pitch * d_pitch);
        sample_count_++;
    }

    Setpoint apply_bumpless_blending(const Setpoint& desired_sp) noexcept {
        if (blend_progress_ < 1.0f) {
            constexpr float kDtRatio = 20.0f / static_cast<float>(kBlendDurationMs);
            blend_progress_ = std::min(1.0f, blend_progress_ + kDtRatio);
            last_output_sp_ = last_output_sp_.blend_to(desired_sp, blend_progress_);
        } else {
            last_output_sp_ = desired_sp;
        }
        return last_output_sp_;
    }
};

} // namespace embedded::autonomy
```
:::

## Покроковий розбір польотного сценарію

Розглянемо послідовність дій арбітра в типовому випробувальному вильоті:

1. **Ініціалізація та зліт (0 .. 60 с):** Апарат злітає під ручним керуванням пілота у режимі `MODE_SHADOW`. Досліджувана нейромережева модель розпізнавання посадкових майданчиків обробляє відеопотік із частотою 30 кадрів/с та генерує віртуальні координати посадки. Арбітр щотакту обчислює різницю між траєкторією пілота та прогнозом моделі, зберігаючи помилку `ΔU` в накопичувач без впливу на мотори.
2. **Активація режиму порадника (60 .. 180 с):** Після стабілізації зв'язку оператор перемикає борт у `MODE_ADVISORY`. Алгоритм виявляє цільову зону і надсилає повідомлення `ADVISORY_SUGGESTION` (маневр зі зниженням швидкості до 5 м/с та доворотом курсу на 40°). Наземна станція відображає маркер маневру з таймером 1.5 с. Пілот візуально оцінює безпеку і натискає тумблер підтвердження на 0.8 секунді. Арбітр підтверджує валідність часового штампа і передає команду на виконання.
3. **Керування під наглядом та екстрене перехоплення (180 .. 300 с):** Борт переходить у `MODE_SUPERVISED`. Пілот тримає палець на пружній кнопці каналу CH7. Алгоритм веде апарат за складною просторовою дугою. На 240 секунді раптовий порив вітру спричиняє розгойдування корпусу, і алгоритм закладає надмірний крен 40°. Пілот миттєво відхиляє правий стік вліво на 30%. Арбітр виявляє перевищення порогу `kStickTakeoverRatio` (15%), деактивує автопілот і за 200 мс плавно переводить кути стабілізації на положення стіків людини, уникаючи звалювання.
4. **Повернення додому (300+ с):** Після стабілізації пілот активує штатний режим повернення на базу, а лог польоту вивантажується для покадрового аналізу аномалії.

## Пастки під час інтеграції в реальне залізо

1. **Плаваючий вхід перемикача перехоплення (Floating Input):** Фізичний контакт перемикача безпеки на макеті або приймачі радіокерування ніколи не повинен залишатися в стані Z-імпедансу. Відсутність апаратного підтягувального резистора (Pull-up 10 кОм до лінії живлення 3.3 В) під час вібрації рами викликає високочастотне перемикання станів (брязкіт), що призводить до хаотичного скидання режимів у польоті.
2. **Інтегральне насичення (Integrator Windup) у момент повернення керування:** Якщо внутрішній контур стабілізації польотного контролера містить інтегральну складову `I_term` для компенсації постійного вітру, під час автономного маневру інтегратор адаптується під уставки алгоритму. Якщо арбітр змінює уставку, але не вирівнює стан інтеграторів, у перший же момент після перемикання апарат отримає потужний обертальний імпульс. Під час переходу в `MODE_MANUAL_OVERRIDE` стан інтеграторів слід примусово заморожувати або перераховувати через поточні кутові швидкості IMU.
3. **Черги повідомлень RTOS із буферизацією (Message Queue Latency):** Якщо між супутнім комп'ютером і польотним контролером використовується черга FreeRTOS розміром понад 1 елемент (`uxQueueLength > 1`), у разі затримки обробки в черзі накопичуються застарілі уставки. Коли оператор вимикає автономію, контролер може продовжувати вичитувати «хвіст» старих команд. Черга уставок завжди повинна мати довжину 1 і оновлюватися викликом `xQueueOverwrite()`.
4. **Гонка станів між таймерами телеметрії та перериваннями (Race Conditions):** Перевірка активності каналу зв'язку (`link_alive`) та лічильника часу кнопки безпеки повинна виконуватися з використанням атомарних операцій (`std::atomic` або заборона переривань `taskENTER_CRITICAL()`). Неатомарне зчитування 32-бітної змінної часу `uint32_t now_ms` на 8- чи 16-бітних архітектурах може призвести до хибного спрацьовування тайм-ауту через одночасне оновлення молодшого й старшого слів таймера.
