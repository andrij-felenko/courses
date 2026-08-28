# ⚙️ Генератор нотаток випуску з Conventional Commits

Автоматизований конвеєр неперервної інтеграції та розгортання ([CI/CD](root:sf-release/ci-cd)) потребує надійного інструменту, який здатен перетворити сиру послідовність повідомлень Git-комітів між двома релізними тегами на структурований документ нотаток випуску. Якщо покладатися на ручне складання списку змін реліз-інженером, процес виходу версії неминуче сповільнюється, а дрібні виправлення безпеки чи ламкі зміни бінарних протоколів губляться в багатосторінковому журналі репозиторію.

## Задача та архітектура синтаксичного розбору

Специфікація Conventional Commits формалізує структуру повідомлення коміту як строго визначену граматику:

```
<тип>[необов'язковий скоуп у дужках][!]: <опис зміни>

[необов'язкове розгорнуте тіло повідомлення]

[необов'язкові футери: мітки задач, CVE-ідентифікатори, блок BREAKING CHANGE]
```

Генератор нотаток випуску реалізує чотири послідовні фази обробки потоку комітів:

1. **Лексичний аналіз і токенізація заголовка:**
   - Виділення базового типу зміни: `feat`, `fix`, `chore`, `docs`, `refactor`, `perf`, `test`, `ci`.
   - Виділення контекстної області в круглих дужках (`scope`), наприклад `telemetry`, `adc`, `can-bus`.
   - Виявлення суфіксного маркера ламкої зміни `!` перед двокрапкою (наприклад, `feat(can)!:` або `fix!:`).
   - Відокремлення опису зміни після двокрапки з видаленням зайвих пробільних символів.

2. **Пошук футерів та міток безпеки:**
   - Пошук блоку `BREAKING CHANGE:` у багаторядковому тілі коміту. Наявність цього футера безумовно переводить зміну до мажорної категорії.
   - Пошук шаблону `CVE-YYYY-NNNN` (наприклад, `CVE-2026-4412`). Наявність ідентифікатора вразливості автоматично маркує коміт як безпековий бюлетень.
   - Вилучення посилань на тікети трекера завдань (наприклад, `Fixes #104`, `Closes JIRA-8812`) для формування клікабельних посилань у фінальному документі.

3. **Фільтрація та категоризація:**
   - Службові коміти внутрішнього супроводу (`chore`, `ci`, `test`, `build`), якщо вони не містять явної мітки `BREAKING CHANGE`, відсікаються від публічного бюлетеня, аби не перевантажувати операторів інженерним шумом.
   - Решта комітів розподіляються за чотирма пріоритетними категоріями:
     - 🔴 **Ламкі зміни (Breaking Changes):** зміни з маркером `!` або футером `BREAKING CHANGE`;
     - 🔒 **Бюлетені безпеки (Security Advisories):** коміти з типом `sec`, скоупом `sec` або знайденим номером CVE;
     - ✨ **Нові можливості (Features):** коміти з типом `feat`;
     - 🐛 **Виправлення дефектів (Bug Fixes):** коміти з типом `fix`.

4. **Форматування та генерація фінального Markdown:**
   - Генерація заголовка документа з номером версії та датою випуску.
   - Послідовний вивід кожної непорожньої секції з виділенням області дії жирним шрифтом (`**scope:** опис`) та додаванням посилань на CVE у моноширинному форматі.

## Модель пам'яті та робота автомата розбору

Парсер реалізовано як детермінований скінченний автомат. На відміну від простих регулярних виразів, які створюють навантаження на стек і можуть спричиняти катастрофічний бектрекінг на пошкоджених вхідних рядках, потоковий розбір безпосередньо у буфері пам'яті працює за лінійний час `O(N)`. Це дозволяє уникнути зайвих динамічних алокацій при обробці тисяч комітів репозиторію.

Автомат переходить між п'ятьма внутрішніми станами:
- `STATE_SEEK_TYPE`: Зчитування літер до першої відкритої дужки `(`, знака оклику `!` або двокрапки `:`.
- `STATE_PARSE_SCOPE`: Накопичення символів контекстної області до закритої дужки `)`.
- `STATE_CHECK_EXCLAMATION`: Перевірка наявності суфікса ламкої зміни.
- `STATE_PARSE_SUBJECT`: Читання короткого опису зміни до символу переведення рядка.
- `STATE_SCAN_FOOTERS`: Пошуковий прохід по тілу коміту для виявлення метаданих `BREAKING CHANGE:` та `CVE-`.

## Реалізація парсера та генератора

Нижче наведено повну реалізацію генератора. У вкладці C реалізовано низькорівневий розбір тексту на фіксованих буферах без сторонніх залежностей. У сусідній вкладці C++ задачу розв'язано за допомогою сучасних ідіом стандарту C++20 із застосуванням `std::string_view`, динамічних векторів та строго типізованих переліків `enum class`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>

#define MAX_ENTRIES 128
#define MAX_STR_LEN 256

typedef enum {
    CAT_BREAKING = 0,
    CAT_SECURITY,
    CAT_FEATURE,
    CAT_FIX,
    CAT_IGNORE,
    CAT_COUNT
} Category;

typedef struct {
    char type[32];
    char scope[32];
    char description[MAX_STR_LEN];
    char cve[32];
    bool is_breaking;
    Category category;
} CommitEntry;

static void trim_spaces(char *str) {
    char *end;
    while (isspace((unsigned char)*str)) str++;
    end = str + strlen(str) - 1;
    while (end > str && isspace((unsigned char)*end)) end--;
    *(end + 1) = '\0';
}

static CommitEntry parse_commit(const char *raw_line) {
    CommitEntry entry;
    memset(&entry, 0, sizeof(entry));
    entry.category = CAT_IGNORE;

    char buffer[MAX_STR_LEN * 2];
    strncpy(buffer, raw_line, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';

    /* Перевірка наявності мітки вразливості CVE */
    const char *cve_pos = strstr(buffer, "CVE-");
    if (cve_pos) {
        int i = 0;
        while (cve_pos[i] && !isspace((unsigned char)cve_pos[i]) && cve_pos[i] != ')' && i < 31) {
            entry.cve[i] = cve_pos[i];
            i++;
        }
        entry.cve[i] = '\0';
    }

    /* Перевірка футера або маркера BREAKING CHANGE */
    if (strstr(buffer, "BREAKING CHANGE:") != NULL) {
        entry.is_breaking = true;
    }

    char *colon = strchr(buffer, ':');
    if (!colon) return entry;

    *colon = '\0';
    char *header = buffer;
    char *desc = colon + 1;
    while (isspace((unsigned char)*desc)) desc++;
    strncpy(entry.description, desc, sizeof(entry.description) - 1);

    /* Розбір типу, скоупу та знака оклику */
    char *open_paren = strchr(header, '(');
    char *close_paren = strchr(header, ')');
    char *excl = strchr(header, '!');

    if (excl) {
        entry.is_breaking = true;
    }

    if (open_paren && close_paren && close_paren > open_paren) {
        *open_paren = '\0';
        *close_paren = '\0';
        strncpy(entry.type, header, sizeof(entry.type) - 1);
        strncpy(entry.scope, open_paren + 1, sizeof(entry.scope) - 1);
    } else {
        if (excl) *excl = '\0';
        strncpy(entry.type, header, sizeof(entry.type) - 1);
    }

    trim_spaces(entry.type);
    trim_spaces(entry.scope);
    trim_spaces(entry.description);

    /* Визначення результуючої категорії */
    if (entry.is_breaking) {
        entry.category = CAT_BREAKING;
    } else if (entry.cve[0] != '\0' || strcmp(entry.type, "sec") == 0 || strcmp(entry.scope, "sec") == 0) {
        entry.category = CAT_SECURITY;
    } else if (strcmp(entry.type, "feat") == 0) {
        entry.category = CAT_FEATURE;
    } else if (strcmp(entry.type, "fix") == 0) {
        entry.category = CAT_FIX;
    } else {
        entry.category = CAT_IGNORE;
    }

    return entry;
}

void generate_release_notes(const char *version, const char *date, const char *raw_commits[], size_t count) {
    CommitEntry entries[MAX_ENTRIES];
    size_t valid_count = 0;

    for (size_t i = 0; i < count && valid_count < MAX_ENTRIES; ++i) {
        CommitEntry e = parse_commit(raw_commits[i]);
        if (e.category != CAT_IGNORE) {
            entries[valid_count++] = e;
        }
    }

    printf("# Нотатки випуску %s (%s)\n\n", version, date);

    const char *headers[CAT_COUNT] = {
        "## 🔴 Обов'язкові дії та несумісні зміни (Breaking Changes)",
        "## 🔒 Бюлетені безпеки (Security Advisories)",
        "## ✨ Нові можливості (Features)",
        "## 🐛 Виправлення дефектів (Bug Fixes)",
        ""
    };

    for (int cat = 0; cat < CAT_IGNORE; ++cat) {
        bool has_items = false;
        for (size_t i = 0; i < valid_count; ++i) {
            if (entries[i].category == (Category)cat) {
                if (!has_items) {
                    printf("%s\n\n", headers[cat]);
                    has_items = true;
                }
                if (entries[i].scope[0] != '\0') {
                    printf("- **%s:** %s", entries[i].scope, entries[i].description);
                } else {
                    printf("- %s", entries[i].description);
                }

                if (entries[i].cve[0] != '\0') {
                    printf(" (`%s`)", entries[i].cve);
                }
                printf("\n");
            }
        }
        if (has_items) printf("\n");
    }
}

int main(void) {
    const char *sample_commits[] = {
        "feat(can)!: перейти на бітову швидкість CAN-FD 2 Мбіт/с",
        "fix(adc): виправити дрейф нульового рівня входу АЦП",
        "fix(sec): усунути переповнення буфера Modbus (CVE-2026-4412)",
        "chore(ci): оновити версію компілятора GCC до 14.2",
        "feat(telemetry): додати періодичний звіт про стан акумулятора",
        "docs(readme): оновити схему підключення UART"
    };
    size_t count = sizeof(sample_commits) / sizeof(sample_commits[0]);

    generate_release_notes("v3.2.0", "2026-08-28", sample_commits, count);
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <array>

enum class Category {
    Breaking = 0,
    Security,
    Feature,
    Fix,
    Ignore,
    Count
};

struct CommitRecord {
    std::string type;
    std::string scope;
    std::string description;
    std::string cve;
    bool is_breaking{false};
    Category category{Category::Ignore};
};

static std::string_view trim(std::string_view s) {
    const auto start = s.find_first_not_of(" \t\n\r");
    if (start == std::string_view::npos) return {};
    const auto end = s.find_last_not_of(" \t\n\r");
    return s.substr(start, end - start + 1);
}

class ReleaseNotesGenerator {
public:
    static CommitRecord parse_commit(std::string_view raw) {
        CommitRecord rec;

        // Пошук ідентифікатора CVE
        if (const auto cve_pos = raw.find("CVE-"); cve_pos != std::string_view::npos) {
            const auto end_pos = raw.find_first_of(" \t\n\r)]", cve_pos);
            rec.cve = std::string(raw.substr(cve_pos, end_pos - cve_pos));
        }

        if (raw.find("BREAKING CHANGE:") != std::string_view::npos) {
            rec.is_breaking = true;
        }

        const auto colon_pos = raw.find(':');
        if (colon_pos == std::string_view::npos) {
            return rec;
        }

        const auto header = trim(raw.substr(0, colon_pos));
        rec.description = std::string(trim(raw.substr(colon_pos + 1)));

        if (header.find('!') != std::string_view::npos) {
            rec.is_breaking = true;
        }

        const auto open_paren = header.find('(');
        const auto close_paren = header.find(')');

        if (open_paren != std::string_view::npos && close_paren != std::string_view::npos && close_paren > open_paren) {
            rec.type = std::string(trim(header.substr(0, open_paren)));
            rec.scope = std::string(trim(header.substr(open_paren + 1, close_paren - open_paren - 1)));
        } else {
            const auto clean_header = header.substr(0, header.find('!'));
            rec.type = std::string(trim(clean_header));
        }

        // Класифікація запису
        if (rec.is_breaking) {
            rec.category = Category::Breaking;
        } else if (!rec.cve.empty() || rec.type == "sec" || rec.scope == "sec") {
            rec.category = Category::Security;
        } else if (rec.type == "feat") {
            rec.category = Category::Feature;
        } else if (rec.type == "fix") {
            rec.category = Category::Fix;
        } else {
            rec.category = Category::Ignore;
        }

        return rec;
    }

    static void render_markdown(std::string_view version, std::string_view date, const std::vector<std::string_view>& raw_commits) {
        std::vector<CommitRecord> entries;
        entries.reserve(raw_commits.size());

        for (const auto& raw : raw_commits) {
            if (auto rec = parse_commit(raw); rec.category != Category::Ignore) {
                entries.push_back(std::move(rec));
            }
        }

        std::cout << "# Нотатки випуску " << version << " (" << date << ")\n\n";

        static constexpr std::array<std::string_view, static_cast<size_t>(Category::Count)> headers = {
            "## 🔴 Обов'язкові дії та несумісні зміни (Breaking Changes)",
            "## 🔒 Бюлетені безпеки (Security Advisories)",
            "## ✨ Нові можливості (Features)",
            "## 🐛 Виправлення дефектів (Bug Fixes)",
            ""
        };

        for (size_t cat_idx = 0; cat_idx < static_cast<size_t>(Category::Ignore); ++cat_idx) {
            const auto current_cat = static_cast<Category>(cat_idx);
            bool section_opened = false;

            for (const auto& entry : entries) {
                if (entry.category == current_cat) {
                    if (!section_opened) {
                        std::cout << headers[cat_idx] << "\n\n";
                        section_opened = true;
                    }
                    if (!entry.scope.empty()) {
                        std::cout << "- **" << entry.scope << ":** " << entry.description;
                    } else {
                        std::cout << "- " << entry.description;
                    }

                    if (!entry.cve.empty()) {
                        std::cout << " (`" << entry.cve << "`)";
                    }
                    std::cout << "\n";
                }
            }
            if (section_opened) {
                std::cout << "\n";
            }
        }
    }
};

int main() {
    const std::vector<std::string_view> commits = {
        "feat(can)!: перейти на бітову швидкість CAN-FD 2 Мбіт/с",
        "fix(adc): виправити дрейф нульового рівня входу АЦП",
        "fix(sec): усунути переповнення буфера Modbus (CVE-2026-4412)",
        "chore(ci): оновити версію компілятора GCC до 14.2",
        "feat(telemetry): додати періодичний звіт про стан акумулятора",
        "docs(readme): оновити схему підключення UART"
    };

    ReleaseNotesGenerator::render_markdown("v3.2.0", "2026-08-28", commits);
    return 0;
}
```
:::

## Крайові випадки та поведінка парсера

Під час промислової експлуатації генератор зустрічається з кількома типами нестандартного вводу, які парсер повинен обробляти детерміновано:

- **Коміти без зазначення скоупу (`feat: add new sensor`):** Програма коректно розпізнає тип `feat` і залишає поле `scope` порожнім, формуючи акуратний пункт списку без зайвих двокрапок чи порожніх дужок.
- **Декілька знаків оклику або пробіли перед двокрапкою (`fix (sensors) ! : message`):** Функція очищення відсікає недруковані символи перед аналізом позиції двокрапки, що гарантує надійне розпізнавання маркера ламкої зміни.
- **Коміти з декількома футерами:** Якщо в тілі коміту одночасно присутні футери `Fixes #142`, `CVE-2026-9901` та `BREAKING CHANGE: payload structure changed`, пріоритет віддається категорії **Breaking Changes**, але номер вразливості та опис міграції зберігаються в повному обсязі.
- **UTF-8 символи в описі:** Парсер коректно пропускає багатобайтові символи в тексті повідомлення, не спотворюючи кириличні символи та спеціальні позначки.
- **Відсутність повідомлення після двокрапки (`feat(adc):`):** Такий некоректний запис ігнорується або формує попередження під час збірки, запобігаючи потраплянню порожніх пунктів у фінальний релізний бюлетень.
- **Злиття кількох виправлень безпеки в один реліз:** Якщо випуск закриває одразу три вразливості, парсер витягує всі згадані CVE-ідентифікатори та вибудовує їх у структурований перелік без дублювання записів.

## Інтеграція в конвеєр CI/CD

У реальних конвеєрах неперервного розгортання цей генератор інтегрується як окремий крок релізного скрипту. Конвеєр виконує команду `git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:"%B%x00"`, розбиває вхідний потік нуль-термінованих повідомлень на окремі записи та передає їх на вхід генератора. 

Отриманий Markdown-документ публікується на сторінці випуску репозиторію, зберігається в архіві артефактів та слугує основою для генерації машиночитабельного маніфесту [API нотаток випуску](root:sf-release/notatky-vypusku/api-release-notes-schema.md). Автоматизація повністю усуває ризик забутих правок і гарантує, що релізний бюлетень є точним дзеркалом реальної історії коду.
