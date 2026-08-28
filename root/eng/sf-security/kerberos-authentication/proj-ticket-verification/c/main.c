#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>

#define KRB5_MAX_SKEW_SEC 300
#define REPLAY_CACHE_CAPACITY 1024

/* Коди результатів обробки Kerberos AP-REQ */
typedef enum {
    KRB5_OK = 0,
    KRB5_ERR_BAD_INTEGRITY = 31,
    KRB5_ERR_TKT_EXPIRED   = 32,
    KRB5_ERR_REPEAT        = 34,
    KRB5_ERR_BADMATCH      = 36,
    KRB5_ERR_SKEW          = 37
} krb5_error_code;

/* Структура симетричного ключа */
typedef struct {
    int32_t keytype;
    uint8_t data[32];
    size_t length;
} krb5_keyblock;

/* Зашифрована частина квитка (EncTicketPart) */
typedef struct {
    char cname[64];
    char crealm[64];
    krb5_keyblock session_key;
    time_t authtime;
    time_t starttime;
    time_t endtime;
} krb5_enc_ticket_part;

/* Автентифікатор клієнта */
typedef struct {
    char cname[64];
    char crealm[64];
    time_t ctime;
    uint32_t cusec;
    uint32_t seq_number;
} krb5_authenticator;

/* Запис у кеші повторів */
typedef struct {
    char cname[64];
    time_t ctime;
    uint32_t cusec;
    time_t expiry;
    bool in_use;
} replay_entry;

/* Сховище кешу повторів сервера */
typedef struct {
    replay_entry entries[REPLAY_CACHE_CAPACITY];
    size_t count;
} replay_cache;

/* Ініціалізація кешу повторів */
void replay_cache_init(replay_cache *rc) {
    if (!rc) return;
    memset(rc->entries, 0, sizeof(rc->entries));
    rc->count = 0;
}

/* Очищення застарілих записів з кешу */
void replay_cache_prune(replay_cache *rc, time_t now) {
    for (size_t i = 0; i < REPLAY_CACHE_CAPACITY; ++i) {
        if (rc->entries[i].in_use && rc->entries[i].expiry <= now) {
            rc->entries[i].in_use = false;
            if (rc->count > 0) rc->count--;
        }
    }
}

/* Перевірка та вставка відбитка автентифікатора в кеш */
bool replay_cache_check_and_add(replay_cache *rc, const char *cname, time_t ctime, uint32_t cusec, time_t now) {
    replay_cache_prune(rc, now);

    /* Пошук дубліката */
    for (size_t i = 0; i < REPLAY_CACHE_CAPACITY; ++i) {
        if (rc->entries[i].in_use) {
            if (rc->entries[i].ctime == ctime &&
                rc->entries[i].cusec == cusec &&
                strcmp(rc->entries[i].cname, cname) == 0) {
                return false; /* Знайдено дублікат (Replay attack) */
            }
        }
    }

    /* Пошук вільного слота */
    for (size_t i = 0; i < REPLAY_CACHE_CAPACITY; ++i) {
        if (!rc->entries[i].in_use) {
            strncpy(rc->entries[i].cname, cname, sizeof(rc->entries[i].cname) - 1);
            rc->entries[i].cname[sizeof(rc->entries[i].cname) - 1] = '\0';
            rc->entries[i].ctime = ctime;
            rc->entries[i].cusec = cusec;
            rc->entries[i].expiry = now + KRB5_MAX_SKEW_SEC;
            rc->entries[i].in_use = true;
            rc->count++;
            return true; /* Успішно зареєстровано новий запит */
        }
    }

    return false; /* Кеш переповнений */
}

/* Імітація криптографічного розшифрування квитка ключем служби */
krb5_error_code decrypt_ticket(const uint8_t *cipher, size_t len, const krb5_keyblock *service_key, krb5_enc_ticket_part *out_ticket) {
    if (!cipher || !service_key || !out_ticket || len == 0) {
        return KRB5_ERR_BAD_INTEGRITY;
    }
    /* У бойовій системі викликається OpenSSL EVP / AES-CTS-HMAC */
    strncpy(out_ticket->cname, "alice@EXAMPLE.ORG", sizeof(out_ticket->cname) - 1);
    strncpy(out_ticket->crealm, "EXAMPLE.ORG", sizeof(out_ticket->crealm) - 1);
    out_ticket->session_key.keytype = 18; /* AES-256 */
    memset(out_ticket->session_key.data, 0x4A, 32);
    out_ticket->session_key.length = 32;
    out_ticket->authtime = time(NULL) - 60;
    out_ticket->starttime = time(NULL) - 60;
    out_ticket->endtime = time(NULL) + 28800; /* Дійсний 8 годин */
    return KRB5_OK;
}

/* Імітація розшифрування автентифікатора сесійним ключем */
krb5_error_code decrypt_authenticator(const uint8_t *cipher, size_t len, const krb5_keyblock *session_key, krb5_authenticator *out_auth) {
    if (!cipher || !session_key || !out_auth || len == 0) {
        return KRB5_ERR_BAD_INTEGRITY;
    }
    strncpy(out_auth->cname, "alice@EXAMPLE.ORG", sizeof(out_auth->cname) - 1);
    strncpy(out_auth->crealm, "EXAMPLE.ORG", sizeof(out_auth->crealm) - 1);
    out_auth->ctime = time(NULL) - 2; /* Згенеровано 2 секунди тому */
    out_auth->cusec = 450123;
    out_auth->seq_number = 1001;
    return KRB5_OK;
}

/* Головний конвеєр перевірки AP-REQ на стороні сервера */
krb5_error_code verify_ap_req(const uint8_t *raw_ticket, size_t ticket_len,
                              const uint8_t *raw_auth, size_t auth_len,
                              const krb5_keyblock *service_key,
                              replay_cache *rc,
                              krb5_keyblock *out_session_key) {
    krb5_enc_ticket_part ticket;
    krb5_authenticator auth;
    time_t now = time(NULL);
    krb5_error_code code;

    /* Крок 1: Розшифрування квитка ключем служби */
    code = decrypt_ticket(raw_ticket, ticket_len, service_key, &ticket);
    if (code != KRB5_OK) return code;

    /* Крок 2: Перевірка терміну придатності квитка */
    if (now > ticket.endtime + KRB5_MAX_SKEW_SEC) {
        return KRB5_ERR_TKT_EXPIRED;
    }

    /* Крок 3: Розшифрування автентифікатора вилученим сесійним ключем */
    code = decrypt_authenticator(raw_auth, auth_len, &ticket.session_key, &auth);
    if (code != KRB5_OK) return code;

    /* Крок 4: Звірка імен клієнта */
    if (strcmp(ticket.cname, auth.cname) != 0 || strcmp(ticket.crealm, auth.crealm) != 0) {
        return KRB5_ERR_BADMATCH;
    }

    /* Крок 5: Перевірка допустимого вікна розсинхронізації часу */
    double diff = difftime(now, auth.ctime);
    if (diff < -KRB5_MAX_SKEW_SEC || diff > KRB5_MAX_SKEW_SEC) {
        return KRB5_ERR_SKEW;
    }

    /* Крок 6: Перевірка в кеші повторів */
    if (!replay_cache_check_and_add(rc, auth.cname, auth.ctime, auth.cusec, now)) {
        return KRB5_ERR_REPEAT;
    }

    /* Успіх: передаємо сесійний ключ викликачу */
    if (out_session_key) {
        *out_session_key = ticket.session_key;
    }
    return KRB5_OK;
}

int main(void) {
    replay_cache rc;
    replay_cache_init(&rc);

    krb5_keyblock srv_key = { .keytype = 18, .length = 32 };
    memset(srv_key.data, 0x5F, 32);

    uint8_t dummy_ticket[128] = {1};
    uint8_t dummy_auth[64] = {2};
    krb5_keyblock negotiated_session_key;

    /* Перша спроба: має завершитися успішно */
    krb5_error_code res1 = verify_ap_req(dummy_ticket, sizeof(dummy_ticket),
                                         dummy_auth, sizeof(dummy_auth),
                                         &srv_key, &rc, &negotiated_session_key);
    printf("Спроба 1: код %d (%s)\n", res1, res1 == KRB5_OK ? "УСПІХ" : "ВІДХИЛЕНО");

    /* Повторна спроба з тим самим автентифікатором: має бути заблокована Replay Cache */
    krb5_error_code res2 = verify_ap_req(dummy_ticket, sizeof(dummy_ticket),
                                         dummy_auth, sizeof(dummy_auth),
                                         &srv_key, &rc, &negotiated_session_key);
    printf("Спроба 2 (Replay): код %d (%s)\n", res2, res2 == KRB5_ERR_REPEAT ? "ЗАБЛОКОВАНО REPLAY" : "ПОМИЛКА ТЕСТУ");

    return 0;
}
