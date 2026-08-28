#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define WARRANTY_MAGIC          0x52524157U /* "WARR" */
#define WARRANTY_SCHEMA_V2      0x0002U
#define MAX_RECORDS_CAPACITY    32U

/* Бітові маски порушень */
#define FLAG_LIQUID_INGRESS     (1U << 0)
#define FLAG_OVERVOLTAGE_EOS    (1U << 1)
#define FLAG_OVERHEAT           (1U << 2)
#define FLAG_MECHANICAL_SHOCK   (1U << 3)
#define FLAG_TAMPER_OPEN        (1U << 4)
#define FLAG_FW_UNAUTHORIZED    (1U << 5)
#define FLAG_REV_POLARITY       (1U << 6)

typedef enum {
    DECISION_APPROVED = 0,
    DECISION_REJECTED_EXPIRED,
    DECISION_REJECTED_LIQUID,
    DECISION_REJECTED_ELECTRICAL,
    DECISION_REJECTED_THERMAL,
    DECISION_REJECTED_MECHANICAL,
    DECISION_REJECTED_TAMPER,
    DECISION_REJECTED_CORRUPTED
} warranty_decision_t;

#pragma pack(push, 1)

typedef struct {
    uint32_t timestamp_poh;
    uint16_t event_type;
    int16_t  peak_temperature_deci_c;
    uint32_t peak_voltage_mv;
    uint16_t peak_shock_deci_g;
    uint8_t  sensor_flags;
    uint8_t  reserved;
    uint32_t record_crc32;
} sensor_violation_entry_t;

typedef struct {
    uint32_t magic;
    uint16_t schema_version;
    uint16_t header_len;
    uint8_t  device_uuid[16];
    uint32_t power_on_hours;
    uint32_t boot_count;
    uint32_t thermal_cycles;
    uint32_t violation_flags;
    int16_t  max_recorded_temp_deci_c;
    uint32_t max_recorded_voltage_mv;
    uint16_t max_recorded_shock_deci_g;
    uint16_t record_count;
    uint32_t header_crc32;
} warranty_image_header_t;

typedef struct {
    warranty_image_header_t header;
    sensor_violation_entry_t records[MAX_RECORDS_CAPACITY];
} warranty_eeprom_image_t;

#pragma pack(pop)

typedef struct {
    uint32_t max_allowed_poh;
    int16_t  max_allowed_temp_deci_c;
    uint32_t max_allowed_voltage_mv;
    uint16_t max_allowed_shock_deci_g;
    uint32_t max_thermal_dose_allowed;
} warranty_policy_t;

typedef struct {
    warranty_decision_t decision;
    uint32_t active_violations;
    uint32_t valid_records_parsed;
    uint32_t calculated_thermal_dose;
    char reason_details[256];
} rma_audit_report_t;

static uint32_t crc32_ieee(const uint8_t *buffer, size_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; ++i) {
        crc ^= (uint32_t)buffer[i];
        for (uint8_t b = 0; b < 8; ++b) {
            crc = (crc & 1U) ? ((crc >> 1) ^ 0xEDB88320U) : (crc >> 1);
        }
    }
    return crc ^ 0xFFFFFFFFU;
}

void init_default_policy(warranty_policy_t *policy) {
    if (!policy) return;
    policy->max_allowed_poh = 17520;           /* 2 роки цілодобової роботи */
    policy->max_allowed_temp_deci_c = 850;      /* 85.0 °C */
    policy->max_allowed_voltage_mv = 28000;     /* 28.0 В */
    policy->max_allowed_shock_deci_g = 500;     /* 50.0 g */
    policy->max_thermal_dose_allowed = 2000;    /* Градусо-годин перегріву */
}

void validate_warranty_log(
    const warranty_eeprom_image_t *image,
    const warranty_policy_t *policy,
    rma_audit_report_t *report
) {
    if (!image || !policy || !report) return;

    memset(report, 0, sizeof(rma_audit_report_t));

    /* 1. Перевірка цілісності заголовка */
    if (image->header.magic != WARRANTY_MAGIC ||
        image->header.schema_version != WARRANTY_SCHEMA_V2) {
        report->decision = DECISION_REJECTED_CORRUPTED;
        snprintf(report->reason_details, sizeof(report->reason_details),
                 "Invalid image magic (0x%08X) or schema version (%d)",
                 image->header.magic, image->header.schema_version);
        return;
    }

    const size_t header_check_size = sizeof(warranty_image_header_t) - sizeof(uint32_t);
    const uint32_t computed_header_crc = crc32_ieee((const uint8_t *)&image->header, header_check_size);
    if (image->header.header_crc32 != computed_header_crc) {
        report->decision = DECISION_REJECTED_CORRUPTED;
        snprintf(report->reason_details, sizeof(report->reason_details),
                 "Header CRC mismatch: stored=0x%08X, computed=0x%08X",
                 image->header.header_crc32, computed_header_crc);
        return;
    }

    report->active_violations = image->header.violation_flags;

    /* 2. Парсинг та валідація записів кільцевого буфера */
    uint16_t actual_records = image->header.record_count;
    if (actual_records > MAX_RECORDS_CAPACITY) {
        actual_records = MAX_RECORDS_CAPACITY;
    }

    uint32_t total_thermal_dose = 0;
    for (uint16_t i = 0; i < actual_records; ++i) {
        const sensor_violation_entry_t *rec = &image->records[i];
        const size_t rec_check_size = sizeof(sensor_violation_entry_t) - sizeof(uint32_t);
        const uint32_t computed_rec_crc = crc32_ieee((const uint8_t *)rec, rec_check_size);

        if (rec->record_crc32 == computed_rec_crc) {
            report->valid_records_parsed++;
            if (rec->peak_temperature_deci_c > policy->max_allowed_temp_deci_c) {
                total_thermal_dose += (uint32_t)(rec->peak_temperature_deci_c - policy->max_allowed_temp_deci_c);
            }
        }
    }
    report->calculated_thermal_dose = total_thermal_dose;

    /* 3. Оцінка політики та визначення вердикту */
    if (image->header.violation_flags & FLAG_LIQUID_INGRESS) {
        report->decision = DECISION_REJECTED_LIQUID;
        snprintf(report->reason_details, sizeof(report->reason_details),
                 "Liquid Contact Indicator (LCI) or moisture sensor tripped");
        return;
    }

    if ((image->header.violation_flags & FLAG_TAMPER_OPEN) ||
        (image->header.violation_flags & FLAG_FW_UNAUTHORIZED)) {
        report->decision = DECISION_REJECTED_TAMPER;
        snprintf(report->reason_details, sizeof(report->reason_details),
                 "Tamper seal enclosure opened or unauthorized firmware signature");
        return;
    }

    if ((image->header.violation_flags & FLAG_OVERVOLTAGE_EOS) ||
        (image->header.violation_flags & FLAG_REV_POLARITY) ||
        (image->header.max_recorded_voltage_mv > policy->max_allowed_voltage_mv)) {
        report->decision = DECISION_REJECTED_ELECTRICAL;
        snprintf(report->reason_details, sizeof(report->reason_details),
                 "Electrical Overstress: peak voltage %u mV exceeds limit %u mV",
                 image->header.max_recorded_voltage_mv, policy->max_allowed_voltage_mv);
        return;
    }

    if ((image->header.violation_flags & FLAG_OVERHEAT) ||
        (image->header.max_recorded_temp_deci_c > policy->max_allowed_temp_deci_c) ||
        (total_thermal_dose > policy->max_thermal_dose_allowed)) {
        report->decision = DECISION_REJECTED_THERMAL;
        snprintf(report->reason_details, sizeof(report->reason_details),
                 "Thermal abuse: peak %.1f C, cumulative dose %u deg-hours",
                 image->header.max_recorded_temp_deci_c / 10.0, total_thermal_dose);
        return;
    }

    if ((image->header.violation_flags & FLAG_MECHANICAL_SHOCK) ||
        (image->header.max_recorded_shock_deci_g > policy->max_allowed_shock_deci_g)) {
        report->decision = DECISION_REJECTED_MECHANICAL;
        snprintf(report->reason_details, sizeof(report->reason_details),
                 "Mechanical shock: peak %.1f g exceeds limit %.1f g",
                 image->header.max_recorded_shock_deci_g / 10.0,
                 policy->max_allowed_shock_deci_g / 10.0);
        return;
    }

    if (image->header.power_on_hours > policy->max_allowed_poh) {
        report->decision = DECISION_REJECTED_EXPIRED;
        snprintf(report->reason_details, sizeof(report->reason_details),
                 "Operating hours expired: %u POH > limit %u POH",
                 image->header.power_on_hours, policy->max_allowed_poh);
        return;
    }

    report->decision = DECISION_APPROVED;
    snprintf(report->reason_details, sizeof(report->reason_details),
             "All sensor limits and policies validated successfully. Warranty repair approved.");
}

void print_audit_report(const rma_audit_report_t *report, const warranty_image_header_t *hdr) {
    if (!report || !hdr) return;

    printf("================ RMA DIAGNOSTIC REPORT ================\n");
    printf("Device UUID: ");
    for (int i = 0; i < 16; ++i) printf("%02X", hdr->device_uuid[i]);
    printf("\nOperating Hours (POH): %u hours | Boot Count: %u\n", hdr->power_on_hours, hdr->boot_count);
    printf("Max Temp: %.1f C | Max Voltage: %u mV | Max Shock: %.1f g\n",
           hdr->max_recorded_temp_deci_c / 10.0, hdr->max_recorded_voltage_mv,
           hdr->max_recorded_shock_deci_g / 10.0);
    printf("Valid Records Parsed: %u | Calculated Thermal Dose: %u\n",
           report->valid_records_parsed, report->calculated_thermal_dose);
    printf("-------------------------------------------------------\n");

    switch (report->decision) {
        case DECISION_APPROVED:
            printf("VERDICT: [APPROVED] Free Warranty Repair\n");
            break;
        case DECISION_REJECTED_LIQUID:
            printf("VERDICT: [REJECTED] Liquid Ingress Damage\n");
            break;
        case DECISION_REJECTED_ELECTRICAL:
            printf("VERDICT: [REJECTED] Electrical Overstress (EOS)\n");
            break;
        case DECISION_REJECTED_THERMAL:
            printf("VERDICT: [REJECTED] Thermal Operating Limit Exceeded\n");
            break;
        case DECISION_REJECTED_MECHANICAL:
            printf("VERDICT: [REJECTED] Mechanical Shock / Impact\n");
            break;
        case DECISION_REJECTED_TAMPER:
            printf("VERDICT: [REJECTED] Tamper Seal Breach / Unauthorized Mod\n");
            break;
        case DECISION_REJECTED_EXPIRED:
            printf("VERDICT: [REJECTED] Warranty Operating Period Expired\n");
            break;
        case DECISION_REJECTED_CORRUPTED:
            printf("VERDICT: [REJECTED] Log Checksum / Integrity Failure\n");
            break;
    }
    printf("Reason: %s\n", report->reason_details);
    printf("=======================================================\n");
}
