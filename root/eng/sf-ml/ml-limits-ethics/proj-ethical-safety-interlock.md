# ⚙️ Апаратний та програмний інтерлок безпеки критичної системи

Автономний класифікатор на борту медичного хірургічного маніпулятора, лазерного терапевтичного комплексу чи промислового мобільного робота обробив сенсорний потік і з упевненістю 0.98 сформував запит на активацію силового органу. Якщо мікроконтролер виконає цю команду безпосередньо за сигналом із нейроприскорювача (NPU), будь-який збій сенсора, вихід вхідного вектора за межі навчального розподілу чи апаратний збій пам'яті ваг призведе до незворотної фізичної шкоди. Нейромережа принципово не здатна надати детермінованих гарантій безпеки: її вихід є статистичною екстраполяцією, а високий бал упевненості свідчить лише про схожість входу з навчальними даними, а не про фізичну безпечність дії.

Щоб унеможливити неконтрольовані дії автономної моделі, силовий контур відділяють від обчислювача багаторівневим детермінованим бар'єром — інтерлоком безпеки (англ. *safety interlock* — схема взаємного блокування). Інтерлок поєднує строгу програмно-криптографічну верифікацію на незалежному мікроконтролері та пряме апаратне знеструмлення силових ланцюгів.

---

### Модель загроз і розподіл обов'язків

Архітектура інтерлока проєктується з розрахунку на те, що головний процесор застосунку (SoC/NPU), операційна система та сама модель машинного навчання можуть бути скомпрометовані, зависнути або видати помилкову команду в довільний момент часу. Звідси випливає принцип повної ізоляції повноважень:

1. **Ймовірнісний контур (NPU / Application SoC):** обробляє камери, лідари чи біомедичні сигнали, виконує інференс нейромережі та генерує структуру-пропозицію `ActuationProposal`. Цей контур не має фізичних електричних зв'язків із затворами силових ключів (MOSFET/IGBT) чи котушками реле.
2. **Детермінований контур безпеки (Safety MCU):** окремий низькорівневий мікроконтролер із сертифікованим ядром реального часу. Він виконує жорстко зашиті перевірки: валідує токен авторизації людини-оператора, контролює фізичний коридор безпеки (англ. *safety envelope*), атомарно фіксує стан у незалежному журналі аудиту та формує дискретний сигнал дозволу `ARM_ENABLE`.
3. **Апаратний інтерлок і фізичний E-Stop:** логічні мікросхеми та реле безпеки з примусово керованими контактами (англ. *force-guided contacts*, стандарт EN 50205). Живлення на приводи подається лише за умови одночасної наявності сигналу `ARM_ENABLE` від контролера та замкненого фізичного ланцюга кнопки аварійної зупинки.

```
+---------------------+       +------------------------+       +----------------------+
|  NPU / Модель ML    |       | Контролер безпеки (MCU)|       | Апаратна логіка AND  |
|  ActuationProposal  +------>| 1. Перевірка токена    +------>| & Силовий комутатор  |
|  (сила, швидкість)  |       | 2. Фізичні ліміти      |ARM_OK |                      |
+---------------------+       | 3. Фіксація в лог      |       +----------+-----------+
                              +-----------+------------+                  |
                                          ^                               | V_PWR (живлення)
+---------------------+                   |                               v
| Пульт оператора     |                   |                    +----------------------+
| OperatorToken       +-------------------+                    | Кнопка E-Stop        |
| (TTL, підпис, роль) |                                        | (фізичний розрив NC) |
+---------------------+                                        +----------------------+
```

---

### Протокол авторизації оператора та часові вікна

У критичних системах застосовується режим підтвердження дій людиною (англ. *Human-in-the-Loop*). Дозвіл оператора передається у формі структури `OperatorToken`. Токен захищений від підробки контрольною сумою або криптографічним підписом і має суворо обмежений час життя (англ. *Time-To-Live*, TTL — типово 100–300 мс).

Часове вікно TTL гарантує, що дія буде виконана лише тоді, коли оператор безпосередньо в цей момент спостерігає за системою й тримає кнопку підтвердження (принцип аварійного вимикача мерця, англ. *Dead Man's Switch*). Якщо зв'язок із пультом переривається чи оператор відпускає клавішу, токен стає протермінованим протягом часток секунди, і контролер безпеки миттєво знімає сигнал `ARM_ENABLE`.

Окрім перевірки часу, контролер безпеки звіряє параметри дії з жорсткими фізичними константами:
- **Граничне зусилля / потужність:** дія блокується, якщо запропоноване зусилля перевищує допустимий поріг (наприклад, понад 150 Н для колаборативного маніпулятора).
- **Максимальна швидкість переміщення:** блокування у разі перевищення ліміту швидкості приводу.
- **Бітова маска дозволів:** перевірка, чи має конкретний оператор право активувати даний тип силового інструмента.
- **Незмінний аудит перед дією:** запис ідентифікатора дії, оцінки моделі та хешу вагових коефіцієнтів у незалежну пам'ять (FRAM/Flash) ДО того, як сигнал активації піде на апаратний ключ.

---

### Програмна реалізація інтерлока безпеки

Нижче наведено повну реалізацію модуля перевірки інтерлока: обробку вхідного запиту від ML-моделі, верифікацію токена оператора, контроль фізичних параметрів та формування команди активації.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_ALLOWED_FORCE_N      150.0f
#define MAX_ALLOWED_VELOCITY_MPS   1.2f
#define TOKEN_MAX_TTL_MS          300U
#define AUDIT_LOG_CAPACITY        128U

typedef enum {
    INTERLOCK_OK = 0,
    INTERLOCK_ERR_TOKEN_EXPIRED,
    INTERLOCK_ERR_TOKEN_INVALID_SIG,
    INTERLOCK_ERR_PERMISSION_DENIED,
    INTERLOCK_ERR_FORCE_LIMIT_EXCEEDED,
    INTERLOCK_ERR_VELOCITY_LIMIT_EXCEEDED,
    INTERLOCK_ERR_ESTOP_TRIGGERED,
    INTERLOCK_ERR_AUDIT_LOG_FULL
} InterlockStatus;

typedef enum {
    PERM_NONE           = 0x00,
    PERM_MOTION_ARM     = 0x01,
    PERM_TOOL_ACTIVATE  = 0x02,
    PERM_OVERRIDE_SPEED = 0x04
} PermissionFlags;

typedef struct {
    uint32_t operator_id;
    uint32_t permissions;
    uint64_t timestamp_ms;
    uint32_t ttl_ms;
    uint32_t signature_crc32;
} OperatorToken;

typedef struct {
    uint32_t action_id;
    uint32_t required_perm;
    float requested_force_n;
    float requested_velocity_mps;
    float ml_confidence;
    uint32_t model_weights_hash;
} ActuationProposal;

typedef struct {
    uint64_t log_timestamp_ms;
    uint32_t action_id;
    uint32_t operator_id;
    float applied_force_n;
    float ml_confidence;
    InterlockStatus status;
} AuditRecord;

typedef struct {
    AuditRecord records[AUDIT_LOG_CAPACITY];
    size_t count;
    bool estop_physical_state;
} SafetyInterlockState;

static uint32_t calc_token_crc(const OperatorToken *tok) {
    /* Простий апаратний CRC32 для ілюстрації цілісності пакета */
    uint32_t crc = 0xFFFFFFFFU;
    const uint8_t *data = (const uint8_t *)tok;
    size_t len = sizeof(OperatorToken) - sizeof(tok->signature_crc32);
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int b = 0; b < 8; ++b) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(int32_t)(crc & 1U)));
        }
    }
    return ~crc;
}

void interlock_init(SafetyInterlockState *state) {
    memset(state, 0, sizeof(SafetyInterlockState));
    state->estop_physical_state = true;
}

InterlockStatus interlock_evaluate(
    SafetyInterlockState *state,
    const ActuationProposal *prop,
    const OperatorToken *tok,
    uint64_t current_time_ms,
    bool hardware_estop_pin_active
) {
    state->estop_physical_state = hardware_estop_pin_active;
    
    if (!hardware_estop_pin_active) {
        return INTERLOCK_ERR_ESTOP_TRIGGERED;
    }

    if (calc_token_crc(tok) != tok->signature_crc32) {
        return INTERLOCK_ERR_TOKEN_INVALID_SIG;
    }

    /* Беззнакова різниця захищає від переповнення монотонного таймера */
    uint64_t elapsed_ms = current_time_ms - tok->timestamp_ms;
    if (elapsed_ms > tok->ttl_ms || tok->ttl_ms > TOKEN_MAX_TTL_MS) {
        return INTERLOCK_ERR_TOKEN_EXPIRED;
    }

    if ((tok->permissions & prop->required_perm) != prop->required_perm) {
        return INTERLOCK_ERR_PERMISSION_DENIED;
    }

    if (prop->requested_force_n > MAX_ALLOWED_FORCE_N || prop->requested_force_n < 0.0f) {
        return INTERLOCK_ERR_FORCE_LIMIT_EXCEEDED;
    }

    if (prop->requested_velocity_mps > MAX_ALLOWED_VELOCITY_MPS || prop->requested_velocity_mps < 0.0f) {
        return INTERLOCK_ERR_VELOCITY_LIMIT_EXCEEDED;
    }

    if (state->count >= AUDIT_LOG_CAPACITY) {
        return INTERLOCK_ERR_AUDIT_LOG_FULL;
    }

    /* Атомарний запис аудиту ДО генерації сигналу керування */
    AuditRecord *rec = &state->records[state->count++];
    rec->log_timestamp_ms = current_time_ms;
    rec->action_id = prop->action_id;
    rec->operator_id = tok->operator_id;
    rec->applied_force_n = prop->requested_force_n;
    rec->ml_confidence = prop->ml_confidence;
    rec->status = INTERLOCK_OK;

    return INTERLOCK_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <chrono>
#include <expected>

namespace safety {

constexpr float MaxAllowedForceN = 150.0f;
constexpr float MaxAllowedVelocityMps = 1.2f;
constexpr std::chrono::milliseconds MaxTokenTtl{300};
constexpr std::size_t AuditCapacity = 128;

enum class InterlockError : std::uint8_t {
    TokenExpired,
    TokenInvalidSignature,
    PermissionDenied,
    ForceLimitExceeded,
    VelocityLimitExceeded,
    EStopTriggered,
    AuditLogFull
};

enum class PermissionFlags : std::uint32_t {
    None           = 0x00,
    MotionArm      = 0x01,
    ToolActivate   = 0x02,
    OverrideSpeed  = 0x04
};

constexpr PermissionFlags operator|(PermissionFlags a, PermissionFlags b) noexcept {
    return static_cast<PermissionFlags>(static_cast<std::uint32_t>(a) | static_cast<std::uint32_t>(b));
}

constexpr bool has_flag(PermissionFlags mask, PermissionFlags flag) noexcept {
    return (static_cast<std::uint32_t>(mask) & static_cast<std::uint32_t>(flag)) == static_cast<std::uint32_t>(flag);
}

struct OperatorToken {
    std::uint32_t operator_id{0};
    PermissionFlags permissions{PermissionFlags::None};
    std::chrono::milliseconds timestamp{0};
    std::chrono::milliseconds ttl{0};
    std::uint32_t signature_crc32{0};

    [[nodiscard]] std::uint32_t compute_crc() const noexcept {
        std::uint32_t crc = 0xFFFFFFFFU;
        auto bytes = std::as_bytes(std::span{this, 1});
        for (std::size_t i = 0; i < bytes.size() - sizeof(signature_crc32); ++i) {
            crc ^= static_cast<std::uint8_t>(bytes[i]);
            for (int b = 0; b < 8; ++b) {
                crc = (crc >> 1) ^ (0xEDB88320U & (-(static_cast<std::int32_t>(crc & 1U))));
            }
        }
        return ~crc;
    }
};

struct ActuationProposal {
    std::uint32_t action_id{0};
    PermissionFlags required_permission{PermissionFlags::None};
    float requested_force_n{0.0f};
    float requested_velocity_mps{0.0f};
    float ml_confidence{0.0f};
    std::uint32_t model_weights_hash{0};
};

struct AuditRecord {
    std::chrono::milliseconds log_time{0};
    std::uint32_t action_id{0};
    std::uint32_t operator_id{0};
    float applied_force_n{0.0f};
    float ml_confidence{0.0f};
};

class SafetyInterlock {
public:
    constexpr SafetyInterlock() noexcept = default;

    [[nodiscard]] std::expected<void, InterlockError> evaluate(
        const ActuationProposal& proposal,
        const OperatorToken& token,
        std::chrono::milliseconds current_time,
        bool hardware_estop_pin_active
    ) noexcept {
        if (!hardware_estop_pin_active) {
            return std::unexpected(InterlockError::EStopTriggered);
        }

        if (token.compute_crc() != token.signature_crc32) {
            return std::unexpected(InterlockError::TokenInvalidSignature);
        }

        const auto elapsed = current_time - token.timestamp;
        if (elapsed > token.ttl || token.ttl > MaxTokenTtl || elapsed < std::chrono::milliseconds{0}) {
            return std::unexpected(InterlockError::TokenExpired);
        }

        if (!has_flag(token.permissions, proposal.required_permission)) {
            return std::unexpected(InterlockError::PermissionDenied);
        }

        if (proposal.requested_force_n > MaxAllowedForceN || proposal.requested_force_n < 0.0f) {
            return std::unexpected(InterlockError::ForceLimitExceeded);
        }

        if (proposal.requested_velocity_mps > MaxAllowedVelocityMps || proposal.requested_velocity_mps < 0.0f) {
            return std::unexpected(InterlockError::VelocityLimitExceeded);
        }

        if (log_count_ >= AuditCapacity) {
            return std::unexpected(InterlockError::AuditLogFull);
        }

        audit_log_[log_count_++] = AuditRecord{
            .log_time = current_time,
            .action_id = proposal.action_id,
            .operator_id = token.operator_id,
            .applied_force_n = proposal.requested_force_n,
            .ml_confidence = proposal.ml_confidence
        };

        return {};
    }

    [[nodiscard]] std::span<const AuditRecord> get_audit_records() const noexcept {
        return std::span<const AuditRecord>(audit_log_.data(), log_count_);
    }

private:
    std::array<AuditRecord, AuditCapacity> audit_log_{};
    std::size_t log_count_{0};
};

} // namespace safety
```
:::

---

### Апаратне узгодження та підводні камені

При практичній реалізації безпекових контурів розробники стикаються з низкою апаратних та алгоритмічних крайових випадків:

1. **Брязкіт контактів кнопки E-Stop (англ. *contact bounce*):** механічні кнопки аварійної зупинки під час натискання та відпускання генерують серію перехідних імпульсів тривалістю до 15–20 мс. Якщо контролер безпеки підключений до кнопки через чутливий вхід переривання GPIO без належного апаратного RC-фільтра та тригера Шмітта, брязкіт може викликати помилкові переривання або некоректне розблокування системи. Промисловий стандарт вимагає використання подвійних сухих нормально замкнених (NC) контактів, які фізично розривають коло живлення реле безпеки незалежно від цифрового опитування MCU.
2. **Переповнення монотонного таймера:** при використанні 32-бітного лічильника мілісекунд апаратний таймер переповнюється кожні `2^32` мс (приблизно 49.7 діб безперервної роботи). Пряме порівняння `current_time > token.timestamp + ttl` призводить до фатального збою при переході через нуль. Використання беззнакової різниці `(uint32_t)(current_time - token.timestamp) > ttl` гарантує коректну роботу в усьому діапазоні значень.
3. **Захист пам'яті журналів аудиту:** звичайна енергозалежна пам'ять SRAM втрачає вміст при раптовому знеструмленні внаслідок натискання кнопки E-Stop. Якщо аварійний запис не встиг зберегтися, аналіз першопричини інциденту стає неможливим. Для надійного збереження логів використовують незалежну сегментовану енергонезалежну пам'ять із необмеженим ресурсом запису — фероелектричну (FRAM) або магніторезистивну (MRAM) пам'ять із резервним іоністорним живленням.
4. **Апаратна розв'язка та перевірка цілісності силових ключів:** силовий ключ комутації живлення повинен мати зворотний діагностичний зв'язок (англ. *status feedback*). Якщо польовий транзистор MOSFET пробивається накоротко, контролер безпеки фіксує наявність напруги на виході за відсутності сигналу `ARM_ENABLE` і через додатковий аварійний контактор негайно знеструмлює всю силову шину.
