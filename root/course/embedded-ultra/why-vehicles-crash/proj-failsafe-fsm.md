# ⚙️ Реалізація ієрархічного Failsafe-автомата та сторожа шини

Надійність безпілотного апарата визначається його здатністю виявляти відхилення параметрів до того, як вони спричинять фізичне руйнування, та детерміновано виконувати процедури спасіння. Реалізація аварійного автомата (*Failsafe FSM*) вимагає чіткої ієрархії пріоритетів, незалежного контролю життєздатності завдань через сторожовий таймер (*Watchdog*) та апаратних функцій самовідновлення заблокованих цифрових інтерфейсів.

## Архітектура аварійного менеджера польотного стека

Аварійний менеджер функціонує як супервізор вищого рівня над контурами стабілізації та навігації. Він не бере безпосередньої участі у формуванні матриці мікшування моторів за нормальних умов, але має найвищий пріоритет перехоплення керування при виникненні нештатних ситуацій.

```
[Радіолінк RC]    ──┐
[Дані GNSS]       ──┤
[Здоров'я IMU]    ──┼─> [Арбітр стану та фільтр брязкоту] ─> [Failsafe FSM] ─> [Команди актуаторам]
[Напруга АКБ]     ──┤                                               │
[Статус шини I2C] ──┘                                               ▼
                                                            [Task Watchdog Feed]
```

Супервізор опрацьовує метрики стану на кожній ітерації головного циклу (з частотою від 50 до 100 Гц). Для запобігання хибним спрацьовуванням від випадкових поодиноких шумів вхідні сигнали проходять через часові фільтри підтвердження (*debouncing*):
* Втрата радіоканалу керування (*RC Link Loss*) зараховується лише після безперервної відсутності валідних пакетів протягом `1500 мс`.
* Просідання напруги батареї фільтрується ковзним середнім з постійною часу `τ = 500 мс`, щоб короткочасний імпульс від прискорення не викликав передчасної аварійної посадки.
* Відмова IMU або зрив контуру кутової швидкості є критичною подією нульової затримки: відсутність оновлення даних довше ніж `40 мс` (два пропущені цикли на частоті 50 Гц) призводить до миттєвого переходу в термінальний стан.

## Фізика та таймінги апаратного розблокування шини I2C

Шина I2C побудована за схемою монтажного «АБО» з відкритим колектором (*Open-Drain*). Коли ведучий мікроконтролер перериває транзакцію читання посеред байта (наприклад, зазнавши короткочасного скидання від просідання живлення або зависання у важкому перериванні), ведений сенсор залишається у стані очікування тактових імпульсів.

Якщо в момент збою передавався нульовий біт даних або біт підтвердження (*ACK*), вихідний польовий транзистор веденого пристрою залишається відкритим, притискаючи лінію `SDA` до потенціалу 0 В.

```
MCU Reset ──> Апаратний I2C бачить SDA = 0 ──> Помилка "Bus Busy" ──> Зависання
                               ▲
                               │ [Рішення: перемикання SCL у GPIO]
                               ▼
Генерація 9 тактів SCL ──> Ведений видає залишок байта ──> SDA переходить у 1 (High-Z)
```

Чому потрібно саме **9 тактів**:
1. Найгірший випадок: збій стався на першому біті 8-бітного слова даних. Веденому сенсору потрібно отримати ще до 8 фронтів тактування на лінії `SCL`, щоб виштовхнути залишок регістра зсуву.
2. 9-й такт призначений для передачі або прийому біта підтвердження (*NACK/ACK*).
3. Після 9-го такту ведений пристрій звільняє лінію `SDA`, дозволяючи підтягувальному резистору підняти напругу до 3.3 В.
4. Ведучий генерує послідовність умови `STOP` (перехід `SDA` з низького рівня у високий при стабільно високому рівні `SCL`), що повертає кінцевий автомат веденого пристрою в режим очікування нової адреси.

Нижче наведено повну реалізацію кінцевого автомата аварійного захисту, функції вивільнення шини I2C та механізму контролю завдань на мовах C та C++.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Перелік станів аварійного автомата */
typedef enum {
    FAILSAFE_STATE_NORMAL = 0,
    FAILSAFE_STATE_DEGRADED,
    FAILSAFE_STATE_RTH,
    FAILSAFE_STATE_EMERGENCY_LAND,
    FAILSAFE_STATE_TERMINATE
} failsafe_state_t;

/* Вхідні сенсорні метрики здоров'я апарата */
typedef struct {
    uint32_t last_rc_packet_ms;
    uint32_t last_gps_fix_ms;
    uint32_t last_imu_sample_ms;
    float battery_voltage_v;
    float roll_deg;
    float pitch_deg;
    bool i2c_bus_healthy;
} vehicle_health_t;

/* Конфігурація часових порогів (мс) та напруг (В) */
#define RC_TIMEOUT_MS           1500
#define GPS_TIMEOUT_MS          3000
#define IMU_TIMEOUT_MS          40
#define BATT_WARNING_VOLTS      14.4f   /* 4S LiPo: 3.6 В/банка */
#define BATT_CRITICAL_VOLTS     13.2f   /* 4S LiPo: 3.3 В/банка */
#define MAX_TILT_ANGLE_DEG      75.0f

typedef struct {
    failsafe_state_t current_state;
    uint32_t state_entry_time_ms;
    bool parachute_deployed;
    bool motors_disarmed;
} failsafe_manager_t;

void failsafe_init(failsafe_manager_t *mgr) {
    mgr->current_state = FAILSAFE_STATE_NORMAL;
    mgr->state_entry_time_ms = 0;
    mgr->parachute_deployed = false;
    mgr->motors_disarmed = false;
}

/* Процедура апаратного вивільнення лінії SDA шини I2C (Bit-Banging) */
bool i2c_bus_clear_recovery(void (*set_scl)(bool high),
                            void (*set_sda)(bool high),
                            bool (*read_sda)(void),
                            void (*delay_us)(uint32_t us)) {
    /* 1. Відпускаємо лінію SDA (налаштування як вхід із pull-up) */
    set_sda(true);
    delay_us(5);

    /* 2. Якщо SDA вже висока — шина не заблокована */
    if (read_sda()) {
        return true;
    }

    /* 3. Генеруємо до 9 тактів SCL для виштовхування біта зі Slave */
    for (uint8_t i = 0; i < 9; ++i) {
        set_scl(false);
        delay_us(5);
        set_scl(true);
        delay_us(5);

        /* Якщо Slave відпустив SDA, виходимо з циклу */
        if (read_sda()) {
            break;
        }
    }

    /* 4. Генерація умови STOP (перехід SDA з 0 в 1 при високому SCL) */
    set_sda(false);
    delay_us(5);
    set_scl(true);
    delay_us(5);
    set_sda(true);
    delay_us(5);

    return read_sda();
}

/* Крок обчислення кінцевого автомата Failsafe */
void failsafe_update(failsafe_manager_t *mgr,
                     const vehicle_health_t *health,
                     uint32_t now_ms) {
    const bool rc_lost = (now_ms - health->last_rc_packet_ms) > RC_TIMEOUT_MS;
    const bool gps_lost = (now_ms - health->last_gps_fix_ms) > GPS_TIMEOUT_MS;
    const bool imu_lost = (now_ms - health->last_imu_sample_ms) > IMU_TIMEOUT_MS;
    const bool batt_critical = health->battery_voltage_v < BATT_CRITICAL_VOLTS;
    const bool batt_warning = health->battery_voltage_v < BATT_WARNING_VOLTS;
    const bool angle_exceeded = (health->roll_deg > MAX_TILT_ANGLE_DEG) ||
                                (health->roll_deg < -MAX_TILT_ANGLE_DEG) ||
                                (health->pitch_deg > MAX_TILT_ANGLE_DEG) ||
                                (health->pitch_deg < -MAX_TILT_ANGLE_DEG);

    /* 1. Безумовна перевірка катастрофічних умов (Перекидання / Втрата IMU) */
    if (angle_exceeded || imu_lost) {
        mgr->current_state = FAILSAFE_STATE_TERMINATE;
        mgr->parachute_deployed = true;
        mgr->motors_disarmed = true;
        return;
    }

    /* 2. Обробка переходів за станами */
    switch (mgr->current_state) {
        case FAILSAFE_STATE_NORMAL:
            if (rc_lost && !gps_lost) {
                mgr->current_state = FAILSAFE_STATE_RTH;
                mgr->state_entry_time_ms = now_ms;
            } else if (rc_lost && gps_lost) {
                mgr->current_state = FAILSAFE_STATE_EMERGENCY_LAND;
                mgr->state_entry_time_ms = now_ms;
            } else if (batt_warning || !health->i2c_bus_healthy) {
                mgr->current_state = FAILSAFE_STATE_DEGRADED;
                mgr->state_entry_time_ms = now_ms;
            }
            break;

        case FAILSAFE_STATE_DEGRADED:
            if (batt_critical) {
                mgr->current_state = FAILSAFE_STATE_EMERGENCY_LAND;
                mgr->state_entry_time_ms = now_ms;
            } else if (rc_lost && !gps_lost) {
                mgr->current_state = FAILSAFE_STATE_RTH;
                mgr->state_entry_time_ms = now_ms;
            } else if (!rc_lost && !batt_warning && health->i2c_bus_healthy) {
                mgr->current_state = FAILSAFE_STATE_NORMAL;
            }
            break;

        case FAILSAFE_STATE_RTH:
            if (batt_critical || gps_lost) {
                mgr->current_state = FAILSAFE_STATE_EMERGENCY_LAND;
                mgr->state_entry_time_ms = now_ms;
            }
            break;

        case FAILSAFE_STATE_EMERGENCY_LAND:
            /* Якщо апарат знижується довше 30 секунд — примусове вимикання моторів */
            if (now_ms - mgr->state_entry_time_ms > 30000) {
                mgr->motors_disarmed = true;
            }
            break;

        case FAILSAFE_STATE_TERMINATE:
            mgr->parachute_deployed = true;
            mgr->motors_disarmed = true;
            break;
    }
}
```
```cpp
#include <cstdint>
#include <functional>

enum class FailsafeState : uint8_t {
    Normal = 0,
    SensorDegraded,
    AutoRth,
    EmergencyDescent,
    CriticalTerminate
};

struct VehicleHealth {
    uint32_t last_rc_packet_ms{0};
    uint32_t last_gps_fix_ms{0};
    uint32_t last_imu_sample_ms{0};
    float battery_voltage_v{16.8f};
    float roll_deg{0.0f};
    float pitch_deg{0.0f};
    bool i2c_bus_healthy{true};
};

class FailsafeManager {
public:
    static constexpr uint32_t kRcTimeoutMs = 1500;
    static constexpr uint32_t kGpsTimeoutMs = 3000;
    static constexpr uint32_t kImuTimeoutMs = 40;
    static constexpr float kBattWarningVolts = 14.4f;
    static constexpr float kBattCriticalVolts = 13.2f;
    static constexpr float kMaxTiltAngleDeg = 75.0f;

    struct ActionFlags {
        bool deploy_parachute{false};
        bool disarm_motors{false};
        bool execute_rth{false};
        bool execute_land{false};
    };

    constexpr FailsafeManager() noexcept = default;

    void update(const VehicleHealth& health, uint32_t now_ms) noexcept {
        const bool rc_lost = (now_ms - health.last_rc_packet_ms) > kRcTimeoutMs;
        const bool gps_lost = (now_ms - health.last_gps_fix_ms) > kGpsTimeoutMs;
        const bool imu_lost = (now_ms - health.last_imu_sample_ms) > kImuTimeoutMs;
        const bool batt_critical = health.battery_voltage_v < kBattCriticalVolts;
        const bool batt_warning = health.battery_voltage_v < kBattWarningVolts;
        const bool angle_exceeded = (health.roll_deg > kMaxTiltAngleDeg) ||
                                    (health.roll_deg < -kMaxTiltAngleDeg) ||
                                    (health.pitch_deg > kMaxTiltAngleDeg) ||
                                    (health.pitch_deg < -kMaxTiltAngleDeg);

        // 1. Аварійне переривання польоту при втраті кутової стабілізації
        if (angle_exceeded || imu_lost) {
            state_ = FailsafeState::CriticalTerminate;
            actions_.deploy_parachute = true;
            actions_.disarm_motors = true;
            return;
        }

        // 2. Ієрархічні переходи
        switch (state_) {
            case FailsafeState::Normal:
                if (rc_lost && !gps_lost) {
                    transition_to(FailsafeState::AutoRth, now_ms);
                } else if (rc_lost && gps_lost) {
                    transition_to(FailsafeState::EmergencyDescent, now_ms);
                } else if (batt_warning || !health.i2c_bus_healthy) {
                    transition_to(FailsafeState::SensorDegraded, now_ms);
                }
                break;

            case FailsafeState::SensorDegraded:
                if (batt_critical) {
                    transition_to(FailsafeState::EmergencyDescent, now_ms);
                } else if (rc_lost && !gps_lost) {
                    transition_to(FailsafeState::AutoRth, now_ms);
                } else if (!rc_lost && !batt_warning && health.i2c_bus_healthy) {
                    transition_to(FailsafeState::Normal, now_ms);
                }
                break;

            case FailsafeState::AutoRth:
                if (batt_critical || gps_lost) {
                    transition_to(FailsafeState::EmergencyDescent, now_ms);
                }
                break;

            case FailsafeState::EmergencyDescent:
                if (now_ms - state_entry_time_ms_ > 30000) {
                    actions_.disarm_motors = true;
                }
                break;

            case FailsafeState::CriticalTerminate:
                actions_.deploy_parachute = true;
                actions_.disarm_motors = true;
                break;
        }

        apply_actions();
    }

    // Апаратне відновлення шини I2C
    static bool clear_i2c_bus(const std::function<void(bool)>& set_scl,
                              const std::function<void(bool)>& set_sda,
                              const std::function<bool()>& read_sda,
                              const std::function<void(uint32_t)>& delay_us) {
        set_sda(true);
        delay_us(5);
        if (read_sda()) return true;

        for (uint8_t i = 0; i < 9; ++i) {
            set_scl(false);
            delay_us(5);
            set_scl(true);
            delay_us(5);
            if (read_sda()) break;
        }

        // STOP condition
        set_sda(false);
        delay_us(5);
        set_scl(true);
        delay_us(5);
        set_sda(true);
        delay_us(5);

        return read_sda();
    }

    [[nodiscard]] FailsafeState get_state() const noexcept { return state_; }
    [[nodiscard]] const ActionFlags& get_actions() const noexcept { return actions_; }

private:
    void transition_to(FailsafeState next, uint32_t now_ms) noexcept {
        state_ = next;
        state_entry_time_ms_ = now_ms;
    }

    void apply_actions() noexcept {
        actions_.execute_rth = (state_ == FailsafeState::AutoRth);
        actions_.execute_land = (state_ == FailsafeState::EmergencyDescent);
    }

    FailsafeState state_{FailsafeState::Normal};
    uint32_t state_entry_time_ms_{0};
    ActionFlags actions_{};
};
```
:::

## Обробка крайових випадків та фільтрація хибних спрацьовувань

Реальні польотні випробування показують, що прості порогові умови без часової гістерезисної фільтрації призводять до хибних спрацьовувань аварійних режимів на граничних маневрах.

### 1. Короткочасне просідання напруги при різкому гальмуванні
При переході двигунів у режим активного гальмування (*Damped Light / Regenerative Braking*) енергія самоіндукції обмоток повертається у батарею, викликаючи короткочасний сплеск напруги, за яким слідує різкий стрибок споживання при компенсаційному розгоні. Якщо поріг `BATT_CRITICAL_VOLTS` оцінювати миттєво, одиночний сплеск струму переведе дрон в аварійну посадку посеред складного маневру. Для захисту використовується інтегральний лічильник часу під критичною напругою: прапорець `batt_critical` виставляється лише тоді, коли напруга утримується нижче порогу довше `1200 мс`.

### 2. Стрибки точності супутникової навігації (HDOP Glitch)
Під впливом завад або міського багатопроменевого поширення радіохвиль приймач GNSS може видати стрибок горизонтального фактора погіршення точності (*HDOP* > 2.5) або повідомити про раптову зміну швидкості на 50 м/с. Аварійний менеджер не повинен негайно активувати RTH за некоректними координатами. Навігаційний блок перевіряє дисперсію інновацій у фільтрі Калмана: якщо нев'язка вимірів супутника та акселерометра перевищує три стандартні відхилення (`3σ`), навігаційні виміри тимчасово відкидаються, а апарат утримує позицію за оптичним потоком або інерціальним чистим рахівництвом (*Dead Reckoning*) до 10 секунд.

### 3. Тріск та розрив пакетів радіоканалу (RC Glitch)
При польотах за перешкодами втрата кількох пакетів поспіль є типовим явищем. Протокол ExpressLRS або Crossfire надсилає пакети з частотою 150–500 Гц. Пропуск 5–10 пакетів (пауза 20–50 мс) вважається нормальним шумом середовища; польотний контролер продовжує виконувати останню валідну команду з поступовим плавним зменшенням кутових швидкостей (*Hold last position with decay*). Лише коли час без пакетів перевищує `RC_TIMEOUT_MS = 1500 мс`, активується автомат Failsafe.

## Інтеграція зі сторожовим таймером операційної системи (Task Watchdog)

У складних прошивках під керуванням FreeRTOS пряме скидання апаратного таймера `IWDG` всередині переривання таймера або окремої низькопріоритетної задачі є класичною архітектурною помилкою. Якщо критичне завдання контуру стабілізації (`Attitude Task`) зависне у нескінченному циклі або заблокується на м'ютексі, низькопріоритетний обробник переривання продовжить регулярно скидати таймер, маскуючи катастрофу від апаратного захисту.

Правильна реалізація передбачає впровадження **бітової маски серцебиття** (*Task Heartbeat Bitmask*):

1. **Реєстрація контрольних точок:** Кожне життєво важливе завдання системи отримує унікальний бітовий прапорець у системному реєстрі (наприклад, біт 0 — `Rate Loop`, біт 1 — `Navigation`, біт 2 — `Failsafe Manager`).
2. **Звіт про проходження дедлайну:** Наприкінці кожної успішної ітерації задача встановлює свій біт викликом атомарної операції.
3. **Супервізор скидання сторожа:** Окрема високопріоритетна задача перевіряє, чи всі біти встановлено в 1 за виділений період (наприклад, кожні 20 мс). Якщо хоча б одна задача пропустила свій дедлайн, супервізор навмисно припиняє годування апаратного сторожа `IWDG`.
4. **Апаратний перезапуск та збереження дампу:** Через 100 мс сторож перезавантажує мікроконтролер. Під час старту завантажувач аналізує регістр причин скидання (наприклад, біт `IWDGRSTF` у регістрі `RCC_CSR` для STM32), зберігає трасування стека в енергонезалежну пам'ять (*Blackbox*) та негайно ініціалізує процедуру аварійної посадки без спроби відновлення небезпечного польотного завдання.
