#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define MAX_INSPECTION_SAMPLES 64
#define MAX_DEFECT_ENTRIES     32

typedef enum {
    TEST_LEVEL_1_PACKAGING_DOCS = 1,
    TEST_LEVEL_2_OPTICAL_SOLVENT = 2,
    TEST_LEVEL_3_XRAY_XRF = 3,
    TEST_LEVEL_4_DECAP_DIE = 4,
    TEST_LEVEL_5_ELECTRICAL_ASA = 5
} InspectionLevel;

typedef enum {
    DEFECT_NONE = 0,
    DEFECT_BLACKTOPPING_DETECTED,
    DEFECT_SOLVENT_MARK_REMOVED,
    DEFECT_PIN1_INDENT_MODIFIED,
    DEFECT_XRAY_DIE_SIZE_MISMATCH,
    DEFECT_XRAY_BOND_WIRE_DEFECT,
    DEFECT_XRF_LEAD_ROHS_VIOLATION,
    DEFECT_DECAP_DIE_LOGO_ABSENT,
    DEFECT_DECAP_WRONG_MASK_ID,
    DEFECT_ASA_SIGNATURE_FAILED,
    DEFECT_QUIESCENT_CURRENT_HIGH
} CounterfeitDefectType;

typedef enum {
    DISPOSITION_ACCEPT = 0,
    DISPOSITION_SUSPECT_HOLD,
    DISPOSITION_QUARANTINE_REJECT
} LotDisposition;

typedef struct {
    uint32_t sample_id;
    InspectionLevel level;
    CounterfeitDefectType defect;
    float measured_metric; /* Відхилення в %, мкА, або товщина */
    char notes[64];
} SampleTestRecord;

typedef struct {
    char lot_number[32];
    char part_number[32];
    char manufacturer[32];
    uint32_t lot_size;
    uint32_t sample_size;
    uint32_t failed_samples_count;
    float calculated_risk_index; /* 0.0 .. 1.0 */
    LotDisposition final_disposition;
    SampleTestRecord records[MAX_DEFECT_ENTRIES];
    uint32_t records_count;
} LotInspectionDossier;

/* Розрахунок інтегрального індексу ризику партії */
float calculate_lot_risk_index(const LotInspectionDossier* dossier) {
    if (!dossier || dossier->sample_size == 0) return 1.0f;

    float weighted_defect_score = 0.0f;

    for (uint32_t i = 0; i < dossier->records_count; ++i) {
        switch (dossier->records[i].defect) {
            case DEFECT_DECAP_WRONG_MASK_ID:
            case DEFECT_DECAP_DIE_LOGO_ABSENT:
                weighted_defect_score += 1.0f; /* 100% фальсифікат */
                break;
            case DEFECT_BLACKTOPPING_DETECTED:
            case DEFECT_SOLVENT_MARK_REMOVED:
            case DEFECT_XRAY_DIE_SIZE_MISMATCH:
                weighted_defect_score += 0.8f;
                break;
            case DEFECT_ASA_SIGNATURE_FAILED:
            case DEFECT_XRF_LEAD_ROHS_VIOLATION:
                weighted_defect_score += 0.6f;
                break;
            case DEFECT_QUIESCENT_CURRENT_HIGH:
            case DEFECT_PIN1_INDENT_MODIFIED:
                weighted_defect_score += 0.4f;
                break;
            default:
                break;
        }
    }

    float risk = (weighted_defect_score / (float)dossier->sample_size);
    if (risk > 1.0f) risk = 1.0f;
    return risk;
}

/* Додавання виявленого дефекту у досьє партії */
bool add_inspection_defect(
    LotInspectionDossier* dossier,
    uint32_t sample_id,
    InspectionLevel level,
    CounterfeitDefectType defect,
    float metric,
    const char* notes
) {
    if (!dossier || dossier->records_count >= MAX_DEFECT_ENTRIES) return false;

    SampleTestRecord* rec = &dossier->records[dossier->records_count++];
    rec->sample_id = sample_id;
    rec->level = level;
    rec->defect = defect;
    rec->measured_metric = metric;
    snprintf(rec->notes, sizeof(rec->notes), "%s", notes ? notes : "");

    if (defect != DEFECT_NONE) {
        dossier->failed_samples_count++;
    }

    dossier->calculated_risk_index = calculate_lot_risk_index(dossier);

    /* Оновлення рішення за стандартом Zero-Defect (C = 0) */
    if (dossier->calculated_risk_index > 0.15f || dossier->failed_samples_count > 0) {
        dossier->final_disposition = DISPOSITION_QUARANTINE_REJECT;
    } else {
        dossier->final_disposition = DISPOSITION_ACCEPT;
    }

    return true;
}

/* Друк офіційного сертифікаційного протоколу вхідного контролю */
void print_lot_inspection_report(const LotInspectionDossier* d) {
    printf("====================================================================\n");
    printf(" ПРОТОКОЛ ВХІДНОГО КОНТРОЛЮ КОМПОНЕНТІВ (AS6081 / IDEA-STD-1010)   \n");
    printf("====================================================================\n");
    printf(" Партномер:       %s\n", d->part_number);
    printf(" Виробник (OCM):  %s\n", d->manufacturer);
    printf(" Номер партії:    %s\n", d->lot_number);
    printf(" Обсяг партії:    %u шт. (Вибірка: %u шт.)\n", d->lot_size, d->sample_size);
    printf(" Забраковано:     %u зразків\n", d->failed_samples_count);
    printf(" Індекс ризику:   %.2f / 1.00\n", d->calculated_risk_index);
    printf(" ВЕРДИКТ ПАРТІЇ:  %s\n",
           d->final_disposition == DISPOSITION_ACCEPT ? "[✓ ПРИДАТНО ДО ВИРОБНИЦТВА]" :
           d->final_disposition == DISPOSITION_SUSPECT_HOLD ? "[? ПРИЗУПИНЕНО / ПОВТОРНИЙ ТЕСТ]" :
           "[✗ КАРАНТИН / КОНТРАФАКТ]");
    printf("--------------------------------------------------------------------\n");
    printf(" Зразок | Рівень | Тип дефекту                  | Метрика | Примітка\n");
    printf("--------+--------+------------------------------+---------+---------\n");

    for (uint32_t i = 0; i < d->records_count; ++i) {
        const SampleTestRecord* r = &d->records[i];
        const char* def_name = "БЕЗ ДЕФЕКТІВ";
        switch (r->defect) {
            case DEFECT_BLACKTOPPING_DETECTED:  def_name = "Blacktopping (епоксид)"; break;
            case DEFECT_SOLVENT_MARK_REMOVED:   def_name = "Маркування змите ацетоном"; break;
            case DEFECT_PIN1_INDENT_MODIFIED:   def_name = "Фрезерована мітка Pin 1"; break;
            case DEFECT_XRAY_DIE_SIZE_MISMATCH: def_name = "Розмір кристала X-Ray"; break;
            case DEFECT_XRAY_BOND_WIRE_DEFECT:  def_name = "Дефект розварки дротів"; break;
            case DEFECT_XRF_LEAD_ROHS_VIOLATION:def_name = "Невідповідність RoHS XRF"; break;
            case DEFECT_DECAP_DIE_LOGO_ABSENT:  def_name = "Відсутній логотип кристала"; break;
            case DEFECT_DECAP_WRONG_MASK_ID:    def_name = "Чужий Mask ID кристала"; break;
            case DEFECT_ASA_SIGNATURE_FAILED:   def_name = "Збій сигнатури Curve Tracer"; break;
            case DEFECT_QUIESCENT_CURRENT_HIGH: def_name = "Струм спокою IDD_q > Max"; break;
            default: break;
        }

        printf(" #%-5u | Рівень %u | %-28s |  %5.1f  | %s\n",
               r->sample_id, (uint32_t)r->level, def_name, r->measured_metric, r->notes);
    }
    printf("====================================================================\n");
}
