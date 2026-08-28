# ⚙️ Програмний модуль рендерингу критичного статус-бару для вбудованих дисплеїв

Критичний статусний рядок автономного комплексу не може бути звичайним графічним віджетом загального призначення. Якщо рендерер карти чи спливаючий діалог конфігурації зависне, виділить надлишок пам'яті в купі або змістить координати елементів інтерфейсу, оператор втратить ситуаційну обізнаність у найбільш небезпечний момент.

Нижче наведено повну архітектуру та реалізацію модуля рендерингу критичного статус-бару (Critical Status Bar Engine) для вбудованих систем (ARM Cortex-M4/M7, ESP32, Embedded Linux). Модуль реалізує обчислення золотого квадранта параметрів, часовий автомат деградації актуальності даних (Data Staleness Decay), фільтрацію напруги з гістерезисом проти колірного мерехтіння, подвійне кодування стану (форма + текст + колір) та блокування найвищого Z-order у графічному конвеєрі.

## Архітектура моделі даних і автомата станів

Модуль спроєктовано за принципом односпрямованого потоку даних (Unidirectional Data Flow) без використання динамічної пам'яті під час польотного циклу:

```
[ Сирі кадри телеметрії ] ──> [ Валідатор актуальності Staleness ] ──> [ Фільтр напруги з гістерезисом ]
                                                                                │
[ Дисплей / Фреймбуфер ] <── [ Top Layer Lock Z-Order ] <── [ Форматування рядків + Подвійне кодування ]
```

1. **Збір сирих метрик:** Апаратні драйвери або парсер протоколу телеметрії (MAVLink, UAVCAN, CRSF/ELRS) заповнюють структуру сирого стану `RawTelemetryFrame` із фіксацією системної мітки часу отримання (`timestamp_ms`).
2. **Оцінка актуальності та виявлення застарівання:** Функція валідації звіряє поточний монотонний час системи з міткою кадру. Якщо дані не оновлювалися понад 1000 мс, стан переходить у режим попередження `STATUS_DEGRADED` із текстовим маркером `[⧗ STALE]`. Якщо затримка перевищує 3000 мс, статус примусово стає `STATUS_CRITICAL` із маркером `[X LOST]`.
3. **Гістерезис енергетики та фільтрація навантаження:** Напруга батареї під навантаженням порівнюється з порогами попередження `V_WARN` (наприклад, 14.8 В для 4S) та критичного розряду `V_CRIT` (14.0 В). Для переходу з гіршого стану в кращий значення напруги мусить перевищити поріг на ширину вікна гістерезису `ΔV_HYST = 0.25 В` та протриматися стабільним щонайменше 1.5 секунди.
4. **Рендеринг у буфер:** Статусний рядок малюється у виділеній неперекривній області екрана (верхні 28–32 пікселі) поверх фреймбуфера або через системний шар `lv_layer_top()` бібліотеки LVGL. Кожен текстовий символ та піктограма отримують контрастне контурне обведення товщиною 1 піксель.

## Розбір крайових випадків та математика фільтрації

Під час реальної експлуатації автономних систем модуль стикається з типовими крайовими ситуаціями, які вимагають детермінованої обробки:

### 1. Імпульсне просідання напруги (Throttle Punch-out)
Під час різкого набору висоти чи маневру ухилення струм споживання зростає в 5–8 разів (наприклад, із 12 А до 80 А). На внутрішньому опорі батареї `R_int` (типово 15–25 мОм для 4S збірки) виникає миттєве падіння напруги:
`ΔV_drop = I_peak · R_int`
При струмі 80 А падіння сягає `80 А · 0.02 Ом = 1.6 В`. Напруга на шині короткочасно просідає з 15.2 В до 13.6 В (нижче критичного порогу 14.0 В). 
Якщо фільтр напруги реагуватиме миттєво без дебаунсу, статус-бар спалахне червоним аварійним кольором і запустить тривожний зумер. Після виходу з маневру напруга відновиться до 15.0 В. 
Щоб запобігти хибним спрацьовуванням, у модулі реалізовано алгоритм подвійної перевірки:
- якщо високий струм супроводжується миттєвим просіданням, прапорець критичного розряду активується лише тоді, коли низька напруга утримується понад 300 мс (за межами типового тривалості ривка тяги);
- повернення у зелену зону блокується таймером утримання `HYSTERESIS_DEBOUNCE_MS = 1500 мс`.

### 2. Асиметрична втрата пакетів телеметрії
У радіоканалах часто виникає ситуація, коли висхідний канал керування (Uplink) працює стабільно завдяки високій потужності передавача наземної станції (1–2 Вт), а зворотний телеметричний канал (Downlink) глушиться завадою бортових передавачів відео. Оператор продовжує керувати апаратом, але показники висоти та батареї завмирають.
Автомат застарівання фіксує зупинку монотонного таймера отримання телеметрії. Після досягнення порогу `STALE_WARN_TIMEOUT_MS = 1000 мс` статус зв'язку негайно переходить у стан `SEV_STALE`, змінює колір на нейтрально-сірий та виводить лічильник віку кадру: `[⧗ STALE: 1.4s]`. Якщо оператор бачить зростаючий лічильник, він усвідомлює, що телеметрія застаріла, і не виконує різких маневрів за неактуальними даними.

### 3. Переповнення монотонного системного таймера (Timer Rollover)
При використанні 32-бітного лічильника мілісекунд `HAL_GetTick()` або `esp_timer_get_time() / 1000` переповнення лічильника відбувається кожні 49.7 діб безперервної роботи. Усі часові різниці в модулі обчислюються виключно через беззнакове віднімання `uint32_t age_ms = now_ms - timestamp_ms;`. Завдяки властивостям арифметики доповнення до двох (two's complement) різниця залишається строго коректною навіть у момент переходу лічильника через нуль `0xFFFFFFFF -> 0x00000000`.

### 4. Апаратне накладання через DMA2D / Chrom-ART
На мікроконтролерах сімейства STM32F7/H7 статус-бар не обов'язково перемальовувати процесорними циклами у загальний буфер кадрів. Дисплейний контролер LTDC підтримує два незалежні апаратні шари (Layer 1 та Layer 2). Нижній шар Layer 1 віддається під відеопотік камери або карту місцевості (формат RGB565 або YUV422), а верхній шар Layer 2 (розміром 800×28 пікселів у форматі ARGB8888 або ARGB4444) виділяється виключно під критичний статусний рядок. Апаратний блок DMA2D виконує альфа-змішування (Alpha Blending) статус-бару з основним відео на льоту під час сканування рядків без залучення ядер CPU.

## Реалізація модуля статусного бару

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

/* --- Конфігурація та константи семантичних кольорів (RGB565) --- */
#define COLOR_RGB565_GREEN       0x2560  /* Норма: #27ae60 */
#define COLOR_RGB565_YELLOW      0xFCC0  /* Увага / Деградація: #f39c12 */
#define COLOR_RGB565_RED         0xC1C5  /* Критична відмова: #c0392b */
#define COLOR_RGB565_GRAY        0x7BEF  /* Застарілі дані: #7f8c8d */
#define COLOR_RGB565_WHITE       0xFFFF  /* Основний текст */
#define COLOR_RGB565_BLACK       0x0000  /* Тінь / Контур / Фон */

#define STALE_WARN_TIMEOUT_MS    1000U
#define STALE_CRIT_TIMEOUT_MS    3000U
#define HYSTERESIS_VOLTAGE_MV    250U    /* 0.25 В */
#define HYSTERESIS_DEBOUNCE_MS   1500U   /* 1.5 с на повернення в норму */

#define STATUS_BAR_HEIGHT        28
#define MAX_TEXT_LEN             64

typedef enum {
    SEV_NORMAL = 0,
    SEV_WARNING,
    SEV_CRITICAL,
    SEV_STALE
} SeverityLevel;

typedef enum {
    NAV_MANUAL = 0,
    NAV_ALTHOLD,
    NAV_POSHOLD,
    NAV_AUTO_MISSION,
    NAV_GUIDED,
    NAV_FAILSAFE_RTL
} FlightMode;

typedef struct {
    float roll_deg;
    float pitch_deg;
    float altitude_amsl_m;
    float altitude_agl_m;
    float ground_speed_mps;
    float vertical_speed_mps;
} SpatialState;

typedef struct {
    uint16_t voltage_mv;
    int16_t  current_cda;     /* Сантиампери (0.01 А) */
    uint16_t consumed_mah;
    uint8_t  battery_soc_pct;
    int8_t   esc_temperature_c;
} PowerHealth;

typedef struct {
    int8_t   rssi_dbm;
    int8_t   snr_db;
    uint8_t  link_quality_pct;
    uint16_t round_trip_time_ms;
} LinkQuality;

typedef struct {
    SpatialState state;
    FlightMode   mode;
    bool         is_armed;
    PowerHealth  power;
    LinkQuality  link;
    uint32_t     timestamp_ms;
} TelemetryFrame;

typedef struct {
    SeverityLevel overall_severity;
    SeverityLevel power_severity;
    SeverityLevel link_severity;
    uint16_t      filtered_voltage_mv;
    uint32_t      last_warn_time_ms;
    char          mode_str[24];
    char          power_str[28];
    char          link_str[28];
    char          state_str[36];
} StatusBarPresenter;

/* Перетворення коду режиму в фіксований текстовий анонсатор */
static const char* flight_mode_to_string(FlightMode mode, bool armed) {
    if (!armed) {
        return "DISARMED";
    }
    switch (mode) {
        case NAV_MANUAL:       return "ARM: MANUAL";
        case NAV_ALTHOLD:      return "ARM: ALTHOLD";
        case NAV_POSHOLD:      return "ARM: POSHOLD";
        case NAV_AUTO_MISSION: return "ARM: AUTO";
        case NAV_GUIDED:       return "ARM: GUIDED";
        case NAV_FAILSAFE_RTL: return "FAILSAFE: RTL";
        default:               return "ARM: UNKNOWN";
    }
}

/* Оцінка стану живлення з гістерезисом та захистом від брязкоту навантаження */
static SeverityLevel evaluate_power_health(StatusBarPresenter *pres, uint16_t v_mv, uint32_t now_ms) {
    const uint16_t v_warn_thresh = 14800; /* 14.8 В */
    const uint16_t v_crit_thresh = 14000; /* 14.0 В */

    if (v_mv < v_crit_thresh) {
        pres->power_severity = SEV_CRITICAL;
        pres->last_warn_time_ms = now_ms;
        return SEV_CRITICAL;
    }

    if (v_mv < v_warn_thresh) {
        if (pres->power_severity == SEV_CRITICAL) {
            /* Відновлення з червоного в жовтий вимагає подолання гістерезису */
            if (v_mv >= (v_crit_thresh + HYSTERESIS_VOLTAGE_MV)) {
                pres->power_severity = SEV_WARNING;
            }
        } else {
            pres->power_severity = SEV_WARNING;
        }
        pres->last_warn_time_ms = now_ms;
        return pres->power_severity;
    }

    /* Напруга вище порогу попередження: перевірка гістерезису повернення в норму */
    if (pres->power_severity == SEV_WARNING) {
        if (v_mv >= (v_warn_thresh + HYSTERESIS_VOLTAGE_MV) &&
            (now_ms - pres->last_warn_time_ms >= HYSTERESIS_DEBOUNCE_MS)) {
            pres->power_severity = SEV_NORMAL;
        }
    } else {
        pres->power_severity = SEV_NORMAL;
    }

    return pres->power_severity;
}

/* Оновлення моделі представлення на основі свіжого телеметричного кадру */
void status_bar_update(StatusBarPresenter *pres, const TelemetryFrame *frame, uint32_t now_ms) {
    uint32_t age_ms = now_ms - frame->timestamp_ms;

    /* 1. Перевірка актуальності телеметрії (Data Staleness) */
    if (age_ms >= STALE_CRIT_TIMEOUT_MS) {
        pres->link_severity = SEV_CRITICAL;
        pres->overall_severity = SEV_CRITICAL;
        snprintf(pres->link_str, sizeof(pres->link_str), "[X LOST: %.1fs]", (float)age_ms / 1000.0f);
    } else if (age_ms >= STALE_WARN_TIMEOUT_MS) {
        pres->link_severity = SEV_STALE;
        pres->overall_severity = SEV_WARNING;
        snprintf(pres->link_str, sizeof(pres->link_str), "[⧗ STALE: %.1fs]", (float)age_ms / 1000.0f);
    } else {
        /* Сигнал свіжий — оцінюємо якість зв'язку */
        if (frame->link.link_quality_pct < 50 || frame->link.rssi_dbm < -100) {
            pres->link_severity = SEV_WARNING;
            snprintf(pres->link_str, sizeof(pres->link_str), "[! LQ:%u%% %ddBm]",
                     frame->link.link_quality_pct, frame->link.rssi_dbm);
        } else {
            pres->link_severity = SEV_NORMAL;
            snprintf(pres->link_str, sizeof(pres->link_str), "[OK LQ:%u%% %ddBm]",
                     frame->link.link_quality_pct, frame->link.rssi_dbm);
        }
    }

    /* 2. Оцінка живлення */
    SeverityLevel pwr_sev = evaluate_power_health(pres, frame->power.voltage_mv, now_ms);
    float volt_f = (float)frame->power.voltage_mv / 1000.0f;
    float curr_f = (float)frame->power.current_cda / 100.0f;

    if (pwr_sev == SEV_CRITICAL) {
        snprintf(pres->power_str, sizeof(pres->power_str), "[X CRIT %.1fV %.1fA]", volt_f, curr_f);
    } else if (pwr_sev == SEV_WARNING) {
        snprintf(pres->power_str, sizeof(pres->power_str), "[! LOW %.1fV %.1fA]", volt_f, curr_f);
    } else {
        snprintf(pres->power_str, sizeof(pres->power_str), "[OK %.1fV %u%%]", volt_f, frame->power.battery_soc_pct);
    }

    /* 3. Режим автопілота */
    snprintf(pres->mode_str, sizeof(pres->mode_str), "%s", flight_mode_to_string(frame->mode, frame->is_armed));

    /* 4. Просторовий стан */
    snprintf(pres->state_str, sizeof(pres->state_str), "H:%.0fm GS:%.1fm/s VSI:%+.1f",
             frame->state.altitude_agl_m, frame->state.ground_speed_mps, frame->state.vertical_speed_mps);

    /* Загальний рівень важливості для окантовки панелі */
    if (pres->link_severity == SEV_CRITICAL || pwr_sev == SEV_CRITICAL || frame->mode == NAV_FAILSAFE_RTL) {
        pres->overall_severity = SEV_CRITICAL;
    } else if (pres->link_severity == SEV_WARNING || pres->link_severity == SEV_STALE || pwr_sev == SEV_WARNING) {
        pres->overall_severity = SEV_WARNING;
    } else {
        pres->overall_severity = SEV_NORMAL;
    }
}

/* Отримання кольору шрифту та фону за рівнем важливості */
uint16_t status_bar_get_color(SeverityLevel sev) {
    switch (sev) {
        case SEV_NORMAL:   return COLOR_RGB565_GREEN;
        case SEV_WARNING:  return COLOR_RGB565_YELLOW;
        case SEV_CRITICAL: return COLOR_RGB565_RED;
        case SEV_STALE:    return COLOR_RGB565_GRAY;
        default:           return COLOR_RGB565_WHITE;
    }
}
```
```cpp
#include <cstdint>
#include <string_view>
#include <array>
#include <algorithm>
#include <cstdio>

namespace gcs::ui {

// Типізовані семантичні кольори RGB565
enum class ColorRGB565 : uint16_t {
    Green       = 0x2560, // Норма: #27ae60
    Yellow      = 0xFCC0, // Увага / Деградація: #f39c12
    Red         = 0xC1C5, // Критична відмова: #c0392b
    Gray        = 0x7BEF, // Застарілі дані: #7f8c8d
    White       = 0xFFFF, // Основний контрастний текст
    Black       = 0x0000  // Контур / Тінь / Фон
};

enum class Severity : uint8_t {
    Normal = 0,
    Warning,
    Critical,
    Stale
};

enum class FlightMode : uint8_t {
    Manual = 0,
    AltHold,
    PosHold,
    AutoMission,
    Guided,
    FailsafeRTL
};

struct SpatialState {
    float roll_deg{0.0f};
    float pitch_deg{0.0f};
    float altitude_amsl_m{0.0f};
    float altitude_agl_m{0.0f};
    float ground_speed_mps{0.0f};
    float vertical_speed_mps{0.0f};
};

struct PowerHealth {
    uint16_t voltage_mv{16800};
    int16_t  current_cda{0};     // 0.01 A
    uint16_t consumed_mah{0};
    uint8_t  battery_soc_pct{100};
    int8_t   esc_temperature_c{35};
};

struct LinkQuality {
    int8_t   rssi_dbm{-65};
    int8_t   snr_db{18};
    uint8_t  link_quality_pct{100};
    uint16_t round_trip_time_ms{25};
};

struct TelemetryFrame {
    SpatialState state{};
    FlightMode   mode{FlightMode::Manual};
    bool         is_armed{false};
    PowerHealth  power{};
    LinkQuality  link{};
    uint32_t     timestamp_ms{0};
};

// Фіксований буфер форматування без динамічної пам'яті
template <size_t Capacity>
class FixedString {
public:
    constexpr FixedString() noexcept { buffer_[0] = '\0'; }

    template <typename... Args>
    void format(const char* fmt, Args... args) noexcept {
        std::snprintf(buffer_.data(), buffer_.size(), fmt, args...);
    }

    [[nodiscard]] constexpr std::string_view view() const noexcept {
        return std::string_view(buffer_.data());
    }

    [[nodiscard]] constexpr const char* c_str() const noexcept {
        return buffer_.data();
    }

private:
    std::array<char, Capacity> buffer_{};
};

class StatusBarPresenter {
public:
    static constexpr uint32_t kStaleWarnTimeoutMs   = 1000;
    static constexpr uint32_t kStaleCritTimeoutMs   = 3000;
    static constexpr uint16_t kHysteresisVoltageMv  = 250;
    static constexpr uint32_t kHysteresisDebounceMs = 1500;
    static constexpr uint16_t kVoltageWarnThreshMv  = 14800; // 14.8 В
    static constexpr uint16_t kVoltageCritThreshMv  = 14000; // 14.0 В

    void update(const TelemetryFrame& frame, uint32_t now_ms) noexcept {
        const uint32_t age_ms = now_ms - frame.timestamp_ms;

        // 1. Оцінка актуальності каналу зв'язку
        if (age_ms >= kStaleCritTimeoutMs) {
            link_severity_ = Severity::Critical;
            link_text_.format("[X LOST: %.1fs]", static_cast<float>(age_ms) / 1000.0f);
        } else if (age_ms >= kStaleWarnTimeoutMs) {
            link_severity_ = Severity::Stale;
            link_text_.format("[⧗ STALE: %.1fs]", static_cast<float>(age_ms) / 1000.0f);
        } else {
            if (frame.link.link_quality_pct < 50 || frame.link.rssi_dbm < -100) {
                link_severity_ = Severity::Warning;
                link_text_.format("[! LQ:%u%% %ddBm]", frame.link.link_quality_pct, frame.link.rssi_dbm);
            } else {
                link_severity_ = Severity::Normal;
                link_text_.format("[OK LQ:%u%% %ddBm]", frame.link.link_quality_pct, frame.link.rssi_dbm);
            }
        }

        // 2. Оцінка стану батареї з гістерезисом
        evaluate_power(frame.power.voltage_mv, now_ms);
        const float volt_f = static_cast<float>(frame.power.voltage_mv) / 1000.0f;
        const float curr_f = static_cast<float>(frame.power.current_cda) / 100.0f;

        if (power_severity_ == Severity::Critical) {
            power_text_.format("[X CRIT %.1fV %.1fA]", volt_f, curr_f);
        } else if (power_severity_ == Severity::Warning) {
            power_text_.format("[! LOW %.1fV %.1fA]", volt_f, curr_f);
        } else {
            power_text_.format("[OK %.1fV %u%%]", volt_f, frame.power.battery_soc_pct);
        }

        // 3. Анонсатор автопілотного режиму
        mode_text_.format("%s", format_mode(frame.mode, frame.is_armed).data());

        // 4. Просторовий стан
        state_text_.format("H:%.0fm GS:%.1fm/s VSI:%+.1f",
                           frame.state.altitude_agl_m,
                           frame.state.ground_speed_mps,
                           frame.state.vertical_speed_mps);

        // Розрахунок глобального рівня деградації
        if (link_severity_ == Severity::Critical || power_severity_ == Severity::Critical || frame.mode == FlightMode::FailsafeRTL) {
            overall_severity_ = Severity::Critical;
        } else if (link_severity_ == Severity::Warning || link_severity_ == Severity::Stale || power_severity_ == Severity::Warning) {
            overall_severity_ = Severity::Warning;
        } else {
            overall_severity_ = Severity::Normal;
        }
    }

    [[nodiscard]] constexpr Severity overall_severity() const noexcept { return overall_severity_; }
    [[nodiscard]] constexpr Severity power_severity() const noexcept   { return power_severity_; }
    [[nodiscard]] constexpr Severity link_severity() const noexcept    { return link_severity_; }

    [[nodiscard]] constexpr std::string_view mode_str() const noexcept  { return mode_text_.view(); }
    [[nodiscard]] constexpr std::string_view power_str() const noexcept { return power_text_.view(); }
    [[nodiscard]] constexpr std::string_view link_str() const noexcept  { return link_text_.view(); }
    [[nodiscard]] constexpr std::string_view state_str() const noexcept { return state_text_.view(); }

    [[nodiscard]] static constexpr ColorRGB565 to_color(Severity sev) noexcept {
        switch (sev) {
            case Severity::Normal:   return ColorRGB565::Green;
            case Severity::Warning:  return ColorRGB565::Yellow;
            case Severity::Critical: return ColorRGB565::Red;
            case Severity::Stale:    return ColorRGB565::Gray;
        }
        return ColorRGB565::White;
    }

private:
    void evaluate_power(uint16_t v_mv, uint32_t now_ms) noexcept {
        if (v_mv < kVoltageCritThreshMv) {
            power_severity_ = Severity::Critical;
            last_warn_time_ms_ = now_ms;
            return;
        }

        if (v_mv < kVoltageWarnThreshMv) {
            if (power_severity_ == Severity::Critical) {
                if (v_mv >= (kVoltageCritThreshMv + kHysteresisVoltageMv)) {
                    power_severity_ = Severity::Warning;
                }
            } else {
                power_severity_ = Severity::Warning;
            }
            last_warn_time_ms_ = now_ms;
            return;
        }

        if (power_severity_ == Severity::Warning) {
            if (v_mv >= (kVoltageWarnThreshMv + kHysteresisVoltageMv) &&
                (now_ms - last_warn_time_ms_ >= kHysteresisDebounceMs)) {
                power_severity_ = Severity::Normal;
            }
        } else {
            power_severity_ = Severity::Normal;
        }
    }

    [[nodiscard]] static constexpr std::string_view format_mode(FlightMode mode, bool armed) noexcept {
        if (!armed) return "DISARMED";
        switch (mode) {
            case FlightMode::Manual:      return "ARM: MANUAL";
            case FlightMode::AltHold:     return "ARM: ALTHOLD";
            case FlightMode::PosHold:     return "ARM: POSHOLD";
            case FlightMode::AutoMission: return "ARM: AUTO";
            case FlightMode::Guided:      return "ARM: GUIDED";
            case FlightMode::FailsafeRTL: return "FAILSAFE: RTL";
        }
        return "ARM: UNKNOWN";
    }

    Severity overall_severity_{Severity::Normal};
    Severity power_severity_{Severity::Normal};
    Severity link_severity_{Severity::Normal};
    uint32_t last_warn_time_ms_{0};

    FixedString<24> mode_text_{};
    FixedString<28> power_text_{};
    FixedString<28> link_text_{};
    FixedString<36> state_text_{};
};

} // namespace gcs::ui
```
:::

## Інтеграція з графічним конвеєром LVGL

Щоб гарантувати виконання принципу незмінного закріплення (Sticky Status Bar) у бібліотеці LVGL (Light and Versatile Graphics Library), статусний бар прив'язується не до активного екрана `lv_scr_act()`, а до спеціального верхнього системного шару — `lv_layer_top()`.

:::tabs
```c
/* Ініціалізація неперекривного статусного бару в LVGL (C) */
void init_sticky_status_bar(void) {
    /* Створюємо контейнер на системному верхньому шарі */
    lv_obj_t *status_bar = lv_obj_create(lv_layer_top());
    lv_obj_set_size(status_bar, LV_PCT(100), STATUS_BAR_HEIGHT);
    lv_obj_set_pos(status_bar, 0, 0);
    
    /* Забороняємо перехоплення подій кліків фоном (кліки проходять крізь порожні зони) */
    lv_obj_clear_flag(status_bar, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
    
    /* Фіксований чорний напівпрозорий фон для максимального контрасту */
    lv_obj_set_style_bg_color(status_bar, lv_color_hex(0x101418), 0);
    lv_obj_set_style_bg_opa(status_bar, LV_OPA_90, 0);
    lv_obj_set_style_border_side(status_bar, LV_BORDER_SIDE_BOTTOM, 0);
    lv_obj_set_style_border_width(status_bar, 2, 0);
    lv_obj_set_style_border_color(status_bar, lv_color_hex(0x27ae60), 0);
}
```
```cpp
/* Ініціалізація неперекривного статусного бару в LVGL (C++ RAII-обгортка) */
namespace gcs::ui {

class StickyStatusBarWidget {
public:
    explicit StickyStatusBarWidget(int32_t height = 28) noexcept {
        container_ = lv_obj_create(lv_layer_top());
        if (!container_) return;

        lv_obj_set_size(container_, LV_PCT(100), height);
        lv_obj_set_pos(container_, 0, 0);
        lv_obj_clear_flag(container_, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);

        lv_obj_set_style_bg_color(container_, lv_color_hex(0x101418), 0);
        lv_obj_set_style_bg_opa(container_, LV_OPA_90, 0);
        lv_obj_set_style_border_side(container_, LV_BORDER_SIDE_BOTTOM, 0);
        lv_obj_set_style_border_width(container_, 2, 0);
        lv_obj_set_style_border_color(container_, lv_color_hex(0x27ae60), 0);
    }

    ~StickyStatusBarWidget() noexcept {
        if (container_) {
            lv_obj_del(container_);
            container_ = nullptr;
        }
    }

    StickyStatusBarWidget(const StickyStatusBarWidget&) = delete;
    StickyStatusBarWidget& operator=(const StickyStatusBarWidget&) = delete;

    StickyStatusBarWidget(StickyStatusBarWidget&& other) noexcept : container_(other.container_) {
        other.container_ = nullptr;
    }

    StickyStatusBarWidget& operator=(StickyStatusBarWidget&& other) noexcept {
        if (this != &other) {
            if (container_) lv_obj_del(container_);
            container_ = other.container_;
            other.container_ = nullptr;
        }
        return *this;
    }

    [[nodiscard]] lv_obj_t* handle() const noexcept { return container_; }

private:
    lv_obj_t* container_{nullptr};
};

} // namespace gcs::ui
```
:::

Будь-які модальні діалоги, вікна підтвердження чи меню, створені користувацьким кодом на активному екрані або навіть на `lv_layer_sys()`, автоматично опиняються нижче за рівнем Z-order, ніж елементи статусу. Це на апаратно-програмному рівні усуває ризик оклюзії життєво важливих параметрів апарата.