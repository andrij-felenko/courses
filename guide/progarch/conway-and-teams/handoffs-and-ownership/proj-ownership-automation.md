# ⚙️ Автоматизація правил володіння та контрактного гейтингу

Ручні передачі відповідальності, бюрократичні узгодження в тикет-системах та ручні перевірки міжкомандних межових умов створюють затримки в релізах тривалістю в дні або тижні. Коли для внесення правки у чужий сервіс розробник змушений створювати тикет у Jira і чекати тижневого ревю від іншої команди, потік розробки зупиняється.

Автоматизований контрактний гейтинг усуває людський фактор і ручне очікування: замість бюрократичних листувань репозиторій містить чіткі декларативні правила володіння (`CODEOWNERS`) та інструмент автоматичної перевірки контрактів у CI/CD-конвеєрі. Якщо внесена сторонньою командою зміна не порушує публічний API-контракт і відповідає автоматичним тестам, злиття дозволяється миттєво.

У цьому матеріалі ми розберемо архітектуру та створення легкого високоефективного двигуна перевірки володіння кодом та контрактів, який інтегрується в CI/CD-конвеєр і реалізує модель InnerSource.

## 1. Архітектурна задача та концепція режиму володіння

У сучасних мультисервісних системах (наприклад, платформі розумного дому Digital Homes) кодова база складається з компонентів різного ступеня ризику:
- **Критичні ядра високого ризику** (модулі шифрування, обробка персональних даних, криптографія, механізми автентифікації). Будь-яке випадкове редагування тут може призвести до катастрофічної вразливості або фінансових збитків.
- **Стандартні бізнес-сервіси та телеметрія** (сервіси збору даних сенсорів, сповіщення, аналітика тарифів). Зміни тут потрібні багатьом продуктовим командам щодня.

Для автоматизації перевірки введено два основні режими володіння для кожного шлях у репозиторії:
1. `STRONG` (Жорстке володіння): Модифікувати файли може лише команда-власник. Будь-який сторонній Pull Request обов'язково заблоковано до отримання ручного підпису хранителя (*steward*).
2. `INNER_SOURCE` (Слабке володіння): Будь-яка команда компанії має право внести зміну через PR. Схвалення надається **автоматично**, якщо зміна пройдено автоматизовані перевірки API-контракту та інтеграційні тести.

## 2. Послідовність роботи двигуна перевірки (Execution Flow)

Під час запуску в CI/CD конвеєрі утиліта виконує наступні етапи:
1. Завантажує таблицю правил володіння з маніфесту `CODEOWNERS`.
2. Отримує список змінених файлів із поточного Pull Request.
3. Для кожного файлу шукає найспецифічніше правило за принципом найдовшого збігу префікса шляху (Longest Prefix Match).
4. Отримує список команд, до яких належить автор PR.
5. Обчислює вердикт для файлу:
   - `VERDICT_ALLOW`: Автор є членом команди-власника — злиття дозволено.
   - `VERDICT_NEED_REVIEW`: Потрібен ручний підпис хранителя (режим `STRONG` або злам контракту).
   - `VERDICT_REJECT`: Виявлено прямо заборонену операцію (наприклад, видалення поля з мажоритарного контракту сторонньою командою).

## 3. Промислова реалізація двигуна перевірки

Нижче наведено робочий кодовий приклад двигуна перевірки правил володіння та контрактів мовами C та C++.

Обидві версії реалізують ідентичну логіку оцінки префіксного збігу та перевірки прав автора, але демонструють ідіоматичні підходи відповідних мов: версія на C використовує явне управління пам'яттю та структурні масиви, тоді як версія C++ спирається на семантику RAII, тип `std::string_view` для уникнення алокацій при роботі з підрядками та суворі строгі перелічення `enum class`.

:::tabs
```c
/* c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

typedef enum {
    OWNERSHIP_STRONG,
    OWNERSHIP_INNER_SOURCE
} OwnershipMode;

typedef enum {
    VERDICT_ALLOW,
    VERDICT_NEED_REVIEW,
    VERDICT_REJECT
} Verdict;

typedef struct {
    char path_prefix[128];
    char owner_team[64];
    OwnershipMode mode;
} OwnershipRule;

typedef struct {
    OwnershipRule *rules;
    size_t count;
    size_t capacity;
} RuleTable;

RuleTable* rule_table_create(size_t capacity) {
    RuleTable *table = (RuleTable*)malloc(sizeof(RuleTable));
    if (!table) return NULL;
    table->rules = (OwnershipRule*)malloc(sizeof(OwnershipRule) * capacity);
    if (!table->rules) {
        free(table);
        return NULL;
    }
    table->count = 0;
    table->capacity = capacity;
    return table;
}

void rule_table_destroy(RuleTable *table) {
    if (!table) return;
    free(table->rules);
    free(table);
}

bool rule_table_add(RuleTable *table, const char *prefix, const char *owner, OwnershipMode mode) {
    if (!table || table->count >= table->capacity) return false;
    OwnershipRule *r = &table->rules[table->count++];
    strncpy(r->path_prefix, prefix, sizeof(r->path_prefix) - 1);
    r->path_prefix[sizeof(r->path_prefix) - 1] = '\0';
    strncpy(r->owner_team, owner, sizeof(r->owner_team) - 1);
    r->owner_team[sizeof(r->owner_team) - 1] = '\0';
    r->mode = mode;
    return true;
}

Verdict evaluate_file_change(const RuleTable *table, const char *file_path, 
                             const char *author_team, bool is_contract_broken) {
    if (!table || !file_path || !author_team) return VERDICT_REJECT;

    const OwnershipRule *best_rule = NULL;
    size_t max_match_len = 0;

    /* Пошук найспецифічнішого правила за принципом найдовшого збігу префікса */
    for (size_t i = 0; i < table->count; ++i) {
        const char *p = table->rules[i].path_prefix;
        size_t len = strlen(p);
        if (strncmp(file_path, p, len) == 0 && len > max_match_len) {
            max_match_len = len;
            best_rule = &table->rules[i];
        }
    }

    /* Якщо шлях не захищено жодним правилом — дозволяємо автоматично */
    if (!best_rule) {
        return VERDICT_ALLOW;
    }

    /* Якщо автор є членом команди-власника — повний доступ */
    if (strcmp(author_team, best_rule->owner_team) == 0) {
        return VERDICT_ALLOW;
    }

    /* Перевірка для сторонніх авторів (InnerSource контриб'юторів) */
    if (best_rule->mode == OWNERSHIP_STRONG) {
        return VERDICT_NEED_REVIEW;
    }

    /* Режим INNER_SOURCE: перевіряємо цілісність контракту */
    if (is_contract_broken) {
        return VERDICT_REJECT; /* Злам API-контракту стороннім автором заборонено */
    }

    return VERDICT_NEED_REVIEW; /* Автоматичне схвалення після CI перевірок */
}

int main(void) {
    RuleTable *table = rule_table_create(10);
    if (!table) return 1;

    rule_table_add(table, "src/core/crypto/", "sec-team", OWNERSHIP_STRONG);
    rule_table_add(table, "src/services/telemetry/", "platform-team", OWNERSHIP_INNER_SOURCE);

    printf("Test 1 (Owner PR): %d\n", 
           evaluate_file_change(table, "src/core/crypto/sha256.c", "sec-team", false));
    printf("Test 2 (External PR Strong): %d\n", 
           evaluate_file_change(table, "src/core/crypto/sha256.c", "billing-team", false));
    printf("Test 3 (InnerSource PR Contract OK): %d\n", 
           evaluate_file_change(table, "src/services/telemetry/ingest.c", "billing-team", false));
    printf("Test 4 (InnerSource PR Contract Broken): %d\n", 
           evaluate_file_change(table, "src/services/telemetry/ingest.c", "billing-team", true));

    rule_table_destroy(table);
    return 0;
}
```
```cpp
// cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <algorithm>

enum class OwnershipMode {
    Strong,
    InnerSource
};

enum class Verdict {
    Allow,
    NeedReview,
    Reject
};

struct OwnershipRule {
    std::string path_prefix;
    std::string owner_team;
    OwnershipMode mode;
};

class OwnershipEngine {
public:
    void add_rule(std::string_view prefix, std::string_view owner, OwnershipMode mode) {
        rules_.push_back({std::string(prefix), std::string(owner), mode});
    }

    [[nodiscard]] Verdict evaluate_change(std::string_view file_path,
                                         std::string_view author_team,
                                         bool is_contract_broken) const noexcept {
        const OwnershipRule* best_rule = nullptr;
        size_t max_match_len = 0;

        for (const auto& rule : rules_) {
            if (file_path.starts_with(rule.path_prefix) && rule.path_prefix.length() > max_match_len) {
                max_match_len = rule.path_prefix.length();
                best_rule = &rule;
            }
        }

        if (!best_rule) {
            return Verdict::Allow;
        }

        if (author_team == best_rule->owner_team) {
            return Verdict::Allow;
        }

        if (best_rule->mode == OwnershipMode::Strong) {
            return Verdict::NeedReview;
        }

        if (is_contract_broken) {
            return Verdict::Reject;
        }

        return Verdict::NeedReview;
    }

private:
    std::vector<OwnershipRule> rules_;
};

int main() {
    OwnershipEngine engine;
    engine.add_rule("src/core/crypto/", "sec-team", OwnershipMode::Strong);
    engine.add_rule("src/services/telemetry/", "platform-team", OwnershipMode::InnerSource);

    std::cout << "Test 1 (Owner PR): " 
              << static_cast<int>(engine.evaluate_change("src/core/crypto/sha256.cpp", "sec-team", false)) << "\n";
    std::cout << "Test 2 (External PR Strong): " 
              << static_cast<int>(engine.evaluate_change("src/core/crypto/sha256.cpp", "billing-team", false)) << "\n";
    std::cout << "Test 3 (InnerSource PR Contract OK): " 
              << static_cast<int>(engine.evaluate_change("src/services/telemetry/ingest.cpp", "billing-team", false)) << "\n";
    std::cout << "Test 4 (InnerSource PR Contract Broken): " 
              << static_cast<int>(engine.evaluate_change("src/services/telemetry/ingest.cpp", "billing-team", true)) << "\n";

    return 0;
}
```
:::

## 4. Інтеграція у конвеєр GitHub Actions / GitLab CI

Автоматичний двигун викликається як перший крок у конвеєрі CI під час створення або оновлення Pull Request.

Нижче наведено конфігурацію workflow GitHub Actions, яка запускає перевірку володіння кодом та контрактний тестувальник:

```yaml
name: Ownership and Contract Gate

on:
  pull_request:
    branches: [ main, develop ]

jobs:
  ownership-check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Get changed files
        id: changed-files
        uses: tj-actions/changed-files@v41

      - name: Run OpenAPI Contract Validator
        id: contract-validator
        run: |
          npx @openapitools/openapi-generator-cli validate -i api/contracts/telemetry-v1.yaml
          echo "contract_ok=true" >> $GITHUB_OUTPUT

      - name: Build Ownership Engine
        run: |
          g++ -O3 -std=c++20 src/tools/ownership_gate.cpp -o ownership_gate

      - name: Evaluate Ownership Rules
        run: |
          ./ownership_gate --files="${{ steps.changed-files.outputs.all_changed_files }}" \
                           --author="${{ github.actor }}" \
                           --contract-ok="${{ steps.contract-validator.outputs.contract_ok }}"
```

## 5. Типові пастки та крайові випадки при автоматизації володіння

При впровадженні автоматичного гейтингу володіння кодом компанії регулярно стикаються з п'ятьма архітектурними пастками:

1. **Мертві правила володіння у `CODEOWNERS`**: Коли розробники змінюють команди або звільняються, правила володіння перетворюються на «білі плями» або посилаються на неіснуючі групи. **Рішення**: CI-конвеєр повинен щотижня запускати лінтер маніфесту володіння, перевіряючи актуальність усіх вказаних групових псевдонімів у LDAP/GitHub.
2. **Пастка тотального `STRONG` режиму**: Спроба позначити всі директорії репозиторію як `STRONG` відтворює традиційні міжкомандні заторні черги. Режим `STRONG` має застосовуватися виключно до точок високого архітектурного ризику (не більше 10–15% кодової бази). Решта 85% коду повинна перебувати у режимі `INNER_SOURCE`.
3. **Забіг умовної швидкості (Race Conditions при паралельних PR)**: Дві сторонні команди одночасно надсилають InnerSource PR у той самий сервіс. Обидва PR окремо проходять автоматичні тести, але після злиття першого з них другий зламає контракт. **Рішення**: Використання черг злиття (Merge Queues або Bors/GitHub Merge Queue), які автоматично ребейзять та повторно запускають контрактний гейтинг над тимчасовою гілкою злиття.
4. **Відсутність процедури аварійного обходу (Break-Glass Policy)**: У випадку критичного інциденту в продакшні (P0 Incident) підпис хранителя або тривалий CI-конвеєр блокує терміновий хотфікс. **Рішення**: Підтримка механізму «аварійного обходу» з обов'язковим автоматичним пост-аудитом на наступний день.
5. **Проблема неявних залежностей**: Стороння команда не змінює сам сервіс, але змінює конфігураційне поле в діалекті сховища, що спричиняє краш сервісу на рантаймі. **Рішення**: Розширення контрактного гейтингу на маніфести конфігурацій та схеми баз даних через автоматизований статичний аналіз залежностей.
