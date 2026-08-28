#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_LINE_LEN 1024
#define MAX_FIELD_LEN 128
#define MAX_ITEMS 256

typedef struct {
    char designator[MAX_FIELD_LEN];
    char mpn[MAX_FIELD_LEN];
    char mfr[MAX_FIELD_LEN];
    char value[MAX_FIELD_LEN];
    char footprint[MAX_FIELD_LEN];
    char alt_mpn[MAX_FIELD_LEN];
    double rail_voltage;
    double rated_voltage;
    bool is_capacitor;
} BomEntry;

typedef struct {
    int total_components;
    int unique_feeders;
    int missing_alt_count;
    int derating_violations;
    int invalid_entries;
} AuditReport;

static void trim_quotes(char *str) {
    size_t len = strlen(str);
    if (len >= 2 && str[0] == '"' && str[len - 1] == '"') {
        memmove(str, str + 1, len - 2);
        str[len - 2] = '\0';
    }
}

static bool parse_csv_line(char *line, BomEntry *entry) {
    char *token;
    char *rest = line;
    int col = 0;

    memset(entry, 0, sizeof(BomEntry));

    while ((token = strtok_r(rest, ",", &rest))) {
        trim_quotes(token);
        switch (col) {
            case 0: strncpy(entry->designator, token, MAX_FIELD_LEN - 1); break;
            case 1: strncpy(entry->mpn, token, MAX_FIELD_LEN - 1); break;
            case 2: strncpy(entry->mfr, token, MAX_FIELD_LEN - 1); break;
            case 3: strncpy(entry->value, token, MAX_FIELD_LEN - 1); break;
            case 4: strncpy(entry->footprint, token, MAX_FIELD_LEN - 1); break;
            case 5: strncpy(entry->alt_mpn, token, MAX_FIELD_LEN - 1); break;
            case 6: entry->rail_voltage = atof(token); break;
            case 7: entry->rated_voltage = atof(token); break;
            default: break;
        }
        col++;
    }

    if (col < 5 || strlen(entry->mpn) == 0 || strlen(entry->designator) == 0) {
        return false;
    }

    if (entry->designator[0] == 'C' || entry->designator[0] == 'c') {
        entry->is_capacitor = true;
    }

    return true;
}

AuditReport audit_bom(BomEntry *entries, int count) {
    AuditReport rep = {0};
    rep.total_components = count;
    rep.unique_feeders = count;

    printf("\n=== РЕЗУЛЬТАТИ ІНЖЕНЕРНОГО АУДИТУ BOM ===\n");

    for (int i = 0; i < count; ++i) {
        /* Перевірка наявності альтернативного джерела */
        if (strlen(entries[i].alt_mpn) == 0) {
            printf("[ПОПЕРЕДЖЕННЯ AML] Позиція %s (MPN: %s) не має другого джерела!\n",
                   entries[i].designator, entries[i].mpn);
            rep.missing_alt_count++;
        }

        /* Перевірка запасу за напругою для конденсаторів (Derating Rule >= 1.5x) */
        if (entries[i].is_capacitor && entries[i].rail_voltage > 0.0) {
            double margin_ratio = entries[i].rated_voltage / entries[i].rail_voltage;
            if (margin_ratio < 1.5) {
                printf("[ДЕФЕКТ НАПРУГИ] Конденсатор %s: номінал %.1fВ для шини %.1fВ (запас %.2f < 1.50)!\n",
                       entries[i].designator, entries[i].rated_voltage,
                       entries[i].rail_voltage, margin_ratio);
                rep.derating_violations++;
            }
        }
    }

    return rep;
}

int main(void) {
    const char *csv_sample =
        "Designator,MPN,Manufacturer,Value,Footprint,Alt_MPN,Rail_V,Rated_V\n"
        "C1,GRM188R71E104KA01D,Murata,100nF,0603,CL10B104KB8NNNC,3.3,25.0\n"
        "C2,GRM155R60J106ME47D,Murata,10uF,0402,,5.0,6.3\n"
        "R1,RC0603FR-0710KL,Yageo,10k,0603,CRCW060310K0FKEA,3.3,50.0\n"
        "U1,STM32G030K8T6,STMicroelectronics,MCU_64K,LQFP-32,,3.3,3.6\n";

    char buffer[MAX_LINE_LEN];
    BomEntry entries[MAX_ITEMS];
    int count = 0;

    char *csv_copy = strdup(csv_sample);
    char *line = strtok(csv_copy, "\n");
    bool is_header = true;

    while (line != NULL) {
        if (is_header) {
            is_header = false;
        } else {
            strncpy(buffer, line, sizeof(buffer) - 1);
            buffer[sizeof(buffer) - 1] = '\0';
            if (parse_csv_line(buffer, &entries[count])) {
                count++;
            }
        }
        line = strtok(NULL, "\n");
    }
    free(csv_copy);

    AuditReport report = audit_bom(entries, count);

    printf("\n--- ПІДСУМОК АУДИТУ ---\n");
    printf("Перевірено позицій: %d\n", report.total_components);
    printf("Порушень запасу напруги: %d\n", report.derating_violations);
    printf("Позицій без Multi-Source: %d\n", report.missing_alt_count);

    if (report.derating_violations > 0 || report.missing_alt_count > 0) {
        printf("СТАТУС: ПОТРІБНЕ ДООПРАЦЮВАННЯ СПЕЦИФІКАЦІЇ\n");
    } else {
        printf("СТАТУС: BOM ЗАТВЕРДЖЕНО ДО ВИРОБНИЦТВА\n");
    }

    return 0;
}
