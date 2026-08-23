# ⚙️ Реалізація автоматизованого FinOps-конвеєра у CI/CD

Ця вставка містить практичну реалізацію автоматизованого FinOps-вартового (англ. *FinOps Guardrail*) у конвеєрах GitHub Actions та GitLab CI. Наведено повний робочий код інспекції інфраструктури як коду (IaC), оцінки станичних та динамічних фінансових метрик, публікації розширених коментарів у Pull Request та автоматичного блокування злиття при порушенні бюджету.

## 1. Загальна архітектура автоматизованого FinOps-конвеєра

Автоматизований FinOps-конвеєр розробляється як невід'ємна частина загального пайплайну безперервної інтеграції (CI/CD). Його головне завдання — дати розробнику миттєвий зворотний зв'язок про фінансові наслідки його правок без залучення ручної праці DevOps-інженерів або фінансових аналітиків.

Конвеєр налаштовується на виконання при кожній події у Pull Request (створення, оновлення коду, додавання або зняття міток). Для запобігання зайвим запускам використовується фільтрація шляхів (`paths`), що обмежує виконання лише тими коммітами, які торкаються файлів конфігурації інфраструктури (`terraform/**`, `helm/**`) або вихідного коду сервісів (`src/**`).

Крім того, у конвеєрі налаштовується контроль паралельних запусків (Concurrency Control). При відправці розробником кількох послідовних коммітів у одну гілку PR попередні тривалі збірки аналізу автоматично скасовуються, заощаджуючи ресурси самих CI-воркерів.

Нижче наведено повну конфігурацію workflow GitHub Actions у файлі `.github/workflows/finops-cost-guardrail.yml`.

```yaml
name: "FinOps Cost Guardrail"

on:
  pull_request:
    types: [opened, synchronize, reopened, labeled, unlabeled]
    paths:
      - 'terraform/**'
      - 'src/**'

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  cost-guardrail:
    name: "Evaluate Cost Fitness Function"
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      statuses: write

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Setup Infracost
        uses: infracost/actions/setup@v3
        with:
          api-key: ${{ secrets.INFRACOST_API_KEY }}

      - name: Generate Infracost Baseline JSON
        run: |
          infracost breakdown --path=terraform/environments/prod \
                             --format=json \
                             --out-file=/tmp/infracost-base.json
        env:
          INFRACOST_VCS_PULL_REQUEST_AUTHOR: ${{ github.actor }}

      - name: Checkout PR Branch
        run: git checkout ${{ github.event.pull_request.head.sha }}

      - name: Generate Infracost Diff JSON
        run: |
          infracost diff --path=terraform/environments/prod \
                         --compare-to=/tmp/infracost-base.json \
                         --format=json \
                         --out-file=/tmp/infracost-diff.json

      - name: Setup Open Policy Agent (OPA)
        uses: open-policy-agent/setup-opa@v2
        with:
          version: latest

      - name: Evaluate Guardrail Policies & Unit-Cost Thresholds
        id: guardrail
        run: |
          python3 .github/scripts/evaluate_cost_guardrails.py \
            --diff-json=/tmp/infracost-diff.json \
            --pr-event=${{ github.event_path }} \
            --output-json=/tmp/guardrail-result.json

      - name: Post PR Comment and Status Check
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const result = JSON.parse(fs.readFileSync('/tmp/guardrail-result.json', 'utf8'));
            
            const commentBody = `## 💰 FinOps Cost Fitness Function Result: ${result.status_emoji}
            
            **Щомісячна зміна витрат:** \`$${result.delta_monthly_cost}\` (${result.delta_percent}%)
            **Поточний кошторис:** \`$${result.new_monthly_cost}/міс\`
            
            ${result.violations_markdown}
            
            <details><summary>🔍 Розгортка за ресурсами</summary>
            
            ${result.breakdown_markdown}
            
            </details>`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: commentBody
            });

            if (result.status === 'BLOCKED') {
              core.setFailed(`FinOps Guardrail Blocked PR: ${result.summary_reason}`);
            }
```

### Покроковий розбір роботи GitHub Actions Workflow

1. **Ініціалізація та права доступу:** Блок `permissions` явно вказує мінімально необхідні привілеї для токена GitHub Actions: читання репозиторію (`contents: read`), запис коментарів у PR (`pull-requests: write`) та можливість встановлення статусу збірки (`statuses: write`). Це відповідає принципу найменших привілеїв (Least Privilege Principle) у системі безпеки CI/CD.
2. **Автентифікація в API цінового двигуна:** Крок `Setup Infracost` підключає секретний ключ `INFRACOST_API_KEY`, збережений у секретах репозиторію. Ключ використовується для завантаження актуальних тарифікаційних сіток хмарних провайдерів (AWS, GCP, Azure) без перевищення лімітів запитів (Rate Limits).
3. **Побудова базового кошторису (Baseline):** Крок `Generate Infracost Baseline JSON` аналізує стабільний стан інфраструктури у гілці `main` і створює файл `/tmp/infracost-base.json`. Це значення є точкою відліку для порівняння. Змінна `INFRACOST_VCS_PULL_REQUEST_AUTHOR` передає інформацію про автора комміта для аналітики.
4. **Обчислення зсуву кошторису (Diff):** Крок `Generate Infracost Diff JSON` переключає робочий простір на комміт поточного Pull Request і генерує файл `/tmp/infracost-diff.json`, який описує дельту витрат. Інструмент розпізнає створені, модифіковані та видалені ресурси.
5. **Виконання фінансового оцінювача:** Python-скрипт `evaluate_cost_guardrails.py` приймає на вхід згенерований diff-файл та метадані події GitHub (`github.event_path`), оцінює бюджетні правила й повертає підсумковий вердикт у JSON-форматі.
6. **Публікація зворотного зв'язку:** Крок `actions/github-script` відправляє сформований маркдаун-звіт у коментарі PR і при наявності статусу `BLOCKED` викликає функцію `core.setFailed`, яка фізично блокує можливість злиття PR (Merge Gate).

## 2. Скрипт оцінки метрик та формування вердикту (`evaluate_cost_guardrails.py`)

Мозок автоматизованого вартого — це Python-скрипт `.github/scripts/evaluate_cost_guardrails.py`. Він обробляє розкладання витрат, перевіряє дотримання корпоративних граничних лімітів, шукає мітку аварійного обходу та будує розширену маркдаун-таблицю для інженерної команди.

Скрипт розроблено з урахуванням захисного програмування (Defensive Programming): він безпечно обробляє відсутність деяких полів у JSON-файлах, захищений від ділення на нуль при перевірці повністю нових проектів (де `totalPastMonthlyCost == 0`) та координує обхід блокувань при наявності мітки `cost-bypass-approved`.

:::tabs
```python
#!/usr/bin/env python3
"""Оцінка фітнес-функції вартості та формування вердикту для CI/CD."""

import json
import sys
import argparse
from typing import Dict, Any, List

# Корпоративні порогові значення за замовчуванням
MAX_ABSOLUTE_DIFF_USD = 200.0
MAX_RELATIVE_DIFF_PERCENT = 15.0
BYPASS_LABEL = "cost-bypass-approved"

def evaluate_guardrails(diff_data: Dict[str, Any], pr_event: Dict[str, Any]) -> Dict[str, Any]:
    """Аналіз JSON-звіту Infracost та генерація структурованого вердикту."""
    total_past = float(diff_data.get("totalPastMonthlyCost", "0") or "0")
    total_new = float(diff_data.get("totalMonthlyCost", "0") or "0")
    total_diff = float(diff_data.get("totalMonthlyCostDiff", "0") or "0")
    
    delta_percent = (total_diff / total_past * 100.0) if total_past > 0 else 0.0
    
    # Перевірка наявності мітки аварійного обходу у PR
    labels = [l["name"] for l in pr_event.get("pull_request", {}).get("labels", [])]
    has_bypass = BYPASS_LABEL in labels
    
    violations = []
    if total_diff > MAX_ABSOLUTE_DIFF_USD:
        violations.append(
            f"❌ Перевищено абсолютний поріг витрат: **+${total_diff:.2f}/міс** (ліміт: `${MAX_ABSOLUTE_DIFF_USD:.2f}/міс`)"
        )
    
    if delta_percent > MAX_RELATIVE_DIFF_PERCENT and total_past > 0:
        violations.append(
            f"❌ Перевищено відносний поріг витрат: **+{delta_percent:.1f}%** (ліміт: `${MAX_RELATIVE_DIFF_PERCENT:.1f}%`)"
        )
    
    # Визначення статусу
    status = "PASSED"
    status_emoji = "✅ PASSED"
    if violations:
        if has_bypass:
            status = "WARNING"
            status_emoji = "⚠️ WARNING (Bypassed)"
        else:
            status = "BLOCKED"
            status_emoji = "🚫 BLOCKED"
            
    # Побудова розгортки змін за ресурсами
    breakdown_items = []
    for project in diff_data.get("projects", []):
        for res in project.get("breakdown", {}).get("resources", []):
            diff = float(res.get("monthlyCostDiff", "0") or "0")
            if abs(diff) > 0.01:
                action = "➕" if diff > 0 else "➖"
                breakdown_items.append(f"| {action} `{res['name']}` | `{res['resourceType']}` | `${diff:+.2f}/міс` |")
                
    breakdown_md = "\n".join([
        "| Ресурс | Тип | Зміна витрат |",
        "| :--- | :--- | :--- |"
    ] + breakdown_items) if breakdown_items else "Змін у структурі витрат не виявлено."
    
    violations_md = "\n".join(violations) if violations else "Порушень фінансових лімітів не зафіксовано."
    if has_bypass and violations:
        violations_md += f"\n\n⚠️ **Примітка:** Блокування знято через наявність мітки `{BYPASS_LABEL}`."

    return {
        "status": status,
        "status_emoji": status_emoji,
        "past_monthly_cost": round(total_past, 2),
        "new_monthly_cost": round(total_new, 2),
        "delta_monthly_cost": round(total_diff, 2),
        "delta_percent": round(delta_percent, 1),
        "violations_markdown": violations_md,
        "breakdown_markdown": breakdown_md,
        "summary_reason": "; ".join(violations) if violations else "OK"
    }

def main():
    parser = argparse.ArgumentParser(description="FinOps Guardrail Evaluator")
    parser.add_argument("--diff-json", required=True, help="Шлях до JSON-файлу Infracost diff")
    parser.add_argument("--pr-event", required=True, help="Шлях до JSON-файлу події GitHub PR")
    parser.add_argument("--output-json", required=True, help="Шлях до вихідного результату")
    args = parser.parse_args()

    with open(args.diff_json, 'r', encoding='utf-8') as f:
        diff_data = json.load(f)
    with open(args.pr_event, 'r', encoding='utf-8') as f:
        pr_event = json.load(f)

    result = evaluate_guardrails(diff_data, pr_event)

    with open(args.output_json, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
```
```typescript
import * as fs from 'fs';

interface ResourceDiff {
  name: string;
  resourceType: string;
  monthlyCostDiff: string;
}

interface InfracostDiff {
  totalPastMonthlyCost: string;
  totalMonthlyCost: string;
  totalMonthlyCostDiff: string;
  projects: Array<{
    breakdown: {
      resources: ResourceDiff[];
    };
  }>;
}

export function evaluateGuardrailTS(diffPath: string, maxDiffUsd: number = 200.0): boolean {
  const rawData = fs.readFileSync(diffPath, 'utf-8');
  const data: InfracostDiff = JSON.parse(rawData);
  const diffUsd = parseFloat(data.totalMonthlyCostDiff || '0');
  
  if (diffUsd > maxDiffUsd) {
    console.error(`[FinOps Guardrail] Cost increase $${diffUsd} exceeds limit $${maxDiffUsd}`);
    return false;
  }
  
  console.log(`[FinOps Guardrail] Cost check passed: +$${diffUsd}/month`);
  return true;
}
```
:::

## 3. Динамічне профілювання юніт-вартості у CI (k6 Script)

Для оцінки **динамічної фітнес-функції (Шар 2)** у CI/CD застосовується скрипт навантажувального тестування на базі k6. Скрипт подає стандартизоване навантаження на сервіс, збирає фізичні показники CPU та RAM і обчислює підсумкову вартість на 1000 запитів.

Профілювання виконується на тестовому стенді (Staging Environment). Скрипт надсилає серію з 1000 запитів, вимірює середню затримку виконання (`http_req_duration`) та розраховує споживання процесорного часу.

```javascript
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  scenarios: {
    unit_cost_profile: {
      executor: 'shared-iterations',
      vus: 10,
      iterations: 1000,
      maxDuration: '2m',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<200'], // Latency SLO < 200ms
  },
};

// Вартісні коефіцієнти AWS Lambda / Fargate (USD за одиницю)
const PRICE_PER_CPU_MS = 0.00000001;
const PRICE_PER_RAM_MB_SEC = 0.000000002;

export default function () {
  const res = http.get('http://telemetry-service.staging.local/api/v1/devices/status');
  
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
}

export function handleSummary(data) {
  const avgDurationMs = data.metrics.http_req_duration.values.avg;
  const totalReqs = data.metrics.http_reqs.values.count;
  
  // Оціночний розрахунок юніт-вартості 1000 запитів
  const estimatedCpuCost = avgDurationMs * PRICE_PER_CPU_MS * totalReqs;
  const estimatedRamCost = (256) * (avgDurationMs / 1000) * PRICE_PER_RAM_MB_SEC * totalReqs;
  const totalUnitCostPer1k = estimatedCpuCost + estimatedRamCost;

  return {
    'stdout': textSummary(data, totalUnitCostPer1k),
    '/tmp/k6-unit-cost.json': JSON.stringify({
      total_requests: totalReqs,
      avg_duration_ms: avgDurationMs,
      unit_cost_per_1k_usd: totalUnitCostPer1k
    }),
  };
}

function textSummary(data, unitCost) {
  return `\n========================================\n` +
         `📊 FinOps Dynamic Unit-Cost Summary\n` +
         `----------------------------------------\n` +
         `Всього запитів: ${data.metrics.http_reqs.values.count}\n` +
         `Середній час відгуку: ${data.metrics.http_req_duration.values.avg.toFixed(2)} ms\n` +
         `Юніт-вартість 1000 запитів: $${unitCost.toFixed(6)} USD\n` +
         `========================================\n`;
}
```

### Зчитування та обробка результатів динамічного профілювання

Отриманий файл `/tmp/k6-unit-cost.json` зчитується фінальним кроком CI-конвеєра. Скрипт порівнює згенероване значення `unit_cost_per_1k_usd` із відповідним значенням базової гілки `main`. Якщо юніт-вартість 1000 запитів перевищує базоване значення понад 10%, CI-бот маркує динамічну фітнес-функцію як `FAILED` і запобігає розгортанню неефективного коду.

## 4. Конфігурація GitLab CI (.gitlab-ci.yml)

Для команд, які використовують GitLab CI/CD, аналогічний конвеєр реалізується через файл `.gitlab-ci.yml` із використанням Docker-образів Infracost та OPA.

```yaml
stages:
  - finops-guardrail

infracost_cost_check:
  stage: finops-guardrail
  image:
    name: infracost/infracost:ci-0.10
    entrypoint: [""]
  script:
    - infracost breakdown --path=terraform/environments/prod --format=json --out-file=/tmp/infracost-base.json
    - git checkout $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME
    - infracost diff --path=terraform/environments/prod --compare-to=/tmp/infracost-base.json --format=json --out-file=/tmp/infracost-comment.md
  only:
    - merge_requests
  artifacts:
    paths:
      - /tmp/infracost-comment.md
```

Ця конфігурація забезпечує повну паритетність функціоналу контролю вартості між різними CI/CD платформами.

## 5. Сповіщення у чати та оптимізація швидкодії CI

Для підвищення оперативної прозорості результат роботи вартого не лише публікується у Pull Request, але й надсилається у командні чати (Slack / Teams / Telegram).

При виявленні статусу `BLOCKED` або при використанні аварійного обходу `cost-bypass-approved` Python-скрипт надсилає HTTP POST запит на Webhook каналу інженерної команди:

```json
{
  "text": "🚨 *FinOps Guardrail Alert*: PR #142 у сервісі `telemetry-service` заблоковано через перевищення бюджету!\n*Зміна кошторису:* +$640.50/міс (+51.2%)\n*Автор:* @developer_name\n*Посилання:* https://github.com/digital-homes/telemetry-service/pull/142"
}
```

Оптимізація часу виконання самого CI-конвеєра є критичною вимогою, щоб перевірка не ставала завадою для розробників. Для цього використовується кешування тарифних таблиць Infracost та файлів моделей на рівні CI-раннерів. Це знижує час виконання кроку аналізу кошторису до 8–12 секунд.

Крім того, у великих корпоративних проєктах рекомендується зберігати індекс історичних оцінок у централізованій базі аналітики (наприклад, у ClickHouse чи PostgreSQL). Це дозволяє FinOps-команді спостерігати тренди зростання кошторису в розрізі команд, сервісів та окремих інженерних продуктів протягом тривалих часових періодів.
