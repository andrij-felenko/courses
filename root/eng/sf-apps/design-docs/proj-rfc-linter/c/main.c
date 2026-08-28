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
