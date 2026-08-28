# ⚙️ Логічний рушій оцінки умов оновлення на боці пристрою

Цей проєкт демонструє повнофункціональну інженерну реалізацію вбудованого рушія перевірки політики оновлення (*Update Policy Evaluator*). Модуль призначений для роботи безпосередньо на кінцевому мікроконтролері (як у просторі основної програми, так і всередині вторинного завантажувача) і виконує роль автономного захисного бар'єра: він приймає вхідний маніфест від хмарного сервера, зіставляє його з реальними фізичними параметрами апаратури та ухвалює остаточне рішення про допуск до оновлення.

Головний архітектурний принцип модуля — повна автономність ухвалення рішень на боці пристрою (*Edge Autonomy*). Хмарний сервер може володіти інформацією про наявність нового релізу, але тільки кінцевий мікроконтролер знає поточну температуру кристала, стан заряду акумулятора під навантаженням та фазу виконання технологічного процесу. Рушій унеможливлює ситуацію, коли директивна команда з хмари призводить до знеструмлення або зависання обладнання під час виконання критичного завдання.

## Двоетапна архітектура оцінки передумов

Рушій інтегрується в життєвий цикл прошивки як двоетапний шлюз контролю (*Two-Stage Verification Gate*). Виконання перевірки один раз на початку сесії є недостатнім, оскільки між отриманням маніфесту та завершенням запису Flash може минути значний проміжок часу:

1. **Фаза попередньої кваліфікації (Pre-Download Gate):** Виконується в контексті основної програми одразу після отримання маніфесту через мережевий інтерфейс. Мета цієї фази — запобігти марній витраті трафіку та енергії акумулятора на завантаження мегабайтного образу, якщо пристрій має іншу апаратну ревізію, застарілу версію завантажувача або перебуває в стані критичного розряду батареї.
2. **Фаза фінального допуску до прошивання (Pre-Commit Gate):** Виконується повторно безпосередньо перед стиранням секторів цільового банку Flash-пам'яті або передачею керування вторинному завантажувачу. Під час тривалого приймання даних через нестабільний радіоканал акумулятор міг розрядитися нижче критичного порога, а температура навколишнього середовища могла впасти нижче точки безпечного запису комірок. Якщо повторний замір фіксує погіршення умов, процес анулюється без пошкодження поточної робочої прошивки.

## Логічні кроки та конвеєр перевірки

Рушій працює за строго детермінованою послідовністю перевірок, де кожна наступна ланка аналізується лише після успішного проходження попередньої:

1. **Апаратна ідентифікація та маска ревізій:** Звіряється текстовий ідентифікатор сімейства плати `hardware_family` та бітова маска схемних ревізій `hardware_revision_mask`. Це захищає від випадкового прошивання образу, скомпільованого під інший процесор або плату з іншою розпіновкою периферійних ліній.
2. **Перевірка захисту від відкату (Anti-Rollback):** Звіряється числовий індекс безпеки `security_version` із поточним монотонним лічильником, збереженим в апаратних регістрах eFuse або захищеному елементі (Secure Element). Спроба встановити стару прошивку з відомими вразливостями відхиляється.
3. **Фільтрація мережевого інтерфейсу:** Перевіряється прапорець поточного мережевого з'єднання (`current_bearer`). Якщо маніфест забороняє використання тарифікованого стільникового зв'язку (`CELLULAR_METERED`) для нетермінових релізів, сесія завантаження блокується.
4. **Адаптація та перевірка енергетичного бюджету:** Для стандартних оновлень встановлюється суворий поріг заряду АКБ (50%) та напруги (3.6 В). Якщо реліз класифіковано як `CRITICAL_SECURITY`, рушій динамічно знижує вимогу до 30% заряду та 3.5 В, дозволяючи екстрене закриття вразливості, але зберігаючи мінімальний запас для запобігання апаратному збою.
5. **Температурний контроль Flash:** Зчитується температура з вбудованого сенсора кристала. Запис Flash за межами робочого діапазону (від -10 °C до +55 °C) блокується для захисту підкладки кремнію.
6. **Оцінка операційного стану та вікна обслуговування:** Якщо пристрій виконує місію (`STATE_ACTIVE_MISSION`) або перебуває в стані аварії (`STATE_EMERGENCY`), запит відкладається (`POSTPONE_BUSY`). Якщо пристрій вільний, але поточний час не потрапляє в регламентне вікно, рушій перевіряє лічильник відкладень: якщо ліміт вичерпано, оновлення дозволяється примусово.

## Програмна реалізація мовами C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define HW_FAMILY_MAX_LEN 32
#define MAX_ALLOWED_POSTPONES 5

typedef enum {
    SEVERITY_FEATURE = 1,
    SEVERITY_MAINTENANCE = 2,
    SEVERITY_SECURITY_STANDARD = 3,
    SEVERITY_CRITICAL_SECURITY = 4
} UpdateSeverity;

typedef enum {
    OP_STATE_SHUTDOWN = 0,
    OP_STATE_IDLE = 1,
    OP_STATE_STANDBY = 2,
    OP_STATE_ACTIVE_MISSION = 3,
    OP_STATE_EMERGENCY = 4
} DeviceOperatingState;

typedef enum {
    BEARER_ETHERNET = (1 << 0),
    BEARER_WIFI = (1 << 1),
    BEARER_CELLULAR_UNMETERED = (1 << 2),
    BEARER_CELLULAR_METERED = (1 << 3)
} NetworkBearerMask;

typedef struct {
    char hardware_family[HW_FAMILY_MAX_LEN];
    uint32_t hardware_revision_mask;
    uint32_t security_version;
    UpdateSeverity severity;
    uint8_t min_battery_soc_pct;
    uint16_t min_battery_voltage_mv;
    int8_t temp_min_c;
    int8_t temp_max_c;
    uint32_t allowed_bearers_mask;
    uint8_t max_postpones;
} PolicyManifest;

typedef struct {
    char hardware_family[HW_FAMILY_MAX_LEN];
    uint32_t hardware_revision_bit;
    uint32_t current_security_version;
    DeviceOperatingState operating_state;
    uint8_t battery_soc_pct;
    uint16_t battery_voltage_mv;
    int8_t board_temperature_c;
    NetworkBearerMask current_bearer;
    bool is_in_maintenance_window;
    uint8_t current_postpone_count;
} DeviceTelemetry;

typedef enum {
    POLICY_DECISION_ACCEPT_NOW = 0,
    POLICY_DECISION_POSTPONE_BUSY = 1,
    POLICY_DECISION_POSTPONE_OUTSIDE_WINDOW = 2,
    POLICY_REJECT_HW_FAMILY_MISMATCH = 10,
    POLICY_REJECT_HW_REV_UNSUPPORTED = 11,
    POLICY_REJECT_ANTI_ROLLBACK = 12,
    POLICY_REJECT_BATTERY_LOW = 13,
    POLICY_REJECT_TEMPERATURE_LIMIT = 14,
    POLICY_REJECT_BEARER_DISALLOWED = 15
} PolicyDecisionCode;

PolicyDecisionCode evaluate_update_policy(const PolicyManifest *manifest,
                                         const DeviceTelemetry *telemetry) {
    if (!manifest || !telemetry) {
        return POLICY_REJECT_HW_FAMILY_MISMATCH;
    }

    /* 1. Апаратна ідентифікація */
    if (strncmp(manifest->hardware_family, telemetry->hardware_family, HW_FAMILY_MAX_LEN) != 0) {
        return POLICY_REJECT_HW_FAMILY_MISMATCH;
    }

    if ((manifest->hardware_revision_mask & telemetry->hardware_revision_bit) == 0) {
        return POLICY_REJECT_HW_REV_UNSUPPORTED;
    }

    /* 2. Захист від відкату на вразливу версію */
    if (manifest->security_version < telemetry->current_security_version) {
        return POLICY_REJECT_ANTI_ROLLBACK;
    }

    /* 3. Перевірка мережевого носія */
    if ((manifest->allowed_bearers_mask & telemetry->current_bearer) == 0) {
        return POLICY_REJECT_BEARER_DISALLOWED;
    }

    /* 4. Енергетичні та температурні обмеження */
    uint8_t effective_soc_limit = manifest->min_battery_soc_pct;
    uint16_t effective_volt_limit = manifest->min_battery_voltage_mv;

    /* Для критичного Zero-Day знижуємо бар'єр заряду для якнайшвидшого латання */
    if (manifest->severity == SEVERITY_CRITICAL_SECURITY) {
        if (effective_soc_limit > 30) {
            effective_soc_limit = 30;
        }
        if (effective_volt_limit > 3500) {
            effective_volt_limit = 3500;
        }
    }

    if (telemetry->battery_soc_pct < effective_soc_limit ||
        telemetry->battery_voltage_mv < effective_volt_limit) {
        return POLICY_REJECT_BATTERY_LOW;
    }

    if (telemetry->board_temperature_c < manifest->temp_min_c ||
        telemetry->board_temperature_c > manifest->temp_max_c) {
        return POLICY_REJECT_TEMPERATURE_LIMIT;
    }

    /* 5. Операційний стан і вікно оновлення */
    bool is_emergency = (manifest->severity == SEVERITY_CRITICAL_SECURITY);

    if (telemetry->operating_state == OP_STATE_ACTIVE_MISSION ||
        telemetry->operating_state == OP_STATE_EMERGENCY) {
        /* Пристрій виконує критичну роботу: навіть Zero-Day не повинен ламати керованість */
        return POLICY_DECISION_POSTPONE_BUSY;
    }

    if (!is_emergency) {
        bool postpone_limit_reached = (telemetry->current_postpone_count >= manifest->max_postpones);

        if (!telemetry->is_in_maintenance_window && !postpone_limit_reached) {
            return POLICY_DECISION_POSTPONE_OUTSIDE_WINDOW;
        }
    }

    return POLICY_DECISION_ACCEPT_NOW;
}
```
```cpp
#include <cstdint>
#include <string_view>
#include <expected>
#include <array>
#include <algorithm>

enum class UpdateSeverity : uint8_t {
    Feature = 1,
    Maintenance = 2,
    SecurityStandard = 3,
    CriticalSecurity = 4
};

enum class DeviceOperatingState : uint8_t {
    Shutdown = 0,
    Idle = 1,
    Standby = 2,
    ActiveMission = 3,
    Emergency = 4
};

enum class NetworkBearer : uint32_t {
    Ethernet = (1 << 0),
    Wifi = (1 << 1),
    CellularUnmetered = (1 << 2),
    CellularMetered = (1 << 3)
};

constexpr NetworkBearer operator|(NetworkBearer a, NetworkBearer b) noexcept {
    return static_cast<NetworkBearer>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

constexpr bool has_flag(NetworkBearer mask, NetworkBearer flag) noexcept {
    return (static_cast<uint32_t>(mask) & static_cast<uint32_t>(flag)) != 0;
}

enum class PolicyRejection : uint8_t {
    HwFamilyMismatch = 10,
    HwRevUnsupported = 11,
    AntiRollback = 12,
    BatteryLow = 13,
    TemperatureLimit = 14,
    BearerDisallowed = 15
};

enum class PostponeReason : uint8_t {
    BusyState = 1,
    OutsideWindow = 2
};

struct PolicyManifest {
    std::string_view hardware_family;
    uint32_t hardware_revision_mask{};
    uint32_t security_version{};
    UpdateSeverity severity{UpdateSeverity::Maintenance};
    uint8_t min_battery_soc_pct{50};
    uint16_t min_battery_voltage_mv{3600};
    int8_t temp_min_c{-10};
    int8_t temp_max_c{55};
    NetworkBearer allowed_bearers{NetworkBearer::Ethernet | NetworkBearer::Wifi};
    uint8_t max_postpones{3};
};

struct DeviceTelemetry {
    std::string_view hardware_family;
    uint32_t hardware_revision_bit{1};
    uint32_t current_security_version{1};
    DeviceOperatingState operating_state{DeviceOperatingState::Idle};
    uint8_t battery_soc_pct{100};
    uint16_t battery_voltage_mv{4100};
    int8_t board_temperature_c{25};
    NetworkBearer current_bearer{NetworkBearer::Wifi};
    bool is_in_maintenance_window{true};
    uint8_t current_postpone_count{0};
};

class UpdatePolicyEngine {
public:
    [[nodiscard]] static std::expected<void, std::expected<PostponeReason, PolicyRejection>>
    evaluate(const PolicyManifest& manifest, const DeviceTelemetry& telemetry) noexcept {
        
        // 1. Апаратна ідентифікація
        if (manifest.hardware_family != telemetry.hardware_family) {
            return std::unexpected(std::unexpected(PolicyRejection::HwFamilyMismatch));
        }

        if ((manifest.hardware_revision_mask & telemetry.hardware_revision_bit) == 0) {
            return std::unexpected(std::unexpected(PolicyRejection::HwRevUnsupported));
        }

        // 2. Захист від відкату (Anti-Rollback)
        if (manifest.security_version < telemetry.current_security_version) {
            return std::unexpected(std::unexpected(PolicyRejection::AntiRollback));
        }

        // 3. Мережевий канал
        if (!has_flag(manifest.allowed_bearers, telemetry.current_bearer)) {
            return std::unexpected(std::unexpected(PolicyRejection::BearerDisallowed));
        }

        // 4. Енергетичні та температурні обмеження
        uint8_t effective_soc = manifest.min_battery_soc_pct;
        uint16_t effective_volt = manifest.min_battery_voltage_mv;

        if (manifest.severity == UpdateSeverity::CriticalSecurity) {
            effective_soc = std::min<uint8_t>(effective_soc, 30);
            effective_volt = std::min<uint16_t>(effective_volt, 3500);
        }

        if (telemetry.battery_soc_pct < effective_soc ||
            telemetry.battery_voltage_mv < effective_volt) {
            return std::unexpected(std::unexpected(PolicyRejection::BatteryLow));
        }

        if (telemetry.board_temperature_c < manifest.temp_min_c ||
            telemetry.board_temperature_c > manifest.temp_max_c) {
            return std::unexpected(std::unexpected(PolicyRejection::TemperatureLimit));
        }

        // 5. Операційний стан і регламентне вікно
        const bool is_emergency = (manifest.severity == UpdateSeverity::CriticalSecurity);

        if (telemetry.operating_state == DeviceOperatingState::ActiveMission ||
            telemetry.operating_state == DeviceOperatingState::Emergency) {
            return std::unexpected(std::expected<PostponeReason, PolicyRejection>(PostponeReason::BusyState));
        }

        if (!is_emergency) {
            const bool postpone_exhausted = (telemetry.current_postpone_count >= manifest.max_postpones);
            if (!telemetry.is_in_maintenance_window && !postpone_exhausted) {
                return std::unexpected(std::expected<PostponeReason, PolicyRejection>(PostponeReason::OutsideWindow));
            }
        }

        return {}; // Успішно схвалено до встановлення
    }
};
```
:::

## Інженерні пастки та апаратні крайові випадки

Практична інтеграція логічного рушія вимагає врахування низки специфічних фізичних властивостей мікроконтролерів:

- **Динамічне вимірювання напруги під навантаженням:** Замір напруги живлення `battery_voltage_mv` не можна виконувати в стані спокою процесора. Батарея з внутрішнім опором (ESR) у 200 мОм може демонструвати на холостому ході нормальні 3.7 В. Однак у момент стирання сектора Flash-пам'яті внутрішній помповий помножувач кристала створює імпульс струму до 40 мА тривалістю в кілька десятків мілісекунд, а одночасна робота модема додає ще до 1.5 А в імпульсі. Це призводить до миттєвого просідання напруги нижче апаратного порога Brownout Reset (BOR, зазвичай 2.7 В), спричиняючи циклічний перезапуск (*Boot Loop*). Тому рушій повинен проводити вимірювання ADC під час активного увімкнення тестового навантаження.
- **Фізика тунелювання Flash на морозі:** Під час зниження температури кремнію нижче -10 °C ширина забороненої зони напівпровідника дещо розширюється, а ефективність інжекції електронів крізь тунельний діелектрик затвора Flash-комірки падає. Якщо контролер виконує стирання за стандартними таймінгами, частина комірок залишається недостертою, що призводить до помилок верифікації контрольної суми CRC32/SHA-256 після запису. Рушій захищає кремній від передчасної деградації, забороняючи прошивання на морозі.
- **Атомарність фіксації анти-відкату:** Оновлення апаратного лічильника `current_security_version` в eFuse-пам'яті або Secure Element має відбуватися виключно **після** того, як нова прошивка успішно запустилася, пройшла повне внутрішнє самотестування периферії та надіслала перше підтверджувальне повідомлення на сервер. Передчасне пропалювання запобіжників eFuse до верифікації нової прошивки перетворить пристрій на невідновлювану «цеглину» у разі невдалого старту.
- **Обслуговування сторожового таймера (Watchdog Service):** Процедура повного стирання банку Flash-пам'яті розміром 1–2 МБ може тривати від 5 до 25 секунд залежно від типу кристала. Якщо функція запису блокує ядро й не скидає лічильник апаратного Watchdog, мікроконтролер буде перезавантажено посеред циклу стирання секторів. Рушій та пов'язані низькорівневі драйвери зобов'язані прати пам'ять ітеративно, сектор за сектором, із гарантованим скиданням сторожового таймера на кожному кроці.
