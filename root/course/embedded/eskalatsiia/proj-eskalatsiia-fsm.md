# Автомат ескалації та обробки таймаутів з відкатом траєкторії

У реальній бортовій системі модуль ескалації не може існувати як абстрактна концептуальна схема. Він працює безпосередньо всередині жорсткого циклу керування (типово з частотою 50–100 Гц у RTOS-задачі або суперлупі супутнього комп'ютера), взаємодіє з підсистемою локального планування траєкторій, каналом телеметрії MAVLink та аварійним контуром failsafe автопілота. Щойно планувальник виявляє просторовий тупик або нейродетектор фіксує перешкоду в зоні граничної невизначеності, борт зобов'язаний виконати низку детермінованих дій: зафіксувати свій кінематичний стан, зібрати компактний двійковий пакет запиту з готовими дискретними опціями A/B, запустити зворотний відлік динамічного таймера й у разі мовчання оператора автономно перейти до каскаду порятунку.

Нижче наведено повну робочу реалізацію скінченного автомата ескалації, підсистеми розрахунку фізичного дедлайну та кільцевого буфера просторових точок (breadcrumb trail) для відкату назад.

## Структури даних та протокол запиту

Для надійної передачі через вузькосмуговий радіолінк (наприклад, telemetry port радіомодема на швидкості 57600 бод, де корисна пропускна здатність рідко перевищує 3–4 кілобайти на секунду) структура запиту має бути строго бінарно запакованою і не перевищувати розміру одного MTU радіоканалу.

Кожен запит ідентифікується монотонним числовим лічильником `query_id`. Це запобігає класичній помилці розподілених систем — «фантомному перемиканню», коли оператор підтверджує попередній інцидент, але через затримку пакет потрапляє на борт у момент виникнення зовсім іншої нештатної ситуації. Поле `trigger_code` містить машинозчитний код причини, який дозволяє наземній станції автоматично підсвітити відповідний шар інтерфейсу (наприклад, накласти червоний контур на візуальний ROI при детекції об'єкта або показати топологію глухого кута при блокуванні costmap).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_OPTIONS_COUNT     4
#define BREADCRUMB_CAPACITY   64
#define ROI_MAX_BYTES         256

/* Коди апаратних тригерів ескалації */
typedef enum {
    ESCALATION_TRIGGER_NONE = 0,
    ESCALATION_TRIGGER_SCENE_AMBIGUITY,    /* Висока ентропія softmax / близькі класи */
    ESCALATION_TRIGGER_PATH_EXHAUSTED,     /* Усі гілки costmap заблоковані */
    ESCALATION_TRIGGER_BORDERLINE_CRITICAL,/* Критичний об'єкт у діапазоні впевненості [0.4..0.7] */
    ESCALATION_TRIGGER_ODD_EXCURSION       /* Порушення умов середовища (сонце, вітер, EKF) */
} EscalationTrigger;

/* Стан автомата ескалації */
typedef enum {
    FSM_STATE_AUTONOMOUS = 0,
    FSM_STATE_ESCALATION_REQUESTED,
    FSM_STATE_AWAITING_OPERATOR,
    FSM_STATE_APPLYING_OVERRIDE,
    FSM_STATE_FAILSAFE_HOLD,
    FSM_STATE_FAILSAFE_BACKTRACK,
    FSM_STATE_FAILSAFE_SAFE_ABORT
} EscalationState;

/* Дискретна дія, прорахована бортом */
typedef struct {
    uint8_t option_id;              /* 1: Ліворуч, 2: Праворуч, 3: Скасувати, 4: Стоп */
    char description[32];           /* Текстовий підпис для UI оператора */
    float estimated_cost_detour_m;  /* Додаткова дистанція у метрах */
    float risk_score;               /* Оцінка залишкового ризику 0.0 .. 1.0 */
} EscalationOption;

/* Пакет запиту до оператора */
typedef struct {
    uint16_t query_id;              /* Монотонний лічильник запитів */
    uint32_t timestamp_ms;          /* Бортовий час створення */
    uint16_t deadline_ms;           /* Динамічний таймаут на відповідь */
    EscalationTrigger trigger_code; /* Чому виник запит */
    float position_xyz[3];          /* Поточні координати */
    float velocity_xyz[3];          /* Поточний вектор швидкості */
    uint8_t options_count;          /* Кількість варіантів дій */
    EscalationOption options[MAX_OPTIONS_COUNT];
    uint16_t roi_size_bytes;        /* Розмір стисненого фрагмента кадру */
    uint8_t roi_jpeg_buffer[ROI_MAX_BYTES];
} EscalationQueryPacket;

/* Точка історії для реверсу траєкторії */
typedef struct {
    float x, y, z;
    float yaw;
    uint32_t timestamp_ms;
    int8_t rssi_dbm;                /* Рівень радіосигналу в цій точці */
} BreadcrumbPoint;

/* Кільцевий буфер історії руху */
typedef struct {
    BreadcrumbPoint buffer[BREADCRUMB_CAPACITY];
    uint16_t head;
    uint16_t count;
} BreadcrumbTrail;
```
```cpp
#include <cstdint>
#include <array>
#include <string_view>
#include <span>
#include <optional>
#include <chrono>

using namespace std::chrono_literals;

enum class EscalationTrigger : uint8_t {
    None = 0,
    SceneAmbiguity,         // Висока ентропія softmax / близькі класи
    PathExhausted,          // Усі гілки costmap заблоковані
    BorderlineCritical,     // Критичний об'єкт у діапазоні [0.4..0.7]
    OddExcursion            // Порушення робочого домену (вітер, EKF)
};

enum class EscalationState : uint8_t {
    Autonomous = 0,
    EscalationRequested,
    AwaitingOperator,
    ApplyingOverride,
    FailsafeHold,
    FailsafeBacktrack,
    FailsafeSafeAbort
};

struct EscalationOption {
    uint8_t option_id{0};
    std::string_view description{};
    float estimated_cost_detour_m{0.0f};
    float risk_score{0.0f};
};

struct BreadcrumbPoint {
    float x{0.0f}, y{0.0f}, z{0.0f};
    float yaw{0.0f};
    std::chrono::milliseconds timestamp{0ms};
    int8_t rssi_dbm{0};
};

class BreadcrumbTrail {
public:
    static constexpr size_t Capacity = 64;

    void push(const BreadcrumbPoint& pt) noexcept {
        buffer_[head_] = pt;
        head_ = (head_ + 1) % Capacity;
        if (count_ < Capacity) {
            count_++;
        }
    }

    [[nodiscard]] std::optional<BreadcrumbPoint> pop_reverse() noexcept {
        if (count_ == 0) {
            return std::nullopt;
        }
        head_ = (head_ == 0) ? (Capacity - 1) : (head_ - 1);
        count_--;
        return buffer_[head_];
    }

    [[nodiscard]] size_t size() const noexcept { return count_; }
    void clear() noexcept { head_ = 0; count_ = 0; }

private:
    std::array<BreadcrumbPoint, Capacity> buffer_{};
    size_t head_{0};
    size_t count_{0};
};
```
:::

Масив опцій `options` заповнюється локальним планувальником перед відправкою. Якщо планувальник знайшов можливість об'їзду ліворуч і праворуч, він генерує варіанти #1 та #2 із точними оцінками подовження шляху `estimated_cost_detour_m`. Якщо ж простір повністю заблокований, генерується лише варіант аварійної зупинки чи переходу до резервної точки місії.

## Фізичний розрахунок динамічного таймауту

Використання фіксованого таймауту (наприклад, 5 чи 10 секунд) неприпустиме для вбудованих систем: на високій швидкості 10-секундне очікування призведе до зіткнення задовго до закінчення таймера, а на нульовій швидкості призведе до передчасного зриву місії. Борт розраховує час, що залишився до точки неповернення, спираючись на фізичні закони кінематики.

Алгоритм визначає мінімальну безпечну дистанцію, яка складається з теоретичного гальмівного шляху платформи при максимальному сповільненні `max_braking_decel_mps2` та обов'язкового буфера безпеки `safety_margin_m`. Різниця між поточною відстанню до перешкоди та цією безпечною дистанцією ділиться на поточну швидкість. Від отриманого значення віднімається сумарна латентність сенсорно-комунікаційного тракту `sensor_lag_ms` (час зняття кадру, інференсу нейромережі та передачі пакету по радіо).

:::tabs
```c
/* Розрахунок дедлайну в мілісекундах */
uint32_t calculate_dynamic_deadline_ms(float distance_to_obstacle_m,
                                       float current_speed_mps,
                                       float max_braking_decel_mps2,
                                       float safety_margin_m,
                                       uint32_t sensor_lag_ms)
{
    /* Якщо апарат стоїть або швидкість мізерна — таймаут обмежується зависанням */
    if (current_speed_mps < 0.1f) {
        return 15000; /* 15 секунд на місці */
    }

    /* Гальмівний шлях: S_brake = V^2 / (2 * a) */
    float braking_distance_m = (current_speed_mps * current_speed_mps) / (2.0f * max_braking_decel_mps2);
    float total_safe_distance_m = braking_distance_m + safety_margin_m;

    /* Якщо вже ближче за гальмівний шлях із запасом — нульовий час, гальмувати негайно */
    if (distance_to_obstacle_m <= total_safe_distance_m) {
        return 0;
    }

    /* Доступна дистанція вільного руху до точки початку екстреного гальмування */
    float distance_available_m = distance_to_obstacle_m - total_safe_distance_m;
    float time_available_sec = distance_available_m / current_speed_mps;

    uint32_t time_available_ms = (uint32_t)(time_available_sec * 1000.0f);
    if (time_available_ms <= sensor_lag_ms) {
        return 0;
    }

    return time_available_ms - sensor_lag_ms;
}
```
```cpp
[[nodiscard]] constexpr std::chrono::milliseconds calculate_dynamic_deadline(
    float distance_to_obstacle_m,
    float current_speed_mps,
    float max_braking_decel_mps2,
    float safety_margin_m,
    std::chrono::milliseconds sensor_lag) noexcept
{
    if (current_speed_mps < 0.1f) {
        return 15000ms; // 15 секунд на місці у стаціонарному режимі
    }

    const float braking_distance_m = (current_speed_mps * current_speed_mps) / (2.0f * max_braking_decel_mps2);
    const float total_safe_distance_m = braking_distance_m + safety_margin_m;

    if (distance_to_obstacle_m <= total_safe_distance_m) {
        return 0ms;
    }

    const float distance_available_m = distance_to_obstacle_m - total_safe_distance_m;
    const float time_available_sec = distance_available_m / current_speed_mps;
    const auto time_available_ms = std::chrono::milliseconds(static_cast<int64_t>(time_available_sec * 1000.0f));

    if (time_available_ms <= sensor_lag) {
        return 0ms;
    }
    return time_available_ms - sensor_lag;
}
```
:::

Якщо отримана величина дедлайну дорівнює нулю або менша за апаратну затримку сенсорів, це означає, що апарат уже увійшов у зону екстреного гальмування. У цьому разі автомат відразу переходить у стан зупинки, не очікуючи на оператора.

## Логіка скінченного автомата та обробка переходів

Автомат оновлюється в кожному такті бортової петлі реального часу. Він фіксує переходи між станами, стежить за таймером очікування оператора, перевіряє цілісність радіоканалу та запускає відповідний етап аварійного каскаду.

У штатному стані `FSM_STATE_AUTONOMOUS` борт безперервно оновлює буфер історії руху `BreadcrumbTrail`. Щойно з'являється тригер ескалації, автомат переходить у стан `FSM_STATE_ESCALATION_REQUESTED`, де розраховує фізичний дедлайн і надсилає пакет. Якщо дедлайн вичерпується або втрачається потік повідомлень `HEARTBEAT` від наземної станції, автомат негайно переходить до трирівневого каскаду безпеки: спершу зупинка на місці (`FSM_STATE_FAILSAFE_HOLD`), потім відкат назад по збережених точках (`FSM_STATE_FAILSAFE_BACKTRACK`), і нарешті — повне знеструмлення або посадка (`FSM_STATE_FAILSAFE_SAFE_ABORT`).

:::tabs
```c
typedef struct {
    EscalationState state;
    EscalationTrigger active_trigger;
    uint16_t current_query_id;
    uint32_t request_started_ms;
    uint32_t dynamic_deadline_ms;
    uint8_t selected_option_id;
    BreadcrumbTrail trail;
    uint32_t last_breadcrumb_time_ms;
} EscalationManager;

void escalation_manager_init(EscalationManager* mgr) {
    memset(mgr, 0, sizeof(EscalationManager));
    mgr->state = FSM_STATE_AUTONOMOUS;
}

/* Періодичний запис пройденої траєкторії для можливого відкату */
void update_breadcrumb_trail(EscalationManager* mgr, float x, float y, float z, float yaw, int8_t rssi, uint32_t now_ms) {
    if (now_ms - mgr->last_breadcrumb_time_ms >= 1000) { /* 1 раз на секунду */
        mgr->last_breadcrumb_time_ms = now_ms;
        BreadcrumbPoint pt = { x, y, z, yaw, now_ms, rssi };
        mgr->trail.buffer[mgr->trail.head] = pt;
        mgr->trail.head = (mgr->trail.head + 1) % BREADCRUMB_CAPACITY;
        if (mgr->trail.count < BREADCRUMB_CAPACITY) {
            mgr->trail.count++;
        }
    }
}

/* Головний такт автомата */
void escalation_manager_tick(EscalationManager* mgr,
                             EscalationTrigger current_trigger,
                             float dist_to_obstacle_m,
                             float speed_mps,
                             bool radio_link_alive,
                             uint32_t now_ms)
{
    switch (mgr->state) {
        case FSM_STATE_AUTONOMOUS:
            if (current_trigger != ESCALATION_TRIGGER_NONE) {
                mgr->active_trigger = current_trigger;
                mgr->current_query_id++;
                mgr->request_started_ms = now_ms;
                mgr->dynamic_deadline_ms = calculate_dynamic_deadline_ms(
                    dist_to_obstacle_m, speed_mps, 2.0f, 4.0f, 200);
                
                mgr->state = (mgr->dynamic_deadline_ms == 0) 
                             ? FSM_STATE_FAILSAFE_HOLD 
                             : FSM_STATE_ESCALATION_REQUESTED;
            }
            break;

        case FSM_STATE_ESCALATION_REQUESTED:
            /* Тут формується та відправляється пакет по MAVLink */
            mgr->state = FSM_STATE_AWAITING_OPERATOR;
            break;

        case FSM_STATE_AWAITING_OPERATOR: {
            uint32_t elapsed = now_ms - mgr->request_started_ms;
            
            /* Перевірка обриву зв'язку або вичерпання дедлайну */
            if (!radio_link_alive || elapsed >= mgr->dynamic_deadline_ms) {
                mgr->state = FSM_STATE_FAILSAFE_HOLD;
                break;
            }
            break;
        }

        case FSM_STATE_APPLYING_OVERRIDE:
            /* Виконання підтвердженої оператором опції; по завершенню повернення */
            mgr->state = FSM_STATE_AUTONOMOUS;
            mgr->active_trigger = ESCALATION_TRIGGER_NONE;
            break;

        case FSM_STATE_FAILSAFE_HOLD:
            /* Апарат зупинився. Якщо зв'язок не відновлено протягом 5 с — відкат назад */
            if (now_ms - mgr->request_started_ms > (mgr->dynamic_deadline_ms + 5000)) {
                mgr->state = FSM_STATE_FAILSAFE_BACKTRACK;
            }
            break;

        case FSM_STATE_FAILSAFE_BACKTRACK:
            /* Реверс за точками з буфера. Якщо буфер вичерпано — контрольована посадка */
            if (mgr->trail.count == 0) {
                mgr->state = FSM_STATE_FAILSAFE_SAFE_ABORT;
            }
            break;

        case FSM_STATE_FAILSAFE_SAFE_ABORT:
            /* Аварійна зупинка, вимкнення моторів, запис у NVRAM */
            break;
    }
}

/* Обробка відповіді оператора від наземної станції */
bool escalation_manager_handle_response(EscalationManager* mgr, uint16_t query_id, uint8_t option_id, uint32_t now_ms) {
    if (mgr->state != FSM_STATE_AWAITING_OPERATOR) {
        return false; /* Запізніла відповідь відкинута */
    }
    if (query_id != mgr->current_query_id) {
        return false; /* Не той ID запиту */
    }
    if (now_ms - mgr->request_started_ms > mgr->dynamic_deadline_ms) {
        return false; /* Таймаут минув */
    }

    mgr->selected_option_id = option_id;
    mgr->state = FSM_STATE_APPLYING_OVERRIDE;
    return true;
}
```
```cpp
class EscalationManager {
public:
    EscalationManager() = default;

    void update_trail(float x, float y, float z, float yaw, int8_t rssi, std::chrono::milliseconds now) noexcept {
        if (now - last_breadcrumb_time_ >= 1000ms) {
            last_breadcrumb_time_ = now;
            trail_.push({x, y, z, yaw, now, rssi});
        }
    }

    void tick(EscalationTrigger current_trigger,
              float dist_to_obstacle_m,
              float speed_mps,
              bool radio_link_alive,
              std::chrono::milliseconds now) noexcept
    {
        switch (state_) {
            case EscalationState::Autonomous:
                if (current_trigger != EscalationTrigger::None) {
                    active_trigger_ = current_trigger;
                    current_query_id_++;
                    request_started_ = now;
                    dynamic_deadline_ = calculate_dynamic_deadline(
                        dist_to_obstacle_m, speed_mps, 2.0f, 4.0f, 200ms);
                    
                    state_ = (dynamic_deadline_ == 0ms)
                             ? EscalationState::FailsafeHold
                             : EscalationState::EscalationRequested;
                }
                break;

            case EscalationState::EscalationRequested:
                state_ = EscalationState::AwaitingOperator;
                break;

            case EscalationState::AwaitingOperator: {
                const auto elapsed = now - request_started_;
                if (!radio_link_alive || elapsed >= dynamic_deadline_) {
                    state_ = EscalationState::FailsafeHold;
                }
                break;
            }

            case EscalationState::ApplyingOverride:
                state_ = EscalationState::Autonomous;
                active_trigger_ = EscalationTrigger::None;
                break;

            case EscalationState::FailsafeHold:
                if (now - request_started_ > (dynamic_deadline_ + 5000ms)) {
                    state_ = EscalationState::FailsafeBacktrack;
                }
                break;

            case EscalationState::FailsafeBacktrack:
                if (trail_.size() == 0) {
                    state_ = EscalationState::FailsafeSafeAbort;
                }
                break;

            case EscalationState::FailsafeSafeAbort:
                break;
        }
    }

    [[nodiscard]] bool handle_response(uint16_t query_id, uint8_t option_id, std::chrono::milliseconds now) noexcept {
        if (state_ != EscalationState::AwaitingOperator) {
            return false;
        }
        if (query_id != current_query_id_) {
            return false;
        }
        if (now - request_started_ > dynamic_deadline_) {
            return false;
        }

        selected_option_id_ = option_id;
        state_ = EscalationState::ApplyingOverride;
        return true;
    }

    [[nodiscard]] EscalationState state() const noexcept { return state_; }
    [[nodiscard]] uint16_t query_id() const noexcept { return current_query_id_; }
    [[nodiscard]] std::chrono::milliseconds deadline() const noexcept { return dynamic_deadline_; }

private:
    EscalationState state_{EscalationState::Autonomous};
    EscalationTrigger active_trigger_{EscalationTrigger::None};
    uint16_t current_query_id_{0};
    std::chrono::milliseconds request_started_{0ms};
    std::chrono::milliseconds dynamic_deadline_{0ms};
    uint8_t selected_option_id_{0};
    BreadcrumbTrail trail_{};
    std::chrono::milliseconds last_breadcrumb_time_{0ms};
};
```
:::

Функція `escalation_manager_handle_response` містить потрійну лінію захисту: перевірку стану автомата, перевірку збігу `query_id` та перевірку монотонного таймера. Будь-який пакет, що не пройшов хоча б один бар'єр, негайно відкидається без впливу на виконавчі органи.

## Інженерні пастки при роботі з таймаутами ескалації

1. **Запізнілі пакети від станції.** Оператор може натиснути кнопку «Об'їзд праворуч» на 100 мс пізніше вичерпання дедлайну, коли борт уже увійшов у режим екстреного гальмування. Якщо борт прийме таку команду без перевірки часової мітки й поточного стану автомата, відбудеться небезпечний різкий ривок приводів у момент, коли кінематичні умови вже змінилися. Завжди відкидайте відповіді, якщо стан автомата змінився з `AWAITING_OPERATOR` на будь-який інший.
2. **Переповнення 32-бітного лічильника часу.** Використання беззнакового віднімання `now_ms - request_started_ms` є обов'язковим для захисту від переповнення таймера `millis()` (переповнюється раз на 49.7 днів). Пряме порівняння `now_ms >= deadline_target_ms` зламається на межі переповнення.
3. **Засмічення буфера точок під час тривалого зависання.** Якщо апарат завис на місці в очікуванні відповіді, запис точок за часом (кожні 1000 мс) витіснить із кільцевого буфера реальну траєкторію підльоту однаковими координатами зависання. Запис у `BreadcrumbTrail` має відбуватися лише тоді, коли апарат змістився у просторі більше ніж на порогову відстань (наприклад, дистанція зсуву не менше 1.5 м від останньої збереженої точки).
4. **Конфлікт пріоритетів між локальним failsafe та ручним пультом.** Якщо під час ескалації оператор одночасно натискає кнопку в інтерфейсі GCS і перехоплює керування аналоговим джойстиком RC, бортовий арбітр команд повинен мати однозначну матрицю пріоритетів: апаратний перемикач режимів на пульті RC завжди має найвищий пріоритет і безумовно скидає автомат ескалації в базовий стан ручного пілотування.
5. **Дрейф локалізації під час бектрекінгу.** Рух назад за раніше записаними точками спирається на локальну одометрію. Якщо під час відкату вимикається GNSS або втрачається оптичний потік, накопичена помилка інтегрування може змістити реверсну траєкторію на кілька метрів убік. Тому під час бектрекінгу радіус безпечної зони довкола точок збільшують удвічі порівняно зі штатним рухом уперед.
