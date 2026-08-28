# ⚙️ Вбудований верифікатор сертифікаційних параметрів і генератор підпису відповідності

Під час сертифікації бездротового приладу за Директивою RED 2014/53/EU випробувальна лабораторія фіксує неподільну комбінацію чотирьох складових: апаратної ревізії друкованої плати (*Hardware Revision*), версії прошивки (*Firmware Version*), типу антени з її коефіцієнтом підсилення та таблиць заводського калібрування вихідної потужності радіотракту (*RF Calibration Tables*). Якщо під час експлуатації або після дистанційного оновлення прошивки (OTA) контролер виставить коефіцієнт підсилення підсилювача потужності (PA) вище задекларованого ліміту (наприклад, +27 dBm замість дозволених для ETSI EN 300 328 +20 dBm EIRP) або увімкне заборонений канал, прилад миттєво стає нелегальним випромінювачем і втрачає презумпцію відповідності.

Щоб унеможливити випадкові помилки конфігурації або навмисні спроби зняття регіональних обмежень, у системне програмне забезпечення пристрою інтегрують спеціалізований модуль верифікації сертифікаційного профілю (*Compliance Enforcement Engine*). Цей модуль перевіряє цілісність сертифікаційних меж під час кожного старту системи до ініціалізації радіочастотних трансиверів та блокує випромінювання у разі будь-яких розбіжностей із Технічним файлом.

### Архітектура сертифікаційного профілю та рівні апаратного захисту

Надійна система верифікації не може спиратися лише на змінні у відкритій оперативній пам'яті, які легко модифікувати через інтерфейс налагодження чи переповнення буфера. Вона будується на трьох взаємопов'язаних рівнях апаратного та програмного контролю:

1. **Апаратний відбиток (Hardware Identity):** ідентифікатор плати та версія схеми зчитуються з однократно програмованої пам'яті (OTP) мікроконтролера, стану апаратних резистивних дільників (*HW Strapping Pins*) або захищеного криптографічного чипа (наприклад, ATECC608 або Secure Element). Це гарантує, що прошивка точно знає, на якій саме ревізії заліза вона запущена, і запобігає завантаженню профілю потужнішої плати на компактний сенсор.
2. **Таблиця регіональних обмежень (Regulatory Power Matrix):** константні структури даних, жорстко зашиті в захищену область Flash-пам'яті або підписані асиметричним ключем виробника. Таблиця містить граничні рівні еквівалентної ізотропно випромінюваної потужності (EIRP в dBm), спектральні маски, дозволені сітки каналів та ліміти робочого циклу (*Duty Cycle*) окремо для європейського домену (`DOMAIN_EU_ETSI`), північноамериканського (`DOMAIN_US_FCC`) та японського (`DOMAIN_JP_MIC`).
3. **Криптографічний хеш маніфесту Технічного файлу:** цифровий дайджест SHA-256, що обчислюється від тексту затвердженої Декларації відповідності (DoC), номера сертифіката експертизи типу та контрольної суми калібрувальних коефіцієнтів. Дайджест слугує цифровим паспортом приладу для систем телеметрії та діагностичних сканерів наглядових органів.

### Покроковий ланцюг завантаження та перевірки параметрів

Процес ініціалізації радіотракту підпорядковується суворому правилу безпечної відмови (*Failsafe Design*): будь-який сумнів у цілісності даних трактується як порушення відповідності та веде до повного вимкнення передавача.

```
[Старт мікроконтролера]
          │
          ▼
[Зчитування ревізії HW з OTP / Fuses]
          │
          ▼
[Обчислення CRC32 калібрувальної таблиці] ──(Невідповідність)──► [Блокування радіо + Режим Failsafe]
          │
      (Збігається)
          ▼
[Визначення регіонального домену]
          │
          ▼
[Перевірка лімітів: Потужність ≤ Ліміт, Канал ∈ Дозволені] ──(Порушення)──► [Заборона передачі + Помилка]
          │
      (У нормі)
          ▼
[Дозвіл живлення PA та старт радіостека]
```

### Реалізація верифікатора сертифікаційних параметрів

Наведений нижче модуль реалізує повну логіку перевірки цілісності калібрувальних таблиць, контроль регіональних обмежень ETSI та генерацію статусного коду для вбудованої діагностики.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_CHANNELS 14
#define REG_DOMAIN_EU_ETSI 0x01
#define REG_DOMAIN_US_FCC  0x02

// Сертифікаційні ліміти, зафіксовані в Технічному файлі
typedef struct {
    uint8_t  domain_id;
    int8_t   max_tx_power_dbm;     // Максимальний допустимий рівень EIRP
    uint16_t min_freq_mhz;         // Нижня межа робочої смуги
    uint16_t max_freq_mhz;         // Верхня межа робочої смуги
    uint8_t  max_duty_cycle_pct;   // Максимальний робочий цикл (%)
    uint16_t allowed_channel_mask; // Бітова маска дозволених каналів (1..13)
} RegulatoryDomainLimits;

typedef struct {
    char     hw_revision[8];
    char     fw_version[16];
    uint8_t  active_domain;
    int8_t   configured_power_dbm;
    uint16_t current_channel_mask;
    uint32_t calibration_crc32;
} DeviceComplianceState;

// Зразок константних лімітів для ринку ЄС (ETSI EN 300 328)
static const RegulatoryDomainLimits ETSI_LIMITS = {
    .domain_id = REG_DOMAIN_EU_ETSI,
    .max_tx_power_dbm = 20,       // 100 мВт EIRP (20 dBm) для 2.4 ГГц
    .min_freq_mhz = 2400,
    .max_freq_mhz = 2483,
    .max_duty_cycle_pct = 100,
    .allowed_channel_mask = 0x1FFF // Канали 1..13 дозволені в ЄС
};

// Генератор CRC32 за стандартом IEEE 802.3
static uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            crc = (crc >> 1) ^ (0xEDB88320 & (-(int32_t)(crc & 1)));
        }
    }
    return ~crc;
}

// Повна верифікація параметрів перед подачею живлення на передавач
bool compliance_verify_rf_parameters(const DeviceComplianceState *state,
                                     uint32_t expected_cal_crc,
                                     char *out_error_reason,
                                     size_t max_err_len) {
    if (state == NULL || out_error_reason == NULL || max_err_len == 0) {
        return false;
    }

    // 1. Контроль цілісності калібрувальних коефіцієнтів у пам'яті
    if (state->calibration_crc32 != expected_cal_crc) {
        strncpy(out_error_reason, "ERR_CALIBRATION_CRC_MISMATCH", max_err_len - 1);
        out_error_reason[max_err_len - 1] = '\0';
        return false;
    }

    // 2. Перевірка дотримання європейських регуляторних норм
    if (state->active_domain == REG_DOMAIN_EU_ETSI) {
        // Контроль перевищення еквівалентної потужності випромінювання
        if (state->configured_power_dbm > ETSI_LIMITS.max_tx_power_dbm) {
            strncpy(out_error_reason, "ERR_ETSI_TX_POWER_EXCEEDED", max_err_len - 1);
            out_error_reason[max_err_len - 1] = '\0';
            return false;
        }

        // Контроль використання заборонених частотних каналів (наприклад, канал 14)
        if ((state->current_channel_mask & ~ETSI_LIMITS.allowed_channel_mask) != 0) {
            strncpy(out_error_reason, "ERR_UNAUTHORIZED_FREQUENCY_CHANNEL", max_err_len - 1);
            out_error_reason[max_err_len - 1] = '\0';
            return false;
        }
    } else {
        strncpy(out_error_reason, "ERR_UNSUPPORTED_OR_INVALID_DOMAIN", max_err_len - 1);
        out_error_reason[max_err_len - 1] = '\0';
        return false;
    }

    out_error_reason[0] = '\0';
    return true;
}
```
```cpp
#include <cstdint>
#include <string_view>
#include <array>
#include <optional>

namespace compliance {

enum class Domain : uint8_t {
    EU_ETSI = 0x01,
    US_FCC  = 0x02
};

struct RegulatoryLimits {
    Domain   domain;
    int8_t   max_tx_power_dbm;
    uint16_t min_freq_mhz;
    uint16_t max_freq_mhz;
    uint8_t  max_duty_cycle_pct;
    uint16_t allowed_channel_mask;
};

// Нормативи ETSI EN 300 328 для діапазону 2.4 ГГц
constexpr RegulatoryLimits ETSI_LIMITS {
    .domain = Domain::EU_ETSI,
    .max_tx_power_dbm = 20,       // 20 dBm (100 mW EIRP)
    .min_freq_mhz = 2400,
    .max_freq_mhz = 2483,
    .max_duty_cycle_pct = 100,
    .allowed_channel_mask = 0x1FFF // Канали 1..13
};

struct ComplianceConfig {
    std::string_view hw_revision;
    std::string_view fw_version;
    Domain           active_domain;
    int8_t           configured_power_dbm;
    uint16_t         channel_mask;
    uint32_t         cal_crc32;
};

class ComplianceValidator {
public:
    explicit constexpr ComplianceValidator(uint32_t expected_crc) noexcept
        : expected_crc_{expected_crc} {}

    [[nodiscard]] std::optional<std::string_view> validate(const ComplianceConfig& cfg) const noexcept {
        // 1. Контроль цілісності калібрувальної таблиці
        if (cfg.cal_crc32 != expected_crc_) {
            return "ERR_CALIBRATION_CRC_MISMATCH";
        }

        // 2. Перевірка дотримання європейських директив
        if (cfg.active_domain == Domain::EU_ETSI) {
            if (cfg.configured_power_dbm > ETSI_LIMITS.max_tx_power_dbm) {
                return "ERR_ETSI_TX_POWER_EXCEEDED";
            }
            if ((cfg.channel_mask & ~ETSI_LIMITS.allowed_channel_mask) != 0) {
                return "ERR_UNAUTHORIZED_FREQUENCY_CHANNEL";
            }
        } else {
            return "ERR_UNSUPPORTED_OR_INVALID_DOMAIN";
        }

        return std::nullopt; // Валідація успішна, порушень не виявлено
    }

private:
    uint32_t expected_crc_;
};

} // namespace compliance
```
:::

### Інженерні пастки та крайові випадки верифікації

Під час експлуатації вбудованих систем розробники часто припускаються типових помилок, які перетворюють валідний сертифікаційний профіль на юридичну та технічну вразливість:

1. **Неприпустимість зміни домену через відкритий інтерфейс.** Регуляторні норми (зокрема Стаття 3.3 Директиви RED та правила FCC Part 15) прямо забороняють надання кінцевому користувачеві можливості самостійно змінювати регуляторний регіон на більш потужний (наприклад, перемикання приладу, розміщеного на ринку ЄС, у режим FCC для отримання потужності +30 dBm). Вибір регіону повинен жорстко прив'язуватися до апаратного SKU під час заводського програмування або верифікуватися криптографічно підписаним конфігураційним сертифікатом.
2. **Деградація енергонезалежної пам'яті (Flash/EEPROM).** Під час тривалої роботи в умовах високих температур або частих циклів перезапису окремі байти калібрувальних коефіцієнтів можуть пошкодитися. Якщо CRC таблиці не збігся, прошивка не має права підставляти «дефолтні» значення на максимальну потужність. Контролер зобов'язаний перейти в аварійний стан захисту (*Safe State*), заблокувати роботу радіопередавача та видати світлову або інтерфейсну індикацію сервісної помилки.
3. **Захист від відкату прошивки (Anti-Rollback Protection).** Якщо у версії прошивки v2.1 було виправлено помилку в роботі PLL синтезатора, яка призводила до виходу за межі дозволеної спектральної маски, стара небезпечна версія v2.0 має бути апаратно заблокована. Для цього використовують апаратні однократні перемички (eFuses) або захищені лічильники завантажувача Secure Boot, що фізично унеможливлює відкат на несертифіковану ревізію коду.
4. **Врахування коефіцієнта підсилення зовнішньої антени.** Якщо пристрій комплектується роз'ємом SMA або U.FL для зовнішньої антени, задекларований рівень EIRP складається з потужності передавача на виході чипа та коефіцієнта підсилення антени мінус втрати в кабелі. Якщо користувач підключає спрямовану антену з підсиленням +9 dBi замість штатної штирової на +2 dBi, прошивка з фіксованим рівнем потужності вийде за ліміт 100 мВт EIRP. У Технічному файлі та інструкції виробник зобов'язаний зафіксувати точний список дозволених антен, або реалізувати автоматичне атенюювання сигналу під час підключення високоефективних антен.
