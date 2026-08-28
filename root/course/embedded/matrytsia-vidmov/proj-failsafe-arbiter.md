# ⚙️ Програмний арбітр аварійних режимів та матриця рішень

Цей модуль реалізує детермінований арбітраж аварійних станів автопілота: він обробляє маску апаратних відмов, фільтрує перехідні процеси таймерами гістерезису та обирає найвищий за пріоритетом безпечний режим польоту.

Автопілот у кожному польотному такті (типово 50–250 Гц) отримує статус працездатності від десятка незалежних драйверів: радіоприймача, супутникового навігатора, модуля моніторингу батареї, сенсорів одометрії та регуляторів обертів. Якщо ці сигнали обробляти розрізненими блоками умовних переходів `if-else`, у системі неминуче виникають конфлікти та некерований брязкіт режимів (state flapping). Наприклад, при одночасній втраті радіосигналу та відмові GNSS незалежні обробники можуть одночасно вимагати повернення додому (RTL) та утримання висоти (AltHold).

Архітектурне вирішення полягає у розділенні виявлення несправностей і прийняття рішень. Стан підсистем кодується бітовою маскою, кожен тип несправності має свій часовий лічильник підтвердження (debounce timer), а фінальний вибір режиму здійснюється через таблицю пріоритетів, де критерій безпеки людей і збереження цілісності простору безумовно переважає збереження апарата.

## Структури даних та бітова маска стану

Працездатність підсистем описується бітовими прапорцями. Нульовий біт означає повну норму, встановлений біт — наявність аномалії або повної відмови відповідного каналу. Для збереження строгої типізації та підтримки різних парадигм програмування оголошення констант маски оформлюється у двох варіантах:

:::tabs
```c
#include <stdint.h>

#define FAULT_RC_LOST       (1u << 0)  // Втрата сигналу пульта керування
#define FAULT_GCS_LOST      (1u << 1)  // Втрата телеметрії наземної станції
#define FAULT_GNSS_GLITCH   (1u << 2)  // Стрибок HDOP / втрата 3D Fix
#define FAULT_BATT_LOW      (1u << 3)  // Перший поріг розряду (Warning)
#define FAULT_BATT_CRIT     (1u << 4)  // Критичний поріг розряду (Land)
#define FAULT_GEOFENCE      (1u << 5)  // Вихід за межі дозволеного радіуса/стелі
#define FAULT_ACTUATOR      (1u << 6)  // Відмова мотора, ESC або сервоприводу
#define FAULT_ATTITUDE_LOSS (1u << 7)  // Втрата розрахунку просторової орієнтації
```
```cpp
#include <cstdint>

namespace autopilot::failsafe {

enum class Fault : uint32_t {
    RcLost        = 1u << 0,  // Втрата сигналу пульта керування
    GcsLost       = 1u << 1,  // Втрата телеметрії наземної станції
    GnssGlitch    = 1u << 2,  // Стрибок HDOP / втрата 3D Fix
    BatteryLow    = 1u << 3,  // Перший поріг розряду (Warning)
    BatteryCrit   = 1u << 4,  // Критичний поріг розряду (Land)
    Geofence      = 1u << 5,  // Вихід за межі дозволеного радіуса/стелі
    ActuatorFail  = 1u << 6,  // Відмова мотора, ESC або сервоприводу
    AttitudeLoss  = 1u << 7   // Втрата розрахунку просторової орієнтації
};

constexpr uint32_t to_mask(Fault f) noexcept {
    return static_cast<uint32_t>(f);
}

} // namespace autopilot::failsafe
```
:::

Дії аварійного захисту ранжуються за рівнем обмеження польоту:

1. `ACTION_NONE` — штатний політ згідно з поточною командою оператора чи автопілота.
2. `ACTION_WARN_ONLY` — індикація на наземну станцію та звуковий сигнал без зміни режиму.
3. `ACTION_RTL` — автономне повернення на точку старту за записаною траєкторією (вимагає GNSS та запасу батареї).
4. `ACTION_LAND` — вертикальний контрольований спуск на поточному місці зі швидкістю 0.5–1.5 м/с.
5. `ACTION_ALTHOLD_SAFE` — перехід у режим стабілізації висоти за барометром і нейтралізації кутів нахилу.
6. `ACTION_TERMINATE` — негайне відсікання живлення приводів (Disarm) або викид рятувального парашута.

## Алгоритм часової фільтрації та підтвердження

Кожен сенсорний драйвер надсилає сирий бітовий прапорець аномалії. Проте рішення про активацію аварійного режиму приймається лише після підтвердження сталості збою. У таблиці таймерів для кожної відмови фіксується часова мітка початку події. Якщо аномалія триває довше сконфігурованого порогу `threshold_ms`, біт копіюється до маски підтверджених несправностей `confirmed_faults`.

Якщо сигнал відновлюється до закінчення інтервалу фільтрації, лічильник скидається в нуль, а прапорець у підтвердженій масці знімається. Такий підхід гарантує повний імунітет до високочастотних завад в ефірі та короткочасних просадок напруги під час різких маневрів.

## Реалізація модуля арбітражу на C та C++

У наведеному коді реалізовано повний конвеєр: прийом сирих прапорців, оновлення часових лічильників гістерезису, арбітраж суперечливих вимог та формування фінальної дії автопілота.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

// Коди дій аварійного автомата
typedef enum {
    FS_ACTION_NONE = 0,
    FS_ACTION_WARN,
    FS_ACTION_ALTHOLD,
    FS_ACTION_RTL,
    FS_ACTION_LAND,
    FS_ACTION_TERMINATE
} fs_action_t;

// Конфігураційні таймаути фільтрації несправностей (у мілісекундах)
typedef struct {
    uint32_t rc_timeout_ms;       // Типово 1500 мс
    uint32_t gcs_timeout_ms;      // Типово 5000 мс
    uint32_t gnss_timeout_ms;     // Типово 3000 мс
    uint32_t batt_debounce_ms;    // Типово 1000 мс
    uint32_t geofence_debounce_ms;// Типово 500 мс
} fs_config_t;

// Стан таймерів відмов
typedef struct {
    uint32_t rc_lost_start_ms;
    uint32_t gcs_lost_start_ms;
    uint32_t gnss_fail_start_ms;
    uint32_t batt_low_start_ms;
    uint32_t batt_crit_start_ms;
    uint32_t geofence_start_ms;
    uint32_t confirmed_faults;
    fs_action_t active_action;
} fs_state_t;

static void update_fault_timer(bool condition, uint32_t now_ms,
                               uint32_t *start_time, uint32_t threshold_ms,
                               uint32_t *fault_mask, uint32_t flag)
{
    if (condition) {
        if (*start_time == 0) {
            *start_time = now_ms; // Фіксація початку аномалії
        }
        if ((now_ms - *start_time) >= threshold_ms) {
            *fault_mask |= flag;  // Підтвердження стійкої відмови
        }
    } else {
        *start_time = 0;
        *fault_mask &= ~flag;     // Скидання при відновленні норми
    }
}

fs_action_t fs_arbiter_update(const fs_config_t *cfg, fs_state_t *st,
                              uint32_t raw_fault_flags, uint32_t now_ms)
{
    // 1. Оновлення та підтвердження таймерів для кожного типу збою
    update_fault_timer((raw_fault_flags & (1u << 0)) != 0, now_ms,
                       &st->rc_lost_start_ms, cfg->rc_timeout_ms,
                       &st->confirmed_faults, (1u << 0));

    update_fault_timer((raw_fault_flags & (1u << 1)) != 0, now_ms,
                       &st->gcs_lost_start_ms, cfg->gcs_timeout_ms,
                       &st->confirmed_faults, (1u << 1));

    update_fault_timer((raw_fault_flags & (1u << 2)) != 0, now_ms,
                       &st->gnss_fail_start_ms, cfg->gnss_timeout_ms,
                       &st->confirmed_faults, (1u << 2));

    update_fault_timer((raw_fault_flags & (1u << 3)) != 0, now_ms,
                       &st->batt_low_start_ms, cfg->batt_debounce_ms,
                       &st->confirmed_faults, (1u << 3));

    update_fault_timer((raw_fault_flags & (1u << 4)) != 0, now_ms,
                       &st->batt_crit_start_ms, cfg->batt_debounce_ms,
                       &st->confirmed_faults, (1u << 4));

    update_fault_timer((raw_fault_flags & (1u << 5)) != 0, now_ms,
                       &st->geofence_start_ms, cfg->geofence_debounce_ms,
                       &st->confirmed_faults, (1u << 5));

    // Апаратна відмова приводу або втрата орієнтації фіксується негайно
    if (raw_fault_flags & (1u << 6)) st->confirmed_faults |= (1u << 6);
    if (raw_fault_flags & (1u << 7)) st->confirmed_faults |= (1u << 7);

    uint32_t f = st->confirmed_faults;

    // 2. Дерево арбітражу пріоритетів (від найкритичнішого до м'якого)

    // Пріоритет 1: Катастрофічна втрата орієнтації
    if (f & (1u << 7)) {
        st->active_action = FS_ACTION_TERMINATE;
        return st->active_action;
    }

    // Пріоритет 2: Критичний розряд батареї
    if (f & (1u << 4)) {
        // Енергії на повернення немає: тільки негайна посадка на місці
        st->active_action = FS_ACTION_LAND;
        return st->active_action;
    }

    // Пріоритет 3: Порушення геозони
    if (f & (1u << 5)) {
        // Якщо GNSS працює, повертаємося додому або сідаємо на межі
        if (!(f & (1u << 2))) {
            st->active_action = FS_ACTION_RTL;
        } else {
            st->active_action = FS_ACTION_LAND;
        }
        return st->active_action;
    }

    // Пріоритет 4: Втрата зв'язку керування (RC Lost)
    if (f & (1u << 0)) {
        // Є супутники — безпечне повернення
        if (!(f & (1u << 2))) {
            st->active_action = FS_ACTION_RTL;
        } else {
            // Без супутників RTL неможливий — перехід на спуск або AltHold
            st->active_action = FS_ACTION_LAND;
        }
        return st->active_action;
    }

    // Пріоритет 5: Одиночна втрата GNSS при наявному зв'язку
    if (f & (1u << 2)) {
        // Залишаємося в утриманні висоти для передачі ручного контролю
        st->active_action = FS_ACTION_ALTHOLD;
        return st->active_action;
    }

    // Пріоритет 6: Попереджувальний поріг батареї
    if (f & (1u << 3)) {
        st->active_action = (!(f & (1u << 2))) ? FS_ACTION_RTL : FS_ACTION_LAND;
        return st->active_action;
    }

    st->active_action = FS_ACTION_NONE;
    return st->active_action;
}
```
```cpp
#include <cstdint>
#include <chrono>
#include <span>

namespace autopilot::failsafe {

enum class Action : uint8_t {
    None = 0,
    Warn,
    AltHold,
    ReturnToLaunch,
    Land,
    Terminate
};

struct Config {
    std::chrono::milliseconds rc_timeout{1500};
    std::chrono::milliseconds gcs_timeout{5000};
    std::chrono::milliseconds gnss_timeout{3000};
    std::chrono::milliseconds batt_debounce{1000};
    std::chrono::milliseconds geofence_debounce{500};
};

class DebounceTimer {
public:
    void update(bool condition, std::chrono::milliseconds now,
                std::chrono::milliseconds threshold, uint32_t& mask, Fault fault) noexcept
    {
        const uint32_t flag = to_mask(fault);
        if (condition) {
            if (start_time_.count() == 0) {
                start_time_ = now;
            }
            if ((now - start_time_) >= threshold) {
                mask |= flag;
            }
        } else {
            start_time_ = std::chrono::milliseconds{0};
            mask &= ~flag;
        }
    }

private:
    std::chrono::milliseconds start_time_{0};
};

class Arbiter {
public:
    explicit constexpr Arbiter(Config cfg) noexcept : cfg_(cfg) {}

    [[nodiscard]] Action evaluate(uint32_t raw_faults, std::chrono::milliseconds now) noexcept {
        // Оновлення таймерів гістерезису
        rc_timer_.update((raw_faults & to_mask(Fault::RcLost)) != 0, now, cfg_.rc_timeout, confirmed_mask_, Fault::RcLost);
        gcs_timer_.update((raw_faults & to_mask(Fault::GcsLost)) != 0, now, cfg_.gcs_timeout, confirmed_mask_, Fault::GcsLost);
        gnss_timer_.update((raw_faults & to_mask(Fault::GnssGlitch)) != 0, now, cfg_.gnss_timeout, confirmed_mask_, Fault::GnssGlitch);
        batt_low_timer_.update((raw_faults & to_mask(Fault::BatteryLow)) != 0, now, cfg_.batt_debounce, confirmed_mask_, Fault::BatteryLow);
        batt_crit_timer_.update((raw_faults & to_mask(Fault::BatteryCrit)) != 0, now, cfg_.batt_debounce, confirmed_mask_, Fault::BatteryCrit);
        fence_timer_.update((raw_faults & to_mask(Fault::Geofence)) != 0, now, cfg_.geofence_debounce, confirmed_mask_, Fault::Geofence);

        if (raw_faults & to_mask(Fault::ActuatorFail)) confirmed_mask_ |= to_mask(Fault::ActuatorFail);
        if (raw_faults & to_mask(Fault::AttitudeLoss)) confirmed_mask_ |= to_mask(Fault::AttitudeLoss);

        return resolve_conflicts();
    }

    [[nodiscard]] uint32_t confirmed_faults() const noexcept { return confirmed_mask_; }

private:
    [[nodiscard]] bool has_fault(Fault f) const noexcept {
        return (confirmed_mask_ & to_mask(f)) != 0;
    }

    [[nodiscard]] Action resolve_conflicts() noexcept {
        if (has_fault(Fault::AttitudeLoss)) {
            return Action::Terminate;
        }
        if (has_fault(Fault::BatteryCrit)) {
            return Action::Land;
        }
        if (has_fault(Fault::Geofence)) {
            return has_fault(Fault::GnssGlitch) ? Action::Land : Action::ReturnToLaunch;
        }
        if (has_fault(Fault::RcLost)) {
            return has_fault(Fault::GnssGlitch) ? Action::Land : Action::ReturnToLaunch;
        }
        if (has_fault(Fault::GnssGlitch)) {
            return Action::AltHold;
        }
        if (has_fault(Fault::BatteryLow)) {
            return has_fault(Fault::GnssGlitch) ? Action::Land : Action::ReturnToLaunch;
        }
        return Action::None;
    }

    Config cfg_;
    uint32_t confirmed_mask_{0};
    DebounceTimer rc_timer_;
    DebounceTimer gcs_timer_;
    DebounceTimer gnss_timer_;
    DebounceTimer batt_low_timer_;
    DebounceTimer batt_crit_timer_;
    DebounceTimer fence_timer_;
};

} // namespace autopilot::failsafe
```
:::

## Інтеграція в операційну систему реального часу (RTOS)

У багатозадачних системах на базі FreeRTOS або Zephyr RTOS підсистема Failsafe виконується як окремий потік із середнім рівнем пріоритету (наприклад, нижче за контур стабілізації IMU на 1 кГц, але вище за потік MAVLink-телеметрії на 50 Гц).

Драйвери периферії не викликають функцію арбітражу безпосередньо з обробників переривань ISR. Замість цього вони встановлюють атомарні бітові прапорці у системній групі подій (Event Group) або надсилають повідомлення у неблокувальну чергу. Потік аварійного автомата прокидається з фіксованим періодом (наприклад, кожні 20 мс / 50 Гц), зчитує знімок усіх сенсорних статусів, оновлює таймери та генерує команду зміни польотного режиму для головного диспетчера польотів (Flight Mode Manager).

Така ізоляція виключає блокування критичних обчислювальних задач оцінки просторової орієнтації (Attitude Estimation Task) та гарантує детермінований час виконання кожної ітерації арбітражу, що не перевищує 5–10 мікросекунд на 32-бітному мікроконтролері з ядром ARM Cortex-M4/M7.

## Інваріанти, тестування та крайові випадки

Під час розробки та валідації модуля арбітражу вбудованого ПЗ дотримуються таких фундаментальних правил:

1. **Одностороннє підвищення суворості дії (Latching)**: якщо підсистема перейшла в стан `FS_ACTION_LAND` через критичний розряд батареї, а потім напруга на кілька мілівольт піднялася через зменшення швидкості зниження, автомат не має права самовільно повертатися в `FS_ACTION_NONE` або `FS_ACTION_RTL`. Вихід з аварійного стану можливий лише за явною командою оператора з пульта або після посадки та зняття з охорони (Disarm).
2. **Атомарність читання маски несправностей**: оскільки оновлення даних від радіоприймача відбувається в перериванні UART/SPI, а розрахунок EKF — у високопріоритетній задачі RTOS, формування вхідної бітової маски має виконуватися через атомарні операції або м'ютекс із захистом від інверсії пріоритетів.
3. **Поведінка при одночасному запуску та відновленні живлення**: під час старту прошивки маска `confirmed_faults` ініціалізується нулями, проте таймери відліку починають працювати лише після завершення фази калібрування сенсорів (Sensor Preflight Calibration). Якщо змусити арбітр оцінювати стан до завершення ініціалізації GNSS, автопілот негайно заблокує старт через помилкову відмову навігації.
4. **Обмеження швидкості зміни аварійного стану**: між послідовними змінами вихідної дії арбітра встановлюється мінімальний квант часу (типово 500 мс), що виключає передачу суперечливих команд у контури PID-регуляторів і запобігає динамічним ударам по силовій установці.
5. **Повне матричне покриття модульними тестами (Unit Testing)**: оскільки арбітр не має прихованого стану окрім зафіксованих таймерів, він піддається вичерпному автоматизованому тестуванню на хост-машині. Тестовий стенд генерує всі 256 можливих комбінацій вхідної 8-бітної маски несправностей і перевіряє точну відповідність вихідної дії затвердженій таблиці ієрархії пріоритетів.
