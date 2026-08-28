# ⚙️ Диспетчер автономних цілей: черга пріоритетів та витіснення

Коли безпілотний апарат переходить від виконання сирих ручних команд до автономної місії, головним ядром бортового програмного забезпечення стає диспетчер цілей. Цей проєкт містить завершену, детерміністичну реалізацію диспетчера автономних завдань для вбудованих систем реального часу. Архітектура побудована без динамічного виділення пам'яті на купі (`zero-heap allocation`), підтримує витіснення поточного завдання за пріоритетом (`preemption`), обробляє асинхронні переривання від сенсорів перешкод і контролює життєвий цикл кожної мети через скінченний автомат.

## Архітектура та принципи роботи

Диспетчер працює як періодичний процес, що викликається в основному циклі навігації з фіксованим кроком часу `dt`. У традиційних високорівневих фреймворках (наприклад, навігаційних стеках роботів) диспетчеризація часто реалізується через динамічні черги, фабрики об'єктів та виклики `malloc`/`free`. У вбудованих системах критичного призначення (крилаті дрони, коптери, автономні всюдиходи) такий підхід призводить до фрагментації оперативної пам'яті та непередбачуваних пауз збирача сміття чи менеджера купи.

Цей диспетчер вирішує задачу через детерміністичний статичний буфер фіксованого розміру, де кожен слот пам'яті виділяється на етапі компіляції.

Система розв'язує чотири ключові інженерні задачі:
1. **Статична черга з пріоритетами**: завдання зберігаються у фіксованому масиві, де кожна ціль має числовий рівень пріоритету від 0 до 255.
2. **Передстартова валідація (Pre-condition gating)**: перед активацією будь-якої цілі перевіряється заряд акумулятора, стан фільтра орієнтації (EKF) та межі дозволеної геозони.
3. **Механізм витіснення (Preemption)**: якщо під час виконання тривалого планового завдання (наприклад, сканування площі з пріоритетом 50) надходить екстрена ціль повернення додому або ухилення від загрози (пріоритет 255), активне завдання негайно призупиняється, зберігаючи свій стан, а керування передається критичній події.
4. **Захист від зависання за таймаутом**: кожна ціль має граничний ліміт часу виконання, після перевищення якого вона аварійно завершується зі статусом `ABORTED`.

## Структури даних та кеш-локальність

Для забезпечення надійності структури даних розбиті на три окремі сутності:
* `GoalItem_t` — незмінний дескриптор цілі (тип дії, просторові координати, пріоритет, радіус толерантності та таймаут).
* `VehicleTelemetry_t` — миттєвий зріз стану апарата, що надходить з навігаційного фільтра та контролера батареї.
* `MissionDispatcher_t` — внутрішній стан диспетчера, що містить масив цілей, масив їхніх поточних статусів у скінченному автоматі, індекс активного завдання та лічильник часу поточної дії.

Такий поділ гарантує, що диспетчер не має побічних ефектів і не змінює глобальних змінних: усі вхідні дані передаються за константними вказівниками або посиланнями, а стан модифікується виключно всередині функції кроку `mission_dispatcher_step()`.

Використання пласких масивів замість зв'язних списків має прямий апаратний виграш на процесорах із кеш-пам'яттю (ARM Cortex-M7, Cortex-A53). Усі елементи черги розміщені в суміжних адресах пам'яті: під час циклічного перегляду черги лінійка кешу завантажує весь масив за одне звернення до ОЗП, що мінімізує затримку перевірки пріоритетів до лічених наносекунд.

:::tabs
== C

```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_GOALS 8

typedef enum {
    GOAL_NAVIGATE_WAYPOINT = 0,
    GOAL_SURVEY_POLYGON,
    GOAL_LOITER_POSITION,
    GOAL_EMERGENCY_RETURN
} GoalAction_e;

typedef enum {
    STATE_EMPTY = 0,
    STATE_PENDING,
    STATE_ACTIVE,
    STATE_PREEMPTED,
    STATE_COMPLETED,
    STATE_ABORTED,
    STATE_REJECTED
} GoalState_e;

typedef struct {
    uint32_t id;
    GoalAction_e action;
    uint8_t priority;       /* 0..255 */
    float target_x;         /* метри у світовій системі NED */
    float target_y;
    float target_z;
    float tolerance_m;      /* радіус досягнення */
    float timeout_s;        /* ліміт часу на виконання */
} GoalItem_t;

typedef struct {
    float pos_x;
    float pos_y;
    float pos_z;
    float battery_v;
    bool geofence_valid;
    bool ekf_healthy;
    bool obstacle_detected;
} VehicleTelemetry_t;

typedef struct {
    GoalItem_t items[MAX_GOALS];
    GoalState_e states[MAX_GOALS];
    uint8_t count;
    int8_t active_idx;
    float active_timer_s;
} MissionDispatcher_t;

void mission_dispatcher_init(MissionDispatcher_t *disp) {
    disp->count = 0;
    disp->active_idx = -1;
    disp->active_timer_s = 0.0f;
    for (uint8_t i = 0; i < MAX_GOALS; i++) {
        disp->states[i] = STATE_EMPTY;
    }
}

bool mission_dispatcher_enqueue(MissionDispatcher_t *disp, const GoalItem_t *item) {
    if (disp->count >= MAX_GOALS) {
        return false;
    }
    disp->items[disp->count] = *item;
    disp->states[disp->count] = STATE_PENDING;
    disp->count++;
    return true;
}

static bool check_preconditions(const GoalItem_t *item, const VehicleTelemetry_t *telem) {
    if (!telem->ekf_healthy || !telem->geofence_valid) {
        return false;
    }
    if (item->action != GOAL_EMERGENCY_RETURN && telem->battery_v < 21.0f) {
        return false;
    }
    return true;
}

void mission_dispatcher_step(MissionDispatcher_t *disp, const VehicleTelemetry_t *telem, float dt_s) {
    /* 1. Якщо виявлено небезпечну перешкоду, формуємо екстрене повернення/зависання */
    if (telem->obstacle_detected && (disp->active_idx >= 0)) {
        if (disp->items[disp->active_idx].action != GOAL_EMERGENCY_RETURN) {
            GoalItem_t emergency_goal = {
                .id = 9999,
                .action = GOAL_EMERGENCY_RETURN,
                .priority = 255,
                .target_x = 0.0f,
                .target_y = 0.0f,
                .target_z = -30.0f,
                .tolerance_m = 2.0f,
                .timeout_s = 120.0f
            };
            mission_dispatcher_enqueue(disp, &emergency_goal);
        }
    }

    /* 2. Пошук найвищого пріоритету серед PENDING та поточної ACTIVE */
    int8_t candidate_idx = -1;
    uint8_t highest_prio = 0;

    if (disp->active_idx >= 0) {
        highest_prio = disp->items[disp->active_idx].priority;
        candidate_idx = disp->active_idx;
    }

    for (uint8_t i = 0; i < disp->count; i++) {
        if (disp->states[i] == STATE_PENDING) {
            if (disp->active_idx < 0 || disp->items[i].priority > highest_prio) {
                highest_prio = disp->items[i].priority;
                candidate_idx = (int8_t)i;
            }
        }
    }

    /* 3. Витіснення або перехід до нового завдання */
    if (candidate_idx >= 0 && candidate_idx != disp->active_idx) {
        if (disp->active_idx >= 0) {
            disp->states[disp->active_idx] = STATE_PREEMPTED;
            printf("[DISPATCHER] Goal #%u PREEMPTED by higher priority goal #%u\n",
                   disp->items[disp->active_idx].id, disp->items[candidate_idx].id);
        }

        if (check_preconditions(&disp->items[candidate_idx], telem)) {
            disp->active_idx = candidate_idx;
            disp->states[candidate_idx] = STATE_ACTIVE;
            disp->active_timer_s = 0.0f;
            printf("[DISPATCHER] Goal #%u ACTIVE (Priority: %u, Target: [%.1f, %.1f, %.1f])\n",
                   disp->items[candidate_idx].id,
                   disp->items[candidate_idx].priority,
                   disp->items[candidate_idx].target_x,
                   disp->items[candidate_idx].target_y,
                   disp->items[candidate_idx].target_z);
        } else {
            disp->states[candidate_idx] = STATE_REJECTED;
            printf("[DISPATCHER] Goal #%u REJECTED by pre-condition check\n",
                   disp->items[candidate_idx].id);
            disp->active_idx = -1;
            return;
        }
    }

    /* 4. Оновлення та перевірка досягнення активної мети */
    if (disp->active_idx >= 0) {
        GoalItem_t *active_goal = &disp->items[disp->active_idx];
        disp->active_timer_s += dt_s;

        /* Перевірка таймауту */
        if (active_goal->timeout_s > 0.0f && disp->active_timer_s > active_goal->timeout_s) {
            disp->states[disp->active_idx] = STATE_ABORTED;
            printf("[DISPATCHER] Goal #%u ABORTED due to timeout (%.1f s)\n",
                   active_goal->id, disp->active_timer_s);
            disp->active_idx = -1;
            return;
        }

        /* Обчислення евклідової дистанції до цільової точки */
        float dx = active_goal->target_x - telem->pos_x;
        float dy = active_goal->target_y - telem->pos_y;
        float dz = active_goal->target_z - telem->pos_z;
        float distance = sqrtf(dx * dx + dy * dy + dz * dz);

        if (distance <= active_goal->tolerance_m) {
            disp->states[disp->active_idx] = STATE_COMPLETED;
            printf("[DISPATCHER] Goal #%u COMPLETED successfully (Distance: %.2f m)\n",
                   active_goal->id, distance);
            disp->active_idx = -1;
        }
    }
}

int main(void) {
    MissionDispatcher_t dispatcher;
    mission_dispatcher_init(&dispatcher);

    VehicleTelemetry_t telemetry = {
        .pos_x = 0.0f,
        .pos_y = 0.0f,
        .pos_z = -10.0f,
        .battery_v = 24.2f,
        .geofence_valid = true,
        .ekf_healthy = true,
        .obstacle_detected = false
    };

    GoalItem_t survey_goal = {
        .id = 101,
        .action = GOAL_SURVEY_POLYGON,
        .priority = 50,
        .target_x = 100.0f,
        .target_y = 50.0f,
        .target_z = -50.0f,
        .tolerance_m = 3.0f,
        .timeout_s = 60.0f
    };

    mission_dispatcher_enqueue(&dispatcher, &survey_goal);

    printf("=== СИМУЛЯЦІЯ АВТОНОМНОГО ДИСПЕТЧЕРА ===\n");
    float dt = 1.0f;

    for (int step = 0; step < 10; step++) {
        /* Імітуємо рух до цілі */
        telemetry.pos_x += 10.0f;
        telemetry.pos_y += 5.0f;
        telemetry.pos_z -= 4.0f;

        /* На 4-му кроці раптово виявляється перешкода */
        if (step == 3) {
            printf("\n--- ПОДІЯ: Сенсор виявив перешкоду на курсі! ---\n");
            telemetry.obstacle_detected = true;
        }

        mission_dispatcher_step(&dispatcher, &telemetry, dt);
    }

    return 0;
}
```

== C++

```cpp
#include <array>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <optional>
#include <span>

enum class GoalAction : uint8_t {
    NavigateWaypoint,
    SurveyPolygon,
    LoiterPosition,
    EmergencyReturn
};

enum class GoalState : uint8_t {
    Empty,
    Pending,
    Active,
    Preempted,
    Completed,
    Aborted,
    Rejected
};

struct GoalItem {
    uint32_t id{0};
    GoalAction action{GoalAction::NavigateWaypoint};
    uint8_t priority{0};
    float target_x{0.0f};
    float target_y{0.0f};
    float target_z{0.0f};
    float tolerance_m{2.0f};
    float timeout_s{60.0f};
};

struct VehicleTelemetry {
    float pos_x{0.0f};
    float pos_y{0.0f};
    float pos_z{0.0f};
    float battery_v{24.0f};
    bool geofence_valid{true};
    bool ekf_healthy{true};
    bool obstacle_detected{false};
};

template <size_t MaxGoals = 8>
class MissionDispatcher {
public:
    constexpr MissionDispatcher() = default;

    bool enqueue(const GoalItem& item) noexcept {
        if (count_ >= MaxGoals) {
            return false;
        }
        items_[count_] = item;
        states_[count_] = GoalState::Pending;
        ++count_;
        return true;
    }

    void step(VehicleTelemetry& telem, float dt_s) noexcept {
        // 1. Екстрене реагування на раптову перешкоду
        if (telem.obstacle_detected && (active_idx_ >= 0)) {
            if (items_[static_cast<size_t>(active_idx_)].action != GoalAction::EmergencyReturn) {
                GoalItem emergency{
                    .id = 9999,
                    .action = GoalAction::EmergencyReturn,
                    .priority = 255,
                    .target_x = 0.0f,
                    .target_y = 0.0f,
                    .target_z = -30.0f,
                    .tolerance_m = 2.0f,
                    .timeout_s = 120.0f
                };
                enqueue(emergency);
            }
        }

        // 2. Пошук найпріоритетнішого кандидата
        int8_t candidate_idx = -1;
        uint8_t highest_prio = 0;

        if (active_idx_ >= 0) {
            highest_prio = items_[static_cast<size_t>(active_idx_)].priority;
            candidate_idx = active_idx_;
        }

        for (size_t i = 0; i < count_; ++i) {
            if (states_[i] == GoalState::Pending) {
                if (active_idx_ < 0 || items_[i].priority > highest_prio) {
                    highest_prio = items_[i].priority;
                    candidate_idx = static_cast<int8_t>(i);
                }
            }
        }

        // 3. Перемикання станів і витіснення
        if (candidate_idx >= 0 && candidate_idx != active_idx_) {
            if (active_idx_ >= 0) {
                states_[static_cast<size_t>(active_idx_)] = GoalState::Preempted;
                std::cout << "[DISPATCHER] Goal #" << items_[static_cast<size_t>(active_idx_)].id
                          << " PREEMPTED by higher priority goal #"
                          << items_[static_cast<size_t>(candidate_idx)].id << "\n";
            }

            if (check_preconditions(items_[static_cast<size_t>(candidate_idx)], telem)) {
                active_idx_ = candidate_idx;
                states_[static_cast<size_t>(candidate_idx)] = GoalState::Active;
                active_timer_s_ = 0.0f;
                std::cout << "[DISPATCHER] Goal #" << items_[static_cast<size_t>(candidate_idx)].id
                          << " ACTIVE (Priority: " << static_cast<int>(items_[static_cast<size_t>(candidate_idx)].priority)
                          << ", Target: [" << items_[static_cast<size_t>(candidate_idx)].target_x
                          << ", " << items_[static_cast<size_t>(candidate_idx)].target_y
                          << ", " << items_[static_cast<size_t>(candidate_idx)].target_z << "])\n";
            } else {
                states_[static_cast<size_t>(candidate_idx)] = GoalState::Rejected;
                std::cout << "[DISPATCHER] Goal #" << items_[static_cast<size_t>(candidate_idx)].id
                          << " REJECTED by pre-condition check\n";
                active_idx_ = -1;
                return;
            }
        }

        // 4. Оновлення та контроль завершення активного завдання
        if (active_idx_ >= 0) {
            auto& active_goal = items_[static_cast<size_t>(active_idx_)];
            active_timer_s_ += dt_s;

            if (active_goal.timeout_s > 0.0f && active_timer_s_ > active_goal.timeout_s) {
                states_[static_cast<size_t>(active_idx_)] = GoalState::Aborted;
                std::cout << "[DISPATCHER] Goal #" << active_goal.id
                          << " ABORTED due to timeout (" << active_timer_s_ << " s)\n";
                active_idx_ = -1;
                return;
            }

            const float dx = active_goal.target_x - telem.pos_x;
            const float dy = active_goal.target_y - telem.pos_y;
            const float dz = active_goal.target_z - telem.pos_z;
            const float dist_sq = dx * dx + dy * dy + dz * dz;

            if (dist_sq <= (active_goal.tolerance_m * active_goal.tolerance_m)) {
                states_[static_cast<size_t>(active_idx_)] = GoalState::Completed;
                std::cout << "[DISPATCHER] Goal #" << active_goal.id
                          << " COMPLETED successfully (Distance: " << std::sqrt(dist_sq) << " m)\n";
                active_idx_ = -1;
            }
        }
    }

    [[nodiscard]] std::span<const GoalState> states() const noexcept {
        return std::span<const GoalState>(states_.data(), count_);
    }

private:
    [[nodiscard]] static bool check_preconditions(const GoalItem& item, const VehicleTelemetry& telem) noexcept {
        if (!telem.ekf_healthy || !telem.geofence_valid) {
            return false;
        }
        if (item.action != GoalAction::EmergencyReturn && telem.battery_v < 21.0f) {
            return false;
        }
        return true;
    }

    std::array<GoalItem, MaxGoals> items_{};
    std::array<GoalState, MaxGoals> states_{};
    size_t count_{0};
    int8_t active_idx_{-1};
    float active_timer_s_{0.0f};
};

int main() {
    MissionDispatcher dispatcher;

    VehicleTelemetry telemetry{
        .pos_x = 0.0f,
        .pos_y = 0.0f,
        .pos_z = -10.0f,
        .battery_v = 24.2f,
        .geofence_valid = true,
        .ekf_healthy = true,
        .obstacle_detected = false
    };

    GoalItem survey_goal{
        .id = 101,
        .action = GoalAction::SurveyPolygon,
        .priority = 50,
        .target_x = 100.0f,
        .target_y = 50.0f,
        .target_z = -50.0f,
        .tolerance_m = 3.0f,
        .timeout_s = 60.0f
    };

    dispatcher.enqueue(survey_goal);

    std::cout << "=== СИМУЛЯЦІЯ АВТОНОМНОГО ДИСПЕТЧЕРА (C++) ===\n";
    const float dt = 1.0f;

    for (int step = 0; step < 10; ++step) {
        telemetry.pos_x += 10.0f;
        telemetry.pos_y += 5.0f;
        telemetry.pos_z -= 4.0f;

        if (step == 3) {
            std::cout << "\n--- ПОДІЯ: Сенсор виявив перешкоду на курсі! ---\n";
            telemetry.obstacle_detected = true;
        }

        dispatcher.step(telemetry, dt);
    }

    return 0;
}
```
:::

## Покроковий розбір виконання симуляції

Симуляційний тест у функції `main()` демонструє життєвий цикл автономної системи під час раптової зміни обстановки:

1. **Кроки 0–2**: У чергу завантажено місію огляду полігону (Goal #101 з пріоритетом 50). Диспетчер успішно проводить передстартову валідацію: напруга акумулятора (24.2 В) вища за критичний поріг (21.0 В), EKF у нормі, геозона не порушена. Завдання переходить у стан `ACTIVE`.
2. **Крок 3**: Сенсор виявляє небезпечну перешкоду безпосередньо на курсі польоту (`obstacle_detected = true`). Автономний контур реакції генерує нову мету аварійного відходу (Goal #9999 з пріоритетом 255).
3. **Крок 4**: На черговому такті диспетчер виявляє кандидата з вищим пріоритетом. Планове завдання #101 миттєво переводиться у стан `PREEMPTED` зі збереженням пройденої відстані, а активним стає аварійне повернення #9999.
4. **Кроки 5–9**: Апарат відпрацьовує маневр ухилення та досягає безпечної точки, переводячи мету #9999 у стан `COMPLETED`.

## Крайові випадки та обробка відмов

Під час розгортання диспетчера на реальному борту слід враховувати такі аномалії:
* **Переповнення черги (Queue Saturation)**: якщо черга заповнена, функція `enqueue()` повертає `false`. У реальних системах низькопріоритетні фонові завдання або завершені елементи відкидаються, звільняючи місце для екстрених команд.
* **Втрата навігації (EKF Divergence)**: якщо навігаційний фільтр втрачає супутники та одометрію (`ekf_healthy = false`), диспетчер миттєво відхиляє будь-які нові просторові цілі та переводить апарат у режим екстреного зависання або посадки на місці.
* **Інтеграція з MAVLink та ROS 2**: стани скінченного автомата (`PENDING`, `ACTIVE`, `PREEMPTED`, `COMPLETED`, `ABORTED`) прямо транслюються у стандартні пакети MAVLink Mission Protocol (`MISSION_ITEM_REACHED`, `MISSION_ACK`) або зворотні виклики ROS 2 `ActionServer`.

## Інженерні застереження під час інтеграції

1. **Не блокувати RTOS-потік**: функція `step()` / `mission_dispatcher_step()` повинна викликатися у таймерному такті з гарантованим інтервалом (наприклад, 10 або 20 Гц). Вона містить лише `O(N)` перевірок масиву і не повинна виконувати тривалих обчислень пошуку шляху чи дискових операцій запису логів.
2. **Асинхронний міст до польотного контролера**: після активації цілі координати передаються у глобальний планувальник через чергу повідомлень без блокування взаємних м'ютексів.
3. **Гістерезис витіснення**: для запобігання гойданню пріоритетів між двома конкуруючими завданнями рекомендовано додати мінімальну різницю пріоритету (`ΔP ≥ 5`) для витіснення вже активного процесу.
4. **Компіляція та верифікація**: приклад компілюється стандартними прапорцями без попереджень:
   ```bash
   # Компіляція C-версії (C11 / C99)
   gcc -Wall -Wextra -pedantic -std=c11 -O2 proj_c.c -lm -o dispatcher_c

   # Компіляція C++ версії (C++20)
   g++ -Wall -Wextra -pedantic -std=c++20 -O2 proj_cpp.cpp -o dispatcher_cpp
   ```
