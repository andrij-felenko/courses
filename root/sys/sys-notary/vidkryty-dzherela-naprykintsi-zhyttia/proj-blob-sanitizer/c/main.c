#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define MAX_FINDINGS 64
#define ENTROPY_THRESHOLD 7.2
#define MIN_BUFFER_FOR_ENTROPY 256

typedef enum {
    SEV_INFO,
    SEV_WARNING,
    SEV_CRITICAL
} severity_t;

typedef enum {
    FINDING_NONE,
    FINDING_BINARY_MAGIC,
    FINDING_HIGH_ENTROPY,
    FINDING_NDA_MARKER,
    FINDING_PRIVATE_KEY
} finding_type_t;

typedef struct {
    finding_type_t type;
    severity_t severity;
    const char *rule_name;
    char description[128];
    size_t offset;
} finding_t;

typedef struct {
    size_t file_size;
    double entropy;
    size_t total_findings;
    finding_t findings[MAX_FINDINGS];
} scan_report_t;

typedef struct {
    const uint8_t magic[8];
    size_t length;
    const char *format_name;
} binary_signature_t;

static const binary_signature_t SIGNATURES[] = {
    {{0x7F, 'E', 'L', 'F'}, 4, "Executable and Linkable Format (ELF)"},
    {{'M', 'Z'}, 2, "DOS/PE Executable (MZ)"},
    {{0xCA, 0xFE, 0xBA, 0xBE}, 4, "Mach-O / Java Class (Fat Binary)"},
    {{0xFE, 0xED, 0xFA, 0xCE}, 4, "Mach-O 32-bit"},
    {{0xFE, 0xED, 0xFA, 0xCF}, 4, "Mach-O 64-bit"},
    {{0x27, 0x05, 0x19, 0x56}, 4, "U-Boot Legacy Image (uImage)"},
    {{0xD0, 0x0D, 0xFE, 0xED}, 4, "Flattened Device Tree (DTB)"}
};
static const size_t NUM_SIGNATURES = sizeof(SIGNATURES) / sizeof(SIGNATURES[0]);

static const char *NDA_PATTERNS[] = {
    "CONFIDENTIAL AND PROPRIETARY",
    "DO NOT DISTRIBUTE",
    "QUALCOMM PROPRIETARY",
    "BROADCOM PROPRIETARY",
    "MEDIATEK STRICT NDA",
    "INTERNAL USE ONLY",
    "UNDER NON-DISCLOSURE AGREEMENT"
};
static const size_t NUM_NDA_PATTERNS = sizeof(NDA_PATTERNS) / sizeof(NDA_PATTERNS[0]);

static const char *KEY_PATTERNS[] = {
    "-----BEGIN RSA PRIVATE KEY-----",
    "-----BEGIN EC PRIVATE KEY-----",
    "-----BEGIN PRIVATE KEY-----",
    "-----BEGIN OPENSSH PRIVATE KEY-----",
    "PRIVATE_KEY_SECRET"
};
static const size_t NUM_KEY_PATTERNS = sizeof(KEY_PATTERNS) / sizeof(KEY_PATTERNS[0]);

static void add_finding(scan_report_t *report, finding_type_t type,
                        severity_t sev, const char *rule, const char *desc, size_t off) {
    if (report->total_findings >= MAX_FINDINGS) {
        return;
    }
    finding_t *f = &report->findings[report->total_findings++];
    f->type = type;
    f->severity = sev;
    f->rule_name = rule;
    f->offset = off;
    strncpy(f->description, desc, sizeof(f->description) - 1);
    f->description[sizeof(f->description) - 1] = '\0';
}

double calculate_shannon_entropy(const uint8_t *data, size_t len) {
    if (len == 0) return 0.0;
    
    size_t byte_counts[256] = {0};
    for (size_t i = 0; i < len; ++i) {
        byte_counts[data[i]]++;
    }

    double entropy = 0.0;
    for (int i = 0; i < 256; ++i) {
        if (byte_counts[i] > 0) {
            double p = (double)byte_counts[i] / (double)len;
            entropy -= p * (log(p) / log(2.0));
        }
    }
    return entropy;
}

void scan_buffer(const uint8_t *data, size_t len, scan_report_t *report) {
    report->file_size = len;
    report->total_findings = 0;
    report->entropy = calculate_shannon_entropy(data, len);

    /* 1. Перевірка бінарних сигнатур у заголовку */
    for (size_t s = 0; s < NUM_SIGNATURES; ++s) {
        if (len >= SIGNATURES[s].length &&
            memcmp(data, SIGNATURES[s].magic, SIGNATURES[s].length) == 0) {
            add_finding(report, FINDING_BINARY_MAGIC, SEV_CRITICAL,
                        "BIN_HEADER", SIGNATURES[s].format_name, 0);
        }
    }

    /* 2. Перевірка ентропії */
    if (len >= MIN_BUFFER_FOR_ENTROPY && report->entropy >= ENTROPY_THRESHOLD) {
        char buf[64];
        snprintf(buf, sizeof(buf), "Висока ентропія (%.2f біт/байт): підозра на зашитий блоб", report->entropy);
        add_finding(report, FINDING_HIGH_ENTROPY, SEV_WARNING, "HIGH_ENTROPY", buf, 0);
    }

    /* 3. Сканування текстових шаблонів (NDA та ключі) */
    const char *text = (const char *)data;
    for (size_t p = 0; p < NUM_NDA_PATTERNS; ++p) {
        const char *pat = NDA_PATTERNS[p];
        size_t pat_len = strlen(pat);
        if (len < pat_len) continue;
        for (size_t i = 0; i <= len - pat_len; ++i) {
            if (strncasecmp(&text[i], pat, pat_len) == 0) {
                add_finding(report, FINDING_NDA_MARKER, SEV_CRITICAL,
                            "NDA_POLICY", pat, i);
                break;
            }
        }
    }

    for (size_t k = 0; k < NUM_KEY_PATTERNS; ++k) {
        const char *pat = KEY_PATTERNS[k];
        size_t pat_len = strlen(pat);
        if (len < pat_len) continue;
        for (size_t i = 0; i <= len - pat_len; ++i) {
            if (strncmp(&text[i], pat, pat_len) == 0) {
                add_finding(report, FINDING_PRIVATE_KEY, SEV_CRITICAL,
                            "LEAKED_SECRET", pat, i);
                break;
            }
        }
    }
}

void print_scan_report(const char *filename, const scan_report_t *report) {
    const char *sev_str[] = {"INFO", "WARNING", "CRITICAL"};
    printf("=================================================================\n");
    printf("Звіт санітизації: %s (Розмір: %zu байт, Ентропія: %.2f біт/байт)\n",
           filename, report->file_size, report->entropy);
    printf("=================================================================\n");
    if (report->total_findings == 0) {
        printf(" [OK] Жодних закритих блобів або секретів не виявлено.\n");
        return;
    }

    for (size_t i = 0; i < report->total_findings; ++i) {
        const finding_t *f = &report->findings[i];
        printf(" [%-8s] Правило: %-14s | Зсув: 0x%06zx | %s\n",
               sev_str[f->severity], f->rule_name, f->offset, f->description);
    }
    printf("-----------------------------------------------------------------\n");
    printf(" Загалом зауважень: %zu\n\n", report->total_findings);
}
