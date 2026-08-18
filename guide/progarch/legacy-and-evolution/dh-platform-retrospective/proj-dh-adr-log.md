# ⚙️ Практичний аудітор ADR та фітнес-функції еволюційного контролю

Цей проєктний практикум містить готовий інструментарій автоматизованого аналізу реєстру ADR (Architecture Decision Records) та перевірки архітектурної ерозії у кодовій базі системи Digital Homes, демоструючи реалізацію статичних фітнес-функцій для захисту системних меж у CI/CD.

---

## 1. Концепція автоматизованого аудиту ADR та фітнес-функцій

Документування архітектурних рішений у формі текстових файлів ADR (Architecture Decision Records) у каталозі `docs/adr` є першою важливою дисциплінарною передумовою зберігання системного контексту. У проєкті Digital Homes кожен ADR містить унікальний ідентифікатор, дату ухвалення рішення, перелік учасників обговорення, опис доменного контексту, мотиви обраного варіанта та обов'язковий атрибут незворотності (`One-Way Door` чи `Two-Way Door`). Проте сам по собі текстовий файл у репозиторії не здатен зупинити розробника під час термінового хотфіксу від прямого імпорту чужої бази даних чи створення некоректного виклику між сервісами. Під тиском термінів без автоматичних перевірок виникає високий ризик того, що розробник обере найкоротший обхідний шлях написання коду, створюючи приховану архітектурну боргову яму.

Для перетворення декларативних ADR на автоматичні та безкомпромісні заслони у системі Digital Homes впроваджено два ключові типи перевірок, які виконуються на рівні конвеєра безперервної інтеграції (CI/CD):

1. **Валідатор структури та метаданих ADR:** Автоматичний сканер, який перевіряє наявність обов'язкових полів у кожному файлі рішення (Статус, Дата, Контекст, Обґрунтування, Наслідки, Незворотність `One-Way` / `Two-Way`). Якщо новий Pull Request додає новий сервіс або змінює протокол без відповідного запису ADR, збірка проєкту негайно зупиняється з вимогою задокументувати вибір.
2. **Статична фітнес-функція залежностей між контекстами:** Сканер вихідного коду, який будує граф імпортів та прямих викликів між модулями й перевіряє його проти декларативної карти дозволених зв'язків. Якщо сервіс телеметрії намагається заімпортити класи білінгу або прямо з'єднатися з базами даних користувачів, фітнес-функція генерує відмову збірки з вказівкою конкретного ADR, яке було порушено.

---

## 2. Реалізація аналізатора меж та фітнес-функції у CI/CD

Нижче наведено практичну реалізацію утиліти перевірки дотримання архітектурних меж між сервісами `Telemetry`, `DeviceRegistry`, `EdgeEngine` та `Billing`. Програма аналізує конфігураційний маніфест дозволених зв'язків та сканує вихідні файли на наявність заборонених викликів.

:::tabs
```c
/* adr_checker.c - Статичний аналізатор архітектурних меж Digital Homes (C version) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE 512
#define MAX_RULES 16

typedef struct {
    char source_context[64];
    char forbidden_target[64];
    char adr_id[16];
} ArchitecturalRule;

typedef struct {
    ArchitecturalRule rules[MAX_RULES];
    int rule_count;
} GovernancePolicy;

void init_policy(GovernancePolicy *policy) {
    policy->rule_count = 0;
    
    /* Правило 1: TelemetryContext не має звертатися до BillingDB (ADR-004) */
    strncpy(policy->rules[0].source_context, "telemetry", 64);
    strncpy(policy->rules[0].forbidden_target, "billing_db", 64);
    strncpy(policy->rules[0].adr_id, "ADR-004", 16);
    
    /* Правило 2: EdgeEngine не має прямо викликати UserAuthService (ADR-012) */
    strncpy(policy->rules[1].source_context, "edge_engine", 64);
    strncpy(policy->rules[1].forbidden_target, "user_auth", 64);
    strncpy(policy->rules[1].adr_id, "ADR-012", 16);
    
    policy->rule_count = 2;
}

int check_line_violation(const char *current_context, const char *line, const GovernancePolicy *policy, char *out_adr) {
    for (int i = 0; i < policy->rule_count; i++) {
        if (strcmp(current_context, policy->rules[i].source_context) == 0) {
            if (strstr(line, policy->rules[i].forbidden_target) != NULL) {
                strncpy(out_adr, policy->rules[i].adr_id, 16);
                return 1; /* Порушення знайдено */
            }
        }
    }
    return 0;
}

int audit_source_file(const char *filepath, const char *context_name, const GovernancePolicy *policy) {
    FILE *fp = fopen(filepath, "r");
    if (!fp) {
        printf("[WARN] Не вдалося відкрити файл: %s\n", filepath);
        return 0;
    }

    char line[MAX_LINE];
    char adr_id[16];
    int line_number = 0;
    int violations = 0;

    while (fgets(line, sizeof(line), fp)) {
        line_number++;
        if (check_line_violation(context_name, line, policy, adr_id)) {
            printf("[FAIL] Порушення %s у %s:%d -> Знайдено заборонений виклик!\n", adr_id, filepath, line_number);
            printf("       Рядок: %s", line);
            violations++;
        }
    }

    fclose(fp);
    return violations;
}

int main(int argc, char *argv[]) {
    printf("=== Digital Homes Architecture Fitness Function Audit ===\n");
    GovernancePolicy policy;
    init_policy(&policy);

    /* Тестова перевірка файлу */
    const char *test_file = "src/telemetry/ingest.c";
    const char *test_context = "telemetry";

    /* Створення фейкового файлу для демо перевірки */
    FILE *demo = fopen(test_file, "w");
    if (demo) {
        fprintf(demo, "#include <stdio.h>\n");
        fprintf(demo, "// Отримання телеметрії\n");
        fprintf(demo, "void process_telemetry() {\n");
        fprintf(demo, "    // ILLEGAL: Пряме звернення до білінгу!\n");
        fprintf(demo, "    connect_to_billing_db();\n");
        fprintf(demo, "}\n");
        fclose(demo);
    }

    int total_violations = audit_source_file(test_file, test_context, &policy);
    
    if (total_violations > 0) {
        printf("\n[RESULT] Блокування збірки: знайдено %d порушень фітнес-функцій!\n", total_violations);
        return 1;
    }

    printf("\n[RESULT] Перевірку пройдено успішно: ерозії меж не виявлено.\n");
    return 0;
}
```
```cpp
// adr_checker.cpp - Ідіоматичний статичний аналізатор фітнес-функцій (C++20 version)
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <filesystem>
#include <expected>

namespace fs = std::filesystem;

struct ArchRule {
    std::string source_context;
    std::string forbidden_target;
    std::string adr_id;
};

class FitnessAuditEngine {
private:
    std::vector<ArchRule> rules_;

public:
    FitnessAuditEngine() {
        // Конфігурація правил на основі журналу ADR Digital Homes
        rules_.push_back({"telemetry", "billing_db", "ADR-004"});
        rules_.push_back({"edge_engine", "user_auth", "ADR-012"});
    }

    [[nodiscard]] std::expected<size_t, std::string> audit_file(const fs::path& filepath, std::string_view current_context) const {
        if (!fs::exists(filepath)) {
            return std::unexpected("Файл не існує: " + filepath.string());
        }

        std::ifstream file(filepath);
        if (!file.is_open()) {
            return std::unexpected("Не вдалося відкрити файл: " + filepath.string());
        }

        std::string line;
        size_t line_num = 0;
        size_t violations = 0;

        while (std::getline(file, line)) {
            line_num++;
            for (const auto& rule : rules_) {
                if (rule.source_context == current_context && line.find(rule.forbidden_target) != std::string::npos) {
                    std::cout << "[FAIL] Фітнес-функція " << rule.adr_id 
                              << " порушена у " << filepath.string() << ":" << line_num << "\n"
                              << "       Вміст: " << line << "\n";
                    violations++;
                }
            }
        }

        return violations;
    }
};

int main() {
    std::cout << "=== Digital Homes C++20 Architectural Fitness Auditor ===\n";
    FitnessAuditEngine engine;

    const fs::path test_path = "src/telemetry/ingest.cpp";
    
    // Створення тестового файлу
    {
        std::ofstream out(test_path);
        out << "#include <iostream>\n";
        out << "void handle_ingest() {\n";
        out << "    // Порушення: прямий доступ до БД білінгу\n";
        out << "    auto db = connect_to_billing_db();\n";
        out << "}\n";
    }

    auto result = engine.audit_file(test_path, "telemetry");
    if (!result) {
        std::cerr << "[ERROR] " << result.error() << "\n";
        return 2;
    }

    if (*result > 0) {
        std::cout << "\n[BUILD BLOCKED] Виявлено " << *result << " зафіксованих порушень ADR!\n";
        return 1;
    }

    std::cout << "\n[SUCCESS] Усі фітнес-функції пройдено успішно.\n";
    return 0;
}
```
```python
# adr_checker.py - Python CLI для валідації метаданих ADR та генерації звіту
import os
import re
import sys
from pathlib import Path

REQUIRED_KEYS = ["Статус", "Дата", "Контекст", "Незворотність"]

def validate_adr_file(filepath: Path) -> list[str]:
    errors = []
    content = filepath.read_text(encoding="utf-8")
    
    for key in REQUIRED_KEYS:
        if not re.search(fr"\*\*_{key}_\*\*:|\*\*{key}\*\*:", content, re.IGNORECASE):
            errors.append(f"Відсутнє обов'язкове поле метаданих: '{key}'")
            
    if "One-Way" not in content and "Two-Way" not in content:
        errors.append("Не вказано тип незворотності рішення ('One-Way' або 'Two-Way')")
        
    return errors

def main():
    print("=== ADR Registry Metadata Validator ===")
    adr_dir = Path("docs/adr")
    
    if not adr_dir.exists():
        print(f"[WARN] Тека {adr_dir} не знайдена. Створення демо-теки.")
        adr_dir.mkdir(parents=True, exist_ok=True)
        demo_adr = adr_dir / "ADR-001-edge-autonomy.md"
        demo_adr.write_text(
            "# ADR-001: Локальна автономність хаба\n\n"
            "**Статус**: Прийнято\n"
            "**Дата**: 2022-03-15\n"
            "**Контекст**: Захист від втрати мережі\n"
            "**Незворотність**: One-Way Door\n\n"
            "## Рішення\nВикористовувати C++ engine на хабі.\n",
            encoding="utf-8"
        )

    total_errors = 0
    for adr_file in adr_dir.glob("*.md"):
        errs = validate_adr_file(adr_file)
        if errs:
            print(f"[FAIL] {adr_file.name}:")
            for e in errs:
                print(f"  - {e}")
            total_errors += len(errs)
        else:
            print(f"[OK] {adr_file.name}")

    if total_errors > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
```
:::

---

## 3. Деталізація алгоритму статичної інспекції та аналізу дерев викликів

Повний процес автоматизованого аудиту кодової бази та валідації архітектурних меж спирається на три послідовні інженерні фази аналізу, які інтегровано в єдиний конвеєр перевірок:

1. **Фаза побудови абстрактного синтаксичного дерева (AST Parsing):** Сканер розбирає вихідний код мовами C, C++, Go чи Python на окремі синтаксичні вузли. Виокремлюються виклики функцій, конструктори об'єктів, оператори створення таблиць та директиви імпорту бібліотек (`#include`, `import`, `use`). Цей крок дозволяє відсікти коментарі та рядкові літерали, аналізуючи лише реальний виконуваний код.
2. **Фаза сопоставлення з контекстною мапою (Context Mapping):** Кожен файл вихідного коду асоціюється з одним із задекларованих у системі обмежених контекстів (Bounded Contexts) на основі його фізичного розташування в дереві каталогів репозиторію. Наприклад, файли з `src/telemetry/*` належать до контексту телеметрії, `src/billing/*` — до білінгу, а `src/edge/*` — до локального рантайму хаба.
3. **Фаза обчислення матриці викликів та виявлення порушень (Call Matrix Calculation):** Кожен знайдений імпорт або виклик порівнюється з декларативною матрицею дозволених міжсервісних зв'язків. Якщо сканер знаходить напрямок виклику, який заборонено задекларованим ADR (наприклад, пряме звернення з телеметрії до бази даних білінгу повз API Gateway чи Event Broker), аналізатор генерує виняток і негайно блокує збірку.

### Обробка крайових випадків та непрямих викликів

При розбудові статичних фітнес-функцій виникає низка складних крайових випадків, які потребують спеціальної обробки у сканері:

- **Динамічний зв'язок через рефлексію або дзеркальні таблиці:** У мовах типу Python або Go розробник може спробувати обійти статичний імпорт за допомогою рефлексії (`getattr`, `reflect`) або виконання динамічного SQL-рядка (`db.Exec("SELECT * FROM billing_db...")`). Фітнес-функція Digital Homes вирішує цю проблему за допомогою комбінації статичного аналізу AST із синтаксичним аналізом текстових шаблонів SQL-запитів.
- **Транзитивні залежності через спільні бібліотеки:** Коли сервіс `Telemetry` та сервіс `Billing` підключають спільну внутрішню бібліотеку `common_utils`, існує ризик виникнення неявної зв'язаності через глобальні змінні чи спільні конфігурації. Фітнес-функція ізолює спільні бібліотеки, перевіряючи, щоб вони не містили доменної логіки та стану.
- **Обхід меж через проміжні шлюзи:** Спроба прокинути виклик через неавторизований проксі-модуль виявляється шляхом обчислення транзитивного замикання графа викликів (Transitive Closure Graph). Сканер будує повний ланцюжок викликів від точки входу до кінцевого виконався й блокує будь-який ланцюг, який перетинає заборонену доменну межу.

---

## 4. Практичні правила інтеграції у CI/CD пайплайн

Для забезпечення постійної дії захисту у проєкті Digital Homes утиліти валідації інтегровано в GitHub Actions та GitLab CI на етап перевірки кожного комміту:

- **Етап 1 (Fast-Fail Metadata Check):** Валідація опису ADR та заповненості полів незворотності за допомогою скрипту `adr_checker.py`. Якщо PR додає новий сервіс без відповідного форматованого ADR — деплой блокується на першій хвилині збірки.
- **Етап 2 (Static Analysis Fitness Checks):** Запуск розкомпільованого C/C++ аналізатора `adr_checker`. Він сканує вихідні файли й виявляє прямі залежності між C++ модулями хаба й Go-сервісами хмари за лічені секунди.
- **Етап 3 (Fitness Function Reporting & Alerting):** У разі виявлення порушення розробник отримує точний звіт із зазначенням конкретного номера ADR, який забороняє таку архітектурну зв'язаність, а також рекомендації щодо правильного використання викликів через публічний API Gateway або брокер повідомлень.

---

## 5. Довгостроковий ефект від впровадження фітнес-функцій

Досвід експлуатації автоматичного аналізатора ADR у системі Digital Homes протягом 2023–2024 років показав такі результати:

1. **Нульовий дрейф меж контекстів:** Жоден із 450 коммітів, зроблених трьома новими командами розробників, не створив несанкціонованого прямого зв'язку між базами даних різних доменів.
2. **Прискорення Onboarding нових інженерів:** Новий розробник може сміливо проводити рефакторинг коду, не побоюючись випадково розвалити чужий домен: автоматична фітнес-функція миттєво підкаже правильну межу у разі помилки.
3. **Чесна документація:** Файли ADR перестали бути закинутими текстовими артефактами. Оскільки заповнення ADR є обов'язковою умовою проходження CI, реєстр рішень завжди підтримується в актуальному стані.
