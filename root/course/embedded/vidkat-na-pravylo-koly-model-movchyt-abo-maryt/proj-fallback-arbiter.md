# ⚙️ Safe Supervisor: арбітр перемикання ML та безударного відкату на правило

У системах керування реального часу вихід нейромережі не можна безпосередньо комутувати на силове коло актуаторів. Якщо прискорювач інференсу пропускає дедлайн через чергу DMA, тензорний рушій зависає або модель видає хаотичні сплески на зашумленому кадрі, пряме підключення виходу спричиняє ударні навантаження на механіку або аварію апарата. Нижче наведено інженерну реалізацію модуля безпечного арбітражу (**Safe Supervisor**), який поєднує моніторинг здоров'я інференсу, автомат станів із часовим гістерезисом та регулятор із безударним переходом (**bumpless transfer**).

## Архітектурний задум і часові обмеження

Модуль спроєктовано для виконання на високонадійному мікроконтролері реального часу (наприклад, STM32H7, Cortex-M7 або Cortex-R5) у жорсткому періодичному циклі стабілізації (типово 50 Гц або 100 Гц з періодом `dt = 20` мс або `10` мс). 

У той час як нейромережевий інференс виконується асинхронно на окремому прискорювачі (NPU / GPU) і може мати джитер затримки від 8 до 30 мс, наглядач Safe Supervisor працює строго синхронно з таймером ШІМ-генератора актуаторів.

Модуль складається з трьох детермінованих компонентів:

1. **Монітор аномалій (Health Monitor):** 
   - Фіксує порушення дедлайнів виконання за принципом Deadline Watchdog: якщо мітка часу кадру `timestamp_ms` застаріла відносно поточного часу системи більш ніж на `deadline_timeout_ms`, або прапорець свіжості `is_fresh` скинуто, кадр визнається дефектним.
   - Оцінює ентропію Шеннона розподілу ймовірностей softmax. У багатокласовій класифікації розмитий вектор свідчить про глибоку невизначеність моделі на границі розділення класів.
   - Фільтрує поодинокі збої за допомогою кільцевого буфера за правилом «`N` збоїв у вікні з `M` останніх тактів». Це запобігає хибному перехопленню керування через випадковий поодинокий артефакт освітлення.

2. **Арбітр станів (State Arbiter FSM):**
   - `NOMINAL_ML`: штатний режим, у якому команди нейромережі санкціонуються та передаються на приводи. У цей час класичний резервний PID-регулятор працює в тіньовому режимі супроводу (*shadow tracking*).
   - `DEGRADED_HOLD`: проміжний фільтрований стан при виявленні поодинокого збою (1 кадр). Наглядач утримує останній валідний сигнал, не допускаючи різких рухів актуаторів.
   - `RULE_FALLBACK`: повноцінний відкат на детерміноване правило (наприклад, курсовий автопілот за IMU/GNSS). Перехід здійснюється безударно.
   - `EMERGENCY_SAFE`: стан повної відмови, коли як нейромережа, так і резервні алгоритми не здатні втримати об'єкт. Виконується аварійне глушіння або переведення системи в пасивний безпечний стан.

3. **Безударний контур актуації (Bumpless Controller):**
   - У штатному режимі підтримує інтегратор резервного PID-регулятора на рівні, який компенсує поточну помилку відносно виходу нейромережі: `I = u_ml - Kp · e - Kd · ė`. Завдяки цьому при перемиканні розрахунковий вихід правила точно збігається з останнім сигналом моделі (`Δu = 0`).
   - При активації відкату здійснює лінійний або косинусний кросфейдинг (плавне динамічне злиття) впродовж інтервалу `T_trans = 250` мс.
   - Обмежує максимальну швидкість переміщення привода (*slew-rate limiting*), фізично унеможливлюючи небезпечні стрибки напруги чи струму в силовій частині.

## Повний вихідний код модуля на C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_CLASSES 8
#define WINDOW_SIZE 5
#define RECOVERY_TICKS 50

typedef enum {
    SUPERVISOR_STATE_NOMINAL_ML,
    SUPERVISOR_STATE_DEGRADED_HOLD,
    SUPERVISOR_STATE_RULE_FALLBACK,
    SUPERVISOR_STATE_EMERGENCY_SAFE
} supervisor_state_t;

typedef struct {
    float max_allowed_entropy;
    float min_confidence_threshold;
    uint32_t deadline_timeout_ms;
    uint8_t fault_threshold_n;
    float max_slew_rate_deg_per_s;
    float loop_dt_s;
    float kp;
    float ki;
    float kd;
} supervisor_config_t;

typedef struct {
    float u_cmd;
    float confidence;
    float class_probs[MAX_CLASSES];
    uint8_t num_classes;
    uint32_t timestamp_ms;
    bool is_fresh;
} ml_inference_frame_t;

typedef struct {
    float current_state;
    float target_state;
    float current_rate;
} plant_feedback_t;

typedef struct {
    supervisor_config_t cfg;
    supervisor_state_t state;
    uint32_t last_valid_frame_ms;
    uint8_t fault_history[WINDOW_SIZE];
    uint8_t fault_history_idx;
    uint16_t recovery_counter;
    
    /* Тіньовий стан PID */
    float pid_integrator;
    float last_error;
    
    /* Стан згладжування актуатора */
    float last_actuator_output;
    float transition_alpha;
} safe_supervisor_t;

/* Обчислення ентропії Шеннона для оцінки розмитості розподілу */
static float calculate_entropy(const float *probs, uint8_t count) {
    if (count <= 1) return 0.0f;
    float h = 0.0f;
    for (uint8_t i = 0; i < count; ++i) {
        if (probs[i] > 1e-6f) {
            h -= probs[i] * log2f(probs[i]);
        }
    }
    return h;
}

/* Оновлення ковзного вікна N з M */
static bool is_fault_persistent(safe_supervisor_t *sup, bool current_fault) {
    sup->fault_history[sup->fault_history_idx] = current_fault ? 1 : 0;
    sup->fault_history_idx = (sup->fault_history_idx + 1) % WINDOW_SIZE;
    
    uint8_t fault_count = 0;
    for (uint8_t i = 0; i < WINDOW_SIZE; ++i) {
        fault_count += sup->fault_history[i];
    }
    return fault_count >= sup->cfg.fault_threshold_n;
}

/* Ініціалізація супервізора */
void safe_supervisor_init(safe_supervisor_t *sup, const supervisor_config_t *cfg) {
    sup->cfg = *cfg;
    sup->state = SUPERVISOR_STATE_NOMINAL_ML;
    sup->last_valid_frame_ms = 0;
    sup->fault_history_idx = 0;
    sup->recovery_counter = 0;
    sup->pid_integrator = 0.0f;
    sup->last_error = 0.0f;
    sup->last_actuator_output = 0.0f;
    sup->transition_alpha = 1.0f;

    for (uint8_t i = 0; i < WINDOW_SIZE; ++i) {
        sup->fault_history[i] = 0;
    }
}

/* Виконання одного кроку наглядача */
float safe_supervisor_step(safe_supervisor_t *sup,
                           const ml_inference_frame_t *ml_frame,
                           const plant_feedback_t *fb,
                           uint32_t current_time_ms) {
    /* 1. Моніторинг здоров'я інференсу */
    bool timing_fault = (current_time_ms - ml_frame->timestamp_ms) > sup->cfg.deadline_timeout_ms;
    bool freshness_fault = !ml_frame->is_fresh;
    float entropy = calculate_entropy(ml_frame->class_probs, ml_frame->num_classes);
    bool entropy_fault = (entropy > sup->cfg.max_allowed_entropy);
    bool conf_fault = (ml_frame->confidence < sup->cfg.min_confidence_threshold);

    bool frame_fault = timing_fault || freshness_fault || entropy_fault || conf_fault;
    bool persistent_fault = is_fault_persistent(sup, frame_fault);

    if (!frame_fault) {
        sup->last_valid_frame_ms = current_time_ms;
    }

    /* 2. Розрахунок виходу детермінованого резервного правила (PID за IMU/сенсорами) */
    float error = fb->target_state - fb->current_state;
    float p_term = sup->cfg.kp * error;
    float d_term = -sup->cfg.kd * fb->current_rate;
    float u_rule = p_term + sup->pid_integrator + d_term;

    /* 3. Автомат станів Safe Supervisor */
    switch (sup->state) {
    case SUPERVISOR_STATE_NOMINAL_ML:
        if (persistent_fault) {
            sup->state = SUPERVISOR_STATE_RULE_FALLBACK;
            sup->recovery_counter = 0;
            sup->transition_alpha = 0.0f; /* Початок плавного переходу */
        } else if (frame_fault) {
            sup->state = SUPERVISOR_STATE_DEGRADED_HOLD;
        } else {
            /* Тіньове стеження: підтягуємо інтегратор під вихід нейромережі */
            if (sup->cfg.ki > 1e-5f) {
                sup->pid_integrator = ml_frame->u_cmd - p_term - d_term;
            }
        }
        break;

    case SUPERVISOR_STATE_DEGRADED_HOLD:
        if (persistent_fault) {
            sup->state = SUPERVISOR_STATE_RULE_FALLBACK;
            sup->recovery_counter = 0;
            sup->transition_alpha = 0.0f;
        } else if (!frame_fault) {
            sup->state = SUPERVISOR_STATE_NOMINAL_ML;
        }
        break;

    case SUPERVISOR_STATE_RULE_FALLBACK:
        /* Інтегрування для детермінованого контуру */
        sup->pid_integrator += sup->cfg.ki * error * sup->cfg.loop_dt_s;

        /* Гістерезис повернення */
        if (!frame_fault) {
            sup->recovery_counter++;
            if (sup->recovery_counter >= RECOVERY_TICKS) {
                sup->state = SUPERVISOR_STATE_NOMINAL_ML;
                sup->recovery_counter = 0;
            }
        } else {
            sup->recovery_counter = 0;
        }

        /* Критичний таймаут: якщо навіть правило не може втримати об'єкт */
        if (current_time_ms - sup->last_valid_frame_ms > 10000 && fabsf(error) > 45.0f) {
            sup->state = SUPERVISOR_STATE_EMERGENCY_SAFE;
        }
        break;

    case SUPERVISOR_STATE_EMERGENCY_SAFE:
        u_rule = 0.0f; /* Аварійний нуль або глушіння */
        break;
    }

    /* 4. Безударний перехід та генерація санкціонованого сигналу */
    float raw_target = 0.0f;
    if (sup->state == SUPERVISOR_STATE_NOMINAL_ML) {
        raw_target = ml_frame->u_cmd;
    } else if (sup->state == SUPERVISOR_STATE_DEGRADED_HOLD) {
        /* Екстраполяція останнього значення без ривків */
        raw_target = sup->last_actuator_output;
    } else if (sup->state == SUPERVISOR_STATE_RULE_FALLBACK) {
        if (sup->transition_alpha < 1.0f) {
            sup->transition_alpha += sup->cfg.loop_dt_s / 0.25f; /* 250 мс злиття */
            if (sup->transition_alpha > 1.0f) sup->transition_alpha = 1.0f;
        }
        raw_target = (1.0f - sup->transition_alpha) * sup->last_actuator_output +
                     sup->transition_alpha * u_rule;
    } else {
        raw_target = 0.0f;
    }

    /* 5. Обмеження швидкості наростання сигналу (Slew-Rate Limiter) */
    float max_delta = sup->cfg.max_slew_rate_deg_per_s * sup->cfg.loop_dt_s;
    float delta = raw_target - sup->last_actuator_output;
    if (delta > max_delta) delta = max_delta;
    if (delta < -max_delta) delta = -max_delta;

    float final_output = sup->last_actuator_output + delta;
    sup->last_actuator_output = final_output;
    sup->last_error = error;

    return final_output;
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <array>
#include <span>
#include <algorithm>
#include <optional>

namespace safety {

constexpr size_t kMaxClasses = 8;
constexpr size_t kWindowSize = 5;
constexpr uint16_t kRecoveryTicks = 50;

enum class SupervisorState : uint8_t {
    NominalMl,
    DegradedHold,
    RuleFallback,
    EmergencySafe
};

struct SupervisorConfig {
    float max_allowed_entropy{1.2f};
    float min_confidence_threshold{0.65f};
    uint32_t deadline_timeout_ms{25};
    uint8_t fault_threshold_n{3};
    float max_slew_rate_deg_per_s{120.0f};
    float loop_dt_s{0.02f};
    float kp{1.5f};
    float ki{0.4f};
    float kd{0.08f};
};

struct InferenceFrame {
    float u_cmd{0.0f};
    float confidence{0.0f};
    std::array<float, kMaxClasses> class_probs{};
    uint8_t num_classes{0};
    uint32_t timestamp_ms{0};
    bool is_fresh{false};
};

struct PlantFeedback {
    float current_state{0.0f};
    float target_state{0.0f};
    float current_rate{0.0f};
};

class SafeSupervisor {
public:
    explicit SafeSupervisor(const SupervisorConfig& cfg) noexcept
        : cfg_{cfg} {}

    [[nodiscard]] SupervisorState state() const noexcept { return state_; }
    [[nodiscard]] float last_output() const noexcept { return last_actuator_output_; }

    [[nodiscard]] float step(const InferenceFrame& ml_frame,
                             const PlantFeedback& fb,
                             uint32_t current_time_ms) noexcept {
        // 1. Моніторинг здоров'я
        const bool timing_fault = (current_time_ms - ml_frame.timestamp_ms) > cfg_.deadline_timeout_ms;
        const bool freshness_fault = !ml_frame.is_fresh;
        const float entropy = calculate_entropy(std::span{ml_frame.class_probs.data(), ml_frame.num_classes});
        const bool entropy_fault = (entropy > cfg_.max_allowed_entropy);
        const bool conf_fault = (ml_frame.confidence < cfg_.min_confidence_threshold);

        const bool frame_fault = timing_fault || freshness_fault || entropy_fault || conf_fault;
        const bool persistent_fault = update_fault_filter(frame_fault);

        if (!frame_fault) {
            last_valid_frame_ms_ = current_time_ms;
        }

        // 2. Детермінований класичний контур (PID)
        const float error = fb.target_state - fb.current_state;
        const float p_term = cfg_.kp * error;
        const float d_term = -cfg_.kd * fb.current_rate;
        float u_rule = p_term + pid_integrator_ + d_term;

        // 3. Автомат станів
        switch (state_) {
        case SupervisorState::NominalMl:
            if (persistent_fault) {
                state_ = SupervisorState::RuleFallback;
                recovery_counter_ = 0;
                transition_alpha_ = 0.0f;
            } else if (frame_fault) {
                state_ = SupervisorState::DegradedHold;
            } else {
                // Shadow tracking інтегратора під команду моделі
                if (cfg_.ki > 1e-5f) {
                    pid_integrator_ = ml_frame.u_cmd - p_term - d_term;
                }
            }
            break;

        case SupervisorState::DegradedHold:
            if (persistent_fault) {
                state_ = SupervisorState::RuleFallback;
                recovery_counter_ = 0;
                transition_alpha_ = 0.0f;
            } else if (!frame_fault) {
                state_ = SupervisorState::NominalMl;
            }
            break;

        case SupervisorState::RuleFallback:
            pid_integrator_ += cfg_.ki * error * cfg_.loop_dt_s;

            if (!frame_fault) {
                if (++recovery_counter_ >= kRecoveryTicks) {
                    state_ = SupervisorState::NominalMl;
                    recovery_counter_ = 0;
                }
            } else {
                recovery_counter_ = 0;
            }

            if (current_time_ms - last_valid_frame_ms_ > 10000 && std::abs(error) > 45.0f) {
                state_ = SupervisorState::EmergencySafe;
            }
            break;

        case SupervisorState::EmergencySafe:
            u_rule = 0.0f;
            break;
        }

        // 4. Безударний перехід та генерація цільового значення
        float raw_target = 0.0f;
        if (state_ == SupervisorState::NominalMl) {
            raw_target = ml_frame.u_cmd;
        } else if (state_ == SupervisorState::DegradedHold) {
            raw_target = last_actuator_output_;
        } else if (state_ == SupervisorState::RuleFallback) {
            if (transition_alpha_ < 1.0f) {
                transition_alpha_ = std::min(1.0f, transition_alpha_ + cfg_.loop_dt_s / 0.25f);
            }
            raw_target = (1.0f - transition_alpha_) * last_actuator_output_ + transition_alpha_ * u_rule;
        } else {
            raw_target = 0.0f;
        }

        // 5. Slew-rate обмеження швидкості наростання
        const float max_delta = cfg_.max_slew_rate_deg_per_s * cfg_.loop_dt_s;
        const float delta = std::clamp(raw_target - last_actuator_output_, -max_delta, max_delta);

        last_actuator_output_ += delta;
        last_error_ = error;

        return last_actuator_output_;
    }

private:
    [[nodiscard]] static float calculate_entropy(std::span<const float> probs) noexcept {
        if (probs.size() <= 1) return 0.0f;
        float h = 0.0f;
        for (float p : probs) {
            if (p > 1e-6f) {
                h -= p * std::log2(p);
            }
        }
        return h;
    }

    [[nodiscard]] bool update_fault_filter(bool current_fault) noexcept {
        fault_history_[fault_history_idx_] = current_fault ? 1 : 0;
        fault_history_idx_ = (fault_history_idx_ + 1) % kWindowSize;

        uint8_t count = 0;
        for (uint8_t val : fault_history_) {
            count += val;
        }
        return count >= cfg_.fault_threshold_n;
    }

    SupervisorConfig cfg_;
    SupervisorState state_{SupervisorState::NominalMl};
    uint32_t last_valid_frame_ms_{0};
    std::array<uint8_t, kWindowSize> fault_history_{};
    size_t fault_history_idx_{0};
    uint16_t recovery_counter_{0};

    float pid_integrator_{0.0f};
    float last_error_{0.0f};
    float last_actuator_output_{0.0f};
    float transition_alpha_{1.0f};
};

} // namespace safety
```
:::

## Покроковий розбір сценарію відмови (Execution Trace)

Розгляньмо динаміку внутрішніх змінних модуля під час моделювання раптової відмови оптичного інференсу на 50 Гц циклі (`dt = 20` мс):

1. **Такти 0..100 (Штатний рух):** 
   - Модель видає `u_cmd = +10.0°`, впевненість `0.92`, час обчислення `14` мс (`deadline_timeout_ms = 25`).
   - Стан автомата: `NOMINAL_ML`.
   - Інтегратор PID безперервно перераховується: якщо пропорційна помилка курсу `p_term = +2.0°`, інтегратор автоматично набуває значення `pid_integrator = 10.0 - 2.0 = +8.0°`.
   - Актуатор отримує рівно `+10.0°`.

2. **Такт 101 (Поодинокий пропуск кадру):** 
   - Камера зазнала засвітки від спалаху. NPU не зміг сформувати результат за 25 мс (`timing_fault = true`).
   - Кільцевий буфер `N` з `M` містить `[1, 0, 0, 0, 0]` (сума 1 < 3).
   - Стан перемикається в `DEGRADED_HOLD`.
   - Актуатор утримує попереднє значення `+10.0°`. Відкат на правило ще не активовано.

3. **Такти 102..103 (Стійка деградація):** 
   - Наступні кадри мають високу ентропію або запізнення. Буфер містить `[1, 1, 1, 0, 0]` (сума 3 ≥ 3).
   - Спрацьовує умова стійкої аномалії `persistent_fault = true`.
   - Стан перемикається в `RULE_FALLBACK`.
   - Коефіцієнт злиття скидається в `transition_alpha = 0.0`.

4. **Такт 104..116 (Безударний перехід тривалістю 250 мс):**
   - Розрахунковий вихід резервного PID за поточними даними IMU вимагає `u_rule = +4.0°`.
   - На такті 104 `transition_alpha = 0.08`: вихід злиття становить `0.92 · 10.0 + 0.08 · 4.0 = +9.52°`.
   - Slew-rate лімітер обмежує зміну за такт до `120°/с · 0.02 с = 2.4°`. Фактична зміна становить лише `0.48°`, що вкладається в ліміт.
   - До такту 116 `transition_alpha` досягає `1.0`, і керування повністю переходить до правила без жодного стрибка чи удару по механіці.

5. **Такти 117..200 (Робота на резервному правилі та відновлення):**
   - Модель поступово виходить із засвітки і починає знову генерувати валідні кадри.
   - Лічильник відновлення `recovery_counter` починає зростати від 0 до 50.
   - Лише після 50 послідовних бездоганних тактів (рівно 1.0 секунда стабільності) автомат повертається в `NOMINAL_ML`.

## Інженерні пастки реалізації

1. **Неперервне накопичення інтегратора під час роботи ML.** Якщо під час керування нейромережею інтегратор резервного PID не перераховувати в режимі тіньового стеження (`pid_integrator = u_cmd - p_term - d_term`), то на момент аварії він міститиме застаріле, випадкове або насичене значення (*integrator windup*). При перемиканні виникне миттєвий неконтрольований сплеск керуючого сигналу.
2. **Брязкіт станів на границі впевненості.** Якщо модель балансує біля порогу 0.65, без гістерезису `N` з `M` та вікна стабілізації `T_recovery ≥ 50` тактів арбітр перемикатиметься щокадру. Це призведе до хаотичного тремтіння сервоприводів та втрати стійкості об'єкта.
3. **Обмеження швидкості наростання (Slew-rate) без урахування періоду циклу.** Обмеження приросту `Δu_max` обов'язково множиться на дискретний крок `dt`. При змінному періоді виконання циклу (jitter) фіксований приріст спотворює фізичну швидкість переміщення привода.
4. **Обчислення логарифмів без захисту від нуля.** Функція `calculate_entropy` обов'язково перевіряє `probs[i] > 1e-6f`. Спроба обчислити `log2(0.0)` дає `-inf` або `NaN`, що миттєво руйнує всю логіку чисел з плаваючою комою у контурі керування.
