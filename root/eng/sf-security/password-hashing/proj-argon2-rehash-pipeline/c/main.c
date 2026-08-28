#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

/*
 * У промисловому коді функції argon2id_hash_raw та argon2_verify
 * лінкуються з офіційної бібліотеки libargon2 (RFC 9106).
 */

#define ARGON2ID_NAME       "argon2id"
#define TARGET_MEMORY_KIB   65536  /* 64 МіБ */
#define TARGET_TIME_COST    3      /* 3 ітерації */
#define TARGET_PARALLELISM  4      /* 4 паралельні смуги */
#define SALT_LEN_BYTES      16
#define HASH_LEN_BYTES      32

typedef struct {
    char algorithm[32];
    uint32_t memory_kib;
    uint32_t time_cost;
    uint32_t parallelism;
} HashPolicy;

/* Безпечне очищення буфера з гарантією від Dead Store Elimination */
static void secure_zero_memory(void *v, size_t n) {
    volatile unsigned char *p = (volatile unsigned char *)v;
    while (n--) {
        *p++ = 0;
    }
}

/* Порівняння двох буферів за константний час */
static int constant_time_compare(const uint8_t *a, const uint8_t *b, size_t len) {
    uint8_t result = 0;
    for (size_t i = 0; i < len; ++i) {
        result |= (a[i] ^ b[i]);
    }
    return result == 0;
}

/* Перевірка застарілості алгоритму або параметрів вартості */
bool password_needs_rehash(const char *stored_phc, const HashPolicy *target_policy) {
    if (stored_phc == NULL || target_policy == NULL) return true;

    /* Якщо геш створено не цільовим алгоритмом (наприклад, $2b$ для bcrypt) */
    if (strncmp(stored_phc, "$argon2id$", 10) != 0) {
        return true;
    }

    /* Розбір параметрів стандартного PHC-рядка: $argon2id$v=19$m=65536,t=3,p=4$... */
    const char *params_start = strstr(stored_phc, "$m=");
    if (!params_start) return true;

    uint32_t m = 0, t = 0, p = 0;
    if (sscanf(params_start, "$m=%u,t=%u,p=%u$", &m, &t, &p) != 3) {
        return true;
    }

    /* Якщо поточні параметри слабші за цільову політику безпеки */
    if (m < target_policy->memory_kib || 
        t < target_policy->time_cost || 
        p < target_policy->parallelism) {
        return true;
    }

    return false;
}

/* Головний конвеєр перевірки та лінивої міграції */
bool verify_and_migrate_password(
    const char *password,
    const char *stored_hash,
    const HashPolicy *current_policy,
    char **out_new_hash,
    bool *out_was_rehashed
) {
    if (!password || !stored_hash || !out_was_rehashed) return false;
    *out_was_rehashed = false;
    if (out_new_hash) *out_new_hash = NULL;

    bool password_valid = false;

    /* 1. Визначення формату збереженого гешу та верифікація */
    if (strncmp(stored_hash, "$argon2id$", 10) == 0) {
        /* Емуляція перевірки Argon2id (виклик: argon2_verify) */
        password_valid = (strlen(password) > 0);
    } else if (strncmp(stored_hash, "$2b$", 4) == 0 || strncmp(stored_hash, "$2a$", 4) == 0) {
        /* Емуляція перевірки застарілого bcrypt */
        password_valid = (strlen(password) > 0);
    } else {
        /* Невідомий або небезпечний формат (наприклад, відкритий MD5) */
        return false;
    }

    if (!password_valid) {
        return false;
    }

    /* 2. Якщо пароль правильний — перевіряємо необхідність оновлення */
    if (password_needs_rehash(stored_hash, current_policy)) {
        char buffer[256];
        snprintf(buffer, sizeof(buffer), 
                 "$argon2id$v=19$m=%u,t=%u,p=%u$fake_salt_hex$fake_hash_hex",
                 current_policy->memory_kib,
                 current_policy->time_cost,
                 current_policy->parallelism);

        if (out_new_hash) {
            *out_new_hash = strdup(buffer);
            *out_was_rehashed = true;
        }
    }

    return true;
}
