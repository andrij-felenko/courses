# ⚙️ Трекер ембарго та автомат станів CVD-процесу

Узгоджене розкриття вразливостей (Coordinated Vulnerability Disclosure) вимагає суворого дотримання часових обмежень (SLA) та автоматизованого контролю переходів між фазами обробки. Помилка в розрахунку дедлайну може призвести або до передчасного витоку інформації про незахищені системи, або до безпідставного затягування випуску критичного безпекового оновлення.

У великих організаціях та командах реагування на інциденти (PSIRT, CERT) облік десятків одночасних вразливостей виконується автоматизованими системами. Нижче наведено архітектуру та робочу реалізацію ядра трекера життєвого циклу CVD-кейсу, що реалізує скінченний автомат станів ISO/IEC 29147 / 30111, автоматичний розрахунок 90-денного ембарго з урахуванням вихідних днів (Weekend Rollover), обробку 14-денного пільгового періоду (Grace Period) та екстрене скорочення строків при виявленні активних атак.

## Проектування автомата станів та структур даних

Ядро системи оперує структурою кейсу `cvd_case_t`, яка зберігає ідентифікатори (CVE, внутрішній ID), часові мітки ключових подій у форматі UNIX epoch UTC, поточний стан автомата та прапорці безпекових подій.

Автомат підтримує такі ключові правила та інваріанти:
1. **Базовий дедлайн:** Розраховується як `T_0 + 90 діб` (7 776 000 секунд).
2. **Перенесення з вихідних (Weekend Rollover):** Якщо фінальна дата припадає на суботу, додається 2 дні; якщо на неділю — додається 1 день для перенесення на найближчий робочий понеділок. Це запобігає ситуаціям, коли адміністратори змушені терміново оновлювати сервери у вихідні дні.
3. **Пільговий період (Grace Period):** Запит на Grace Period додає рівно 14 діб за умови, що кейс перебуває в стані розробки або готовності патча (`STATE_IN_PROGRESS` або `STATE_PATCH_READY`).
4. **Екстрене скорочення (Emergency Trigger):** Подія виявлення експлуатації в дикій природі `FLAG_IN_THE_WILD` встановлює дедлайн на `T_event + 7 діб`; подія витоку експлойта `FLAG_PUBLIC_LEAK` скорочує строк до `T_event + 2 доби` (48 годин) з автоматичним переведенням у стан `STATE_EMERGENCY`.

## Реалізація ядра трекера ембарго

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>
#include <string.h>

#define SECONDS_PER_DAY 86400LL
#define DEFAULT_EMBARGO_DAYS 90
#define GRACE_PERIOD_DAYS 14
#define EMERGENCY_IN_THE_WILD_DAYS 7
#define EMERGENCY_LEAK_DAYS 2

typedef enum {
    STATE_SUBMITTED = 0,
    STATE_TRIAGED,
    STATE_IN_PROGRESS,
    STATE_PATCH_READY,
    STATE_PRE_NOTIFY,
    STATE_DISCLOSED,
    STATE_EMERGENCY,
    STATE_REJECTED
} cvd_state_t;

typedef struct {
    char case_id[32];
    char cve_id[20];
    cvd_state_t state;
    time_t submitted_time;
    time_t embargo_deadline;
    bool in_the_wild;
    bool public_leak;
    bool grace_applied;
} cvd_case_t;

static time_t adjust_weekend_rollover(time_t target_time) {
    struct tm tm_buf;
#if defined(_WIN32)
    gmtime_s(&tm_buf, &target_time);
#else
    gmtime_r(&target_time, &tm_buf);
#endif
    // tm_wday: 0 = Sunday, 6 = Saturday
    if (tm_buf.tm_wday == 6) {
        return target_time + 2 * SECONDS_PER_DAY; // Перенесення суботи на понеділок
    } else if (tm_buf.tm_wday == 0) {
        return target_time + 1 * SECONDS_PER_DAY; // Перенесення неділі на понеділок
    }
    return target_time;
}

bool cvd_case_init(cvd_case_t *c, const char *case_id, time_t submit_time) {
    if (!c || !case_id) return false;
    memset(c, 0, sizeof(cvd_case_t));
    snprintf(c->case_id, sizeof(c->case_id), "%s", case_id);
    c->state = STATE_SUBMITTED;
    c->submitted_time = submit_time;
    time_t raw_deadline = submit_time + (DEFAULT_EMBARGO_DAYS * SECONDS_PER_DAY);
    c->embargo_deadline = adjust_weekend_rollover(raw_deadline);
    return true;
}

bool cvd_case_triage(cvd_case_t *c, const char *cve_id, bool accepted) {
    if (!c || c->state != STATE_SUBMITTED) return false;
    if (!accepted) {
        c->state = STATE_REJECTED;
        return true;
    }
    if (cve_id) {
        snprintf(c->cve_id, sizeof(c->cve_id), "%s", cve_id);
    }
    c->state = STATE_TRIAGED;
    return true;
}

bool cvd_case_start_remediation(cvd_case_t *c) {
    if (!c || c->state != STATE_TRIAGED) return false;
    c->state = STATE_IN_PROGRESS;
    return true;
}

bool cvd_case_apply_grace_period(cvd_case_t *c) {
    if (!c || c->grace_applied) return false;
    if (c->state != STATE_IN_PROGRESS && c->state != STATE_PATCH_READY) return false;
    
    c->embargo_deadline += (GRACE_PERIOD_DAYS * SECONDS_PER_DAY);
    c->embargo_deadline = adjust_weekend_rollover(c->embargo_deadline);
    c->grace_applied = true;
    return true;
}

bool cvd_case_trigger_emergency(cvd_case_t *c, time_t event_time, bool is_in_the_wild, bool is_leak) {
    if (!c || c->state == STATE_DISCLOSED || c->state == STATE_REJECTED) return false;
    
    c->state = STATE_EMERGENCY;
    if (is_leak) {
        c->public_leak = true;
        c->embargo_deadline = event_time + (EMERGENCY_LEAK_DAYS * SECONDS_PER_DAY);
    } else if (is_in_the_wild) {
        c->in_the_wild = true;
        c->embargo_deadline = event_time + (EMERGENCY_IN_THE_WILD_DAYS * SECONDS_PER_DAY);
    }
    return true;
}

bool cvd_case_disclose(cvd_case_t *c, time_t current_time) {
    if (!c || c->state == STATE_REJECTED || c->state == STATE_DISCLOSED) return false;
    if (current_time >= c->embargo_deadline || c->state == STATE_EMERGENCY || c->state == STATE_PRE_NOTIFY) {
        c->state = STATE_DISCLOSED;
        return true;
    }
    return false;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <optional>
#include <expected>
#include <format>

using namespace std::chrono;

enum class CvdState {
    Submitted,
    Triaged,
    InProgress,
    PatchReady,
    PreNotify,
    Disclosed,
    Emergency,
    Rejected
};

enum class CvdError {
    InvalidStateTransition,
    GracePeriodAlreadyApplied,
    GracePeriodNotAllowedInCurrentState,
    CaseAlreadyClosed,
    EmbargoNotExpired
};

class CvdCaseTracker {
public:
    explicit CvdCaseTracker(std::string_view case_id, sys_seconds submit_time)
        : case_id_(case_id), submitted_time_(submit_time), state_(CvdState::Submitted) {
        auto raw_deadline = submit_time + days(90);
        embargo_deadline_ = adjust_weekend_rollover(raw_deadline);
    }

    [[nodiscard]] const std::string& case_id() const noexcept { return case_id_; }
    [[nodiscard]] const std::string& cve_id() const noexcept { return cve_id_; }
    [[nodiscard]] CvdState state() const noexcept { return state_; }
    [[nodiscard]] sys_seconds embargo_deadline() const noexcept { return embargo_deadline_; }
    [[nodiscard]] bool is_grace_applied() const noexcept { return grace_applied_; }

    std::expected<void, CvdError> triage(std::string_view cve_id, bool accepted) {
        if (state_ != CvdState::Submitted) {
            return std::unexpected(CvdError::InvalidStateTransition);
        }
        if (!accepted) {
            state_ = CvdState::Rejected;
            return {};
        }
        cve_id_ = cve_id;
        state_ = CvdState::Triaged;
        return {};
    }

    std::expected<void, CvdError> start_remediation() {
        if (state_ != CvdState::Triaged) {
            return std::unexpected(CvdError::InvalidStateTransition);
        }
        state_ = CvdState::InProgress;
        return {};
    }

    std::expected<void, CvdError> mark_patch_ready() {
        if (state_ != CvdState::InProgress) {
            return std::unexpected(CvdError::InvalidStateTransition);
        }
        state_ = CvdState::PatchReady;
        return {};
    }

    std::expected<void, CvdError> start_pre_notification() {
        if (state_ != CvdState::PatchReady) {
            return std::unexpected(CvdError::InvalidStateTransition);
        }
        state_ = CvdState::PreNotify;
        return {};
    }

    std::expected<void, CvdError> apply_grace_period() {
        if (grace_applied_) {
            return std::unexpected(CvdError::GracePeriodAlreadyApplied);
        }
        if (state_ != CvdState::InProgress && state_ != CvdState::PatchReady) {
            return std::unexpected(CvdError::GracePeriodNotAllowedInCurrentState);
        }
        embargo_deadline_ = adjust_weekend_rollover(embargo_deadline_ + days(14));
        grace_applied_ = true;
        return {};
    }

    std::expected<void, CvdError> trigger_emergency(sys_seconds event_time, bool in_the_wild, bool public_leak) {
        if (state_ == CvdState::Disclosed || state_ == CvdState::Rejected) {
            return std::unexpected(CvdError::CaseAlreadyClosed);
        }
        state_ = CvdState::Emergency;
        if (public_leak) {
            public_leak_ = true;
            embargo_deadline_ = event_time + days(2);
        } else if (in_the_wild) {
            in_the_wild_ = true;
            embargo_deadline_ = event_time + days(7);
        }
        return {};
    }

    std::expected<void, CvdError> disclose(sys_seconds current_time) {
        if (state_ == CvdState::Disclosed || state_ == CvdState::Rejected) {
            return std::unexpected(CvdError::CaseAlreadyClosed);
        }
        if (current_time < embargo_deadline_ && state_ != CvdState::Emergency && state_ != CvdState::PreNotify) {
            return std::unexpected(CvdError::EmbargoNotExpired);
        }
        state_ = CvdState::Disclosed;
        return {};
    }

private:
    static sys_seconds adjust_weekend_rollover(sys_seconds target_time) {
        sys_days dp = floor<days>(target_time);
        year_month_day ymd{dp};
        weekday wd{dp};
        if (wd == Saturday) {
            return target_time + days(2);
        }
        if (wd == Sunday) {
            return target_time + days(1);
        }
        return target_time;
    }

    std::string case_id_;
    std::string cve_id_;
    CvdState state_;
    sys_seconds submitted_time_;
    sys_seconds embargo_deadline_;
    bool in_the_wild_{false};
    bool public_leak_{false};
    bool grace_applied_{false};
};
```
:::

## Детальний розбір алгоритмічних рішень

### 1. Календарна арифметика та захист від часових аномалій

У розробці систем координації безпеки класичною помилкою є використання локальних функцій часу (`localtime`, `mktime`), які залежать від налаштувань часового поясу сервера та правил переходу на літній/зимовий час (DST). У наведеній реалізації:
- Мовою C використовується строго потокобезпечна функція `gmtime_r` (або `gmtime_s` на платформі Windows), яка розбирає часову мітку в структурований формат `struct tm` виключно за нульовим меридіаном (UTC).
- Мовою C++ застосовується сучасний календарний апарат бібліотеки `<chrono>` (C++20), де операції виконуються з типом `std::chrono::sys_seconds` та `std::chrono::sys_days`, що унеможливлює помилки переповнення чи некоректного врахування високосних секунд.

### 2. Строга типізація та захист переходів стану

Модель станів виключає недійсні послідовності викликів (наприклад, перехід до публікації без попереднього тріажу або повторне застосування пільгового періоду).
- У версії мовою C функції повертають булевий статус успішності операції `bool`, сигналізуючи про відхилення некоректних переходів.
- У версії мовою C++ використовується типізований контейнер `std::expected<void, CvdError>`, який примушує викликаючий код явно обробляти всі можливі варіанти помилок бізнес-логіки (`InvalidStateTransition`, `GracePeriodAlreadyApplied`, `EmbargoNotExpired`).

### 3. Механізм пріоритетного екстреного переривання

Якщо кейс перебуває у тривалому 90-денному циклі виправлення, і моніторинг фіксує появу публічного PoC на GitHub або продаж 0-day експлойта на підпільному форумі, виклик методу `trigger_emergency()` миттєво змінює стан на `Emergency` та перезаписує дедлайн:
- Для витоку вихідного коду експлойта дедлайн скорочується до 48 годин, що дає вендору мінімальний час на перевірку та випуск термінового хотфікса.
- Для виявлених цільових атак дедлайн встановлюється на 7 діб за стандартом Google Project Zero.
- Спроба розкриття через `disclose()` у стані `Emergency` спрацьовує негайно, дозволяючи системі миттєво зняти обмеження доступу та опублікувати бюлетень безпеки для захисту користувачів.

## Трасування виконання: числовий приклад розрахунку ембарго

Розглянемо практичний сценарій обробки вразливості, зареєстрованої в суботу, 30 травня 2026 року об 11:00 UTC:
1. **Початковий розрахунок:** До моменту надходження `2026-05-30T11:00:00Z` додається 90 діб. Нескорегована дата завершення: `2026-08-28T11:00:00Z` (п'ятниця). Оскільки це робочий день, дедлайн фіксується на `2026-08-28T11:00:00Z`.
2. **Сценарій зміщення на вихідний:** Якщо звіт подано в неділю, 31 травня 2026 року, 90 діб спливають у суботу, 29 серпня 2026 року. Функція `adjust_weekend_rollover()` визначає `tm_wday == 6` і автоматично додає `2 * 86400` секунд, переносячи дату на понеділок, 31 серпня 2026 року.
3. **Запит на Grace Period:** На 80-й день (18 серпня) вендор надсилає запит на 14-денне продовження через тривале тестування на апаратних кластерах. Виклик `apply_grace_period()` зсуває дедлайн з 28 серпня на 11 вересня 2026 року (п'ятниця).
4. **Екстрене переривання:** Якщо 5 вересня служба Threat Intelligence фіксує активні атаки на клієнтів через дану вразливість, спрацьовує метод `trigger_emergency(now, in_the_wild=true, public_leak=false)`. Новий дедлайн стає рівним `2026-09-12T11:00:00Z` (7 діб), і вендор випускає бюлетень безпеки негайно, не чекаючи планової дати 11 вересня.

## Інтеграція з базами даних та аудитом дій

У промислових системах координації кожен виклик мутації стану супроводжується записом у незмінний журнал аудиту. Фіксація переходів автомата із збереженням цифрового підпису оператора запобігає несанкціонованому перенесенню строків без відома першовідкривача або координатора. При збереженні стану в реляційній СУБД (PostgreSQL / SQLite) транзакція блокує рядок кейсу (`SELECT FOR UPDATE`), щоб уникнути стану гонки при одночасному надходженні запиту на Grace Period від розробника та повідомлення про витік експлойта від аналітика моніторингу.
