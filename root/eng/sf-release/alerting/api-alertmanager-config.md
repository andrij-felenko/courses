# 📋 Специфікація правил алертингу та конфігурації Alertmanager

Цей документ містить вичерпну технічну та структурну специфікацію форматів визначення правил алертингу в Prometheus, конфігурації конвеєра маршрутизації Alertmanager, правил інгібування, інтерфейсу HTTP API v2 та схеми JSON-контракту сповіщень webhook.

## 1. Специфікація файлу правил Prometheus (Prometheus Rule Schema)

Правила алертингу та запису (recording rules) визначаються у декларативних файлах формату YAML. Кожен файл містить одну або декілька іменованих груп правил. 

### Семантика обчислення груп правил
- **Послідовне виконання всередині групи:** Усі правила всередині однієї групи (`group`) обчислюються строго послідовно в порядку їхнього оголошення в файлі через фіксований часовий інтервал `interval`. Якщо обчислення одного складного виразу PromQL затримується, наступне правило тієї ж групи чекає завершення попереднього.
- **Паралельне виконання груп:** Окремі групи правил обчислюються в незалежних паралельних потоках (goroutines). Час виконання однієї групи не впливає на графік виконання інших.
- **Ізоляція часового зрізу:** Під час обчислення групи всі правила використовують єдину фіксовану часову мітку зрізу (evaluation timestamp), що гарантує узгодженість взаємопов'язаних виразів.

```yaml
groups:
  - name: <string>                     # Унікальне ім'я групи правил (обов'язкове)
    interval: <duration>               # Інтервал обчислення (за замовчуванням глобальний, наприклад 15s або 1m)
    limit: <int>                       # Максимальна кількість алертів, яку може згенерувати ця група (0 = без обмежень)
    rules:
      - alert: <string>                # Назва алерту (автоматично додається як мітка alertname=<name>)
        expr: <promql_expression>      # Векторний вираз PromQL, що повертає часові ряди з аномалією
        for: <duration>                # Тривалість утримання умови в стані PENDING перед переходом у FIRING (наприклад, 5m)
        keep_firing_for: <duration>    # Мінімальний час утримання стану FIRING після нормалізації метрики (захист від брязкання)
        labels:                        # Набір користувацьких статичних міток для маршрутизації
          severity: page | ticket | info
          team: <string>
          tier: <string>
          env: <string>
        annotations:                   # Інформаційні метадані для людей (підтримують синтаксис шаблонів Go text/template)
          summary: <string>
          description: <string>
          runbook_url: <url>
          dashboard_url: <url>
```

### Деталізація полів специфікації правила:

1. **`alert` (Ідентифікатор правила):**
   Рядок ASCII, що містить назву типу збою (наприклад, `HighErrorRate`, `DiskFillingFast`, `KubePodCrashLooping`). Автоматично записується в зарезервовану мітку `alertname`.

2. **`expr` (Логічний вираз PromQL):**
   Вираз векторного запиту PromQL. Якщо вираз повертає непорожній миттєвий вектор (instant vector), кожен знайдений часовий ряд ініціює створення окремого екземпляра алерту з відповідним набором міток часового ряду.
   - Заборонено використовувати вирази діапазону (range vectors, наприклад `http_requests_total[5m]`) безпосередньо як корінь виразу `expr`. Вони обов'язково повинні бути обгорнуті у векторну функцію агрегації (`rate()`, `increase()`, `avg_over_time()`).

3. **`for` (Фільтр затримки переходу):**
   Часовий інтервал (наприклад, `30s`, `5m`, `1h`). Якщо `for` задано, алерт при першому виявленні переходить у стан `Pending`. Лише якщо умова залишається істинною протягом усього інтервалу `for`, стан змінюється на `Firing`. Якщо `for: 0s` або поле відсутнє, алерт переходить у `Firing` негайно.

4. **`keep_firing_for` (Буфер згасання):**
   Додатковий інтервал стабілізації (введений у Prometheus 2.42+). Запобігає передчасному зняттю алерту при короткочасних просіданнях навантаження або мережевих розривах під час збору метрик.

5. **`labels` (Мітки маршрутизації):**
   Словник пар ключ-значення. Ці мітки об'єднуються з мітками вихідного часового ряду. Якщо виникає конфлікт імен міток, значення з блоку `labels` правила має пріоритет над мітками з метрики.

6. **`annotations` (Метадані інциденту):**
   Словник текстових полів, призначених для читання черговими інженерами. Значення полів інтерпретуються рушієм шаблонів Go (`text/template`) і мають доступ до таких змінних:
   - `$labels`: об'єкт, що містить усі мітки поточного екземпляра алерту (наприклад, `{{ $labels.instance }}`, `{{ $labels.namespace }}`).
   - `$value`: чисельне значення виразу PromQL у форматі float64 (наприклад, `{{ $value | humanizePercentage }}` або `{{ $value | humanize1024 }}`).
   - `$externalLabels`: глобальні мітки екземпляра сервера Prometheus.

## 2. Специфікація конфігурації Alertmanager (alertmanager.yml)

Конфігураційний файл Alertmanager описує глобальні параметри з'єднань, повне дерево маршрутизації, правила інгібування та налаштування приймачів сповіщень.

```yaml
global:
  resolve_timeout: 5m                  # Час, після якого алерт автоматично переходить у RESOLVED за відсутності оновлень
  http_config:
    idle_conn_timeout: 90s
  smtp_smarthost: 'smtp.internal.net:587'
  smtp_from: 'alertmanager@company.com'
  smtp_require_tls: true

# ── Кореневий маршрут (Root Route) ──────────────────────────────────────────
route:
  receiver: 'default-slack-catchall'   # Приймач за замовчуванням для незгрупованих сповіщень
  group_by: ['alertname', 'cluster', 'service'] # Ключі групування алертів у єдиний пакет
  group_wait: 30s                      # Пауза накопичення нових алертів у групі перед першою відправкою
  group_interval: 5m                   # Мінімальний інтервал між відправками оновлень для вже активної групи
  repeat_interval: 4h                  # Інтервал повторного нагадування про активний інцидент без змін стану

  # ── Дерево підмаршрутів (Sub-routes) ─────────────────────────────────────
  routes:
    # Гілка 1: Критичні аварії на продакшені -> Пейджер
    - matchers:
        - severity = "page"
        - env = "production"
      receiver: 'pagerduty-production-sre'
      group_wait: 10s
      group_interval: 2m
      repeat_interval: 1h
      continue: false                  # Зупинити пошук наступних маршрутів при збігу

    # Гілка 2: Некритичні попередження -> Автоматичне створення тікетів
    - matchers:
        - severity = "ticket"
      receiver: 'jira-service-desk'
      group_wait: 1m
      group_interval: 10m
      repeat_interval: 12h
      continue: false

    # Гілка 3: Командні канали за міткою сервісу
    - matchers:
        - service =~ "auth|billing|checkout"
      receiver: 'core-platform-slack'
      continue: true                   # Продовжити обхід дерева для доставки копії в інші канали

# ── Правила приглушення (Inhibition Rules) ──────────────────────────────────
inhibit_rules:
  - source_matchers:                   # Критерії активного батьківського алерту (джерело блокування)
      - alertname = "NodeNetworkDown"
      - severity = "page"
    target_matchers:                   # Дочірні алерти, які будуть приглушені
      - alertname =~ "InstanceDown|ServiceUnreachable|HighLatency"
    equal: ['cluster', 'node']         # Мітки, значення яких повинні строго збігатися

  - source_matchers:
      - alertname = "DatacenterPowerFailure"
    target_matchers:
      - severity =~ "page|ticket"
    equal: ['datacenter']

# ── Отримувачі та інтеграції (Receivers) ────────────────────────────────────
receivers:
  - name: 'pagerduty-production-sre'
    pagerduty_configs:
      - service_key: '<pagerduty_integration_key>'
        severity: 'critical'
        send_resolved: true
        client: 'Alertmanager Prod'
        client_url: 'https://alertmanager.internal.net'

  - name: 'default-slack-catchall'
    slack_configs:
      - channel: '#alerts-unrouted'
        api_url: 'https://hooks.slack.com/services/T00/B00/X00'
        send_resolved: true
        title: '{{ template "slack.default.title" . }}'
        text: '{{ template "slack.default.text" . }}'

  - name: 'jira-service-desk'
    webhook_configs:
      - url: 'https://jira-bridge.internal.net/api/v1/alerts'
        send_resolved: false
        max_alerts: 50
```

### Алгоритм маршрутизації в дереві маршрутів:
1. Кожен екземпляр алерту надходить у кореневий вузол `route`.
2. Alertmanager послідовно перевіряє масив `routes` зверху вниз.
3. Для кожного вузла перевіряються всі селектори `matchers`. Підтримуються 4 оператори зіставлення:
   - `=` : точний збіг рядка.
   - `!=`: нерівність рядка.
   - `=~`: збіг за регулярним виразом (RE2).
   - `!~`: заперечення збігу за регулярним виразом.
4. Якщо вузол збігається з мітками алерту, алерт призначається приймачу цього вузла (`receiver`). Якщо на вузлі встановлено `continue: false` (за замовчуванням), обхід дерева завершується. Якщо `continue: true`, пошук триває далі для можливого дублювання сповіщення в інші приймачі.

## 3. Специфікація HTTP REST API v2 Alertmanager

Alertmanager надає відкритий REST API v2 на основі специфікації OpenAPI. Цей інтерфейс використовується веб-інтерфейсами, CLI-утилітою `amtool` та зовнішніми системами автоматизації для отримання поточного стану сповіщень та керування регламентними вікнами.

### Основні ендпоінти API:

1. **`GET /api/v2/alerts`**
   Повертає повний перелік активних та нещодавно знятих алертів у системі.
   - Параметри URL-запиту:
     - `filter`: масив селекторів міток для вибірки (наприклад, `filter=severity="page"`, `filter=cluster=~"prod-.*"`).
     - `silenced`: булевий прапорець (true/false) — чи включати алерти, приглушені активними вікнами замовчування.
     - `inhibited`: булевий прапорець — чи включати алерти, заблоковані правилами інгібування.
     - `active`: фільтрація за поточним станом активності.
   - Формат відповіді: JSON-масив об'єктів алерту з полями `labels`, `annotations`, `receivers`, `fingerprint`, `startsAt`, `updatedAt`, `endsAt`, `status`.

2. **`POST /api/v2/alerts`**
   Програмний ендпоінт для прямого надсилання алертів у Alertmanager від сторонніх систем телеметрії або серверів Prometheus.
   - Тіло запиту: JSON-масив об'єктів `PostableAlert` (обов'язкові поля `labels`, необов'язкові `annotations`, `startsAt`, `endsAt`, `generatorURL`).

3. **`GET /api/v2/silences`**
   Отримання переліку діючих, майбутніх та архівних вікон замовчування.
   - Параметри фільтрації: `filter` за мітками або автором.
   - Повертає об'єкти замовчування зі статусами `state: "active" | "pending" | "expired"`.

4. **`POST /api/v2/silences`**
   Створення нового вікна замовчування інженером або скриптом автоматизованого розгортання перед початком робіт:
   ```json
   {
     "matchers": [
       { "name": "cluster", "value": "prod-eu", "isRegex": false, "isEqual": true },
       { "name": "service", "value": "checkout", "isRegex": false, "isEqual": true }
     ],
     "startsAt": "2026-08-20T02:00:00Z",
     "endsAt": "2026-08-20T04:00:00Z",
     "createdBy": "oncall-engineer@company.com",
     "comment": "Planned database migration window ticket #OPS-402"
   }
   ```

5. **`DELETE /api/v2/silence/{id}`**
   Дострокове скасування вікна замовчування після успішного завершення робіт.

## 4. Специфікація JSON-контракту Webhook (Alertmanager v4 Schema)

При взаємодії з користувацькими шлюзами сповіщень Alertmanager надсилає HTTP POST-запит з тілом у форматі JSON (версія протоколу v4).

### Повна схема JSON-пейлоаду:

```json
{
  "version": "4",
  "groupKey": "{}:{alertname=\"HighErrorRate\", cluster=\"prod-eu-1\"}",
  "truncatedAlerts": 0,
  "status": "firing",
  "receiver": "webhook-gateway",
  "groupLabels": {
    "alertname": "HighErrorRate",
    "cluster": "prod-eu-1"
  },
  "commonLabels": {
    "alertname": "HighErrorRate",
    "cluster": "prod-eu-1",
    "job": "payment-api",
    "severity": "page"
  },
  "commonAnnotations": {
    "summary": "Payment API error rate is above 1%",
    "runbook_url": "https://wiki.internal.net/runbooks/payment-api-5xx"
  },
  "externalURL": "https://alertmanager.internal.net",
  "alerts": [
    {
      "status": "firing",
      "labels": {
        "alertname": "HighErrorRate",
        "cluster": "prod-eu-1",
        "instance": "10.240.4.12:8080",
        "job": "payment-api",
        "severity": "page"
      },
      "annotations": {
        "dashboard_url": "https://grafana.internal.net/d/payments?var-instance=10.240.4.12:8080",
        "description": "Instance 10.240.4.12:8080 error rate is 4.8% over last 5m",
        "runbook_url": "https://wiki.internal.net/runbooks/payment-api-5xx",
        "summary": "Payment API error rate is above 1%"
      },
      "startsAt": "2026-08-20T01:15:00.000Z",
      "endsAt": "0001-01-01T00:00:00.000Z",
      "generatorURL": "https://prometheus.internal.net/graph?g0.expr=...",
      "fingerprint": "8f3b2c1d4e5a6b7c"
    }
  ]
}
```

### Гарантії доставки та вимоги до приймача (Webhook Contract):
1. **Семантика доставки «щонайменше один раз» (At-least-once):** За наявності мережевих збоїв Alertmanager повторює POST-запит з експоненційним відкатом (Exponential Backoff: від 100ms до максимум 5 хвилин). Приймач зобов'язаний бути **ідемпотентним**, використовуючи комбінацію полів `groupKey` та `fingerprint` як унікальний ключ дедуплікації.
2. **Таймаут відповіді:** Приймач зобов'язаний повернути HTTP-статус `200 OK` або `204 No Content` протягом не більше ніж 10 секунд, інакше спроба вважається невдалою і планується повтор.
3. **Статус відновлення (`endsAt`):** Якщо алерт перейшов у стан `resolved`, поле `status` встановлюється в `"resolved"`, а поле `endsAt` містить точний час фіксації нормалізації метрики.
4. **Форматування повідомлень через бібліотеку шаблонів:** Шаблонізатор підтримує вбудовані функції обробки тексту: `reReplaceAll`, `title`, `toUpper`, `toLower`, `join`, `match`, а також числові помічники форматування байтів (`humanize1024`) та затримок часу (`humanizeDuration`).
