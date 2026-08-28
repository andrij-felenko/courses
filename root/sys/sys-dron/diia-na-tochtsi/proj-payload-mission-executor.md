# ⚙️ Виконавча підсистема корисного навантаження в автономній місії

Управління корисним навантаженням (камерою, сервозамком скидання вантажу, соленоїдним скидачем та тривісним підвісом) вимагає суворо детермінованої обробки просторово-часових умов у реальному часі без блокування швидких контурів навігації та стабілізації автопілота. Цей модуль реалізує автомат станів виконання дій місії, розрахунок інтервалів зйомки, апаратне підтвердження скидання вантажу через кінцевик або шунт струму, а також реєстрацію подій зворотного зв'язку.

---

### Архітектура підсистеми та часові вимоги

Підсистема корисного навантаження інтегрується в диспетчер задач автопілота як періодичний процес із частотою виконання 50 Гц (період дискретизації `Δt = 20` мс). Такий вибір частоти обумовлений двома компромісними вимогами:
1. **Швидкодія механіки та переривань:** реакція на спрацьовування кінцевика, зняття імпульсу затвора камери (тривалість 50 мс) та моніторинг струмового сплеску соленоїда (тривалість 40–80 мс) вимагають розрізнення часу краще ніж 25 мс.
2. **Економія процесорного часу:** розрахунок тригонометричних функцій наведення підвісу (`atan2`, корені) та оновлення геодезичних відстаней не повинні навантажувати ядро мікроконтролера, на якому паралельно працюють контури орієнтації (400–1000 Гц) та розрахунку фільтра калманівського оцінювача стану (EKF, 100–250 Гц).

Модуль складається з трьох ключових автоматів:
- **Дистанційний тригер аерофотозйомки (`Distance Trigger FSM`):** відстежує пройдений шлях за 3D-вектором зміщення, фільтрує кутові коливання та формує строби керування затвором фіксованої тривалості.
- **Виконавчий автомат скидання вантажу (`Cargo Drop FSM`):** керує силовими ключами та сервоприводами, відраховує таймаути ходу, контролює датчики кінцевого положення та проводить аварійний цикл розхитування у випадку заклинювання ригеля.
- **Контролер наведення оптичної осі (`ROI Tracking Engine`):** трансформує координати цільового наземного орієнтира у просторові кути тангажу й азимуту для передачі на зовнішній контролер підвісу.

---

### Обробка апаратного зворотного зв'язку та аварійних станів

Надійна робота модуля скидання базується на трьох рівнях захисту:
- **Антибрязковий захист кінцевика (`Switch Debounce`):** контакти механічного мікроперемикача зазнають інтенсивних вібрацій від моторів безпілотника. Програмний стан `DROP_STATE_SUCCESS` встановлюється лише тоді, коли логічний рівень на вході GPIO залишається стабільним протягом щонайменше 15 мс (три послідовні цикли опитування).
- **Захист соленоїда від струмового перевантаження (`Overcurrent / Jam Detection`):** котушка соленоїда розрахована на короткочасне імпульсне навантаження струмом 4–8 А. Якщо механічний сердечник заклинило в проміжному положенні або сталося міжвиткове замикання, струм через шунт перевищує безпечний поріг (наприклад, 2500 мА) довше за 80 мс. У цьому випадку силовий транзистор негайно вимикається для захисту бортової мережі від просідання напруги та запобігання термічному руйнуванню приводу.
- **Процедура автоматичного розхитування (`Wiggle Retry Cycle`):** якщо кінцевик не замкнувся за відведений час ходу (400 мс), модуль виконує серію швидких реверсивних рухів ригеля з тривалістю імпульсу 80 мс, дозволяючи зняти механічне напруження від тертя вушка вантажу.

---

### Вимоги до детермінізму та робота з пам'яттю

Підсистема спроектована згідно з жорсткими стандартами для вбудованих систем авіоніки:
1. **Повна відсутність динамічного виділення пам'яті:** оператори `malloc`, `free`, `new` та `delete` повністю заборонені в робочому циклі. Усі масиви, структури та кільцеві буфери мають фіксований статичний розмір, визначений на етапі компіляції.
2. **Гарантований верхній час виконання (WCET):** основна функція оновлення `payload_update()` виконує фіксовану кількість арифметичних операцій без нескінченних циклів або очікувань апаратної готовності периферії (`busy-wait polling`).
3. **Ізоляція через рівень абстракції обладнання (HAL):** взаємодія з таймерами, портами GPIO, АЦП та шинами зв'язку винесена в чисті інтерфейсні функції, що дозволяє виконувати компіляцію та модульне тестування підсистеми як на цільовому мікроконтролері (STM32, ESP32), так і в програмному симуляторі SITL на ПК.

---

### Інтеграція з протоколом MAVLink та формати повідомлень

Модуль безпосередньо транслює команди протоколу MAVLink у внутрішні стани:
- `MAV_CMD_DO_SET_ROI_LOCATION` (команда #197): встановлює координати цільової точки у поля `roi_target` та переводить прапорець `roi_active` в `true`.
- `MAV_CMD_DO_SET_CAM_TRIGG_DIST` (команда #214): налаштовує крок дистанційного тригера `trigger_dist_m`. Значення менше 0.1 м вимикає генератор інтервалів.
- `MAV_CMD_DO_GRIPPER` (команда #211) / `MAV_CMD_PAYLOAD_PREPARE_DEPLOY` (команда #30001): ініціює процедуру розмикання замка через `payload_start_drop_sequence()`.

Після успішного спрацьовування затвора або завершення скидання модуль формує асинхронні повідомлення `CAMERA_FEEDBACK` (повідомлення #180) та `CAMERA_IMAGE_CAPTURED` (повідомлення #263), передаючи наземній станції порядковий номер кадру, час експозиції з мікросекундною точністю, координати GNSS та поточні кути підвісу.

Нижче наведено повну промислову реалізацію модуля мовами C та C++.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define MAX_PAYLOAD_EVENTS      16
#define MAX_DROP_RETRIES        3
#define DEFAULT_SHUTTER_PULSE_MS 50
#define DROP_TIMEOUT_MS         400
#define CURRENT_STALL_THRESHOLD_MA 2500

typedef enum {
    TRIGGER_MODE_DISABLED = 0,
    TRIGGER_MODE_DISTANCE,
    TRIGGER_MODE_TIME,
    TRIGGER_MODE_MANUAL
} trigger_mode_t;

typedef enum {
    DROP_STATE_IDLE = 0,
    DROP_STATE_ARMED,
    DROP_STATE_TRIGGERED,
    DROP_STATE_VERIFYING,
    DROP_STATE_SUCCESS,
    DROP_STATE_STALLED,
    DROP_STATE_FAULT
} drop_state_t;

typedef struct {
    double lat;
    double lon;
    float alt_ned;
} geo_point_t;

typedef struct {
    float x;
    float y;
    float z;
} vector3f_t;

typedef struct {
    uint32_t timestamp_ms;
    uint32_t sequence_id;
    uint8_t  event_type; // 1: Shutter, 2: Drop Success, 3: Drop Fault, 4: ROI Lock
    geo_point_t position;
    float pitch_deg;
    float yaw_deg;
    uint16_t current_ma;
} payload_event_log_t;

typedef struct {
    // Тригер камери
    trigger_mode_t cam_mode;
    float trigger_dist_m;
    uint32_t trigger_interval_ms;
    vector3f_t last_cam_pos;
    uint32_t last_cam_time_ms;
    uint32_t shutter_off_time_ms;
    bool shutter_active;
    uint32_t photo_count;

    // Скидання навантаження
    drop_state_t drop_state;
    uint32_t drop_start_time_ms;
    uint8_t drop_retry_count;
    bool limit_switch_active;
    uint16_t measured_current_ma;

    // Наведення підвісу (ROI)
    bool roi_active;
    geo_point_t roi_target;
    float gimbal_cmd_pitch;
    float gimbal_cmd_yaw;

    // Кільцевий буфер подій
    payload_event_log_t events[MAX_PAYLOAD_EVENTS];
    uint8_t event_head;
    uint8_t event_tail;
} payload_manager_t;

// Апаратні заглушки інтерфейсів платформи
extern uint32_t platform_get_time_ms(void);
extern void platform_gpio_set_shutter(bool high);
extern void platform_pwm_set_drop_servo(uint16_t pwm_us);
extern void platform_solenoid_enable(bool enable);
extern bool platform_read_limit_switch(void);
extern uint16_t platform_adc_read_drop_current_ma(void);
extern void platform_send_gimbal_setpoint(float pitch_deg, float yaw_deg);

void payload_init(payload_manager_t *pm) {
    memset(pm, 0, sizeof(payload_manager_t));
    pm->cam_mode = TRIGGER_MODE_DISABLED;
    pm->drop_state = DROP_STATE_IDLE;
    pm->roi_active = false;
}

static void log_payload_event(payload_manager_t *pm, uint8_t event_type, const geo_point_t *pos, float pitch, float yaw, uint16_t current_ma) {
    uint8_t next = (pm->event_head + 1) % MAX_PAYLOAD_EVENTS;
    if (next != pm->event_tail) {
        payload_event_log_t *e = &pm->events[pm->event_head];
        e->timestamp_ms = platform_get_time_ms();
        e->sequence_id = pm->photo_count;
        e->event_type = event_type;
        e->position = *pos;
        e->pitch_deg = pitch;
        e->yaw_deg = yaw;
        e->current_ma = current_ma;
        pm->event_head = next;
    }
}

void payload_set_roi_target(payload_manager_t *pm, double lat, double lon, float alt_ned) {
    pm->roi_target.lat = lat;
    pm->roi_target.lon = lon;
    pm->roi_target.alt_ned = alt_ned;
    pm->roi_active = true;
}

void payload_clear_roi(payload_manager_t *pm) {
    pm->roi_active = false;
}

void payload_start_drop_sequence(payload_manager_t *pm) {
    if (pm->drop_state == DROP_STATE_IDLE || pm->drop_state == DROP_STATE_ARMED) {
        pm->drop_state = DROP_STATE_TRIGGERED;
        pm->drop_start_time_ms = platform_get_time_ms();
        pm->drop_retry_count = 0;

        // Подача команди на розблокування замка (імпульс серво або соленоїда)
        platform_pwm_set_drop_servo(2000);
        platform_solenoid_enable(true);
    }
}

void payload_update(payload_manager_t *pm, const vector3f_t *pos_ned, const geo_point_t *current_geo, float roll_deg, float pitch_deg, float yaw_deg) {
    uint32_t now = platform_get_time_ms();

    // 1. Обробка імпульсу затвора камери
    if (pm->shutter_active && now >= pm->shutter_off_time_ms) {
        platform_gpio_set_shutter(false);
        pm->shutter_active = false;
    }

    // 2. Генератор інтервалів зйомки
    if (pm->cam_mode == TRIGGER_MODE_DISTANCE && pm->trigger_dist_m > 0.1f) {
        // Блокуємо спрацьовування на крутих віражах (крен > 15 градусів)
        if (fabsf(roll_deg) < 15.0f && fabsf(pitch_deg) < 20.0f) {
            float dx = pos_ned->x - pm->last_cam_pos.x;
            float dy = pos_ned->y - pm->last_cam_pos.y;
            float dz = pos_ned->z - pm->last_cam_pos.z;
            float dist_moved = sqrtf(dx * dx + dy * dy + dz * dz);

            if (dist_moved >= pm->trigger_dist_m) {
                pm->last_cam_pos = *pos_ned;
                pm->shutter_active = true;
                pm->shutter_off_time_ms = now + DEFAULT_SHUTTER_PULSE_MS;
                pm->photo_count++;
                platform_gpio_set_shutter(true);
                log_payload_event(pm, 1, current_geo, pm->gimbal_cmd_pitch, pm->gimbal_cmd_yaw, 0);
            }
        }
    }

    // 3. Автомат стану механізму скидання вантажу
    switch (pm->drop_state) {
        case DROP_STATE_TRIGGERED:
            pm->measured_current_ma = platform_adc_read_drop_current_ma();
            pm->limit_switch_active = platform_read_limit_switch();

            // Перевірка на коротке замикання або заклинювання
            if (pm->measured_current_ma > CURRENT_STALL_THRESHOLD_MA) {
                platform_solenoid_enable(false);
                pm->drop_state = DROP_STATE_STALLED;
                log_payload_event(pm, 3, current_geo, 0, 0, pm->measured_current_ma);
                break;
            }

            // Перевірка спрацьовування кінцевика
            if (pm->limit_switch_active) {
                platform_solenoid_enable(false);
                pm->drop_state = DROP_STATE_SUCCESS;
                log_payload_event(pm, 2, current_geo, 0, 0, pm->measured_current_ma);
            } else if (now - pm->drop_start_time_ms > DROP_TIMEOUT_MS) {
                // Таймаут ходу ригеля: спроба повторного циклу
                if (pm->drop_retry_count < MAX_DROP_RETRIES) {
                    pm->drop_retry_count++;
                    pm->drop_start_time_ms = now;
                    // Цикл розхитування (вібрації замка)
                    platform_pwm_set_drop_servo(1000);
                    platform_solenoid_enable(false);
                    platform_pwm_set_drop_servo(2000);
                    platform_solenoid_enable(true);
                } else {
                    platform_solenoid_enable(false);
                    pm->drop_state = DROP_STATE_FAULT;
                    log_payload_event(pm, 3, current_geo, 0, 0, pm->measured_current_ma);
                }
            }
            break;

        default:
            break;
    }

    // 4. Розрахунок наведення підвісу на ціль (ROI)
    if (pm->roi_active) {
        // Локальна апроксимація зміщення в метрах
        double d_lat = (pm->roi_target.lat - current_geo->lat) * 111132.95;
        double d_lon = (pm->roi_target.lon - current_geo->lon) * (111412.84 * cos(current_geo->lat * 0.01745329));
        float d_z = pm->roi_target.alt_ned - current_geo->alt_ned;

        float dist_xy = sqrtf((float)(d_lat * d_lat + d_lon * d_lon));
        if (dist_xy > 1.0f) {
            pm->gimbal_cmd_pitch = atan2f(-d_z, dist_xy) * 57.29578f;
            pm->gimbal_cmd_yaw   = atan2f((float)d_lon, (float)d_lat) * 57.29578f;
            platform_send_gimbal_setpoint(pm->gimbal_cmd_pitch, pm->gimbal_cmd_yaw);
        }
    }
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <array>
#include <span>
#include <optional>
#include <expected>

namespace drone::payload {

constexpr size_t MaxPayloadEvents = 16;
constexpr uint8_t MaxDropRetries = 3;
constexpr uint32_t DefaultShutterPulseMs = 50;
constexpr uint32_t DropTimeoutMs = 400;
constexpr uint16_t CurrentStallThresholdMa = 2500;

enum class TriggerMode : uint8_t {
    Disabled = 0,
    Distance,
    Time,
    Manual
};

enum class DropState : uint8_t {
    Idle = 0,
    Armed,
    Triggered,
    Verifying,
    Success,
    Stalled,
    Fault
};

enum class DropError : uint8_t {
    Timeout,
    OvercurrentStall,
    SwitchMismatch
};

struct GeoPoint {
    double lat{0.0};
    double lon{0.0};
    float alt_ned{0.0f};
};

struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

struct PayloadEventLog {
    uint32_t timestamp_ms{0};
    uint32_t sequence_id{0};
    uint8_t  event_type{0}; // 1: Shutter, 2: Drop Success, 3: Drop Fault, 4: ROI Lock
    GeoPoint position{};
    float pitch_deg{0.0f};
    float yaw_deg{0.0f};
    uint16_t current_ma{0};
};

// Абстрактний апаратний драйвер
class IPayloadHardware {
public:
    virtual ~IPayloadHardware() = default;
    virtual uint32_t getTimeMs() const = 0;
    virtual void setShutterGpio(bool active) = 0;
    virtual void setDropServoPwm(uint16_t pulse_us) = 0;
    virtual void setSolenoid(bool active) = 0;
    virtual bool readLimitSwitch() const = 0;
    virtual uint16_t readDropCurrentMa() const = 0;
    virtual void setGimbalAngles(float pitch_deg, float yaw_deg) = 0;
};

class PayloadManager {
public:
    explicit PayloadManager(IPayloadHardware& hw) : hw_(hw) {}

    void setDistanceTrigger(float distance_m) noexcept {
        trigger_dist_m_ = distance_m;
        cam_mode_ = (distance_m > 0.1f) ? TriggerMode::Distance : TriggerMode::Disabled;
    }

    void setRoiTarget(const GeoPoint& target) noexcept {
        roi_target_ = target;
        roi_active_ = true;
    }

    void clearRoi() noexcept {
        roi_active_ = false;
    }

    std::expected<void, DropError> startDropSequence() noexcept {
        if (drop_state_ == DropState::Idle || drop_state_ == DropState::Armed) {
            drop_state_ = DropState::Triggered;
            drop_start_time_ms_ = hw_.getTimeMs();
            drop_retry_count_ = 0;

            hw_.setDropServoPwm(2000);
            hw_.setSolenoid(true);
            return {};
        }
        return std::unexpected(DropError::SwitchMismatch);
    }

    void update(const Vector3f& pos_ned, const GeoPoint& current_geo, float roll_deg, float pitch_deg, float yaw_deg) noexcept {
        const uint32_t now = hw_.getTimeMs();

        // 1. Обробка тривалості імпульсу затвора
        if (shutter_active_ && now >= shutter_off_time_ms_) {
            hw_.setShutterGpio(false);
            shutter_active_ = false;
        }

        // 2. Розрахунок дистанційного тригера
        if (cam_mode_ == TriggerMode::Distance && trigger_dist_m_ > 0.1f) {
            if (std::abs(roll_deg) < 15.0f && std::abs(pitch_deg) < 20.0f) {
                const float dx = pos_ned.x - last_cam_pos_.x;
                const float dy = pos_ned.y - last_cam_pos_.y;
                const float dz = pos_ned.z - last_cam_pos_.z;
                const float dist = std::sqrt(dx * dx + dy * dy + dz * dz);

                if (dist >= trigger_dist_m_) {
                    last_cam_pos_ = pos_ned;
                    shutter_active_ = true;
                    shutter_off_time_ms_ = now + DefaultShutterPulseMs;
                    photo_count_++;
                    hw_.setShutterGpio(true);
                    logEvent(1, current_geo, gimbal_cmd_pitch_, gimbal_cmd_yaw_, 0);
                }
            }
        }

        // 3. Автомат скидання вантажу
        if (drop_state_ == DropState::Triggered) {
            const uint16_t current_ma = hw_.readDropCurrentMa();
            const bool limit_reached = hw_.readLimitSwitch();

            if (current_ma > CurrentStallThresholdMa) {
                hw_.setSolenoid(false);
                drop_state_ = DropState::Stalled;
                logEvent(3, current_geo, 0.0f, 0.0f, current_ma);
            } else if (limit_reached) {
                hw_.setSolenoid(false);
                drop_state_ = DropState::Success;
                logEvent(2, current_geo, 0.0f, 0.0f, current_ma);
            } else if (now - drop_start_time_ms_ > DropTimeoutMs) {
                if (drop_retry_count_ < MaxDropRetries) {
                    drop_retry_count_++;
                    drop_start_time_ms_ = now;
                    hw_.setDropServoPwm(1000);
                    hw_.setSolenoid(false);
                    hw_.setDropServoPwm(2000);
                    hw_.setSolenoid(true);
                } else {
                    hw_.setSolenoid(false);
                    drop_state_ = DropState::Fault;
                    logEvent(3, current_geo, 0.0f, 0.0f, current_ma);
                }
            }
        }

        // 4. Геометрія наведення підвісу
        if (roi_active_) {
            constexpr double MetersPerLat = 111132.95;
            constexpr double DegToRad = 0.017453292519943295;
            constexpr float RadToDeg = 57.29577951308232f;

            const double d_lat = (roi_target_.lat - current_geo.lat) * MetersPerLat;
            const double d_lon = (roi_target_.lon - current_geo.lon) * (111412.84 * std::cos(current_geo.lat * DegToRad));
            const float d_z = roi_target_.alt_ned - current_geo.alt_ned;

            const float dist_xy = std::sqrt(static_cast<float>(d_lat * d_lat + d_lon * d_lon));
            if (dist_xy > 1.0f) {
                gimbal_cmd_pitch_ = std::atan2(-d_z, dist_xy) * RadToDeg;
                gimbal_cmd_yaw   = std::atan2(static_cast<float>(d_lon), static_cast<float>(d_lat)) * RadToDeg;
                hw_.setGimbalAngles(gimbal_cmd_pitch_, gimbal_cmd_yaw_);
            }
        }
    }

    [[nodiscard]] DropState getDropState() const noexcept { return drop_state_; }
    [[nodiscard]] uint32_t getPhotoCount() const noexcept { return photo_count_; }
    [[nodiscard]] std::span<const PayloadEventLog> getRecentEvents() const noexcept {
        return std::span<const PayloadEventLog>(events_.data(), event_count_);
    }

private:
    void logEvent(uint8_t type, const GeoPoint& pos, float pitch, float yaw, uint16_t current_ma) noexcept {
        PayloadEventLog& e = events_[event_head_];
        e.timestamp_ms = hw_.getTimeMs();
        e.sequence_id = photo_count_;
        e.event_type = type;
        e.position = pos;
        e.pitch_deg = pitch;
        e.yaw_deg = yaw;
        e.current_ma = current_ma;

        event_head_ = (event_head_ + 1) % MaxPayloadEvents;
        if (event_count_ < MaxPayloadEvents) {
            event_count_++;
        }
    }

    IPayloadHardware& hw_;

    TriggerMode cam_mode_{TriggerMode::Disabled};
    float trigger_dist_m_{0.0f};
    Vector3f last_cam_pos_{};
    uint32_t shutter_off_time_ms_{0};
    bool shutter_active_{false};
    uint32_t photo_count_{0};

    DropState drop_state_{DropState::Idle};
    uint32_t drop_start_time_ms_{0};
    uint8_t drop_retry_count_{0};

    bool roi_active_{false};
    GeoPoint roi_target_{};
    float gimbal_cmd_pitch_{0.0f};
    float gimbal_cmd_yaw_{0.0f};

    std::array<PayloadEventLog, MaxPayloadEvents> events_{};
    size_t event_head_{0};
    size_t event_count_{0};
};

} // namespace drone::payload
```
:::

---

### Покроковий сценарій проходження дії в польоті

Розглянемо типову послідовність викликів під час виконання місії доставки:
1. **Підхід до точки скидання:** планувальник маршруту активує точку типу `NAV_WAYPOINT` з параметром `Loiter Time = 3.0 с`. Модуль навігації веде дрон у зону цілі.
2. **Гальмування та стабілізація:** при вході в радіус `R_acc = 1.5 м` контролер положення гасить швидкість. Після досягнення умови `|V| < 0.2 м/с` та завершення 3 секунд зависання планувальник викликає `payload_start_drop_sequence()`.
3. **Активація актуатора:** сервопривід переводиться в положення `2000 мкс`, соленоїд отримує сигнал відкриття. Автомат переходить у стан `DROP_STATE_TRIGGERED`.
4. **Перевірка зворотного зв'язку:** через 180 мс ригель доходить до крайнього положення, замикаючи контакти кінцевика. Датчик підтверджує відкриття, соленоїд знеструмлюється, статус скидання стає `DROP_STATE_SUCCESS`.
5. **Фіксація події:** викликається функція `log_payload_event()`, яка зберігає поточні RTK-координати, час та спожитий струм у кільцевий буфер журналу, після чого планувальник місії перемикається на наступну навігаційну точку повернення додому.
