# ⚙️ Скінченний автомат детектора контакту з землею

Визначення моменту посадки (англ. *Land Detection*) — це найвідповідальніший бар'єр безпеки безпілотного літального апарата. Помилка у визначенні призводить або до передчасного відключення моторів у повітрі з падінням апарата, або до запізнілого роззброєння, коли регулятор орієнтації намагається компенсувати нахил на ґрунті через інтегральну складову (англ. *Integrator Windup*) і перекидає дрон через лапу шасі (*Tip-over*).

Цей проєкт демонструє модуль скінченного автомата детектування посадки (*Land Detector State Machine*), розрахований на роботу в контурі реального часу з частотою 50–100 Гц. Модуль агрегує дані вертикальної швидкості `v_z`, виходу тяги регулятора `throttle`, дисперсії вібрацій акселерометра та споживаного струму силової шини.

## 1. Фізичні критерії розпізнавання контакту

Просте зчитування висоти з барометра чи супутникового приймача не дає надійної відповіді на питання, чи торкнувся апарат землі. Як було доведено в [аеродинаміці екранного ефекту](root:embedded/posadka-naoslip-i-chomu-vona-mazhetsia/math-ground-effect-thrust.md), біля ґрунту барометр зазнає аеродинамічного підпору до 20–30 Па, показуючи помилкову висоту нижче рівня землі, а супутниковий GNSS зазнає багатопроменевих завад.

Тому надійний детектор посадки спирається на комплекс із чотирьох незалежних фізичних ознак:

1. **Зупинка вертикального руху (Zero Vertical Velocity):** коли апарат опускається зі швидкістю `0.4 м/с` і торкається опори, його вертикальна швидкість `v_z` падає до нуля (`|v_z| < 0.15 м/с`), незважаючи на те, що автопілот вимагає продовження спуску.
2. **Газ на нижньому обмеженні (Throttle Saturation):** оскільки вертикальна швидкість припинила падати, інтегральний та пропорційний регулятори висоти зменшують сигнал тяги, заганяючи вихід газу на мінімально допустимий рівень холостого ходу (`throttle <= throttle_min_land`).
3. **Імпульс реакції опори на акселерометрі (Touchdown Shock):** момент контакту створює механічний сплеск прискорення вздовж вертикальної осі Z. Навіть на м'яких пружинних ніжках шасі похідна прискорення (ривок, англ. *jerk*) та відхилення модуля сили `|a_z - g|` перевищують поріг `3.0–4.5 м/с²`.
4. **Падіння навантаження на ротори (Current Drop):** коли дрон висить у повітрі, мотори споживають значний струм для прокачування маси повітря. У момент контакту з землею на мінімальному газі аеродинамічний опір падає, і загальний струм споживання силової шини знижується на 35–50% від номіналу висіння.

## 2. Архітектура станів автомата

Скінченний автомат реалізує чотири послідовні фази:

```
[ LAND_STATE_FLYING ]
         │  Команда на посадку (Auto Land / RTL)
         ▼
[ LAND_STATE_DESCENDING ]
         │  Висота h < h_transition (або команда на фінальний спуск)
         ▼
[ LAND_STATE_NEAR_GROUND ]   <─── Заморозка I-терму, обмеження тяги T_max ≤ 0.7·T_hover
         │  |v_z| < 0.15 м/с + Throttle ≤ Min + Сплеск перевантаження / Спад струму (t ≥ 350 мс)
         ▼
[ LAND_STATE_GROUND_CONTACT ]
         │  Підтвердження нерухомості без підскоків (t ≥ 500 мс)
         ▼
[ LAND_STATE_LANDED ]        ───> Відсічка ШІМ (Disarm)
```

1. **`FLYING`**: штатний польотний режим. Моніторинг не втручається в роботу контурів стабілізації.
2. **`DESCENDING`**: зниження з робочою швидкістю `1.0–1.5 м/с` за даними глобальної навігації.
3. **`NEAR_GROUND`**: апарат перебуває в зоні дії екранного ефекту (`h < 1.5 м`). Заморожується інтегральна складова PID по крену/тангажу для запобігання перекиданню (*anti-windup*), максимальна тяга обмежується на рівні `0.7 · T_hover`, уставка вертикальної швидкості затискається на `0.3–0.4 м/с`.
4. **`GROUND_CONTACT`**: перший фізичний контакт. Фіксується за одночасним виконанням умов: вертикальна швидкість нижче порогу зупинки, вихід газу на нижньому упорі, характерний імпульс по осі Z акселерометра.
5. **`LANDED`**: стан стійкого перебування на ґрунті. Видається прапорець безпечного роззброєння (*Disarm Signal*).

## 3. Реалізація детектора посадки

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    LAND_STATE_FLYING = 0,
    LAND_STATE_DESCENDING,
    LAND_STATE_NEAR_GROUND,
    LAND_STATE_GROUND_CONTACT,
    LAND_STATE_LANDED
} land_state_t;

typedef struct {
    float v_z_descend_target;    /* Цільова швидкість посадки, м/с (напр. -0.4f) */
    float v_z_stopped_thresh;    /* Поріг нульової вертикальної швидкості, м/с (0.15f) */
    float throttle_min_limit;    /* Мінімальний поріг газу (0.12f від діапазону 0..1) */
    float accel_shock_thresh;    /* Поріг ударного прискорення дотику, м/с^2 (3.5f) */
    float current_drop_ratio;    /* Відносне падіння струму при розвантаженні (0.65f) */
    uint32_t contact_time_ms;    /* Час витримки контакту до підтвердження (350 мс) */
    uint32_t disarm_delay_ms;    /* Затримка перед повним вимкненням моторів (500 мс) */
} land_detector_config_t;

typedef struct {
    float alt_ground_relative;   /* Висота над землею (ToF або EKF), м */
    float v_z_filtered;          /* Оцінка вертикальної швидкості (вгору > 0), м/с */
    float throttle_out;          /* Поточний вихідний газ регулятора (0.0 .. 1.0) */
    float accel_z_raw;           /* Прискорення по осі Z (з урахуванням 1g), м/с^2 */
    float battery_current;       /* Струм споживання, А */
    float hover_current;         /* Базовий струм висіння, А */
    bool is_landing_commanded;   /* Прапорець активного режиму посадки */
} land_sensor_data_t;

typedef struct {
    land_state_t state;
    uint32_t state_timer_ms;
    bool i_term_freeze;
    bool disarm_request;
    land_detector_config_t cfg;
} land_detector_t;

void land_detector_init(land_detector_t *detector, const land_detector_config_t *cfg) {
    detector->state = LAND_STATE_FLYING;
    detector->state_timer_ms = 0;
    detector->i_term_freeze = false;
    detector->disarm_request = false;
    detector->cfg = *cfg;
}

void land_detector_update(land_detector_t *detector, const land_sensor_data_t *sensors, uint32_t dt_ms) {
    if (!sensors->is_landing_commanded) {
        detector->state = LAND_STATE_FLYING;
        detector->state_timer_ms = 0;
        detector->i_term_freeze = false;
        detector->disarm_request = false;
        return;
    }

    switch (detector->state) {
        case LAND_STATE_FLYING:
            detector->state = LAND_STATE_DESCENDING;
            detector->state_timer_ms = 0;
            detector->i_term_freeze = false;
            break;

        case LAND_STATE_DESCENDING:
            /* Перехід у зону екранного ефекту за даними висотоміра */
            if (sensors->alt_ground_relative <= 1.5f && sensors->alt_ground_relative > 0.0f) {
                detector->state = LAND_STATE_NEAR_GROUND;
                detector->state_timer_ms = 0;
                detector->i_term_freeze = true; /* Заморожуємо інтегратор кута для захисту від tip-over */
            }
            break;

        case LAND_STATE_NEAR_GROUND: {
            detector->i_term_freeze = true;

            /* Перевірка умов фізичного контакту з поверхнею */
            bool v_z_stopped = fabsf(sensors->v_z_filtered) < detector->cfg.v_z_stopped_thresh;
            bool throttle_low = sensors->throttle_out <= detector->cfg.throttle_min_limit;
            bool accel_shock = fabsf(sensors->accel_z_raw - 9.81f) > detector->cfg.accel_shock_thresh;
            bool current_dropped = (sensors->battery_current < (sensors->hover_current * detector->cfg.current_drop_ratio));

            if (throttle_low && (v_z_stopped || accel_shock || current_dropped)) {
                detector->state_timer_ms += dt_ms;
                if (detector->state_timer_ms >= detector->cfg.contact_time_ms) {
                    detector->state = LAND_STATE_GROUND_CONTACT;
                    detector->state_timer_ms = 0;
                }
            } else {
                detector->state_timer_ms = 0;
            }
            break;
        }

        case LAND_STATE_GROUND_CONTACT:
            detector->i_term_freeze = true;
            detector->state_timer_ms += dt_ms;

            /* Якщо апарат знову підкинуло вітром/газом - повернення на попередній стан */
            if (sensors->throttle_out > detector->cfg.throttle_min_limit * 1.5f ||
                sensors->v_z_filtered > detector->cfg.v_z_stopped_thresh * 2.0f) {
                detector->state = LAND_STATE_NEAR_GROUND;
                detector->state_timer_ms = 0;
                break;
            }

            if (detector->state_timer_ms >= detector->cfg.disarm_delay_ms) {
                detector->state = LAND_STATE_LANDED;
                detector->disarm_request = true;
            }
            break;

        case LAND_STATE_LANDED:
            detector->disarm_request = true;
            detector->i_term_freeze = true;
            break;
    }
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <algorithm>

enum class LandState : uint8_t {
    Flying = 0,
    Descending,
    NearGround,
    GroundContact,
    Landed
};

struct LandDetectorConfig {
    float v_z_descend_target   {-0.40f}; // м/с
    float v_z_stopped_thresh   { 0.15f}; // м/с
    float throttle_min_limit   { 0.12f}; // 0.0 .. 1.0
    float accel_shock_thresh   { 3.50f}; // м/с^2
    float current_drop_ratio   { 0.65f}; // частка від висіння
    uint32_t contact_time_ms   { 350};   // мс
    uint32_t disarm_delay_ms   { 500};   // мс
};

struct LandSensorData {
    float alt_ground_relative  {0.0f};
    float v_z_filtered         {0.0f};
    float throttle_out         {0.0f};
    float accel_z_raw          {9.81f};
    float battery_current      {0.0f};
    float hover_current        {15.0f};
    bool is_landing_commanded  {false};
};

class LandDetector {
public:
    explicit LandDetector(const LandDetectorConfig& config = LandDetectorConfig{})
        : cfg_{config} {}

    void update(const LandSensorData& sensors, uint32_t dt_ms) noexcept {
        if (!sensors.is_landing_commanded) {
            state_ = LandState::Flying;
            state_timer_ms_ = 0;
            i_term_freeze_ = false;
            disarm_request_ = false;
            return;
        }

        switch (state_) {
            case LandState::Flying:
                state_ = LandState::Descending;
                state_timer_ms_ = 0;
                i_term_freeze_ = false;
                break;

            case LandState::Descending:
                if (sensors.alt_ground_relative <= 1.5f && sensors.alt_ground_relative > 0.0f) {
                    state_ = LandState::NearGround;
                    state_timer_ms_ = 0;
                    i_term_freeze_ = true;
                }
                break;

            case LandState::NearGround: {
                i_term_freeze_ = true;
                const bool v_z_stopped = std::abs(sensors.v_z_filtered) < cfg_.v_z_stopped_thresh;
                const bool throttle_low = sensors.throttle_out <= cfg_.throttle_min_limit;
                const bool accel_shock = std::abs(sensors.accel_z_raw - 9.81f) > cfg_.accel_shock_thresh;
                const bool current_dropped = sensors.battery_current < (sensors.hover_current * cfg_.current_drop_ratio);

                if (throttle_low && (v_z_stopped || accel_shock || current_dropped)) {
                    state_timer_ms_ += dt_ms;
                    if (state_timer_ms_ >= cfg_.contact_time_ms) {
                        state_ = LandState::GroundContact;
                        state_timer_ms_ = 0;
                    }
                } else {
                    state_timer_ms_ = 0;
                }
                break;
            }

            case LandState::GroundContact:
                i_term_freeze_ = true;
                state_timer_ms_ += dt_ms;

                // Захист від помилкового детектування (порив вітру підкинув апарат)
                if (sensors.throttle_out > cfg_.throttle_min_limit * 1.5f ||
                    sensors.v_z_filtered > cfg_.v_z_stopped_thresh * 2.0f) {
                    state_ = LandState::NearGround;
                    state_timer_ms_ = 0;
                    break;
                }

                if (state_timer_ms_ >= cfg_.disarm_delay_ms) {
                    state_ = LandState::Landed;
                    disarm_request_ = true;
                }
                break;

            case LandState::Landed:
                disarm_request_ = true;
                i_term_freeze_ = true;
                break;
        }
    }

    [[nodiscard]] LandState state() const noexcept { return state_; }
    [[nodiscard]] bool should_freeze_i_term() const noexcept { return i_term_freeze_; }
    [[nodiscard]] bool should_disarm() const noexcept { return disarm_request_; }

private:
    LandState state_{LandState::Flying};
    uint32_t state_timer_ms_{0};
    bool i_term_freeze_{false};
    bool disarm_request_{false};
    LandDetectorConfig cfg_{};
};
```
:::

## 4. Аналіз крайових випадків та типові пастки

Під час практичної інтеграції детектора посадки розробники стикаються з трьома критичними крайовими ситуаціями:

### 1. Посадка на похилий схил (20°–30°)

Коли дрон торкається схилу однією опорою, корпус отримує постійний кутовий нахил. Якщо автомат не заморозив інтегральну складову (стан `NEAR_GROUND`), регулятор почне вирівнювати апарат за горизонтом, викручуючи нижній мотор на повну тягу. Це миттєво провокує перекидання та перекид апарата вниз по схилу.

Заморожування інтегратора та затискання максимальної тяги до `0.7 · T_hover` змушує дрон плавно прилягти всіма опорами на поверхню під силою власної ваги.

### 2. Вібраційний шум акселерометра від пошкоджених пропелерів

Якщо один із пропелерів має надщерблену кромку або втратив балансування, високочастотні вібрації на частоті обертання 100–150 Гц створюють амплітуду прискорення на рамі до `±6.0 м/с²`.

Якщо поріг `accel_shock_thresh` налаштований нижче `2.5 м/с²`, автомат зафіксує хибний удар об землю ще під час висіння на висоті кількох метрів.

Щоб запобігти цьому, алгоритм використовує комбіновану перевірку: сплеск акселерометра зараховується лише тоді, коли вихідний газ регулятора вже впав до нижньої межі (`throttle <= throttle_min_limit`).

### 3. Просідання напруги батареї наприкінці місії (Voltage Sag)

При поверненні на критично низькому заряді (Low Battery Failsafe) напруга акумулятора падає з 4.2 В до 3.3 В на банку. Для збереження тяги висіння польотний контролер змушений збільшувати шпаруватість ШІМ та споживаний струм.

Якщо поріг струму розвантаження задано як абсолютне число в амперах, детектор ніколи не зафіксує торкання, оскільки струм у висінні перевищив стандартне значення.

Тому поріг струму розраховується **адаптивно**: оцінювач фіксує середній струм висіння `hover_current` у перші 3–5 секунд після початку зниження й порівнює поточний струм як відносну частку `I_current / I_hover`.

### 4. Захисний таймаут примусового роззброєння (Failsafe Disarm)

Якщо апарат завис на гілках дерев, сів на високу густу траву або зачепився шасі за натягнутий канат, вертикальна швидкість може не обнулитися повністю, а газ не вийти в мінімум.

Для виходу з такого глухого кута детектор має вбудований аварійний таймер: якщо апарат перебуває в режимі посадки понад 12 секунд без фіксації контакту, автопілот плавно знижує газ до нуля зі швидкістю 15%/с і примусово виконує роззброєння моторів.
