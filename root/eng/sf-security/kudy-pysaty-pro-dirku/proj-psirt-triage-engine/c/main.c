#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <time.h>
#include <stdbool.h>

#define MAX_CONTACTS 16
#define MAX_LINE_LEN 1024

typedef struct {
    char contacts[MAX_CONTACTS][MAX_LINE_LEN];
    size_t contact_count;
    char encryption[MAX_LINE_LEN];
    char policy[MAX_LINE_LEN];
    char canonical[MAX_LINE_LEN];
    time_t expires_timestamp;
    bool has_expires;
} security_txt_t;

typedef enum {
    SEC_OK = 0,
    SEC_ERR_NO_CONTACT,
    SEC_ERR_NO_EXPIRES,
    SEC_ERR_EXPIRED,
    SEC_ERR_INVALID_DATE,
    SEC_ERR_MALFORMED
} sec_status_t;

/* Обрізання пробілів з обох боків рядка */
static char *trim_whitespace(char *str) {
    while (isspace((unsigned char)*str)) str++;
    if (*str == 0) return str;
    char *end = str + strlen(str) - 1;
    while (end > str && isspace((unsigned char)*end)) end--;
    end[1] = '\0';
    return str;
}

/* Парсинг ISO 8601 дати: YYYY-MM-DDTHH:MM:SS */
static bool parse_iso8601_utc(const char *date_str, time_t *out_time) {
    struct tm tm_val;
    memset(&tm_val, 0, sizeof(struct tm));

    int year, month, day, hour, min, sec;
    if (sscanf(date_str, "%4d-%2d-%2dT%2d:%2d:%2d",
               &year, &month, &day, &hour, &min, &sec) < 6) {
        return false;
    }

    tm_val.tm_year = year - 1900;
    tm_val.tm_mon  = month - 1;
    tm_val.tm_mday = day;
    tm_val.tm_hour = hour;
    tm_val.tm_min  = min;
    tm_val.tm_sec  = sec;

    /* Обчислення time_t для UTC */
#if defined(_WIN32)
    *out_time = _mkgmtime(&tm_val);
#else
    *out_time = timegm(&tm_val);
#endif
    return (*out_time != (time_t)-1);
}

/* Основна функція парсингу вмісту security.txt */
sec_status_t parse_security_txt(const char *content, security_txt_t *out_sec) {
    if (!content || !out_sec) return SEC_ERR_MALFORMED;
    memset(out_sec, 0, sizeof(security_txt_t));

    char line_buf[MAX_LINE_LEN];
    const char *ptr = content;

    while (*ptr) {
        /* Зчитування одного рядка */
        size_t len = 0;
        while (*ptr && *ptr != '\n' && *ptr != '\r' && len < MAX_LINE_LEN - 1) {
            line_buf[len++] = *ptr++;
        }
        line_buf[len] = '\0';

        /* Пропуск переведення рядків */
        while (*ptr == '\n' || *ptr == '\r') ptr++;

        char *line = trim_whitespace(line_buf);
        if (*line == '\0' || *line == '#') continue; /* Пропуск коментарів */

        char *colon = strchr(line, ':');
        if (!colon) continue;

        *colon = '\0';
        char *field = trim_whitespace(line);
        char *val   = trim_whitespace(colon + 1);

        if (strcasecmp(field, "Contact") == 0) {
            if (out_sec->contact_count < MAX_CONTACTS) {
                strncpy(out_sec->contacts[out_sec->contact_count++], val, MAX_LINE_LEN - 1);
            }
        } else if (strcasecmp(field, "Expires") == 0) {
            if (parse_iso8601_utc(val, &out_sec->expires_timestamp)) {
                out_sec->has_expires = true;
            } else {
                return SEC_ERR_INVALID_DATE;
            }
        } else if (strcasecmp(field, "Encryption") == 0) {
            strncpy(out_sec->encryption, val, MAX_LINE_LEN - 1);
        } else if (strcasecmp(field, "Policy") == 0) {
            strncpy(out_sec->policy, val, MAX_LINE_LEN - 1);
        } else if (strcasecmp(field, "Canonical") == 0) {
            strncpy(out_sec->canonical, val, MAX_LINE_LEN - 1);
        }
    }

    /* Перевірка обов'язкових полів згідно з RFC 9116 */
    if (out_sec->contact_count == 0) {
        return SEC_ERR_NO_CONTACT;
    }
    if (!out_sec->has_expires) {
        return SEC_ERR_NO_EXPIRES;
    }

    /* Перевірка строку придатності */
    time_t now = time(NULL);
    if (difftime(out_sec->expires_timestamp, now) < 0) {
        return SEC_ERR_EXPIRED;
    }

    return SEC_OK;
}
