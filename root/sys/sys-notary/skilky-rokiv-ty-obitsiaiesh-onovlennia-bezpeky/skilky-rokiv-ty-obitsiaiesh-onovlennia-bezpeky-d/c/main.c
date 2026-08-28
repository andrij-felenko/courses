#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

#define MAX_NAME_LEN     64
#define MAX_CVE_LEN      32
#define MAX_REVISIONS    16
#define MAX_COMPONENTS   64
#define MAX_CVES         128

typedef enum {
    CRA_CLASS_DEFAULT = 0,
    CRA_CLASS_IMPORTANT_I,
    CRA_CLASS_IMPORTANT_II,
    CRA_CLASS_CRITICAL
} cra_product_class_t;

typedef enum {
    SEVERITY_LOW = 0,
    SEVERITY_MEDIUM,
    SEVERITY_HIGH,
    SEVERITY_CRITICAL
} cve_severity_t;

typedef enum {
    VEX_STATUS_NOT_AFFECTED = 0,
    VEX_STATUS_AFFECTED,
    VEX_STATUS_FIXED,
    VEX_STATUS_UNDER_INVESTIGATION
} vex_status_t;

typedef struct {
    char model_id[MAX_NAME_LEN];
    uint32_t hardware_rev_id;
    time_t release_date;
    time_t end_of_sale_date;
    time_t promised_support_end;
    size_t flash_rom_capacity_bytes;
    size_t current_firmware_size_bytes;
    uint32_t security_version_number;
    cra_product_class_t cra_class;
} hardware_revision_t;

typedef struct {
    char cve_id[MAX_CVE_LEN];
    double cvss_score;
    double epss_probability;
    bool in_cisa_kev;
    bool is_zero_day_active;
    cve_severity_t severity;
    vex_status_t vex_status;
    time_t discovery_timestamp;
} vulnerability_record_t;

typedef struct {
    char package_name[MAX_NAME_LEN];
    char purl[MAX_NAME_LEN * 2];
    char version[MAX_NAME_LEN];
    size_t binary_size_bytes;
    vulnerability_record_t cves[MAX_CVES];
    size_t cve_count;
} sbom_component_t;

typedef struct {
    hardware_revision_t rev;
    sbom_component_t components[MAX_COMPONENTS];
    size_t component_count;
} product_lifecycle_t;

static inline cve_severity_t cvss_to_severity(double cvss) {
    if (cvss >= 9.0) return SEVERITY_CRITICAL;
    if (cvss >= 7.0) return SEVERITY_HIGH;
    if (cvss >= 4.0) return SEVERITY_MEDIUM;
    return SEVERITY_LOW;
}

bool check_support_compliance(const hardware_revision_t *hw, time_t current_time,
                              double *remaining_years, bool *is_cra_compliant) {
    if (!hw || !remaining_years || !is_cra_compliant) return false;

    double diff_sec = difftime(hw->promised_support_end, current_time);
    *remaining_years = diff_sec / (365.25 * 24.0 * 3600.0);

    /* Перевірка вимоги 5 років від дати релізу */
    double promised_total = difftime(hw->promised_support_end, hw->release_date) / (365.25 * 24.0 * 3600.0);
    *is_cra_compliant = (promised_total >= 5.0);

    return (diff_sec > 0);
}

uint32_t calculate_cra_notification_deadline_hours(const vulnerability_record_t *cve) {
    if (!cve) return 0;
    if (cve->is_zero_day_active || cve->in_cisa_kev) {
        return 24; /* Раннє сповіщення ENISA за 24 години */
    }
    if (cve->severity == SEVERITY_CRITICAL) {
        return 72; /* Офіційне повідомлення про критичний інцидент */
    }
    return 336; /* 14 діб для планового звіту */
}

bool evaluate_flash_budget_headroom(const hardware_revision_t *hw, size_t patch_delta_bytes,
                                    size_t *projected_size, double *free_percentage) {
    if (!hw || !projected_size || !free_percentage) return false;

    *projected_size = hw->current_firmware_size_bytes + patch_delta_bytes;
    if (*projected_size > hw->flash_rom_capacity_bytes) {
        *free_percentage = 0.0;
        return false; /* Переповнення Flash */
    }

    size_t free_bytes = hw->flash_rom_capacity_bytes - *projected_size;
    *free_percentage = ((double)free_bytes / (double)hw->flash_rom_capacity_bytes) * 100.0;
    return true;
}

void print_product_audit_report(const product_lifecycle_t *prod, time_t current_time) {
    if (!prod) return;

    double remaining_years = 0.0;
    bool is_cra_ok = false;
    bool is_active = check_support_compliance(&prod->rev, current_time, &remaining_years, &is_cra_ok);

    printf("=== ЗВІТ АУДИТУ ПІДТРИМКИ БЕЗПЕКИ: МОДЕЛЬ %s (REV %u) ===\n",
           prod->rev.model_id, prod->rev.hardware_rev_id);
    printf("Статус підтримки:      %s (Залишилося: %.2f років)\n",
           is_active ? "АКТИВНА" : "ЗАКІНЧИЛАСЯ (EOL)", remaining_years);
    printf("Відповідність CRA 5Y:  %s\n", is_cra_ok ? "ВІДПОВІДАЄ (>= 5 років)" : "ПОРУШЕННЯ (< 5 років)");
    printf("Поточний рівень SVN:   %u\n", prod->rev.security_version_number);
    printf("Заповнення Flash ROM:  %zu / %zu байтів (%.1f%% вільно)\n",
           prod->rev.current_firmware_size_bytes, prod->rev.flash_rom_capacity_bytes,
           ((double)(prod->rev.flash_rom_capacity_bytes - prod->rev.current_firmware_size_bytes) / 
            (double)prod->rev.flash_rom_capacity_bytes) * 100.0);

    printf("\n--- АКТИВНІ ВРАЗЛИВОСТІ ТА ДЕДЛАЙНИ РЕГУЛЯТОРІВ ---\n");
    for (size_t i = 0; i < prod->component_count; ++i) {
        const sbom_component_t *comp = &prod->components[i];
        for (size_t j = 0; j < comp->cve_count; ++j) {
            const vulnerability_record_t *v = &comp->cves[j];
            uint32_t deadline = calculate_cra_notification_deadline_hours(v);
            printf("[%s] %s | Пакет: %s@%s | CVSS: %.1f | EPSS: %.4f | Сповіщення: <= %u год\n",
                   v->cve_id, (v->vex_status == VEX_STATUS_AFFECTED) ? "AFFECTED" : "NOT_AFFECTED",
                   comp->package_name, comp->version, v->cvss_score, v->epss_probability, deadline);
        }
    }
}
