# ⚙️ Арбітр реліз-кандидатів: автоматизована перевірка артефактів, бюджетів та HIL-звітів

Під час підготовки прошивки до масового виробництва ручна перевірка протоколів тестування та розмірів бінарних образів стає джерелом критичних помилок. Забутий тестовий прапорець компіляції, непомітне розростання секції `.bss` або одиничний збій на стенді Hardware-in-the-Loop (HIL), проігнорований інженером під час нічного релізу, перетворюють партію пристроїв на заводський брак.

Автоматизований арбітр якості (Quality Gate Arbiter) розв'язує цю проблему: він виконує машинну верифікацію критеріїв виходу, перевіряє ліміти апаратних ресурсів за даними лінкера, валідує логи тестів і приймає детерміноване рішення про промоцію кандидата в релізний образ.

---

## 1. Архітектура та математична модель верифікації

Арбітр аналізує бінарний стан системи через три незалежні проекції: розподіл пам'яті, результати апаратних тестів та енергетичні показники.

### Розрахунок бюджетів пам'яті

Для мікроконтролерів із фіксованим обсягом Flash ROM та SRAM сумарне використання пам'яті обчислюється на основі аналізу секцій об'єктного файлу (ELF) або мапи компонування (`.map`):

```
Flash_Used = Size(.text) + Size(.rodata) + Size(.data)
SRAM_Used  = Size(.data) + Size(.bss) + Size(.noinit)
```

Секція `.data` враховується в обох бюджетах: її початкові значення зберігаються у Flash-пам'яті (LMA, Load Memory Address) і копіюються завантажувальним кодом у SRAM (VMA, Virtual Memory Address) під час старту мікроконтролера. Секція `.bss` ініціалізується нулями тільки в SRAM.

Вільний простір стеку перевіряється за методом водного знаку (Stack Watermarking): під час ініціалізації вся область оперативної пам'яті, виділена під стек, заповнюється сигнатурним шаблоном (наприклад, `0xA5A5A5A5` або `0xDEADBEEF`). Після завершення 72-годинного стрес-тесту арбітр сканує пам'ять від дна стеку вгору й знаходить першу адресу, де шаблон було перезаписано даними вкладених функцій та обробників переривань (ISR).

---

## 2. Реалізація арбітра релізу (C та C++)

Нижче наведено робочу реалізацію аналізатора та валідатора критеріїв виходу.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_DEFECTS_LIMIT 0
#define MAX_FLASH_BYTES (8 * 1024 * 1024 + 512 * 1024) /* 8.5 MiB */
#define MAX_RAM_BYTES   (384 * 1024)                    /* 384 KiB */
#define MAX_BOOT_TIME_MS 250
#define MAX_SLEEP_CURRENT_UA 15.0f

typedef struct {
    uint32_t flash_used_bytes;
    uint32_t ram_used_bytes;
    uint32_t boot_time_ms;
    float sleep_current_ua;
    uint32_t hil_total_tests;
    uint32_t hil_passed_tests;
    uint32_t critical_defects_count;
    bool hardfault_occurred;
    bool watchdog_reset_occurred;
} ReleaseCandidateMetrics;

typedef enum {
    DECISION_PROMOTED_GA = 0,
    DECISION_REJECTED_BUDGET_OVERRUN = 1,
    DECISION_REJECTED_HIL_FAILURE = 2,
    DECISION_REJECTED_CRITICAL_BUGS = 3,
    DECISION_REJECTED_SYSTEM_FAULT = 4
} GateDecision;

typedef struct {
    GateDecision decision;
    char reason[256];
    char candidate_sha256[65];
} EvaluationResult;

GateDecision evaluate_release_candidate(const ReleaseCandidateMetrics* metrics,
                                        const char* binary_sha256,
                                        EvaluationResult* out_result) {
    if (!metrics || !binary_sha256 || !out_result) {
        return DECISION_REJECTED_SYSTEM_FAULT;
    }

    memset(out_result, 0, sizeof(EvaluationResult));
    strncpy(out_result->candidate_sha256, binary_sha256, 64);

    /* 1. Перевірка блокуючих дефектів */
    if (metrics->critical_defects_count > MAX_DEFECTS_LIMIT) {
        out_result->decision = DECISION_REJECTED_CRITICAL_BUGS;
        snprintf(out_result->reason, sizeof(out_result->reason),
                 "Відхилено: виявлено %u критичних дефектів (ліміт: %u)",
                 metrics->critical_defects_count, MAX_DEFECTS_LIMIT);
        return out_result->decision;
    }

    /* 2. Перевірка апаратних збоїв на стенді */
    if (metrics->hardfault_occurred || metrics->watchdog_reset_occurred) {
        out_result->decision = DECISION_REJECTED_SYSTEM_FAULT;
        snprintf(out_result->reason, sizeof(out_result->reason),
                 "Відхилено: зафіксовано фатальні збої (HardFault=%d, WDT_Reset=%d)",
                 metrics->hardfault_occurred, metrics->watchdog_reset_occurred);
        return out_result->decision;
    }

    /* 3. Перевірка 100% успішності HIL-тестів */
    if (metrics->hil_total_tests == 0 || metrics->hil_passed_tests < metrics->hil_total_tests) {
        out_result->decision = DECISION_REJECTED_HIL_FAILURE;
        snprintf(out_result->reason, sizeof(out_result->reason),
                 "Відхилено: HIL-тести не пройдено на 100%% (%u з %u успішних)",
                 metrics->hil_passed_tests, metrics->hil_total_tests);
        return out_result->decision;
    }

    /* 4. Перевірка бюджетів флеш-пам'яті та ОЗП */
    if (metrics->flash_used_bytes > MAX_FLASH_BYTES) {
        out_result->decision = DECISION_REJECTED_BUDGET_OVERRUN;
        snprintf(out_result->reason, sizeof(out_result->reason),
                 "Відхилено: перевищення Flash ROM (%u байт > %u ліміт)",
                 metrics->flash_used_bytes, MAX_FLASH_BYTES);
        return out_result->decision;
    }

    if (metrics->ram_used_bytes > MAX_RAM_BYTES) {
        out_result->decision = DECISION_REJECTED_BUDGET_OVERRUN;
        snprintf(out_result->reason, sizeof(out_result->reason),
                 "Відхилено: перевищення SRAM (%u байт > %u ліміт)",
                 metrics->ram_used_bytes, MAX_RAM_BYTES);
        return out_result->decision;
    }

    /* 5. Перевірка енергоспоживання та часу запуску */
    if (metrics->sleep_current_ua > MAX_SLEEP_CURRENT_UA) {
        out_result->decision = DECISION_REJECTED_BUDGET_OVERRUN;
        snprintf(out_result->reason, sizeof(out_result->reason),
                 "Відхилено: струм сну %.2f мкА перевищує поріг %.2f мкА",
                 metrics->sleep_current_ua, MAX_SLEEP_CURRENT_UA);
        return out_result->decision;
    }

    if (metrics->boot_time_ms > MAX_BOOT_TIME_MS) {
        out_result->decision = DECISION_REJECTED_BUDGET_OVERRUN;
        snprintf(out_result->reason, sizeof(out_result->reason),
                 "Відхилено: час завантаження %u мс перевищує ліміт %u мс",
                 metrics->boot_time_ms, MAX_BOOT_TIME_MS);
        return out_result->decision;
    }

    out_result->decision = DECISION_PROMOTED_GA;
    snprintf(out_result->reason, sizeof(out_result->reason),
             "СХВАЛЕНО: Всі вихідні критерії виконано. Кандидат готовий до промоції в GA.");
    return DECISION_PROMOTED_GA;
}

int main(void) {
    ReleaseCandidateMetrics rc_sample = {
        .flash_used_bytes = 4194304, /* 4 MiB */
        .ram_used_bytes = 196608,   /* 192 KiB */
        .boot_time_ms = 180,
        .sleep_current_ua = 11.4f,
        .hil_total_tests = 1450,
        .hil_passed_tests = 1450,
        .critical_defects_count = 0,
        .hardfault_occurred = false,
        .watchdog_reset_occurred = false
    };

    const char* sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";
    EvaluationResult res;

    GateDecision status = evaluate_release_candidate(&rc_sample, sha256, &res);

    printf("=== РЕЗУЛЬТАТ АРБІТРАЖУ РЕЛІЗ-КАНДИДАТА ===\n");
    printf("Статус рішення: %d\n", status);
    printf("Обґрунтування : %s\n", res.reason);
    printf("SHA-256 образу: %s\n", res.candidate_sha256);

    return (status == DECISION_PROMOTED_GA) ? 0 : 1;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <expected>
#include <cstdint>
#include <format>
#include <span>

namespace ReleaseEngineering {

struct Budgets {
    static constexpr uint32_t MaxFlashBytes = 8 * 1024 * 1024 + 512 * 1024; // 8.5 MiB
    static constexpr uint32_t MaxRamBytes = 384 * 1024;                     // 384 KiB
    static constexpr uint32_t MaxBootTimeMs = 250;
    static constexpr float MaxSleepCurrentMicroAmps = 15.0f;
    static constexpr uint32_t MaxAllowedBlockers = 0;
};

struct CandidateMetrics {
    uint32_t flashUsedBytes{0};
    uint32_t ramUsedBytes{0};
    uint32_t bootTimeMs{0};
    float sleepCurrentMicroAmps{0.0f};
    uint32_t hilTotalTests{0};
    uint32_t hilPassedTests{0};
    uint32_t criticalDefectsCount{0};
    bool hardfaultOccurred{false};
    bool watchdogResetOccurred{false};
};

enum class RejectionReason {
    CriticalBugsPresent,
    FatalHardwareFault,
    HilTestsIncomplete,
    FlashOverrun,
    RamOverrun,
    PowerBudgetExceeded,
    BootTimeExceeded
};

struct PromotionCertificate {
    std::string releaseTag;
    std::string sha256Hash;
    std::string approvalSummary;
};

class QualityGateArbiter {
public:
    static std::expected<PromotionCertificate, std::pair<RejectionReason, std::string>>
    evaluate(std::string_view releaseTag,
             std::string_view sha256Hash,
             const CandidateMetrics& m) noexcept {
        
        // 1. Нульовий рівень критичних багів
        if (m.criticalDefectsCount > Budgets::MaxAllowedBlockers) {
            return std::unexpected(std::make_pair(
                RejectionReason::CriticalBugsPresent,
                std::format("Знайдено {} критичних багів при ліміті {}",
                            m.criticalDefectsCount, Budgets::MaxAllowedBlockers)
            ));
        }

        // 2. Відсутність апаратних панік
        if (m.hardfaultOccurred || m.watchdogResetOccurred) {
            return std::unexpected(std::make_pair(
                RejectionReason::FatalHardwareFault,
                std::format("Зафіксовано апаратний збій (HardFault={}, WDT={})",
                            m.hardfaultOccurred, m.watchdogResetOccurred)
            ));
        }

        // 3. 100% проходження HIL
        if (m.hilTotalTests == 0 || m.hilPassedTests < m.hilTotalTests) {
            return std::unexpected(std::make_pair(
                RejectionReason::HilTestsIncomplete,
                std::format("HIL верифікація неповна: {}/{} успішно",
                            m.hilPassedTests, m.hilTotalTests)
            ));
        }

        // 4. Перевірка обсягів пам'яті
        if (m.flashUsedBytes > Budgets::MaxFlashBytes) {
            return std::unexpected(std::make_pair(
                RejectionReason::FlashOverrun,
                std::format("Flash ROM {} перевищує ліміт {}",
                            m.flashUsedBytes, Budgets::MaxFlashBytes)
            ));
        }

        if (m.ramUsedBytes > Budgets::MaxRamBytes) {
            return std::unexpected(std::make_pair(
                RejectionReason::RamOverrun,
                std::format("SRAM {} перевищує ліміт {}",
                            m.ramUsedBytes, Budgets::MaxRamBytes)
            ));
        }

        // 5. Енергетичний та часовий бюджет
        if (m.sleepCurrentMicroAmps > Budgets::MaxSleepCurrentMicroAmps) {
            return std::unexpected(std::make_pair(
                RejectionReason::PowerBudgetExceeded,
                std::format("Струм сну {:.2f} uA > {:.2f} uA ліміту",
                            m.sleepCurrentMicroAmps, Budgets::MaxSleepCurrentMicroAmps)
            ));
        }

        if (m.bootTimeMs > Budgets::MaxBootTimeMs) {
            return std::unexpected(std::make_pair(
                RejectionReason::BootTimeExceeded,
                std::format("Час старту {} мс > {} мс ліміту",
                            m.bootTimeMs, Budgets::MaxBootTimeMs)
            ));
        }

        return PromotionCertificate{
            .releaseTag = std::string(releaseTag),
            .sha256Hash = std::string(sha256Hash),
            .approvalSummary = "Усі критерії виходу виконано на 100%. Готово до підпису GA."
        };
    }
};

} // namespace ReleaseEngineering

int main() {
    using namespace ReleaseEngineering;

    CandidateMetrics metrics{
        .flashUsedBytes = 4194304,
        .ramUsedBytes = 196608,
        .bootTimeMs = 180,
        .sleepCurrentMicroAmps = 11.4f,
        .hilTotalTests = 1450,
        .hilPassedTests = 1450,
        .criticalDefectsCount = 0,
        .hardfaultOccurred = false,
        .watchdogResetOccurred = false
    };

    auto result = QualityGateArbiter::evaluate(
        "v2.4.0-rc.3",
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        metrics
    );

    if (result.has_value()) {
        const auto& cert = result.value();
        std::cout << "=== СЕРТИФІКАТ ПРОМОЦІЇ GA ===\n";
        std::cout << "Тег релізу : " << cert.releaseTag << "\n";
        std::cout << "SHA-256    : " << cert.sha256Hash << "\n";
        std::cout << "Підсумок   : " << cert.approvalSummary << "\n";
        return 0;
    } else {
        const auto& [err, msg] = result.error();
        std::cerr << "=== ВІДХИЛЕННЯ РЕЛІЗ-КАНДИДАТА ===\n";
        std::cerr << "Причина: " << msg << "\n";
        return 1;
    }
}
```
:::

---

## 3. Практичний розбір критичних ситуацій та крайових випадків

### 1. Недетермінованість компіляції (`__DATE__`, `__TIME__`, шляхи хоста)

Якщо компілятор вставляє поточний час збірки у бінарний файл через системні макроси, кожна наступна компіляція того самого коміту генеруватиме інший SHA-256 хеш. Арбітр визнає такий бінарник стороннім артефактом, заблокувавши випуск на заводську лінію.

Для усунення проблеми в систему збірки CMake/Makefile додаються прапорці детермінізму:
- `-Werror=date-time`: примусова заборона використання макросів часу в коді.
- `-ffile-prefix-map=$(PWD)=.`: видалення абсолютних шляхів файлової системи хоста, що гарантує однаковий DWARF-вивід незалежно від каталогу компіляції.
- Встановлення фіксованого значення змінної `SOURCE_DATE_EPOCH` у конвеєрі.

### 2. Ігнорування імпульсного споживання струму під час запуску радіомодуля

Класичною пасткою під час верифікації енергоспоживання є орієнтація на середній струм споживання мультиметра. Під час старту радіопередавача (Wi-Fi/BLE/LTE-M) споживання стрибає з 15 мкА до 120 мА за частки мікросекунди.

Якщо ємність згладжувальних конденсаторів біля виводів живлення мікроконтролера розрахована без запасу або деградує при низькій температурі (-20 °C), виникає різке просідання напруги шини живлення `V_DD`. Внутрішній компаратор мікроконтролера фіксує падіння нижче порогу `V_BOR` і генерує `Brownout Reset`. Арбітр HIL-стенду зобов'язаний зчитувати логи спеціалізованого осцилографа-профайлера струму для фіксації пікових імпульсів.

### 3. Стекова колізія під час вкладених переривань (ISR Stack Exhaustion)

Окремі функціональні тести виконуються у власних ізольованих контекстах і не створюють максимального навантаження на пам'ять. Справжній пік використання стеку виникає у випадку, коли під час глибокого стеку викликів алгоритму обробки криптографії одночасно надходять два апаратних переривання: спочатку таймер вищого пріоритету, а всередині нього — термінове переривання аварії шини живлення.

Регістри процесора автоматично зберігаються в поточному стеку, що призводить до виходу покажчика стеку `SP` за межі виділеної області пам'яті та перезапису змінних секції `.bss`. Арбітр вимагає обов'язкового проходження тесту зі штучною генерацією лавини переривань (Interrupt Storm Stress Test) для підтвердження мінімального запасу стеку (не менше 4096 байт вільного водного знаку).

---

## 4. Інтеграція в конвеєр автоматизованої збірки

Арбітр виконується на фінальному етапі конвеєра CI після завершення прогону апаратної ферми. Він агрегує дані з кількох системних джерел:

```
[Збірка ELF/BIN] ──> [Утиліта size / .map] ──┐
                                             ├──> [RC Gate Arbiter] ──> [Підпис HSM / GA]
[HIL Ферма]      ──> [JSON звіт pytest-hil] ─┘
```

1. **Отримання розмірів через GNU binutils**:
   Конвеєр виконує виклик `arm-none-eabi-size -A firmware.elf` та передає вивід у парсер арбітра. Це усуває залежність від текстових звітів IDE.
2. **Верифікація логів тестового фреймворку**:
   Фреймворк автоматизації HIL (наприклад, на базі pytest із плагінами для логічних аналізаторів Saleae та програматорів J-Link) генерує структурований звіт про статус виконання кожного тесту, час відповіді пристрою по шині CAN та відсутність перехоплених HardFault винятків.
3. **Генерація сертифіката промоції**:
   У разі позитивного вердикту арбітр записує файл `promotion-cert.json`, що містить SHA-256 хеш артефакту, підпис оцінювача та точну дату верифікації. Тільки за наявності цього файлу відкривається доступ до криптографічного ключа підпису релізу.

---

## 5. Валідація зносу секторів флеш-пам'яті (Flash Wear & Endurance Gate)

Окремим прихованим ризиком у вбудованих пристроях є передчасна деградація енергонезалежної пам'яті (NOR/NAND Flash) через неоптимальний алгоритм збереження телеметрії або логів під час стрес-тесту. 

Якщо логіка прошивки виконує синхронний запис дрібних структур безпосередньо у флеш-сектор без буферизації та вирівнювання зносу (Wear Leveling), ліміт у 10 000 – 100 000 циклів стирання сектору може бути вичерпаний за кілька місяців польової експлуатації.

Арбітр випускних воріт якості зчитує лічильники циклів стирання (Erase Cycle Counters) з діагностичного сектору пам'яті HIL-стенду до початку та після завершення 72-годинного стрес-прогону:
- Допустимий приріст циклів стирання за час тестування не повинен перевищувати розрахункову норму річного ресурсу (наприклад, не більше 50 циклів стирання на добу під максимальним трафіком).
- Перевищення цього ліміту автоматично класифікується як критичний дефект P1 і блокує перехід кандидата в статус GA до оптимізації алгоритму збереження даних у файловій системі.
