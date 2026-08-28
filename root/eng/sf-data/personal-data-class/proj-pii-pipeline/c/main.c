#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_FIELD_LEN 128
#define TOKEN_HEX_LEN 65

typedef enum {
    ROLE_ADMIN,
    ROLE_ANALYST,
    ROLE_AUDITOR
} UserRole;

typedef enum {
    CLASS_PUBLIC,
    CLASS_DIRECT_PII,
    CLASS_QUASI_ID,
    CLASS_SENSITIVE
} DataClassification;

typedef struct {
    char raw_email[MAX_FIELD_LEN];
    char raw_card[MAX_FIELD_LEN];
    uint32_t age;
    char raw_zip[16];
    char diagnosis[MAX_FIELD_LEN];
} UserRecord;

typedef struct {
    char email_display[MAX_FIELD_LEN];
    char card_display[MAX_FIELD_LEN];
    char age_display[32];
    char zip_display[16];
    char diagnosis_display[MAX_FIELD_LEN];
} TransformedRecord;

/* Спрощена реалізація FNV-1a з сіллю для детермінованого HMAC-подібного токена */
static void generate_pseudonym_token(const char *input, const char *salt, char *out_hex) {
    uint64_t hash = 0xcbf29ce484222325ULL;
    const uint64_t prime = 0x100000001b3ULL;
    
    for (const char *p = salt; *p; p++) {
        hash ^= (uint64_t)(unsigned char)(*p);
        hash *= prime;
    }
    for (const char *p = input; *p; p++) {
        hash ^= (uint64_t)(unsigned char)(*p);
        hash *= prime;
    }
    snprintf(out_hex, TOKEN_HEX_LEN, "tok_%016llx", (unsigned long long)hash);
}

/* Маскування email: user.name@domain.com -> u***e@domain.com */
static void mask_email(const char *src, char *dst, size_t dst_size) {
    const char *at = strchr(src, '@');
    if (!at || at == src) {
        snprintf(dst, dst_size, "******");
        return;
    }
    size_t local_len = (size_t)(at - src);
    if (local_len <= 2) {
        snprintf(dst, dst_size, "*%s", at);
    } else {
        snprintf(dst, dst_size, "%c***%c%s", src[0], src[local_len - 1], at);
    }
}

/* Маскування картки: 4111222233334444 -> ****-****-****-4444 */
static void mask_card(const char *src, char *dst, size_t dst_size) {
    size_t len = strlen(src);
    if (len < 4) {
        snprintf(dst, dst_size, "****");
        return;
    }
    snprintf(dst, dst_size, "****-****-****-%s", src + len - 4);
}

/* Генералізація віку в діапазони k-анонімності */
static void bucket_age(uint32_t age, char *dst, size_t dst_size) {
    uint32_t lower = (age / 10) * 10;
    uint32_t upper = lower + 9;
    snprintf(dst, dst_size, "%u–%u", lower, upper);
}

/* Генералізація індексу: 02138 -> 021** */
static void bucket_zip(const char *src, char *dst, size_t dst_size) {
    size_t len = strlen(src);
    if (len <= 2) {
        snprintf(dst, dst_size, "***");
    } else {
        snprintf(dst, dst_size, "%.3s**", src);
    }
}

void transform_record(const UserRecord *in, UserRole role, const char *salt, TransformedRecord *out) {
    if (role == ROLE_ADMIN) {
        /* Адміністратор: повний прямий доступ для обслуговування */
        strncpy(out->email_display, in->raw_email, sizeof(out->email_display) - 1);
        strncpy(out->card_display, in->raw_card, sizeof(out->card_display) - 1);
        snprintf(out->age_display, sizeof(out->age_display), "%u", in->age);
        strncpy(out->zip_display, in->raw_zip, sizeof(out->zip_display) - 1);
        strncpy(out->diagnosis_display, in->diagnosis, sizeof(out->diagnosis_display) - 1);
    } else if (role == ROLE_ANALYST) {
        /* Аналітик: динамічне маскування PII + генералізація квазі-ID */
        mask_email(in->raw_email, out->email_display, sizeof(out->email_display));
        mask_card(in->raw_card, out->card_display, sizeof(out->card_display));
        bucket_age(in->age, out->age_display, sizeof(out->age_display));
        bucket_zip(in->raw_zip, out->zip_display, sizeof(out->zip_display));
        strncpy(out->diagnosis_display, in->diagnosis, sizeof(out->diagnosis_display) - 1);
    } else {
        /* Аудитор: детерміновані псевдоніми та супресія чутливих станів */
        generate_pseudonym_token(in->raw_email, salt, out->email_display);
        generate_pseudonym_token(in->raw_card, salt, out->card_display);
        snprintf(out->age_display, sizeof(out->age_display), "[SUPPRESSED]");
        bucket_zip(in->raw_zip, out->zip_display, sizeof(out->zip_display));
        snprintf(out->diagnosis_display, sizeof(out->diagnosis_display), "[PROTECTED]");
    }
}

int main(void) {
    UserRecord user = {
        .raw_email = "william.weld@mass.gov",
        .raw_card = "4111555588880213",
        .age = 48,
        .raw_zip = "02138",
        .diagnosis = "Type-2 Diabetes"
    };
    const char *secret_salt = "k9_vault_pepper_2026";
    TransformedRecord result;

    printf("=== РОЛЬ: ANALYST ===\n");
    transform_record(&user, ROLE_ANALYST, secret_salt, &result);
    printf("Email: %s\nCard:  %s\nAge:   %s\nZIP:   %s\nDiag:  %s\n\n",
           result.email_display, result.card_display, result.age_display,
           result.zip_display, result.diagnosis_display);

    printf("=== РОЛЬ: AUDITOR ===\n");
    transform_record(&user, ROLE_AUDITOR, secret_salt, &result);
    printf("Email: %s\nCard:  %s\nAge:   %s\nZIP:   %s\nDiag:  %s\n",
           result.email_display, result.card_display, result.age_display,
           result.zip_display, result.diagnosis_display);

    return 0;
}
