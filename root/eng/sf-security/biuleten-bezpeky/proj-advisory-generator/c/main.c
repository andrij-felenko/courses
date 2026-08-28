#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

typedef struct {
    int major;
    int minor;
    int patch;
} SemVer;

typedef enum {
    REMEDIATION_VENDOR_FIX = 0,
    REMEDIATION_WORKAROUND = 1,
    REMEDIATION_MITIGATION = 2
} RemediationType;

typedef struct {
    RemediationType type;
    char details[256];
    char fixed_version[32];
} Remediation;

typedef struct {
    char cve_id[32];
    char cwe_id[32];
    double cvss_base_score;
    char cvss_vector[96];
    SemVer min_affected;
    SemVer max_affected;
    Remediation remediation;
} SecurityAdvisory;

bool parse_semver(const char* str, SemVer* out) {
    if (!str || !out) return false;
    return sscanf(str, "%d.%d.%d", &out->major, &out->minor, &out->patch) == 3;
}

int compare_semver(const SemVer* a, const SemVer* b) {
    if (a->major != b->major) return a->major - b->major;
    if (a->minor != b->minor) return a->minor - b->minor;
    return a->patch - b->patch;
}

bool is_version_vulnerable(const SemVer* current, const SemVer* min_aff, const SemVer* max_aff) {
    if (!current || !min_aff || !max_aff) return false;
    return (compare_semver(current, min_aff) >= 0 && compare_semver(current, max_aff) <= 0);
}

void evaluate_advisory(const SecurityAdvisory* adv, const char* installed_ver_str) {
    SemVer installed;
    if (!parse_semver(installed_ver_str, &installed)) {
        fprintf(stderr, "Помилка: некоректний формат версії встановленого пакета: %s\n", installed_ver_str);
        return;
    }

    printf("=== Аналіз бюлетеня: %s ===\n", adv->cve_id);
    printf("Клас дефекту: %s | CVSS: %.1f [%s]\n", adv->cwe_id, adv->cvss_base_score, adv->cvss_vector);
    printf("Перевірка версії: %s\n", installed_ver_str);

    if (is_version_vulnerable(&installed, &adv->min_affected, &adv->max_affected)) {
        printf("[УВАГА] Система ВРАЗЛИВА! Встановлена версія підпадає під дію загрози.\n");
        if (adv->remediation.type == REMEDIATION_VENDOR_FIX) {
            printf("Рекомендована дія: Оновити пакет до версії >= %s\n", adv->remediation.fixed_version);
            printf("Деталі: %s\n", adv->remediation.details);
        } else if (adv->remediation.type == REMEDIATION_WORKAROUND) {
            printf("Рекомендована дія: Застосувати тимчасовий захід (Workaround)\n");
            printf("Інструкція: %s\n", adv->remediation.details);
        }
    } else {
        printf("[OK] Встановлена версія безпечна (не зачеплена цією вадою).\n");
    }
    printf("\n");
}

int main(void) {
    SecurityAdvisory adv = {
        .cve_id = "CVE-2024-38856",
        .cwe_id = "CWE-787",
        .cvss_base_score = 9.8,
        .cvss_vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        .min_affected = { .major = 2, .minor = 1, .patch = 0 },
        .max_affected = { .major = 2, .minor = 4, .patch = 3 },
        .remediation = {
            .type = REMEDIATION_VENDOR_FIX,
            .fixed_version = "2.4.4",
            .details = "Встановіть оновлений пакет з репозиторію безпеки або вимкніть TLS-сесії."
        }
    };

    evaluate_advisory(&adv, "2.4.1");
    evaluate_advisory(&adv, "2.4.4");
    evaluate_advisory(&adv, "2.0.9");

    return 0;
}
