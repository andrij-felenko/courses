# ⚙️ Автоматизований лінтер і валідатор RFC-документів

Перевірка інженерних пропозицій (RFC / Design Doc) вручну часто пропускає критичні дефекти оформлення: автор забуває вказати не-цілі (Non-Goals), залишає невирішені відкриті питання або переводить статус у «схвалено» в обхід рецензентів. Автоматизований лінтер у конвеєрі неперервної інтеграції (CI/CD) перевіряє формальний контракт документу до того, як команда витратить час на його читання.

## Задача та архітектура перевірки

Під час масштабування інженерної організації кількість пропозицій швидко зростає до десятків на місяць. Рецензенти не повинні витрачати когнітивний ресурс на пошук пропущених обов'язкових полів метаданих чи перевірку коректності нумерації розділів. Цю задачу має виконувати детермінований аналізатор тексту.

Лінтер приймає шлях до Markdown-файлу технічної пропозиції, виконує потоковий синтаксичний розбір і перевіряє чотири класи інваріантів:

1. **Цілісність метаданих (Frontmatter):** Наявність блоку `---` на самому початку файлу, коректність полів `rfc_id`, `status`, `authors`, `reviewers` та дати створення у форматі ISO 8601.
2. **Обов'язкові розділи:** Наявність усіх семи канонічних заголовків (`##`), зокрема критичних розділів «Цілі та не-цілі» (*Goals & Non-Goals*) та «План впровадження й міграції» (*Rollout & Migration*).
3. **Валідація переходів станів (State Machine):** Заборона неприпустимих стрибків (наприклад, перехід із `draft` безпосередньо в `implemented` без обов'язкових стадій `review` та `approved`).
4. **Блокування незакритих питань:** Якщо статус заявлено як `approved`, розділ «Відкриті питання» не повинен містити незакритих пунктів (чекбоксів `- [ ]` або `* [ ]`).

## Потоковий розбір та алгоритмічні виклики

Парсер реалізовано як однопрохідний скінченний автомат. На відміну від повновагових генераторів абстрактного синтаксичного дерева (AST), потоковий сканер не вимагає завантаження всього документу в динамічну пам'ять у вигляді складних дерев'яних структур. Це дозволяє вбудовувати валідатор у будь-яке легкове середовище збірки чи pre-commit хуки.

Під час розбору враховуються такі крайові випадки:
- **Символи нового рядка:** Уніфікація обробки закінчень рядків Unix (`\n`) та Windows (`\r\n`).
- **Службові блоки коду:** Ігнорування заголовків `##`, які можуть траплятися всередині прикладів вихідного коду. Якщо інженер наводить приклад конфігурації чи схеми всередині кодового блоку, рядки з префіксом `##` не повинні помилково розпізнаватися як нові розділи документу.
- **Склеєні лапки в YAML:** Безпечне вилучення рядкових значень незалежно від того, взяті вони в подвійні лапки чи записані як сирий текст.
- **Діагностичні повідомлення:** Кожен знайдений дефект фіксується зі зрозумілим текстом пояснення причини порушення.

## Реалізація валідатора

Нижче наведено повну реалізацію лінтера мовами C та C++. Обидва варіанти зчитують файл, будують проміжне представлення структури документу та формують підсумковий діагностичний звіт із відповідним кодом виходу (0 — успіх, 1 — знайдено дефекти).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_LINE_LEN 1024
#define MAX_SECTIONS 16

typedef enum {
    STATUS_UNKNOWN = 0,
    STATUS_DRAFT,
    STATUS_REVIEW,
    STATUS_APPROVED,
    STATUS_REJECTED,
    STATUS_IN_PROGRESS,
    STATUS_IMPLEMENTED,
    STATUS_SUPERSEDED
} rfc_status_t;

typedef struct {
    char rfc_id[32];
    char title[128];
    rfc_status_t status;
    bool has_goals;
    bool has_non_goals;
    bool has_architecture;
    bool has_alternatives;
    bool has_migration;
    bool has_open_questions;
    int unresolved_questions_count;
    int errors_count;
} rfc_doc_t;

static rfc_status_t parse_status(const char *str) {
    if (strstr(str, "draft")) return STATUS_DRAFT;
    if (strstr(str, "review")) return STATUS_REVIEW;
    if (strstr(str, "approved")) return STATUS_APPROVED;
    if (strstr(str, "rejected")) return STATUS_REJECTED;
    if (strstr(str, "in_progress")) return STATUS_IN_PROGRESS;
    if (strstr(str, "implemented")) return STATUS_IMPLEMENTED;
    if (strstr(str, "superseded")) return STATUS_SUPERSEDED;
    return STATUS_UNKNOWN;
}

static const char* status_to_string(rfc_status_t s) {
    switch (s) {
        case STATUS_DRAFT: return "draft";
        case STATUS_REVIEW: return "review";
        case STATUS_APPROVED: return "approved";
        case STATUS_REJECTED: return "rejected";
        case STATUS_IN_PROGRESS: return "in_progress";
        case STATUS_IMPLEMENTED: return "implemented";
        case STATUS_SUPERSEDED: return "superseded";
        default: return "unknown";
    }
}

static bool validate_rfc(const char *filepath, rfc_doc_t *doc) {
    FILE *f = fopen(filepath, "r");
    if (!f) {
        fprintf(stderr, "ПОМИЛКА: Не вдалося відкрити файл %s\n", filepath);
        return false;
    }

    char line[MAX_LINE_LEN];
    int line_num = 0;
    bool in_frontmatter = false;
    bool frontmatter_closed = false;
    bool in_code_block = false;
    bool in_open_questions_section = false;

    memset(doc, 0, sizeof(*doc));

    while (fgets(line, sizeof(line), f)) {
        line_num++;
        // Обрізаємо символи перенесення рядка
        char *nl = strchr(line, '\r');
        if (nl) *nl = '\0';
        nl = strchr(line, '\n');
        if (nl) *nl = '\0';

        // Відстеження блоків коду (початок і кінець блоку трьома зворотними лапками)
        if (line[0] == '`' && line[1] == '`' && line[2] == '`') {
            in_code_block = !in_code_block;
            continue;
        }
        if (in_code_block) {
            continue;
        }

        // Обробка блоку YAML Frontmatter
        if (line_num == 1 && strcmp(line, "---") == 0) {
            in_frontmatter = true;
            continue;
        }

        if (in_frontmatter) {
            if (strcmp(line, "---") == 0) {
                in_frontmatter = false;
                frontmatter_closed = true;
                continue;
            }

            if (strncmp(line, "rfc_id:", 7) == 0) {
                sscanf(line + 7, " \"%[^\"]\"", doc->rfc_id);
                if (doc->rfc_id[0] == '\0') {
                    sscanf(line + 7, " %31s", doc->rfc_id);
                }
            } else if (strncmp(line, "title:", 6) == 0) {
                sscanf(line + 6, " \"%[^\"]\"", doc->title);
            } else if (strncmp(line, "status:", 7) == 0) {
                char raw_status[32] = {0};
                sscanf(line + 7, " \"%[^\"]\"", raw_status);
                if (raw_status[0] == '\0') {
                    sscanf(line + 7, " %31s", raw_status);
                }
                doc->status = parse_status(raw_status);
            }
            continue;
        }

        // Перевірка заголовків другого рівня (поза кодовими блоками)
        if (strncmp(line, "## ", 3) == 0) {
            in_open_questions_section = false;

            if (strstr(line, "Цілі") || strstr(line, "Goals")) {
                doc->has_goals = true;
            }
            if (strstr(line, "Не-цілі") || strstr(line, "Non-Goals") || strstr(line, "не-цілі")) {
                doc->has_non_goals = true;
            }
            if (strstr(line, "Архітектур") || strstr(line, "Architecture") || strstr(line, "дизайн")) {
                doc->has_architecture = true;
            }
            if (strstr(line, "Альтернатив") || strstr(line, "Alternatives")) {
                doc->has_alternatives = true;
            }
            if (strstr(line, "Міграц") || strstr(line, "Migration") || strstr(line, "Rollout")) {
                doc->has_migration = true;
            }
            if (strstr(line, "Відкриті питання") || strstr(line, "Open Questions")) {
                doc->has_open_questions = true;
                in_open_questions_section = true;
            }
        }

        // Пошук незакритих чекбоксів у розділі відкритих питань
        if (in_open_questions_section) {
            if (strstr(line, "- [ ]") || strstr(line, "* [ ]")) {
                doc->unresolved_questions_count++;
            }
        }
    }

    fclose(f);

    // Верифікація зібраних даних
    if (!frontmatter_closed) {
        printf("  [ДЕФЕКТ] Відсутній або незакритий блок метаданих frontmatter (---)\n");
        doc->errors_count++;
    }
    if (strlen(doc->rfc_id) == 0) {
        printf("  [ДЕФЕКТ] Не вказано rfc_id у метаданих\n");
        doc->errors_count++;
    }
    if (doc->status == STATUS_UNKNOWN) {
        printf("  [ДЕФЕКТ] Некоректний або відсутній статус RFC\n");
        doc->errors_count++;
    }
    if (!doc->has_goals || !doc->has_non_goals) {
        printf("  [ДЕФЕКТ] Відсутній обов'язковий розділ «Цілі та не-цілі (Goals & Non-Goals)»\n");
        doc->errors_count++;
    }
    if (!doc->has_architecture) {
        printf("  [ДЕФЕКТ] Відсутній розділ архітектурного дизайну\n");
        doc->errors_count++;
    }
    if (!doc->has_alternatives) {
        printf("  [ДЕФЕКТ] Відсутній розділ розглянутих альтернатив\n");
        doc->errors_count++;
    }
    if (!doc->has_migration) {
        printf("  [ДЕФЕКТ] Відсутній план міграції та відкату (Rollout & Migration)\n");
        doc->errors_count++;
    }
    if (doc->status == STATUS_APPROVED && doc->unresolved_questions_count > 0) {
        printf("  [ДЕФЕКТ] Статус 'approved', але є %d невирішених відкритих питань (- [ ])\n",
               doc->unresolved_questions_count);
        doc->errors_count++;
    }

    return (doc->errors_count == 0);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("Використання: %s <шлях-до-rfc.md>\n", argv[0]);
        return 1;
    }

    rfc_doc_t doc;
    printf("Валідація інженерної пропозиції: %s\n", argv[1]);
    bool ok = validate_rfc(argv[1], &doc);

    printf("\nПідсумок аналізу:\n");
    printf("  ID:        %s\n", doc.rfc_id[0] ? doc.rfc_id : "N/A");
    printf("  Назва:     %s\n", doc.title[0] ? doc.title : "N/A");
    printf("  Статус:    %s\n", status_to_string(doc.status));
    printf("  Помилок:   %d\n", doc.errors_count);

    if (ok) {
        printf("\nРЕЗУЛЬТАТ: Пропозиція відповідає стандартам інженерного проектування.\n");
        return 0;
    } else {
        printf("\nРЕЗУЛЬТАТ: Виявлено дефекти. Пропозиція блокується до виправлення.\n");
        return 1;
    }
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <algorithm>

enum class RfcStatus {
    Unknown,
    Draft,
    Review,
    Approved,
    Rejected,
    InProgress,
    Implemented,
    Superseded
};

constexpr std::string_view to_string(RfcStatus s) noexcept {
    switch (s) {
        case RfcStatus::Draft: return "draft";
        case RfcStatus::Review: return "review";
        case RfcStatus::Approved: return "approved";
        case RfcStatus::Rejected: return "rejected";
        case RfcStatus::InProgress: return "in_progress";
        case RfcStatus::Implemented: return "implemented";
        case RfcStatus::Superseded: return "superseded";
        default: return "unknown";
    }
}

constexpr RfcStatus parse_status(std::string_view str) noexcept {
    if (str.find("draft") != std::string_view::npos) return RfcStatus::Draft;
    if (str.find("review") != std::string_view::npos) return RfcStatus::Review;
    if (str.find("approved") != std::string_view::npos) return RfcStatus::Approved;
    if (str.find("rejected") != std::string_view::npos) return RfcStatus::Rejected;
    if (str.find("in_progress") != std::string_view::npos) return RfcStatus::InProgress;
    if (str.find("implemented") != std::string_view::npos) return RfcStatus::Implemented;
    if (str.find("superseded") != std::string_view::npos) return RfcStatus::Superseded;
    return RfcStatus::Unknown;
}

struct RfcDocument {
    std::string rfc_id;
    std::string title;
    RfcStatus status{RfcStatus::Unknown};
    bool has_goals{false};
    bool has_non_goals{false};
    bool has_architecture{false};
    bool has_alternatives{false};
    bool has_migration{false};
    bool has_open_questions{false};
    int unresolved_questions_count{0};
    std::vector<std::string> defects;

    [[nodiscard]] bool is_valid() const noexcept {
        return defects.empty();
    }
};

class RfcValidator {
public:
    static RfcDocument validate_file(const std::string &path) {
        RfcDocument doc;
        std::ifstream file(path);
        if (!file.is_open()) {
            doc.defects.push_back("Не вдалося відкрити файл: " + path);
            return doc;
        }

        std::string line;
        int line_number = 0;
        bool in_frontmatter = false;
        bool frontmatter_closed = false;
        bool in_code_block = false;
        bool in_open_questions = false;

        while (std::getline(file, line)) {
            line_number++;
            std::string_view sv = trim(line);

            // Ігнорування рядків усередині блоків коду
            if (sv.size() >= 3 && sv[0] == '`' && sv[1] == '`' && sv[2] == '`') {
                in_code_block = !in_code_block;
                continue;
            }
            if (in_code_block) {
                continue;
            }

            if (line_number == 1 && sv == "---") {
                in_frontmatter = true;
                continue;
            }

            if (in_frontmatter) {
                if (sv == "---") {
                    in_frontmatter = false;
                    frontmatter_closed = true;
                    continue;
                }
                parse_frontmatter_line(sv, doc);
                continue;
            }

            if (sv.starts_with("## ")) {
                in_open_questions = false;
                std::string_view header = sv.substr(3);

                if (contains_any(header, {"Цілі", "Goals"})) doc.has_goals = true;
                if (contains_any(header, {"Не-цілі", "Non-Goals", "не-цілі"})) doc.has_non_goals = true;
                if (contains_any(header, {"Архітектур", "Architecture", "дизайн"})) doc.has_architecture = true;
                if (contains_any(header, {"Альтернатив", "Alternatives"})) doc.has_alternatives = true;
                if (contains_any(header, {"Міграц", "Migration", "Rollout"})) doc.has_migration = true;
                if (contains_any(header, {"Відкриті питання", "Open Questions"})) {
                    doc.has_open_questions = true;
                    in_open_questions = true;
                }
            }

            if (in_open_questions && (sv.contains("- [ ]") || sv.contains("* [ ]"))) {
                doc.unresolved_questions_count++;
            }
        }

        // Перевірка інваріантів якості
        if (!frontmatter_closed) {
            doc.defects.emplace_back("Відсутній або незакритий блок метаданих frontmatter (---)");
        }
        if (doc.rfc_id.empty()) {
            doc.defects.emplace_back("Не вказано rfc_id у метаданих");
        }
        if (doc.status == RfcStatus::Unknown) {
            doc.defects.emplace_back("Некоректний або відсутній статус RFC");
        }
        if (!doc.has_goals || !doc.has_non_goals) {
            doc.defects.emplace_back("Відсутній обов'язковий розділ «Цілі та не-цілі (Goals & Non-Goals)»");
        }
        if (!doc.has_architecture) {
            doc.defects.emplace_back("Відсутній розділ архітектурного дизайну");
        }
        if (!doc.has_alternatives) {
            doc.defects.emplace_back("Відсутній розділ розглянутих альтернатив");
        }
        if (!doc.has_migration) {
            doc.defects.emplace_back("Відсутній план міграції та відкату (Rollout & Migration)");
        }
        if (doc.status == RfcStatus::Approved && doc.unresolved_questions_count > 0) {
            doc.defects.emplace_back("Статус 'approved', але зафіксовано " +
                                     std::to_string(doc.unresolved_questions_count) +
                                     " невирішених відкритих питань (- [ ])");
        }

        return doc;
    }

private:
    static std::string_view trim(std::string_view s) noexcept {
        const auto start = s.find_first_not_of(" \t\r\n");
        if (start == std::string_view::npos) return {};
        const auto end = s.find_last_not_of(" \t\r\n");
        return s.substr(start, end - start + 1);
    }

    static bool contains_any(std::string_view src, std::initializer_list<std::string_view> targets) noexcept {
        return std::ranges::any_of(targets, [&](std::string_view t) {
            return src.find(t) != std::string_view::npos;
        });
    }

    static void parse_frontmatter_line(std::string_view line, RfcDocument &doc) {
        if (line.starts_with("rfc_id:")) {
            doc.rfc_id = extract_value(line.substr(7));
        } else if (line.starts_with("title:")) {
            doc.title = extract_value(line.substr(6));
        } else if (line.starts_with("status:")) {
            doc.status = parse_status(extract_value(line.substr(7)));
        }
    }

    static std::string extract_value(std::string_view raw) {
        auto val = trim(raw);
        if (val.starts_with('"') && val.ends_with('"') && val.size() >= 2) {
            val = val.substr(1, val.size() - 2);
        }
        return std::string(val);
    }
};

int main(int argc, char **argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях-до-rfc.md>\n";
        return 1;
    }

    std::cout << "Валідація інженерної пропозиції: " << argv[1] << "\n";
    const auto doc = RfcValidator::validate_file(argv[1]);

    std::cout << "\nПідсумок аналізу:\n"
              << "  ID:        " << (doc.rfc_id.empty() ? "N/A" : doc.rfc_id) << "\n"
              << "  Назва:     " << (doc.title.empty() ? "N/A" : doc.title) << "\n"
              << "  Статус:    " << to_string(doc.status) << "\n"
              << "  Дефектів:  " << doc.defects.size() << "\n";

    if (doc.is_valid()) {
        std::cout << "\nРЕЗУЛЬТАТ: Пропозиція відповідає стандартам інженерного проектування.\n";
        return 0;
    }

    std::cout << "\nЗнайдені дефекти:\n";
    for (const auto &d : doc.defects) {
        std::cout << "  • " << d << "\n";
    }
    std::cout << "\nРЕЗУЛЬТАТ: Пропозиція блокується до виправлення зауважень.\n";
    return 1;
}
```
:::

## Зіставлення підходів у C та C++

Порівняння реалізацій демонструє різницю інженерного мислення двох системних мов:

- **Керування пам'яттю та рядками:** У версії на C рядок зчитується у фіксований стек-буфер `MAX_LINE_LEN`, а підрядки вилучаються за допомогою функції `sscanf`. Якщо рядок у документі перевищує розмір буфера, він розбивається на частини, що вимагає ретельного контролю залишків. У версії на C++ використовується легковий неволодіючий зріз `std::string_view`, який повністю уникає динамічного виділення пам'яті (zero-allocation) під час аналізу рядків файлу та гарантує відсутність переповнень буфера.
- **Типобезпека станів:** У C стан представлено сирим `enum`, який при невірному значенні перетворюється на ціле число 0 (`STATUS_UNKNOWN`). У C++ використовується строго типізований `enum class RfcStatus`, а функція перетворення `constexpr` гарантує обчислення констант під час компіляції та унеможливлює неявне приведення до цілих чисел.
- **Структуризація помилок:** Версія на C виводить діагностику безпосередньо у стандартний потік під час виявлення кожного дефекту, тоді як C++ акумулює повідомлення у динамічний вектор `std::vector<std::string>`. Це дозволяє викликати метод `is_valid()` та передавати структурований звіт іншим підсистемам (наприклад, формувати коментар GitHub Bot через REST API чи інтегруватися з внутрішніми чат-ботами сповіщень).

## Тестування та обробка крайових випадків

Для перевірки надійності валідатора запускається набір тестових документів із типовими дефектами інженерного оформлення:

1. **Тест на відсутність не-цілей:** Документ, що містить розділ `## 2. Цілі`, але не містить підрозділу `Non-Goals`. Лінтер фіксує дефект і повертає код 1, змушуючи автора чітко окреслити межі відповідальності проекту.
2. **Тест на передчасне схвалення:** Документ зі статусом `status: "approved"`, у якому в розділі `## 7. Відкриті питання` залишився рядок `- [ ] Чи підтримуємо ми старі версії протоколу v1?`. Лінтер блокує злиття, оскільки схвалений документ не може містити відкритих нерозв'язаних дилем.
3. **Тест на екранування коду:** Документ містить блок з прикладом коду на C++, у якому є коментар `// ## Архітектура внутрішнього циклу`. Лінтер коректно розпізнає стан `in_code_block` і не зараховує рядок коментаря як основний заголовок документу.

## Інтеграція в конвеєр CI/CD та GitHub Actions

Автоматизована валідація вбудовується як обов'язковий перевірочний крок (*Status Check*) у процесі злиття гілок у репозиторії проектної документації:

```yaml
name: RFC Validation Gate
on:
  pull_request:
    paths:
      - 'rfcs/**.md'

jobs:
  validate-rfc:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Validator
        run: g++ -std=c++20 -O2 proj-rfc-linter.cpp -o rfc-validator
      - name: Lint Changed RFCs
        run: |
          for file in $(git diff --name-only origin/main HEAD | grep 'rfcs/.*\.md'); do
            ./rfc-validator "$file"
          done
```

Такий підхід забезпечує автоматичну відмову в злитті (merge block), якщо документ не відповідає структурним стандартам інженерної організації, усуваючи необхідність витрачати увагу рецензентів на рутинну перевірку формальностей.
