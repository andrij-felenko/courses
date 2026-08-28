// dco_verifier.c — Високопродуктивний валідатор DCO на чистому C (C99/C11)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>

#define MAX_TRAILERS 32
#define MAX_LINE_LEN 1024
#define MAX_MSG_SIZE 65536

typedef enum {
    DCO_OK = 0,
    DCO_ERR_MISSING_SIGN_OFF = 1,
    DCO_ERR_EMAIL_MISMATCH = 2,
    DCO_ERR_MALFORMED_TRAILER = 3,
    DCO_ERR_EMPTY_MESSAGE = 4
} dco_status_t;

typedef struct {
    char key[64];
    char name[128];
    char email[128];
} dco_trailer_t;

typedef struct {
    dco_trailer_t trailers[MAX_TRAILERS];
    size_t count;
    bool has_signed_off_by;
} dco_parsed_t;

// Допоміжна функція: обрізання пробілів з обох кінців
static void trim(char *s) {
    char *p = s;
    int l = (int)strlen(p);
    while (l > 0 && isspace((unsigned char)p[l - 1])) p[--l] = 0;
    while (*p && isspace((unsigned char)*p)) ++p, --l;
    memmove(s, p, l + 1);
}

// Регістронезалежне порівняння рядків
static int strcasecmp_custom(const char *s1, const char *s2) {
    while (*s1 && (tolower((unsigned char)*s1) == tolower((unsigned char)*s2))) {
        s1++;
        s2++;
    }
    return tolower((unsigned char)*s1) - tolower((unsigned char)*s2);
}

// Парсинг окремого рядка трейлера виду "Key: Name <email@domain.org>"
static bool parse_trailer_line(const char *line, dco_trailer_t *out) {
    const char *colon = strchr(line, ':');
    if (!colon) return false;

    size_t key_len = colon - line;
    if (key_len >= sizeof(out->key)) key_len = sizeof(out->key) - 1;
    strncpy(out->key, line, key_len);
    out->key[key_len] = '\0';
    trim(out->key);

    const char *val = colon + 1;
    const char *open_bracket = strchr(val, '<');
    const char *close_bracket = strrchr(val, '>');

    if (!open_bracket || !close_bracket || close_bracket <= open_bracket) {
        return false;
    }

    size_t name_len = open_bracket - val;
    if (name_len >= sizeof(out->name)) name_len = sizeof(out->name) - 1;
    strncpy(out->name, val, name_len);
    out->name[name_len] = '\0';
    trim(out->name);

    size_t email_len = close_bracket - open_bracket - 1;
    if (email_len >= sizeof(out->email)) email_len = sizeof(out->email) - 1;
    strncpy(out->email, open_bracket + 1, email_len);
    out->email[email_len] = '\0';
    trim(out->email);

    return (strlen(out->name) > 0 && strlen(out->email) > 0);
}

// Розбір блоку трейлерів у кінці повідомлення
static dco_parsed_t parse_commit_trailers(const char *msg) {
    dco_parsed_t res;
    memset(&res, 0, sizeof(res));

    if (!msg || strlen(msg) == 0) return res;

    // Розбиваємо повідомлення на масив рядків
    char buffer[MAX_MSG_SIZE];
    strncpy(buffer, msg, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';

    char *lines[512];
    size_t line_cnt = 0;
    char *curr = buffer;

    while (*curr && line_cnt < 512) {
        lines[line_cnt++] = curr;
        char *nl = strchr(curr, '\n');
        if (!nl) break;
        *nl = '\0';
        curr = nl + 1;
    }

    // Шукаємо трейлери знизу вгору до першого порожнього рядка
    for (int i = (int)line_cnt - 1; i >= 0; i--) {
        char line_copy[MAX_LINE_LEN];
        strncpy(line_copy, lines[i], sizeof(line_copy) - 1);
        line_copy[sizeof(line_copy) - 1] = '\0';
        trim(line_copy);

        if (strlen(line_copy) == 0) {
            if (res.count > 0) break; // Зустріли порожній рядок над блоком трейлерів
            continue; // Пропускаємо кінцеві порожні рядки
        }

        dco_trailer_t tr;
        if (parse_trailer_line(line_copy, &tr)) {
            if (res.count < MAX_TRAILERS) {
                res.trailers[res.count++] = tr;
                if (strcasecmp_custom(tr.key, "Signed-off-by") == 0) {
                    res.has_signed_off_by = true;
                }
            }
        } else {
            // Якщо рядок не є трейлером і ми вже щось знаходили — блок закінчився
            if (res.count > 0) break;
        }
    }

    return res;
}

// Перевірка відповідності автора та виводу JSON звіту
dco_status_t verify_dco(const char *msg, const char *expected_name, const char *expected_email) {
    if (!msg || strlen(msg) == 0) {
        fprintf(stderr, "{\"status\":\"error\",\"reason\":\"empty_commit_message\"}\n");
        return DCO_ERR_EMPTY_MESSAGE;
    }

    dco_parsed_t parsed = parse_commit_trailers(msg);

    if (!parsed.has_signed_off_by) {
        printf("{\"valid\":false,\"error\":\"missing_signed_off_by\","
               "\"expected_author\":\"%s <%s>\"}\n", expected_name, expected_email);
        return DCO_ERR_MISSING_SIGN_OFF;
    }

    // Перевіряємо збіг пошти хоча б в одному Signed-off-by
    bool email_matched = false;
    for (size_t i = 0; i < parsed.count; i++) {
        if (strcasecmp_custom(parsed.trailers[i].key, "Signed-off-by") == 0) {
            if (strcasecmp_custom(parsed.trailers[i].email, expected_email) == 0) {
                email_matched = true;
                break;
            }
        }
    }

    if (!email_matched) {
        printf("{\"valid\":false,\"error\":\"email_mismatch\","
               "\"expected_email\":\"%s\",\"found_sign_off\":\"%s <%s>\"}\n",
               expected_email, parsed.trailers[0].name, parsed.trailers[0].email);
        return DCO_ERR_EMAIL_MISMATCH;
    }

    printf("{\"valid\":true,\"status\":\"ok\",\"signed_by\":\"%s <%s>\",\"trailers_count\":%zu}\n",
           expected_name, expected_email, parsed.count);
    return DCO_OK;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <Author Name> <Author Email> [Commit Message File]\n", argv[0]);
        return 2;
    }

    const char *author_name = argv[1];
    const char *author_email = argv[2];

    char msg_buf[MAX_MSG_SIZE];
    size_t bytes_read = 0;

    if (argc >= 4) {
        FILE *f = fopen(argv[3], "rb");
        if (!f) {
            perror("Помилка відкриття файлу коміту");
            return 2;
        }
        bytes_read = fread(msg_buf, 1, sizeof(msg_buf) - 1, f);
        fclose(f);
    } else {
        bytes_read = fread(msg_buf, 1, sizeof(msg_buf) - 1, stdin);
    }

    msg_buf[bytes_read] = '\0';
    return (int)verify_dco(msg_buf, author_name, author_email);
}
