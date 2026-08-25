# ⚙️ Побудова пайплайну «Архітектура як код»: від моделі Structurizr DSL до автоматичної валідації архітектурних правил

У великих інженерних організаціях розробка розподілених систем стикається з хронічною проблемою застарівання документації. Схеми, намальовані у графічних редакторах, зберігаються у вигляді статичних зображень і втрачають актуальність уже через кілька тижнів після релізу. Коли розробник створює новий виклик між сервісами, він рідко згадує про необхідність оновити картинку у Confluence чи Wiki.

Цей проєкт демонструє створення надійного виробничого конвеєра **«Архітектура як код» (Architecture as Code / AaC)**. Ми пройдемо повний шлях інженерної реалізації:
1. Створення декларативної моделі розподіленої платіжної платформи на мові Structurizr DSL.
2. Експорт абстрактного синтаксичного дерева (AST) моделі в машиночитний JSON-формат.
3. Реалізація архітектурного лінтера (Architecture Fitness Functions), який автоматично блокує порушення шаруватої архітектури та відсутність мережевих протоколів.
4. Інтеграція перевірок та генерації векторних SVG-діаграм у пайплайн неперервної інтеграції (CI/CD).

---

## 1. Опис архітектурної моделі (Structurizr DSL)

Почнемо з опису моделі нашої платіжної системи. Створимо файл `architecture/workspace.dsl`.

Модель фіксує ієрархію від бізнес-акторів до внутрішніх компонентів сервісу обробки платежів:

```dsl
workspace "Payment Gateway Architecture" "Архітектурна модель розподіленої платіжної платформи" {

    !identifiers hierarchical

    model {
        # Зовнішні стейкхолдери
        customer = person "Customer" "Клієнт інтернет-магазину" "User"
        merchant = person "Merchant" "Торговець, який переглядає звіти" "User"

        # Сторонні банківські сервіси
        bank = softwareSystem "Bank Acquiring" "Зовнішній банківський еквайринг" "External"
        fraudApi = softwareSystem "Fraud Screening" "Сторонній скоринг шахрайства" "External"

        # Наша програмна платформа
        paymentPlatform = softwareSystem "Payment Platform" "Високонавантажена платіжна платформа" {
            webSpa = container "Web SPA" "Клієнтський веб-кабінет" "React, TypeScript" "Web"
            apiGateway = container "API Gateway" "Точка входу, auth, rate limiting" "Envoy, Go" "Gateway"
            
            paymentService = container "Payment Service" "Оркестрація транзакцій" "Go 1.22" "Microservice" {
                grpcHandler = component "gRPC Handler" "Приймає запити створення платежу" "gRPC Server"
                orchestrator = component "Payment Orchestrator" "Керує станом саги платежу" "State Machine"
                outboxPub = component "Outbox Publisher" "Зберігає події в таблицю outbox" "Transactional Outbox"
                bankClient = component "Bank Client Adapter" "Взаємодіє з банком" "ISO 8583 Client"
            }

            ledgerService = container "Ledger Service" "Бухгалтерський баланс подвійного запису" "C++20" "Microservice"
            paymentDb = container "Payment DB" "Зберігає стан транзакцій" "PostgreSQL 16" "Database"
            messageBus = container "Event Bus" "Потік подій платежів" "Apache Kafka" "Broker"
        }

        # Зв'язки (Relationships)
        customer -> paymentPlatform.webSpa "Оплачує замовлення" "HTTPS"
        merchant -> paymentPlatform.webSpa "Переглядає баланс" "HTTPS"

        paymentPlatform.webSpa -> paymentPlatform.apiGateway "Викликає API" "JSON / HTTPS"
        paymentPlatform.apiGateway -> paymentPlatform.paymentService.grpcHandler "Створює платіж" "gRPC / Protobuf"
        paymentPlatform.apiGateway -> paymentPlatform.ledgerService "Запитує виписку" "gRPC / Protobuf"

        paymentPlatform.paymentService.grpcHandler -> paymentPlatform.paymentService.orchestrator "Передає команду" "In-process"
        paymentPlatform.paymentService.orchestrator -> paymentPlatform.paymentService.outboxPub "Фіксує подію" "In-process"
        paymentPlatform.paymentService.orchestrator -> paymentPlatform.paymentService.bankClient "Запитує авторизацію" "In-process"

        paymentPlatform.paymentService.outboxPub -> paymentPlatform.paymentDb "Атомарний запис транзакції та Outbox" "SQL / TCP"
        paymentPlatform.paymentService.bankClient -> bank "Авторизує платіж" "ISO 8583 / TLS"
        paymentPlatform.paymentService.outboxPub -> paymentPlatform.messageBus "Публікує PaymentCompleted" "Kafka Wire Protocol"
        paymentPlatform.messageBus -> paymentPlatform.ledgerService "Споживає події платежів" "Kafka Consumer Group"
    }

    views {
        systemContext paymentPlatform "Context_View" {
            include *
            autoLayout lr
        }

        container paymentPlatform "Containers_View" {
            include *
            autoLayout lr
        }

        component paymentPlatform.paymentService "PaymentService_Components" {
            include *
            autoLayout lr
        }

        styles {
            element "Person" { shape Person background #15803d color #ffffff }
            element "Software System" { background #1e40af color #ffffff }
            element "External" { background #64748b color #ffffff }
            element "Container" { background #2563eb color #ffffff }
            element "Component" { background #7c3aed color #ffffff }
            element "Database" { shape Cylinder background #b45309 color #ffffff }
            element "Broker" { shape Pipe background #b45309 color #ffffff }
            relationship "Relationship" { color #334155 thickness 2 }
        }
    }
}
```

---

## 2. Експорт моделі у формат JSON

Для автоматичного аналізу та перевірки правил архітектурної відповідності ми експортуємо модель у формат JSON за допомогою офіційної утиліти `structurizr-cli`:

```bash
# Експорт моделі Structurizr DSL у проміжний JSON-файл
structurizr export -w architecture/workspace.dsl -f json -o architecture/output/
```

Отриманий файл `workspace.json` містить нормалізований граф усіх сутностей і зв'язків системи.

---

## 3. Розробка архітектурного лінтера (Architecture Fitness Functions)

Архітектурна фітнес-функція — це автоматизований тест, який перевіряє дотримання архітектурних інваріантів під час кожної збірки системи.

Ми реалізуємо три критичні перевірки:
1. **Правило повноти протоколів (Rule 1):** жоден зв'язок у системі не може залишатися без вказаної технології або протоколу. Порожні стрілки є дефектом документації.
2. **Правило ізоляції контурів / No Bypass (Rule 2):** клієнтські застосунки (`Web SPA`, `Mobile App`) зобов'язані спілкуватися з внутрішніми мікросервісами та базами даних виключно через `API Gateway`. Прямий доступ із фронтенду до баз даних або внутрішніх бекендів категорично заборонений.
3. **Правило єдиного власника бази даних / Single Writer (Rule 3):** до сховища `Payment DB` дозволено підключатися лише мікросервісу `Payment Service`. Будь-який прямий SQL-доступ від інших сервісів (наприклад, від `Ledger Service`) порушує межі обмеженого контексту (Bounded Context).

Реалізуємо лінтер на трьох мовах, залежно від технологічного стеку вашої інфраструктури:

:::tabs
```ts
// validator.ts — Архітектурний валідатор на TypeScript / Node.js
import * as fs from 'fs';

interface Relationship {
    source: string;
    destination: string;
    description: string;
    technology: string;
}

interface WorkspaceModel {
    relationships: Relationship[];
    containers: { id: string; name: string; tags: string[] }[];
}

export function validateArchitecture(modelJsonPath: string): { passed: boolean; errors: string[] } {
    const raw = fs.readFileSync(modelJsonPath, 'utf-8');
    const model: WorkspaceModel = JSON.parse(raw);
    const errors: string[] = [];

    for (const rel of model.relationships) {
        // Правило 1: Перевірка обов'язковості опису протоколу
        if (!rel.technology || rel.technology.trim().length === 0) {
            errors.push(`[RULE-1] Зв'язок "${rel.source} -> ${rel.destination}" (${rel.description}) не має вказаного протоколу!`);
        }

        // Правило 2: Захист від прямого доступу UI до баз даних
        if (rel.source.includes('webSpa') && rel.destination.includes('Db')) {
            errors.push(`[RULE-2 CRITICAL] Виявлено прямий доступ UI "${rel.source}" до бази даних "${rel.destination}" в обхід API Gateway!`);
        }

        // Правило 3: Принцип Single Writer для бази даних платежів
        if (rel.destination.includes('paymentDb') && !rel.source.includes('paymentService')) {
            errors.push(`[RULE-3] Порушення ізоляції даних: сторонній контейнер "${rel.source}" намагається напряму читати/писати в "${rel.destination}".`);
        }
    }

    return {
        passed: errors.length === 0,
        errors
    };
}

// Точка входу
const result = validateArchitecture('./architecture/output/workspace.json');
if (!result.passed) {
    console.error(`❌ Архітектурний аудит провалено (${result.errors.length} дефектів):`);
    result.errors.forEach(err => console.error(`  - ${err}`));
    process.exit(1);
} else {
    console.log('✅ Архітектурну модель верифіковано: усі інваріанти виконано.');
}
```
```py
# validator.py — Архітектурний валідатор на Python
import json
import sys
from typing import List, Dict, Any

def validate_architecture(model_json_path: str) -> bool:
    """Перевіряє архітектурні інваріанти на графі зв'язків C4 моделі."""
    with open(model_json_path, "r", encoding="utf-8") as f:
        model: Dict[str, Any] = json.load(f)

    relationships: List[Dict[str, str]] = model.get("relationships", [])
    errors: List[str] = []

    for rel in relationships:
        src = rel.get("source", "")
        dst = rel.get("destination", "")
        desc = rel.get("description", "")
        tech = rel.get("technology", "").strip()

        # Правило 1: Перевірка наявності протоколу
        if not tech:
            errors.append(f"[RULE-1] Зв'язок '{src} -> {dst}' ({desc}) не містить специфікації протоколу!")

        # Правило 2: Захист від обходу API Gateway
        if "webSpa" in src and "Db" in dst:
            errors.append(f"[RULE-2 CRITICAL] Пряме підключення фронтенду '{src}' до сховища '{dst}' в обхід шлюзу!")

        # Правило 3: Принцип Single Writer для платіжної бази
        if "paymentDb" in dst and "paymentService" not in src:
            errors.append(f"[RULE-3] Несанкціонований доступ до бази: контейнер '{src}' звертається до '{dst}'!")

    if errors:
        print(f"❌ Архітектурний аудит виявив {len(errors)} дефектів:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return False

    print("✅ Архітектурний валідатор: модель відповідає всім встановленим правилам.")
    return True

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "./architecture/output/workspace.json"
    if not validate_architecture(target):
        sys.exit(1)
```
```cpp
// validator.cpp — Архітектурний валідатор на C++20
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

struct Relationship {
    std::string source;
    std::string destination;
    std::string description;
    std::string technology;
};

class ArchitectureLinter {
public:
    static bool validate(const std::string& json_path) {
        std::ifstream file(json_path);
        if (!file.is_open()) {
            std::cerr << "Помилка відкриття файлу моделі: " << json_path << "\n";
            return false;
        }

        json data;
        file >> data;

        std::vector<std::string> violations;

        for (const auto& item : data.value("relationships", json::array())) {
            Relationship rel{
                item.value("source", ""),
                item.value("destination", ""),
                item.value("description", ""),
                item.value("technology", "")
            };

            // Інваріант 1: Обов'язковість зазначення протоколу
            if (rel.technology.empty()) {
                violations.push_back("[RULE-1] Відсутній протокол у зв'язку: " + rel.source + " -> " + rel.destination);
            }

            // Інваріант 2: Заборона прямого доступу UI до бази даних
            if (rel.source.find("webSpa") != std::string::npos && rel.destination.find("Db") != std::string::npos) {
                violations.push_back("[RULE-2 CRITICAL] Прямий доступ із клієнта до БД: " + rel.source + " -> " + rel.destination);
            }

            // Інваріант 3: Single Writer для платіжної БД
            if (rel.destination.find("paymentDb") != std::string::npos && rel.source.find("paymentService") == std::string::npos) {
                violations.push_back("[RULE-3] Порушення Single Writer: сторонній сервіс " + rel.source + " викликає " + rel.destination);
            }
        }

        if (!violations.empty()) {
            std::cerr << "❌ Архітектурний лінтинг провалено (" << violations.size() << " дефектів):\n";
            for (const auto& v : violations) {
                std::cerr << "  - " << v << "\n";
            }
            return false;
        }

        std::cout << "✅ C++ валідатор: модель повністю відповідає архітектурним інваріантам.\n";
        return true;
    }
};

int main(int argc, char* argv[]) {
    std::string path = (argc > 1) ? argv[1] : "./architecture/output/workspace.json";
    return ArchitectureLinter::validate(path) ? 0 : 1;
}
```
:::

---

## 4. Конфігурація автоматизованого пайплайну CI/CD

Об'єднаємо всі кроки в єдиний робочий процес GitHub Actions (`.github/workflows/architecture.yml`). Конвеєр запускається під час кожного Pull Request, який змінює файли в теці `architecture/`:

```yaml
name: Architecture as Code CI

on:
  push:
    branches: [ main ]
    paths:
      - 'architecture/**'
  pull_request:
    branches: [ main ]
    paths:
      - 'architecture/**'

jobs:
  validate-and-render:
    name: Validate Architecture & Render Diagrams
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Structurizr CLI
        run: |
          mkdir -p structurizr
          curl -sSL https://github.com/structurizr/cli/releases/download/v2024.03.03/structurizr-cli.zip -o structurizr.zip
          unzip -q structurizr.zip -d structurizr
          sudo ln -s $(pwd)/structurizr/structurizr.sh /usr/local/bin/structurizr

      - name: Export Workspace to JSON
        run: |
          mkdir -p architecture/output
          structurizr export -w architecture/workspace.dsl -f json -o architecture/output/

      - name: Run Architecture Fitness Functions (Linter)
        run: |
          npm install -g ts-node typescript
          ts-node architecture/validator.ts

      - name: Export Diagrams to PlantUML and SVG
        run: |
          mkdir -p architecture/diagrams
          structurizr export -w architecture/workspace.dsl -f plantuml/c4plantuml -o architecture/diagrams/
          sudo apt-get update && sudo apt-get install -y plantuml
          plantuml -tsvg architecture/diagrams/*.puml

      - name: Publish Architecture Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: architecture-svg-diagrams
          path: architecture/diagrams/*.svg
```

---

## 5. Глибокий аналіз архітектурних фітнес-функцій

Чому традиційні модульні (Unit) та інтеграційні (E2E) тести не здатні замінити архітектурні фітнес-функції?
- **Модульні тести** перевіряють ізольовану логіку всередині окремої функції чи класу. Вони не бачать загальної топології системи та не знають, хто викликає цей клас.
- **Інтеграційні тести** перевіряють успішність проходження даних через ланцюжок викликів, але не контролюють легітимність самих каналів зв'язку. Якщо розробник фронтенду напряму підключиться до внутрішньої бази даних, E2E-тест успішно пройде, проте система отримає критичну діру в безпеці та порушення ізоляції даних.

Архітектурний лінтер аналізує **орієнтований граф залежностей** системи як цілісну структуру. Це дозволяє реалізувати розширені алгоритмічні перевірки:

### 5.1. Пошук циклічних залежностей (Circular Dependency Detection)
Наявність циклів між мікросервісами (коли сервіс А викликає сервіс Б, сервіс Б викликає сервіс В, а сервіс В знову викликає сервіс А) створює взаємні блокування (Deadlocks) та унеможливлює незалежне розгортання. За допомогою алгоритму пошуку в глибину (DFS) або алгоритму Тар'яна лінтер знаходить циклічні контури ще до написання коду.

### 5.2. Контроль глибини синхронних викликів (Call Depth Limits)
Ланцюжки синхронних викликів (HTTP/gRPC) довжиною понад 3–4 кроки суттєво збільшують хвостову латентність (Tail Latency) та призводять до каскадних збоїв. Лінтер автоматично перевіряє довжину синхронних шляхів у графі моделі та сигналізує про необхідність переходу на асинхронні події через брокер повідомлень (Kafka).

### 5.3. Інтеграція з Git Pre-commit Hooks
Щоб розробник отримував миттєвий зворотний зв'язок ще до відправки коду на сервер, валідатор можна підключити до локального Git-хука `.git/hooks/pre-commit`:

```bash
#!/bin/sh
# .git/hooks/pre-commit — локальна валідація архітектури
echo "🔍 Перевірка архітектурних інваріантів C4..."
structurizr export -w architecture/workspace.dsl -f json -o architecture/output/
python architecture/validator.py architecture/output/workspace.json

if [ $? -ne 0 ]; then
    echo "❌ Комміт відхилено: виявлено порушення архітектурних правил!"
    exit 1
fi
```

---

## 6. Практичні висновки та інженерна користь

Впровадження пайплайну «Архітектура як код» забезпечує відчутні переваги для команди:
1. **Автоматичний контроль архітектурних рішень:** Будь-яка спроба інженера створити пряме підключення між неавторизованими сервісами блокується ще на етапі перевірки коду в системі CI/CD.
2. **Завжди актуальна документація:** Діаграми у форматі SVG генеруються автоматично під час злиття коду в гілку `main` і публікуються на внутрішньому порталі документації.
3. **Версійний контроль архітектури:** Історія архітектурних змін зберігається безпосередньо в Git-історії у вигляді зрозумілих текстових diff-блоків.
4. **Усунення когнітивного розриву:** Розробники, архітектори та DevOps-інженери використовують одну й ту саму термінологію та єдину систему координат, усуваючи непорозуміння під час масштабування розподілених систем.
