# ⚙️ Автоматизований канареєчний пайплайн з аналізом метрик та автовідкатом

Пайплайн безперервної доставки не має права покладатися на інтуїцію інженера чи візуальний огляд дашборду після деплою. Коли система Digital Homes обслуговує сотні тисяч активних пристроїв, людина просто не здатна вчасно помітити приховане витікання пам'яті у 99-му перцентилі затримки або поступове зростання відсотка втрачених подій телеметрії за п'ятнадцять хвилин спостереження. Безпечна доставка вимагає **автоматизованого оркестратора канарки**, який самостійно керує частками трафіку, зчитує метрики з Prometheus, обчислює підсумковий бал здоров'я (Canary Score) та у разі виявлення аномалії здійснює миттєвий відкат.

Нижче наведено повністю робочий контролер канареєчного розгортання для бекенду Digital Homes. Він інтегрується між вхідним шлюзом (Envoy) та системою моніторингу, реалізуючи порівняльний аналіз метрик і прогресивне підвищення навантаження.

## Архітектура канареєчного контролера

Оркестратор працює як автономний агент усередині кластера Kubernetes або оркестратора розгортання. Його завдання — виконувати контрольний цикл (reconciliation loop), на кожній ітерації якого стан канаркового розгортання порівнюється з поточними метриками телеметрії.

Сервіс взаємодіє з двома зовнішніми системами:
- **Вхідний маршрутизатор (Envoy Ingress / API Gateway)**: через REST API або gRPC xDS контролер змінює вагові коефіцієнти маршрутів між базовим кластером (`dh-backend-baseline`) та канарковим кластером (`dh-backend-canary`).
- **Сервер моніторингу (Prometheus / Thanos)**: через HTTP API `/api/v1/query` контролер щохвилини виконує серію PromQL-запитів для паралельного збору показників з обох кластерів.

Контролер реалізує кінцевий автомат (State Machine), який може перебувати в одному з п'яти станів: `INIT` (ініціалізація нод), `SOAKING` (витримка під трафіком), `EVALUATING` (обчислення оцінки здоров'я), `PROMOTING` (перехід на наступну фазу) або `ROLLING_BACK` (аварійний відкат у 0%).

## Детальний розбір PromQL запитів та метрик

Для чесного порівняння двох версій контролер зчитує метрики за рухоме вікно тривалістю п'ять хвилин (`[5m]`). Використання 5-хвилинного вікна у функції `rate()` дозволяє згладити короткочасні випадкові сплески трафіку й отримати стійке середнє значення.

### 1. Відносна частота помилок (Relative Error Delta)

Порівнювати абсолютну кількість помилок (наприклад, 100 помилок на канарці та 9900 на базі) неможливо, оскільки канарка отримує лише 1% трафіку. Тому контролер обчислює **відсоток помилок відносно загальної кількості запитів** для кожного кластера:

```
Rate_Error(Baseline) = sum(rate(http_requests_total{version="v1.4", status=~"5.."}[5m])) 
                       / (sum(rate(http_requests_total{version="v1.4"}[5m])) + 0.001)

Rate_Error(Canary)   = sum(rate(http_requests_total{version="v1.5", status=~"5.."}[5m])) 
                       / (sum(rate(http_requests_total{version="v1.5"}[5m])) + 0.001)
```

Маленька константа `0.001` додається до знаменника для запобігання діленню на нуль у разі відсутності трафіку. Якщо відносна частота помилок канарки `Rate_Error(Canary)` перевищує базову `Rate_Error(Baseline)` більше ніж на `0.005` (тобто на 0.5 процентного пункту), це сигналізує про виникнення критичного багу у новому коді.

### 2. Перцентилі затримки (p95 та p99 Latency)

Середня затримка (p50) часто приховує реальні проблеми користувачів. Наприклад, якщо 95% запитів відповідають за 10 мілісекунд, а 5% запитів блокуються на 5 секунд через некоректну роботу замків бази даних, середня затримка залишиться чудовою, проте 5% мешканців чекатимуть біля замків.

Тому контролер аналізує квантилі за допомогою функції `histogram_quantile`:

```
p95(Baseline) = histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{version="v1.4"}[5m])) by (le))
p95(Canary)   = histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{version="v1.5"}[5m])) by (le))
```

Контролер обчислює відношення `p95(Canary) / p95(Baseline)`. Якщо канарка показує уповільнення на 20% і більше (коефіцієнт > 1.20), це свідчить про наявність неоптимальних запитів чи конкурентних блокувань.

### 3. Специфічні IoT-метрики платформи Digital Homes

Для бекенду контролю розумних будинків класичних HTTP-метрик недостатньо. Контролер обов'язково аналізує доменну метрику повторних підключень хабів `dh_device_reconnects_total`.

Коли нова версія бекенду містить помилку в процедурі рукостискання (TLS/gRPC handshake), хаби починають розривати з'єднання і підключатися знову. Оскільки підключення є найважчою операцією для центрального процесора, сплеск метрики `reconnects` віщує швидке падіння всього кластера від шторму авторизацій.

## Програмна реалізація оркестратора

Нижче наведено повний вихідний код оркестратора канареєчного розгортання. Код містить реалізацію виконання запитів до Prometheus, керування ваговими коефіцієнтами маршрутизатора Envoy, обчислення підсумкового бала здоров'я та логіку автоматичного відкату.

:::tabs
```python
import time
import sys
import requests
from typing import Dict, Any

class CanaryOrchestrator:
    """Оркестратор канареєчного розгортання для бекенду Digital Homes."""

    def __init__(self, prometheus_url: str, gateway_admin_url: str):
        self.prometheus_url = prometheus_url
        self.gateway_admin_url = gateway_admin_url
        self.session = requests.Session()

    def query_scalar_metric(self, promql: str) -> float:
        """Виконує PromQL запит та повертає скалярне значення метрики.
        
        У разі відсутності даних або помилки мережі повертає 0.0.
        """
        try:
            response = self.session.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": promql},
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
            result = data.get("data", {}).get("result", [])
            if not result or "value" not in result[0]:
                return 0.0
            return float(result[0]["value"][1])
        except Exception as e:
            print(f"[WARN] Помилка виконання PromQL запиту '{promql}': {e}", file=sys.stderr)
            return 0.0

    def set_canary_weight(self, weight_percent: int) -> None:
        """Оновлює вагові коефіцієнти вхідного шлюзу Envoy.
        
        Розподіляє 100% трафіку між dh-backend-baseline та dh-backend-canary.
        """
        baseline_weight = 100 - weight_percent
        payload = {
            "routes": [
                {"cluster": "dh-backend-baseline", "weight": baseline_weight},
                {"cluster": "dh-backend-canary", "weight": weight_percent}
            ]
        }
        try:
            resp = self.session.post(
                f"{self.gateway_admin_url}/v1/routes/weight",
                json=payload,
                timeout=3.0
            )
            resp.raise_for_status()
            print(f"[ROUTER] Вагу трафіку оновлено: База={baseline_weight}%, Канарка={weight_percent}%")
        except Exception as e:
            print(f"[CRITICAL] Не вдалося оновити вагу трафіку в Envoy: {e}", file=sys.stderr)
            raise

    def evaluate_canary_health(self, step_duration_sec: int = 300) -> float:
        """Очікує час витримки та обчислює підсумкову оцінку здоров'я канарки."""
        print(f"[SOAK] Очікуємо час витримки (soak time): {step_duration_sec} секунд...")
        time.sleep(step_duration_sec)

        # 1. Відсоток помилок 5xx
        err_baseline = self.query_scalar_metric(
            'sum(rate(http_requests_total{job="dh-backend",version="v1.4",status=~"5.."}[5m])) '
            '/ (sum(rate(http_requests_total{job="dh-backend",version="v1.4"}[5m])) + 0.001)'
        )
        err_canary = self.query_scalar_metric(
            'sum(rate(http_requests_total{job="dh-backend",version="v1.5",status=~"5.."}[5m])) '
            '/ (sum(rate(http_requests_total{job="dh-backend",version="v1.5"}[5m])) + 0.001)'
        )

        # 2. Затримка 95-го перцентиля (p95 latency)
        p95_baseline = self.query_scalar_metric(
            'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="dh-backend",version="v1.4"}[5m])) by (le))'
        )
        p95_canary = self.query_scalar_metric(
            'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="dh-backend",version="v1.5"}[5m])) by (le))'
        )

        # 3. Частота перепідключень IoT-хабів
        reconn_baseline = self.query_scalar_metric('sum(rate(dh_device_reconnects_total{version="v1.4"}[5m]))')
        reconn_canary = self.query_scalar_metric('sum(rate(dh_device_reconnects_total{version="v1.5"}[5m]))')

        score = 100.0
        err_diff = err_canary - err_baseline

        print(f"[METRICS] Помилки: База={err_baseline:.4f}, Канарка={err_canary:.4f} (Δ={err_diff:.4f})")
        print(f"[METRICS] Затримка p95: База={p95_baseline:.3f}s, Канарка={p95_canary:.3f}s")
        print(f"[METRICS] Перепідключення: База={reconn_baseline:.2f}/s, Канарка={reconn_canary:.2f}/s")

        # Штраф за зростання помилок
        if err_diff > 0.005:
            print(f"[PENALTY] Зростання помилок на {err_diff*100:.2f}%! (-50 балів)")
            score -= 50.0

        # Штраф за деградацію затримки p95
        if p95_baseline > 0 and (p95_canary / p95_baseline) > 1.20:
            ratio = p95_canary / p95_baseline
            print(f"[PENALTY] Сповільнення p95 у {ratio:.2f} разів! (-30 балів)")
            score -= 30.0

        # Штраф за аномалію перепідключень хабів
        if reconn_baseline > 0 and (reconn_canary / reconn_baseline) > 1.50:
            ratio = reconn_canary / reconn_baseline
            print(f"[PENALTY] Спричинено шторм підключень хабів у {ratio:.2f} разів! (-40 балів)")
            score -= 40.0

        return max(0.0, score)

    def execute_progressive_rollout(self) -> bool:
        """Послідовний конвеєр розгортання: 1% -> 10% -> 50% -> 100%."""
        steps = [1, 10, 50, 100]
        for weight in steps:
            print(f"\n==========================================")
            print(f"[CANARY STEP] Початок фази: {weight}% трафіку")
            print(f"==========================================")
            
            self.set_canary_weight(weight)
            
            if weight == 100:
                print("[SUCCESS] Канарка успішно пройшла всі перевірки й стала базовою версією!")
                return True

            score = self.evaluate_canary_health(step_duration_sec=300)
            print(f"[EVALUATION] Підсумкова оцінка здоров'я: {score:.1f} / 100.0")

            if score < 75.0:
                print(f"[CRITICAL] Оцінка {score:.1f} нижча за поріг 75.0! Ініціація відкату!")
                self.rollback()
                return False

        return True

    def rollback(self) -> None:
        """Аварійне зняття трафіку з канарки та відновлення стабільного стану."""
        print("\n[ROLLBACK] Скидаємо трафік канарки в 0%! Усі запити ідуть на v1.4")
        try:
            self.set_canary_weight(0)
            print("[ROLLBACK] Відкат трафіку завершено успішно.")
        except Exception as e:
            print(f"[EMERGENCY] Не вдалося автоматично скинути трафік: {e}", file=sys.stderr)
```

```go
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"
)

type CanaryController struct {
	PrometheusURL   string
	GatewayAdminURL string
	Client          *http.Client
}

type PromResponse struct {
	Status string `json:"status"`
	Data   struct {
		Result []struct {
			Value []interface{} `json:"value"`
		} `json:"result"`
	} `json:"data"`
}

func NewCanaryController(promURL, gatewayURL string) *CanaryController {
	return &CanaryController{
		PrometheusURL:   promURL,
		GatewayAdminURL: gatewayURL,
		Client:          &http.Client{Timeout: 5 * time.Second},
	}
}

func (c *CanaryController) QueryScalarMetric(promql string) float64 {
	reqURL := fmt.Sprintf("%s/api/v1/query?query=%s", c.PrometheusURL, promql)
	resp, err := c.Client.Get(reqURL)
	if err != nil {
		fmt.Fprintf(os.Stderr, "[WARN] Помилка запиту Prometheus: %v\n", err)
		return 0.0
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var pResp PromResponse
	if err := json.Unmarshal(body, &pResp); err != nil {
		return 0.0
	}

	if len(pResp.Data.Result) == 0 || len(pResp.Data.Result[0].Value) < 2 {
		return 0.0
	}

	valStr, ok := pResp.Data.Result[0].Value[1].(string)
	if !ok {
		return 0.0
	}

	var val float64
	fmt.Sscanf(valStr, "%f", &val)
	return val
}

func (c *CanaryController) SetCanaryWeight(weight int) error {
	payload := map[string]interface{}{
		"routes": []map[string]interface{}{
			{"cluster": "dh-backend-baseline", "weight": 100 - weight},
			{"cluster": "dh-backend-canary", "weight": weight},
		},
	}
	data, _ := json.Marshal(payload)
	resp, err := c.Client.Post(c.GatewayAdminURL+"/v1/routes/weight", "application/json", bytes.NewBuffer(data))
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	fmt.Printf("[ROUTER] Встановлено вагу: База=%d%%, Канарка=%d%%\n", 100-weight, weight)
	return nil
}

func (c *CanaryController) EvaluateHealth() float64 {
	time.Sleep(5 * time.Minute)

	errBase := c.QueryScalarMetric("sum(rate(http_requests_total{version=\"v1.4\",status=~\"5..\"}[5m])) / (sum(rate(http_requests_total{version=\"v1.4\"}[5m])) + 0.001)")
	errCanary := c.QueryScalarMetric("sum(rate(http_requests_total{version=\"v1.5\",status=~\"5..\"}[5m])) / (sum(rate(http_requests_total{version=\"v1.5\"}[5m])) + 0.001)")

	p95Base := c.QueryScalarMetric("histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{version=\"v1.4\"}[5m])) by (le))")
	p95Canary := c.QueryScalarMetric("histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{version=\"v1.5\"}[5m])) by (le))")

	score := 100.0
	if errCanary-errBase > 0.005 {
		score -= 50.0
	}
	if p95Base > 0 && (p95Canary/p95Base) > 1.20 {
		score -= 30.0
	}
	return score
}

func (c *CanaryController) ExecuteRollout() bool {
	steps := []int{1, 10, 50, 100}
	for _, w := range steps {
		if err := c.SetCanaryWeight(w); err != nil {
			c.Rollback()
			return false
		}
		if w == 100 {
			return true
		}
		score := c.EvaluateHealth()
		if score < 75.0 {
			c.Rollback()
			return false
		}
	}
	return true
}

func (c *CanaryController) Rollback() {
	_ = c.SetCanaryWeight(0)
	fmt.Println("[ROLLBACK] Аварійне зняття трафіку завершено.")
}
```
:::

## Виробничі пастки та крайові випадки

Побудова автоматичного оркестратора канареєчного розгортання вимагає врахування низки критичних нюансів експлуатації під високим навантаженням.

### 1. Проблема низького обсягу вибірки в нічний час

Якщо розгортання виконується о 3-й годині ночі, загальний обсяг запитів на 1% канарки може становити всього 5–10 запитів за хвилину. За такої вибірки один випадковий таймаут через мережевий збій у провайдера дасть відсоток помилок у 10% або 20%, що викличе **хибнопозитивний відкат (False Positive Rollback)**.

Для запобігання цьому оркестратор має перевіряти мінімальний розмір вибірки. Якщо `sum(rate(http_requests_total[5m])) < 100`, аналіз заперечується, а фаза витримки продовжується до збору статистично значущої кількості даних.

### 2. Затримка збору метрик у Prometheus (Scraping Delay)

Prometheus збирає метрики з подів із фіксованим інтервалом (Scrape Interval, зазвичай 15 або 30 секунд). Після оновлення ваги в Envoy на 1% перші дані з'являться в Prometheus лише через 30–60 секунд.

Якщо оркестратор почне виконувати PromQL-запити одразу після виклику API Envoy, він зчитає порожні значення або застарілі метрики попередньої версії. Тому після зміни ваги трафіку контролер робить обов'язкову павзу в **60 секунд** (warmup pause) перед початком збору метрик для розрахунку `Canary Score`.

### 3. Тимчасовий відсіч зв'язку з системою моніторингу

Якщо під час аналізу канарки сам сервер Prometheus стає тимчасово недоступним через мережеве коливання чи перезапуск, функція `query_scalar_metric` не повинна повертати 0.0 і трактувати це як падіння канарки.

Контролер реалізує повторні спроби виклику API (Retries with Exponential Backoff). Лише у разі трьох послідовних невдалих спроб зв'язатися з моніторингом розгортання переходить у стан `PAUSED` і надсилає сповіщення дежурному інженеру, утримуючи поточну вагу трафіку без примусового відкату.

### 4. Вплив паралельних експериментів та Feature Flags

Якщо під час розгортання канарки `v1.5` продуктова команда паралельно вмикає новий прапорець функції (Feature Flag) для великої когорти користувачів, сплеск помилок може бути спричинений саме цим прапорцем, а не новим бінарним кодом.

Для ізоляції факторів контролер перевіряє аудит-лог змін конфігурації. Якщо під час фази канарки зафіксовано зміну прапорців функцій, аналіз призупиняється, а система вимагає завершення розгортання інфраструктури перед проведенням бізнес-експериментів.

### 5. Стратегії ротації тривалих TCP та gRPC з'єднань

Особливістю IoT-платформи Digital Homes є наявність сотень тисяч відкритих WebSocket та gRPC з'єднань, які тримаються годинами. Коли вхідний шлюз оновлює ваговий коефіцієнт канарки з 0% до 1%, це налаштування застосовується **виключно до нових вхідних TCP-з'єднань**. 

Якщо пристрої не перепідключаються, канарка не дістане реального навантаження, і фаза витримки (soak phase) пройде насамоті. Для забезпечення реативного навантаження на канарку застосовуються дві стратегії:
- **Active Connection Draining**: базові ноди `v1.4` після початку оновлення надсилають клієнтам м'який сигнал завершення сесії (`GOAWAY` у gRPC чи `1001 Going Away` у WebSocket) з випадковим джиттером від 0 до 60 секунд. Це спонукає хаби заново пройти балансувальник.
- **Max Connection TTL**: кожне з'єднання має вбудований максимальний час життя (наприклад, 1 годину). Після закінчення TTL з'єднання перевідкривається автоматично.

### 6. Захист від шторму авторизацій при відкаті (Thundering Herd Prevention)

Коли канарка падає і контролер скидає вагу в 0%, тисячі пристроїв, які встигли підключитися до канарки, одночасно отримують обрив з'єднання і намагаються підключитися до базового кластера. 

Якщо всі 5000 хабів ударять у базовий кластер в одну й ту саму мілісекунду, вони покладуть базовий кластер через сплеск TLS-рукостискань та навантаження на БД авторизації. Щоб уникнути цього, клієнтські бібліотеки IoT-пристроїв Digital Homes обов'язково застосовують алгоритм **експоненційного відступу з випадковим джиттером (Exponential Backoff with Full Jitter)**:

```
delay = random(0, min(max_backoff, base_backoff * (2 ^ attempt)))
```

Це розмазує хвилю підключень у часі й дозволяє базовому кластеру безболісно поглинути відкат.
