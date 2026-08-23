# ⚙️ Автоматизований контролер архітектурних обмежений у CI/CD

Опис реалізації контролера **Architecture Fitness Harness** — тестового модуля, який запускається на етапі збирання у CI/CD та автоматично перевіряє архітектурні інваріанти системи. Контролер запобігає ерозії архітектури, блокуючи злиття коду, який порушує межі контекстів, перевищує ліміти затримок або випускає сервіси без маркерів спостережуваності.

Традиційний підхід до збереження архітектурної цілісності очікував, що архітектори особисто переглядатимуть кожен pull request. На практиці це створює вузьке місце, сповільнює розробку та призводить до пропускання людським оком непоміченої деградації. Автоматизований контролер Fitness Harness перетворює сухі вимоги архітектурного чеклиста на інженерні тести, які виконуються за секунди при кожному збиранні коду. Завдяки цьому архітектурні обмеження стають частиною автоматизованого тестового покриття, унеможливлюючи появу прихованого технічного боргу.

Застосування автоматичних гарнесів дозволяє втілити концепцію «архітектури як коду» (Architecture as Code). Замість зберігання правил у статичних PDF-файлах на корпоративній вікі, інженерні обмеження формалізуються у формі виконуваних модулів, які супроводжують вихідний код проєкту та розвиваються разом із ним.

## 1. Архітектурні інваріанти, що підлягають автоматичній перевірці

Перевірка архітектури в автоматичному режимі вимагає чіткого визначення математично вимірюваних правил. Модуль Fitness Harness зосереджується на трьох фундаментальних категоріях обмежень:

1. **Ізоляція доменних меж (Coupling Policy):** Суворі правила Clean Architecture або Hexagonal Architecture вимагають, щоб доменне ядро системи (`Domain`) залишалося чистим від технологічних деталей. Воно не повинно імпортувати або залежати від зовнішніх інфраструктурних бібліотек (`Infrastructure`), драйверів баз даних чи веб-фреймворків. Порушення цього правила призводить до неможливості ізольованого тестування бізнес-логіки та створює паразитне зчеплення. Контролер парсить дерева синтаксичних залежностей (AST) та блокує несанкціоновані імпорти.
2. **Бюджет затримок та мережевих таймаутів (Latency Budget):** Мережеві виклики між розподіленими сервісами є головним джерелом каскадних аварій. Контролер перевіряє, що жоден HTTP/gRPC виклик не залишається без явно вказаного таймауту (дозволений діапазон: від 1 до 1000 мс) та обов'язкового механізму Circuit Breaker для захисту від накопичення блокуючих сокетів.
3. **Маркери спостережуваності (Observability Compliance):** Для забезпечення простежуваності викликів у розподіленій трасувальній сітці кожен сервіс зобов'язаний витягувати та прокидати далі заголовки сквозного контексту (W3C Trace Context). Якщо сервіс губить заголовок `traceparent`, простежуваність запиту розривається, що унеможливлює швидкий пошук аномалій у продакшні.

Аналізатор зчитує граф залежностей проєкту, перевіряє наявність конфігураційних файлів та валідує вихідні початкові файли за допомогою синтаксичного деревоподібного аналізу (AST-parsing) або аналізу метаданих сервісного реєстру.

## 2. Крайові випадки та складні сценарії валідації

Під час автоматичного аналізу архітектури виникає низка крайніх випадків, які потребують спеціального опрацювання в коді гарнеса:

- **Динамічний імпорт та рефлексія:** Якщо розробник намагається обійти статичний аналіз за допомогою динамічного завантаження модулів (наприклад, `dlopen()` у C++ або `import()` у Node.js), гарнес прапорить відсутність статичного контракту як блокуючий ризик (`CriticalBlocker`).
- **Транзитивні залежності (Transitive Dependencies):** Доменний модуль може не імпортувати інфраструктуру напряму, але залежить від спільної бібліотеки `Shared`, яка у свою чергу імпортує драйвер бази даних. Гарнес виконує транзитивний обхід графа залежностей на всю глибину.
- **Непідтверджені таймаути в сторонніх SDK:** При використанні сторонніх клієнтських бібліотек (наприклад, AWS SDK або Redis Client) таймаути часто за замовчуванням встановлені у нескінченність (`0`). Контролер перевіряє файли конфігурації ініціалізації клієнтів і вимагає явного перевизначення таймаутів.

## 3. Простеження викликів та інтеграція з CI/CD

Процес валідації гарнесом розгортається у три послідовні фази:

```
[Фаза 1: Static Parsing] ──> [Фаза 2: Graph Evaluation] ──> [Фаза 3: Verdict Output]
   (Збір залежностей)           (Перевірка 4 правил)          (0 / 1 Exit Code)
```

На першій фазі гарнес зчитує всі вихідні файли та конфігураційні маніфести, будуючи орієнтований граф залежностей (Dependency DAG). На другій фазі до кожного вузла графа застосовуються правила ізоляції домену, лімітів затримок, Circuit Breakers та наявності контексту простежуваності. На третій фазі формується звіт. Якщо знайдено бодай один `CriticalBlocker`, процес завершується з кодом `1`, зупиняючи розгортання.

## 4. Реалізація контролера у CI/CD

Нижче наведено робочі реалізації тестового гарнеса двома мовами програмування: на C++20 для високопродуктивних системних модулів та на TypeScript для мікросервісного середовища Node.js. Обидва варіанти зчитають топологічну мапу сервісів і повертають суворий код помилки у разі виявлення критичних блокуючих порушень (`CriticalBlocker`).

:::tabs
```cpp
// FitnessHarness.cpp — Архітектурний контролер для C++20 / Backend
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <expected>
#include <memory>
#include <unordered_set>
#include <regex>

struct ServiceNode {
    std::string name;
    std::string layer; // "Domain", "Application", "Infrastructure"
    std::unordered_set<std::string> dependencies;
    bool has_circuit_breaker{false};
    double network_timeout_ms{0.0};
    bool has_w3c_tracing{false};
};

enum class ViolationSeverity { Warning, CriticalBlocker };

struct ArchitectureViolation {
    std::string rule_id;
    std::string message;
    ViolationSeverity severity;
};

class FitnessHarnessEvaluator {
public:
    explicit FitnessHarnessEvaluator(std::vector<ServiceNode> nodes)
        : nodes_(std::move(nodes)) {}

    [[nodiscard]] std::expected<void, std::vector<ArchitectureViolation>> evaluate_gate() const {
        std::vector<ArchitectureViolation> violations;

        for (const auto& node : nodes_) {
            // Крок 1. Перевірка інваріанта ізоляції доменного шару (Clean Architecture Gate)
            if (node.layer == "Domain") {
                for (const auto& dep : node.dependencies) {
                    if (dep.find("Infrastructure") != std::string::npos ||
                        dep.find("HttpAdapter") != std::string::npos) {
                        violations.push_back({
                            "RULE-01-DOMAIN-ISOLATION",
                            "Доменний модуль '" + node.name + "' імпортує інфраструктурний модуль '" + dep + "'",
                            ViolationSeverity::CriticalBlocker
                        });
                    }
                }
            }

            // Крок 2. Перевірка наявності Circuit Breaker та таймаутів при мережевих викликах
            if (!node.dependencies.empty()) {
                if (node.network_timeout_ms <= 0.0 || node.network_timeout_ms > 1000.0) {
                    violations.push_back({
                        "RULE-02-NETWORK-TIMEOUT-BUDGET",
                        "Сервіс '" + node.name + "' має небезпечний мережевий таймаут: " + 
                            std::to_string(node.network_timeout_ms) + " мс (дозволено: 1..1000 мс)",
                        ViolationSeverity::CriticalBlocker
                    });
                }
                if (!node.has_circuit_breaker) {
                    violations.push_back({
                        "RULE-03-CIRCUIT-BREAKER-MISSING",
                        "Зовнішні виклики в '" + node.name + "' не захищені Circuit Breaker",
                        ViolationSeverity::CriticalBlocker
                    });
                }
            }

            // Крок 3. Валідація спостережуваності (W3C Tracing)
            if (!node.has_w3c_tracing) {
                violations.push_back({
                    "RULE-04-OBSERVABILITY-TRACING",
                    "Відсутня простежуваність (W3C Trace Context) у сервісі '" + node.name + "'",
                    ViolationSeverity::Warning
                });
            }
        }

        if (has_critical_blockers(violations)) {
            return std::unexpected(violations);
        }
        return {};
    }

private:
    std::vector<ServiceNode> nodes_;

    static bool has_critical_blockers(const std::vector<ArchitectureViolation>& list) {
        for (const auto& v : list) {
            if (v.severity == ViolationSeverity::CriticalBlocker) {
                return true;
            }
        }
        return false;
    }
};

int main() {
    std::vector<ServiceNode> architecture_graph = {
        {"EnergyCoreDomain", "Domain", {"SharedUtils"}, true, 0.0, true},
        {"SmartLockAdapter", "Infrastructure", {"EnergyCoreDomain", "RedisDriver"}, true, 250.0, true},
        {"UnsafeGateway", "Application", {"InfrastructureHttpAdapter"}, false, 5000.0, false}
    };

    FitnessHarnessEvaluator evaluator(architecture_graph);
    auto result = evaluator.evaluate_gate();

    if (!result) {
        std::cerr << "[FITNESS HARNESS] ✖ АРХІТЕКТУРНИЙ ГЕЙТ НЕ ПРОЙДЕНО!\n";
        for (const auto& violation : result.error()) {
            std::cerr << "  - [" << violation.rule_id << "] " 
                      << (violation.severity == ViolationSeverity::CriticalBlocker ? "CRITICAL: " : "WARN: ")
                      << violation.message << "\n";
        }
        return 1;
    }

    std::cout << "[FITNESS HARNESS] ✔ Усі архітектурні інваріанти задоволено.\n";
    return 0;
}
```
```ts
// FitnessHarness.ts — Архітектурний контролер для TypeScript / Node.js / Microservices
import { readFileSync } from 'fs';

export interface ServiceSpec {
  name: string;
  layer: 'Domain' | 'Application' | 'Infrastructure';
  dependencies: string[];
  circuitBreakerEnabled: boolean;
  networkTimeoutMs: number;
  w3cTracingEnabled: boolean;
}

export interface RuleViolation {
  ruleId: string;
  message: string;
  isBlocker: boolean;
}

export class ArchitectureFitnessChecker {
  constructor(private readonly services: ServiceSpec[]) {}

  public validateArchitecture(): { passed: boolean; violations: RuleViolation[] } {
    const violations: RuleViolation[] = [];

    for (const service of this.services) {
      // 1. Clean Architecture boundary enforcement
      if (service.layer === 'Domain') {
        const forbiddenDep = service.dependencies.find(
          (dep) => dep.includes('Infrastructure') || dep.includes('HttpAdapter')
        );
        if (forbiddenDep) {
          violations.push({
            ruleId: 'RULE-01-DOMAIN-ISOLATION',
            message: `Доменний сервіс ${service.name} прямо залежить від ${forbiddenDep}`,
            isBlocker: true,
          });
        }
      }

      // 2. Resilience and Timeout budget
      if (service.dependencies.length > 0) {
        if (service.networkTimeoutMs > 1000 || service.networkTimeoutMs <= 0) {
          violations.push({
            ruleId: 'RULE-02-TIMEOUT-BUDGET',
            message: `Сервіс ${service.name} перевищує ліміт затримки: ${service.networkTimeoutMs}мс`,
            isBlocker: true,
          });
        }
        if (!service.circuitBreakerEnabled) {
          violations.push({
            ruleId: 'RULE-03-CIRCUIT-BREAKER',
            message: `Сервіс ${service.name} не має Circuit Breaker для зовнішніх викликів`,
            isBlocker: true,
          });
        }
      }

      // 3. Observability tracing context
      if (!service.w3cTracingEnabled) {
        violations.push({
          ruleId: 'RULE-04-TRACING-CONTEXT',
          message: `Втрачено W3C Trace Context у сервісі ${service.name}`,
          isBlocker: false,
        });
      }
    }

    const hasBlockers = violations.some((v) => v.isBlocker);
    return { passed: !hasBlockers, violations };
  }
}
```
:::

## 5. Інтеграція та робочий процес у CI/CD Конвеєрі

Модуль Fitness Harness підключається на етапі статичного аналізу перед запуском важких інтеграційних тестів. Завдяки цьому інженери отримують швидкий зворотний зв'язок (Feedback Loop) тривалістю в кілька секунд, не чекаючи на повну збірку контейнерів.

Послідовність виконання у конвеєрі виглядає так:

```
[Git Push / PR] ──> [Static Dependency Parser] ──> [Fitness Harness Executable]
                                                           │
                                   ┌───────────────────────┴───────────────────────┐
                                   ▼                                               ▼
                         [Блокуючі порушення]                           [Інваріанти задоволено]
                                   │                                               │
                                   ▼                                               ▼
                        [CI Fail & Slack Alert]                        [Запуск Integration Tests]
```

Якщо гарнес виявляє попередження (`Warning`), вони додаються до підсумкового звіту про розгортання, але не зупиняють реліз. Якщо ж знайдено принаймні одне критичне блокуюче порушення (`CriticalBlocker`), CI/CD зупиняє конвеєр із кодом повернення `1`. Практика автоматизації таких перевірок повністю виключає можливість випадкового потрапляння небезпечних конфігурацій чи некоректних залежностей у продуктивне середовище.
