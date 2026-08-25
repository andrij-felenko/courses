# ⚙️ Шлюз валідації data-контрактів та маршрутизація в карантинний буфер (DLQ)

Шлюз валідації data-контрактів — це спеціалізований програмний компонент на межі прийому інформації (англ. *Ingestion Gatekeeper*), який перехоплює вхідний потік повідомлень від сервісів-продюсерів, перевіряє кожен запис на відповідність затвердженій специфікації контракту та розподіляє потік на два ізольовані канали:

1. **Валідні події:** збагачуються службовими метаданими аудиту (версія контракту, часова мітка прийому) і спрямовуються в основне аналітичне сховище (DWH, Data Lakehouse, таблиці Apache Iceberg / Delta Lake).
2. **Браковані події:** не блокують роботу конвеєра і не видаляються безслідно, а загортаються в стандартизований діагностичний конверт і маршрутизуються в **карантинну чергу помилок** (англ. *Dead Letter Queue*, DLQ) для подальшого розслідування та повторної обробки розробниками продюсера.

## Архітектурні вимоги до шлюзу валідації

Під час проєктування шлюзу валідації на високонавантажених потоках даних необхідно розв'язати три інженерні компроміси:

- **Мінімальна затримка обробки (Low Latency Overhead):** парсинг та валідація не повинні створювати суттєвого уповільнення наскрізної передачі даних. У критичних вузлах це вимагає відсутності зайвих алокацій пам'яті (Zero-Copy) та швидкої перевірки діапазонів значень.
- **Ізоляція відмов (Fault Isolation):** некоректне повідомлення від одного продюсера не повинно зупиняти обробку валідних повідомлень сусідніх сервісів чи переповнювати пам'ять процесу.
- **Повна діагностична прозорість (Observability):** кожен запис у карантині зобов'язаний містити повний первинний рядок байтів, точне ім'я порушеного правила контракту та часову мітку збою.

## Етапи валідаційного конвеєра

Процес верифікації кожного повідомлення у шлюзі складається з чотирьох послідовних кроків:

1. **Синтаксичний розбір:** перевірка коректності структури документа (валідація JSON/Avro). Якщо байти пошкоджені або не є валідним документом, повідомлення негайно відправляється в DLQ із міткою `PARSE_ERROR`.
2. **Перевірка обов'язковості полів (Nullability Check):** перевірка присутності всіх ключів, позначених у контракті як `required: true`.
3. **Контроль типів та обмежень діапазонів:** перевірка, що числові значення не виходять за допустимі межі (`total_amount_cents >= 0`), коди валют відповідають стандарту ISO-4217, а статуси належать дозволеному переліку `enum`.
4. **Оцінка бізнес-інваріантів:** виконання крос-польових правил (наприклад, перевірка інваріанту `tax_amount_cents <= total_amount_cents`).

## Реалізація шлюзу валідації

Нижче наведено повнофункціональну реалізацію шлюзу валідації різними мовами програмування. Кожна реалізація дотримується ідіоматичних підходів своєї екосистеми: обробка помилок через типи-результати, безпека типів та ізоляція буферів.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_set>
#include <optional>
#include <chrono>
#include <memory>

// Структура валідованої бізнес-події замовлення
struct OrderEvent {
    std::string event_id;
    std::string order_id;
    std::string user_id;
    std::string order_state;
    std::string currency;
    int64_t total_amount_cents{0};
    int64_t tax_amount_cents{0};
    int32_t items_count{0};
    std::string created_at;
};

// Діагностичний конверт для ізоляції бракованих записів у DLQ
struct DlqEnvelope {
    std::string dlq_id;
    std::string failed_at;
    std::string contract_version;
    std::string error_reason;
    std::string raw_payload;
};

// Клас валідатора згідно зі специфікацією контракту
class DataContractValidator {
public:
    explicit DataContractValidator(std::string version)
        : contract_version_(std::move(version)),
          valid_states_{"PENDING", "PAID", "PROCESSING", "SHIPPED", "CANCELLED", "REFUNDED"} {}

    // Повертає std::nullopt у разі успіху або опис помилки
    [[nodiscard]] std::optional<std::string> validate(const OrderEvent& ev) const {
        // 1. Перевірка обов'язкових ідентифікаторів
        if (ev.event_id.empty() || ev.order_id.empty() || ev.user_id.empty()) {
            return "Відсутній обов'язковий ідентифікатор (event_id, order_id або user_id)";
        }

        // 2. Контроль числових меж
        if (ev.total_amount_cents < 0) {
            return "Поле total_amount_cents не може бути від'ємним";
        }
        if (ev.items_count <= 0 || ev.items_count > 500) {
            return "Кількість items_count має бути в діапазоні від 1 до 500";
        }

        // 3. Перевірка скінченного автомата статусів
        if (valid_states_.find(ev.order_state) == valid_states_.end()) {
            return "Недопустимий статус order_state: " + ev.order_state;
        }

        // 4. Перевірка формату валюти ISO-4217
        if (ev.currency.size() != 3) {
            return "Код currency має містити рівно 3 символи ISO-4217";
        }

        // 5. Перевірка семантичного бізнес-інваріанту: tax <= total
        if (ev.tax_amount_cents > ev.total_amount_cents) {
            return "Інваріант порушено: tax_amount_cents перевищує total_amount_cents";
        }

        return std::nullopt; // Валідація пройдена успішно
    }

    [[nodiscard]] const std::string& version() const noexcept { return contract_version_; }

private:
    std::string contract_version_;
    std::unordered_set<std::string> valid_states_;
};

// Шлюз маршрутизації потоку даних
class IngestionGateway {
public:
    explicit IngestionGateway(DataContractValidator validator)
        : validator_(std::move(validator)) {}

    void process(const OrderEvent& ev, const std::string& raw_json) {
        if (auto err = validator_.validate(ev); err.has_value()) {
            dlq_sink_.push_back(DlqEnvelope{
                "dlq-uuid-7f8e-4a",
                "2026-08-20T12:00:00Z",
                validator_.version(),
                *err,
                raw_json
            });
        } else {
            dwh_sink_.push_back(ev);
        }
    }

    [[nodiscard]] size_t dwh_count() const noexcept { return dwh_sink_.size(); }
    [[nodiscard]] size_t dlq_count() const noexcept { return dlq_sink_.size(); }

private:
    DataContractValidator validator_;
    std::vector<OrderEvent> dwh_sink_;
    std::vector<DlqEnvelope> dlq_sink_;
};

int main() {
    DataContractValidator validator("2.3.0");
    IngestionGateway gateway(std::move(validator));

    // Валідна подія від коректного сервісу
    OrderEvent good_event{
        "ev-001", "ord-100", "usr-500", "PAID", "USD", 15000, 3000, 2, "2026-08-20T12:00:00Z"
    };

    // Бракована подія (порушення інваріанту та від'ємна сума)
    OrderEvent bad_event{
        "ev-002", "ord-101", "usr-501", "INVALID_STATUS", "USD", -500, 100, 0, "2026-08-20T12:01:00Z"
    };

    gateway.process(good_event, "{\"raw\":\"good_payload\"}");
    gateway.process(bad_event, "{\"raw\":\"bad_payload\"}");

    std::cout << "Прийнято у DWH: " << gateway.dwh_count() 
              << " | Відправлено в DLQ: " << gateway.dlq_count() << "\n";
    return 0;
}
```
```python
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

class DataContractValidator:
    def __init__(self, contract_version: str):
        self.contract_version = contract_version
        self.valid_states = {"PENDING", "PAID", "PROCESSING", "SHIPPED", "CANCELLED", "REFUNDED"}

    def validate_record(self, raw_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        # 1. Перевірка обов'язкових полів (Nullability)
        required_fields = ["event_id", "order_id", "user_id", "order_state", "currency", "total_amount_cents", "created_at"]
        for f in required_fields:
            if f not in raw_data or raw_data[f] is None:
                return False, f"Відсутнє обов'язкове поле: {f}"

        # 2. Перевірка типів і допустимих діапазонів
        amount = raw_data["total_amount_cents"]
        if not isinstance(amount, int) or amount < 0:
            return False, "Поле total_amount_cents має бути невід'ємним цілим числом"

        items = raw_data.get("items_count", 1)
        if not isinstance(items, int) or items <= 0 or items > 500:
            return False, "Поле items_count має бути цілим числом у діапазоні [1, 500]"

        if raw_data["order_state"] not in self.valid_states:
            return False, f"Недопустимий статус order_state: {raw_data['order_state']}"

        if len(raw_data.get("currency", "")) != 3:
            return False, "Код currency має складатися рівно з 3 літер ISO-4217"

        # 3. Перевірка бізнес-інваріанту: tax <= total
        tax = raw_data.get("tax_amount_cents", 0)
        if isinstance(tax, int) and tax > amount:
            return False, "Інваріант порушено: tax_amount_cents перевищує total_amount_cents"

        return True, None

class IngestionGateway:
    def __init__(self, validator: DataContractValidator):
        self.validator = validator
        self.dwh_sink: List[Dict[str, Any]] = []
        self.dlq_sink: List[Dict[str, Any]] = []

    def process_event(self, raw_payload: str) -> None:
        try:
            record = json.loads(raw_payload)
        except Exception as e:
            self._route_to_dlq(raw_payload, f"Помилка парсингу JSON: {str(e)}")
            return

        is_valid, error_reason = self.validator.validate_record(record)
        if is_valid:
            # Збагачення метаданими валідації та запис у DWH
            record["_ingested_at"] = datetime.now(timezone.utc).isoformat()
            record["_contract_version"] = self.validator.contract_version
            self.dwh_sink.append(record)
        else:
            self._route_to_dlq(raw_payload, error_reason)

    def _route_to_dlq(self, payload: Any, reason: Optional[str]) -> None:
        quarantine_envelope = {
            "dlq_id": str(uuid.uuid4()),
            "failed_at": datetime.now(timezone.utc).isoformat(),
            "contract_version": self.validator.contract_version,
            "error_reason": reason,
            "raw_payload": payload
        }
        self.dlq_sink.append(quarantine_envelope)

if __name__ == "__main__":
    val = DataContractValidator("2.3.0")
    gateway = IngestionGateway(val)

    good_event = json.dumps({
        "event_id": "a1b2c3d4-0000-0000-0000-000000000001",
        "order_id": "b2c3d4e5-0000-0000-0000-000000000002",
        "user_id": "c3d4e5f6-0000-0000-0000-000000000003",
        "order_state": "PAID",
        "currency": "USD",
        "total_amount_cents": 15000,
        "tax_amount_cents": 3000,
        "items_count": 2,
        "created_at": "2026-08-20T12:00:00Z"
    })

    bad_event = json.dumps({
        "event_id": "a1b2c3d4-0000-0000-0000-000000000002",
        "order_id": "b2c3d4e5-0000-0000-0000-000000000004",
        "user_id": "c3d4e5f6-0000-0000-0000-000000000005",
        "order_state": "UNKNOWN_STATE",
        "currency": "USD",
        "total_amount_cents": -500,
        "created_at": "2026-08-20T12:01:00Z"
    })

    gateway.process_event(good_event)
    gateway.process_event(bad_event)

    print(f"Прийнято у DWH: {len(gateway.dwh_sink)} | Відправлено в DLQ: {len(gateway.dlq_sink)}")
```
```ts
interface OrderEvent {
  eventId: string;
  orderId: string;
  userId: string;
  orderState: string;
  currency: string;
  totalAmountCents: number;
  taxAmountCents: number;
  itemsCount: number;
  createdAt: string;
}

interface DlqEnvelope {
  dlqId: string;
  failedAt: string;
  contractVersion: string;
  errorReason: string;
  rawPayload: string;
}

class DataContractValidator {
  private readonly validStates = new Set(["PENDING", "PAID", "PROCESSING", "SHIPPED", "CANCELLED", "REFUNDED"]);

  constructor(public readonly contractVersion: string) {}

  public validate(ev: Partial<OrderEvent>): { valid: boolean; error?: string } {
    if (!ev.eventId || !ev.orderId || !ev.userId) {
      return { valid: false, error: "Відсутній обов'язковий ідентифікатор" };
    }
    if (typeof ev.totalAmountCents !== "number" || ev.totalAmountCents < 0) {
      return { valid: false, error: "totalAmountCents має бути невід'ємним числом" };
    }
    if (typeof ev.itemsCount !== "number" || ev.itemsCount <= 0 || ev.itemsCount > 500) {
      return { valid: false, error: "itemsCount має бути числом у межах [1, 500]" };
    }
    if (!ev.orderState || !this.validStates.has(ev.orderState)) {
      return { valid: false, error: `Недопустимий статус orderState: ${ev.orderState}` };
    }
    if (!ev.currency || ev.currency.length !== 3) {
      return { valid: false, error: "Код currency має складатись з 3 символів" };
    }
    if ((ev.taxAmountCents ?? 0) > ev.totalAmountCents) {
      return { valid: false, error: "taxAmountCents перевищує totalAmountCents" };
    }
    return { valid: true };
  }
}

class IngestionGateway {
  public dwhSink: OrderEvent[] = [];
  public dlqSink: DlqEnvelope[] = [];

  constructor(private validator: DataContractValidator) {}

  public process(rawJson: string): void {
    try {
      const parsed = JSON.parse(rawJson) as Partial<OrderEvent>;
      const check = this.validator.validate(parsed);
      if (check.valid) {
        this.dwhSink.push(parsed as OrderEvent);
      } else {
        this.dlqSink.push({
          dlqId: "uuid-dlq-sample",
          failedAt: new Date().toISOString(),
          contractVersion: this.validator.contractVersion,
          errorReason: check.error || "Validation error",
          rawPayload: rawJson,
        });
      }
    } catch (err) {
      this.dlqSink.push({
        dlqId: "uuid-dlq-parse-err",
        failedAt: new Date().toISOString(),
        contractVersion: this.validator.contractVersion,
        errorReason: "JSON parse error",
        rawPayload: rawJson,
      });
    }
  }
}
```
```go
package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"time"
)

type OrderEvent struct {
	EventID          string `json:"event_id"`
	OrderID          string `json:"order_id"`
	UserID           string `json:"user_id"`
	OrderState       string `json:"order_state"`
	Currency         string `json:"currency"`
	TotalAmountCents int64  `json:"total_amount_cents"`
	TaxAmountCents   int64  `json:"tax_amount_cents"`
	ItemsCount       int32  `json:"items_count"`
	CreatedAt        string `json:"created_at"`
}

type DlqEnvelope struct {
	DlqID           string `json:"dlq_id"`
	FailedAt        string `json:"failed_at"`
	ContractVersion string `json:"contract_version"`
	ErrorReason     string `json:"error_reason"`
	RawPayload      string `json:"raw_payload"`
}

type DataContractValidator struct {
	version     string
	validStates map[string]bool
}

func NewValidator(version string) *DataContractValidator {
	return &DataContractValidator{
		version: version,
		validStates: map[string]bool{
			"PENDING": true, "PAID": true, "PROCESSING": true,
			"SHIPPED": true, "CANCELLED": true, "REFUNDED": true,
		},
	}
}

func (v *DataContractValidator) Validate(ev *OrderEvent) error {
	if ev.EventID == "" || ev.OrderID == "" || ev.UserID == "" {
		return errors.New("відсутній обов'язковий ідентифікатор")
	}
	if ev.TotalAmountCents < 0 {
		return errors.New("total_amount_cents не може бути від'ємним")
	}
	if ev.ItemsCount <= 0 || ev.ItemsCount > 500 {
		return errors.New("items_count має бути в діапазоні [1, 500]")
	}
	if !v.validStates[ev.OrderState] {
		return fmt.Errorf("недопустимий статус order_state: %s", ev.OrderState)
	}
	if len(ev.Currency) != 3 {
		return errors.New("код currency має складатись з 3 символів")
	}
	if ev.TaxAmountCents > ev.TotalAmountCents {
		return errors.New("tax_amount_cents перевищує total_amount_cents")
	}
	return nil
}

type IngestionGateway struct {
	validator *DataContractValidator
	DwhSink   []OrderEvent
	DlqSink   []DlqEnvelope
}

func (g *IngestionGateway) Process(rawJSON string) {
	var ev OrderEvent
	if err := json.Unmarshal([]byte(rawJSON), &ev); err != nil {
		g.routeToDlq(rawJSON, "Помилка парсингу JSON: "+err.Error())
		return
	}
	if err := g.validator.Validate(&ev); err != nil {
		g.routeToDlq(rawJSON, err.Error())
		return
	}
	g.DwhSink = append(g.DwhSink, ev)
}

func (g *IngestionGateway) routeToDlq(payload, reason string) {
	g.DlqSink = append(g.DlqSink, DlqEnvelope{
		DlqID:           "dlq-uuid-go-mock",
		FailedAt:        time.Now().UTC().Format(time.RFC3339),
		ContractVersion: g.validator.version,
		ErrorReason:     reason,
		RawPayload:      payload,
	})
}
```
:::

## Інженерні пастки та захист від деградації

Під час експлуатації шлюзів валідації у виробничому середовищі виникають типові критичні ситуації:

### 1. Шторм карантинної черги (DLQ Flooding Storm)
Якщо бекенд-команда випускає багований реліз, що ламає 100% генерованих подій, шлюз валідації починає перенаправляти весь обсяг трафіку в чергу DLQ. Це може спричинити вичерпання дискового простору брокера або переповнення бази даних карантину.
*Захист:* шлюз повинен містити автоматичний запобіжник (Circuit Breaker): якщо частка браку перевищує 50% за 10-секундне вікно, шлюз активує семплювання помилок у DLQ та генерує критичний алерт найвищого пріоритету P1 (PagerDuty) команді продюсера.

### 2. Витік пам'яті через накопичення контексту помилок
Збереження сирих рядків `raw_payload` великого розміру в пам'яті процесу під час сплесків навантаження створює ризик аварійного завершення процесу через Out-of-Memory (OOM).
*Захист:* обмеження максимального розміру сирого пейлоаду в конверті DLQ (наприклад, обрізання до перших 64 КБ) та асинхронне скидання карантинних пакетів на диск через пули потоків.

### 3. Деградація пропускної здатності на регулярних виразах
Використання складних нескомпільованих регулярних виразів для перевірки рядкових полів у гарячому циклі валідації (наприклад, катастрофічний бектрекінг при валідації адрес електронної пошти) може уповільнити обробку в тисячі разів.
*Захист:* попередня компіляція всіх шаблонів регулярних виразів під час ініціалізації валідатора (`std::regex` / `re.compile`) або заміна регулярних виразів на швидкі посимвольні перевірки фіксованої довжини.

## Ідемпотентна дедуплікація на шлюзі вводу

Data-контракт вимагає гарантії унікальності первинного ідентифікатора `event_id`. Оскільки брокери повідомлень (Apache Kafka, RabbitMQ) у разі мережевих збоїв та повторних спроб відправки працюють за моделлю доставки «щонайменше один раз» (англ. *at-least-once delivery*), шлюз валідації повинен здійснювати дедуплікацію потоку.

Для запобігання дублюванню записів у сховищі DWH шлюз застосовує дворівневий механізм фільтрації:
1. **Швидкий імовірнісний фільтр Блума в пам'яті (In-Memory Bloom Filter):** дозволяє миттєво відсіяти 99.9% унікальних подій без звернення до зовнішнього стану.
2. **Розподілений ковзний буфер ідентифікаторів (Redis / RocksDB із TTL):** зберігає хеші `event_id` за останні 24 години. Якщо вхідний `event_id` уже присутній у буфері, подія позначається як дублікат і пропускається повз DWH без генерації помилки в DLQ, забезпечуючи семантику ефективної однократної доставки (англ. *effectively-once processing*).

## Конвеєр повторної обробки з карантину (DLQ Replay Pipeline)

Ізоляція бракованих даних у DLQ має сенс лише тоді, коли існує регламентований процес їх відновлення. Життєвий цикл ліквідації аварії через DLQ складається з чотирьох фаз:

1. **Сповіщення та локалізація:** автоматичний моніторинг фіксує сплеск записів у DLQ, витягує з діагностичного конверта версію коду продюсера та надсилає сповіщення черговому інженеру команди-власника.
2. **Виправлення першопричини (Hotfix):** розробники продюсера виправляють баг у бізнес-коді або узгоджують мінорне оновлення схеми контракту в реєстрі.
3. **Пакетне виправлення даних (Data Mutation / Patching):** якщо дані в карантині містили виправні семантичні помилки (наприклад, переплутаний знак знижки), утиліта відновлення проганяє сирі пейлоади `raw_payload` через скрипт трансформації.
4. **Повторний впуск у конвеєр (Replay Ingestion):** виправлені події з оновленими часовими мітками повторно подаються на вхідний шлюз валідації, успішно проходять перевірку та записуються в аналітичні таблиці сховища без порушення історичної послідовності.

