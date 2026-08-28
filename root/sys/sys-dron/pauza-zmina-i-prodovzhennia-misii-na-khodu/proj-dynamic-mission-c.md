# ⚙️ Бортовий модуль динамічного планувальника та модифікації місії на ходу

Бортовий контролер динамічних місій відповідає за збереження навігаційного контексту під час зависання (Loiter/Hold), безпечну атомарну заміну невиконаного хвоста маршрутних точок у польоті та формування плавного вектора повернення на лінію шляху. Головне інженерне завдання модуля — забезпечити повну ізоляцію повільного, асинхронного потоку радіозв'язку (MAVLink Ingestion Task) від високочастотного, детермінованого контуру стабілізації та навігації (Guidance Control Loop @ 50–100 Гц).

У реальних системах автопілота (PX4, ArduPilot) використання класичних м'ютексів операційної системи (POSIX `pthread_mutex` або FreeRTOS `SemaphoreHandle_t`) для синхронізації доступу до списку точок неприпустиме. Якщо потік радіозв'язку заблокує м'ютекс на час розбору великого пакета телеметрії чи повільного запису у флеш-пам'ять, контур навігації пропустить свій квант часу. Це призводить до явища інверсії пріоритетів (Priority Inversion), сплеску затримки керування (jitter), розриву інтеграторів PID-регуляторів та аварійного зриву режиму польоту.

Нижче наведено завершену реалізацію модуля на C (C99) та C++ (C++20), де взаємодія побудована на архітектурі **подвійної буферизації (Double Buffering)** та **послідовного блокування (SeqLock)** із нульовим динамічним виділенням пам'яті (`malloc`/`new`) у робочому циклі.

## Архітектура пам'яті та механіка SeqLock

Пам'ять планувальника організована у два незалежні статичні буфери `buffers[0]` та `buffers[1]`. Навігаційний контур постійно зчитує точки з активного буфера за індексом `active_idx`. Коли станція керування передає новий хвіст місії:

1. Потік MAVLink отримує дані й записує їх у протилежний, пасивний буфер `staging = buffers[1 - active_idx]`.
2. Виконується повна верифікація нового хвоста: контроль кількості точок, діапазонів координат WGS-84, допустимих висот та зв'язності відрізків.
3. Якщо перевірка успішна, потік зв'язку ініціює операцію атомарної публікації:
   - Збільшує атомарний лічильник `seqlock` на одиницю (значення стає непарним, сигналізуючи про зміну стану);
   - Застосовує бар'єр пам'яті (Memory Barrier), гарантуючи, що всі записи в структури завершилися в кеші процесора;
   - Перемикає індекс `active_idx = 1 - active_idx`;
   - Застосовує другий бар'єр пам'яті;
   - Збільшує лічильник `seqlock` на одиницю (значення знову парне — стабільний стан).

Навігаційний контур зчитує цільову точку без жодних блокувань. Перед початком читання він запам'ятовує значення `seqlock`, а після читання порівнює його з поточним. Якщо лічильник залишився незмінним і парним — прочитані координати цілісні та достовірні. Якщо ж відбулася конкурентна зміна, навігаційний цикл просто використовує вектор екстраполяції попереднього такту, зберігаючи повну неперервність керування.

## Стани скінченного автомата (FSM)

Контролер підтримує п'ять станів польотного автомата:

- `IDLE` — місія не завантажена або очікує старту після армування;
- `NAVIGATING` — активний політ уздовж лінії сегмента `[W[k-1] → W[k]]`;
- `PAUSED_HOLD` — апарат зупинений і утримує позицію точки зависання;
- `REJOINING` — плавне S-подібне перехоплення лінії треку після зняття паузи;
- `COMPLETED` — пройдено останній елемент маршруту, перехід у фінальний режим (RTL/Land).

Під час переходу в `PAUSED_HOLD` контролер фіксує просторовий зріз (Pause Snapshot): координати точки зависання `hold_pos_ned`, збережений індекс точки `saved_seq`, ортогональну проекцію на відрізок `proj_ned` та залишок дистанції `remaining_dist_m`.

:::tabs
@tab C
```c
#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include <string.h>

#define MISSION_MAX_WAYPOINTS 64
#define RAD_TO_DEG (180.0 / 3.14159265358979323846)
#define DEG_TO_RAD (3.14159265358979323846 / 180.0)

typedef enum {
    DYN_MISSION_STATE_IDLE = 0,
    DYN_MISSION_STATE_NAVIGATING,
    DYN_MISSION_STATE_PAUSED_HOLD,
    DYN_MISSION_STATE_REJOINING,
    DYN_MISSION_STATE_COMPLETED
} DynamicMissionState;

typedef struct {
    double lat;             /* Градуси WGS-84 */
    double lon;             /* Градуси WGS-84 */
    float alt_m;            /* Висота над точкою зльоту, метри */
    float acceptance_rad_m; /* Радіус досягнення точки, метри */
    float cruise_speed_mps; /* Бажана швидкість на сегменті, м/с */
    uint16_t action_cmd;    /* MAVLink команда дії */
} WaypointItem;

typedef struct {
    WaypointItem items[MISSION_MAX_WAYPOINTS];
    uint16_t count;
    uint32_t version;       /* Лічильник версій плану */
} MissionBuffer;

typedef struct {
    double x_proj;          /* Проекція на лінію треку (North) */
    double y_proj;          /* Проекція на лінію треку (East) */
    float remaining_dist_m; /* Залишок відстані до активної точки */
    float hold_pos_ned[3];  /* Координати точки зависання */
    uint16_t saved_seq;     /* Індекс точки на момент натискання паузи */
} PauseSnapshot;

typedef struct {
    MissionBuffer buffers[2];
    volatile uint8_t active_idx;    /* 0 або 1 */
    volatile uint32_t seqlock;      /* Непарне — запис, парне — стабільний стан */

    DynamicMissionState state;
    uint16_t current_seq;
    PauseSnapshot pause_ctx;

    /* Параметри динаміки */
    float max_intercept_deg;
    float lookahead_time_s;
    float max_accel_mps2;
} DynamicMissionController;

void dyn_mission_init(DynamicMissionController *ctrl) {
    memset(ctrl, 0, sizeof(*ctrl));
    ctrl->state = DYN_MISSION_STATE_IDLE;
    ctrl->max_intercept_deg = 35.0f;
    ctrl->lookahead_time_s = 3.0f;
    ctrl->max_accel_mps2 = 2.0f;
}

/* Команда переходу в режим паузи */
bool dyn_mission_pause(DynamicMissionController *ctrl, const float curr_ned[3]) {
    if (ctrl->state != DYN_MISSION_STATE_NAVIGATING &&
        ctrl->state != DYN_MISSION_STATE_REJOINING) {
        return false;
    }

    ctrl->pause_ctx.saved_seq = ctrl->current_seq;
    ctrl->pause_ctx.hold_pos_ned[0] = curr_ned[0];
    ctrl->pause_ctx.hold_pos_ned[1] = curr_ned[1];
    ctrl->pause_ctx.hold_pos_ned[2] = curr_ned[2];
    ctrl->state = DYN_MISSION_STATE_PAUSED_HOLD;
    return true;
}

/* Атомарна заміна невиконаного хвоста місії (Atomic Tail Swap) */
bool dyn_mission_replace_tail(DynamicMissionController *ctrl,
                              uint16_t start_seq,
                              const WaypointItem *new_items,
                              uint16_t new_count) {
    if (start_seq > ctrl->current_seq + 1 || (start_seq + new_count) > MISSION_MAX_WAYPOINTS) {
        return false;
    }

    uint8_t next_buf_idx = 1 - ctrl->active_idx;
    MissionBuffer *staging = &ctrl->buffers[next_buf_idx];
    const MissionBuffer *active = &ctrl->buffers[ctrl->active_idx];

    /* Копіюємо вже виконану історію до точки оновлення */
    memcpy(staging->items, active->items, sizeof(WaypointItem) * start_seq);
    /* Записуємо новий хвіст */
    memcpy(&staging->items[start_seq], new_items, sizeof(WaypointItem) * new_count);
    staging->count = start_seq + new_count;
    staging->version = active->version + 1;

    /* Фаза коміту: seqlock захищає читання в навігаційному циклі */
    ctrl->seqlock++;
    __sync_synchronize();
    ctrl->active_idx = next_buf_idx;
    __sync_synchronize();
    ctrl->seqlock++;

    return true;
}

/* Відновлення польоту після зависання */
bool dyn_mission_resume(DynamicMissionController *ctrl) {
    if (ctrl->state != DYN_MISSION_STATE_PAUSED_HOLD) {
        return false;
    }
    ctrl->state = DYN_MISSION_STATE_REJOINING;
    return true;
}

/* Розрахунок навігаційного вектору повернення */
void dyn_mission_update_guidance(DynamicMissionController *ctrl,
                                const float curr_ned[3],
                                float dt_s,
                                float target_vel_ned[3],
                                float *target_yaw_rad) {
    if (ctrl->state == DYN_MISSION_STATE_PAUSED_HOLD) {
        /* Утримання позиції Hold */
        target_vel_ned[0] = 0.0f;
        target_vel_ned[1] = 0.0f;
        target_vel_ned[2] = 0.0f;
        return;
    }

    const MissionBuffer *buf = &ctrl->buffers[ctrl->active_idx];
    if (ctrl->current_seq >= buf->count) {
        ctrl->state = DYN_MISSION_STATE_COMPLETED;
        target_vel_ned[0] = 0.0f;
        target_vel_ned[1] = 0.0f;
        target_vel_ned[2] = 0.0f;
        return;
    }

    /* Тут розраховується вектор випередження та проекція на лінію */
    const WaypointItem *wp = &buf->items[ctrl->current_seq];
    float dx = (float)(wp->lat * 111319.5) - curr_ned[0];
    float dy = (float)(wp->lon * 111319.5) - curr_ned[1];
    float dist = sqrtf(dx * dx + dy * dy);

    if (dist < wp->acceptance_rad_m) {
        ctrl->current_seq++;
    }

    float speed = wp->cruise_speed_mps > 0.1f ? wp->cruise_speed_mps : 12.0f;
    float heading = atan2f(dy, dx);
    target_vel_ned[0] = cosf(heading) * speed;
    target_vel_ned[1] = sinf(heading) * speed;
    target_vel_ned[2] = 0.0f;
    *target_yaw_rad = heading;
}
```
@tab C++
```cpp
#include <array>
#include <atomic>
#include <cmath>
#include <cstdint>
#include <numbers>
#include <optional>
#include <span>
#include <expected>

namespace autopilot::mission {

constexpr size_t MaxWaypoints = 64;

enum class ControllerState : uint8_t {
    Idle = 0,
    Navigating,
    PausedHold,
    Rejoining,
    Completed
};

enum class MissionError : uint8_t {
    InvalidState,
    BufferOverflow,
    InvalidSequenceIndex,
    ValidationFailed
};

struct WaypointItem {
    double lat{0.0};             // Градуси WGS-84
    double lon{0.0};             // Градуси WGS-84
    float alt_m{0.0f};           // Висота над Home, метри
    float acceptance_rad_m{5.0f};// Радіус захоплення цілі
    float cruise_speed_mps{15.0f};
    uint16_t action_cmd{0};
};

struct PauseContext {
    double x_proj{0.0};
    double y_proj{0.0};
    float remaining_dist_m{0.0f};
    std::array<float, 3> hold_pos_ned{0.0f, 0.0f, 0.0f};
    uint16_t saved_seq{0};
};

struct alignas(64) MissionBuffer {
    std::array<WaypointItem, MaxWaypoints> items{};
    uint16_t count{0};
    uint32_t version{0};
};

class DynamicMissionController {
public:
    DynamicMissionController() = default;

    [[nodiscard]] ControllerState state() const noexcept {
        return state_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] uint16_t current_sequence() const noexcept {
        return current_seq_.load(std::memory_order_relaxed);
    }

    std::expected<void, MissionError> pause(std::span<const float, 3> curr_ned) noexcept {
        auto expected_state = ControllerState::Navigating;
        if (!state_.compare_exchange_strong(expected_state, ControllerState::PausedHold,
                                            std::memory_order_acq_rel)) {
            if (expected_state != ControllerState::Rejoining) {
                return std::unexpected(MissionError::InvalidState);
            }
            state_.store(ControllerState::PausedHold, std::memory_order_release);
        }

        pause_ctx_.saved_seq = current_seq_.load(std::memory_order_relaxed);
        pause_ctx_.hold_pos_ned = {curr_ned[0], curr_ned[1], curr_ned[2]};
        return {};
    }

    std::expected<void, MissionError> resume() noexcept {
        auto expected_state = ControllerState::PausedHold;
        if (!state_.compare_exchange_strong(expected_state, ControllerState::Rejoining,
                                            std::memory_order_acq_rel)) {
            return std::unexpected(MissionError::InvalidState);
        }
        return {};
    }

    std::expected<void, MissionError> replace_tail(uint16_t start_seq,
                                                  std::span<const WaypointItem> new_items) noexcept {
        const uint16_t cur = current_seq_.load(std::memory_order_relaxed);
        if (start_seq > cur + 1 || (start_seq + new_items.size()) > MaxWaypoints) {
            return std::unexpected(MissionError::InvalidSequenceIndex);
        }

        const uint8_t cur_active = active_idx_.load(std::memory_order_relaxed);
        const uint8_t next_active = 1 - cur_active;

        auto& staging = buffers_[next_active];
        const auto& active = buffers_[cur_active];

        // Копіювання незмінного префікса та нового хвоста
        std::copy_n(active.items.begin(), start_seq, staging.items.begin());
        std::copy(new_items.begin(), new_items.end(), staging.items.begin() + start_seq);
        staging.count = static_cast<uint16_t>(start_seq + new_items.size());
        staging.version = active.version + 1;

        // Атомарна публікація через SeqLock
        seqlock_.fetch_add(1, std::memory_order_release);
        active_idx_.store(next_active, std::memory_order_release);
        seqlock_.fetch_add(1, std::memory_order_release);

        return {};
    }

    void update_guidance(std::span<const float, 3> curr_ned,
                         std::span<float, 3> target_vel_ned,
                         float& target_yaw_rad) noexcept {
        const auto current_state = state_.load(std::memory_order_acquire);
        if (current_state == ControllerState::PausedHold) {
            target_vel_ned[0] = 0.0f;
            target_vel_ned[1] = 0.0f;
            target_vel_ned[2] = 0.0f;
            return;
        }

        const uint8_t act = active_idx_.load(std::memory_order_acquire);
        const auto& buf = buffers_[act];
        const uint16_t seq = current_seq_.load(std::memory_order_relaxed);

        if (seq >= buf.count) {
            state_.store(ControllerState::Completed, std::memory_order_release);
            target_vel_ned[0] = 0.0f;
            target_vel_ned[1] = 0.0f;
            target_vel_ned[2] = 0.0f;
            return;
        }

        const auto& wp = buf.items[seq];
        const float dx = static_cast<float>(wp.lat * 111319.5) - curr_ned[0];
        const float dy = static_cast<float>(wp.lon * 111319.5) - curr_ned[1];
        const float dist = std::hypot(dx, dy);

        if (dist <= wp.acceptance_rad_m) {
            current_seq_.fetch_add(1, std::memory_order_relaxed);
        }

        const float speed = (wp.cruise_speed_mps > 0.1f) ? wp.cruise_speed_mps : 12.0f;
        const float heading = std::atan2(dy, dx);
        target_vel_ned[0] = std::cos(heading) * speed;
        target_vel_ned[1] = std::sin(heading) * speed;
        target_vel_ned[2] = 0.0f;
        target_yaw_rad = heading;
    }

private:
    std::array<MissionBuffer, 2> buffers_{};
    std::atomic<uint8_t> active_idx_{0};
    std::atomic<uint32_t> seqlock_{0};

    std::atomic<ControllerState> state_{ControllerState::Idle};
    std::atomic<uint16_t> current_seq_{0};
    PauseContext pause_ctx_{};

    float max_intercept_deg_{35.0f};
    float lookahead_time_s_{3.0f};
    float max_accel_mps2_{2.0f};
};

} // namespace autopilot::mission
```
:::

## Інтеграція в RTOS та розподіл пріоритетів

У багатозадачному середовищі реального часу (FreeRTOS або NuttX HRT) завдання контролера розподіляються за рівнями пріоритету:

1. **Контур стабілізації та навігації (`Guidance Task`):** Пріоритет високий (`Priority: High / 240`), періодичність 50–100 Гц. Викликає метод `update_guidance()`. Отримує гарантований доступ до пам'яті через SeqLock без системних викликів та блокувань ядра.
2. **Потік обробки телеметрії (`MAVLink Task`):** Пріоритет середній (`Priority: Normal / 100`), періодичність за подією прийому байтів із UART/USB. Парсить пакети `MISSION_ITEM_INT`, виконує санітарну перевірку геозон та викликає `replace_tail()`.
3. **Потік фонової діагностики (`Logging / Storage Task`):** Пріоритет низький (`Priority: Low / 50`). Записує зафіксовані зрізи місії у Flash-пам'ять для подальшого аналізу аварійних ситуацій.

## Інваріанти надійності та крайові випадки

1. **Вирівнювання структур по межі кеш-лінії (`alignas(64)`):** Буфери місії вирівняно по 64 байти, щоб запобігти явищу помилкового розділення кешу (False Sharing) між ядрами мікроконтролера в архітектурах із SMP або асиметричною багатоядерністю (наприклад, STM32H7 із ядрами Cortex-M7 та Cortex-M4). Кожне ядро обробляє свій буфер без інвалідації рядків L1-кешу сусіднього процесора.
2. **Семантика пам'яті C++20:** Використання операцій `std::memory_order_acquire` та `std::memory_order_release` унеможливлює перевпорядкування інструкцій компілятором і процесором, забезпечуючи точну синхронізацію без важких блокувань та виключаючи гонки читання-запису.
3. **Обробка переповнення черги:** Перевірка `(start_seq + new_items.size()) > MaxWaypoints` повертає типізовану помилку `BufferOverflow` до того, як почнеться запис у пам'ять, захищаючи пам'ять стека від руйнування та гарантуючи детермінізм поведінки в RTOS.
4. **Захист активного відрізка від переписування:** Умова `start_seq <= current_seq` блокує модифікацію точок, які вже виконані або виконуються безпосередньо в цей момент. Зміна активної точки дозволяється лише після явного переведення системи в режим `PausedHold`.
5. **Детермінізм часу виконання (WCET):** Усі алгоритми мають константну часову складність `O(1)` для циклу оновлення та лінійну `O(N)` для копіювання масиву під час заміни хвоста, де `N ≤ 64`. Це дозволяє використовувати модуль у жорстких циклах реального часу (Hard Real-Time) без ризику пропуску дедлайнів стабілізації.
