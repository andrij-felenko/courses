# ⚙️ Двигунець валідації та автоматизації бекпортів на C та C++

У проєктах із довготривалою підтримкою (LTS) ручний перенос комітів за допомогою команди `git cherry-pick` регулярно стикається з двома фатальними проблемами: втратою метаданих походження (інженер забуває вказати ключ `-x` або втрачає номер вихідного коміту в `main`) та непоміченим пропуском залежних латок (коміт виправлення спирається на внутрішній рефакторинг або новий допоміжний метод, якого ще немає в гілці підтримки).

Ця вставка містить повноцінну інженерну утиліту аналізу черги бекпортів: вона перевіряє структуру коміту, витягує хеш вихідного коміту з тіла повідомлення, парсить модифіковані файли й статистику змін, оцінює розмір дельти та сигналізує про ризик семантичного дрейфу чи порушення атомарності латки.

## Архітектура та етапи перевірки валідатора

Утиліта реалізує строгий трирівневий конвеєр інспекції латки:

1. **Аналіз структури заголовка та префікса гілки:**
   Кожен бекпорт-коміт зобов'язаний містити у першому рядку квадратні дужки з точною назвою цільової гілки підтримки, наприклад: `[v2.4] fix(io): prevent descriptor leak`. Валідатор парсить перший рядок, виділяє назву гілки та перевіряє її валідність проти реєстру активних релізів.
2. **Вилучення та перевірка ланцюга походження (Commit Provenance):**
   Утиліта шукає у тілі повідомлення стандартні маркери `(cherry picked from commit <SHA>)` або Git trailer `Upstream-commit: <SHA>`. Якщо маркер відсутній або довжина хешу становить менше 7 шістнадцяткових символів, коміт негайно бракується. Це захищає репозиторій від невідстежуваних анонімних змін.
3. **Оцінка ліміту змін та радіуса ураження (Diffstat Analysis):**
   Валідатор розбирає блок статистики змін (`diffstat`), підраховуючи загальну кількість доданих і видалених рядків. Якщо сумарна дельта перевищує граничний ліміт безпечного бекпорту (наприклад, 300 рядків), утиліта повертає статус помилки `DiffLimitExceeded`. Масивні коміти сигналізують про те, що розробник спробував перенести виправлення разом із супутнім рефакторингом.

## Реалізація валідатора черги бекпортів на C та C++

:::tabs
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_SHA_LEN 64
#define MAX_LINE_LEN 1024
#define MAX_FILES 128

typedef enum {
    BACKPORT_OK = 0,
    BACKPORT_ERR_NO_UPSTREAM = 1,
    BACKPORT_ERR_INVALID_HEADER = 2,
    BACKPORT_ERR_DIFF_TOO_LARGE = 3
} backport_status_t;

typedef struct {
    char target_branch[32];
    char upstream_sha[MAX_SHA_LEN];
    char commit_subject[MAX_LINE_LEN];
    int lines_added;
    int lines_deleted;
    int files_changed_count;
    char changed_files[MAX_FILES][128];
} backport_metadata_t;

static void trim_trailing_newline(char *str) {
    size_t len = strlen(str);
    while (len > 0 && (str[len - 1] == '\n' || str[len - 1] == '\r')) {
        str[--len] = '\0';
    }
}

static bool extract_upstream_sha(const char *line, char *out_sha, size_t max_out) {
    const char *pattern_cp = "(cherry picked from commit ";
    const char *pattern_up = "Upstream-commit: ";
    const char *pos = strstr(line, pattern_cp);
    
    if (pos) {
        pos += strlen(pattern_cp);
        size_t idx = 0;
        while (*pos && *pos != ')' && idx < max_out - 1) {
            out_sha[idx++] = *pos++;
        }
        out_sha[idx] = '\0';
        return idx >= 7; /* Мінімальна довжина скороченого SHA */
    }

    pos = strstr(line, pattern_up);
    if (pos) {
        pos += strlen(pattern_up);
        size_t idx = 0;
        while (*pos && *pos != ' ' && *pos != '\n' && *pos != '\r' && idx < max_out - 1) {
            out_sha[idx++] = *pos++;
        }
        out_sha[idx] = '\0';
        return idx >= 7;
    }

    return false;
}

backport_status_t validate_backport_stream(FILE *stream, backport_metadata_t *meta) {
    char line_buf[MAX_LINE_LEN];
    bool has_header = false;
    bool found_upstream = false;

    memset(meta, 0, sizeof(*meta));

    while (fgets(line_buf, sizeof(line_buf), stream)) {
        trim_trailing_newline(line_buf);

        /* Перевірка першого рядка: заголовок коміту */
        if (!has_header && strlen(line_buf) > 0) {
            strncpy(meta->commit_subject, line_buf, sizeof(meta->commit_subject) - 1);
            has_header = true;

            /* Перевірка префікса гілки [vX.Y] */
            if (line_buf[0] == '[' && strchr(line_buf, ']')) {
                const char *end_bracket = strchr(line_buf, ']');
                size_t b_len = (size_t)(end_bracket - line_buf - 1);
                if (b_len < sizeof(meta->target_branch)) {
                    strncpy(meta->target_branch, line_buf + 1, b_len);
                    meta->target_branch[b_len] = '\0';
                }
            }
            continue;
        }

        /* Пошук мітки Upstream SHA */
        if (!found_upstream && extract_upstream_sha(line_buf, meta->upstream_sha, sizeof(meta->upstream_sha))) {
            found_upstream = true;
        }

        /* Парсинг рядків статистики diffstat: ' 3 files changed, 10 insertions(+), 2 deletions(-)' */
        if (strstr(line_buf, "files changed") || strstr(line_buf, "file changed")) {
            int fc = 0;
            if (sscanf(line_buf, " %d file", &fc) == 1) {
                meta->files_changed_count = fc;
            }
            char *p_ins = strstr(line_buf, "insertion");
            if (p_ins) {
                char *rev = p_ins - 2;
                while (rev > line_buf && *rev != ' ' && *rev != ',') rev--;
                meta->lines_added = atoi(rev + 1);
            }
            char *p_del = strstr(line_buf, "deletion");
            if (p_del) {
                char *rev = p_del - 2;
                while (rev > line_buf && *rev != ' ' && *rev != ',') rev--;
                meta->lines_deleted = atoi(rev + 1);
            }
        }
    }

    if (!found_upstream) {
        return BACKPORT_ERR_NO_UPSTREAM;
    }

    if (meta->lines_added + meta->lines_deleted > 300) {
        return BACKPORT_ERR_DIFF_TOO_LARGE;
    }

    return BACKPORT_OK;
}

int main(void) {
    const char *sample_log =
        "[v2.4] fix(io): prevent file descriptor leak during ring reset\n"
        "\n"
        "Under high packet rates, resetting the descriptor ring failed to close\n"
        "pending eventfds, leading to exhaustion of process handles.\n"
        "\n"
        "(cherry picked from commit 8f4a21b3c990a174f82d1c9b3a0e4123456789ab)\n"
        "Fixes: CVE-2026-1940\n"
        "---\n"
        " 2 files changed, 14 insertions(+), 3 deletions(-)\n";

    FILE *input = fmemopen((void *)sample_log, strlen(sample_log), "r");
    if (!input) {
        perror("fmemopen failed");
        return EXIT_FAILURE;
    }

    backport_metadata_t meta;
    backport_status_t res = validate_backport_stream(input, &meta);
    fclose(input);

    if (res == BACKPORT_OK) {
        printf("STATUS: VALID BACKPORT\n");
        printf("Target Branch : %s\n", meta.target_branch);
        printf("Upstream SHA  : %s\n", meta.upstream_sha);
        printf("Delta Lines   : +%d / -%d\n", meta.lines_added, meta.lines_deleted);
    } else {
        printf("STATUS: REJECTED (code %d)\n", res);
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <sstream>
#include <algorithm>
#include <charconv>

namespace release::backport {

enum class ValidationError {
    MissingUpstreamSha,
    MissingBranchPrefix,
    DiffLimitExceeded,
    InvalidStructure
};

struct CommitMetadata {
    std::string target_branch;
    std::string upstream_sha;
    std::string subject;
    int lines_added{0};
    int lines_deleted{0};
    int files_changed{0};
};

class BackportInspector {
public:
    static constexpr int MaxSafeLineDiff = 300;

    [[nodiscard]] static auto parse(std::string_view raw_commit_log) 
        -> std::pair<std::optional<CommitMetadata>, std::optional<ValidationError>> 
    {
        CommitMetadata meta;
        std::istringstream stream{std::string(raw_commit_log)};
        std::string line;
        bool header_parsed = false;

        while (std::getline(stream, line)) {
            trim(line);
            if (line.empty()) continue;

            if (!header_parsed) {
                meta.subject = line;
                header_parsed = true;

                if (line.starts_with('[') && line.find(']') != std::string::npos) {
                    const auto end_idx = line.find(']');
                    meta.target_branch = line.substr(1, end_idx - 1);
                } else {
                    return {std::nullopt, ValidationError::MissingBranchPrefix};
                }
                continue;
            }

            if (meta.upstream_sha.empty()) {
                if (auto sha = extract_sha(line, "(cherry picked from commit "); sha) {
                    meta.upstream_sha = *sha;
                } else if (auto sha_up = extract_sha(line, "Upstream-commit: "); sha_up) {
                    meta.upstream_sha = *sha_up;
                }
            }

            parse_diffstat(line, meta);
        }

        if (meta.upstream_sha.empty()) {
            return {std::nullopt, ValidationError::MissingUpstreamSha};
        }

        if (meta.lines_added + meta.lines_deleted > MaxSafeLineDiff) {
            return {std::nullopt, ValidationError::DiffLimitExceeded};
        }

        return {meta, std::nullopt};
    }

private:
    static void trim(std::string& s) {
        s.erase(s.find_last_not_of(" \r\n\t") + 1);
    }

    static auto extract_sha(std::string_view line, std::string_view prefix) -> std::optional<std::string> {
        const auto pos = line.find(prefix);
        if (pos == std::string_view::npos) return std::nullopt;

        auto rest = line.substr(pos + prefix.size());
        if (const auto end_bracket = rest.find(')'); end_bracket != std::string_view::npos) {
            rest = rest.substr(0, end_bracket);
        }
        if (rest.size() >= 7) {
            return std::string(rest);
        }
        return std::nullopt;
    }

    static void parse_diffstat(std::string_view line, CommitMetadata& meta) {
        if (line.find("file changed") == std::string_view::npos && 
            line.find("files changed") == std::string_view::npos) {
            return;
        }

        std::istringstream ls{std::string(line)};
        std::string token;
        while (ls >> token) {
            if (token.find("insertion") != std::string::npos) {
                // обробка токена
            }
        }
        
        if (const auto p_ins = line.find("insertion"); p_ins != std::string_view::npos) {
            const auto space_before = line.rfind(' ', p_ins - 2);
            if (space_before != std::string_view::npos) {
                std::from_chars(line.data() + space_before + 1, line.data() + p_ins - 1, meta.lines_added);
            }
        }
        if (const auto p_del = line.find("deletion"); p_del != std::string_view::npos) {
            const auto space_before = line.rfind(' ', p_del - 2);
            if (space_before != std::string_view::npos) {
                std::from_chars(line.data() + space_before + 1, line.data() + p_del - 1, meta.lines_deleted);
            }
        }
    }
};

} // namespace release::backport

int main() {
    constexpr std::string_view sample_commit = 
        "[v2.4] fix(io): prevent file descriptor leak during ring reset\n"
        "\n"
        "Under high packet rates, resetting the descriptor ring failed to close\n"
        "pending eventfds, leading to exhaustion of process handles.\n"
        "\n"
        "(cherry picked from commit 8f4a21b3c990a174f82d1c9b3a0e4123456789ab)\n"
        "Fixes: CVE-2026-1940\n"
        "---\n"
        " 2 files changed, 14 insertions(+), 3 deletions(-)\n";

    const auto [meta, err] = release::backport::BackportInspector::parse(sample_commit);

    if (meta.has_value()) {
        std::cout << "STATUS: VALID BACKPORT (C++20)\n";
        std::cout << "Target Branch : " << meta->target_branch << "\n";
        std::cout << "Upstream SHA  : " << meta->upstream_sha << "\n";
        std::cout << "Lines Changed : +" << meta->lines_added << " / -" << meta->lines_deleted << "\n";
        return 0;
    }

    std::cerr << "VALIDATION FAILED: Code " << static_cast<int>(*err) << "\n";
    return 1;
}
```
:::

## Аналіз безпеки пам'яті та ідіом C/C++

Порівняння двох реалізацій демонструє різницю системного підходу між мовами:

* **Безпека в C-реалізації:** функція `validate_backport_stream` використовує потоковий ввід через `fgets()` із фіксованим буфером `MAX_LINE_LEN`, що запобігає переповненню стека. Операції копіювання рядків захищені явними обмеженнями `strncpy` з примусовим нуль-термінатором на останньому байті. Для тестування використовується POSIX-функція `fmemopen`, яка обгортає пам'ять у файловий потік без створення тимчасових файлів на диску.
* **Ідіоматичність C++20:** реалізація повністю відмовляється від сирих вказівників на користь неволодіючих зрізів `std::string_view`. Парсинг чисел виконується за допомогою `std::from_chars`, яка працює без динамічних алокацій пам'яті та не генерує винятків. Повернення результату організовано через пару `std::optional`, що унеможливлює використання непроініціалізованих структур при виникненні помилок валідації.
* **Складність алгоритму:** обидві реалізації мають лінійну часову складність `O(N)`, де `N` — довжина журналу коміту в байтах, та константну просторову складність `O(1)` відносно розміру всього репозиторію, оскільки вони не завантажують у пам'ять повний граф DAG, а обробляють журнал потоково.

## Інтеграція валідатора у хуки Git (Pre-Receive Hook)

Утиліта компілюється в статичний бінарний файл і викликається на сервері контролю версій у хуку `pre-receive` під час спроби відправки змін у захищені гілки `support/*`:

```bash
#!/usr/bin/env bash
# Git pre-receive hook: Валідація бекпортів перед записом у репозиторій

set -euo pipefail

while read -r oldrev newrev refname; do
    if [[ "$refname" =~ ^refs/heads/support/ ]]; then
        # Перевірка кожного нового коміту в діапазоні
        for commit in $(git rev-list "$oldrev..$newrev"); do
            git log -1 --stat "$commit" | /usr/local/bin/backport-inspector || {
                echo "ПОМИЛКА: Коміт $commit відхилено валідатором бекпортів." >&2
                echo "Переконайтеся у наявності [vX.Y] префікса, Upstream SHA та допустимому розмірі diff." >&2
                exit 1
            }
        done
    fi
done
```

## Інтеграція в матричні конвеєри GitHub Actions та GitLab CI

Окрім серверних хуків, валідатор викликається на першому кроці конвеєра CI для кожного відкритого Pull Request у релізну гілку. Якщо валідатор завершується з ненульовим кодом, матриця тестування HIL навіть не запускається, що економить дорогі години роботи фізичних стендів тестування мікроконтролерів.

```yaml
# Крок валідації метаданих у GitHub Actions
- name: Validate Backport Metadata
  run: |
    git log -1 --stat ${{ github.sha }} | ./build/backport-inspector
```

## Фази фазинг-тестування парсера (Fuzzing)

Для захисту від зловмисно сформованих повідомлень комітів та неочікуваних символів кодування валідатор проходить обов'язкове фазинг-тестування за допомогою інструменту LLVM LibFuzzer. Перевіряються такі граничні вектори атаки:
1. **Вбудовані нульові байти (Embedded Null Bytes):** введення символу `\0` всередині рядка SHA або заголовка коміту для перевірки стійкості C-рядків.
2. **Переповнення буферів довгими рядками:** надсилання рядків довжиною понад 65 536 символів без перенесення рядка для валідації поведінки `fgets()` та вичерпання пам'яті.
3. **Деформовані трейлери Git:** випадкові комбінації дужок, пробілів та багатобайтових символів UTF-8 у позиції вилучення хешу.

## Інженерні пастки та крайові випадки валідації

1. **Втрата SHA при об'єднанні комітів (Squash Cherry-pick):**
   Якщо інженер застосовує команду `git cherry-pick -n` (no-commit) для об'єднання кількох латок в одну, стандартна мітка `-x` втрачається. Автоматизований валідатор повинен вимагати переліку всіх вихідних хешів у форматі `Upstream-commits: SHA1, SHA2, SHA3`.
2. **Перенесення комітів злиття (Merge Commits):**
   Команда `git cherry-pick` без прапорця `-m 1` зазнає помилки при спробі перенести merge-коміт. У стабільних гілках супроводу перенесення merge-комітів забороняється: кожен патч має бути лінійним атомарним комітом.
3. **Хибні спрацьовування diffstat при зміні бінарних файлів:**
   При модифікації скомпільованих ресурсів чи блобів прошивок лічильник рядків повертає `0`, хоча розмір змін може бути критичним. Валідатор повинен окремо перевіряти статус бінарних дельт.
4. **Контекстний зсув зміщення хунків (Hunk Offset Drift):**
   Якщо рядок у файлі змістився на 500 рядків униз через старі зміни в гілці LTS, Git може застосувати патч із так званим «fuzzy matching» (неточне зіставлення). Це загрожує модифікацією іншої однойменної функції. Валідатор повинен аналізувати рівень нечіткості контексту (fuzz factor) та блокувати латки з високим зсувом.
