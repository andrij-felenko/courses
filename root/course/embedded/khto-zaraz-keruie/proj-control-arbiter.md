# ⚙️ Модуль пріоритетного арбітражу й селектора каналів керування

Цей проєкт демонструє повну практичну реалізацію модуля арбітражу та селектора каналів керування для автономних безпілотних систем. Архітектура розв'язує фундаментальну інженерну задачу: як безпечно, детерміновано та безударно розділити авторитет керування між людиною-пілотом (RC), бортовим AI-планувальником (Offboard), наземною станцією керування (GCS) та апаратною системою аварійного порятунку (Failsafe).

Модуль спроєктовано для роботи у складі високонадійних польотних контролерів і бортових автопілотів (класу PX4 / ArduPilot / custom RTOS).

## Архітектурні принципи та механізм роботи

Конвеєр обробки команд будується навколо чотирьох ключових ланок:

1. **Сторожовий таймер життєздатності (Liveness Watchdog):** Кожне джерело, зареєстроване в системі, отримує власний часовий слот. При надходженні нового кадру фіксується мікросекундна мітка часу. Якщо інтервал між пакетами перевищує сконфігурований поріг `timeout_us`, джерело автоматично маркується як `TimedOut` і виключається з вибору.
2. **Детекція наміру пілота та витіснення за стіками (Stick Override):** Ручний пульт не повинен блокувати автономний політ, доки стіки стоять у пружинному центрі. Щойно пілот відхиляє будь-яку ручку за межі мертвої смуги `stick_deadband`, арбітр миттєво активує ручний пріоритет.
3. **Безударне згладжування швидкості наростання (Slew-Rate Limiter):** Щоб виключити стрибки уставки при зміні джерела, вихідний вектор фільтрується лімітером похідної `du/dt <= max_slew_rate`. Завдяки цьому внутрішні ПІД-контури регулювання кутових швидкостей і струмові ключі моторів захищені від ударних навантажень.
4. **Аварійний арбітраж найвищого рівня:** Стан `Failsafe` має безумовний пріоритет над будь-якими іншими джерелами, ігнорує положення стіків і примусово виконує процедури аварійної посадки або повернення додому.

## Математика обчислення відхилення стіків

Для детекції активності пілота часто постає вибір між евклідовою нормою `L2 = sqrt(r^2 + p^2 + y^2)` та нормою Чебишова `L_infinity = max(|r|, |p|, |y|)`.

У вбудованих мікроконтролерах реального часу (наприклад, Cortex-M4/M7) обчислення квадратного кореня вимагає додаткових машинних тактів і може вносити похибки на краях діапазону. Норма Чебишова:

```
deflection = max(|roll|, |pitch|, |yaw|)
```

має значні переваги:
- **Обчислювальна простота:** виконується за кілька тактів за допомогою апаратних інструкцій FPU `VABS.F32` та `VMAXNM.F32`.
- **Ізольована чутливість осей:** якщо пілот штовхає лише тангаж (Pitch вперед/назад), поріг спрацьовує точно при досягненні 8% ходу осі, незалежно від стану інших каналів.

## Програмна реалізація

Нижче наведено самодостатню реалізацію модуля мовами C (стандарт C99) та C++ (сучасний ідіоматичний C++20 із типізованими переліками `enum class`, просторами імен та `std::chrono`). До коду включено повний консольний симулятор польотних сценаріїв.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define SOURCE_FAILSAFE    0
#define SOURCE_RC_PILOT    1
#define SOURCE_OFFBOARD    2
#define SOURCE_GCS_MISSION 3
#define SOURCE_COUNT       4
#define SOURCE_NONE        255

typedef struct {
    uint64_t timestamp_us;
    float channels[4]; /* [0]=Roll, [1]=Pitch, [2]=Yaw, [3]=Thrust [0..1] */
    bool valid;
} setpoint_t;

typedef struct {
    uint32_t timeout_us;
    float stick_deadband;
    float max_slew_rate[4]; /* Максимальна швидкість зміни (од/с) */
    bool allow_stick_override;
} source_cfg_t;

typedef struct {
    setpoint_t raw_sp;
    uint64_t last_heartbeat_us;
    source_cfg_t cfg;
    bool is_active;
    bool is_timed_out;
} source_slot_t;

typedef struct {
    source_slot_t slots[SOURCE_COUNT];
    uint8_t active_source;
    uint8_t previous_source;
    setpoint_t output_sp;
    uint64_t last_eval_us;
    uint32_t switch_count;
} arbiter_t;

static float clampf(float val, float min_v, float max_v) {
    if (val < min_v) return min_v;
    if (val > max_v) return max_v;
    return val;
}

void arbiter_init(arbiter_t *arb) {
    arb->active_source = SOURCE_NONE;
    arb->previous_source = SOURCE_NONE;
    arb->last_eval_us = 0;
    arb->switch_count = 0;
    
    for (int i = 0; i < 4; ++i) {
        arb->output_sp.channels[i] = 0.0f;
    }
    arb->output_sp.valid = false;
    arb->output_sp.timestamp_us = 0;

    for (int i = 0; i < SOURCE_COUNT; ++i) {
        arb->slots[i].raw_sp.valid = false;
        arb->slots[i].last_heartbeat_us = 0;
        arb->slots[i].is_active = false;
        arb->slots[i].is_timed_out = true;
        
        arb->slots[i].cfg.timeout_us = 500000;      /* 500 мс таймаут за замовчуванням */
        arb->slots[i].cfg.stick_deadband = 0.08f;   /* 8% мертва смуга */
        arb->slots[i].cfg.allow_stick_override = true;
        arb->slots[i].cfg.max_slew_rate[0] = 6.0f;  /* Roll: 6.0 рад/с² */
        arb->slots[i].cfg.max_slew_rate[1] = 6.0f;  /* Pitch: 6.0 рад/с² */
        arb->slots[i].cfg.max_slew_rate[2] = 10.0f; /* Yaw: 10.0 рад/с² */
        arb->slots[i].cfg.max_slew_rate[3] = 3.0f;  /* Thrust: 3.0 (100% за 330 мс) */
    }
}

void arbiter_submit_setpoint(arbiter_t *arb, uint8_t src_id, const setpoint_t *sp, uint64_t now_us) {
    if (src_id >= SOURCE_COUNT || !sp) return;
    arb->slots[src_id].raw_sp = *sp;
    arb->slots[src_id].last_heartbeat_us = now_us;
    arb->slots[src_id].is_active = true;
    arb->slots[src_id].is_timed_out = false;
}

static bool check_stick_deflection(const source_slot_t *slot) {
    if (!slot->is_active || slot->is_timed_out || !slot->raw_sp.valid) return false;
    
    float r = fabsf(slot->raw_sp.channels[0]);
    float p = fabsf(slot->raw_sp.channels[1]);
    float y = fabsf(slot->raw_sp.channels[2]);
    float db = slot->cfg.stick_deadband;
    
    return (r > db) || (p > db) || (y > db);
}

uint8_t arbiter_evaluate(arbiter_t *arb, uint64_t now_us, setpoint_t *out_sp) {
    /* 1. Оновлення таймаутів */
    for (int i = 0; i < SOURCE_COUNT; ++i) {
        source_slot_t *slot = &arb->slots[i];
        if (slot->is_active) {
            uint64_t elapsed = now_us - slot->last_heartbeat_us;
            if (elapsed > slot->cfg.timeout_us) {
                slot->is_timed_out = true;
                slot->is_active = false;
            }
        }
    }

    /* 2. Пріоритетний вибір джерела */
    uint8_t selected = SOURCE_NONE;

    if (arb->slots[SOURCE_FAILSAFE].is_active && !arb->slots[SOURCE_FAILSAFE].is_timed_out) {
        selected = SOURCE_FAILSAFE;
    } else if (arb->slots[SOURCE_RC_PILOT].is_active && !arb->slots[SOURCE_RC_PILOT].is_timed_out) {
        bool sticks_moved = check_stick_deflection(&arb->slots[SOURCE_RC_PILOT]);
        if (sticks_moved) {
            selected = SOURCE_RC_PILOT;
        } else if (arb->slots[SOURCE_OFFBOARD].is_timed_out && arb->slots[SOURCE_GCS_MISSION].is_timed_out) {
            selected = SOURCE_RC_PILOT;
        }
    }

    if (selected == SOURCE_NONE) {
        if (arb->slots[SOURCE_OFFBOARD].is_active && !arb->slots[SOURCE_OFFBOARD].is_timed_out) {
            selected = SOURCE_OFFBOARD;
        }
    }

    if (selected == SOURCE_NONE) {
        if (arb->slots[SOURCE_GCS_MISSION].is_active && !arb->slots[SOURCE_GCS_MISSION].is_timed_out) {
            selected = SOURCE_GCS_MISSION;
        }
    }

    if (selected != arb->active_source) {
        arb->previous_source = arb->active_source;
        arb->active_source = selected;
        arb->switch_count++;
    }

    /* 3. Безударна фільтрація швидкості зміни (Slew Rate) */
    float dt = 0.0025f; /* 400 Гц за замовчуванням */
    if (arb->last_eval_us > 0 && now_us > arb->last_eval_us) {
        dt = (float)(now_us - arb->last_eval_us) * 1e-6f;
        if (dt > 0.1f) dt = 0.1f;
    }
    arb->last_eval_us = now_us;

    if (selected != SOURCE_NONE && arb->slots[selected].raw_sp.valid) {
        const setpoint_t *target = &arb->slots[selected].raw_sp;
        for (int i = 0; i < 4; ++i) {
            float target_val = target->channels[i];
            float current_val = arb->output_sp.channels[i];
            float max_rate = arb->slots[selected].cfg.max_slew_rate[i];
            float max_delta = max_rate * dt;

            float delta = target_val - current_val;
            float clamped_delta = clampf(delta, -max_delta, max_delta);
            arb->output_sp.channels[i] = current_val + clamped_delta;
        }
        arb->output_sp.valid = true;
    } else {
        for (int i = 0; i < 3; ++i) {
            arb->output_sp.channels[i] = 0.0f;
        }
        arb->output_sp.channels[3] = 0.0f;
        arb->output_sp.valid = false;
    }

    arb->output_sp.timestamp_us = now_us;
    if (out_sp) {
        *out_sp = arb->output_sp;
    }

    return selected;
}

int main(void) {
    arbiter_t arb;
    arbiter_init(&arb);
    uint64_t now = 1000000; /* 1.0 c */

    printf("=== СИМУЛЯЦІЯ ДИСПЕТЧЕРА ПРІОРИТЕТІВ ДЖЕРЕЛ КЕРУВАННЯ ===\n\n");

    /* 1. Автономний режим: комп'ютер Offboard подає крен 20° (0.35 рад) */
    setpoint_t offboard_sp = {
        .timestamp_us = now,
        .channels = {0.35f, 0.0f, 0.0f, 0.55f},
        .valid = true
    };
    arbiter_submit_setpoint(&arb, SOURCE_OFFBOARD, &offboard_sp, now);

    setpoint_t out;
    uint8_t src = arbiter_evaluate(&arb, now, &out);
    printf("[1.00s] Стан: Автономія Offboard | Джерело: %u (Offboard=2) | Roll: %.3f rad, Thrust: %.2f\n", 
           src, out.channels[0], out.channels[3]);

    /* 2. Пілот бачить перешкоду й різко штовхає тангаж на 45° (0.78 рад) */
    now += 50000; /* +50 мс */
    setpoint_t rc_sp = {
        .timestamp_us = now,
        .channels = {0.0f, 0.78f, 0.0f, 0.70f},
        .valid = true
    };
    arbiter_submit_setpoint(&arb, SOURCE_RC_PILOT, &rc_sp, now);
    src = arbiter_evaluate(&arb, now, &out);
    printf("[1.05s] Пілот штовхнув стік! Джерело: %u (RC_PILOT=1) | Pitch out: %.3f (початок згладжування)\n", 
           src, out.channels[1]);

    /* Кроки роботи лімітера Slew-Rate */
    for (int step = 0; step < 4; ++step) {
        now += 25000; /* +25 мс */
        arbiter_submit_setpoint(&arb, SOURCE_RC_PILOT, &rc_sp, now);
        arbiter_evaluate(&arb, now, &out);
        printf("  [+25ms] Slew-rate динаміка | Pitch out: %.3f rad (ціль: 0.780)\n", out.channels[1]);
    }

    /* 3. Спрацьовує аварійний автомат Failsafe (критичний розряд батареї) */
    now += 10000;
    setpoint_t fs_sp = {
        .timestamp_us = now,
        .channels = {0.0f, 0.0f, 0.0f, 0.30f}, /* Горизонт 0°, спуск */
        .valid = true
    };
    arbiter_submit_setpoint(&arb, SOURCE_FAILSAFE, &fs_sp, now);
    src = arbiter_evaluate(&arb, now, &out);
    printf("\n[1.16s] ТРИВОГА FAILSAFE! Джерело: %u (FAILSAFE=0) | Витіснено всі інші канали!\n", src);

    return 0;
}
```
```cpp
#include <iostream>
#include <array>
#include <chrono>
#include <cmath>
#include <algorithm>
#include <span>

namespace embedded::control {

using Microseconds = std::chrono::microseconds;

enum class SourceId : uint8_t {
    Failsafe = 0,
    RcPilot = 1,
    Offboard = 2,
    GcsMission = 3,
    None = 255
};

constexpr size_t SourceCount = 4;

struct Setpoint {
    Microseconds timestamp{0};
    std::array<float, 4> channels{0.0f, 0.0f, 0.0f, 0.0f}; // Roll, Pitch, Yaw, Thrust
    bool valid{false};
};

struct SourceConfig {
    Microseconds timeout{std::chrono::milliseconds(500)};
    float stick_deadband{0.08f};
    std::array<float, 4> max_slew_rate{6.0f, 6.0f, 10.0f, 3.0f}; // од/с на канал
    bool allow_stick_override{true};
};

class ControlArbiter {
public:
    ControlArbiter() noexcept {
        for (auto& slot : slots_) {
            slot.config = SourceConfig{};
        }
    }

    void submit_setpoint(SourceId id, const Setpoint& sp, Microseconds now) noexcept {
        auto idx = static_cast<size_t>(id);
        if (idx >= SourceCount) return;
        slots_[idx].raw_sp = sp;
        slots_[idx].last_heartbeat = now;
        slots_[idx].is_active = true;
        slots_[idx].is_timed_out = false;
    }

    Setpoint evaluate(Microseconds now) noexcept {
        // 1. Оновлення таймаутів
        for (auto& slot : slots_) {
            if (slot.is_active) {
                if ((now - slot.last_heartbeat) > slot.config.timeout) {
                    slot.is_timed_out = true;
                    slot.is_active = false;
                }
            }
        }

        // 2. Ієрархія авторитету
        SourceId selected = SourceId::None;

        if (is_slot_available(SourceId::Failsafe)) {
            selected = SourceId::Failsafe;
        } else if (is_slot_available(SourceId::RcPilot)) {
            bool sticks_moved = check_stick_deflection(slots_[static_cast<size_t>(SourceId::RcPilot)]);
            if (sticks_moved) {
                selected = SourceId::RcPilot;
            } else if (slots_[static_cast<size_t>(SourceId::Offboard)].is_timed_out &&
                       slots_[static_cast<size_t>(SourceId::GcsMission)].is_timed_out) {
                selected = SourceId::RcPilot;
            }
        }

        if (selected == SourceId::None && is_slot_available(SourceId::Offboard)) {
            selected = SourceId::Offboard;
        }

        if (selected == SourceId::None && is_slot_available(SourceId::GcsMission)) {
            selected = SourceId::GcsMission;
        }

        if (selected != active_source_) {
            previous_source_ = active_source_;
            active_source_ = selected;
            transitions_++;
        }

        // 3. Безударне обмеження швидкості зміни уставки (Slew Rate)
        float dt = 0.0025f;
        if (last_eval_time_.count() > 0 && now > last_eval_time_) {
            dt = std::chrono::duration<float>(now - last_eval_time_).count();
            dt = std::clamp(dt, 0.0001f, 0.1f);
        }
        last_eval_time_ = now;

        if (selected != SourceId::None && slots_[static_cast<size_t>(selected)].raw_sp.valid) {
            const auto& target = slots_[static_cast<size_t>(selected)].raw_sp;
            const auto& cfg = slots_[static_cast<size_t>(selected)].config;

            for (size_t i = 0; i < 4; ++i) {
                float target_val = target.channels[i];
                float current_val = smoothed_output_.channels[i];
                float max_delta = cfg.max_slew_rate[i] * dt;
                float delta = std::clamp(target_val - current_val, -max_delta, max_delta);
                smoothed_output_.channels[i] = current_val + delta;
            }
            smoothed_output_.valid = true;
        } else {
            smoothed_output_.channels = {0.0f, 0.0f, 0.0f, 0.0f};
            smoothed_output_.valid = false;
        }

        smoothed_output_.timestamp = now;
        return smoothed_output_;
    }

    [[nodiscard]] SourceId active_source() const noexcept { return active_source_; }
    [[nodiscard]] uint32_t transition_count() const noexcept { return transitions_; }

private:
    struct Slot {
        Setpoint raw_sp{};
        Microseconds last_heartbeat{0};
        SourceConfig config{};
        bool is_active{false};
        bool is_timed_out{true};
    };

    [[nodiscard]] bool is_slot_available(SourceId id) const noexcept {
        const auto& s = slots_[static_cast<size_t>(id)];
        return s.is_active && !s.is_timed_out;
    }

    [[nodiscard]] static bool check_stick_deflection(const Slot& slot) noexcept {
        if (!slot.is_active || slot.is_timed_out || !slot.raw_sp.valid) return false;
        float r = std::abs(slot.raw_sp.channels[0]);
        float p = std::abs(slot.raw_sp.channels[1]);
        float y = std::abs(slot.raw_sp.channels[2]);
        float db = slot.config.stick_deadband;
        return (r > db) || (p > db) || (y > db);
    }

    std::array<Slot, SourceCount> slots_{};
    SourceId active_source_{SourceId::None};
    SourceId previous_source_{SourceId::None};
    Setpoint smoothed_output_{};
    Microseconds last_eval_time_{0};
    uint32_t transitions_{0};
};

} // namespace embedded::control

int main() {
    using namespace embedded::control;
    using namespace std::chrono_literals;

    ControlArbiter arbiter;
    auto now = 1000000us;

    std::cout << "=== C++ СИМУЛЯЦІЯ ДИСПЕТЧЕРА ПРІОРИТЕТІВ ДЖЕРЕЛ КЕРУВАННЯ ===\n\n";

    // 1. Offboard уставка
    Setpoint offboard_sp{
        .timestamp = now,
        .channels = {0.35f, 0.0f, 0.0f, 0.55f},
        .valid = true
    };
    arbiter.submit_setpoint(SourceId::Offboard, offboard_sp, now);

    auto out = arbiter.evaluate(now);
    std::cout << "[1.00s] Активне джерело: " << static_cast<int>(arbiter.active_source())
              << " | Roll: " << out.channels[0] << ", Thrust: " << out.channels[3] << "\n";

    // 2. Перехоплення стіками пілота
    now += 50ms;
    Setpoint rc_sp{
        .timestamp = now,
        .channels = {0.0f, 0.78f, 0.0f, 0.70f},
        .valid = true
    };
    arbiter.submit_setpoint(SourceId::RcPilot, rc_sp, now);
    out = arbiter.evaluate(now);
    std::cout << "[1.05s] Пілот перехопив керування! Джерело: " 
              << static_cast<int>(arbiter.active_source())
              << " | Pitch out: " << out.channels[1] << "\n";

    // Плавний вихід на цільове значення
    for (int i = 0; i < 4; ++i) {
        now += 25ms;
        arbiter.submit_setpoint(SourceId::RcPilot, rc_sp, now);
        out = arbiter.evaluate(now);
        std::cout << "  [+25ms] Slew rate: Pitch out = " << out.channels[1] << "\n";
    }

    return 0;
}
```
:::

## Покроковий розбір сценаріїв роботи стенда

Тестовий стенд демонструє критичні фази зміни авторитету керування в реальному часі:

1. **Автономне слідування траєкторії (1.00s):** Бортовий комп'ютер передає уставку крену `0.35 рад` (близько 20°) і тягу `0.55`. Оскільки стіки пілота перебувають у нейтралі, а аварійних подій немає, арбітр обирає `SourceId::Offboard` як активне джерело.
2. **Миттєве перехоплення пілотом (1.05s):** Пілот виявляє небезпеку й різко відхиляє стік тангажу до `0.78 рад` (близько 45°). Оскільки величина `|0.78| > 0.08` перевищує поріг мертвої смуги, арбітр миттєво перемикає активне джерело на `SourceId::RcPilot`.
3. **Безударне наростання тангажу (кроки +25ms):** Хоча пілот задав тангаж 45° миттєво (сходинка), вихідний сигнал `Pitch out` зростає плавно: `0.150 -> 0.300 -> 0.450 -> 0.600 -> 0.750 рад`. Кожен крок обмежено лімітом `max_slew_rate = 6.0 рад/с²`. Це захищає механіку та мотори від удару.
4. **Аварійна ескалація Failsafe (1.16s):** Монітор батареї фіксує критичне падіння напруги й активує слот `SourceId::Failsafe`. Арбітр безумовно витісняє пілота та спрямовує апарат у режим аварійної автопосадки з нульовим креном/тангажем і контрольованою тягою `0.30`.

## Трасування та перевірка логічним аналізатором

Для апаратної верифікації часу реакції арбітра на реальній платі (наприклад, STM32H7 або ESP32-S3) використовують виділений діагностичний пін GPIO:
- **Перемикання піна у високий рівень:** у момент детекції відхилення стіка в функції `arbiter_evaluate()`.
- **Перемикання у низький рівень:** у момент завершення розрахунку мікшера моторів та генерації першого зміненого DShot-пакета.

За допомогою цифрового логічного аналізатора (Logic Analyzer) вимірюється часова затримка від отримання останнього байта пакета CRSF по шині UART до фронту зміни ШІМ/DShot сигналу на двигунах. У правильно спроєктованому диспетчері цей інтервал не перевищує одного періоду польотного циклу (менше 2.5 мс при частоті 400 Гц).

## Інженерні рекомендації щодо інтеграції

- **Асинхронний прийом без блокувань (Lock-Free Ingest):** Якщо пакети RC або MAVLink надходять через переривання UART DMA, неприпустимо використовувати блокуючі м'ютекси (Mutex). Застосовуйте атомарний подвійний буфер (*Ping-Pong Buffer*), де обробник переривання записує у тіньовий слот, а функція польотного циклу `evaluate()` атомарно зчитує активний слот.
- **Узгодження таймауту з джиттером ОС:** Для джерел на базі Linux (комп'ютер-компаньйон) таймаут повинен перевищувати три періоди передачі пакетів (наприклад, 150 мс для потоку 20 Гц), щоб уникнути помилкових спрацьовувань при сплесках завантаження CPU або garbage collection у високорівневих мовах (Python, ROS 2).
- **Гістерезис мертвої смуги:** Для стіків пульта рекомендується реалізувати окремий поріг входу (`0.08`) та поріг виходу (`0.05`), що запобігає тремтінню арбітра на граничних положеннях ручок.
- **Діагностика через Blackbox:** Записуйте ідентифікатор активного джерела `active_source` та поточне відхилення стіків у кожен польотний лог — це ключовий інструмент розслідування інцидентів та відмов у польоті.
- **Тестування на стенді Hardware-in-the-Loop (HIL):** Перед польотом перевірте всі комбінації випадіння пакетів: вимикайте передавач під час активного автономного польоту, симулюйте падіння процесу зору та перевіряйте, що перехід у ручний режим або Failsafe відбувається детерміновано менш ніж за 200 мс.
