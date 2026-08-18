# ⚙️ Інструментування SLI, правила PromQL та автоматичний замок релізів

Ця практична вставка містить покроковий інженерний керівник із побудови повного конвеєра спостережності для індикаторів рівнів сервісів (SLI). Вставка покриває чотири ключові етапи: специфікацію вимірювання метрик у форматі OpenTelemetry Collector, обчислення швидкостей вигорання за допомогою правил запису й алертів Prometheus PromQL за багатовіконною схемою (Multi-Window Multi-Burn-Rate), конфігурацію маршутизації Alertmanager, а також реалізацію автономного сервісу-контролера вимикача релізів (Release Freeze Controller).

## 1. Специфікація метрик та інструментування OpenTelemetry

Першим етапом побудови надійної спостережності є збір базових первинних подій безпосередньо на швах системи. Для вимірювання доступності та латентності сервісу відчинення замків `dh-lock-service` застосовується стандартизований лічильник HTTP-запитів `http_server_request_duration_seconds`.

Кожен виклик інструментується трьома обов'язковими мітками (labels): `http_route` (конкретна кінцева точка API), `http_status_code` (код відповіді HTTP) та `le` (верхня межа бакета гістограми латентності в секундах).

Обробка телеметрії виконується агентом OpenTelemetry Collector. Процесор `transform` аналізує вхідні метрики у рантаймі та автоматично перевіряє, чи задовольняє подія критеріям вдосконалості: код відповіді має дорівнювати 200, а затримка обробки `duration_ms` не повинна перевищувати поріг у 500 мілісекунд (0.5 секунди). Якщо обидві умови виконані, процесор додає атрибут `sli_good = true`.

Використання OpenTelemetry Collector як проміжного буфера дозволяє відокремити кодову базу застосунку від конкретного сховища моніторингу. Якщо в майбутньому команда вирішить змінити Prometheus на Datadog, VictoriaMetrics чи Cortex, кодову базу сервісу відчинення замків не доведеться змінювати взагалі — достатньо буде оновити конфігурацію експортера в агенті. Крім того, це дозволяє виконувати семплінг та фільтрацію телеметрії без додаткових витрат на CPU в самому застосунку.

```yaml
# otel-collector-config.yaml — Конфігурація агента збору та трансформації метрик
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024

  transform:
    error_mode: ignore
    log_statements:
      - context: metric
        statements:
          # Маркування вдалих подій для dh-lock-service: HTTP 200 та latency <= 0.5s (500ms)
          - set(attributes["sli_good"], "true") where metric.name == "http.server.request.duration" and attributes["http.status_code"] == 200 and attributes["duration_ms"] <= 500

exporters:
  prometheus:
    endpoint: "0.0.0.0:8889"
    namespace: "dh"
    send_timestamps: true
    metric_expiration: 180s

service:
  pipelines:
    metrics:
      receivers: [otlp]
      processors: [batch, transform]
      exporters: [prometheus]
```

Завдяки такій конфігурації метрики надходять до Prometheus у вигляді стандартизованих серій даних, що дозволяє виконувати швидку агрегацію без додаткового навантаження на базу даних телеметрії.

## 2. Записи та алерти Prometheus PromQL (Multi-Window Multi-Burn-Rate)

Обчислення швидкостей вигорання (Burn Rates) безпосередньо під час виконання алерту на сирих бакетах гістограм створило б надмірне навантаження на сервер Prometheus при кожному ітераційному оцінюванні rules. Якщо на сервіс надходить 10 000 запитів на секунду, сира обробка бакетів за 6 годин вимагатиме читання мільйонів точок із TSDB кожні 15 секунд.

Тому процес розбивається на два рівні: правила запису (recording rules), які кешують проміжні частоти подій у часі, та правила сповіщень (alerting rules), які виконують швидкі логічні перевірки над готовими індексами.

Правила запису обчислюють чотири часові вікна: 5 хвилин, 30 хвилин, 1 годину та 6 годин. Для обчислення частоти невдалих запитів `job:http_requests_errors:rate` складаються дві категорії помилок: всі запити з HTTP-кодами, відмінними від 200, а також запити із кодом 200, чия латентність перевищила 0.5 секунди. Кількість повільних запитів визначається через математичне віднімання бакета `le="0.5"` від загальної кількості запитів `le="+Inf"`.

Після цього формуються відносні показники `job:slo_burn_rate:ratio`, які ділять фактичну частку помилок на номінальний бюджет `0.001` (що відповідає цільовому SLO 99.9%). Значення `ratio = 1.0` означає нормальне вигорання, `ratio = 14.4` означає критичне прискорення вигорання у 14.4 раза.

```yaml
# prometheus-slo-rules.yaml — Правила запису та алертингу для dh-lock-service
groups:
  - name: dh_lock_service_slo_recording
    interval: 30s
    rules:
      # Загальна частота запитів (Total Events Rate) за 5 хвилин, 30 хвилин, 1 годину, 6 годин
      - record: job:http_requests_total:rate5m
        expr: sum(rate(dh_http_server_request_duration_seconds_count{job="dh-lock-service", http_route="/v1/lock/unlock"}[5m]))
      
      - record: job:http_requests_total:rate30m
        expr: sum(rate(dh_http_server_request_duration_seconds_count{job="dh-lock-service", http_route="/v1/lock/unlock"}[30m]))

      - record: job:http_requests_total:rate1h
        expr: sum(rate(dh_http_server_request_duration_seconds_count{job="dh-lock-service", http_route="/v1/lock/unlock"}[1h]))

      - record: job:http_requests_total:rate6h
        expr: sum(rate(dh_http_server_request_duration_seconds_count{job="dh-lock-service", http_route="/v1/lock/unlock"}[6h]))

      # Частота помилок (Bad Events Rate: HTTP != 200 OR duration > 0.5s)
      - record: job:http_requests_errors:rate5m
        expr: |
          sum(rate(dh_http_server_request_duration_seconds_count{job="dh-lock-service", http_route="/v1/lock/unlock", http_status_code!="200"}[5m]))
          +
          sum(rate(dh_http_server_request_duration_seconds_bucket{job="dh-lock-service", http_route="/v1/lock/unlock", http_status_code="200", le="+Inf"}[5m]))
          -
          sum(rate(dh_http_server_request_duration_seconds_bucket{job="dh-lock-service", http_route="/v1/lock/unlock", http_status_code="200", le="0.5"}[5m]))

      - record: job:http_requests_errors:rate30m
        expr: |
          sum(rate(dh_http_server_request_duration_seconds_count{job="dh-lock-service", http_route="/v1/lock/unlock", http_status_code!="200"}[30m]))
          +
          sum(rate(dh_http_server_request_duration_seconds_bucket{job="dh-lock-service", http_route="/v1/lock/unlock", http_status_code="200", le="+Inf"}[30m]))
          -
          sum(rate(dh_http_server_request_duration_seconds_bucket{job="dh-lock-service", http_route="/v1/lock/unlock", http_status_code="200", le="0.5"}[30m]))

      - record: job:http_requests_errors:rate1h
        expr: |
          sum(rate(dh_http_server_request_duration_seconds_count{job="dh-lock-service", http_route="/v1/lock/unlock", http_status_code!="200"}[1h]))
          +
          sum(rate(dh_http_server_request_duration_seconds_bucket{job="dh-lock-service", http_route="/v1/lock/unlock", http_status_code="200", le="+Inf"}[1h]))
          -
          sum(rate(dh_http_server_request_duration_seconds_bucket{job="dh-lock-service", http_route="/v1/lock/unlock", http_status_code="200", le="0.5"}[1h]))

      - record: job:http_requests_errors:rate6h
        expr: |
          sum(rate(dh_http_server_request_duration_seconds_count{job="dh-lock-service", http_route="/v1/lock/unlock", http_status_code!="200"}[6h]))
          +
          sum(rate(dh_http_server_request_duration_seconds_bucket{job="dh-lock-service", http_route="/v1/lock/unlock", http_status_code="200", le="+Inf"}[6h]))
          -
          sum(rate(dh_http_server_request_duration_seconds_bucket{job="dh-lock-service", http_route="/v1/lock/unlock", http_status_code="200", le="0.5"}[6h]))

      # Обчислення поточного Burn Rate відносно SLO = 99.9% (Error Budget = 0.001)
      - record: job:slo_burn_rate:ratio5m
        expr: (job:http_requests_errors:rate5m / job:http_requests_total:rate5m) / 0.001

      - record: job:slo_burn_rate:ratio30m
        expr: (job:slo_burn_rate:ratio30m = (job:http_requests_errors:rate30m / job:http_requests_total:rate30m) / 0.001)

      - record: job:slo_burn_rate:ratio1h
        expr: (job:slo_burn_rate:ratio1h = (job:http_requests_errors:rate1h / job:http_requests_total:rate1h) / 0.001)

      - record: job:slo_burn_rate:ratio6h
        expr: (job:slo_burn_rate:ratio6h = (job:http_requests_errors:rate6h / job:http_requests_total:rate6h) / 0.001)

  - name: dh_lock_service_slo_alerts
    rules:
      # Критичний алерт 14.4x (2% бюджету за годину + триває останні 5 хвилин)
      - alert: DHLockServiceSLOCriticalBurnRate
        expr: (job:slo_burn_rate:ratio1h > 14.4) and (job:slo_burn_rate:ratio5m > 14.4)
        for: 2m
        labels:
          severity: critical
          tier: p1
          receiver: pagerduty
        annotations:
          summary: "Критична швидкість спалювання бюджету помилок dh-lock-service (Burn Rate 14.4x)"
          description: "Сервіс замків витрачає 2% бюджету помилок за годину. За 50 годин бюджет буде вичерпано повністю."

      # Попереджувальний алерт 6.0x (5% бюджету за 6 годин + триває останні 30 хвилин)
      - alert: DHLockServiceSLOWarningBurnRate
        expr: (job:slo_burn_rate:ratio6h > 6.0) and (job:slo_burn_rate:ratio30m > 6.0)
        for: 15m
        labels:
          severity: warning
          tier: p2
          receiver: slack_tickets
        annotations:
          summary: "Попереджувальне спалювання бюджету помилок dh-lock-service (Burn Rate 6.0x)"
          description: "Сервіс замків витрачає 5% бюджету помилок за 6 годин. Створено тикет для чергової зміни."
```

Правила сповіщень застосовують кон'юнкцію `and` між довгим і коротким вікнами. Алерт `DHLockServiceSLOCriticalBurnRate` спрацьовує лише у разі, коли Burn Rate за годину перевищує 14.4x **і одночасно** Burn Rate за останні 5 хвилин також перевищує 14.4x. Це повністю виключає ненавмисні дзвінки черговим після виправлення аварій, коли збій вже вщух, але довге вікно ще зберігає пам'ять про нього.

## 3. Конфігурація маршрутизації Alertmanager

Отримані від Prometheus сповіщення надходять до компонента Alertmanager, який відповідає за групування, пригнічення (inhibition) та маршрутизацію до відповідних каналів зв'язку (PagerDuty, Opsgenie, Slack або Webhook).

Нижче наведено конфігурацію маршрутизації Alertmanager:

```yaml
# alertmanager-config.yaml — Правила маршрутизації та пригнічення сповіщень
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 1m
  repeat_interval: 4h
  receiver: 'default-slack'
  routes:
    - match:
        severity: critical
        receiver: 'pagerduty-oncall'
      continue: false

    - match:
        severity: warning
        receiver: 'slack-tickets'
      continue: false

inhibit_rules:
  # Пригнічувати алерти SLO для мікросервісу, якщо впала базова мережа кластера
  - source_match:
      alertname: 'NetworkDataCenterDown'
    target_match_re:
      alertname: '.*SLO.*'
    equal: ['cluster']

receivers:
  - name: 'default-slack'
    slack_configs:
      - channel: '#alerts-general'

  - name: 'pagerduty-oncall'
    pagerduty_configs:
      - service_key: 'YOUR-PAGERDUTY-SERVICE-KEY'
        severity: 'critical'

  - name: 'slack-tickets'
    slack_configs:
      - channel: '#alerts-dh-team'
```

Завдяки пригніченню (`inhibit_rules`), якщо в дата-центрі сталася масштабна мережева аварія (`NetworkDataCenterDown`), сповіщення від дев'яти окремих сервісів про вигорання SLO автоматично блокуються. Інженер бачить тільки один кореневий алерт, що захищає від сліпоти при аварійному штормі сповіщень.

## 4. Сервіс-контролер вимикача релізів (Release Freeze Controller)

Щоб перетворити Error Budget Policy з паперової домовленості на авто-виконувану систему, розгортається автономний фоновий сервіс-контролер. Контролер періодично виконує HTTP-запити до Prometheus HTTP API, обчислює підсумкову суму всіх помилок та загальну кількість запитів за останні 30 днів (2 592 000 секунд), і розраховує залишок бюджету помилок у відсотках.

Якщо залишок бюджету стає меншим або дорівнює 0% (`Budget <= 0.0`), контролер взаємодіє з API кластера Kubernetes і патчить ресурс `ConfigMap` з назвою `dh-release-policy` у просторі імен `dh-system`, встановлюючи значення `RELEASE_FREEZE_ENABLED = "true"`. 

Конвеєри автоматичного випуску коду (GitHub Actions, ArgoCD або GitLab CI) перевіряють цей прапорець перед початком фази стабілізації деплою. Якщо прапорець активний, конвеєр перериває виконання з помилкою `Release Frozen due to Error Budget Exhaustion`, запобігаючи деплою будь-яких нових функціональних релізів.

При відновленні бюджету (наприклад, після виходу згорілого 30-денного інтервалу або внесення виправлень) контролер автоматично скидає прапорець у `false`, поновлюючи нормальний цикл розробки та автоматичних випусків без втручання системних адміністраторів.

Для функціонування контролера в кластері Kubernetes створюється обліковий запис `ServiceAccount` із прив'язкою `Role` та `RoleBinding`, яка надає право читання й модифікації ресурсів `ConfigMap` у просторі імен `dh-system`.

Нижче наведено еквівалентні реалізації контролера мовами Python та Go у вигляді двох сумісних вкладок. Реалізація мовою Python зручна для швидкого деплою у вигляді скриптів або серверлесс-функцій, тоді як Go-версія забезпечує мінімальне використання пам'яті (до 15 МБ) та бінарну автономність без зовнішніх залежностей у рантаймі.

:::tabs
```python
# controller.py — Python-реалізація контролера заморозки релізів
import os
import time
import requests
from kubernetes import client, config

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus-k8s.monitoring:9090")
SLO_TARGET = 0.999  # 99.9%
WINDOW_SECONDS = 30 * 24 * 3600  # 30 днів
CONFIGMAP_NAME = "dh-release-policy"
NAMESPACE = "dh-system"

def query_prometheus(query: str) -> float:
    response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query}, timeout=10)
    response.raise_for_status()
    data = response.json()
    result = data.get("data", {}).get("result", [])
    if not result:
        return 0.0
    return float(result[0]["value"][1])

def calculate_remaining_budget() -> float:
    # Запит кількості невдалих запитів за 30 днів
    query_errors = f'sum(increase(dh_http_server_request_duration_seconds_count{{job="dh-lock-service", http_status_code!="200"}}[{WINDOW_SECONDS}s]))'
    query_total = f'sum(increase(dh_http_server_request_duration_seconds_count{{job="dh-lock-service"}}[{WINDOW_SECONDS}s]))'
    
    total_requests = query_prometheus(query_total)
    if total_requests == 0:
        return 100.0  # Немає трафіку — бюджет повний
        
    error_requests = query_prometheus(query_errors)
    current_sli = (total_requests - error_requests) / total_requests
    allowed_errors = total_requests * (1.0 - SLO_TARGET)
    
    remaining_budget_percent = ((allowed_errors - error_requests) / allowed_errors) * 100.0
    print(f"SLI: {current_sli:.5f} | Total: {total_requests} | Errors: {error_requests} | Budget Remaining: {remaining_budget_percent:.2f}%")
    return remaining_budget_percent

def update_k8s_freeze_policy(freeze: bool):
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()
        
    v1 = client.CoreV1Api()
    cm = v1.read_namespaced_config_map(name=CONFIGMAP_NAME, namespace=NAMESPACE)
    current_val = cm.data.get("RELEASE_FREEZE_ENABLED", "false")
    new_val = "true" if freeze else "false"
    
    if current_val != new_val:
        cm.data["RELEASE_FREEZE_ENABLED"] = new_val
        v1.patch_namespaced_config_map(name=CONFIGMAP_NAME, namespace=NAMESPACE, body=cm)
        print(f"ПОЛІТИКУ ЗМІНЕНО: RELEASE_FREEZE_ENABLED = {new_val}")

def main():
    while True:
        try:
            budget = calculate_remaining_budget()
            if budget <= 0.0:
                print("УВАГА: Бюджет помилок вичерпано! Активація Freeze Policy.")
                update_k8s_freeze_policy(freeze=True)
            else:
                update_k8s_freeze_policy(freeze=False)
        except Exception as e:
            print(f"Помилка виконання контролера: {e}")
        time.sleep(60)

if __name__ == "__main__":
    main()
```
```go
// controller.go — Go-реалізація контролера заморозки релізів
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"time"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
)

const (
	sloTarget      = 0.999
	windowSeconds  = 30 * 24 * 3600
	configMapName  = "dh-release-policy"
	namespace      = "dh-system"
)

type PromResponse struct {
	Data struct {
		Result []struct {
			Value []interface{} `json:"value"`
		} `json:"result"`
	} `json:"data"`
}

func queryPrometheus(promURL, query string) (float64, error) {
	u := fmt.Sprintf("%s/api/v1/query?query=%s", promURL, url.QueryEscape(query))
	resp, err := http.Get(u)
	if err != nil {
		return 0, err
	}
	defer resp.Body.Close()

	var pr PromResponse
	if err := json.NewDecoder(resp.Body).Decode(&pr); err != nil {
		return 0, err
	}
	if len(pr.Data.Result) == 0 || len(pr.Data.Result[0].Value) < 2 {
		return 0, nil
	}
	strVal, ok := pr.Data.Result[0].Value[1].(string)
	if !ok {
		return 0, fmt.Errorf("invalid value format")
	}
	return strconv.ParseFloat(strVal, 64)
}

func main() {
	promURL := os.Getenv("PROMETHEUS_URL")
	if promURL == "" {
		promURL = "http://prometheus-k8s.monitoring:9090"
	}

	config, err := rest.InClusterConfig()
	if err != nil {
		config, err = clientcmd.BuildConfigFromFlags("", os.Getenv("KUBECONFIG"))
		if err != nil {
			log.Fatalf("Error loading kubeconfig: %v", err)
		}
	}
	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		log.Fatalf("Error creating k8s client: %v", err)
	}

	for {
		qTotal := fmt.Sprintf(`sum(increase(dh_http_server_request_duration_seconds_count{job="dh-lock-service"}[%ds]))`, windowSeconds)
		qErrors := fmt.Sprintf(`sum(increase(dh_http_server_request_duration_seconds_count{job="dh-lock-service", http_status_code!="200"}[%ds]))`, windowSeconds)

		total, err := queryPrometheus(promURL, qTotal)
		if err != nil {
			log.Printf("Error querying total: %v", err)
			time.Sleep(60 * time.Second)
			continue
		}
		if total == 0 {
			time.Sleep(60 * time.Second)
			continue
		}

		errors, err := queryPrometheus(promURL, qErrors)
		if err != nil {
			log.Printf("Error querying errors: %v", err)
			time.Sleep(60 * time.Second)
			continue
		}

		allowedErrors := total * (1.0 - sloTarget)
		remainingBudget := ((allowedErrors - errors) / allowedErrors) * 100.0
		freeze := remainingBudget <= 0.0

		log.Printf("SLI Checked | Remaining Budget: %.2f%% | Freeze Needed: %v", remainingBudget, freeze)

		ctx := context.Background()
		cm, err := clientset.CoreV1().ConfigMaps(namespace).Get(ctx, configMapName, metav1.GetOptions{})
		if err == nil {
			currentVal := cm.Data["RELEASE_FREEZE_ENABLED"]
			newVal := "false"
			if freeze {
				newVal = "true"
			}
			if currentVal != newVal {
				cm.Data["RELEASE_FREEZE_ENABLED"] = newVal
				_, err = clientset.CoreV1().ConfigMaps(namespace).Update(ctx, cm, metav1.UpdateOptions{})
				if err != nil {
					log.Printf("Error updating ConfigMap: %v", err)
				} else {
					log.Printf("ConfigMap updated: RELEASE_FREEZE_ENABLED = %s", newVal)
				}
			}
		}
		time.Sleep(60 * time.Second)
	}
}
```
:::

Обидві реалізації забезпечують автоматичне, безперервне та детерміноване керування політикою випуску релізів. Завдяки цьому зникає потреба в тривалих усних переговорах між розробкою та операційними інженерами: якщо залишок бюджету опускається нижче нуля, система сама захищає себе від подальшої деструктивної дестабілізації.
