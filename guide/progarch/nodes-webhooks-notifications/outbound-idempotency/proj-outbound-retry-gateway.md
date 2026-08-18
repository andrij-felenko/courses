# ⚙️ Реалізація вихідного шлюзу з ключем ідемпотентності та авторетраєм

У цьому практичному проєкті ми розглянемо повноцінну реалізацію вихідного ідемпотентного HTTP-шлюзу (Outbound Idempotency Gateway), який використовується сервісами системи Digital Homes для взаємодії зі сторонніми API (платіжними провайдерами Stripe, пуш-сервісами Apple APNs та Google FCM, шлюзами SMS-повідомлень).

Шлюз розв'язує три практичні задачі:
1. **Детерміноване формування ключа**: Обчислює `Idempotency-Key` на основі унікального бізнес-ідентифікатора доменної сутності (`order_id`) без використання випадкових UUID під час ретраїв.
2. **Управління таймаутами та циклом спроб**: Автоматично перехоплює мережеві помилки (`ECONNRESET`, `ETIMEDOUT`), помилки сервера `5xx` та відповіді конфлікту `409 Conflict`, здійснюючи повторні спроби за алгоритмом **Exponential Backoff із дрожанням (Jitter)**.
3. **Класифікація відповідей**: Розрізняє тимчасові мережеві збої (які потребують повтору) від фатальних помилок валідації `4xx` або розходження параметрів `422 Payload Mismatch` (які повторювати заборонено).

---

## Загальна логіка виконання та трасування спроб

Перш ніж переходити до коду різними мовами, простежимо траєкторію виконання одного вихідного запиту на списання коштів за замовлення `ord_9918` на суму $120.00:

1. **Ініціалізація**: Доменний сервіс викликає метод шлюзу `charge_order("ord_9918", 120.00)`.
2. **Формування заголовків**: Шлюз створює ключ `charge_order_ord_9918_v1` та канонічне JSON-тіло `{"amount":120.00,"order_id":"ord_9918"}`.
3. **Перша спроба (Attempt 1)**: Шлюз виконує HTTP POST запит із заголовком `Idempotency-Key: charge_order_ord_9918_v1`. На 4-й секунді очікування виникає мережевий таймаут TCP (`504 Gateway Timeout`). Стан невідомий.
4. **Розрахунок затримки**: Шлюз обирає початкову затримку 1 секунда, засинає.
5. **Друга спроба (Attempt 2)**: Шлюз надсилає **ТОЧНО ТАКИЙ САМИЙ** HTTP POST запит із **ТИМ САМИМ** заголовком `Idempotency-Key: charge_order_ord_9918_v1`. Зовнішнє API повертає статус `HTTP 409 Conflict` (попередній запит ще обробляється у змитому потоці).
6. **Розрахунок затримки**: Шлюз зчитує `409 Conflict`, вираховує нову затримку 2 секунди, засинає.
7. **Третя спроба (Attempt 3)**: Шлюз надсилає третій запит із **ТИМ САМИМ** ключем. Зовнішнє API повертає `HTTP 200 OK` із прапорцем `Idempotent-Replay: true` та збереженим JSON-тілом у спілці.
8. **Успішне завершення**: Шлюз повертає об'єкт відповіді доменному сервісу, бізнес-сагу завершено.

---

## Багатомовні реалізації (:::tabs)

Нижче наведено ідіоматичні реалізації вихідного шлюзу п'ятьма мовами програмування. Кожна реалізація дотримується прийнятих у цій мові патернів управління пам'яттю, обробки помилок та асинхронності.

:::tabs
```c
/* C: Вихідний шлюз з підтримкою Idempotency-Key та автоматичним повтором при таймаутах */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

typedef struct {
    int status_code;
    char body[512];
    int is_network_error;
} http_response_t;

/* Симуляція вихідного HTTP POST запиту до зовнішнього API */
static http_response_t mock_http_post(const char *url, const char *idempotency_key, const char *payload, int attempt) {
    http_response_t res;
    memset(&res, 0, sizeof(res));

    /* Симуляція таймауту мережі на 1-й спробі, 409 Conflict на 2-й і 200 OK на 3-й */
    if (attempt == 1) {
        res.is_network_error = 1; /* Таймаут / ECONNRESET */
        res.status_code = 0;
    } else if (attempt == 2) {
        res.status_code = 409;   /* In-flight conflict */
        snprintf(res.body, sizeof(res.body), "{\"error\": \"in_flight\"}");
    } else {
        res.status_code = 200;
        snprintf(res.body, sizeof(res.body), "{\"status\": \"charged\", \"id\": \"ch_1092\"}");
    }
    return res;
}

int send_outbound_charge(const char *order_id, double amount, int max_retries) {
    char idempotency_key[128];
    snprintf(idempotency_key, sizeof(idempotency_key), "charge_order_%s_v1", order_id);

    char payload[256];
    snprintf(payload, sizeof(payload), "{\"order_id\":\"%s\",\"amount\":%.2f}", order_id, amount);

    int backoff_sec = 1;
    for (int attempt = 1; attempt <= max_retries; attempt++) {
        printf("[OUTBOUND C] Спроба %d/%d з Idempotency-Key: %s\n", attempt, max_retries, idempotency_key);
        
        http_response_t res = mock_http_post("https://api.stripe.com/v1/charges", idempotency_key, payload, attempt);

        if (res.is_network_error || res.status_code >= 500) {
            printf("[WARN C] Мережева помилка або 5xx (%d). Чекаємо %d с...\n", res.status_code, backoff_sec);
            sleep(backoff_sec);
            backoff_sec *= 2;
            continue;
        }

        if (res.status_code == 409) {
            printf("[WARN C] 409 Conflict (операція виконується). Чекаємо %d с...\n", backoff_sec);
            sleep(backoff_sec);
            continue;
        }

        if (res.status_code == 200 || res.status_code == 201) {
            printf("[SUCCESS C] Успішно виконано: %s\n", res.body);
            return 0; /* Успіх */
        }

        printf("[FATAL C] Незворотна помилка %d: %s\n", res.status_code, res.body);
        return -1;
    }

    printf("[ERROR C] Вичерпано ліміт спроб для замовлення %s\n", order_id);
    return -2;
}
```
```cpp
// C++20: Ідіоматичний вихідний шлюз з RAII, std::string_view та std::expected
#include <iostream>
#include <string>
#include <string_view>
#include <expected>
#include <thread>
#include <chrono>
#include <format>

struct HttpResponse {
    int status_code{0};
    std::string body;
    bool is_network_error{false};
};

enum class GatewayError {
    NetworkTimeout,
    PayloadMismatch,
    FatalClientError,
    RetriesExhausted
};

class OutboundPaymentGateway {
public:
    explicit OutboundPaymentGateway(std::string api_url) : api_url_(std::move(api_url)) {}

    std::expected<HttpResponse, GatewayError> execute_charge(
        std::string_view order_id, double amount, int max_retries = 3
    ) {
        const std::string idempotency_key = std::format("charge_order_{}_v1", order_id);
        const std::string payload = std::format(R"({{"order_id":"{}","amount":{:.2f}}})", order_id, amount);

        std::chrono::seconds backoff{1};

        for (int attempt = 1; attempt <= max_retries; ++attempt) {
            std::cout << std::format("[OUTBOUND C++] Спроба {}/{} | Key: {}\n", attempt, max_retries, idempotency_key);
            
            auto res = mock_http_post(idempotency_key, payload, attempt);

            if (res.is_network_error || res.status_code >= 500) {
                std::cout << std::format("[WARN C++] Таймаут/5xx ({}). Пауза {}s\n", res.status_code, backoff.count());
                std::this_thread::sleep_for(backoff);
                backoff *= 2;
                continue;
            }

            if (res.status_code == 409) {
                std::cout << std::format("[WARN C++] 409 Conflict. Пауза {}s\n", backoff.count());
                std::this_thread::sleep_for(backoff);
                continue;
            }

            if (res.status_code == 200 || res.status_code == 201) {
                return res;
            }

            if (res.status_code == 422) {
                return std::unexpected(GatewayError::PayloadMismatch);
            }

            return std::unexpected(GatewayError::FatalClientError);
        }

        return std::unexpected(GatewayError::RetriesExhausted);
    }

private:
    std::string api_url_;

    HttpResponse mock_http_post(std::string_view key, std::string_view payload, int attempt) {
        if (attempt == 1) return HttpResponse{.status_code = 0, .body = "", .is_network_error = true};
        if (attempt == 2) return HttpResponse{.status_code = 409, .body = R"({"error":"in_flight"})"};
        return HttpResponse{.status_code = 200, .body = R"({"status":"charged","id":"ch_1092"})"};
    }
};
```
```ts
// TypeScript: Асинхронний вихідний шлюз з fetch та AbortController
interface ChargeResult {
  id: string;
  status: string;
}

export class OutboundIdempotentClient {
  constructor(private readonly baseUrl: string) {}

  async postWithIdempotency<T>(
    path: string,
    idempotencyKey: string,
    body: Record<string, unknown>,
    maxRetries = 3
  ): Promise<T> {
    let backoffMs = 500;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      try {
        const response = await fetch(`${this.baseUrl}${path}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Idempotency-Key": idempotencyKey,
          },
          body: JSON.stringify(body),
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (response.ok) {
          return (await response.json()) as T;
        }

        if (response.status === 409 || response.status >= 500) {
          console.warn(`[RETRY TS] HTTP ${response.status}. Retrying in ${backoffMs}ms...`);
          await new Promise((resolve) => setTimeout(resolve, backoffMs));
          backoffMs *= 2;
          continue;
        }

        throw new Error(`Non-retriable error HTTP ${response.status}`);
      } catch (err: unknown) {
        clearTimeout(timeoutId);
        console.warn(`[NETWORK_ERROR TS] Attempt ${attempt} failed:`, err);
        if (attempt === maxRetries) throw err;
        await new Promise((resolve) => setTimeout(resolve, backoffMs));
        backoffMs *= 2;
      }
    }

    throw new Error("Max retries exceeded");
  }
}
```
```py
# Python: Надійний вихідний HTTP-клієнт з детермінованим Idempotency-Key
import time
import hashlib
import requests

class OutboundGateway:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def make_deterministic_key(self, entity_id: str, action: str) -> str:
        raw = f"{entity_id}:{action}".encode("utf-8")
        return f"idemp_{hashlib.sha256(raw).hexdigest()[:24]}"

    def post_charge(self, order_id: str, amount: float, max_retries: int = 3) -> dict:
        key = self.make_deterministic_key(order_id, "charge")
        payload = {"order_id": order_id, "amount": amount}
        headers = {"Idempotency-Key": key, "Content-Type": "application/json"}

        backoff = 1.0
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(
                    f"{self.base_url}/v1/charges",
                    json=payload,
                    headers=headers,
                    timeout=5.0
                )
                if response.status_code in (200, 201):
                    return response.json()
                elif response.status_code in (409, 502, 503, 504):
                    time.sleep(backoff)
                    backoff *= 2.0
                    continue
                else:
                    response.raise_for_status()
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                if attempt == max_retries:
                    raise
                time.sleep(backoff)
                backoff *= 2.0

        raise TimeoutError(f"Exhausted retries for order {order_id}")
```
```go
// Go: Вихідний HTTP-клієнт з context та exponential backoff
package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type Gateway struct {
	Client *http.Client
	URL    string
}

func (g *Gateway) ChargeOrder(ctx context.Context, orderID string, amount float64) error {
	idempotencyKey := fmt.Sprintf("charge_%s_v1", orderID)
	payload, _ := json.Marshal(map[string]any{"order_id": orderID, "amount": amount})

	backoff := 500 * time.Millisecond

	for attempt := 1; attempt <= 3; attempt++ {
		reqCtx, cancel := context.WithTimeout(ctx, 3*time.Second)
		req, _ := http.NewRequestWithContext(reqCtx, "POST", g.URL+"/v1/charges", bytes.NewBuffer(payload))
		req.Header.Set("Idempotency-Key", idempotencyKey)
		req.Header.Set("Content-Type", "application/json")

		resp, err := g.Client.Do(req)
		cancel()

		if err != nil || (resp != nil && resp.StatusCode >= 500) || (resp != nil && resp.StatusCode == 409) {
			time.Sleep(backoff)
			backoff *= 2
			continue
		}
		defer resp.Body.Close()

		if resp.StatusCode == 200 || resp.StatusCode == 201 {
			fmt.Printf("[SUCCESS Go] Платіж успішно проведено з ключем %s\n", idempotencyKey)
			return nil
		}

		return fmt.Errorf("фатальна помилка HTTP %d", resp.StatusCode)
	}

	return fmt.Errorf("перевищено кількість спроб")
}
```
:::

---

## Порівняльний аналіз реалізацій мовами системного та високорівневого програмування

### 1. Реалізація мовою C: Низькорівневий контроль та управління пам'яттю
У C-реалізації вихідного шлюзу ключовим є суворий контроль буферів та статичне виділення пам'яті за допомогою `snprintf`. Функція `send_outbound_charge` використовує формований стек буферів `idempotency_key` та `payload`. Виклик `sleep(backoff_sec)` використовується для найпростішої затримки повтору. В умовах реального системного програмування (наприклад, для вбудованих контролерів хабів Digital Homes) замість `sleep` використовується таймер `select` або `epoll`, що дозволяє не блокувати операційний цикл. 

Важливим моментом у C є перевірка коду повернення: `0` вказує на успіх, від'ємні значення (`-1`, `-2`) розрізняють фатальну помилку домену від вичерпання спроб мережі.

### 2. Реалізація мовою C++20: RAII та безерогійна семантика з `std::expected`
У реалізації C++20 ми використовуємо сучасні стандарти мови. Замість винятків або C-подібних кодів помилок застосовується тип `std::expected<HttpResponse, GatewayError>`, що з'явився в C++23 (або виражається через `std::variant` у C++20). Це гарантує, що клієнтський код на етапі компіляції змушений обробити всі варіанти помилок шлюзу (`NetworkTimeout`, `PayloadMismatch`, `FatalClientError`).

Управління ресурсами виконується за принципом RAII (Resource Acquisition Is Initialization). Рядки й заголовки обертаються в `std::string_view` та `std::format`, що повністю виключає ризик витоку пам'яті чи переповнення буфера. Для затримок використовується стандартна бібліотека `std::this_thread::sleep_for(backoff)`.

### 3. Реалізація мовою TypeScript: Асинхронні проміси та AbortController
У TypeScript реалізації вихідний шлюз побудований довкола стандартного API `fetch` та об'єкта `AbortController`. Оскільки в мережевому середовищі Node.js або браузера блоки розриву зв'язку можуть зависати на невизначений термін, кожна спроба ретраю створює свій `AbortController` із таймером `setTimeout(() => controller.abort(), 5000)`. Це гарантує, що якщо сокет «повис» на рівні ОС, шлюз примусово обірве спробу через 5 секунд і почне наступну спробу з тим самим ключем.

### 4. Реалізація мовою Python: Семантика обробки винятків та детермінований хеш
У Python шлюз спирається на бібліотеку `requests` (або асинхронний аналог `httpx`). Для генерації ключа використовується модуль `hashlib`, що обчислює `SHA-256` хеш від комбінації `order_id:action`. Це показує приклад стратегії детермінованого обчислення ключів, коли унікального бізнес-рядка недостатньо. Обробка мережевих таймаутів перехоплює базові винятки `requests.exceptions.Timeout` та `requests.exceptions.ConnectionError`.

### 5. Реалізація мовою Go: Контексти скасування та таймери
У мові Go вихідний шлюз будується з використанням пакету `context`. Кожен вихідний виклик створює короткоживучий контекст `context.WithTimeout(ctx, 3*time.Second)`. Це дозволяє передавати сигнал скасування крізь усю ієрархію викликів (наприклад, якщо користувач скасував HTTP-запит на веб-фронтенді, контекст скасується, і воркер припинить непотрібні ретраї). Використання `http.NewRequestWithContext` гарантує правильне закриття мережевих сокетів та вивільнення ресурсів через `defer resp.Body.Close()`.

---

## Тестування та верифікація вихідного шлюзу

Для верифікації коректності роботи вихідного ідемпотентного шлюзу застосовують такі види тестування:

1. **Хаос-тестування мережі (Network Chaos / Connection Injection)**:
   За допомогою інструментів `toxiproxy` або `iptables` у мережевий канал між шлюзом та емулятором API впорскуються таймаути, скидання TCP-пакетів (`ECONNRESET`) та затримки на 10 секунд. Верифікується, що шлюз робить повторні спроби strictly з тим самим `Idempotency-Key`.

2. **Перевірка унікальності на емуляторі (Mountebank / WireMock)**:
   Емулятор стороннього API конфігурується так, щоб повертати `504 Timeout` на перші дві спроби та `200 OK` на третю. Верифікується, що лічильник оброблених транзакцій на боці емулятора дорівнює **1**, а кількість отриманих HTTP-запитів дорівнює **3** (усі з однаковим заголовком `Idempotency-Key`).
