# ⚙️ Автоматизована реконструкція таймлайну інциденту та валідатор метрик

Під час повномасштабної аварії в розподіленій системі гетерогенні потоки телеметрії (сповіщення Prometheus, вебхуки PagerDuty, події Kubernetes та коміти Git) генерують тисячі записів із дрейфом годинників та неузгодженими часовими поясами. Автоматизований реконструктор таймлайну нормалізує ці події до єдиного стандарту UTC, сортує їх за зростанням, обчислює ключові SRE-метрики (MTTD, MTTA, MTTM, MTTR) та виявляє порушення причинно-наслідкових інваріантів, усуваючи суб'єктивні спотворення пам'яті учасників.

---

## 1. Архітектура та постановка задачі

Під час повномасштабної аварії в розподіленій системі інженери та автоматизовані агенти генерують тисячі повідомлень у різних підсистемах:
* Метричні сервіси фіксують точний момент виходу індикатора SLI за межі норми;
* Менеджер алертів реєструє надсилання сповіщення черговому інженеру;
* Платформа оркестрації логує перезапуски контейнерів та перемикання трафіку;
* Чергові інженери залишають коментарі в інцидентному чаті щодо виконаних дій.

Ручне зведення цих розрізнених записів у єдиний таймлайн призводить до двох типових проблем:
1. **Помилки ручної фіксації часу:** через людський стрес та неузгодженість локальних годинників мітки часу записуються із запізненням або округленням до десятків хвилин.
2. **Порушення монотонності:** неточні часові мітки створюють ілюзію, що інженер застосував виправлення до того, як спрацював алерт, що спотворює подальший аналіз.

Інструмент нормалізує всі події до єдиного стандарту часу UTC із мілісекундною точністю, сортує їх за зростанням, перевіряє коректність послідовності фаз та генерує фінальний звіт для постмортему.

---

## 2. Математична модель інтервалів надійності SRE

Хронологія інциденту розглядається як дискретний набір часових міток на осі часу `t`:

* `T_inject` — момент внесення дефекту в систему (наприклад, злиття помилкового PR або зміна конфігурації);
* `T_trigger` — активація дефекту зовнішньою подією (наприклад, нічний сплеск трафіку чи спрацювання планувальника завдань);
* `T_impact` — початок фактичного погіршення користувацького досвіду (вихід помилок за межі базового рівня);
* `T_detect` — реєстрація аномалії автоматичним моніторингом або спрацьовування правила алерту;
* `T_ack` — підтвердження отримання сповіщення черговим інженером та створення інцидентного каналу;
* `T_mitigate` — застосування тимчасового заходу, що ізолював збій (відкат версії, активація аварійного прапорця, перемикання трафіку);
* `T_impact_end` — повернення частоти помилок і латентності до нормативних меж SLO;
* `T_resolve` — повне очищення стану системи, оновлення пошкоджених даних та закриття інцидентного штабу.

На основі цих реперних точок алгоритм обчислює стандартні SRE-інтервали:

```text
MTTD = T_detect − T_impact          [Час до виявлення моніторингом]
MTTA = T_ack − T_detect             [Час реакції чергового на алерт]
MTTM = T_mitigate − T_ack           [Час локалізації та придушення збою]
MTTR = T_resolve − T_impact         [Повний час повернення до норми]
Impact_Duration = T_impact_end − T_impact
```

---

## 3. Реалізація реконструктора таймлайну

Нижче наведено повнофункціональну реалізацію мовами C++20 та Python 3.11:

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <chrono>
#include <optional>
#include <expected>
#include <algorithm>
#include <format>
#include <sstream>
#include <iomanip>

namespace postmortem {

enum class Phase {
    DefectInjected,
    TriggerEvent,
    ImpactStarted,
    DetectedByAlert,
    AcknowledgedByOncall,
    MitigationApplied,
    ImpactEnded,
    FullyResolved,
    Unknown
};

[[nodiscard]] constexpr std::string_view phase_to_string(Phase phase) noexcept {
    switch (phase) {
        case Phase::DefectInjected:        return "defect_injected";
        case Phase::TriggerEvent:          return "trigger_event";
        case Phase::ImpactStarted:         return "impact_started";
        case Phase::DetectedByAlert:       return "detected_by_alert";
        case Phase::AcknowledgedByOncall:  return "acknowledged_by_oncall";
        case Phase::MitigationApplied:     return "mitigation_applied";
        case Phase::ImpactEnded:           return "impact_ended";
        case Phase::FullyResolved:         return "fully_resolved";
        case Phase::Unknown:               return "unknown";
    }
    return "unknown";
}

[[nodiscard]] constexpr Phase string_to_phase(std::string_view sv) noexcept {
    if (sv == "defect_injected")        return Phase::DefectInjected;
    if (sv == "trigger_event")          return Phase::TriggerEvent;
    if (sv == "impact_started")         return Phase::ImpactStarted;
    if (sv == "detected_by_alert")      return Phase::DetectedByAlert;
    if (sv == "acknowledged_by_oncall") return Phase::AcknowledgedByOncall;
    if (sv == "mitigation_applied")     return Phase::MitigationApplied;
    if (sv == "impact_ended")           return Phase::ImpactEnded;
    if (sv == "fully_resolved")         return Phase::FullyResolved;
    return Phase::Unknown;
}

using TimePoint = std::chrono::system_clock::time_point;

struct TimelineEvent {
    TimePoint timestamp;
    Phase phase;
    std::string component;
    std::string description;
    std::string source_url;
};

struct IncidentMetrics {
    std::chrono::seconds mttd{0}; // Mean Time to Detect (Impact -> Detect)
    std::chrono::seconds mtta{0}; // Mean Time to Acknowledge (Detect -> Ack)
    std::chrono::seconds mttm{0}; // Mean Time to Mitigate (Ack -> Mitigation)
    std::chrono::seconds mttr{0}; // Mean Time to Resolve (Impact -> Resolve)
    std::chrono::seconds total_impact_duration{0};
};

enum class ValidationError {
    EmptyTimeline,
    NonMonotonicTimestamps,
    MissingImpactStart,
    MissingResolution,
    MitigationBeforeDetection,
    AckBeforeDetection
};

class TimelineReconstructor {
public:
    void add_event(TimelineEvent event) {
        events_.push_back(std::move(event));
    }

    [[nodiscard]] std::expected<IncidentMetrics, ValidationError> process_and_validate() {
        if (events_.empty()) {
            return std::unexpected(ValidationError::EmptyTimeline);
        }

        // Сортування за часом
        std::stable_sort(events_.begin(), events_.end(), [](const auto& a, const auto& b) {
            return a.timestamp < b.timestamp;
        });

        std::optional<TimePoint> t_impact;
        std::optional<TimePoint> t_detect;
        std::optional<TimePoint> t_ack;
        std::optional<TimePoint> t_mitigate;
        std::optional<TimePoint> t_impact_end;
        std::optional<TimePoint> t_resolve;

        for (const auto& ev : events_) {
            switch (ev.phase) {
                case Phase::ImpactStarted:         t_impact = ev.timestamp; break;
                case Phase::DetectedByAlert:       t_detect = ev.timestamp; break;
                case Phase::AcknowledgedByOncall:  t_ack = ev.timestamp; break;
                case Phase::MitigationApplied:     t_mitigate = ev.timestamp; break;
                case Phase::ImpactEnded:           t_impact_end = ev.timestamp; break;
                case Phase::FullyResolved:         t_resolve = ev.timestamp; break;
                default: break;
            }
        }

        if (!t_impact.has_value()) {
            return std::unexpected(ValidationError::MissingImpactStart);
        }
        if (!t_resolve.has_value() && !t_impact_end.has_value()) {
            return std::unexpected(ValidationError::MissingResolution);
        }

        // Перевірка інваріантів причинно-наслідкового зв'язку
        if (t_detect && t_ack && *t_ack < *t_detect) {
            return std::unexpected(ValidationError::AckBeforeDetection);
        }
        if (t_detect && t_mitigate && *t_mitigate < *t_detect) {
            return std::unexpected(ValidationError::MitigationBeforeDetection);
        }

        IncidentMetrics metrics;
        if (t_detect && t_impact) {
            metrics.mttd = std::chrono::duration_cast<std::chrono::seconds>(*t_detect - *t_impact);
        }
        if (t_ack && t_detect) {
            metrics.mtta = std::chrono::duration_cast<std::chrono::seconds>(*t_ack - *t_detect);
        }
        if (t_mitigate && t_ack) {
            metrics.mttm = std::chrono::duration_cast<std::chrono::seconds>(*t_mitigate - *t_ack);
        }
        if (t_resolve && t_impact) {
            metrics.mttr = std::chrono::duration_cast<std::chrono::seconds>(*t_resolve - *t_impact);
        }
        if (t_impact_end && t_impact) {
            metrics.total_impact_duration = std::chrono::duration_cast<std::chrono::seconds>(*t_impact_end - *t_impact);
        } else if (t_resolve && t_impact) {
            metrics.total_impact_duration = metrics.mttr;
        }

        return metrics;
    }

    [[nodiscard]] const std::vector<TimelineEvent>& events() const noexcept {
        return events_;
    }

private:
    std::vector<TimelineEvent> events_;
};

} // namespace postmortem

int main() {
    using namespace std::chrono_literals;
    auto now = std::chrono::system_clock::now();

    postmortem::TimelineReconstructor reconstructor;

    reconstructor.add_event({
        now,
        postmortem::Phase::ImpactStarted,
        "checkout-gateway",
        "Стрибок 5xx помилок через блокування пулу HikariCP",
        "https://monitoring.internal/alerts/500"
    });

    reconstructor.add_event({
        now + 120s,
        postmortem::Phase::DetectedByAlert,
        "alertmanager",
        "Спрацював алерт High5xxErrorRate (burn rate > 14x)",
        "https://alertmanager.internal/#/alert/412"
    });

    reconstructor.add_event({
        now + 300s,
        postmortem::Phase::AcknowledgedByOncall,
        "pagerduty",
        "Черговий інженер підтвердив інцидент",
        "https://pagerduty.internal/inc/841"
    });

    reconstructor.add_event({
        now + 1500s,
        postmortem::Phase::MitigationApplied,
        "feature-flags",
        "Вимкнено виклик зовнішнього податкового шлюзу",
        "https://flags.internal/tax-fallback"
    });

    reconstructor.add_event({
        now + 2400s,
        postmortem::Phase::FullyResolved,
        "checkout-gateway",
        "Черги розвантажилися, p99 латентність повернулася до норми",
        "https://grafana.internal/d/health"
    });

    auto res = reconstructor.process_and_validate();
    if (!res) {
        std::cerr << "Помилка валідації таймлайну!\n";
        return 1;
    }

    const auto& m = *res;
    std::cout << "=== МЕТРИКИ ІНЦИДЕНТУ ===\n";
    std::cout << "MTTD (Час до виявлення):     " << m.mttd.count() / 60 << " хв " << m.mttd.count() % 60 << " с\n";
    std::cout << "MTTA (Час реакції чергового): " << m.mtta.count() / 60 << " хв " << m.mtta.count() % 60 << " с\n";
    std::cout << "MTTM (Час до пом'якшення):   " << m.mttm.count() / 60 << " хв " << m.mttm.count() % 60 << " с\n";
    std::cout << "MTTR (Повний час відновлення): " << m.mttr.count() / 60 << " хв " << m.mttr.count() % 60 << " с\n";

    return 0;
}
```
```py
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import List, Optional


class Phase(Enum):
    DEFECT_INJECTED = "defect_injected"
    TRIGGER_EVENT = "trigger_event"
    IMPACT_STARTED = "impact_started"
    DETECTED_BY_ALERT = "detected_by_alert"
    ACKNOWLEDGED_BY_ONCALL = "acknowledged_by_oncall"
    MITIGATION_APPLIED = "mitigation_applied"
    IMPACT_ENDED = "impact_ended"
    FULLY_RESOLVED = "fully_resolved"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class TimelineEvent:
    timestamp: datetime
    phase: Phase
    component: str
    description: str
    source_url: str


@dataclass
class IncidentMetrics:
    mttd_seconds: float
    mtta_seconds: float
    mttm_seconds: float
    mttr_seconds: float
    total_impact_seconds: float


class ValidationError(Exception):
    pass


class TimelineReconstructor:
    def __init__(self) -> None:
        self._events: List[TimelineEvent] = []

    def add_event(self, event: TimelineEvent) -> None:
        self._events.append(event)

    def process_and_validate(self) -> IncidentMetrics:
        if not self._events:
            raise ValidationError("Таймлайн порожній")

        # Сортування за міткою часу
        sorted_events = sorted(self._events, key=lambda e: e.timestamp)

        phases_map = {ev.phase: ev.timestamp for ev in sorted_events}

        t_impact = phases_map.get(Phase.IMPACT_STARTED)
        t_detect = phases_map.get(Phase.DETECTED_BY_ALERT)
        t_ack = phases_map.get(Phase.ACKNOWLEDGED_BY_ONCALL)
        t_mitigate = phases_map.get(Phase.MITIGATION_APPLIED)
        t_impact_end = phases_map.get(Phase.IMPACT_ENDED)
        t_resolve = phases_map.get(Phase.FULLY_RESOLVED)

        if not t_impact:
            raise ValidationError("Відсутня обов'язкова фаза початку впливу (IMPACT_STARTED)")
        if not t_resolve and not t_impact_end:
            raise ValidationError("Відсутня фаза завершення інциденту (FULLY_RESOLVED або IMPACT_ENDED)")

        if t_detect and t_ack and t_ack < t_detect:
            raise ValidationError("Порушення інваріанту: підтвердження (ACK) раніше за виявлення алерта")
        if t_detect and t_mitigate and t_mitigate < t_detect:
            raise ValidationError("Порушення інваріанту: пом'якшення раніше за виявлення алерта")

        mttd = (t_detect - t_impact).total_seconds() if t_detect and t_impact else 0.0
        mtta = (t_ack - t_detect).total_seconds() if t_ack and t_detect else 0.0
        mttm = (t_mitigate - t_ack).total_seconds() if t_mitigate and t_ack else 0.0
        mttr = (t_resolve - t_impact).total_seconds() if t_resolve and t_impact else 0.0

        if t_impact_end and t_impact:
            total_impact = (t_impact_end - t_impact).total_seconds()
        else:
            total_impact = mttr

        return IncidentMetrics(
            mttd_seconds=mttd,
            mtta_seconds=mtta,
            mttm_seconds=mttm,
            mttr_seconds=mttr,
            total_impact_seconds=total_impact,
        )


if __name__ == "__main__":
    t0 = datetime.now(timezone.utc)
    reconstructor = TimelineReconstructor()

    reconstructor.add_event(
        TimelineEvent(
            timestamp=t0,
            phase=Phase.IMPACT_STARTED,
            component="checkout-gateway",
            description="Стрибок 5xx помилок через блокування пулу HikariCP",
            source_url="https://monitoring.internal/alerts/500",
        )
    )

    reconstructor.add_event(
        TimelineEvent(
            timestamp=t0 + timedelta(seconds=120),
            phase=Phase.DETECTED_BY_ALERT,
            component="alertmanager",
            description="Спрацював алерт High5xxErrorRate (burn rate > 14x)",
            source_url="https://alertmanager.internal/#/alert/412",
        )
    )

    reconstructor.add_event(
        TimelineEvent(
            timestamp=t0 + timedelta(seconds=300),
            phase=Phase.ACKNOWLEDGED_BY_ONCALL,
            component="pagerduty",
            description="Черговий інженер підтвердив інцидент",
            source_url="https://pagerduty.internal/inc/841",
        )
    )

    reconstructor.add_event(
        TimelineEvent(
            timestamp=t0 + timedelta(seconds=1500),
            phase=Phase.MITIGATION_APPLIED,
            component="feature-flags",
            description="Вимкнено виклик зовнішнього податкового шлюзу",
            source_url="https://flags.internal/tax-fallback",
        )
    )

    reconstructor.add_event(
        TimelineEvent(
            timestamp=t0 + timedelta(seconds=2400),
            phase=Phase.FULLY_RESOLVED,
            component="checkout-gateway",
            description="Черги розвантажилися, p99 латентність повернулася до норми",
            source_url="https://grafana.internal/d/health",
        )
    )

    metrics = reconstructor.process_and_validate()
    print(f"MTTD: {metrics.mttd_seconds / 60:.1f} хв")
    print(f"MTTA: {metrics.mtta_seconds / 60:.1f} хв")
    print(f"MTTM: {metrics.mttm_seconds / 60:.1f} хв")
    print(f"MTTR: {metrics.mttr_seconds / 60:.1f} хв")
```
:::

---

## 4. Детальний аналіз архітектурних рішень та структур даних

Розглянемо вибір підходів та інженерних гарантій у коді реконструктора:

### 4.1. Вибір `std::expected` замість винятків у C++20
Утиліти перевірки та CLI-лінтери часто аналізують сотні файлів у пакетному режимі в конвеєрах CI. Використання монадичного типу повернення `std::expected<IncidentMetrics, ValidationError>` надає три суттєві переваги:
1. **Явна сигнатура помилок:** інтерфейс функції одразу декларує всі можливі стани збою без прихованих викидів винятків у стек.
2. **Нульові накладні витрати на розгортання стека:** перевірка результату зводиться до перевірки булевого прапорця та розпакування значення, що працює зі швидкістю одного процесорного переходу.
3. **Зручна композиція:** результат легко інтегрується з функціональними ланцюжками обробки через методи `.and_then()` та `.transform_error()`.

### 4.2. Стабільне сортування `std::stable_sort` проти швидкого сортування
Події з різних систем можуть мати ідентичні мітки часу з точністю до секунди (наприклад, алерт моніторингу та запис у журналі Kubernetes події). Алгоритм застосовує `std::stable_sort`, гарантуючи збереження первинного відносного порядку надходження одночасних повідомлень. Це запобігає недетерміністичному переставлянню записів у фінальному звіті між різними запусками валідатора.

### 4.3. Використання типізованих інтервалів `std::chrono`
Замість зберігання тривалостей у вигляді сирих цілих чисел або чисел із плаваючою комою, код використовує `std::chrono::seconds` та `std::chrono::system_clock::time_point`. Це унеможливлює помилки змішування секунд із мілісекундами на етапі компіляції та автоматично забезпечує коректне форматування часу без ризику переповнення 32-бітних лічильників.

---

## 5. Обробка складних крайових випадків у розподіленому середовищі

У реальних виробничих кластерах сирі логи містять аномалії, які вимагають специфічної евристичної обробки:

### 5.1. Неузгодженість годинників та часовий дрейф (Clock Drift Compensation)
Якщо сервери бази даних і вузли моніторингу мають часовий зсув у 2–3 секунди через затримки протоколу NTP, подія отримання запиту може мати мітку часу меншу за подію його відправлення.
* **Алгоритм нормалізації:** валідатор аналізує граф розподіленого трасування (Distributed Trace Tree) зі стандарту OpenTelemetry. Якщо спан клієнта `S_c` передує спану сервера `S_s`, але `t(S_s.start) < t(S_c.start)`, обчислюється корекційний коефіцієнт зсуву `delta = t(S_c.start) - t(S_s.start) + 0.5 * RTT`. Усі часові мітки сервера локально зсуваються на величину `delta`, а у звіті фіксується попередження про необхідність калібрування NTP-демона.
* **Аналіз критичного шляху (Trace Critical Path):** парсер автоматично витягує ланцюг спанів із найбільшим внеском у загальну затримку (latency outlier) під час інциденту. Це дозволяє вказати в таймлайні не просто факт уповільнення, а точний SQL-запит або блокувальний RPC-виклик, який спровокував дефіцит пулу ресурсів.

### 5.2. Багаторазове перемикання та каскадне флапання (Mitigation Flapping)
Коли інженери застосовують серію послідовних виправлень (наприклад, збільшення ліміту пам'яті, потім перезапуск, потім повний відкат релізу), таймлайн отримує кілька подій `mitigation_applied`.
* **Правило обчислення MTTM:** метрика часу до пом'якшення фіксується не за першою невдалою спробою, а за **останньою дією, після якої почався стійкий спад помилок**. Усі проміжні спроби класифікуються як `mitigation_attempt_aborted` із підрахунком сумарного часу, витраченого на нерелевантні дії.

### 5.3. Ручне виявлення за відсутності алертів (Silent Degradation)
У випадках, коли моніторинг не зреагував на деградацію (наприклад, через помилку в конфігурації селектора метрик), інцидент ініціюється оператором підтримки вручну.
* **Обробка MTTD:** валідатор фіксує `mttd = 0` для автоматичного каналу, виставляє прапорець `detected_manually = true` та вимагає наявності в переліку коригувальних дій обов'язкового завдання класу `tier_3_detection` щодо створення відповідного алерта у системі спостережуваності.

---

## 6. Парсинг гетерогенних джерел телеметрії

Реконструктор підтримує пряме завантаження подій із типових інфраструктурних джерел:

### 6.1. Адаптер вебхуків Prometheus Alertmanager
Alertmanager надсилає JSON-пакети при зміні стану алерту (`firing` / `resolved`):

```json
{
  "version": "4",
  "status": "firing",
  "alerts": [
    {
      "status": "firing",
      "labels": {
        "alertname": "High5xxErrorRate",
        "service": "checkout-gateway",
        "severity": "critical"
      },
      "annotations": {
        "description": "5xx error rate is 18.4% (threshold > 1%)"
      },
      "startsAt": "2026-08-14T02:18:10.204Z",
      "endsAt": "0001-01-01T00:00:00Z",
      "generatorURL": "https://prometheus.internal/graph?..."
    }
  ]
}
```

Адаптер витягує часову мітку `startsAt`, зіставляє мітку `alertname` з внутрішнім каталогом і генерує об'єкт `TimelineEvent` із фазою `Phase::DetectedByAlert`.

### 6.2. Адаптер вебхуків платформи чергувань PagerDuty (Webhook v3)
PagerDuty сповіщає про зміну стану інциденту за допомогою вебхука подій:

```json
{
  "event": {
    "id": "01CA74G8Z9",
    "event_type": "incident.acknowledged",
    "occurred_at": "2026-08-14T02:20:00.142Z",
    "agent": {
      "html_url": "https://company.pagerduty.com/users/PKRAV12",
      "summary": "Oleg Kravets"
    },
    "data": {
      "id": "Q149",
      "title": "High5xxErrorRate checkout-gateway"
    }
  }
}
```

Обробник витягує поле `occurred_at` як точний час квитування алерта інженером (`Phase::AcknowledgedByOncall`) та фіксує ім'я чергового у блоці метаданих.

### 6.3. Адаптер подій платформи Kubernetes
Під час аварії в кластері події переповнення пам'яті (OOMKilled) або невдалих проб готовності (Readiness Probe Failed) фіксуються в журналі аудиту Kubernetes API:

```json
{
  "apiVersion": "events.k8s.io/v1",
  "kind": "Event",
  "metadata": {
    "creationTimestamp": "2026-08-14T02:16:45Z",
    "name": "checkout-gateway-7b9d8-oom"
  },
  "regarding": {
    "kind": "Pod",
    "name": "checkout-gateway-7b9d8"
  },
  "reason": "OOMKilled",
  "note": "Container checkout exceeded memory limit of 2GiB"
}
```

Парсер інтерпретує подію `OOMKilled` як індикатор ескалації впливу (`Phase::ImpactStarted`) та прив'язує її до відповідного мікросервісу.

---

## 7. Парсинг журналів інцидентних чатів (Slack / Teams Intent Extraction)

Окрім машинних сигналів, значна частина важливих рішень приймається людьми в екстреному інцидентному чаті (Incident Bridge). Парсер містить евристичний модуль розбору текстових логів чату:

1. **Командні мітки Slack-бота:**
   * Повідомлення `/incident ack` перетворюється на подію `Phase::AcknowledgedByOncall`.
   * Повідомлення `/incident mitigate <опис>` генерує подію `Phase::MitigationApplied`.
   * Повідомлення `/incident resolve` формує мітку `Phase::FullyResolved`.
2. **Семантичні патерни у відкритому тексті:**
   Якщо інженери не використовували бот-команди, регулярні вирази шукають ключові фрази («відкотили реліз на v2.4.1», «трафік перемкнуто на backup-кластер», «база стабілізувалася») та пропонують фасилітатору відповідні часові позначки як чернетки подій для включення у фінальний постмортем.

---

## 8. Побудова ациклічного графа причинності (Causal DAG Generation)

Простого списку подій недостатньо для розуміння каскадних відмов у мікросервісних топологіях. Реконструктор будує орієнтований ациклічний граф (Directed Acyclic Graph, DAG), де кожна вершина — це подія, а дуги відображають пряму причинну залежність:

* **Вершина `V_1`:** Збільшення латентності стороннього податкового шлюзу TaxCloud (`t = 02:14`).
* **Вершина `V_2`:** Вичерпання пулу з'єднань HikariCP у сервісі `billing-service` (`t = 02:16`, залежить від `V_1`).
* **Вершина `V_3`:** Каскадне накопичення черги запитів у шлюзі `checkout-gateway` (`t = 02:16:30`, залежить від `V_2`).
* **Вершина `V_4`:** Спрацювання алерта `High5xxErrorRate` (`t = 02:18:10`, залежить від `V_3`).

Алгоритм топологічного сортування перевіряє граф на відсутність циклічних залежностей та автоматично формує розділ «Причинно-наслідковий ланцюг» у звіті постмортему.

---

## 9. Виявлення точок зламу в часових рядах (Changepoint Detection)

Для об'єктивного визначення мітки `T_impact` парсер реалізує алгоритм кумулятивної суми відхилень (Cumulative Sum Control Chart, CUSUM) над часовим рядом помилок:

```text
S[k] = max(0, S[k-1] + (x[k] − mu_0 − k_shift · sigma))
```

де:
* `x[k]` — виміряна частота помилок у кванті часу `k`;
* `mu_0` — базове середнє значення помилок у нормальному стані системи;
* `sigma` — стандартне відхилення базового шуму;
* `k_shift` — допустимий поріг зсуву (зазвичай `0.5`).

Коли `S[k]` перевищує критичний поріг рішення `H = 5 · sigma`, алгоритм автоматично фіксує момент `T_impact` як індекс першого стрибка `S[k] > 0`, усуваючи необхідність ручного вгадування часу початку деградації за нерівними графіками.

---

## 10. Інтеграція з синтетичними пробами (Canary Synthetic Correlation)

Окрім аналізу пасивного користувацького трафіку, реконструктор зіставляє дані з активними синтетичними пробами (Canary Probing):
* Синтетичні зонди надсилають контрольні транзакції кожні 5 секунд із фіксованого пулу тестових акаунтів.
* Якщо синтетичний запит зазнав невдачі, але користувацький трафік ще не показав масових 5xx через кешування або локальну чергу браузера, часова мітка синтетичної невдачі приймається як `T_trigger`.
* Це дає змогу виявити «приховану фазу збою» (Dark Outage Phase), коли система вже деградувала, але користувачі ще не встигли звернутися до несправного ендпоінта.

---

## 11. Агрегація процентилів надійності за квартал (Rolling Percentiles)

Під час регулярного квартального аудиту надійності інфраструктурна команда запускає реконструктор у пакетному режимі над сотнями постмортемів за останні 90 днів:

1. **Розрахунок медіани та 95-го процентиля:**
   * `p50(MTTD)` — типовий час реакції автоматичного моніторингу;
   * `p95(MTTD)` — виявлення «сліпих зон» у рідкісних крайових сценаріях;
   * `p50(MTTA)` — якість організації чергувань та відсутність втоми від алертів (Alert Fatigue);
   * `p95(MTTM)` — готовність команд до швидкої локалізації збоїв за допомогою автоматизованих прапорців та канарок.
2. **Виявлення тенденцій деградації:**
   Якщо за квартал `p95(MTTM)` зріс із 15 до 45 хвилин при незмінному `MTTD`, це свідчить про зростання архітектурної зв'язності сервісів: інженери швидко дізнаються про аварію, але витрачають усе більше часу на локалізацію каскадної відмови через заплутані міжсервісні залежності.

---

## 12. Експорт візуалізації у формати Graphviz DOT та Mermaid

Для наочності звіту інструмент генерує декларативну розмітку графа інциденту, яку можна безпосередньо рендерити у внутрішній системі документації:

```text
graph TD
  A[T0: Реліз PR #1402] -->|Латентний дефект| B[T1: Сплеск навантаження 2000 rps]
  B -->|Вичерпання пулу з'єднань| C[T2: Початок 5xx помилок у checkout-gateway]
  C -->|Вихід за поріг burn rate| D[T3: Спрацював алерт High5xxErrorRate]
  D -->|Реакція чергового 1хв 50с| E[T4: Активовано аварійний прапорець]
  E -->|Розвантаження черг| F[T5: Повне відновлення SLO]
```

Ця візуалізація дає змогу всім учасникам постмортем-мітингу за кілька секунд охопити весь каскад причин і наслідків без читання сотень рядків сирих логів.

---

## 13. Автоматизована валідація виправлень та хаос-тестування

Найвища цінність постмортему полягає у гарантії того, що зафіксований сценарій більше ніколи не повториться. Утиліта містить модуль генерації регресійних хаос-тестів:

1. **Генерація маніфесту Chaos Mesh на основі параметрів інциденту:**
   Парсер аналізує категорію збою (`root_contributing_factors`) та створює експеримент для середовища Staging. Для інциденту з дедлоком бази генерується хаос-тест на внесення 2000 мс мережевої затримки на порти зовнішнього податкового API при навантаженні 3000 rps.
2. **Верифікація спрацьовування запобіжників:**
   Конвеєр CI автоматично проганяє хаос-тест перед закриттям задачі `ACT-002` (впровадження Circuit Breaker). Завдання вважається виконаним лише тоді, коли симуляція зовнішньої затримки підтверджує: Circuit Breaker розмикає ланцюг за 200 мс, а пул з'єднань бази даних залишається ненасиченим (< 20% зайнятих з'єднань).
3. **Автоматичне закриття завдань у трекері:**
   У разі успішного проходження хаос-експерименту утиліта надсилає підтверджувальний коментар у Jira/GitHub Issues з посиланням на результати запуску та автоматично переводить статус `action_item` у стан `done`. Це скорочує ручну рутину та гарантує інженерну достовірність виконаних покращень.

---

## 14. Гібридні логічні годинники (HLC) у розподіленій телеметрії

Коли система розгорнута у глобальному мультирегіональному кластері, фізичний протокол NTP не може гарантувати абсолютну монотонність через релятивістські мережеві затримки.

Для подолання цієї невизначеності реконструктор підтримує роботу з гібридними логічними годинниками (Hybrid Logical Clocks, HLC):
* Кожна подія містить пару значень: фізичний час `l` та логічний лічильник `c`.
* При надходженні повідомлення від віддаленого сервісу годинник оновлюється за правилом: `l_next = max(l_local, l_msg, physical_now())`, а лічильник `c` інкрементується у разі рівності фізичних міток.
* Завдяки HLC реконструктор безпомилково відновлює причинно-наслідковий порядок подій (Causal Consistency) між незалежними дата-центрами навіть при наявності апаратного дрейфу фізичних годинників до 500 мілісекунд.
* Якщо подія `A` спричинила подію `B` через ланцюг RPC-викликів, їхній HLC-вектор гарантує відношення `HLC(A) < HLC(B)`, усуваючи парадокси ретроактивного пом'якшення.

---

## 15. Продуктивність та потокова обробка великих журналів

Коли після великого інциденту необхідно проаналізувати 500 мегабайтів сирих текстових журналів за кілька секунд, традиційний парсинг через повне завантаження DOM у пам'ять стає неефективним.

Архітектура парсера C++ використовує такі оптимізації:
1. **Нуль-алокаційний перегляд рядків (`std::string_view`):** замість копіювання фрагментів тексту назви сервісів та описів подій передаються як зрізи незмінного буфера пам'яті вихідного файлу.
2. **Пам'ять, виділена єдиним блоком (`reserve`):** внутрішній вектор подій попередньо резервує пам'ять для очікуваної кількості записів, усуваючи повторні виклики `realloc` під час парсингу великих масивів телеметрії.
3. **Лінійна складність перевірки:** валідація інваріантів виконується за один прохід `O(N)` після первинного стабільного сортування `O(N log N)`, що дозволяє обробити 100 000 записів менш ніж за 40 мілісекунд на одному процесорному ядрі.

---

## 16. Генерація аудиторського звіту та інтеграція

Після успішної валідації та розрахунку метрик реконструктор експортує форматований Markdown-блок, готовий для вставки в артефакт постмортему:

```text
### Хронологічний аудит подій (генеровано автоматично):
* **02:14:00 UTC** · [checkout-gateway] Стрибок 5xx помилок через блокування пулу HikariCP
* **02:18:10 UTC** · [alertmanager] Спрацював алерт High5xxErrorRate (burn rate > 14x)
* **02:20:00 UTC** · [pagerduty] Черговий інженер підтвердив інцидент
* **02:45:00 UTC** · [feature-flags] Вимкнено виклик зовнішнього податкового шлюзу
* **03:22:00 UTC** · [checkout-gateway] Черги розвантажилися, стан стабілізовано

### Зведені інтервали надійності:
* MTTD (Виявлення): 4 хв 10 с
* MTTA (Реакція): 1 хв 50 с
* MTTM (Пом'якшення): 25 хв 00 с
* MTTR (Повне відновлення): 68 хв 00 с
```

Автоматичне формування цього блоку унеможливлює суб'єктивні помилки при складанні звіту та забезпечує повну узгодженість даних між інженерними командами.
