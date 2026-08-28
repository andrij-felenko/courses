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
