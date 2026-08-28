# ⚙️ Конвеєр класифікації інцидентів та обчислення строків сповіщення

Коли черговий аналітик центру моніторингу безпеки (SOC) або інженер групи реагування на інциденти (PSIRT) фіксує ознаки несанкціонованого проникнення чи активної експлуатації вразливості нульового дня, починається жорсткий зворотний відлік регуляторних таймерів. Помилка в оцінці строків навіть на кілька годин несе за собою пряму загрозу втрати комерційних ліцензій, накладення багатомільйонних штрафів з боку наглядових органів та судових позовів від клієнтів. Щоб повністю усунути людський фактор та забезпечити надійну невідмовність дій, процедури класифікації інцидентів, розрахунку граничних термінів та автоматичної ескалації передаються спеціалізованому програмному рушію тріажу.

```
+--------------------------------------------------------------------------------------------------+
| Архітектура конвеєра тріажу та диспетчеризації обов'язкових сповіщень                            |
+--------------------------------------------------------------------------------------------------+
| Джерела подій (SIEM, EDR, PSIRT, Зовнішній репорт, CVE стрічка)                                 |
|                                   │                                                              |
|                                   ▼                                                              |
| ┌──────────────────────────────────────────────────────────────────────────────────────────────┐ |
| │ Рушій тріажу (Triage Engine):                                                                │ |
| │ 1. Валідація події (активна експлуатація, витік PII, операційний збій)                       │ |
| │ 2. Визначення застосовних режимів (CRA | NIS2 | GDPR | SEC)                                   │ |
| │ 3. Запуск монотонних таймерів (24h Early Warning, 72h Detailed Notice, 4d SEC 8-K)           │ |
| └──────────────────────────────────────────────────────────────────────────────────────────────┘ |
|                                   │                                                              |
|                  ┌────────────────┴────────────────┐                                             |
|                  ▼                                 ▼                                             |
| ┌─────────────────────────────────┐ ┌──────────────────────────────────────────────────────────┐ │
| │ Диспетчер сповіщень (Notifier)  │ │ Монітор строків (Deadline Watchdog)                      │ │
| │ Формування CSAF 2.0 / JSON      │ │ Відстеження наближення дедлайнів (12h, 4h, 1h алерти)   │ │
| │ Відправка в ENISA/CSIRT/DPA     │ │ Ескалація на юридичний відділ та керівництво             │ │
| └─────────────────────────────────┘ └──────────────────────────────────────────────────────────┘ │
+--------------------------------------------------------------------------------------------------+
```

## Алгоритм роботи, структура даних та модель станів

Програмний комплекс тріажу побудований навколо кінцевого автомата (*Finite State Machine*, FSM), який відстежує життєвий цикл безпекової події та фіксує чотири ключові часові відмітки:

1. **Мітка фізичного виявлення (`detected_at`):** Момент часу за шкалою UTC, коли датчик IDS, лог або зовнішній лист дослідника вперше надійшов до системи. Ця мітка є строго незмінною і слугує точкою відліку для внутрішніх криміналістичних розслідувань.
2. **Мітка юридичного усвідомлення (`awareness_at`):** Момент, коли чергова зміна SOC або інженер PSIRT підтвердила достовірність інциденту. Саме від цієї секунди європейські регламенти (Стаття 33 GDPR, Стаття 14 CRA, Стаття 23 NIS 2) починають відлік 24-годинних та 72-годинних вікон.
3. **Мітка матеріальності (`materiality_at`):** Момент, коли колегія керівництва або офіцер з кібербезпеки (CISO) кваліфікували інцидент як матеріальний для публічної фінансової звітності. Ця мітка запускає чотириденний таймер форми SEC 8-K.
4. **Мітка завершення та виправлення (`mitigated_at`):** Момент випуску стабільного виправлення або застосування захисних правил, від якого відраховуються фінальні строки (14 днів за CRA, 1 місяць за NIS 2).

Кожна безпекова подія проходить крізь фільтр класифікаційних правил, де комбінація технічних ознак (наявність активного експлойта в мережі, компрометація конфіденційних таблиць бази даних, відмова мережевого шлюзу) перетворюється на набір активних прапорців нормативних режимів. Якщо подія зачіпає декілька юрисдикцій одночасно, рушій обчислює незалежні дедлайни для кожного каналу зв'язку та призначає індивідуальні рівні попередження для чергових офіцерів.

Нижче наведено повноцінну інженерну реалізацію логіки тріажу, валідації прапорців режимів та обчислення часових інтервалів мовами C та C++.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

#define REGIME_CRA   (1U << 0)
#define REGIME_NIS2  (1U << 1)
#define REGIME_GDPR  (1U << 2)
#define REGIME_SEC   (1U << 3)

typedef enum {
    SEVERITY_LOW = 0,
    SEVERITY_MEDIUM,
    SEVERITY_HIGH,
    SEVERITY_CRITICAL
} IncidentSeverity;

typedef enum {
    STATE_NEW = 0,
    STATE_TRIAGED,
    STATE_EARLY_WARNING_SENT,
    STATE_DETAILED_NOTICE_SENT,
    STATE_FINAL_REPORT_SENT,
    STATE_CLOSED
} IncidentState;

typedef struct {
    uint64_t incident_id;
    uint32_t active_regimes;
    IncidentSeverity severity;
    IncidentState state;
    time_t detected_at;
    time_t awareness_at;
    time_t early_warning_deadline;
    time_t detailed_notice_deadline;
    time_t final_report_deadline;
    bool has_active_exploit;
    bool pii_compromised;
    bool operational_outage;
} IncidentContext;

/* Додавання робочих днів для вимог SEC (виключаючи суботу й неділю) */
time_t add_business_days(time_t start, int days) {
    struct tm tm_buf;
    time_t current = start;
    int added = 0;

    while (added < days) {
        current += 86400; /* +24 години */
        gmtime_r(&current, &tm_buf);
        if (tm_buf.tm_wday != 0 && tm_buf.tm_wday != 6) {
            added++;
        }
    }
    return current;
}

int incident_triage_init(IncidentContext *ctx, uint64_t id, time_t detected_at) {
    if (!ctx) return -1;
    memset(ctx, 0, sizeof(*ctx));
    ctx->incident_id = id;
    ctx->detected_at = detected_at;
    ctx->awareness_at = detected_at;
    ctx->state = STATE_NEW;
    return 0;
}

void incident_evaluate_regimes(IncidentContext *ctx) {
    ctx->active_regimes = 0;

    /* CRA: активно експлуатована вразливість у продукті */
    if (ctx->has_active_exploit) {
        ctx->active_regimes |= REGIME_CRA;
    }

    /* NIS 2: операційний збій чи суттєвий вплив на сервіси */
    if (ctx->operational_outage || ctx->severity >= SEVERITY_HIGH) {
        ctx->active_regimes |= REGIME_NIS2;
    }

    /* GDPR: несанкціонований доступ або витік персональних даних */
    if (ctx->pii_compromised) {
        ctx->active_regimes |= REGIME_GDPR;
    }

    /* SEC: критичні збитки для публічної компанії */
    if (ctx->severity == SEVERITY_CRITICAL) {
        ctx->active_regimes |= REGIME_SEC;
    }

    /* Розрахунок дедлайнів від моменту усвідомлення (awareness_at) */
    if (ctx->active_regimes & (REGIME_CRA | REGIME_NIS2)) {
        ctx->early_warning_deadline = ctx->awareness_at + (24 * 3600);
        ctx->detailed_notice_deadline = ctx->awareness_at + (72 * 3600);
        ctx->final_report_deadline = ctx->awareness_at + (30 * 86400);
    } else if (ctx->active_regimes & REGIME_GDPR) {
        ctx->early_warning_deadline = 0; /* Не передбачено раннього сповіщення */
        ctx->detailed_notice_deadline = ctx->awareness_at + (72 * 3600);
        ctx->final_report_deadline = 0;
    }

    if (ctx->active_regimes & REGIME_SEC) {
        /* 4 робочі дні з моменту кваліфікації суттєвості */
        time_t sec_deadline = add_business_days(ctx->awareness_at, 4);
        if (ctx->detailed_notice_deadline == 0 || sec_deadline < ctx->detailed_notice_deadline) {
            ctx->detailed_notice_deadline = sec_deadline;
        }
    }

    ctx->state = STATE_TRIAGED;
}

void incident_check_deadlines(const IncidentContext *ctx, time_t current_time) {
    if (ctx->early_warning_deadline > 0 && ctx->state < STATE_EARLY_WARNING_SENT) {
        double diff_hours = difftime(ctx->early_warning_deadline, current_time) / 3600.0;
        if (diff_hours < 0) {
            printf("[CRITICAL] Incident #%llu: 24h Early Warning SLA BREACHED by %.1f hours!\n",
                   (unsigned long long)ctx->incident_id, -diff_hours);
        } else if (diff_hours <= 4.0) {
            printf("[WARNING] Incident #%llu: 24h Early Warning deadline in %.1f hours.\n",
                   (unsigned long long)ctx->incident_id, diff_hours);
        }
    }

    if (ctx->detailed_notice_deadline > 0 && ctx->state < STATE_DETAILED_NOTICE_SENT) {
        double diff_hours = difftime(ctx->detailed_notice_deadline, current_time) / 3600.0;
        if (diff_hours < 0) {
            printf("[CRITICAL] Incident #%llu: Detailed Notification SLA BREACHED by %.1f hours!\n",
                   (unsigned long long)ctx->incident_id, -diff_hours);
        } else if (diff_hours <= 12.0) {
            printf("[ALERT] Incident #%llu: Detailed Notification deadline in %.1f hours.\n",
                   (unsigned long long)ctx->incident_id, diff_hours);
        }
    }
}
```
@tab C++
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <optional>
#include <cstdint>
#include <format>

namespace security {

enum class RegimeFlags : uint32_t {
    None  = 0,
    CRA   = 1U << 0,
    NIS2  = 1U << 1,
    GDPR  = 1U << 2,
    SEC   = 1U << 3
};

inline constexpr RegimeFlags operator|(RegimeFlags a, RegimeFlags b) noexcept {
    return static_cast<RegimeFlags>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

inline constexpr bool has_flag(RegimeFlags mask, RegimeFlags flag) noexcept {
    return (static_cast<uint32_t>(mask) & static_cast<uint32_t>(flag)) != 0;
}

enum class Severity {
    Low,
    Medium,
    High,
    Critical
};

enum class IncidentState {
    New,
    Triaged,
    EarlyWarningDispatched,
    DetailedNoticeDispatched,
    FinalReportDispatched,
    Closed
};

class IncidentTriageEngine {
public:
    using Clock = std::chrono::system_clock;
    using TimePoint = std::chrono::time_point<Clock>;

    struct IncidentDetails {
        uint64_t id{0};
        Severity severity{Severity::Low};
        IncidentState state{IncidentState::New};
        RegimeFlags regimes{RegimeFlags::None};
        TimePoint detected_at{};
        TimePoint awareness_at{};
        std::optional<TimePoint> early_warning_deadline{};
        std::optional<TimePoint> detailed_notice_deadline{};
        std::optional<TimePoint> final_report_deadline{};
        bool has_active_exploit{false};
        bool pii_compromised{false};
        bool operational_outage{false};
    };

    explicit IncidentTriageEngine(uint64_t id, TimePoint detected = Clock::now()) {
        ctx_.id = id;
        ctx_.detected_at = detected;
        ctx_.awareness_at = detected;
        ctx_.state = IncidentState::New;
    }

    void set_exploit_observed(bool active) noexcept { ctx_.has_active_exploit = active; }
    void set_pii_compromised(bool compromised) noexcept { ctx_.pii_compromised = compromised; }
    void set_operational_outage(bool outage) noexcept { ctx_.operational_outage = outage; }
    void set_severity(Severity sev) noexcept { ctx_.severity = sev; }

    void evaluate_regimes() {
        ctx_.regimes = RegimeFlags::None;

        if (ctx_.has_active_exploit) {
            ctx_.regimes = ctx_.regimes | RegimeFlags::CRA;
        }
        if (ctx_.operational_outage || ctx_.severity >= Severity::High) {
            ctx_.regimes = ctx_.regimes | RegimeFlags::NIS2;
        }
        if (ctx_.pii_compromised) {
            ctx_.regimes = ctx_.regimes | RegimeFlags::GDPR;
        }
        if (ctx_.severity == Severity::Critical) {
            ctx_.regimes = ctx_.regimes | RegimeFlags::SEC;
        }

        if (has_flag(ctx_.regimes, RegimeFlags::CRA) || has_flag(ctx_.regimes, RegimeFlags::NIS2)) {
            ctx_.early_warning_deadline = ctx_.awareness_at + std::chrono::hours(24);
            ctx_.detailed_notice_deadline = ctx_.awareness_at + std::chrono::hours(72);
            ctx_.final_report_deadline = ctx_.awareness_at + std::chrono::hours(24 * 30);
        } else if (has_flag(ctx_.regimes, RegimeFlags::GDPR)) {
            ctx_.early_warning_deadline = std::nullopt;
            ctx_.detailed_notice_deadline = ctx_.awareness_at + std::chrono::hours(72);
            ctx_.final_report_deadline = std::nullopt;
        }

        if (has_flag(ctx_.regimes, RegimeFlags::SEC)) {
            auto sec_deadline = add_business_days(ctx_.awareness_at, 4);
            if (!ctx_.detailed_notice_deadline || sec_deadline < *ctx_.detailed_notice_deadline) {
                ctx_.detailed_notice_deadline = sec_deadline;
            }
        }

        ctx_.state = IncidentState::Triaged;
    }

    void inspect_deadlines(TimePoint now = Clock::now()) const {
        if (ctx_.early_warning_deadline && ctx_.state < IncidentState::EarlyWarningDispatched) {
            auto diff = std::chrono::duration_cast<std::chrono::minutes>(*ctx_.early_warning_deadline - now);
            double hours = diff.count() / 60.0;
            if (hours < 0.0) {
                std::cout << std::format("[CRITICAL] Incident #{}: Early Warning deadline breached by {:.1f}h!\n",
                                         ctx_.id, -hours);
            } else if (hours <= 4.0) {
                std::cout << std::format("[WARNING] Incident #{}: Early Warning deadline in {:.1f}h.\n",
                                         ctx_.id, hours);
            }
        }

        if (ctx_.detailed_notice_deadline && ctx_.state < IncidentState::DetailedNoticeDispatched) {
            auto diff = std::chrono::duration_cast<std::chrono::minutes>(*ctx_.detailed_notice_deadline - now);
            double hours = diff.count() / 60.0;
            if (hours < 0.0) {
                std::cout << std::format("[CRITICAL] Incident #{}: Detailed Notification breached by {:.1f}h!\n",
                                         ctx_.id, -hours);
            } else if (hours <= 12.0) {
                std::cout << std::format("[ALERT] Incident #{}: Detailed Notification deadline in {:.1f}h.\n",
                                         ctx_.id, hours);
            }
        }
    }

    [[nodiscard]] const IncidentDetails& details() const noexcept { return ctx_; }

private:
    static TimePoint add_business_days(TimePoint start, int days) {
        TimePoint current = start;
        int added = 0;
        while (added < days) {
            current += std::chrono::hours(24);
            auto time_t_val = Clock::to_time_t(current);
            std::tm tm_buf{};
            gmtime_r(&time_t_val, &tm_buf);
            if (tm_buf.tm_wday != 0 && tm_buf.tm_wday != 6) {
                ++added;
            }
        }
        return current;
    }

    IncidentDetails ctx_;
};

} // namespace security
```
:::

## Інженерні пастки та захист від системних помилок

Під час проектування та розгортання виробничих систем тріажу інженери стикаються з чотирма критичними технічними викликами:

1. **Стрибки системного часу та синхронізація NTP:**
   Якщо віртуальна машина або контейнер коригує системний годинник через різкий стрибок часу (*time step*), простий виклик `difftime()` може повернути некоректний або від'ємний інтервал. Це загрожує або фальшивим спрацьовуванням тривоги, або, навпаки, пропуском дедлайну сповіщення. Щоб захиститися від цього ефекту, внутрішні черги таймерів рушія зобов'язані спиратися на монотонний таймер ядра операційної системи (`CLOCK_MONOTONIC_RAW` у Linux), тоді як шкала UTC використовується виключно для серіалізації дедлайнів у зовнішні повідомлення.

2. **Розрив між первинною аномалією та підтвердженням факту:**
   Автоматизовані сенсори IDS та EDR щодня реєструють тисячі підозрілих подій. Якщо вважати кожне спрацьовування юридичним початком 24-годинного відліку, команда буде змушена безперервно надсилати регуляторам спам із хибних сповіщень. Рушій повинен чітко розмежовувати стан непідтвердженої аномалії (`STATE_NEW`) та стан верифікованої компрометації (`STATE_TRIAGED`). При цьому в журнал аудиту обов'язково записується як первинний час спрацьовування сенсора, так і час завершення первинного аналізу, що захищає компанію під час зовнішніх перевірок.

3. **Багатопотокова синхронізація та незмінність перебігу подій:**
   Коли група аналітиків паралельно досліджує різні сегменти мережі, стан інциденту може оновлюватися одночасно з кількох робочих місць. Щоб запобігти стану перегонів (*race conditions*), зміна прапорців режимів та перехід автомата станів повинні виконуватися атомарно з обов'язковою публікацією нової версії контексту в захищений від редагування лог. Це гарантує, що жодне надіслане сповіщення не буде скасоване або продубльоване внаслідок паралельних дій операторів.

4. **Політика повторних спроб та черги тупикових повідомлень:**
   Мережеві шлюзи наглядових органів або портали ENISA можуть зазнавати перевантаження або тимчасових збоїв якраз у момент масштабної світової кібератаки. Якщо диспетчер сповіщень отримає HTTP помилку `503 Service Unavailable`, він не має права скидати пакет або мовчки зупиняти конвеєр. Архітектура вимагає використання стійкої черги повідомлень (*Dead Letter Queue*) із експоненційним відступом (*exponential backoff*) та локальним криптографічним квитуванням кожної спроби надсилання, що підтверджує сумлінність дій організації у разі судового розгляду.

5. **Криптографічне скріплення контексту інциденту:**
   Для запобігання підміні даних або ретроспективній фальсифікації звітності стан інциденту на кожному кроці (при переході з `STATE_TRIAGED` у `STATE_EARLY_WARNING_SENT`) хешується алгоритмом SHA-256 і підписується апаратним модулем безпеки (HSM) або токеном TPM. Згенерований цифровий підпис зберігається разом із квитанцією прийому від CSIRT, утворюючи криміналістично непорушний доказ дотримання нормативних строків.
