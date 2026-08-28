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
:::code proj-fitness-guard/cpp/fitness_checker.cpp
:::code proj-fitness-guard/py/fitness_checker.py
:::

---

## 3. Валідація схем подій Kafka Outbox та монотонності версій

Другим критичним вектором ерозії під час міграції є дрейф схем даних у Kafka топіку `dh.twin.events.v1`. Якщо розробник додає поле в JSON-подію без дотримання зворотної сумісності (англ. *backward compatibility*) або пропускає монотонне число `versionSeq`, матеріалізовані представлення Read Model у v2 аварійно зупиняться.

### 3.1 Правила еволюції схем подій

1. **Обов'язковість версійних полів**: Кожна подія оновлення стану мусить містити суворо монотонний 64-бітний цілочисельний лічильник `versionSeq` для даного `homeId`.
2. **Заборона видалення полів (No Destructive Changes)**: Існуючі поля не можна видаляти або змінювати їхній тип даних. Дозволяється лише додавання нових опціональних полів.
3. **Строгий формат ідентифікаторів**: `homeId` мусить відповідати виразу `^home-[0-9]+$`, а `eventId` — виразу `^evt-[a-f0-9]{8}$`.

Нижче наведено Python-модуль валідації JSON Schema контрактів подій у CI/CD.

:::code proj-fitness-guard/py/schema_fitness_validator.py

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
          g++ -std=c++20 -O2 root/course/progarch/dh-cloud-v2/proj-fitness-guard/fitness_checker.cpp -o fitness_checker

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
          python root/course/progarch/dh-cloud-v2/proj-fitness-guard/schema_fitness_validator.py schemas/events
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
    - g++ -std=c++20 -O2 root/course/progarch/dh-cloud-v2/proj-fitness-guard/fitness_checker.cpp -o fitness_checker
    - ./fitness_checker .
    - apt-get update && apt-get install -y python3-pip
    - pip3 install jsonschema
    - python3 root/course/progarch/dh-cloud-v2/proj-fitness-guard/schema_fitness_validator.py schemas/events
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
