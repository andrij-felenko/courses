# ⚙️ Дворівневий планувальник з арбітражем та безударним перемиканням

У системах керування рухом (роботизовані платформи, маніпулятори, сервоприводи верстатів із ЧПК) головна небезпека для механіки криється у раптових динамічних перешкодах. Якщо керування спирається виключно на високорівневий планувальник траєкторії (Slow Path із типовим періодом перерахунку графа чи оптимізації 100–500 мс), час реакції на несподівану людину чи перешкоду в зоні руху стає фатальним. За цей час машина встигає подолати значну відстань і спричинити аварію на повній швидкості.

Цей практичний модуль демонструє повну реалізацію вбудованого дворівневого гібридного контролера, що об'єднує:
1. **Швидкий реактивний шар (Fast Path / Рефлекси, 1 кГц):** періодичне опитування давача наближення, миттєве виявлення загрози зіткнення (< 1 мс), примусове придушення команд планувальника та виконання екстреного гальмування із заданим максимальним сповільненням.
2. **Повільний дорадчий шар (Slow Path / Планувальник, 10–50 Гц):** генерація плавної багатоточкової траєкторії руху до цільової координати.
3. **Арбітр без блокувань (Subsumption Arbitrator):** потокобезпечна передача уставок через подвійний атомарний буфер без ризику інверсії пріоритетів і без блокування швидкого контуру м'ютексами.
4. **Модуль безударного злиття (Bumpless Transfer / Re-anchoring):** після усунення перешкоди система синхронізує поточний фізичний стан осі з планувальником і формує кубічний сплайн Ерміта для плавного відновлення руху без стрибка швидкості й струмового удару в моторі.

## Архітектура потоків та розподіл пам'яті

Ключова вимога до проектування швидкого контуру — **абсолютний часовий детермінізм**. Обробник переривання таймера або високопріоритетна задача RTOS, що працює на частоті 1 кГц (бюджет циклу ≤ 1000 мкс), у жодному разі не повинні захоплювати м'ютекси, очікувати на семафори чи виділяти динамічну пам'ять (`malloc`/`new`). 

Взаємодія між ниткою повільного планувальника та швидким контуром керування організована за схемою подвійної буферизації (`double buffering`) з використанням атомарного індексу та бар'єрів пам'яті:
- Планувальник готує нову цільову точку `trajectory_point_t` у неактивному слоті масиву.
- Після завершення формування структури планувальник атомарно публікує новий індекс із семантикою `memory_order_release`.
- Швидкий контур під час кожного такту 1 кГц читає активний індекс із семантикою `memory_order_acquire`, гарантовано отримуючи цілісний зріз даних без блокування обчислень.

```
[ Повільний планувальник (10-50 Гц) ]
                 │
           q_plan(t)
                 ▼
       [ Атомарний буфер ]
                 │
                 ▼
          ┌───────────────┐
          │ Арбітр вибору │ ◄── [ Давач наближення (1 кГц, <1 мс) ]
          └───────┬───────┘
                  │
             q_cmd(t) (Результуюча команда)
                  │
                  ├─► [ Контур швидкості / ШІМ актуатора ]
                  │
                  └─► [ Зворотний зв'язок: Re-anchoring ]
```

## Математична модель безударного злиття (Bumpless Transfer)

Коли реактивний шар зупиняє привід перед перешкодою, фактичне положення осі `current_position` відхиляється від старої планової точки `plan_position`. Якщо після зникнення перешкоди миттєво повернути керування старому планувальнику, виникне ступінчастий розрив положення:

```
Δq = plan_position - current_position
```

Для регулятора положення стрибок `Δq` виглядає як миттєва нескінченна швидкість. У результаті пропорційна й диференціальна ланки видають максимальний струм насичення, викликаючи механічний удар, зрив ротора або спрацьовування захисту інвертора.

Щоб перехід був абсолютно плавним, модуль реалізує кубічну інтерполяцію Ерміта на часовому інтервалі злиття `T_blend` (типово 100–300 мс). Нормований час інтерполяції змінюється від 0 до 1:

```
s = t / T_blend,   де s ∈ [0, 1]
```

Базисні функції кубічного полінома Ерміта забезпечують неперервність положення ($C⁰$) та неперервність швидкості ($C¹$) на обох межах переходу:

```
h00(s) =  2·s³ - 3·s² + 1    [вага початкового положення]
h10(s) =    s³ - 2·s² + s    [вага початкової швидкості]
h01(s) = -2·s³ + 3·s²        [вага цільового положення]
h11(s) =    s³ -   s²        [вага цільової швидкості]
```

Результуюче положення в кожен момент інтерполяції обчислюється як зважена сума граничних станів:

```
q(s) = h00(s)·pos_start + h10(s)·vel_start·T_blend + h01(s)·pos_target + h11(s)·vel_target·T_blend
```

Диференціювання цього виразу за часом дає гладку командну швидкість без стрибків прискорення.

## Реалізація на C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <math.h>

#define CONTROL_FREQ_HZ       1000.0f
#define CONTROL_DT            (1.0f / CONTROL_FREQ_HZ)
#define MAX_ACCEL             5.0f    // м/с^2
#define MAX_DECEL_EMERGENCY   15.0f   // м/с^2 (екстрене рефлекторне гальмування)
#define SAFE_DISTANCE_M       0.30f   // Поріг реактивного спрацювання (30 см)

typedef enum {
    STATE_IDLE,
    STATE_FOLLOWING_PLAN,
    STATE_REACTIVE_OVERRIDE,
    STATE_BLENDING_RECOVERY
} controller_mode_t;

typedef struct {
    float position;
    float velocity;
    float acceleration;
} trajectory_point_t;

typedef struct {
    trajectory_point_t points[2];
    atomic_int active_idx;
} double_buffer_t;

typedef struct {
    // Фізичний стан осі
    float current_position;
    float current_velocity;
    float proximity_distance;
    
    // Стан арбітра
    controller_mode_t mode;
    double_buffer_t plan_buffer;
    
    // Стан рефлекторного гальмування
    float reflex_target_pos;
    
    // Параметри для безударного переходу (Bumpless Transfer)
    float blend_start_pos;
    float blend_start_vel;
    float blend_progress;
    float blend_duration;
    
    // Прапорець для сповіщення планувальника про необхідність репланування
    atomic_bool replan_required;
} hybrid_controller_t;

void hybrid_controller_init(hybrid_controller_t *ctrl) {
    ctrl->current_position = 0.0f;
    ctrl->current_velocity = 0.0f;
    ctrl->proximity_distance = 10.0f;
    ctrl->mode = STATE_IDLE;
    atomic_init(&ctrl->plan_buffer.active_idx, 0);
    atomic_init(&ctrl->replan_required, false);
    ctrl->blend_progress = 0.0f;
    ctrl->blend_duration = 0.20f; // 200 мс інтервал злиття
}

// ── Повільний шар: запис нової уставки фоновим планувальником (10–50 Гц) ─────
void planner_submit_setpoint(hybrid_controller_t *ctrl, const trajectory_point_t *pt) {
    int current_active = atomic_load_explicit(&ctrl->plan_buffer.active_idx, memory_order_relaxed);
    int next_write = 1 - current_active;
    
    ctrl->plan_buffer.points[next_write] = *pt;
    atomic_store_explicit(&ctrl->plan_buffer.active_idx, next_write, memory_order_release);
}

// ── Швидкий шар: 1 кГц цикл детерміністичного арбітражу та актуації ─────────
float fast_path_control_step(hybrid_controller_t *ctrl, float sensor_proximity) {
    ctrl->proximity_distance = sensor_proximity;
    
    // 1. Миттєва перевірка рефлекторного порогу (Fast Path)
    bool hazard = (ctrl->proximity_distance < SAFE_DISTANCE_M);
    
    if (hazard) {
        if (ctrl->mode != STATE_REACTIVE_OVERRIDE) {
            // Перехоплення керування: придушення плану (Subsumption)
            ctrl->mode = STATE_REACTIVE_OVERRIDE;
            ctrl->reflex_target_pos = ctrl->current_position;
            atomic_store_explicit(&ctrl->replan_required, true, memory_order_release);
        }
    }
    
    // 2. Арбітраж і формування керуючого сигналу
    float cmd_velocity = 0.0f;
    
    switch (ctrl->mode) {
        case STATE_REACTIVE_OVERRIDE: {
            // Рефлекторне екстрене гальмування із заданим темпом сповільнення
            if (ctrl->current_velocity > 0.0f) {
                ctrl->current_velocity -= MAX_DECEL_EMERGENCY * CONTROL_DT;
                if (ctrl->current_velocity < 0.0f) ctrl->current_velocity = 0.0f;
            } else if (ctrl->current_velocity < 0.0f) {
                ctrl->current_velocity += MAX_DECEL_EMERGENCY * CONTROL_DT;
                if (ctrl->current_velocity > 0.0f) ctrl->current_velocity = 0.0f;
            }
            
            ctrl->current_position += ctrl->current_velocity * CONTROL_DT;
            cmd_velocity = ctrl->current_velocity;
            
            // Якщо перешкоду усунуто і привід зупинився — переходимо до злиття
            if (!hazard && fabsf(ctrl->current_velocity) < 0.01f) {
                ctrl->mode = STATE_BLENDING_RECOVERY;
                ctrl->blend_start_pos = ctrl->current_position;
                ctrl->blend_start_vel = ctrl->current_velocity;
                ctrl->blend_progress = 0.0f;
            }
            break;
        }
        
        case STATE_BLENDING_RECOVERY: {
            // Обчислення кубічного сплайна Ерміта для повернення на цільовий план
            ctrl->blend_progress += CONTROL_DT / ctrl->blend_duration;
            
            int active = atomic_load_explicit(&ctrl->plan_buffer.active_idx, memory_order_acquire);
            trajectory_point_t target = ctrl->plan_buffer.points[active];
            
            if (ctrl->blend_progress >= 1.0f) {
                // Злиття завершено — повний перехід на план
                ctrl->mode = STATE_FOLLOWING_PLAN;
                ctrl->current_position = target.position;
                ctrl->current_velocity = target.velocity;
                cmd_velocity = target.velocity;
            } else {
                float s = ctrl->blend_progress;
                float h00 = 2.0f * s * s * s - 3.0f * s * s + 1.0f;
                float h10 = s * s * s - 2.0f * s * s + s;
                float h01 = -2.0f * s * s * s + 3.0f * s * s;
                float h11 = s * s * s - s * s;
                
                float blended_pos = h00 * ctrl->blend_start_pos +
                                    h10 * ctrl->blend_start_vel * ctrl->blend_duration +
                                    h01 * target.position +
                                    h11 * target.velocity * ctrl->blend_duration;
                
                cmd_velocity = (blended_pos - ctrl->current_position) / CONTROL_DT;
                ctrl->current_position = blended_pos;
                ctrl->current_velocity = cmd_velocity;
            }
            break;
        }
        
        case STATE_FOLLOWING_PLAN:
        default: {
            // Стандартне відпрацювання уставки планувальника
            int active = atomic_load_explicit(&ctrl->plan_buffer.active_idx, memory_order_acquire);
            trajectory_point_t target = ctrl->plan_buffer.points[active];
            
            ctrl->current_position = target.position;
            ctrl->current_velocity = target.velocity;
            cmd_velocity = target.velocity;
            break;
        }
    }
    
    return cmd_velocity;
}
```
```cpp
#include <atomic>
#include <cmath>
#include <array>
#include <optional>
#include <span>
#include <algorithm>

class HybridTrajectoryController {
public:
    enum class Mode : uint8_t {
        Idle,
        FollowingPlan,
        ReactiveOverride,
        BlendingRecovery
    };

    struct TrajectoryPoint {
        float position{0.0f};
        float velocity{0.0f};
        float acceleration{0.0f};
    };

    explicit HybridTrajectoryController(float safe_distance = 0.30f, 
                                       float max_emergency_decel = 15.0f,
                                       float blend_duration = 0.20f) noexcept
        : safe_distance_m_(safe_distance),
          max_decel_emergency_(max_emergency_decel),
          blend_duration_s_(blend_duration) {}

    // ── Повільний шар (Slow Path): передача нової точки фоновим планувальником
    void submit_planned_setpoint(const TrajectoryPoint& pt) noexcept {
        const auto current_active = active_idx_.load(std::memory_order_relaxed);
        const auto write_idx = 1 - current_active;
        
        plan_buffer_[write_idx] = pt;
        active_idx_.store(write_idx, std::memory_order_release);
    }

    // Перевірка планувальником потреби у повному глобальному реплануванні
    [[nodiscard]] bool check_and_clear_replan_flag() noexcept {
        return replan_required_.exchange(false, std::memory_order_acq_rel);
    }

    // ── Швидкий шар (Fast Path): 1 кГц детерміністичний крок із ISR таймера ──
    [[nodiscard]] float process_control_step(float sensor_proximity_m, float dt = 0.001f) noexcept {
        const bool hazard = (sensor_proximity_m < safe_distance_m_);

        // 1. Миттєве виявлення загрози (Subsumption тригер)
        if (hazard && mode_ != Mode::ReactiveOverride) {
            mode_ = Mode::ReactiveOverride;
            replan_required_.store(true, std::memory_order_release);
        }

        // 2. Арбітраж і розрахунок команди на актуатор
        float output_velocity = 0.0f;

        switch (mode_) {
            case Mode::ReactiveOverride: {
                // Екстрене сповільнення до повної зупинки
                if (current_velocity_ > 0.0f) {
                    current_velocity_ = std::max(0.0f, current_velocity_ - max_decel_emergency_ * dt);
                } else if (current_velocity_ < 0.0f) {
                    current_velocity_ = std::min(0.0f, current_velocity_ + max_decel_emergency_ * dt);
                }

                current_position_ += current_velocity_ * dt;
                output_velocity = current_velocity_;

                // Коли загрозу знято і вісь зупинилась — починаємо злиття
                if (!hazard && std::abs(current_velocity_) < 0.005f) {
                    mode_ = Mode::BlendingRecovery;
                    blend_start_pos_ = current_position_;
                    blend_start_vel_ = current_velocity_;
                    blend_progress_ = 0.0f;
                }
                break;
            }

            case Mode::BlendingRecovery: {
                // Обчислення кубічного сплайна Ерміта C^1 (Bumpless Transfer)
                blend_progress_ += dt / blend_duration_s_;
                const auto active = active_idx_.load(std::memory_order_acquire);
                const auto& target = plan_buffer_[active];

                if (blend_progress_ >= 1.0f) {
                    mode_ = Mode::FollowingPlan;
                    current_position_ = target.position;
                    current_velocity_ = target.velocity;
                    output_velocity = target.velocity;
                } else {
                    const float s = blend_progress_;
                    const float s2 = s * s;
                    const float s3 = s2 * s;

                    const float h00 = 2.0f * s3 - 3.0f * s2 + 1.0f;
                    const float h10 = s3 - 2.0f * s2 + s;
                    const float h01 = -2.0f * s3 + 3.0f * s2;
                    const float h11 = s3 - s2;

                    const float blended_pos = h00 * blend_start_pos_ +
                                              h10 * blend_start_vel_ * blend_duration_s_ +
                                              h01 * target.position +
                                              h11 * target.velocity * blend_duration_s_;

                    output_velocity = (blended_pos - current_position_) / dt;
                    current_position_ = blended_pos;
                    current_velocity_ = output_velocity;
                }
                break;
            }

            case Mode::FollowingPlan:
            case Mode::Idle:
            default: {
                const auto active = active_idx_.load(std::memory_order_acquire);
                const auto& target = plan_buffer_[active];

                current_position_ = target.position;
                current_velocity_ = target.velocity;
                output_velocity = target.velocity;
                break;
            }
        }

        return output_velocity;
    }

    [[nodiscard]] Mode current_mode() const noexcept { return mode_; }
    [[nodiscard]] float current_position() const noexcept { return current_position_; }
    [[nodiscard]] float current_velocity() const noexcept { return current_velocity_; }

private:
    float safe_distance_m_;
    float max_decel_emergency_;
    float blend_duration_s_;

    float current_position_{0.0f};
    float current_velocity_{0.0f};

    Mode mode_{Mode::Idle};

    std::array<TrajectoryPoint, 2> plan_buffer_{};
    std::atomic<int> active_idx_{0};

    float blend_start_pos_{0.0f};
    float blend_start_vel_{0.0f};
    float blend_progress_{0.0f};

    std::atomic<bool> replan_required_{false};
};
```
:::

## Інженерні пастки та їх подолання

Під час інтеграції дворівневих гібридних контролерів розробники найчастіше стикаються з трьома небезпечними дефектами:

1. **Інтегральне насичення (Integrator Windup) у підпорядкованому ПІД-контурі:** коли реактивний шар перехоплює актуатор і гальмує вісь до повної зупинки, контур положення бачить наростаючу різницю між застиглим положенням ротора та віртуальною уставкою старого плану. Інтегральна ланка починає накопичувати помилку, заповнюючи буфер до максимального значення насичення. Щойно реактивний шар відпускає керування, накопичений інтеграл викидає в мотор максимальний струм, спричиняючи дикий ривок і зрізання зубів редуктора.
   *Рішення:* під час активності `STATE_REACTIVE_OVERRIDE` швидкий шар зобов'язаний надсилати сигнал скидання або тимчасового заморожування інтегратора (`PID clamp / freeze`).
2. **Диференційний удар (Derivative Kick):** якщо перемикання між аварійним гальмуванням та плановою траєкторією здійснюється простим ступінчастим перемиканням селектора, миттєвий розрив першої похідної координати викликає імпульсний сплеск диференціальної компоненти ПІД-регулятора. Застосування наведеної інтерполяції Ерміта 3-го порядку усуває стрибок швидкості, гарантуючи $C¹$-гладкість переходу.
3. **Дрейф планувальника та розсинхронізація (State Divergence):** якщо планувальник продовжує обчислювати рух за старим таймлайном, поки вісь фактично стоїть на місці через спрацьовування рефлексу, його внутрішня модель світу стає неадекватною. Прапорець `replan_required` забезпечує зворотний зв'язок: прокинувшись, фоновий планувальник бачить факт перехоплення, зчитує фактичні координати осі та починає побудову нового глобального графа від поточної фізичної точки.

## Профілювання та верифікація затримки реакції

Надійність рефлекторного шару перевіряється апаратним тестуванням із вимірюванням точного часу затримки (лат. *latentia* — «прихованість, затримка»):

- **Апаратний тригер:** вхідний контакт підключають до оптичного датчика або генератора імпульсів, який імітує раптову появу об'єкта.
- **Діагностичний пін GPIO:** на початку функції `fast_path_control_step()` встановлюють логічну одиницю на вільній ніжці мікроконтролера, а після розрахунку команди — скидають у нуль.
- **Осцилограф або логічний аналізатор:** підключають перший канал до сигналу перешкоди, другий — до діагностичного піна, третій — до виходу ШІМ драйвера мотора.

Час від фронту сигналу небезпеки до зміни шпаруватості ШІМ на осцилографі повинен становити строго менше 1 мс (один такт переривання таймера). Будь-який викид тривалості за межі 1000 мкс свідчить про блокування переривань іншими драйверами або помилку пріоритетів NVIC/RTOS.
