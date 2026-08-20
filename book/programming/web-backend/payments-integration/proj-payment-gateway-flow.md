# ⚙️ Наскрізний конвеєр обробки платежів та безпечних вебхуків

Цей проєкт демонструє повну реалізацію бекенд-вузла інтеграції з платіжним провайдером. Розподілена природа фінансових транзакцій не дозволяє вважати списання грошей звичайним синхронним HTTP-викликом: збої в мережі, відтерміновані банківські перевірки за стандартом 3D Secure 2, дубльовані вебхуки та ризик порушення порядку доставки подій вимагають суворої архітектурної дисципліни.

Архітектура розглядає шість критичних етапів надійного платіжного конвеєра:
1. **Ідемпотентне створення та підтвердження списання (PaymentIntent):** робота з ізольованими клієнтськими токенами, передача детермінованого заголовка `Idempotency-Key` та обробка асинхронного челенджу 3DS 2.0.
2. **Криптографічно захищений обробник вебхуків:** валідація підпису HMAC-SHA256 без попередньої десеріалізації тіла, захист від атак за часом (timing attacks) та перевірка часового вікна для запобігання атакам повторного відтворення (replay attacks).
3. **Дедуплікація подій та монотонний захист станів (State Guard):** ізоляція обробки подій у транзакціях бази даних та захист від ситуацій, коли пізніша подія приходить раніше за попередню.
4. **Збереження платіжного засобу для підписок (SetupIntent):** отримання банківської згоди на регулярні списання без присутності покупця (off-session).
5. **Обробка повернень коштів (Refunds):** сторнування операцій та коригування балансів при частковому чи повному поверненні.
6. **Обробка спорів (Disputes / Chargebacks) та блокування ризикових замовлень:** обробка вебхука `charge.dispute.created` із автоматичним формуванням резерву збитків у головній книзі.

## Крок 1: Ініціалізація та ідемпотентне створення списання

Коли покупець завершує оформлення замовлення, клієнтський браузер через безпечний iframe платіжного шлюзу (Hosted Fields) токенізує сирі реквізити банківської картки (PAN, CVV). Платіжний провайдер зберігає дані в ізольованому PCI-сховищі й повертає клієнту непрозорий токен платіжного засобу (`pm_1N4x9k...`). Фронтенд передає цей токен на власний бекенд разом із номером кошика чи замовлення.

Бекенд формує запит на створення платіжного наміру (PaymentIntent). Оскільки будь-який мережевий запит між бекендом магазину та шлюзом може перерватися через таймаут після фактичного списання коштів, бекенд генерує детермінований ключ ідемпотентності (`Idempotency-Key`). Цей ключ прив'язується до комбінації ідентифікатора замовлення та суми. Якщо клієнт повторить спробу чекауту через обрив зв'язку, провайдер розпізнає повторний ключ і поверне збережений результат замість повторного списання грошей з картки.

Якщо банк-емітент вимагає обов'язкової автентифікації покупця (SCA відповідно до європейської директиви PSD2), платіжний намір переходить у стан `requires_action`. Бекенд повертає клієнту тимчасовий токен `client_secret`, за допомогою якого фронтенд запускає модальне вікно підтвердження 3DS (введення SMS-коду або підтвердження у банківському додатку):

:::tabs
```typescript
import crypto from "node:crypto";

export interface CreatePaymentParams {
  orderId: string;
  amountCents: number;
  currency: string;
  paymentMethodId: string;
  customerId: string;
}

export type PaymentIntentStatus =
  | "requires_payment_method"
  | "requires_confirmation"
  | "requires_action"
  | "processing"
  | "requires_capture"
  | "succeeded"
  | "canceled"
  | "failed";

export interface PaymentIntentResult {
  intentId: string;
  status: PaymentIntentStatus;
  clientSecret: string | null;
  requiresAction: boolean;
}

export class PaymentGatewayService {
  constructor(
    private readonly apiKey: string,
    private readonly pspBaseUrl: string = "https://api.stripe.com/v1"
  ) {}

  /**
   * Створює та ідемпотентно підтверджує платіжний намір.
   */
  async processCheckout(params: CreatePaymentParams): Promise<PaymentIntentResult> {
    // Детермінований ключ ідемпотентності для захисту від мережевих повторів
    const idempotencyKey = `checkout_${params.orderId}_${params.amountCents}`;

    const payload = new URLSearchParams({
      amount: params.amountCents.toString(),
      currency: params.currency.toLowerCase(),
      payment_method: params.paymentMethodId,
      confirm: "true", // Спробувати списати негайно
      "metadata[order_id]": params.orderId,
      "metadata[customer_id]": params.customerId,
      capture_method: "automatic",
    });

    const response = await fetch(`${this.pspBaseUrl}/payment_intents`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        "Content-Type": "application/x-www-form-urlencoded",
        "Idempotency-Key": idempotencyKey,
      },
      body: payload.toString(),
    });

    if (!response.ok) {
      const errorBody = await response.json();
      throw new Error(`Платіж відхилено: ${errorBody.error?.message ?? "Невідома помилка"}`);
    }

    const data = await response.json();
    return {
      intentId: data.id,
      status: data.status as PaymentIntentStatus,
      clientSecret: data.client_secret ?? null,
      requiresAction: data.status === "requires_action",
    };
  }
}
```
```python
import urllib.parse
import urllib.request
import json
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class CreatePaymentParams:
    order_id: str
    amount_cents: int
    currency: str
    payment_method_id: str
    customer_id: str

@dataclass(frozen=True)
class PaymentIntentResult:
    intent_id: str
    status: str
    client_secret: Optional[str]
    requires_action: bool

class PaymentGatewayService:
    def __init__(self, api_key: str, base_url: str = "https://api.stripe.com/v1"):
        self._api_key = api_key
        self._base_url = base_url

    def process_checkout(self, params: CreatePaymentParams) -> PaymentIntentResult:
        # Формування детермінованого ключа ідемпотентності
        idempotency_key = f"checkout_{params.order_id}_{params.amount_cents}"

        form_data = urllib.parse.urlencode({
            "amount": str(params.amount_cents),
            "currency": params.currency.lower(),
            "payment_method": params.payment_method_id,
            "confirm": "true",
            "metadata[order_id]": params.order_id,
            "metadata[customer_id]": params.customer_id,
            "capture_method": "automatic",
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self._base_url}/payment_intents",
            data=form_data,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Idempotency-Key": idempotency_key,
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                status = data.get("status", "unknown")
                return PaymentIntentResult(
                    intent_id=data["id"],
                    status=status,
                    client_secret=data.get("client_secret"),
                    requires_action=(status == "requires_action"),
                )
        except urllib.error.HTTPError as err:
            err_data = json.loads(err.read().decode("utf-8"))
            msg = err_data.get("error", {}).get("message", "Помилка платіжного шлюзу")
            raise RuntimeError(f"Платіж відхилено: {msg}") from err
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <optional>
#include <expected>
#include <cstdint>
#include <format>
#include <sstream>

struct CreatePaymentParams {
    std::string order_id;
    int64_t amount_cents;
    std::string currency;
    std::string payment_method_id;
    std::string customer_id;
};

enum class PaymentIntentStatus {
    RequiresPaymentMethod,
    RequiresConfirmation,
    RequiresAction,
    Processing,
    RequiresCapture,
    Succeeded,
    Canceled,
    Failed,
    Unknown
};

struct PaymentIntentResult {
    std::string intent_id;
    PaymentIntentStatus status;
    std::optional<std::string> client_secret;
    bool requires_action;
};

class PaymentGatewayService {
private:
    std::string api_key_;
    std::string base_url_;

public:
    explicit PaymentGatewayService(std::string_view api_key,
                                  std::string_view base_url = "https://api.stripe.com/v1")
        : api_key_(api_key), base_url_(base_url) {}

    [[nodiscard]] std::string make_idempotency_key(const CreatePaymentParams& params) const {
        return std::format("checkout_{}_{}", params.order_id, params.amount_cents);
    }

    [[nodiscard]] std::expected<PaymentIntentResult, std::string>
    process_checkout(const CreatePaymentParams& params) const {
        const std::string idem_key = make_idempotency_key(params);

        if (params.amount_cents <= 0) {
            return std::unexpected("Сума списання повинна бути додатною");
        }

        // Імітація обробки відповіді шлюзу у разі потреби 3DS автентифікації
        PaymentIntentResult result{
            .intent_id = "pi_mock_99182312",
            .status = PaymentIntentStatus::RequiresAction,
            .client_secret = "pi_mock_99182312_secret_test",
            .requires_action = true
        };

        return result;
    }
};
```
:::

## Крок 2: Верифікація криптографічного підпису вебхуків

Повернення покупця на сторінку підтвердження замовлення (`return_url`) ніколи не розглядається як остаточний доказ успіху оплати. Покупець може випадково закрити вкладку до завершення редиректу, розрядити акумулятор телефона, або зловмисник може спробувати сфальсифікувати GET-параметри запиту. Єдиним джерелом правди про фінансовий кліринг є асинхронний вебхук, надісланий серверами платіжного провайдера.

Оскільки ендпоїнт вебхука відкритий для публічного інтернету, будь-хто може відправити туди підроблені дані про нібито оплачене замовлення. Для захисту від спуфінгу та підробки даних кожен запит супроводжується криптографічним підписом у заголовку `Stripe-Signature` (або `X-Signature`).

Процедура валідації вимагає суворого дотримання трьох інженерних правил:
1. **Перевірка мітки часу:** заголовок містить поле `t=timestamp`. Якщо різниця між системним часом сервера торговця та міткою перевищує 300 секунд, запит відхиляється. Це запобігає атакам повторного відтворення (replay attacks), коли зловмисник записує перехоплений валідний вебхук і надсилає його повторно через місяць.
2. **Незмінне сире тіло (Raw Body):** обчислення HMAC-SHA256 здійснюється над конкатенацією `${t}.${raw_body}`. Тіло запиту береться у вигляді байтового буфера до того, як HTTP-фреймворк розпарсить його в JSON-об'єкт. Якщо порядок ключів або відступи в JSON зміняться, криптографічний геш перестане збігатися.
3. **Порівняння за сталий час:** результуючий геш звіряється з отриманим виключно через функцію `crypto.timingSafeEqual`, яка витрачає однаковий час незалежно від того, на якому саме байті сталася розбіжність, що блокує атаки викрадення підпису за часом відгуку:

:::tabs
```typescript
import crypto from "node:crypto";

export interface VerifiedWebhookEvent {
  id: string;
  type: string;
  data: {
    object: Record<string, any>;
  };
}

export class WebhookSignatureVerifier {
  constructor(
    private readonly webhookSecret: string,
    private readonly toleranceSeconds: number = 300
  ) {}

  /**
   * Перевіряє справжність вебхука за сталий час та з урахуванням мітки часу.
   */
  verifyAndParse(rawBody: Buffer, signatureHeader: string): VerifiedWebhookEvent {
    const parts = signatureHeader.split(",");
    let timestamp = "";
    let signature = "";

    for (const part of parts) {
      const [key, value] = part.trim().split("=");
      if (key === "t") timestamp = value;
      if (key === "v1") signature = value;
    }

    if (!timestamp || !signature) {
      throw new Error("Невалідний формат заголовка Stripe-Signature");
    }

    // 1. Перевірка часового вікна (Replay Attack Prevention)
    const eventTime = Number.parseInt(timestamp, 10);
    const currentTime = Math.floor(Date.now() / 1000);
    if (Number.isNaN(eventTime) || Math.abs(currentTime - eventTime) > this.toleranceSeconds) {
      throw new Error("Мітка часу вебхука виходить за межі допустимого вікна (replay attack)");
    }

    // 2. Обчислення очікуваного HMAC-SHA256 підпису
    const signedPayload = `${timestamp}.${rawBody.toString("utf8")}`;
    const hmac = crypto.createHmac("sha256", this.webhookSecret);
    hmac.update(signedPayload);
    const expectedSignature = hmac.digest("hex");

    // 3. Порівняння за сталий час для захисту від timing attacks
    const sigBuffer = Buffer.from(signature, "hex");
    const expectedBuffer = Buffer.from(expectedSignature, "hex");

    if (sigBuffer.length !== expectedBuffer.length || !crypto.timingSafeEqual(sigBuffer, expectedBuffer)) {
      throw new Error("Криптографічний підпис вебхука не збігається");
    }

    return JSON.parse(rawBody.toString("utf8")) as VerifiedWebhookEvent;
  }
}
```
```python
import hmac
import hashlib
import time
import json
from typing import Dict, Any

class WebhookSignatureVerifier:
    def __init__(self, webhook_secret: str, tolerance_seconds: int = 300):
        self._secret = webhook_secret.encode("utf-8")
        self._tolerance = tolerance_seconds

    def verify_and_parse(self, raw_body: bytes, signature_header: str) -> Dict[str, Any]:
        parts = dict(item.strip().split("=", 1) for item in signature_header.split(","))
        timestamp = parts.get("t")
        received_sig = parts.get("v1")

        if not timestamp or not received_sig:
            raise ValueError("Некоректний заголовок Stripe-Signature")

        # 1. Перевірка мітки часу
        event_time = int(timestamp)
        now = int(time.time())
        if abs(now - event_time) > self._tolerance:
            raise ValueError("Мітка часу виходить за допустимі межі (загроза повтору)")

        # 2. Обчислення очікуваного HMAC
        signed_payload = f"{timestamp}.".encode("utf-8") + raw_body
        expected_sig = hmac.new(self._secret, signed_payload, hashlib.sha256).hexdigest()

        # 3. Порівняння за сталий час
        if not hmac.compare_digest(expected_sig, received_sig):
            raise ValueError("Підпис вебхука недійсний")

        return json.loads(raw_body.decode("utf-8"))
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <expected>
#include <chrono>
#include <sstream>
#include <iomanip>
#include <span>

// Функція для безпечного порівняння двох буферів за сталий час
bool constant_time_compare(std::span<const uint8_t> a, std::span<const uint8_t> b) {
    if (a.size() != b.size()) return false;
    uint8_t result = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        result |= a[i] ^ b[i];
    }
    return result == 0;
}

class WebhookSignatureVerifier {
private:
    std::string secret_;
    int64_t tolerance_seconds_;

public:
    explicit WebhookSignatureVerifier(std::string_view secret, int64_t tolerance = 300)
        : secret_(secret), tolerance_seconds_(tolerance) {}

    [[nodiscard]] std::expected<bool, std::string>
    verify_header(std::string_view raw_payload, std::string_view header, int64_t current_timestamp) const {
        std::string_view timestamp_str;
        std::string_view signature_hex;

        std::stringstream ss{std::string(header)};
        std::string item;
        while (std::getline(ss, item, ',')) {
            auto eq_pos = item.find('=');
            if (eq_pos != std::string::npos) {
                auto key = item.substr(0, eq_pos);
                auto val = item.substr(eq_pos + 1);
                if (key == "t") timestamp_str = val;
                if (key == "v1") signature_hex = val;
            }
        }

        if (timestamp_str.empty() || signature_hex.empty()) {
            return std::unexpected("Відсутні обов'язкові параметри t або v1 у заголовку");
        }

        int64_t event_time = std::stoll(std::string(timestamp_str));
        if (std::abs(current_timestamp - event_time) > tolerance_seconds_) {
            return std::unexpected("Мітка часу вебхука застаріла або з майбутнього");
        }

        return true;
    }
};
```
:::

## Крок 3: Дедуплікація, захист хронології та подвійний бухгалтерський запис

Оскільки платіжні шлюзи використовують гарантію доставки «щонайменше один раз» (at-least-once delivery) з повторними спробами при затримках відповідей, один і той самий вебхук гарантовано прийде кілька разів. Крім того, внаслідок асинхронної маршрутизації в чергах повідомлень подія `payment_intent.succeeded` може прибути на обробник раніше, ніж початкова подія `payment_intent.created`.

Щоб гарантувати абсолютну цілісність, обробник виконує три критичні кроки в межах єдиної транзакції бази даних:
1. **Дедуплікація повідомлень:** ідентифікатор події (`event.id`) фіксується в таблиці оброблених подій (`processed_events`) з унікальним обмеженням (`UNIQUE CONSTRAINT`). Якщо подія з таким ID вже була зафіксована, обробник негайно повертає статус успіху `200 OK`, не виконуючи повторних дій.
2. **Монотонний захист станів (State Guard):** локальний запис замовлення блокується на рівні рядка (`SELECT FOR UPDATE`). Якщо замовлення вже перейшло в стан `PAID`, будь-які запізнілі або проміжні події безпечно ігноруються.
3. **Фінансовий подвійний запис (Ledger Booking):** сума списання та утримана провайдером комісія заносяться в незмінний фінансовий журнал у вигляді збалансованих дебетових і кредитових проводок:

:::tabs
```typescript
export interface OrderRecord {
  id: string;
  status: "PENDING" | "PAID" | "CANCELED" | "REFUNDED";
  amountCents: number;
}

export interface LedgerLine {
  accountId: string; // Наприклад: '1010-PSP-CLEARING', '4010-REVENUE', '5010-FEES'
  debitCents: number;
  creditCents: number;
}

export class OrderFulfillmentCoordinator {
  private readonly processedEventIds = new Set<string>();
  private readonly orders = new Map<string, OrderRecord>();
  private readonly ledger: LedgerLine[] = [];

  constructor() {
    // Ініціалізація тестового замовлення в БД
    this.orders.set("ord_884920", {
      id: "ord_884920",
      status: "PENDING",
      amountCents: 10990,
    });
  }

  /**
   * Атомарна та ідемпотентна обробка події payment_intent.succeeded.
   */
  async handlePaymentSucceeded(event: {
    id: string;
    data: { object: { id: string; amount: number; metadata: { order_id: string } } };
  }): Promise<{ status: "PROCESSED" | "ALREADY_PROCESSED" | "IGNORED_OLD_STATE" }> {
    const eventId = event.id;

    // 1. Дедуплікація: перевірка чи подія вже оброблялася
    if (this.processedEventIds.has(eventId)) {
      return { status: "ALREADY_PROCESSED" };
    }

    const orderId = event.data.object.metadata.order_id;
    const order = this.orders.get(orderId);
    if (!order) {
      throw new Error(`Замовлення ${orderId} не знайдено в локальній базі`);
    }

    // 2. Монотонний захист станів (State Guard)
    if (order.status === "PAID") {
      this.processedEventIds.add(eventId);
      return { status: "IGNORED_OLD_STATE" };
    }

    // 3. Атомарне оновлення замовлення та фіксація у фінансовому журналі (Ledger)
    order.status = "PAID";

    const amount = event.data.object.amount;
    const estimatedFee = Math.round(amount * 0.029 + 30); // 2.9% + 30¢

    // Подвійний запис: Дебет активів (PSP), Кредит доходів (Sales)
    this.ledger.push(
      { accountId: "1010-PSP-CLEARING", debitCents: amount, creditCents: 0 },
      { accountId: "4010-SALES-REVENUE", debitCents: 0, creditCents: amount },
      // Проводка комісії шлюзу
      { accountId: "5010-GATEWAY-EXPENSE", debitCents: estimatedFee, creditCents: 0 },
      { accountId: "1010-PSP-CLEARING", debitCents: 0, creditCents: estimatedFee }
    );

    this.processedEventIds.add(eventId);
    return { status: "PROCESSED" };
  }

  getOrder(orderId: string): OrderRecord | undefined {
    return this.orders.get(orderId);
  }

  getLedgerBalance(accountId: string): number {
    return this.ledger
      .filter((l) => l.accountId === accountId)
      .reduce((acc, l) => acc + l.debitCents - l.creditCents, 0);
  }
}
```
```python
from dataclasses import dataclass
from typing import Dict, List, Set, Optional

@dataclass
class OrderRecord:
    id: str
    status: str
    amount_cents: int

@dataclass
class LedgerLine:
    account_id: str
    debit_cents: int
    credit_cents: int

class OrderFulfillmentCoordinator:
    def __init__(self):
        self._processed_events: Set[str] = set()
        self._orders: Dict[str, OrderRecord] = {
            "ord_884920": OrderRecord(id="ord_884920", status="PENDING", amount_cents=10990)
        }
        self._ledger: List[LedgerLine] = []

    def handle_payment_succeeded(self, event: Dict) -> str:
        event_id = event["id"]

        # 1. Дедуплікація
        if event_id in self._processed_events:
            return "ALREADY_PROCESSED"

        obj = event["data"]["object"]
        order_id = obj.get("metadata", {}).get("order_id")
        order = self._orders.get(order_id)

        if not order:
            raise KeyError(f"Замовлення {order_id} не знайдено")

        # 2. Монотонний State Guard
        if order.status == "PAID":
            self._processed_events.add(event_id)
            return "IGNORED_OLD_STATE"

        # 3. Оновлення стану та запис до Ledger
        order.status = "PAID"
        amount = obj["amount"]
        fee = round(amount * 0.029 + 30)

        # Проводки подвійного запису
        self._ledger.extend([
            LedgerLine(account_id="1010-PSP-CLEARING", debit_cents=amount, credit_cents=0),
            LedgerLine(account_id="4010-SALES-REVENUE", debit_cents=0, credit_cents=amount),
            LedgerLine(account_id="5010-GATEWAY-EXPENSE", debit_cents=fee, credit_cents=0),
            LedgerLine(account_id="1010-PSP-CLEARING", debit_cents=0, credit_cents=fee),
        ])

        self._processed_events.add(event_id)
        return "PROCESSED"
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <cstdint>
#include <cmath>

enum class OrderStatus {
    Pending,
    Paid,
    Canceled,
    Refunded
};

struct OrderRecord {
    std::string id;
    OrderStatus status;
    int64_t amount_cents;
};

struct LedgerLine {
    std::string account_id;
    int64_t debit_cents;
    int64_t credit_cents;
};

class OrderFulfillmentCoordinator {
private:
    std::unordered_set<std::string> processed_event_ids_;
    std::unordered_map<std::string, OrderRecord> orders_;
    std::vector<LedgerLine> ledger_;

public:
    OrderFulfillmentCoordinator() {
        orders_["ord_884920"] = OrderRecord{
            .id = "ord_884920",
            .status = OrderStatus::Pending,
            .amount_cents = 10990
        };
    }

    std::string handle_payment_succeeded(const std::string& event_id,
                                         const std::string& order_id,
                                         int64_t amount_cents) {
        // 1. Дедуплікація подій
        if (processed_event_ids_.contains(event_id)) {
            return "ALREADY_PROCESSED";
        }

        auto it = orders_.find(order_id);
        if (it == orders_.end()) {
            return "ORDER_NOT_FOUND";
        }

        // 2. Монотонний захист станів (State Guard)
        if (it->second.status == OrderStatus::Paid) {
            processed_event_ids_.insert(event_id);
            return "IGNORED_OLD_STATE";
        }

        // 3. Зміна стану та подвійний бухгалтерський запис
        it->second.status = OrderStatus::Paid;
        const int64_t fee = static_cast<int64_t>(std::round(amount_cents * 0.029 + 30));

        ledger_.push_back(LedgerLine{.account_id = "1010-PSP-CLEARING", .debit_cents = amount_cents, .credit_cents = 0});
        ledger_.push_back(LedgerLine{.account_id = "4010-SALES-REVENUE", .debit_cents = 0, .credit_cents = amount_cents});
        ledger_.push_back(LedgerLine{.account_id = "5010-GATEWAY-EXPENSE", .debit_cents = fee, .credit_cents = 0});
        ledger_.push_back(LedgerLine{.account_id = "1010-PSP-CLEARING", .debit_cents = 0, .credit_cents = fee});

        processed_event_ids_.insert(event_id);
        return "PROCESSED";
    }

    [[nodiscard]] int64_t get_account_net_balance(const std::string& account_id) const {
        int64_t balance = 0;
        for (const auto& line : ledger_) {
            if (line.account_id == account_id) {
                balance += (line.debit_cents - line.credit_cents);
            }
        }
        return balance;
    }
};
```
:::

## Крок 4: Збереження платіжного засобу під регулярні підписки (SetupIntent)

Для SaaS-сервісів та періодичних підписок клієнт не може вводити CVV-код щомісяця. Бекенд зобов'язаний зберегти платіжний засіб із попередньою згодою банку на безконтактні списання без присутності покупця (Merchant Initiated Transactions, MIT).

Для цього створюється об'єкт `SetupIntent`. Він проводить первинну верифікацію картки з проходженням 3D Secure 2 без фактичного зняття коштів:

:::tabs
```typescript
export interface SetupCardParams {
  customerId: string;
  paymentMethodId: string;
}

export class SubscriptionSetupService {
  constructor(
    private readonly apiKey: string,
    private readonly pspBaseUrl: string = "https://api.stripe.com/v1"
  ) {}

  /**
   * Створює SetupIntent для прив'язки картки до клієнта під майбутні підписки.
   */
  async attachPaymentMethod(params: SetupCardParams): Promise<{ setupIntentId: string; status: string }> {
    const payload = new URLSearchParams({
      customer: params.customerId,
      payment_method: params.paymentMethodId,
      usage: "off_session", // Дозвіл на списання у фоні
      confirm: "true",
    });

    const response = await fetch(`${this.pspBaseUrl}/setup_intents`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        "Content-Type": "application/x-www-form-urlencoded",
        "Idempotency-Key": `setup_${params.customerId}_${params.paymentMethodId}`,
      },
      body: payload.toString(),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(`Помилка прив'язки картки: ${err.error?.message ?? "Невідома помилка"}`);
    }

    const data = await response.json();
    return {
      setupIntentId: data.id,
      status: data.status,
    };
  }
}
```
```python
import urllib.parse
import urllib.request
import json
from typing import Dict

class SubscriptionSetupService:
    def __init__(self, api_key: str, base_url: str = "https://api.stripe.com/v1"):
        self._api_key = api_key
        self._base_url = base_url

    def attach_payment_method(self, customer_id: str, payment_method_id: str) -> Dict[str, str]:
        payload = urllib.parse.urlencode({
            "customer": customer_id,
            "payment_method": payment_method_id,
            "usage": "off_session",
            "confirm": "true"
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self._base_url}/setup_intents",
            data=payload,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Idempotency-Key": f"setup_{customer_id}_{payment_method_id}"
            },
            method="POST"
        )

        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {
                "setup_intent_id": data["id"],
                "status": data["status"]
            }
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <expected>
#include <format>

struct SetupCardResult {
    std::string setup_intent_id;
    std::string status;
};

class SubscriptionSetupService {
private:
    std::string api_key_;
    std::string base_url_;

public:
    explicit SubscriptionSetupService(std::string_view api_key,
                                    std::string_view base_url = "https://api.stripe.com/v1")
        : api_key_(api_key), base_url_(base_url) {}

    [[nodiscard]] std::expected<SetupCardResult, std::string>
    attach_payment_method(std::string_view customer_id, std::string_view payment_method_id) const {
        if (customer_id.empty() || payment_method_id.empty()) {
            return std::unexpected("Ідентифікатори клієнта та методу оплати не можуть бути порожніми");
        }

        // Імітація успішного отримання мандата off-session
        return SetupCardResult{
            .setup_intent_id = std::format("seti_{}_{}", customer_id, payment_method_id),
            .status = "succeeded"
        };
    }
};
```
:::

## Крок 5: Обробка повернень (Refunds) та коригування фінансового балансу

Повернення коштів (Refund) є дзеркальною фінансовою операцією, яка може ініціюватися як торговцем через панель адміністрування чи API, так і покупцем за погодженим зверненням. На відміну від скасування непідтвердженої авторизації (`Void`), повернення вже списаного платежу не повертає фіксовану транзакційну комісію еквайрингу й займає від 3 до 5 банківських днів на повернення коштів на картковий рахунок клієнта.

Коли провайдер завершує повернення коштів, на бекенд надходить вебхук `charge.refunded`. Обробник зобов'язаний сформувати сторнуючі проводки в головній книзі (зменшення активів транзитного рахунку та дебетування контрарного рахунку повернень продажу), гарантуючи, що баланси товарних залишків та виручки залишаються строго збалансованими:

:::tabs
```typescript
export interface RefundRequestParams {
  paymentIntentId: string;
  amountCents?: number; // Необов'язково для повного повернення
  reason?: "duplicate" | "fraudulent" | "requested_by_customer";
}

export class PaymentRefundService {
  constructor(
    private readonly apiKey: string,
    private readonly pspBaseUrl: string = "https://api.stripe.com/v1"
  ) {}

  /**
   * Ініціює повне або часткове повернення коштів за платіжним наміром.
   */
  async processRefund(params: RefundRequestParams): Promise<{ refundId: string; status: string }> {
    const payloadData: Record<string, string> = {
      payment_intent: params.paymentIntentId,
    };
    if (params.amountCents) {
      payloadData.amount = params.amountCents.toString();
    }
    if (params.reason) {
      payloadData.reason = params.reason;
    }

    const payload = new URLSearchParams(payloadData);
    const idempotencyKey = `refund_${params.paymentIntentId}_${params.amountCents ?? "full"}`;

    const response = await fetch(`${this.pspBaseUrl}/refunds`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        "Content-Type": "application/x-www-form-urlencoded",
        "Idempotency-Key": idempotencyKey,
      },
      body: payload.toString(),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(`Помилка повернення: ${err.error?.message ?? "Невідома помилка"}`);
    }

    const data = await response.json();
    return {
      refundId: data.id,
      status: data.status,
    };
  }
}
```
```python
import urllib.parse
import urllib.request
import json
from typing import Optional, Dict

class PaymentRefundService:
    def __init__(self, api_key: str, base_url: str = "https://api.stripe.com/v1"):
        self._api_key = api_key
        self._base_url = base_url

    def process_refund(self, payment_intent_id: str, amount_cents: Optional[int] = None) -> Dict[str, str]:
        payload_dict = {"payment_intent": payment_intent_id}
        if amount_cents:
            payload_dict["amount"] = str(amount_cents)

        payload = urllib.parse.urlencode(payload_dict).encode("utf-8")
        idempotency_key = f"refund_{payment_intent_id}_{amount_cents or 'full'}"

        req = urllib.request.Request(
            f"{self._base_url}/refunds",
            data=payload,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Idempotency-Key": idempotency_key,
            },
            method="POST",
        )

        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {
                "refund_id": data["id"],
                "status": data["status"]
            }
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <optional>
#include <expected>
#include <format>

struct RefundResult {
    std::string refund_id;
    std::string status;
};

class PaymentRefundService {
private:
    std::string api_key_;
    std::string base_url_;

public:
    explicit PaymentRefundService(std::string_view api_key,
                                 std::string_view base_url = "https://api.stripe.com/v1")
        : api_key_(api_key), base_url_(base_url) {}

    [[nodiscard]] std::expected<RefundResult, std::string>
    process_refund(std::string_view payment_intent_id, std::optional<int64_t> amount_cents = std::nullopt) const {
        if (payment_intent_id.empty()) {
            return std::unexpected("Ідентифікатор наміру не може бути порожнім");
        }

        return RefundResult{
            .refund_id = std::format("re_{}", payment_intent_id),
            .status = "succeeded"
        };
    }
};
```
:::

## Крок 6: Обробка спорів (Disputes) та формування фінансового резерву

Коли покупець ініціює чарджбек через свій банк, шлюз миттєво списує оскаржувану суму разом зі штрафною комісією $15–$25 і надсилає вебхук `charge.dispute.created`.

Обробник повинен зафіксувати дедлайн надання доказів у базі даних та відобразити списання коштів у бухгалтерському обліку:
- **ДЕБЕТ:** Рахунок втрат від спорів `5020-Dispute-Expense` (штраф $15.00).
- **ДЕБЕТ:** Контрарний рахунок резервів `2020-Disputed-Funds-Hold` ($100.00).
- **КРЕДИТ:** Транзитний рахунок шлюзу `1010-PSP-Clearing` ($115.00).

Якщо після надання доказів банк ухвалює рішення на користь магазину (`charge.dispute.closed` зі статусом `won`), система сторнує резерв `2020` і повертає $100 на баланс `1010`. Якщо спір програно (`lost`), зарезервовані кошти остаточно списуються у збитки від неповернених замовлень.
