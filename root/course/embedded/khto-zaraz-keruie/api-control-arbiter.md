# 📋 Інтерфейс та структури даних диспетчера керування

Цей інтерфейс визначає програмний контракт модуля арбітражу та мультиплексування джерел керування в автономних вбудованих системах. Його головне призначення — створити детермінований, суворо типізований бар'єр між зовнішніми комунікаційними драйверами (радіоприймачі RC, демони MAVLink, вузли micro-ROS, підсистеми аварійного моніторингу) та внутрішніми високочастотними контурами стабілізації (каскадні ПІД-регулятори кутових швидкостей і тяги).

Модуль спроєктовано для роботи в умовах жорсткого реального часу (Hard Real-Time):
1. **Відсутність динамічної пам'яті:** усі структури розміщуються статично на етапі ініціалізації або на стеку задачі; жодних викликів `malloc()`, `free()`, `new` або динамічних контейнерів змінного розміру під час польоту.
2. **Детермінований час виконання (Bounded WCET):** функції обробки та арбітражу виконують константну кількість операцій `O(N)` (де `N` — кількість зареєстрованих джерел, зазвичай 4..8) без рекурсій та розгалужень із невідомими лічильниками ітерацій.
3. **Безпека потоків і подвійне буферизування:** чітке розділення фази асинхронного приймання даних (запис у вхідні слоти) та синхронної фази оцінки у високочастотному польотному циклі (100–400 Гц).

## Переліки та базові типи даних

Джерела рішень розбиті на фіксовані рівні авторитету. Менше числове значення відповідає вищому пріоритету витіснення: аварійний автомат безпеки (`SOURCE_FAILSAFE`) має найвищий ранг і здатний миттєво перебити будь-які дії оператора або алгоритмів.

:::tabs
```c
#ifndef CONTROL_ARBITER_TYPES_H
#define CONTROL_ARBITER_TYPES_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Ідентифікатори джерел керування в порядку зменшення пріоритету.
 */
typedef enum {
    SOURCE_FAILSAFE    = 0,  /**< Аварійний контур безпеки (найвищий авторитет) */
    SOURCE_RC_PILOT    = 1,  /**< Ручний пульт пілота (ручне перехоплення стіками) */
    SOURCE_OFFBOARD    = 2,  /**< Бортовий комп'ютер / планувальник / AI-зір */
    SOURCE_GCS_MISSION = 3,  /**< Наземна станція / автопілотна місія за точками */
    SOURCE_COUNT       = 4,  /**< Загальна кількість підтримуваних джерел */
    SOURCE_NONE        = 255 /**< Жодне джерело не вибрано / безпечний дефолт */
} control_source_id_t;

/**
 * @brief Бітова маска станів життєздатності слота джерела.
 */
typedef enum {
    SOURCE_STATE_INACTIVE     = 0,       /**< Джерело вимкнене або ще не надсилало кадрів */
    SOURCE_STATE_ACTIVE       = (1 << 0),/**< Сигнал свіжий, таймаут не перевищено */
    SOURCE_STATE_TIMED_OUT    = (1 << 1),/**< Heartbeat або потік даних прострочено */
    SOURCE_STATE_PREEMPTED    = (1 << 2),/**< Джерело живе, але витіснене вищим пріоритетом */
    SOURCE_STATE_STICK_ACTIVE = (1 << 3) /**< Зафіксовано рух стіка поза зоною мертвої смуги */
} source_state_flags_t;

/**
 * @brief Тип цільової уставки для внутрішнього контуру стабілізації.
 */
typedef enum {
    SETPOINT_TYPE_ATTITUDE_RATE, /**< Кутові швидкості (рад/с) + нормалізований газ [0..1] */
    SETPOINT_TYPE_ATTITUDE_ANGLE,/**< Кути Ойлера (крен/тангаж/курс у рад) + газ [0..1] */
    SETPOINT_TYPE_VELOCITY_NED,  /**< Вектор швидкості у системі NED (м/с) + курс */
    SETPOINT_TYPE_POSITION_NED   /**< Координати цілі у системі NED (м) */
} setpoint_type_t;

/**
 * @brief Уніфікований контейнер уставки керування.
 */
typedef struct {
    uint64_t timestamp_us;       /**< Монотонна мітка часу створення/прийому кадру (мкс) */
    setpoint_type_t type;        /**< Фізичний режим уставки */
    float channels[4];           /**< Канали: [0]=Roll, [1]=Pitch, [2]=Yaw, [3]=Thrust */
    bool valid;                  /**< Прапорець цілісності та валідності даних */
} control_setpoint_t;

/**
 * @brief Параметри конфігурації арбітражу для конкретного джерела.
 */
typedef struct {
    uint32_t timeout_us;         /**< Поріг сторожового таймера неактивності (мкс) */
    float stick_deadband;        /**< Мертва смуга виявлення перехоплення стіком [0..1] */
    float max_slew_rate[4];      /**< Максимальна швидкість зміни каналів (од/с) */
    bool allow_stick_override;   /**< Дозвіл витіснення іншого джерела рухом стіків */
} source_config_t;

#endif /* CONTROL_ARBITER_TYPES_H */
```
```cpp
#pragma once

#include <cstdint>
#include <cstddef>
#include <array>
#include <optional>
#include <chrono>

namespace embedded::control {

using Microseconds = std::chrono::microseconds;
using TimePoint = std::chrono::time_point<std::chrono::steady_clock, Microseconds>;

/**
 * @brief Ідентифікатори джерел керування в порядку спадання авторитету.
 */
enum class SourceId : uint8_t {
    Failsafe = 0,    ///< Аварійний контур безпеки (найвищий авторитет)
    RcPilot = 1,     ///< Ручний пульт пілота (ручне перехоплення)
    Offboard = 2,    ///< Бортовий комп'ютер / AI-планувальник
    GcsMission = 3,  ///< Наземна станція / польотна місія
    None = 255       ///< Жодне джерело не обрано
};

constexpr size_t SourceCount = 4;

/**
 * @brief Стан активності джерела.
 */
enum class SourceState : uint8_t {
    Inactive = 0,
    Active = 1 << 0,
    TimedOut = 1 << 1,
    Preempted = 1 << 2,
    StickActive = 1 << 3
};

inline constexpr SourceState operator|(SourceState a, SourceState b) {
    return static_cast<SourceState>(static_cast<uint8_t>(a) | static_cast<uint8_t>(b));
}

inline constexpr bool has_flag(SourceState val, SourceState flag) {
    return (static_cast<uint8_t>(val) & static_cast<uint8_t>(flag)) != 0;
}

/**
 * @brief Типи уставок стабілізації.
 */
enum class SetpointType : uint8_t {
    AttitudeRate,
    AttitudeAngle,
    VelocityNed,
    PositionNed
};

/**
 * @brief Уніфікована уставка керування.
 */
struct Setpoint {
    Microseconds timestamp{0};
    SetpointType type{SetpointType::AttitudeAngle};
    std::array<float, 4> channels{0.0f, 0.0f, 0.0f, 0.0f}; // Roll, Pitch, Yaw, Thrust
    bool valid{false};
};

/**
 * @brief Конфігураційні параметри джерела.
 */
struct SourceConfig {
    Microseconds timeout{std::chrono::milliseconds(500)};
    float stick_deadband{0.08f};
    std::array<float, 4> max_slew_rate{6.0f, 6.0f, 10.0f, 3.0f}; // од/с на канал
    bool allow_stick_override{true};
};

} // namespace embedded::control
```
:::

## Публічний інтерфейс диспетчера

Публічний API надає методи конфігурації, періодичного подання вхідних даних від комунікаційних задач, оновлення сторожових таймерів і синхронної оцінки уставки на кожному такті польотного циклу.

:::tabs
```c
#ifndef CONTROL_ARBITER_H
#define CONTROL_ARBITER_H

#include "control_arbiter_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    control_setpoint_t raw_setpoint;
    uint64_t last_heartbeat_us;
    uint64_t last_packet_us;
    source_config_t config;
    uint8_t state_flags;
    bool registered;
} source_slot_t;

typedef struct {
    source_slot_t sources[SOURCE_COUNT];
    control_source_id_t active_source;
    control_source_id_t previous_source;
    control_setpoint_t smoothed_output;
    uint64_t last_eval_time_us;
    uint32_t transition_counter;
} arbiter_instance_t;

/**
 * @brief Ініціалізація структури арбітра значеннями за замовчуванням.
 * @param arb Вказівник на структуру екземпляра арбітра.
 */
void arbiter_init(arbiter_instance_t *arb);

/**
 * @brief Конфігурація порогів таймауту та лімітів наростання для слота.
 * @param arb Вказівник на екземпляр арбітра.
 * @param id Ідентифікатор джерела (0..SOURCE_COUNT-1).
 * @param cfg Вказівник на структуру конфігурації.
 * @return true, якщо слот успішно сконфігуровано.
 */
bool arbiter_configure_source(arbiter_instance_t *arb, 
                              control_source_id_t id, 
                              const source_config_t *cfg);

/**
 * @brief Оновлення мітки сторожового таймера (heartbeat feed).
 * @param arb Вказівник на екземпляр арбітра.
 * @param id Ідентифікатор джерела.
 * @param now_us Поточний монотонний системний час у мікросекундах.
 */
void arbiter_feed_heartbeat(arbiter_instance_t *arb, 
                            control_source_id_t id, 
                            uint64_t now_us);

/**
 * @brief Подання нового кадру уставки від комунікаційного драйвера.
 * @param arb Вказівник на екземпляр арбітра.
 * @param id Ідентифікатор джерела.
 * @param sp Вказівник на нову уставку.
 * @param now_us Поточний монотонний системний час у мікросекундах.
 */
void arbiter_submit_setpoint(arbiter_instance_t *arb, 
                             control_source_id_t id, 
                             const control_setpoint_t *sp, 
                             uint64_t now_us);

/**
 * @brief Основний крок оцінки пріоритетів та безударної фільтрації.
 * @param arb Вказівник на екземпляр арбітра.
 * @param now_us Поточний монотонний час системи у мікросекундах.
 * @param out_setpoint Буфер для запису згладженої уставки для регулятора.
 * @return Ідентифікатор джерела, яке зараз володіє авторитетом керування.
 */
control_source_id_t arbiter_evaluate(arbiter_instance_t *arb, 
                                     uint64_t now_us, 
                                     control_setpoint_t *out_setpoint);

/**
 * @brief Отримання поточного активного джерела авторитету.
 */
control_source_id_t arbiter_get_active_source(const arbiter_instance_t *arb);

/**
 * @brief Примусове захоплення виміряного стану апарата для безперервного рестарту.
 * @param arb Вказівник на екземпляр арбітра.
 * @param current_state Масив [Roll, Pitch, Yaw, Thrust] поточного стану EKF.
 * @param now_us Поточний час у мікросекундах.
 */
void arbiter_reset_state(arbiter_instance_t *arb, 
                         const float current_state[4], 
                         uint64_t now_us);

#ifdef __cplusplus
}
#endif

#endif /* CONTROL_ARBITER_H */
```
```cpp
#pragma once

#include "control_arbiter_types.hpp"
#include <span>

namespace embedded::control {

/**
 * @brief Клас пріоритетного селектора та безударного фільтра каналів керування.
 */
class ControlArbiter {
public:
    ControlArbiter() noexcept;

    /**
     * @brief Налаштувати часові пороги та ліміти наростання для джерела.
     */
    bool configure_source(SourceId id, const SourceConfig& cfg) noexcept;

    /**
     * @brief Зафіксувати надходження сигналу життєздатності (watchdog feed).
     */
    void feed_heartbeat(SourceId id, Microseconds now) noexcept;

    /**
     * @brief Передати нову уставку від каналу зв'язку.
     */
    void submit_setpoint(SourceId id, const Setpoint& sp, Microseconds now) noexcept;

    /**
     * @brief Виконати арбітраж та обчислити згладжену вихідну уставку.
     * @param now Поточний монотонний час.
     * @return Результуюча уставка, готова для подачі у внутрішній каскад ПІД.
     */
    Setpoint evaluate(Microseconds now) noexcept;

    /**
     * @brief Отримати поточне активне джерело авторитету.
     */
    [[nodiscard]] SourceId active_source() const noexcept { return active_source_; }

    /**
     * @brief Захоплення поточного стану апарата для безударного рестарту.
     */
    void capture_state(std::span<const float, 4> current_state, Microseconds now) noexcept;

    /**
     * @brief Отримати діагностичний стан слота.
     */
    [[nodiscard]] SourceState source_state(SourceId id) const noexcept;

    /**
     * @brief Кількість перемикань авторитету з моменту запуску.
     */
    [[nodiscard]] uint32_t transition_count() const noexcept { return transitions_; }

private:
    struct Slot {
        Setpoint raw_sp{};
        Microseconds last_heartbeat{0};
        Microseconds last_packet{0};
        SourceConfig config{};
        SourceState state{SourceState::Inactive};
        bool configured{false};
    };

    std::array<Slot, SourceCount> slots_{};
    SourceId active_source_{SourceId::None};
    SourceId previous_source_{SourceId::None};
    Setpoint smoothed_output_{};
    Microseconds last_eval_time_{0};
    uint32_t transitions_{0};

    [[nodiscard]] bool check_stick_activity(const Slot& slot) const noexcept;
    void apply_slew_rate(const Setpoint& target, float dt_sec) noexcept;
};

} // namespace embedded::control
```
:::

## Детальний розбір полів і фізичних одиниць

1. **`timestamp_us` (uint64_t):** Монотонний системний час у мікросекундах від старту апарата (наприклад, з апаратного лічильника циклів DWT у мікроконтролерах ARM Cortex-M або `esp_timer_get_time()` в ESP32). 64-бітне представлення гарантує відсутність переповнення протягом 584 тисяч років безперервної роботи, що повністю знімає проблему помилкових стрибків часу при переході через нуль, яка виникає в 32-бітних мілісекундних таймерах кожні 49.7 днів.
2. **`channels[4]` (float):**
   - `channels[0]` (Roll / Крен): кут крену в радіанах (типово ±0.6 рад / ±35°) для кутового режиму або кутова швидкість у рад/с (±5.0 рад/с) для акро-режиму.
   - `channels[1]` (Pitch / Тангаж): кут тангажу в радіанах (±0.6 рад) або кутова швидкість (±5.0 рад/с).
   - `channels[2]` (Yaw / Курс): кутова швидкість гарпажу в рад/с (±3.0..10.0 рад/с) або цільовий азимут.
   - `channels[3]` (Thrust / Тяга): нормалізований колективний газ у діапазоні `[0.0 .. 1.0]`. Значення `0.0` відповідає зупинці моторів, `0.5` — розрахунковій точці висіння, `1.0` — максимальній тязі силової установки.
3. **`stick_deadband` (float):** Нормалізований радіус мертвої смуги навколо нейтрального положення стіків пульта `[0.0 .. 1.0]`. Значення `0.08` означає, що перші 8% ходу стіка ігноруються як шум потенціометра або тепловий дрейф датчиків Холла.
4. **`max_slew_rate[4]` (float):** Гранично допустима швидкість наростання сигналу за секунду. Для дронів середнього класу типовими є значення:
   - Крен / Тангаж: `6.0 rad/s²` (перехід від 0 до 30° за 87 мс).
   - Курс: `10.0 rad/s²` (швидкий розворот).
   - Тяга: `3.0 /s` (наростання газу від 0 до 100% за 330 мс, що запобігає зриву струму на регуляторах швидкості ESC).

## Валідація вхідних даних та діапазони безпеки

Перед тим як уставка записується у внутрішній слот, інтерфейс вимагає проходження санітарної перевірки:
1. **Перевірка на NaN та нескінченність (NaN/Inf Gating):** Будь-який кадр, що містить значення `isnan(channels[i])` або `isinf(channels[i])`, негайно відкидається, слот позначається як невалідний, а лічильник помилок протоколу інкрементується.
2. **Жорсткий кліпінг меж (Physical Boundary Clamping):** Кути крену й тангажу примусово обмежуються діапазоном `[-0.785 .. +0.785]` рад (±45°), а тяга — діапазоном `[0.0 .. 1.0]`. Це унеможливлює передачу некоректно масштабованих команд із зовнішнього софту.
3. **Селекція режимів (Setpoint Type Consistency):** Якщо джерело раптово змінює тип уставки (наприклад, перемикається з кутових швидкостей на вектор швидкості NED), арбітр вимагає примусового виклику `arbiter_reset_state()`, щоб переініціалізувати внутрішні інтегратори регулятора.

## Потокова модель та інтеграція в RTOS

У багатозадачних операційних системах (FreeRTOS, Zephyr) комунікаційні задачі та петля стабілізації виконуються в різних контекстах із різними пріоритетами:
- **Комунікаційні задачі (Пріоритет Low/Medium):** задачі прийому кадрів CRSF від радіоприймача, демони MAVLink UART та клієнти micro-ROS працюють асинхронно. Коли надходить новий валідний пакет, задача викликає функцію `arbiter_submit_setpoint()`.
- **Польотна задача реального часу (Пріоритет Real-Time, 400 Гц):** прокидається строго за апаратним таймером кожні 2.5 мс, зчитує гіроскопи, викликає `arbiter_evaluate()` та передає уставку в мікшер моторів.

Щоб уникнути взаємних блокувань (Deadlock) та інверсії пріоритетів (Priority Inversion), передача даних між асинхронним прийомом і польотною петлею організовується через **подвійну буферизацію з атомарними прапорцями** (*Lock-Free Ping-Pong Buffer*) або короткі критичні секції із забороною переривань на час копіювання структури `control_setpoint_t` (всього 24 байти, що займає близько 10–15 машинних тактів).

## Обробка крайових випадків та відновлення після збоїв

1. **Одночасне зникнення всіх джерел:** Якщо обривається зв'язок із пультом, бортовий комп'ютер вимикається через збій живлення, а наземна станція мовчить, арбітр виставляє активним джерелом `SOURCE_NONE` та переводить вихідну уставку в аварійний дефолт (нульові кути крену й тангажу, плавне зниження газу).
2. **Брязкіт стіків на межі мертвої смуги:** Для запобігання високочастотному перемиканню режимів туди-назад, коли пілот тримає стік рівно на порозі `0.08`, алгоритм застосовує гістерезис: поріг активації становить `0.08`, а поріг деактивації — `0.05`.
3. **Холодний старт і захист від стрибка:** При першому запуску системи після перезавантаження, доки EKF не видасть достовірну оцінку стану, фільтр Slew-Rate блокує будь-яку видачу тяги на мотори, утримуючи значення `channels[3] = 0.0`.
4. **Просідання живлення (Brown-out Recovery):** Якщо контролер перезавантажується під час польоту через короткочасне просідання напруги, функція `arbiter_reset_state()` миттєво підтягує початкову уставку до поточного кута нахилу та обертів, унеможливлюючи перекидання апарата при повторному старті.
