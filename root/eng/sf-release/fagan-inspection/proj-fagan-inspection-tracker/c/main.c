#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define FAGAN_MAX_STR_LEN       128
#define FAGAN_MAX_DESC_LEN      256
#define FAGAN_MAX_INSPECTORS    8
#define FAGAN_INITIAL_CAPACITY  16

typedef enum {
    SEV_MINOR = 0,
    SEV_MAJOR,
    SEV_CRITICAL
} defect_severity_t;

typedef enum {
    CAT_LOGIC = 0,
    CAT_CONCURRENCY,
    CAT_HW_INTERFACE,
    CAT_RESOURCE_SAFETY,
    CAT_STANDARDS_MISRA
} defect_category_t;

typedef enum {
    PHASE_PREPARATION = 0,
    PHASE_MEETING
} detection_phase_t;

typedef enum {
    ARTIFACT_EMBEDDED_C_CPP = 0,
    ARTIFACT_SCHEMATIC,
    ARTIFACT_PCB_LAYOUT
} artifact_type_t;

typedef enum {
    DECISION_PASSED = 0,
    DECISION_REWORK_VERIFY,
    DECISION_RE_INSPECT
} exit_decision_t;

typedef struct {
    char location[FAGAN_MAX_STR_LEN];
    char description[FAGAN_MAX_DESC_LEN];
    defect_severity_t severity;
    defect_category_t category;
    detection_phase_t phase;
    int line_or_refdes_num;
} defect_entry_t;

typedef struct {
    char artifact_name[FAGAN_MAX_STR_LEN];
    char author[FAGAN_MAX_STR_LEN];
    char moderator[FAGAN_MAX_STR_LEN];
    char reader[FAGAN_MAX_STR_LEN];
    char inspectors[FAGAN_MAX_INSPECTORS][FAGAN_MAX_STR_LEN];
    int inspector_count;
    artifact_type_t artifact_type;
    size_t artifact_size_units; /* Кількість LOC або компонентів */
    double prep_time_person_hours;
    double meeting_duration_minutes;
    defect_entry_t *defects;
    size_t defect_count;
    size_t defect_capacity;
} fagan_session_t;

typedef struct {
    double inspection_rate_per_hour;
    double defect_density_per_kloc;
    double weighted_defect_score;
    size_t critical_count;
    size_t major_count;
    size_t minor_count;
    size_t prep_findings_count;
    size_t meeting_findings_count;
    exit_decision_t decision;
    bool rate_warning;
} inspection_metrics_t;

static const char* severity_to_str(defect_severity_t sev) {
    switch (sev) {
        case SEV_CRITICAL: return "CRITICAL";
        case SEV_MAJOR:    return "MAJOR";
        case SEV_MINOR:    return "MINOR";
        default:           return "UNKNOWN";
    }
}

static const char* category_to_str(defect_category_t cat) {
    switch (cat) {
        case CAT_LOGIC:           return "Logic/Algorithm";
        case CAT_CONCURRENCY:     return "Concurrency/ISR";
        case CAT_HW_INTERFACE:    return "Hardware Interface";
        case CAT_RESOURCE_SAFETY: return "Resource/Memory Safety";
        case CAT_STANDARDS_MISRA: return "Standards/MISRA";
        default:                  return "Unknown";
    }
}

static const char* decision_to_str(exit_decision_t dec) {
    switch (dec) {
        case DECISION_PASSED:        return "PASSED (Artifact Approved)";
        case DECISION_REWORK_VERIFY: return "REWORK (Verify fixes by Moderator)";
        case DECISION_RE_INSPECT:    return "RE-INSPECT (Mandatory Full Re-session)";
        default:                     return "UNKNOWN";
    }
}

bool fagan_session_init(fagan_session_t *session,
                        const char *artifact_name,
                        const char *author,
                        const char *moderator,
                        const char *reader,
                        artifact_type_t type,
                        size_t size_units,
                        double meeting_mins) {
    if (!session || !artifact_name || !author || !moderator || !reader || size_units == 0) {
        return false;
    }

    memset(session, 0, sizeof(fagan_session_t));
    strncpy(session->artifact_name, artifact_name, FAGAN_MAX_STR_LEN - 1);
    strncpy(session->author, author, FAGAN_MAX_STR_LEN - 1);
    strncpy(session->moderator, moderator, FAGAN_MAX_STR_LEN - 1);
    strncpy(session->reader, reader, FAGAN_MAX_STR_LEN - 1);
    session->artifact_type = type;
    session->artifact_size_units = size_units;
    session->meeting_duration_minutes = meeting_mins;

    session->defects = (defect_entry_t*)malloc(FAGAN_INITIAL_CAPACITY * sizeof(defect_entry_t));
    if (!session->defects) {
        return false;
    }
    session->defect_capacity = FAGAN_INITIAL_CAPACITY;
    session->defect_count = 0;
    return true;
}

bool fagan_session_add_inspector(fagan_session_t *session, const char *inspector_name) {
    if (!session || !inspector_name) return false;
    if (session->inspector_count >= FAGAN_MAX_INSPECTORS) return false;

    strncpy(session->inspectors[session->inspector_count], inspector_name, FAGAN_MAX_STR_LEN - 1);
    session->inspector_count++;
    return true;
}

void fagan_session_add_prep_time(fagan_session_t *session, double person_hours) {
    if (session && person_hours > 0.0) {
        session->prep_time_person_hours += person_hours;
    }
}

bool fagan_session_record_defect(fagan_session_t *session,
                                 const char *location,
                                 int line_or_refdes,
                                 defect_severity_t severity,
                                 defect_category_t category,
                                 detection_phase_t phase,
                                 const char *description) {
    if (!session || !location || !description) return false;

    if (session->defect_count >= session->defect_capacity) {
        size_t new_cap = session->defect_capacity * 2;
        defect_entry_t *new_arr = (defect_entry_t*)realloc(session->defects,
                                                          new_cap * sizeof(defect_entry_t));
        if (!new_arr) return false;
        session->defects = new_arr;
        session->defect_capacity = new_cap;
    }

    defect_entry_t *entry = &session->defects[session->defect_count];
    strncpy(entry->location, location, FAGAN_MAX_STR_LEN - 1);
    entry->line_or_refdes_num = line_or_refdes;
    entry->severity = severity;
    entry->category = category;
    entry->phase = phase;
    strncpy(entry->description, description, FAGAN_MAX_DESC_LEN - 1);

    session->defect_count++;
    return true;
}

bool fagan_session_calculate_metrics(const fagan_session_t *session,
                                    inspection_metrics_t *metrics) {
    if (!session || !metrics || session->artifact_size_units == 0) return false;

    memset(metrics, 0, sizeof(inspection_metrics_t));

    if (session->meeting_duration_minutes > 0.0) {
        metrics->inspection_rate_per_hour =
            ((double)session->artifact_size_units * 60.0) / session->meeting_duration_minutes;
    } else {
        metrics->inspection_rate_per_hour = 0.0;
    }

    /* Поріг швидкості для вбудованих систем: оптимально 100..150 LOC/год */
    if (metrics->inspection_rate_per_hour > 220.0 || metrics->inspection_rate_per_hour < 40.0) {
        metrics->rate_warning = true;
    }

    for (size_t i = 0; i < session->defect_count; ++i) {
        const defect_entry_t *d = &session->defects[i];
        switch (d->severity) {
            case SEV_CRITICAL:
                metrics->critical_count++;
                metrics->weighted_defect_score += 10.0;
                break;
            case SEV_MAJOR:
                metrics->major_count++;
                metrics->weighted_defect_score += 3.0;
                break;
            case SEV_MINOR:
                metrics->minor_count++;
                metrics->weighted_defect_score += 1.0;
                break;
        }

        if (d->phase == PHASE_PREPARATION) {
            metrics->prep_findings_count++;
        } else {
            metrics->meeting_findings_count++;
        }
    }

    metrics->defect_density_per_kloc =
        ((double)session->defect_count * 1000.0) / (double)session->artifact_size_units;

    /* Визначення фінального рішення модератора */
    if (metrics->critical_count > 0 || metrics->weighted_defect_score >= 25.0) {
        metrics->decision = DECISION_RE_INSPECT;
    } else if (metrics->major_count > 0 || metrics->minor_count > 0) {
        metrics->decision = DECISION_REWORK_VERIFY;
    } else {
        metrics->decision = DECISION_PASSED;
    }

    return true;
}

void fagan_session_print_report(const fagan_session_t *session,
                                const inspection_metrics_t *metrics) {
    if (!session || !metrics) return;

    printf("================================================================================\n");
    printf("                  ПРОТОКОЛ ФОРМАЛЬНОЇ ІНСПЕКЦІЇ ФАГАНА                          \n");
    printf("================================================================================\n");
    printf("Артефакт:        %s\n", session->artifact_name);
    printf("Автор:           %s\n", session->author);
    printf("Модератор:       %s\n", session->moderator);
    printf("Читець:          %s\n", session->reader);
    printf("Інспектори (%d):  ", session->inspector_count);
    for (int i = 0; i < session->inspector_count; ++i) {
        printf("%s%s", session->inspectors[i], (i == session->inspector_count - 1) ? "" : ", ");
    }
    printf("\n");
    printf("Розмір об'єкта:  %zu %s\n", session->artifact_size_units,
           (session->artifact_type == ARTIFACT_EMBEDDED_C_CPP) ? "LOC" : "Компонентів");
    printf("Час засідання:   %.1f хв | Трудовитрати підготовки: %.1f людино-годин\n",
           session->meeting_duration_minutes, session->prep_time_person_hours);
    printf("--------------------------------------------------------------------------------\n");
    printf("МЕТРИКИ ЯКОСТІ ТА ЕФЕКТИВНОСТІ:\n");
    printf("  Швидкість інспекції: %.1f од/год %s\n",
           metrics->inspection_rate_per_hour,
           metrics->rate_warning ? "[УВАГА: темп поза оптимальними межами 100-150!]" : "[НОРМА]");
    printf("  Знайдено дефектів:   %zu (Підготовка: %zu, Засідання: %zu)\n",
           session->defect_count, metrics->prep_findings_count, metrics->meeting_findings_count);
    printf("  Розподіл критичності: CRITICAL: %zu | MAJOR: %zu | MINOR: %zu\n",
           metrics->critical_count, metrics->major_count, metrics->minor_count);
    printf("  Щільність дефектів:  %.2f дефектів / KLOC\n", metrics->defect_density_per_kloc);
    printf("  Зважений бал (WDS):  %.1f\n", metrics->weighted_defect_score);
    printf("--------------------------------------------------------------------------------\n");
    printf("РЕЗУЛЬТАТ (Exit Criteria): %s\n", decision_to_str(metrics->decision));
    printf("================================================================================\n");
    printf("ЗАРЕЄСТРОВАНІ ДЕФЕКТИ:\n");
    for (size_t i = 0; i < session->defect_count; ++i) {
        const defect_entry_t *d = &session->defects[i];
        printf("[%02zu] %-8s | %-16s | %s:%d\n     Опис: %s\n",
               i + 1,
               severity_to_str(d->severity),
               category_to_str(d->category),
               d->location,
               d->line_or_refdes_num,
               d->description);
    }
    printf("================================================================================\n");
}

void fagan_session_free(fagan_session_t *session) {
    if (session) {
        if (session->defects) {
            free(session->defects);
            session->defects = NULL;
        }
        session->defect_count = 0;
        session->defect_capacity = 0;
    }
}

int main(void) {
    fagan_session_t session;
    if (!fagan_session_init(&session,
                            "drivers/spi_dma_stm32f4.c",
                            "О. Ковальчук (Firmware)",
                            "І. Бондар (Lead Moderator)",
                            "В. Ткаченко (Reader)",
                            ARTIFACT_EMBEDDED_C_CPP,
                            380,   /* 380 LOC драйвера */
                            150.0  /* 2.5 години = 150 хв */)) {
        fprintf(stderr, "Помилка ініціалізації сесії інспекції\n");
        return 1;
    }

    fagan_session_add_inspector(&session, "М. Шевченко (Safety Engineer)");
    fagan_session_add_inspector(&session, "Д. Мельник (Hardware Architect)");
    fagan_session_add_prep_time(&session, 3.5);

    /* Фіксація дефектів, знайдених під час підготовки та засідання */
    fagan_session_record_defect(&session, "spi_dma_stm32f4.c", 142,
                                SEV_CRITICAL, CAT_CONCURRENCY, PHASE_PREPARATION,
                                "Відсутній memory barrier перед запуском DMA; гонка кешу та пам'яті");

    fagan_session_record_defect(&session, "spi_dma_stm32f4.c", 89,
                                SEV_MAJOR, CAT_HW_INTERFACE, PHASE_MEETING,
                                "Не скидається прапорець TXE перед читанням RXNE на шині SPI; зависання");

    fagan_session_record_defect(&session, "spi_dma_stm32f4.c", 215,
                                SEV_MINOR, CAT_STANDARDS_MISRA, PHASE_PREPARATION,
                                "Порушення MISRA Rule 10.4: неявне приведення знакового int до uint32_t");

    inspection_metrics_t metrics;
    if (fagan_session_calculate_metrics(&session, &metrics)) {
        fagan_session_print_report(&session, &metrics);
    }

    fagan_session_free(&session);
    return 0;
}
