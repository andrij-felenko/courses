# 📋 Специфікація та правила FinOps-політик у CI (Infracost API & Rego Contract)

Ця вставка містить розширену довідкову специфікацію форматів даних, програмних інтерфейсів (API), OpenAPI/JSON-схем, специфікацій політик Open Policy Agent (OPA) та параметрів конфігурації для автоматичного контролю вартості у CI/CD. Вона слугує нормативним контрактом для інтеграції статичного та динамічного фінансового аналізу у пайплайни розгортання інфраструктури.

## 1. Специфікація CLI та конфігурації Infracost

Інструмент Infracost надає інтерфейс командного рядка (CLI) для синтаксичного аналізу файлів конфігурації інфраструктури як коду (Infrastructure as Code — IaC) та порівняння прогнозного кошторису з актуальними тарифами хмарних провайдерів.

### Основні команди та прапорці CLI

Використання Infracost у CI-конвеєрі спирається на три базові команди execution flow:

1. **`infracost breakdown`**: Виконує повну інспекцію вказаного каталогу інфраструктури (наприклад, `terraform/environments/prod`) та генерує підсумковий знімок витрат для базової гілки (наприклад, `main`).
   - `--path`: Шлях до робочого каталогу Terraform/OpenTofu або до згенерованого файлу Terraform Plan у форматі JSON (`plan.json`).
   - `--format=json`: Формат виводу результату. Для автоматизованого аналізу у CI завжди використовується `json`.
   - `--out-file`: Шлях до вихідного JSON-файла, де буде збережено знімок кошторису (`/tmp/infracost-base.json`).
   - `--usage-file`: Опціональний шлях до файлу оцінки користувацького навантаження (`infracost-usage.yml`), який визначає прогнозні обсяги трафіку та запросів для ресурсів із тарифікацією за використанням (Usage-based Resources).

2. **`infracost diff`**: Виконує відносний порівняльний аналіз між поточним станом робочого простору у Pull Request та раніше збереженим базовим JSON-знімком.
   - `--path`: Шлях до модифікованого каталогу інфраструктури PR.
   - `--compare-to`: Обов'язковий шлях до базового JSON-файла (`/tmp/infracost-base.json`).
   - `--format=json`: Формат підсумкового відносного звіту (`/tmp/infracost-diff.json`).

3. **`infracost output`**: Трансформує згенерований JSON-звіт у зручні формати для публікації у VCS-платформах.
   - `--format=github-comment`: Генерує маркдаун-текст коментаря, адаптований для публікації через GitHub PR Comments API.
   - `--format=gitlab-comment`: Генерує маркдаун-текст коментаря для GitLab Merge Request.

### Специфікація файлу оцінки використання (infracost-usage.yml)

Для ресурсів, вартість яких залежить від динамічного навантаження в рантаймі (наприклад, AWS Lambda, Amazon DynamoDB, Amazon S3, Google Cloud Run), Infracost використовує конфігураційний файл `infracost-usage.yml`. Цей файл описує прогнозні обсяги використання ресурсів:

```yaml
version: "0.1"
resource_usage:
  aws_lambda_function.telemetry_processor:
    monthly_requests: 50000000          # Прогноз: 50 млн викликів на місяць
    request_duration_ms: 150            # Середня тривалість виконання 150 мс
  aws_dynamodb_table.device_state:
    monthly_read_request_units: 10000000  # 10 млн одиниць читання RCU
    monthly_write_request_units: 2000000  # 2 млн одиниць запису WCU
  aws_s3_bucket.video_archive:
    capacity_gb: 5000                   # 5 ТБ збережених даних у S3 Standard
    monthly_get_requests: 100000        # 100 тисяч GET-запитів
    monthly_put_requests: 50000         # 50 тисяч PUT-запитів
```

## 2. Специфікація JSON-виводу Infracost Diff

Під час виконання команди `infracost diff --format=json` у CI-конвеєрі створюється структурований документ, який описує поточний стан інфраструктури, майбутній стан та абсолютні й відносні зміни у витратах.

Нижче наведено розширену JSON-структуру згенерованого документа, яка використовується як вхідні дані (`input.infracost`) для оцінки OPA-політик.

```json
{
  "$schema": "https://schema.infracost.io/v0.2/config.json",
  "version": "0.2",
  "currency": "USD",
  "projects": [
    {
      "name": "digital-homes/telemetry-service",
      "metadata": {
        "path": "terraform/environments/prod",
        "type": "terraform_dir",
        "vcsRepoUrl": "https://github.com/digital-homes/telemetry-service",
        "vcsSubPath": "terraform/environments/prod"
      },
      "pastMonthlyCost": "1250.00",
      "monthlyCost": "1890.50",
      "diffMonthlyCost": "640.50",
      "breakdown": {
        "resources": [
          {
            "name": "aws_db_instance.telemetry_db",
            "resourceType": "aws_db_instance",
            "tags": {
              "Environment": "production",
              "Owner": "data-team",
              "CostCenter": "CC-409"
            },
            "metadata": {
              "instanceType": "db.r6g.2xlarge",
              "region": "eu-central-1"
            },
            "pastMonthlyCost": "480.00",
            "monthlyCost": "960.00",
            "monthlyCostDiff": "480.00",
            "costComponents": [
              {
                "name": "Database instance (on-demand, db.r6g.2xlarge)",
                "unit": "hours",
                "monthlyQuantity": "730",
                "price": "0.6576",
                "monthlyCost": "480.00",
                "monthlyCostDiff": "240.00"
              },
              {
                "name": "Provisioned IOPS SSD storage (io2)",
                "unit": "GB",
                "monthlyQuantity": "500",
                "price": "0.125",
                "monthlyCost": "62.50",
                "monthlyCostDiff": "62.50"
              }
            ]
          }
        ]
      }
    }
  ],
  "totalPastMonthlyCost": "1250.00",
  "totalMonthlyCost": "1890.50",
  "totalMonthlyCostDiff": "640.50"
}
```

### Семантика ключових полів JSON-документа

- **`totalPastMonthlyCost`**: Сумарна оціночна вартість інфраструктури у доларах США на місяць до внесення змін з поточного Pull Request. Обчислюється як сума `pastMonthlyCost` усіх ресурсів.
- **`totalMonthlyCost`**: Прогнозована сумарна щомісячна вартість інфраструктури після розгортання змін із поточного Pull Request.
- **`totalMonthlyCostDiff`**: Абсолютна різниця у витратах між новим та попереднім станом (`totalMonthlyCost - totalPastMonthlyCost`). Може бути як додатною (подорожчання), так і від'ємною (оптимізація/здешевлення).
- **`projects[].breakdown.resources`**: Список усіх оброблених інфраструктурних ресурсів. Кожен ресурс містить масив `tags` для перевірки фінансової атрибуції та масив `costComponents`.
- **`costComponents`**: Деталізований розклад цінових складових конкретного ресурсу. Наприклад, для бази даних RDS це окремі компоненти: вартість обчислювального екземпляра (погодинна оплата), вартість зарезервованого дискового простору (GB/місяць) та вартість зарезервованих операцій вводу-виводу (IOPS).

## 3. Специфікація OPA-політики (Rego Policy Contract)

Правила фінансових вартових (FinOps Guardrails) описуються декларативною мовою Rego двигуна Open Policy Agent (OPA). Двигун OPA приймає на вхід об'єднаний контекст, який складається з JSON-звіту Infracost (`input.infracost`) та метаданих події Pull Request з Git-платформи (`input.pull_request`).

Нижче наведено нормативну специфікацію модуля `finops.guardrails`, який обчислює вердикт відповідності бюджетним лімітам.

```rego
package finops.guardrails

import future.keywords.in
import future.keywords.every

# За замовчуванням злиття коду заборонено, якщо політика не повернула явний allow
default allow = false
default max_diff_percent = 15.0
default max_absolute_diff_usd = 200.0
default emergency_bypass_tag = "cost-bypass-approved"

# Дозволити розгортання, якщо відсутні явні порушення або присутній підписаний bypass
allow {
    not has_violations
}

allow {
    has_emergency_bypass
}

# Перевірка наявності мітки екстреного обходу у метаданих PR
has_emergency_bypass {
    input.pull_request.labels[_] == emergency_bypass_tag
}

# Правило 1: Виявлення перевищення абсолютного порогу подорожчання
violations[msg] {
    diff := to_number(input.infracost.totalMonthlyCostDiff)
    diff > max_absolute_diff_usd
    msg := sprintf("Абсолютне зростання вартості (+$%.2f/міс) перевищує встановлений корпоративний поріг ($%.2f/міс)", [diff, max_absolute_diff_usd])
}

# Правило 2: Виявлення перевищення відносного порогу подорожчання у відсотках
violations[msg] {
    past := to_number(input.infracost.totalPastMonthlyCost)
    past > 0
    diff := to_number(input.infracost.totalMonthlyCostDiff)
    percent := (diff / past) * 100.0
    percent > max_diff_percent
    msg := sprintf("Відносне зростання вартості (+%.1f%%) перевищує допустимий ліміт проекту (+%.1f%%)", [percent, max_diff_percent])
}

# Правило 3: Перевірка обов'язкових тегів фінансової атрибуції на нових або змінених ресурсах
violations[msg] {
    some project in input.infracost.projects
    some resource in project.breakdown.resources
    resource.monthlyCostDiff != "0.00"
    missing_tags := required_tags - object.keys(resource.tags)
    count(missing_tags) > 0
    msg := sprintf("Інфраструктурний ресурс %s модифіковано, але відсутні обов'язкові FinOps-теги: %v", [resource.name, missing_tags])
}

# Набір обов'язкових тегів для будь-якого ресурсу у хмарі
required_tags = {"Environment", "Owner", "CostCenter"}

# Вподобана умова наявності хоча б одного порушення
has_violations { count(violations) > 0 }
```

### Механізм виконання та семантика політики Rego

1. **Вхідний контекст (`input`)**: Двигун OPA одержує єдине дерево даних, що містить поля `input.infracost` (структура розкладу витрат) та `input.pull_request` (список залучених файлів, міток, автора та опису PR).
2. **Множина порушень (`violations`)**: Кожне правило у формі `violations[msg]` генерує новий текстовий рядок помилки при виконанні зазначених умов. Якщо жодне правило не спрацювало, множина `violations` є порожньою (`count(violations) == 0`).
3. **Обчислення правдивої умови (`allow`)**: Головна змінна `allow` набуває значення `true` лише у двох випадках: коли множина порушень порожня, або коли серед міток Pull Request присутній спеціальний ідентифікатор `cost-bypass-approved`.
4. **Валідація тегів (`required_tags`)**: Правило 3 порівнює множину обов'язкових ключів `{"Environment", "Owner", "CostCenter"}` із фактичними ключами об'єкта `resource.tags`. Якщо ресурс подорожчав або змінив конфігурацію, але не має хоча б одного з цих тегів, генерується повідомлення про блокування.

## 4. Матриця конфігурації FinOps Guardrails

Параметри та правила перевірки конфігуруються у файлі `.finops-guardrails.yml`, який розміщується в корені репозиторію проєкту. Це дозволяє гнучко налаштовувати порогові значення залежно від критичності середовища (Development vs Staging vs Production).

```yaml
version: "1.0"
guardrails:
  production:
    max_absolute_diff_usd: 200.0
    max_relative_diff_percent: 15.0
    block_on_missing_tags: true
    require_adr_on_warn: true
    unit_cost_max_degradation_percent: 10.0
    bypass_label: "cost-bypass-approved"
    required_tags:
      - Environment
      - Owner
      - CostCenter
      - Service
  staging:
    max_absolute_diff_usd: 500.0
    max_relative_diff_percent: 50.0
    block_on_missing_tags: false
    require_adr_on_warn: false
    unit_cost_max_degradation_percent: 25.0
    bypass_label: "cost-bypass-approved"
```

Нижче наведено повну довідкову таблицю параметрів конфігурації з розшифровкою їхнього призначення та типів даних.

| Параметрична назва | Тип даних | Значення за замовчуванням | Опис і детальні правила застосування |
| :--- | :--- | :--- | :--- |
| `max_absolute_diff_usd` | Float | `200.0` | Максимально дозволений абсолютний приріст щомісячного рахунку в USD на один PR. При перевищенні генерується помилка `BLOCKED`. |
| `max_relative_diff_percent` | Float | `15.0` | Максимально дозволений відносний приріст кошторису інфраструктури у відсотках відносно поточного базового бюджету `totalPastMonthlyCost`. |
| `block_on_missing_tags` | Boolean | `true` | Прапор суворого блокування PR, якщо нові ресурси не мають усіх обов'язкових фінансових тегів (`Owner`, `CostCenter`, `Environment`). |
| `require_adr_on_warn` | Boolean | `true` | Вимагати обов'язкового посилання на документ рішення (ADR-XXX) у тексті опису PR при наявності м'яких попереджень. |
| `unit_cost_max_degradation_percent` | Float | `10.0` | Максимально допустиме відсоткове зростання динамічного профілю юніт-вартості транзакції під час канаркового або CI-навантажувального тесту. |
| `bypass_label` | String | `cost-bypass-approved` | Унікальна текстова мітка PR у GitHub/GitLab, яка знімає суворі блокування для екстрених гарячих правок під час інцидентів. |

## 5. Специфікація коментаря PR Bot та JSON-метаданих

Після виконання оцінки CI-бот генерує розширений коментар у Pull Request, який містить як візуальну маркдаун-таблицю для людей, так і прихований JSON-конверт для автоматизованого зчитування іншими CI-сервісами.

### Приклад згенерованого Маркдаун-коментаря у Pull Request

```markdown
## 💰 FinOps Cost Fitness Function Result: 🚫 BLOCKED

**Щомісячна зміна витрат:** `+$640.50` (+51.2%)
**Поточний кошторис:** `$1890.50/міс` (базовий: `$1250.00/міс`)

### ❌ Виявлені порушення бюджетних політик:
- ❌ Перевищено абсолютний поріг витрат: **+$640.50/міс** (корпоративний ліміт: `$200.00/міс`)
- ❌ Перевищено відносний поріг витрат: **+51.2%** (проєктний ліміт: `+15.0%`)
- ❌ Інфраструктурний ресурс `aws_db_instance.telemetry_db` модифіковано, але відсутні обов'язкові FinOps-теги: `["CostCenter"]`

<details><summary>🔍 Деталізація змін за ресурсами</summary>

| Ресурс | Тип ресурсу | Зміна витрат |
| :--- | :--- | :--- |
| ➕ `aws_db_instance.telemetry_db` | `aws_db_instance` | `+$480.00/міс` |
| ➕ `aws_ebs_volume.telemetry_io` | `aws_ebs_volume` | `+$160.50/міс` |

</details>

---
*Для зняття блокування у випадку екстреної аварії додайте мітку `cost-bypass-approved` або внесіть посилання на схвалений ADR у опис PR.*
```

### JSON Schema метаданих коментаря (FinOpsCICommentPayload)

Для забезпечення програмної сумісності та збереження історії фінансових оцінок у базі метрик, бот додає у нижній частині коментаря прихований тег `<script type="application/json">` із JSON-документом, який відповідає наступній JSON-схемі.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "FinOpsCICommentPayload",
  "type": "object",
  "properties": {
    "commit_sha": {
      "type": "string",
      "description": "Повний SHA-1 хеш комміту, для якого виконувалася оцінка"
    },
    "pipeline_id": {
      "type": "string",
      "description": "Унікальний ідентифікатор запуску CI конвеєра"
    },
    "currency": {
      "type": "string",
      "default": "USD"
    },
    "past_monthly_cost": {
      "type": "number",
      "description": "Базова вартість інфраструктури до внесення змін"
    },
    "new_monthly_cost": {
      "type": "number",
      "description": "Прогнозована нова вартість інфраструктури"
    },
    "delta_monthly_cost": {
      "type": "number",
      "description": "Абсолютна зміна вартості у USD"
    },
    "delta_percent": {
      "type": "number",
      "description": "Відносна зміна вартості у відсотках"
    },
    "status": {
      "type": "string",
      "enum": ["PASSED", "WARNING", "BLOCKED"]
    },
    "violations": {
      "type": "array",
      "items": { "type": "string" }
    },
    "breakdown_summary": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "resource_name": { "type": "string" },
          "action": { "type": "string", "enum": ["ADD", "MODIFY", "REMOVE"] },
          "delta_usd": { "type": "number" }
        },
        "required": ["resource_name", "action", "delta_usd"]
      }
    }
  },
  "required": ["commit_sha", "status", "delta_monthly_cost", "violations"]
}
```
