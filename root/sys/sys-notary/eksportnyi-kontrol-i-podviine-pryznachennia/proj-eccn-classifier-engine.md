# ⚙️ Рушій автоматизованої класифікації ECCN та валідації експортних параметрів

Під час проєктування, серійного виробництва та міжнародного постачання високотехнологічної апаратної продукції — від промислових телеметричних контролерів і бездротових сенсорних шлюзів до автономних навігаційних блоків — ручна перевірка компонентів на відповідність нормам експортного контролю є повільним і вразливим до людського фактора процесом. Випадкова заміна АЦП на швидкіснішу модифікацію іншого постачальника, використання нестандартного алгоритму шифрування замість загальноприйнятого протоколу TLS або монтаж мікросхем із розширеним військовим температурним діапазоном може непомітно для інженерної команди перевести кінцевий пристрій із цивільного кошика EAR99 до списку товарів подвійного призначення (Dual-Use) чи навіть під юрисдикцію військового експортного контролю ITAR.

Автоматизований класифікаційний рушій ECCN розв'язує цю проблему шляхом формалізованого аудиту технічних специфікацій на рівні конвеєра безперервної інтеграції (CI/CD) та підсистеми захищеної ініціалізації вбудованого мікроконтролера. Рушій приймає структуровані апаратні метрики з цифрової відомості матеріалів (SBOM), розраховує частку компонентів американського походження за правилом *De Minimis*, порівнює країну призначення за глобальною картою санкційних ризиків та видає однозначний ліцензійний вердикт перед відвантаженням плати або публікацією бінарного образу прошивки.

## Архітектура та послідовність аудиту

Програмний рушій реалізує детермінований алгоритм аналізу, що складається з чотирьох послідовних етапів перевірки:

1. **Аналіз порогових апаратних характеристик (Hardware Threshold Screening):**
   - **Радіаційна стійкість (TID):** Якщо апаратна платформа містить радіаційно стійкі мікросхеми із сумарною накопиченою дозою іонізаційного випромінювання `≥ 500 крад(Si)` (`5 × 10³ Гр(Si)`), пристрою присвоюється категорія `3A001.a.1`, яка вимагає отримання індивідуальної експортної ліцензії в органах державного контролю.
   - **Інерційні сенсори (MEMS IMU):** Якщо дрейф нульового сигналу гіроскопа у сталому режимі (*In-run bias stability*) становить `≤ 0.5 °/год` (500 міліградусів на годину), виріб класифікується за кодом `7A002` (тактичні та навігаційні системи, що можуть використовуватися для автономного польоту крилатих апаратів в умовах придушення GNSS).
   - **Аналогово-цифрові перетворювачі (АЦП):** Якщо мікроконтролер або окрема мікросхема тракту прийому сигналів забезпечує частоту дискретизації `≥ 1 GSPS` при роздільній здатності `≥ 10 біт`, виріб підпадає під контроль за статтею `3A001.a.5` (високошвидкісна електроніка для радарів та станцій радіотехнічного моніторингу).
   - **Робочий температурний діапазон:** Якщо мікросхеми та пасивні елементи розраховані на безперервне функціонування в межах від `-55 °C` до `+125 °C` (або вище за військовими стандартами на кшталт MIL-STD-883), встановлюється категорія `3A001.a.2`.
   - **Криптографічний захист:** Якщо довжина ключа симетричного шифрування перевищує `56 біт`, рушій перевіряє походження алгоритму. За наявності закритого або власного криптографічного механізму встановлюється жорсткий код `5A002.a.1`. Якщо ж у виробі використано виключно стандартні відкриті алгоритми масового ринку (наприклад, TLS 1.3 або SSH згідно з приміткою Note 4), пристрій перекласифікується на `5A992.c` із можливістю відвантаження за ліцензійним винятком `ENC`.

2. **Розрахунок співвідношення De Minimis:**
   - Алгоритм обчислює частку американських компонентів у загальній собівартості продукту.
   - Якщо кінцевий виріб містить понад `25%` контрольованих компонентів походженням зі США, на реекспорт виробу за межі країни виробництва поширюється дія американського регламенту EAR. Для держав під міжнародним ембарго цей поріг автоматично знижується до `10%`.

3. **Верифікація країни призначення та кінцевого використання (KYC):**
   - Перевірка стандартизованого дволітерного коду країни (ISO 3166-1 alpha-2) за списками повного торговельного ембарго (Куба `CU`, Іран `IR`, Північна Корея `KP`, Сирія `SY`, РФ `RU`, Білорусь `BY`).
   - Оцінка ознаки військового кінцевого використання (*Military End-User*, MEU). Наявність прапорця MEU автоматично скасовує дію кошика EAR99 та ліцензійного винятку ENC, переводячи операцію в режим обов'язкового ліцензування.

4. **Формування аудиторського звіту:**
   - Генерація фінального класифікатора ECCN, вибір допустимого експортного режиму (NLR — без ліцензії, License Exception ENC або обов'язкова індивідуальна ліцензія) та текстовий опис першопричини обмеження.

## Інженерна реалізація класифікатора

Нижче наведено повну реалізацію верифікатора мовами C99 та C++20. Структури даних розраховані на детерміноване виконання без динамічного виділення пам'яті у критичних секціях, що забезпечує їх пряму інтеграцію у захищені завантажувачі контролерів та інструменти статичного аналізу збірок.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

#define MAX_ECCN_LEN 16
#define MAX_REASON_LEN 64

// Типи дозволеного експортного режиму
typedef enum {
    EXPORT_MODE_NLR = 0,               // No License Required (ліцензія не потрібна)
    EXPORT_MODE_LICENSE_EXCEPTION_ENC, // Ліцензійний виняток для масової криптографії
    EXPORT_MODE_LICENSE_REQUIRED,      // Обов'язкова індивідуальна експортна ліцензія
    EXPORT_MODE_PROHIBITED_EMBARGO     // Повне ембарго / заборона експорту
} ExportMode;

// Структура вхідних апаратних та фінансових специфікацій виробу
typedef struct {
    uint32_t adc_sample_rate_sps;   // Частота вибірки АЦП (семплів на секунду)
    uint8_t  adc_resolution_bits;   // Роздільна здатність АЦП (біт)
    int16_t  temp_min_celsius;      // Мінімальна робоча температура (°C)
    int16_t  temp_max_celsius;      // Максимальна робоча температура (°C)
    uint32_t crypto_key_bits;       // Довжина симетричного ключа (біт)
    bool     has_custom_crypto;     // Наявність власного криптографічного протоколу
    uint32_t imu_bias_drift_mdeg_h; // Дрейф гіроскопа (міліградуси на годину, 500 = 0.5 °/год)
    uint32_t rad_hardness_krad;     // Радіаційна стійкість (krad Si)
    uint32_t us_origin_cost_cents;  // Вартість компонентів походженням зі США (центи)
    uint32_t total_product_cost_cents; // Повна ринкова собівартість виробу (центи)
    char     dest_country_iso[3];   // Дволітерний код країни призначення (наприклад, "DE", "UA", "IR")
    bool     is_military_end_user;  // Прапорець кінцевого військового використання
} ProductExportSpec;

// Структура підсумкового звіту класифікації
typedef struct {
    char       eccn_code[MAX_ECCN_LEN];
    ExportMode mode;
    uint8_t    de_minimis_percent;
    char       primary_control_reason[MAX_REASON_LEN];
} ExportComplianceReport;

// Перевірка списку країн під суворим ембарго
static bool is_embargoed_country(const char* iso) {
    static const char* const EMBARGO_LIST[] = {"CU", "IR", "KP", "SY", "RU", "BY"};
    const size_t list_size = sizeof(EMBARGO_LIST) / sizeof(EMBARGO_LIST[0]);
    for (size_t i = 0; i < list_size; ++i) {
        if (strncmp(iso, EMBARGO_LIST[i], 2) == 0) {
            return true;
        }
    }
    return false;
}

// Головна функція класифікації та аудиту
bool evaluate_export_compliance(const ProductExportSpec* spec, ExportComplianceReport* report) {
    if (!spec || !report) {
        return false;
    }

    memset(report, 0, sizeof(ExportComplianceReport));
    strncpy(report->eccn_code, "EAR99", MAX_ECCN_LEN - 1);
    report->mode = EXPORT_MODE_NLR;
    strncpy(report->primary_control_reason, "None (Commercial EAR99)", MAX_REASON_LEN - 1);

    // 1. Розрахунок частки De Minimis
    if (spec->total_product_cost_cents > 0) {
        uint64_t calc = ((uint64_t)spec->us_origin_cost_cents * 100ULL) / spec->total_product_cost_cents;
        report->de_minimis_percent = (calc > 100) ? 100 : (uint8_t)calc;
    }

    // 2. Аналіз технічних порогових характеристик
    if (spec->rad_hardness_krad >= 500) {
        strncpy(report->eccn_code, "3A001.a.1", MAX_ECCN_LEN - 1);
        report->mode = EXPORT_MODE_LICENSE_REQUIRED;
        strncpy(report->primary_control_reason, "Radiation Hardness >= 500 krad(Si)", MAX_REASON_LEN - 1);
    } else if (spec->imu_bias_drift_mdeg_h > 0 && spec->imu_bias_drift_mdeg_h <= 500) {
        strncpy(report->eccn_code, "7A002", MAX_ECCN_LEN - 1);
        report->mode = EXPORT_MODE_LICENSE_REQUIRED;
        strncpy(report->primary_control_reason, "Navigation-Grade Gyro Drift <= 0.5 deg/hr", MAX_REASON_LEN - 1);
    } else if (spec->adc_resolution_bits >= 10 && spec->adc_sample_rate_sps >= 1000000000U) {
        strncpy(report->eccn_code, "3A001.a.5", MAX_ECCN_LEN - 1);
        report->mode = EXPORT_MODE_LICENSE_REQUIRED;
        strncpy(report->primary_control_reason, "High-Speed ADC >= 1 GSPS at >= 10-bit", MAX_REASON_LEN - 1);
    } else if (spec->temp_min_celsius <= -55 && spec->temp_max_celsius >= 125) {
        strncpy(report->eccn_code, "3A001.a.2", MAX_ECCN_LEN - 1);
        report->mode = EXPORT_MODE_LICENSE_REQUIRED;
        strncpy(report->primary_control_reason, "Military Temp Range (-55C to +125C)", MAX_REASON_LEN - 1);
    } else if (spec->crypto_key_bits > 56) {
        if (spec->has_custom_crypto) {
            strncpy(report->eccn_code, "5A002.a.1", MAX_ECCN_LEN - 1);
            report->mode = EXPORT_MODE_LICENSE_REQUIRED;
            strncpy(report->primary_control_reason, "Dual-Use Proprietary Cryptography", MAX_REASON_LEN - 1);
        } else {
            strncpy(report->eccn_code, "5A992.c", MAX_ECCN_LEN - 1);
            report->mode = EXPORT_MODE_LICENSE_EXCEPTION_ENC;
            strncpy(report->primary_control_reason, "Mass Market Cryptography (Note 4)", MAX_REASON_LEN - 1);
        }
    }

    // 3. Перевірка країни та кінцевого використання
    if (is_embargoed_country(spec->dest_country_iso)) {
        report->mode = EXPORT_MODE_PROHIBITED_EMBARGO;
        strncpy(report->primary_control_reason, "Sanctioned/Embargoed Destination", MAX_REASON_LEN - 1);
    } else if (spec->is_military_end_user && report->mode != EXPORT_MODE_LICENSE_REQUIRED) {
        report->mode = EXPORT_MODE_LICENSE_REQUIRED;
        strncpy(report->primary_control_reason, "Military End-User (MEU) Restriction", MAX_REASON_LEN - 1);
    }

    return true;
}
```
```cpp
#include <cstdint>
#include <string_view>
#include <array>
#include <algorithm>

namespace notary::compliance {

enum class ExportMode : uint8_t {
    NoLicenseRequired,
    LicenseExceptionEnc,
    LicenseRequired,
    ProhibitedEmbargo
};

struct ProductExportSpec {
    uint32_t         adc_sample_rate_sps{0};
    uint8_t          adc_resolution_bits{0};
    int16_t          temp_min_celsius{0};
    int16_t          temp_max_celsius{0};
    uint32_t         crypto_key_bits{0};
    bool             has_custom_crypto{false};
    uint32_t         imu_bias_drift_mdeg_h{0};
    uint32_t         rad_hardness_krad{0};
    uint32_t         us_origin_cost_cents{0};
    uint32_t         total_product_cost_cents{0};
    std::string_view dest_country_iso{"UA"};
    bool             is_military_end_user{false};
};

struct ExportComplianceReport {
    std::string_view eccn_code{"EAR99"};
    ExportMode       mode{ExportMode::NoLicenseRequired};
    uint8_t          de_minimis_percent{0};
    std::string_view primary_control_reason{"None (Commercial EAR99)"};
};

class EccnClassifierEngine {
private:
    static constexpr std::array<std::string_view, 6> EMBARGO_COUNTRIES = {
        "CU", "IR", "KP", "SY", "RU", "BY"
    };

    [[nodiscard]] static constexpr bool is_embargoed(std::string_view iso) noexcept {
        return std::ranges::any_of(EMBARGO_COUNTRIES, [iso](std::string_view entry) {
            return entry == iso;
        });
    }

    [[nodiscard]] static constexpr uint8_t calculate_de_minimis(uint32_t us_cost, uint32_t total_cost) noexcept {
        if (total_cost == 0) {
            return 0;
        }
        const uint64_t percent = (static_cast<uint64_t>(us_cost) * 100ULL) / total_cost;
        return static_cast<uint8_t>(std::min<uint64_t>(percent, 100ULL));
    }

public:
    [[nodiscard]] static constexpr ExportComplianceReport evaluate(const ProductExportSpec& spec) noexcept {
        ExportComplianceReport report{};
        report.de_minimis_percent = calculate_de_minimis(spec.us_origin_cost_cents, spec.total_product_cost_cents);

        // 1. Аналіз технічних характеристик
        if (spec.rad_hardness_krad >= 500) {
            report.eccn_code = "3A001.a.1";
            report.mode = ExportMode::LicenseRequired;
            report.primary_control_reason = "Radiation Hardness >= 500 krad(Si)";
        } else if (spec.imu_bias_drift_mdeg_h > 0 && spec.imu_bias_drift_mdeg_h <= 500) {
            report.eccn_code = "7A002";
            report.mode = ExportMode::LicenseRequired;
            report.primary_control_reason = "Navigation-Grade Gyro Drift <= 0.5 deg/hr";
        } else if (spec.adc_resolution_bits >= 10 && spec.adc_sample_rate_sps >= 1'000'000'000U) {
            report.eccn_code = "3A001.a.5";
            report.mode = ExportMode::LicenseRequired;
            report.primary_control_reason = "High-Speed ADC >= 1 GSPS at >= 10-bit";
        } else if (spec.temp_min_celsius <= -55 && spec.temp_max_celsius >= 125) {
            report.eccn_code = "3A001.a.2";
            report.mode = ExportMode::LicenseRequired;
            report.primary_control_reason = "Military Temp Range (-55C to +125C)";
        } else if (spec.crypto_key_bits > 56) {
            if (spec.has_custom_crypto) {
                report.eccn_code = "5A002.a.1";
                report.mode = ExportMode::LicenseRequired;
                report.primary_control_reason = "Dual-Use Proprietary Cryptography";
            } else {
                report.eccn_code = "5A992.c";
                report.mode = ExportMode::LicenseExceptionEnc;
                report.primary_control_reason = "Mass Market Cryptography (Note 4)";
            }
        }

        // 2. Аналіз географічних та кінцевих обмежень
        if (is_embargoed(spec.dest_country_iso)) {
            report.mode = ExportMode::ProhibitedEmbargo;
            report.primary_control_reason = "Sanctioned/Embargoed Destination";
        } else if (spec.is_military_end_user && report.mode != ExportMode::LicenseRequired) {
            report.mode = ExportMode::LicenseRequired;
            report.primary_control_reason = "Military End-User (MEU) Restriction";
        }

        return report;
    }
};

} // namespace notary::compliance
```
:::

## Інженерні пастки та крайові випадки верифікації

Під час інтеграції класифікаційного рушія в конвеєр розробки та виробництва інженерам необхідно враховувати специфічні крайові ситуації:

1. **Багатомодульні системи та вбудовані SoC:** Сучасні гетерогенні процесори містять на одному кристалі стандартні процесорні ядра загального призначення та спеціалізовані апаратні периферійні блоки (криптографічні рушії, високошвидкісні перетворювачі сигналів, блоки векторних прискорювачів). Юридична класифікація виробу завжди здійснюється за **найсуворішим** із наявних внутрішніх модулів. Навіть якщо прискорювач шифрування не використовується прикладною програмою, його фізична присутність на кристалі визначає кінцевий ECCN.
2. **Динаміка розрахунку De Minimis при коливаннях собівартості:** Ринкова ціна готового виробу та вартість імпортних електронних компонентів можуть коливатися залежно від обсягу партій, логістичних витрат та валютних курсів. Зниження собівартості локальної збірки за незмінної ціни імпортованого американського мікроконтролера може призвести до перевищення порогу 25%, що несподівано поширює дію регламенту EAR на продукт, який раніше не підпадав під обмеження.
3. **Оновлення прошивок через бездротовий канал (OTA):** Програмне оновлення, яке активує нові частотні діапазони радіомодуля, додає механізми тунелювання трафіку з ключами понад 56 біт або знімає штучні обмеження частоти вибірки сенсорів, юридично кваліфікується як експорт нового програмного забезпечення за категоріями `5D002` або `3D001`.
4. **Контроль технічних даних у хмарних сервісах:** Збереження вихідних текстів прошивок чи схемотехнічних файлів у публічних сховищах або хмарних репозиторіях із серверами за межами національної юрисдикції розглядається як передача технологій (уявний експорт), якщо доступ до них не захищено наскрізним шифруванням, схваленим регулятором.

## Тестові вектори та інтеграція у заводський конвеєр

Для гарантування надійності класифікатора вбудоване програмне забезпечення стенда фінального тестування (FCT — *Functional Circuit Test*) виконує верифікацію набору еталонних конфігурацій перед прошивкою серійного номера та криптографічних сертифікатів:

| Тестовий сценарій | Вхідні параметри виробу | Очікуваний код ECCN | Режим експорту | Першопричина обмеження |
|---|---|---|---|---|
| **Цивільний телеметричний трекер** | АЦП 12-біт 100 kSPS, діапазон -40..+85 °C, TLS 1.3 (Note 4), дрейф IMU 5.0 °/год, US cost 15% | `5A992.c` | `EXPORT_MODE_LICENSE_EXCEPTION_ENC` | Масова криптографія загального призначення |
| **Високошвидкісний SDR-приймач** | АЦП 14-біт 2.5 GSPS, діапазон -40..+85 °C, без шифрування, US cost 30% | `3A001.a.5` | `EXPORT_MODE_LICENSE_REQUIRED` | Швидкодія АЦП ≥ 1 GSPS при ≥ 10 біт |
| **Авіаційний навігаційний модуль** | IMU дрейф 0.1 °/год, діапазон -55..+125 °C, US cost 10% | `7A002` | `EXPORT_MODE_LICENSE_REQUIRED` | Стабільність нуля гіроскопа ≤ 0.5 °/год |
| **Радіаційностійкий космічний контролер** | Стійкість TID 600 krad(Si), діапазон -55..+125 °C | `3A001.a.1` | `EXPORT_MODE_LICENSE_REQUIRED` | Накопичена доза випромінювання ≥ 500 krad(Si) |
| **Постачання підсанкційному покупцеві** | Цивільний прилад EAR99, але країна призначення `RU` або прапорець `is_military_end_user = true` | `EAR99` | `EXPORT_MODE_PROHIBITED_EMBARGO` / `LICENSE_REQUIRED` | Санкційні списки або військовий кінцевий споживач |

Якщо функція `evaluate_export_compliance()` повертає `EXPORT_MODE_PROHIBITED_EMBARGO` або `EXPORT_MODE_LICENSE_REQUIRED` без підтвердженого номера експортної ліцензії в базі ERP підприємства, заводський програматор блокує запис робочого ключа підпису, унеможливлюючи несанкціоноване відвантаження продукції.
