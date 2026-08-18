# ⚙️ Автоматизований fitness-контроль ерозії коду та схем у CI/CD

Під час масштабної еволюційної міграції гео-розподіленої платформи з монолітної версії v1 у мікросервісну v2-архітектуру головною загрозою для цілісності платформи стає непомітна ерозія (лат. *erosio* — роз'їдання) кодових меж. Коли сотні інженерів паралельно випускають продуктивні фічі, деплоять прапорці міграції та переписують внутрішні адаптери даних, у коді неминуче виникають негативні обходи. Розробники нових v2-мікросервісів під тиском дедлайнів починають напряму підключати легасі-заголовочні файли PostgreSQL-моделей, оминати абстрактний кодовий шов `DeviceTwinRepository` або ігнорувати передачу обов'язкових версійних заголовків когерентності.

Ця вставка містить повністю функціональний інженерний практикум з побудови автоматизованого контуру архітектурного контролю (англ. *Architecture Fitness Guard*). Ми розберемо створення статичних аналізаторів меж шарів мовами C++20 та Python, автоматичні валідатори зворотної сумісності схем подій Kafka Outbox, а також повну конфігурацію конвеєра CI/CD, який діє як суворий машиний вартовий і блокує деплой при виявленні найменшого архітектурного дрейфу.

---

## 1. Концепція архітектурних функцій пристосованості (Fitness Functions)

Архітектурна функція пристосованості (англ. *Architectural Fitness Function*) — це автоматизований тест або перевірка, яка вимірює відповідність реалізованого коду задуманим архітектурним обмеженням. Поняття прийшло з еволюційних обчислень і було адаптовано для програмної архітектури Нілом Фордом, Ребеккою Парсонс та Патріком Куа.

У контексті міграції Digital Homes v1 → v2 фітнес-функції вирішують три критичні завдання:

1. **Захист абстрактного кодового шва**: Заборонити будь-якому коду v2 звертатися до легасі-модулів `dh::v1::legacy_db` або безпосередньо до PostgreSQL v1. Усі мутації стану мають ходити виключно через шов `DeviceTwinRepository`.
2. **Контроль інваріантів схем даних**: Гарантувати, що кожна подія зміни стану твіна у Kafka містить суворо монотонне поле `versionSeq`, унікальний `eventId` та валідний формат `etag`.
3. **Запобігання циклам залежностей**: Перевіряти, що нові доменні мікросервіси (Notif, Analytics, Automation) не створюють циклічних включень між собою та платформеними бібліотеками.

---

## 2. Аналіз кодових меж C++20: Захист абстрактного шва

У високонавантажених компонентах Digital Homes (наприклад, у регіональних Fleet Routers та сервісі твіна) кодова база written у C++20. Для перевірки дотримання меж шарів аналізатор сканує дерево вихідних файлів, будує граф включень `#include` та звіряє його із матрицею дозволених залежностей.

### 2.1 Механіка роботи C++ аналізатора

Аналізатор відкриває кожен файл `.cpp` та `.hpp`, виділяє регулярним виразом директиви препроцесора `#include` та аналізує відносний шлях. Якщо файл знаходиться в каталозі `src/v2/` або `src/services/twin/`, але включає заголовки з `src/v1/legacy_db/` чи прямо використовує `postgres_raw_client.hpp`, аналізатор реєструє порушення `LAYER_VIOLATION`.

Нижче наведено ідіоматичні реалізації перевірника мовами C++20 та Python.

:::tabs
```cpp
// fitness_checker.cpp — Статичний перевірник архітектурних меж C++20
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <filesystem>
#include <regex>
#include <set>
#include <map>
#include <stdexcept>

namespace fs = std::filesystem;

struct Violation {
    std::string source_file;
    std::size_t line_number;
    std::string included_header;
    std::string rule_name;
};

class ArchitectureFitnessGuard {
public:
    explicit ArchitectureFitnessGuard(fs::path root_dir) : root_dir_(std::move(root_dir)) {}

    // Заборона включення легасі-заголовків із зазначених каталогів
    void add_forbidden_rule(std::string source_pattern, std::string forbidden_header_substring) {
        forbidden_rules_.push_back({std::move(source_pattern), std::move(forbidden_header_substring)});
    }

    std::vector<Violation> inspect_codebase() {
        std::vector<Violation> violations;
        std::regex include_regex(R"#(^\s*#include\s*["<]([^">]+)[">])#");

        for (const auto& entry : fs::recursive_directory_iterator(root_dir_)) {
            if (!entry.is_regular_file()) continue;
            auto ext = entry.path().extension().string();
            if (ext != ".cpp" && ext != ".hpp" && ext != ".h" && ext != ".cc") continue;

            std::string rel_path = fs::relative(entry.path(), root_dir_).string();
            std::replace(rel_path.begin(), rel_path.end(), '\\', '/');

            std::ifstream file(entry.path());
            std::string line;
            std::size_t line_num = 0;

            while (std::getline(file, line)) {
                ++line_num;
                std::smatch match;
                if (std::regex_search(line, match, include_regex)) {
                    std::string header = match[1].str();

                    for (const auto& rule : forbidden_rules_) {
                        if (rel_path.find(rule.source_pattern) != std::string::npos &&
                            header.find(rule.forbidden_substring) != std::string::npos) {
                            violations.push_back({
                                rel_path,
                                line_num,
                                header,
                                "LAYER_VIOLATION: v2 code cannot include legacy v1 db headers"
                            });
                        }
                    }
                }
            }
        }
        return violations;
    }

private:
    struct Rule {
        std::string source_pattern;
        std::string forbidden_substring;
    };

    fs::path root_dir_;
    std::vector<Rule> forbidden_rules_;
};

int main(int argc, char* argv[]) {
    try {
        fs::path repo_root = (argc > 1) ? argv[1] : fs::current_path();
        ArchitectureFitnessGuard guard(repo_root);

        // Налаштування суворих архітектурних правил міграції
        guard.add_forbidden_rule("src/v2/", "v1/legacy_db/");
        guard.add_forbidden_rule("src/v2/", "postgres_raw_client.hpp");
        guard.add_forbidden_rule("src/services/twin/", "monolith_shared_state.h");

        std::cout << "[FITNESS GUARD] Запуск аналізу меж коду в: " << repo_root << std::endl;
        auto violations = guard.inspect_codebase();

        if (!violations.empty()) {
            std::cerr << "\n❌ ВИЯВЛЕНО ЕРОЗІЮ АРХІТЕКТУРИ (" << violations.size() << " порушень):\n";
            for (const auto& v : violations) {
                std::cerr << "  • " << v.source_file << ":" << v.line_number 
                          << " -> включено '" << v.included_header << "' [" << v.rule_name << "]\n";
            }
            return 1;
        }

        std::cout << "✅ [FITNESS GUARD] Ерозії коду не виявлено. Усі шви архітектури дотримано.\n";
        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання перевірника: " << ex.what() << std::endl;
        return 2;
    }
}
```
```python
# fitness_checker.py — Ідіоматичний Python-еквівалент аналізатора AST для Python/C++ коду
import os
import re
import sys
from pathlib import Path
from typing import List, NamedTuple

class Violation(NamedTuple):
    source_file: str
    line_number: int
    included_header: str
    rule_name: str

class PythonArchitectureGuard:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.rules = []

    def add_rule(self, source_pattern: str, forbidden_substring: str):
        self.rules.append((source_pattern, forbidden_substring))

    def inspect(self) -> List[Violation]:
        violations = []
        include_regex = re.compile(r'^\s*(?:#include\s*["<]([^">]+)[">]|from\s+([\w\.]+)\s+import|import\s+([\w\.]+))')

        for file_path in self.root_dir.rglob('*'):
            if file_path.suffix not in ('.py', '.cpp', '.hpp', '.h', '.cc'):
                continue

            rel_path = file_path.relative_to(self.root_dir).as_posix()

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        match = include_regex.search(line)
                        if match:
                            target = match.group(1) or match.group(2) or match.group(3)
                            for src_pat, forbidden in self.rules:
                                if src_pat in rel_path and forbidden in target:
                                    violations.append(Violation(
                                        source_file=rel_path,
                                        line_number=line_num,
                                        included_header=target,
                                        rule_name="LAYER_VIOLATION: Strict separation v2 from v1"
                                    ))
            except Exception as e:
                print(f"Помилка читання файла {rel_path}: {e}", file=sys.stderr)

        return violations

if __name__ == '__main__':
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    guard = PythonArchitectureGuard(root)
    guard.add_rule("src/v2/", "v1/legacy_db")
    guard.add_rule("src/v2/", "postgres_raw_client")
    
    found_violations = guard.inspect()
    if found_violations:
        print(f"❌ ВИЯВЛЕНО ЕРОЗІЮ АРХІТЕКТУРИ ({len(found_violations)} порушень):", file=sys.stderr)
        for v in found_violations:
            print(f"  • {v.source_file}:{v.line_number} -> '{v.included_header}'", file=sys.stderr)
        sys.exit(1)
    
    print("✅ [FITNESS GUARD] Усі архітектурні межі чисто дотримано.")
    sys.exit(0)
```
:::

---

## 3. Валідація схем подій Kafka Outbox та монотонності версій

Другим критичним вектором ерозії під час міграції є дрейф схем даних у Kafka топіку `dh.twin.events.v1`. Якщо розробник додає поле в JSON-подію без дотримання зворотної сумісності (англ. *backward compatibility*) або пропускає монотонне число `versionSeq`, матеріалізовані представлення Read Model у v2 аварійно зупиняться.

### 3.1 Правила еволюції схем подій

1. **Обов'язковість версійних полів**: Кожна подія оновлення стану мусить містити суворо монотонний 64-бітний цілочисельний лічильник `versionSeq` для даного `homeId`.
2. **Заборона видалення полів (No Destructive Changes)**: Існуючі поля не можна видаляти або змінювати їхній тип даних. Дозволяється лише додавання нових опціональних полів.
3. **Строгий формат ідентифікаторів**: `homeId` мусить відповідати виразу `^home-[0-9]+$`, а `eventId` — виразу `^evt-[a-f0-9]{8}$`.

Нижче наведено Python-модуль валідації JSON Schema контрактів подій у CI/CD.

```python
# schema_fitness_validator.py — Перевірка схем подій та контракту когерентності
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator, ValidationError

TWIN_EVENT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["eventId", "homeId", "deviceId", "versionSeq", "etag", "observedAtMs", "payload"],
    "properties": {
        "eventId": {"type": "string", "pattern": "^evt-[a-f0-9]{8}$"},
        "homeId": {"type": "string", "pattern": "^home-[0-9]+$"},
        "deviceId": {"type": "string"},
        "versionSeq": {"type": "integer", "minimum": 1},
        "etag": {"type": "string", "pattern": "^W/\"v[0-9]+-[a-f0-9]+\"$"},
        "observedAtMs": {"type": "integer", "minimum": 1700000000000},
        "payload": {
            "type": "object",
            "required": ["state"],
            "properties": {
                "state": {"type": "object"}
            }
        }
    },
    "additionalProperties": False
}

def validate_event_samples(schema_dir: Path) -> int:
    validator = Draft202012Validator(TWIN_EVENT_SCHEMA)
    errors_count = 0

    print(f"[SCHEMA VALIDATOR] Сканування зразків подій у: {schema_dir}")
    for json_file in schema_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                sample_data = json.load(f)

            errors = list(validator.iter_errors(sample_data))
            if errors:
                errors_count += len(errors)
                print(f"❌ Файл {json_file.name} не відповідає контракту v2:")
                for err in errors:
                    print(f"   • Шлях '{err.json_path}': {err.message}")
            else:
                print(f"  ✓ {json_file.name} — підтверджено")

        except Exception as ex:
            errors_count += 1
            print(f"❌ Некоректний JSON у {json_file.name}: {ex}")

    return errors_count

if __name__ == '__main__':
    target_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("schemas/samples")
    if not target_dir.exists():
        print(f"Каталог {target_dir} не знайдено, створюємо базову перевірку...")
        sys.exit(0)

    total_errors = validate_event_samples(target_dir)
    if total_errors > 0:
        print(f"\n❌ ЗНАЙДЕНО {total_errors} ПОМИЛОК У СХЕМАХ ПОДІЙ! CI БЛОКОВАНО.")
        sys.exit(1)
    
    print("\n✅ Схеми подій v2 повністю відповідають контракту.")
    sys.exit(0)
```

---

## 4. Конфігурація CI/CD конвеєра (GitHub Actions & GitLab CI)

Для перетворення фітнес-функцій на автоматичні ворота складання їх додають у конвеєр безперервної інтеграції. Будь-яка спроба створити Pull Request, який порушує межі шарів або схеми подій, зупиняється на етапі CI з поверненням ненульового коду виходу `exit 1`.

### 4.1 Конфігурація GitHub Actions Workflow

```yaml
# .github/workflows/architecture-fitness-guard.yml
name: Architecture Fitness Guard

on:
  push:
    branches: [ main, release/* ]
  pull_request:
    branches: [ main, release/* ]

jobs:
  fitness-check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up C++ Build Environment
        run: |
          sudo apt-get update
          sudo apt-get install -y cmake g++

      - name: Compile Fitness Guard Checker
        run: |
          g++ -std=c++20 -O2 guide/progarch/legacy-and-evolution/dh-cloud-v2/proj-fitness-guard/fitness_checker.cpp -o fitness_checker

      - name: Execute C++ Layer Boundary Check
        run: |
          ./fitness_checker .

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Python Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install jsonschema

      - name: Validate Kafka Outbox Event Schemas
        run: |
          python guide/progarch/legacy-and-evolution/dh-cloud-v2/proj-fitness-guard/schema_fitness_validator.py schemas/events
```

### 4.2 Конфігурація GitLab CI Pipeline

```yaml
# .gitlab-ci.yml — Етап перевірки архітектурного здоров'я
stages:
  - architecture-guard
  - build
  - test

architecture-fitness-job:
  stage: architecture-guard
  image: gcc:13
  script:
    - g++ -std=c++20 -O2 guide/progarch/legacy-and-evolution/dh-cloud-v2/proj-fitness-guard/fitness_checker.cpp -o fitness_checker
    - ./fitness_checker .
    - apt-get update && apt-get install -y python3-pip
    - pip3 install jsonschema
    - python3 guide/progarch/legacy-and-evolution/dh-cloud-v2/proj-fitness-guard/schema_fitness_validator.py schemas/events
  only:
    - merge_requests
    - main
```

---

## 5. Крайові випадки та обхідні шляхи: Коли правила вимагають винятків

У реальних проєктах виникають ситуації, коли тимчасовий доступ з v2 до v1 є неминучим (наприклад, під час ліквідації аварійного збою на Фазі 2 міграції). Для запобігання перетворенню фітнес-функцій на догматичний бар'єр застосовується паттерн **Architecture Exception Registry (Реєстр архітектурних винятків)**.

Тимчасовий виняток оформлюється у спеціальному конфігураційному файлі `.architecture-exceptions.json` із вказанням конкретного автора, посилання на таску у Jira та суворого терміну дії (англ. *Expiration Date*):

```json
[
  {
    "exceptionId": "EXC-2026-08-01",
    "sourceFile": "src/v2/emergency_fallback.cpp",
    "allowedHeader": "v1/legacy_db/postgres_raw_client.hpp",
    "approvedBy": "architect-lead@digitalhomes.io",
    "jiraTicket": "DH-4912",
    "expiresAt": "2026-09-30",
    "reason": "Захисний Fallback читання під час Фази 2 міграції Твіна"
  }
]
```

Якщо аналізатор знаходить порушення, яке включено до реєстру винятків, і термін дії винятку `expiresAt` ще не минув, перевірка завершується попередженням `WARNING` замість блокування збірки `FAIL`. Щойно дата винятку минає, фітнес-функція автоматично почне валити збірку, примушуючи команду своєчасно прибирати тимчасові обходи.

---

## 6. Підсумкова матриця контролю ерозії коду та схем

| Компонент контролю | Інструмент / Метод | Час виконання | Реакція на порушення |
| :--- | :--- | :--- | :--- |
| **Межі шарів C++** | AST `#include` checker | Git PR / CI Pipeline | `Exit 1` — Блокування Merge |
| **Сумісність схем Kafka** | JSON Schema Validator | Git PR / CI Pipeline | `Exit 1` — Блокування Merge |
| **Реєстр винятків** | `.architecture-exceptions.json` | Щоденний Cron | `Warning` / `Fail` при простроченні |
| **Дрейф у продакшені** | Prometheus metrics probe | Runtime Telemetry | Alert у PagerDuty / Slack |

Побудований контур автоматизованого контролю перетворює теоретичні архітектурні правила на дієвий машиний конвеєр, гарантуючи, що гео-розподілена v2-архітектура Digital Homes збереже чистоту своїх меж протягом усього життєвого циклу еволюції.
