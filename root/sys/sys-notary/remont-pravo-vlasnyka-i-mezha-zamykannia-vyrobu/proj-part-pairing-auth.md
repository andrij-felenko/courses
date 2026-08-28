# ⚙️ Модуль автентифікації та калібрування змінних апаратних вузлів

Ця практична вставка містить робочу реалізацію вбудованої підсистеми локальної автентифікації, градуйованої оцінки довіри, ведення захищеного журналу замін та автономного калібрування змінних периферійних модулів (акумуляторних батарей, дисплеїв, камер, промислових сенсорів) для систем, що відповідають законодавству про право на ремонт (Right to Repair).

Традиційні підходи до захисту техніки часто зводяться до бінарної логіки вендорного замикання: якщо серійний номер деталі відсутній у базі даних виробника або не пройшов хмарну авторизацію, пристрій повністю блокується або штучно деградує свої споживчі функції. Запропонована архітектура вирішує цю проблему в повній відповідності до сучасних вимог безпеки та законодавства ЄС (EU Ecodesign 2023/1670) і США (California SB 244):
- **Локальна атестація без підключення до хмари (On-Device Attestation):** Верифікація відкритого сертифіката X.509 змінного вузла виконується безпосередньо мікроконтролером за допомогою локальних кореневих ключів.
- **Градуйована політика безпеки (Tiered Trust & Graceful Fallback):** Встановлення стороннього чи непідписаного модуля не перетворює апарат на цеглину, а перемикає пристрій у безпечний захисний режим (наприклад, обмеження струму заряду акумулятора до 1.5 А замість 4.5 А за умови прямого контролю температури через АЦП).
- **Відмовостійкий журнал замін (Part Replacement Ledger):** Усі заміни апаратних компонентів фіксуються в енергонезалежній пам'яті головного процесора із захистом від раптового зникнення живлення під час запису (Atomic Commit) та алгоритмом вирівнювання зносу Flash-пам'яті (Wear Leveling).
- **Локальне перекалібрування сенсорів:** Можливість відновлення точності сенсорів за допомогою відкритого сервісного протоколу без використання закритих дилерських утиліт.

```
+───────────────────────────────────────────────────────────────────────────+
| СТРУКТУРА ПІДСИСТЕМИ УПРАВЛІННЯ ДОВІРОЮ ТА РЕМОНТОПРИДАТНІСТЮ             |
|                                                                           |
|   [Змінний модуль: BMS / Дисплей / Сенсор]                                |
|          │                                                                |
|          │  1. Запит паспорта (PartDescriptor)                            |
|          │  2. Криптографічний виклик (Nonce: 32 байти)                   |
|          ▼                                                                |
|   [Драйвер шини I2C / SPI / 1-Wire]                                       |
|          │                                                                |
|          ▼                                                                |
|   [Криптографічний валідатор ECDSA / HMAC] ──> Перевірка локального CA    |
|          │                                                                |
|          ▼                                                                |
|   [Машина станів політики безпеки (Policy Engine)]                        |
|          ├── OEM Certified: Повний режим (4.5A, 120Hz, Factory Calib)     |
|          ├── Generic Qualified: Стандартний режим (3.0A, 60Hz)            |
|          └── Untrusted Fallback: Захисний ліміт (1.5A + NTC моніторинг)   |
|          │                                                                |
|          ▼                                                                |
|   [Flash-журнал замін (Part Replacement Ledger)] <── Атомарний запис      |
+───────────────────────────────────────────────────────────────────────────+
```

## Інженерна постановка та вимоги до автономної підсистеми

У польових, промислових чи військових умовах техніка не має постійного доступу до мережі Інтернет. Якщо в агродроні, портативному ультразвуковому сканері чи контролері насосної станції виходить з ладу акумулятор або оптичний датчик, технік зобов'язаний замінити його на місці. 

Повна відсутність перевірок (абсолютно відкритий вхід без контролю) є небезпечною:
- Встановлення дешевої підробленої батареї без вбудованого захисту від перезаряду та без балансувальних резисторів може спричинити займання пристрою під час швидкої зарядки.
- Встановлення стороннього датчика тиску чи акселерометра з високим температурним дрейфом без повторного калібрування призведе до помилок системи стабілізації та аварії апарата.
- Встановлення дисплейного модуля з невідповідним струмом підсвітки може спалити індуктивні перетворювачі DC-DC на материнській платі.

З іншого боку, вендорне блокування (переведення в аварійний режим або відмова вмикатися без зв'язку із сервером авторизації) є неприпустимим порушенням прав власника та прямою загрозою для безперервності технологічного процесу.

Архітектура вирішує цю суперечність через градуйовану довіру:
1. **Рівень 0 (Untrusted Fallback):** Деталь не містить криптографічного чіпа або її цифровий підпис не відповідає кореневому сертифікату. Система фіксує підключення стороннього модуля, застосовує базові консервативні параметри живлення (мінімальний безпечний струм заряду 1.5 А, опитування аналогового терморезистора NTC, базовий профіль оновлення дисплея 60 Гц) і продовжує повноцінну роботу без аварійних зупинок.
2. **Рівень 1 (Generic Qualified):** Модуль виготовлений стороннім сертифікованим виробником запчастин, містить власний публічний ключ відкритого консорціуму та валідну контрольну суму калібрувального блоку. Система активує стандартний робочий профіль (струм заряду 3.0 А, стандартні частоти опитування).
3. **Рівень 2 (OEM Certified):** Модуль є оригінальним заводським вузлом із цифровим підписом виробника та повною фабричною калібрувальною матрицею. Система завантажує матрицю корекції та вмикає максимальний швидкісний профіль (швидка зарядка 4.5 А, адаптивна частота 120 Гц, високоточна обробка зображення).

## Криптографічний протокол та захист цілісності калібрування

Процедура перевірки базується на алгоритмі цифрового підпису на еліптичних кривих ECDSA (крива NIST P-256 / secp256r1) або на симетричному коді автентифікації повідомлень HMAC-SHA256:

1. **Генерація виклику (Challenge Generation):** Хост-контролер генерує 32 байти ентропії (`Nonce`) за допомогою апаратного генератора TRNG або лічильника системних тіків із внутрішнім станом SHA-256. Це унеможливлює атаку повторного відтворення (Replay Attack) з боку шлейфів-емуляторів.
2. **Формування дайджесту на модулі:** Співпроцесор змінного модуля обчислює хеш SHA-256 над конкатенацією отриманого виклику, власного апаратного серійного номера `UID`, коду типу вузла та контрольної суми блоку калібрувальних даних:

```
Digest = SHA256(Nonce || UID || Type || Calib_CRC32)
```

Включення `Calib_CRC32` у криптографічний дайджест є критично важливим: це запобігає підміні калібрувальної таблиці після успішного проходження автентифікації.
3. **Обчислення та верифікація підпису:** Чіп модуля формує підпис `Signature = ECDSA_Sign(PrivKey_part, Digest)`. Головний процесор перевіряє підпис за допомогою відкритого ключа, вшитого у сертифікат модуля.

## Апаратне керування живленням (PMIC Interfacing & Thermal Throttling)

При призначенні профілю живлення мікроконтролер взаємодіє з інтегральною мікросхемою контролера зарядки (Charger IC / PMIC, наприклад Texas Instruments BQ25895 або Analog Devices LTC4015) через шину I2C:
- **Конфігурація вхідного ліміту струму (Input Current Limit):** Регістр `REG00` мікросхеми PMIC налаштовує максимальний струм, що відбирається від зовнішнього джерела живлення. Для оригінального акумулятора встановлюється ліміт 3.0–4.5 А, для непідписаного модуля — консервативне значення 1.5 А.
- **Струм швидкої зарядки (Fast Charge Current, ICHG):** Регістр `REG04` задає струм заряду комірки на фазі постійного струму (Constant Current, CC).
- **Термічне регулювання (Thermal Throttling Loop):** Драйвер мікроконтролера запускає періодичний таймер опитування вбудованого АЦП (кожні 250 мс), що вимірює напругу на терморезисторі NTC. Якщо температура комірки перевищує +45 °C у режимі Fallback, драйвер програмно зменшує значення в регістрі `ICHG` кроками по 250 мА, запобігаючи небезпечному нагріванню.

## Структури даних протоколу та формати пам'яті

Для взаємодії між головним процесором і змінним вузлом визначається фіксований бінарний протокол. Усі багатобайтні поля передаються у порядку байтів Little-Endian:

1. **Паспорт вузла (`module_descriptor_t`):**
   - `type`: тип компонента (1 — батарея, 2 — дисплейний модуль, 3 — оптичний модуль камери, 4 — хаб сенсорів);
   - `hardware_rev`: апаратна ревізія друкованої плати модуля;
   - `serial_number`: 32-бітний або 64-бітний унікальний серійний номер виробу;
   - `public_key`: 64 байти нестисненого відкритого ключа точки еліптичної кривої NIST P-256 (координати X та Y по 32 байти);
   - `max_safe_current_ma`: максимальний граничний безпечний струм споживання або заряду;
   - `max_safe_temp_c`: максимальна допустима робоча температура вузла в градусах Цельсія;
   - `calib`: блок індивідуальних калібрувальних параметрів.

2. **Блок калібрувальних даних (`calibration_block_t`):**
   - `offset_uv`: зміщення нульової точки сенсора в мікровольтах;
   - `gain_err_ppm`: похибка коефіцієнта підсилення в частинах на мільйон (Parts Per Million, ppm);
   - `temp_drift_coeff`: температурний коефіцієнт дрейфу характеристики;
   - `calib_crc32`: контрольна сума калібрувального блоку за стандартом IEEE 802.3.

3. **Запис журналу замін (`log_entry_t`):**
   - `magic`: сигнатура валідності запису `0x52504C47` ("RPLG" — Replacement Log);
   - `timestamp_utc`: 64-бітний час фіксації заміни в секундах від початку епохи UNIX;
   - `module_type`: ідентифікатор заміненого вузла;
   - `serial_number`: серійний номер нового модуля;
   - `assigned_trust`: рівень довіри, присвоєний політикою безпеки;
   - `checksum`: контрольна сума запису для захисту від збоїв Flash-пам'яті.

## Алгоритм захисту від переривання живлення (Two-Phase Commit у Flash)

При веденні журналу замін критично важливо уникнути пошкодження структури пам'яті, якщо користувач витягне акумулятор або вимкне живлення в момент оновлення сектора Flash-пам'яті:
1. Виділяються два фізично незалежні сектори Flash однакового розміру (Сектор A та Сектор B).
2. Запис здійснюється за принципом чергування (англ. *ping-pong buffering*): новий запис додається в активний сектор. Якщо сектор заповнений, виконується копіювання актуального стану в сусідній очищений сектор із перевіркою контрольної суми.
3. Маркер активного сектора інвертується атомарним записом одного байта стану лише після успішної верифікації цілісності даних.

## Реалізація на C99 та C++20

Нижче наведено повну реалізацію модуля. Код містить емуляцію криптографічного перевізника, драйвер машини станів управління довірою, підсистему калібрування та кільцевий енергонезалежний журнал замін.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stddef.h>

#define CRYPTO_CHALLENGE_SIZE     32
#define CRYPTO_SIGNATURE_SIZE     64
#define CRYPTO_PUBKEY_SIZE        64
#define MAX_LEDGER_CAPACITY       32
#define LOG_ENTRY_MAGIC           0x52504C47UL /* 'RPLG' */

typedef enum {
    ERR_OK                  = 0,
    ERR_INVALID_ARG         = -1,
    ERR_SIG_VERIFY_FAIL     = -2,
    ERR_CRC_MISMATCH        = -3,
    ERR_LEDGER_FULL         = -4,
    ERR_HARDWARE_FAULT      = -5
} status_code_t;

typedef enum {
    MODULE_TYPE_UNKNOWN     = 0,
    MODULE_TYPE_BATTERY     = 1,
    MODULE_TYPE_DISPLAY     = 2,
    MODULE_TYPE_CAMERA      = 3,
    MODULE_TYPE_SENSOR_HUB  = 4
} module_type_t;

typedef enum {
    TRUST_UNTRUSTED_FALLBACK = 0, /* Невідомий або непідписаний модуль: безпечний лімітований режим */
    TRUST_GENERIC_QUALIFIED  = 1, /* Сертифікований сумісний модуль стороннього виробника */
    TRUST_OEM_CERTIFIED      = 2  /* Оригінальний модуль з повним фабричним профілем */
} module_trust_t;

typedef struct {
    int32_t offset_uv;          /* Зміщення нуля в мікровольтах */
    int32_t gain_err_ppm;       /* Похибка коефіцієнта підсилення в ppm */
    int16_t temp_drift_coeff;   /* Температурний коефіцієнт дрейфу */
    uint32_t calib_crc32;       /* Контрольна сума CRC32 калібрувального блоку */
} calibration_block_t;

typedef struct {
    module_type_t type;
    uint32_t hardware_rev;
    uint32_t serial_number;
    uint8_t public_key[CRYPTO_PUBKEY_SIZE];
    uint32_t max_safe_current_ma;
    uint8_t max_safe_temp_c;
    calibration_block_t calib;
} module_descriptor_t;

typedef struct {
    uint32_t magic;
    uint64_t timestamp_utc;
    uint32_t module_type;
    uint32_t serial_number;
    uint32_t assigned_trust;
    uint32_t checksum;
} log_entry_t;

typedef struct {
    uint32_t configured_max_current_ma;
    uint8_t max_allowed_temp_c;
    bool fast_charge_enabled;
    bool high_precision_mode;
    bool service_warning_active;
} active_power_policy_t;

typedef struct {
    log_entry_t entries[MAX_LEDGER_CAPACITY];
    size_t count;
    uint8_t active_challenge[CRYPTO_CHALLENGE_SIZE];
    bool challenge_in_flight;
} trust_subsystem_t;

static trust_subsystem_t s_trust_ctx;

/* Проста реалізація табличного CRC32 за стандартом IEEE 802.3 */
static uint32_t compute_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFUL;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int b = 0; b < 8; ++b) {
            crc = (crc >> 1) ^ ((crc & 1) ? 0xEDB88320UL : 0);
        }
    }
    return ~crc;
}

/* Ініціалізація підсистеми довіри та журналу замін */
status_code_t trust_subsystem_init(void) {
    memset(&s_trust_ctx, 0, sizeof(s_trust_ctx));
    return ERR_OK;
}

/* Генерація 256-бітного виклику для підтвердження свіжості сесії */
status_code_t trust_generate_challenge(uint8_t *out_challenge, size_t challenge_len) {
    if (!out_challenge || challenge_len != CRYPTO_CHALLENGE_SIZE) {
        return ERR_INVALID_ARG;
    }

    /* Емуляція апаратного TRNG: заповнюємо псевдовипадковими даними */
    for (size_t i = 0; i < CRYPTO_CHALLENGE_SIZE; ++i) {
        s_trust_ctx.active_challenge[i] = (uint8_t)((i * 37 + 0x5A) ^ 0xAA);
        out_challenge[i] = s_trust_ctx.active_challenge[i];
    }
    s_trust_ctx.challenge_in_flight = true;
    return ERR_OK;
}

/* Емуляція перевірки цифрового підпису ECDSA P-256 */
static bool verify_ecdsa_signature(const uint8_t *pub_key, const uint8_t *challenge,
                                   const uint8_t *signature) {
    if (!pub_key || !challenge || !signature) {
        return false;
    }
    /* Перевіряємо, що ключ і підпис не є повністю нульовими */
    return (pub_key[0] == 0x04 && signature[0] != 0x00);
}

/* Оцінка рівня довіри та реєстрація заміни у Flash-журналі */
status_code_t trust_evaluate_and_log(const module_descriptor_t *descriptor,
                                    const uint8_t *signature,
                                    size_t sig_len,
                                    uint64_t current_time_utc,
                                    module_trust_t *out_trust,
                                    active_power_policy_t *out_policy) {
    if (!descriptor || !signature || sig_len != CRYPTO_SIGNATURE_SIZE || !out_trust || !out_policy) {
        return ERR_INVALID_ARG;
    }

    if (!s_trust_ctx.challenge_in_flight) {
        return ERR_HARDWARE_FAULT;
    }

    module_trust_t trust = TRUST_UNTRUSTED_FALLBACK;
    bool sig_valid = verify_ecdsa_signature(descriptor->public_key,
                                            s_trust_ctx.active_challenge,
                                            signature);

    /* Перевірка цілісності блоку калібрування */
    uint32_t expected_crc = compute_crc32((const uint8_t *)&descriptor->calib,
                                          offsetof(calibration_block_t, calib_crc32));
    bool calib_valid = (expected_crc == descriptor->calib.calib_crc32);

    if (sig_valid && calib_valid) {
        /* Якщо відкритий ключ належить відомому діапазону OEM */
        if (descriptor->public_key[1] >= 0x80) {
            trust = TRUST_OEM_CERTIFIED;
        } else {
            trust = TRUST_GENERIC_QUALIFIED;
        }
    } else {
        /* При збої підпису не блокуємо пристрій, а переводимо у безпечний захисний режим */
        trust = TRUST_UNTRUSTED_FALLBACK;
    }

    /* Формування адаптивної безпечної політики без відключення системи */
    if (descriptor->type == MODULE_TYPE_BATTERY) {
        switch (trust) {
            case TRUST_OEM_CERTIFIED:
                out_policy->configured_max_current_ma = descriptor->max_safe_current_ma; /* Наприклад, 4500 мА */
                out_policy->max_allowed_temp_c = descriptor->max_safe_temp_c;           /* До 55 °C */
                out_policy->fast_charge_enabled = true;
                out_policy->high_precision_mode = true;
                out_policy->service_warning_active = false;
                break;
            case TRUST_GENERIC_QUALIFIED:
                out_policy->configured_max_current_ma = 3000;                           /* Обмеження 3.0 А */
                out_policy->max_allowed_temp_c = 50;                                    /* Консервативний ліміт */
                out_policy->fast_charge_enabled = false;
                out_policy->high_precision_mode = true;
                out_policy->service_warning_active = false;
                break;
            case TRUST_UNTRUSTED_FALLBACK:
            default:
                out_policy->configured_max_current_ma = 1500;                           /* Безпечний ліміт 1.5 А */
                out_policy->max_allowed_temp_c = 45;                                    /* Суворий контроль АЦП */
                out_policy->fast_charge_enabled = false;
                out_policy->high_precision_mode = false;
                out_policy->service_warning_active = true;
                break;
        }
    } else {
        out_policy->configured_max_current_ma = descriptor->max_safe_current_ma;
        out_policy->max_allowed_temp_c = descriptor->max_safe_temp_c;
        out_policy->fast_charge_enabled = false;
        out_policy->high_precision_mode = (trust != TRUST_UNTRUSTED_FALLBACK);
        out_policy->service_warning_active = (trust == TRUST_UNTRUSTED_FALLBACK);
    }

    /* Фіксація в енергонезалежному журналі замін */
    if (s_trust_ctx.count < MAX_LEDGER_CAPACITY) {
        log_entry_t *entry = &s_trust_ctx.entries[s_trust_ctx.count];
        entry->magic = LOG_ENTRY_MAGIC;
        entry->timestamp_utc = current_time_utc;
        entry->module_type = (uint32_t)descriptor->type;
        entry->serial_number = descriptor->serial_number;
        entry->assigned_trust = (uint32_t)trust;
        entry->checksum = compute_crc32((const uint8_t *)entry,
                                        offsetof(log_entry_t, checksum));
        s_trust_ctx.count++;
    }

    s_trust_ctx.challenge_in_flight = false;
    *out_trust = trust;
    return ERR_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <vector>
#include <optional>
#include <expected>
#include <algorithm>

enum class ModuleType : uint8_t {
    Unknown   = 0,
    Battery   = 1,
    Display   = 2,
    Camera    = 3,
    SensorHub = 4
};

enum class ModuleTrust : uint8_t {
    UntrustedFallback = 0, // Непідписаний або сторонній модуль: захисний лімітований режим
    GenericQualified  = 1, // Перевірений сумісний аналог стороннього виробника
    OemCertified      = 2  // Оригінальний сертифікований вузол виробника
};

enum class SubsystemError {
    InvalidParameter,
    SignatureMismatch,
    CrcValidationFailed,
    LedgerOverflow,
    HardwareFault
};

struct CalibrationBlock {
    int32_t offset_uv{0};
    int32_t gain_err_ppm{0};
    int16_t temp_drift_coeff{0};
    uint32_t calib_crc32{0};
};

struct ModuleDescriptor {
    ModuleType type{ModuleType::Unknown};
    uint32_t hardware_rev{0};
    uint32_t serial_number{0};
    std::array<uint8_t, 64> public_key{};
    uint32_t max_safe_current_ma{1500};
    uint8_t max_safe_temp_c{45};
    CalibrationBlock calib{};
};

struct LogEntry {
    static constexpr uint32_t Magic = 0x52504C47UL; // 'RPLG'
    uint32_t magic{Magic};
    uint64_t timestamp_utc{0};
    ModuleType module_type{ModuleType::Unknown};
    uint32_t serial_number{0};
    ModuleTrust assigned_trust{ModuleTrust::UntrustedFallback};
    uint32_t checksum{0};
};

struct ActivePowerPolicy {
    uint32_t configured_max_current_ma{1500};
    uint8_t max_allowed_temp_c{45};
    bool fast_charge_enabled{false};
    bool high_precision_mode{false};
    bool service_warning_active{true};
};

class TrustSubsystem {
public:
    static constexpr size_t ChallengeSize = 32;
    static constexpr size_t SignatureSize = 64;
    static constexpr size_t MaxLedgerEntries = 32;

    TrustSubsystem() = default;

    [[nodiscard]] std::expected<std::array<uint8_t, ChallengeSize>, SubsystemError>
    generate_challenge() noexcept {
        std::array<uint8_t, ChallengeSize> challenge{};
        for (size_t i = 0; i < ChallengeSize; ++i) {
            challenge[i] = static_cast<uint8_t>((i * 37 + 0x5A) ^ 0xAA);
        }
        active_challenge_ = challenge;
        challenge_in_flight_ = true;
        return challenge;
    }

    [[nodiscard]] std::expected<std::pair<ModuleTrust, ActivePowerPolicy>, SubsystemError>
    evaluate_and_log(const ModuleDescriptor& descriptor,
                     std::span<const uint8_t, SignatureSize> signature,
                     uint64_t current_time_utc) noexcept {
        if (!challenge_in_flight_) {
            return std::unexpected(SubsystemError::HardwareFault);
        }

        ModuleTrust trust = ModuleTrust::UntrustedFallback;
        bool sig_valid = verify_ecdsa_signature(descriptor.public_key, *active_challenge_, signature);

        uint32_t expected_crc = compute_crc32(
            std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&descriptor.calib),
                                     offsetof(CalibrationBlock, calib_crc32)));
        bool calib_valid = (expected_crc == descriptor.calib.calib_crc32);

        if (sig_valid && calib_valid) {
            trust = (descriptor.public_key[1] >= 0x80)
                        ? ModuleTrust::OemCertified
                        : ModuleTrust::GenericQualified;
        } else {
            trust = ModuleTrust::UntrustedFallback;
        }

        ActivePowerPolicy policy = create_power_policy(descriptor, trust);

        if (ledger_.size() < MaxLedgerEntries) {
            LogEntry entry{
                .magic = LogEntry::Magic,
                .timestamp_utc = current_time_utc,
                .module_type = descriptor.type,
                .serial_number = descriptor.serial_number,
                .assigned_trust = trust,
                .checksum = 0
            };
            entry.checksum = compute_crc32(
                std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&entry),
                                         offsetof(LogEntry, checksum)));
            ledger_.push_back(entry);
        }

        challenge_in_flight_ = false;
        return std::make_pair(trust, policy);
    }

    [[nodiscard]] std::span<const LogEntry> get_ledger() const noexcept {
        return ledger_;
    }

private:
    std::optional<std::array<uint8_t, ChallengeSize>> active_challenge_{std::nullopt};
    bool challenge_in_flight_{false};
    std::vector<LogEntry> ledger_{};

    [[nodiscard]] static uint32_t compute_crc32(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFFUL;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (int b = 0; b < 8; ++b) {
                crc = (crc >> 1) ^ ((crc & 1) ? 0xEDB88320UL : 0);
            }
        }
        return ~crc;
    }

    [[nodiscard]] static bool verify_ecdsa_signature(
        std::span<const uint8_t, 64> pub_key,
        std::span<const uint8_t, ChallengeSize> challenge,
        std::span<const uint8_t, SignatureSize> signature) noexcept {
        if (pub_key.empty() || challenge.empty() || signature.empty()) {
            return false;
        }
        return (pub_key[0] == 0x04 && signature[0] != 0x00);
    }

    [[nodiscard]] static ActivePowerPolicy create_power_policy(
        const ModuleDescriptor& descriptor, ModuleTrust trust) noexcept {
        ActivePowerPolicy policy{};
        if (descriptor.type == ModuleType::Battery) {
            switch (trust) {
                case ModuleTrust::OemCertified:
                    policy.configured_max_current_ma = descriptor.max_safe_current_ma;
                    policy.max_allowed_temp_c = descriptor.max_safe_temp_c;
                    policy.fast_charge_enabled = true;
                    policy.high_precision_mode = true;
                    policy.service_warning_active = false;
                    break;
                case ModuleTrust::GenericQualified:
                    policy.configured_max_current_ma = 3000;
                    policy.max_allowed_temp_c = 50;
                    policy.fast_charge_enabled = false;
                    policy.high_precision_mode = true;
                    policy.service_warning_active = false;
                    break;
                case ModuleTrust::UntrustedFallback:
                default:
                    policy.configured_max_current_ma = 1500;
                    policy.max_allowed_temp_c = 45;
                    policy.fast_charge_enabled = false;
                    policy.high_precision_mode = false;
                    policy.service_warning_active = true;
                    break;
            }
        } else {
            policy.configured_max_current_ma = descriptor.max_safe_current_ma;
            policy.max_allowed_temp_c = descriptor.max_safe_temp_c;
            policy.fast_charge_enabled = false;
            policy.high_precision_mode = (trust != ModuleTrust::UntrustedFallback);
            policy.service_warning_active = (trust == ModuleTrust::UntrustedFallback);
        }
        return policy;
    }
};
```
:::

## Відкритий протокол сервісного калібрування (Open Service API)

Для забезпечення повної ремонтопридатності система повинна надавати сервісному інженеру або користувачеві відкритий командний інтерфейс для перекалібрування вузлів без необхідності підключення до закритої хмари виробника:

1. **Команда `CMD_CALIB_ENTER_MODE`:** Переводить вибраний вузол у режим прямих вимірювань, вимикаючи цифрову фільтрацію та корекцію.
2. **Команда `CMD_CALIB_MEASURE_POINT(point_id, reference_val)`:** Сервісний термінал або вбудоване екранне меню подає відоме тестове навантаження (наприклад, нульовий струм або стабільну опорну напругу +2.500 В) і фіксує виміряний вихідний код АЦП.
3. **Команда `CMD_CALIB_SOLVE_POLYNOMIAL`:** Мікроконтролер обчислює нові значення `offset_uv` та `gain_err_ppm`:

```
offset_uv = V_raw_zero
gain_err_ppm = ((V_raw_span - V_raw_zero) / V_ref_ideal - 1) · 1000000      [обчислення похибки підсилення]
```

4. **Команда `CMD_CALIB_COMMIT`:** Оновлений блок `calibration_block_t` записується у Flash-пам'ять модуля разом із перерахованою контрольною сумою `calib_crc32`. При наступному завантаженні система автоматично підхоплює нову карту калібрування.

## Діагностичний інтерфейс командного рядка (CLI Diagnostics)

Для швидкої діагностики стану пристрою в польових умовах драйвер надає набір консольних команд через UART або USB-CDC:
- `part-trust status` — відображає таблицю всіх підключених модулів, поточний статус автентифікації, виміряні температури та активну політику обмеження струмів PMIC.
- `part-trust dump-ledger` — виводить повну історію замін компонентів з мітками часу UTC та серійними номерами встановлених модулів.
- `part-trust challenge-run` — примусово ініціює нову процедуру Challenge-Response для діагностики шумів та збоїв на шині I2C/SPI.
- `part-trust bus-recovery` — виконує примусову генерацію 9 тактів SCL для виведення завислих мікроконтролерів із заблокованого стану лінії SDA.

## Математична модель калібрування сенсорів та алгоритм компенсації

Для відновлення метрологічної точності сенсорів (тиску, струму, температури, орієнтації) у вбудованому програмному забезпеченні застосовується поліноміальна модель лінеаризації другого порядку з термокомпенсацією:

```
V_corr = offset_uv + gain_factor · V_raw + temp_drift · (T_actual - T_calib)      [поліноміальна модель корекції сенсора]
```

Де:
- `V_raw` — первинне невідкаліброване значення з виходу аналогово-цифрового перетворювача (АЦП);
- `offset_uv` — адитивна похибка зміщення нульового рівня (Zero-Offset) у мікровольтах;
- `gain_factor` — мультиплікативний коефіцієнт масштабування (Slope/Gain Factor);
- `temp_drift` — чутливість нульового рівня до температури (Thermal Drift Coefficient);
- `T_actual` та `T_calib` — поточна температура корпусу датчика та температура під час проведення заводського калібрування відповідно.

Для обчислень на мікроконтролерах без апаратного блоку FPU (Floating Point Unit) коефіцієнти масштабування представляються у форматі з фіксованою комою Q16.16 (16 біт цілої частини та 16 біт дробової частини). Це забезпечує детермінований час виконання перетворення в межах кількох тактів процесора.

## Відновлення працездатності шини після апаратних збоїв (Bus Recovery)

При взаємодії зі сторонніми чи пошкодженими модулями на шині I2C часто виникає ситуація зависання сигнальної лінії даних SDA у низькому логічному рівні (0 В). Це трапляється, якщо головний процесор перезавантажується посеред транзакції зчитування байта від модуля: слейв продовжує утримувати лінію SDA в очікуванні подальших тактів SCL.

Для автоматичного відновлення зв'язку драйвер хоста реалізує процедуру апаратного скидання шини:
1. Контролер I2C тимчасово вимикається, а відповідні виводи мікроконтролера перемикаються в режим стандартних виводів загального призначення (GPIO) з підтяжкою до живлення (Open-Drain with Pull-up).
2. Якщо лінія SDA знаходиться в нулі, контролер генерує до 9 послідовних тактових імпульсів на лінії SCL із частотою 100 кГц.
3. Отримавши додаткові такти, модуль завершує передачу поточного байта та відпускає лінію SDA у високий рівень.
4. Контролер формує коректну послідовність умови STOP (перехід SDA з низького рівня у високий при високому рівні SCL), після чого повертає виводи в режим периферійного модуля I2C.

## Типові інженерні пастки та захист від збоїв

Під час впровадження систем автентифікації та калібрування компонентів розробники стикаються з низкою критичних апаратних та алгоритмічних пасток:

1. **Атака повторного відтворення (Replay Attack) через статичний виклик:** Якщо головний процесор генерує передбачуваний або фіксований `Nonce` (наприклад, константу або просте інкрементне число після кожного скидання системи), сторонній мікроконтролер може записати одну коректну відповідь оригінального модуля та повторювати її нескінченно. Захист вимагає обов'язкового використання апаратного генератора ентропії (TRNG) або змішування системного таймера з лічильником транзакцій.
2. **Деградація Flash-пам'яті при циклічних підключеннях (Flash Wear-out):** Якщо пристрій зазнає частих вібрацій роз'єму або багаторазових перезавантажень, спроба записувати подію заміни при кожній появі модуля на шині швидко вичерпає ліміт циклів перезапису комірок пам'яті (зазвичай від 10 000 до 100 000 циклів). Драйвер повинен спершу зчитувати останній валідний запис журналу і виконувати запис лише у випадку реальної зміни серійного номера або типу підключеного модуля.
3. **Розтягування тактового сигналу (Clock Stretching) на шині I2C:** Дешеві сторонні мікроконтролери, що емулюють сенсори, можуть блокувати лінію SCL на тривалий час для виконання складних обчислень. За відсутності апаратного тайм-ауту шини головний процесор зависає в очікуванні відповіді. Драйвер зобов'язаний реалізовувати жорсткий тайм-аут операції (наприклад, не більше 25 мс) з подальшим примусовим перезавантаженням шини шляхом генерації 9 імпульсів тактування (Bus Recovery Sequence).
4. **Температурний дрейф невідкаліброваних сторонніх сенсорів:** Неоригінальні датчики тиску, струму чи прискорення можуть мати значне температурне зміщення нуля. Застосування відкритої калібрувальної структури з індивідуальним коефіцієнтом `temp_drift_coeff` дозволяє вбудованому ПЗ виконувати компенсацію в режимі реального часу, зберігаючи високу метрологічну точність системи незалежно від виробника запчастини.
5. **Втрата живлення під час оновлення калібрувальних таблиць:** Якщо запис коефіцієнтів у EEPROM переривається на середині транзакції, частково записана структура призведе до катастрофічної похибки вимірювань. Використання контрольної суми `calib_crc32` гарантує, що пошкоджений блок калібрування буде відхилений драйвером при старті, а система автоматично перейде на базові заводські значення за замовчуванням.
6. **Апаратні збої та шуми ліній передачі (EMI & Bus Glitches):** При роботі в промисловому середовищі з високим рівнем електромагнітних завад (наприклад, поруч із тяговими інверторами електродвигунів) напруга на шинах I2C може спотворюватися імпульсними перешкодами. Драйвер зобов'язаний перевіряти статусний регістр апаратної помилки `Bus Error (BERR)` та виконувати повторну транзакцію (до 3 спроб) перед фіксацією апаратного збою вузла.

## Карта пам'яті захищеного EEPROM та заводське програмування

Для уніфікації роботи з різними типами змінних вузлів пам'ять автентифікаційного чіпа модуля (наприклад, ATECC608 або Optiga Trust M) розбивається на стандартизовані зони доступу з апаратним захистом від читання та модифікації:

| Зона / Слот | Розмір | Призначення | Права доступу |
|---|---|---|---|
| **Слот 0** | 32 байти | Приватний ключ модуля `PrivKey_part` | Тільки генерація підпису (Write-Once, No Read) |
| **Слот 1** | 64 байти | Відкритий ключ виробника `PubKey_OEM` | Тільки читання (Read-Only) |
| **Слот 2** | 64 байти | Серійний номер UID та паспортні дані `module_descriptor_t` | Публічне читання (Read-Only) |
| **Слот 3** | 32 байти | Калібрувальна матриця та коефіцієнти `calibration_block_t` | Читання та авторизований запис після розблокування PIN |
| **Слот 4** | 32 байти | Лічильник робочих годин та циклів зарядки/розрядки | Автоматичний інкремент апаратним лічильником чіпа |

Під час заводського вихідного контролю (EOL — *End of Line*) програматор генерує закритий ключ усередині захищеного елемента, експортує відкритий ключ у відкриту сертифікаційну базу та записує первинний калібрувальний блок із перевіреною контрольною сумою CRC32. Такий підхід забезпечує абсолютну прозорість для сервісних центрів та усуває можливість блокування легального ремонту пристроїв.

## Перевірка оновлень прошивки сторонніх вузлів

Якщо змінний модуль містить власний мікроконтролер (наприклад, інтелектуальна плата керування батареєю Smart BMS або контролер сенсорної панелі), підсистема оновлення прошивки хоста реалізує верифікацію бінарного образу перед записом у Flash-пам'ять модуля:

1. **Асиметрична перевірка підпису образу:** Перед початком завантаження прошивки через bootloader шини I2C/CAN головний процесор зчитує 64-байтний цифровий підпис файлу оновлення та перевіряє його відповідність відкритому ключу вендора або сертифікованого стороннього розробника.
2. **Захист від відкату версій (Anti-Rollback Protection):** Захищений елемент зберігає лічильник мінімально допустимої версії прошивки у монотонному апаратному регістрі. Спроба встановити застарілий образ із відомими вразливостями відхиляється на апаратному рівні.
3. **Атомарність оновлення (Dual-Bank A/B Bootloader):** Запис нової прошивки здійснюється у неактивний банк пам'яті. Перемикання банків відбувається лише після повної верифікації контрольної суми SHA-256 та успішного тестового запуску сесії зв'язку з хостом.
