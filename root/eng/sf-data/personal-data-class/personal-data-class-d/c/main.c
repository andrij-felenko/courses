#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_STR 128

typedef enum {
    ROLE_ADMIN,
    ROLE_ANALYST,
    ROLE_AUDITOR
} AccessRole;

/* Структура сирого вхідного запису */
typedef struct {
    char email[MAX_STR];        /* DIRECT_PII */
    char card_pan[MAX_STR];     /* DIRECT_PII */
    uint32_t age;               /* QUASI_IDENTIFIER */
    char zip_code[16];          /* QUASI_IDENTIFIER */
    char diagnosis[MAX_STR];    /* SENSITIVE_ATTRIBUTE */
} IngestionRecord;

/* Структура результату після проходження фільтрів приватності */
typedef struct {
    char email_out[MAX_STR];
    char card_out[MAX_STR];
    char age_out[32];
    char zip_out[16];
    char diagnosis_out[MAX_STR];
} SanitizedRecord;

/* Детермінований токенізатор на основі 64-бітного гешу FNV-1a з секретною сіллю */
static void hmac_tokenize(const char *input, const char *secret, char *out_buf, size_t out_size) {
    uint64_t hash = 0xcbf29ce484222325ULL;
    const uint64_t prime = 0x100000001b3ULL;

    for (const char *p = secret; *p; p++) {
        hash = (hash ^ (uint64_t)((unsigned char)*p)) * prime;
    }
    for (const char *p = input; *p; p++) {
        hash = (hash ^ (uint64_t)((unsigned char)*p)) * prime;
    }
    snprintf(out_buf, out_size, "tok_%016llx", (unsigned long long)hash);
}

/* Динамічне часткове маскування email */
static void mask_email(const char *in, char *out, size_t out_size) {
    const char *at = strchr(in, '@');
    if (!at || at == in) {
        snprintf(out, out_size, "***@***");
        return;
    }
    size_t name_len = (size_t)(at - in);
    if (name_len <= 2) {
        snprintf(out, out_size, "*%s", at);
    } else {
        snprintf(out, out_size, "%c***%c%s", in[0], in[name_len - 1], at);
    }
}

/* Генералізація віку в 10-річні бакети */
static void generalize_age(uint32_t age, char *out, size_t out_size) {
    uint32_t lower = (age / 10) * 10;
    snprintf(out, out_size, "%u–%u", lower, lower + 9);
}

/* Генералізація поштового індексу (залишаємо перші 3 цифри) */
static void generalize_zip(const char *zip, char *out, size_t out_size) {
    if (strlen(zip) < 3) {
        snprintf(out, out_size, "***");
    } else {
        snprintf(out, out_size, "%.3s**", zip);
    }
}

void process_privacy_pipeline(const IngestionRecord *in, AccessRole role, 
                              const char *pepper, SanitizedRecord *out) {
    if (role == ROLE_ADMIN) {
        /* Адміністратор системи бачить відкриті дані для налагодження */
        strncpy(out->email_out, in->email, sizeof(out->email_out) - 1);
        strncpy(out->card_out, in->card_pan, sizeof(out->card_out) - 1);
        snprintf(out->age_out, sizeof(out->age_out), "%u", in->age);
        strncpy(out->zip_out, in->zip_code, sizeof(out->zip_out) - 1);
        strncpy(out->diagnosis_out, in->diagnosis, sizeof(out->diagnosis_out) - 1);
    } else if (role == ROLE_ANALYST) {
        /* Аналітик отримує масковані PII, генералізовані квазі-ID та чутливі агрегати */
        mask_email(in->email, out->email_out, sizeof(out->email_out));
        snprintf(out->card_out, sizeof(out->card_out), "****-****-****-%s", 
                 strlen(in->card_pan) >= 4 ? in->card_pan + strlen(in->card_pan) - 4 : "****");
        generalize_age(in->age, out->age_out, sizeof(out->age_out));
        generalize_zip(in->zip_code, out->zip_out, sizeof(out->zip_out));
        strncpy(out->diagnosis_out, in->diagnosis, sizeof(out->diagnosis_out) - 1);
    } else {
        /* Аудитор або зовнішній сервіс отримує суворі токени та повну супресію діагнозів */
        hmac_tokenize(in->email, pepper, out->email_out, sizeof(out->email_out));
        hmac_tokenize(in->card_pan, pepper, out->card_out, sizeof(out->card_out));
        snprintf(out->age_out, sizeof(out->age_out), "[SUPPRESSED]");
        generalize_zip(in->zip_code, out->zip_out, sizeof(out->zip_out));
        snprintf(out->diagnosis_out, sizeof(out->diagnosis_out), "[REDACTED]");
    }
}

int main(void) {
    IngestionRecord raw = {
        .email = "alisa.shevchenko@cyber.ua",
        .card_pan = "5168742299014588",
        .age = 34,
        .zip_code = "01001",
        .diagnosis = "Acute Bronchitis"
    };
    const char *hsm_pepper = "sec_pepper_v2_2026";
    SanitizedRecord res;

    printf("=== РОЛЬ: ANALYST ===\n");
    process_privacy_pipeline(&raw, ROLE_ANALYST, hsm_pepper, &res);
    printf("Email: %s | Card: %s | Age: %s | ZIP: %s | Diag: %s\n\n",
           res.email_out, res.card_out, res.age_out, res.zip_out, res.diagnosis_out);

    printf("=== РОЛЬ: AUDITOR ===\n");
    process_privacy_pipeline(&raw, ROLE_AUDITOR, hsm_pepper, &res);
    printf("Email: %s | Card: %s | Age: %s | ZIP: %s | Diag: %s\n",
           res.email_out, res.card_out, res.age_out, res.zip_out, res.diagnosis_out);

    return 0;
}
