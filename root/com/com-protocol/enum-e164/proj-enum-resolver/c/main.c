#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdint.h>
#include <netinet/in.h>
#include <arpa/nameser.h>
#include <resolv.h>
#include <regex.h>

#define ENUM_MAX_RECORDS 16
#define ENUM_BUFFER_SIZE 4096
#define ENUM_URI_MAX_LEN 256

typedef struct {
    uint16_t order;
    uint16_t preference;
    char flags[16];
    char services[64];
    char regexp[256];
    char replacement[256];
} enum_naptr_record_t;

/* Етап 1 та 2: Нормалізація номера та генерація ENUM FQDN */
int e164_to_enum_fqdn(const char *e164_input, char *fqdn_out, size_t fqdn_size,
                      char *canonical_out, size_t canon_size) {
    char digits[32];
    size_t digit_count = 0;

    if (!e164_input || e164_input[0] != '+') return -1;

    for (size_t i = 1; e164_input[i] != '\0'; ++i) {
        char c = e164_input[i];
        if (isdigit((unsigned char)c)) {
            if (digit_count >= 15) return -1; /* Перевищення ліміту E.164 */
            digits[digit_count++] = c;
        } else if (c != ' ' && c != '-' && c != '(' && c != ')') {
            return -1; /* Неприпустимий символ у номері */
        }
    }
    if (digit_count < 3) return -1;

    /* Зберігаємо нормалізований номер +380... */
    if (canonical_out && canon_size > digit_count + 1) {
        canonical_out[0] = '+';
        memcpy(canonical_out + 1, digits, digit_count);
        canonical_out[digit_count + 1] = '\0';
    }

    /* Формуємо доменне ім'я: інверсія цифр через крапку + суфікс */
    size_t pos = 0;
    for (int i = (int)digit_count - 1; i >= 0; --i) {
        if (pos + 2 >= fqdn_size) return -1;
        fqdn_out[pos++] = digits[i];
        fqdn_out[pos++] = '.';
    }
    const char *suffix = "e164.arpa";
    if (pos + strlen(suffix) >= fqdn_size) return -1;
    strcpy(fqdn_out + pos, suffix);

    return 0;
}

/* Функція сортування: спочатку order, потім preference */
int compare_naptr_records(const void *a, const void *b) {
    const enum_naptr_record_t *r1 = (const enum_naptr_record_t *)a;
    const enum_naptr_record_t *r2 = (const enum_naptr_record_t *)b;
    if (r1->order != r2->order)
        return (int)r1->order - (int)r2->order;
    return (int)r1->preference - (int)r2->preference;
}

/* Безпечний парсинг рядка змінної довжини (Pascal string) з DNS RDATA */
static const unsigned char *extract_dns_string(const unsigned char *ptr,
                                               const unsigned char *end,
                                               char *dst, size_t dst_size) {
    if (ptr >= end) return NULL;
    uint8_t len = *ptr++;
    if (ptr + len > end || len >= dst_size) return NULL;
    memcpy(dst, ptr, len);
    dst[len] = '\0';
    return ptr + len;
}

/* Етап 6: Виконання sed-підстановки !pattern!replacement!flags */
int execute_sed_replacement(const char *sed_expr, const char *input_num,
                            char *uri_out, size_t out_size) {
    if (!sed_expr || strlen(sed_expr) < 3) return -1;
    char delimiter = sed_expr[0];

    const char *p_pat_start = sed_expr + 1;
    const char *p_pat_end = strchr(p_pat_start, delimiter);
    if (!p_pat_end) return -1;

    const char *p_rep_start = p_pat_end + 1;
    const char *p_rep_end = strchr(p_rep_start, delimiter);
    if (!p_rep_end) return -1;

    size_t pat_len = (size_t)(p_pat_end - p_pat_start);
    size_t rep_len = (size_t)(p_rep_end - p_rep_start);

    char pattern[256], replacement[256];
    if (pat_len >= sizeof(pattern) || rep_len >= sizeof(replacement)) return -1;
    memcpy(pattern, p_pat_start, pat_len);
    pattern[pat_len] = '\0';
    memcpy(replacement, p_rep_start, rep_len);
    replacement[rep_len] = '\0';

    int cflags = REG_EXTENDED;
    const char *p_flags = p_rep_end + 1;
    if (strchr(p_flags, 'i') || strchr(p_flags, 'I')) cflags |= REG_ICASE;

    regex_t compiled_re;
    if (regcomp(&compiled_re, pattern, cflags) != 0) return -1;

    regmatch_t match_groups[10];
    int match_res = regexec(&compiled_re, input_num, 10, match_groups, 0);
    if (match_res != 0) {
        regfree(&compiled_re);
        return -1; /* Шаблон регулярного виразу не збігся */
    }

    /* Формуємо результат, замінюючи \1..\9 на відповідні захоплені групи */
    size_t out_pos = 0;
    for (size_t i = 0; i < rep_len; ++i) {
        if (replacement[i] == '\\' && isdigit((unsigned char)replacement[i + 1])) {
            int group_num = replacement[i + 1] - '0';
            if (group_num >= 0 && group_num < 10 && match_groups[group_num].rm_so != -1) {
                regoff_t g_len = match_groups[group_num].rm_eo - match_groups[group_num].rm_so;
                if (out_pos + (size_t)g_len >= out_size) {
                    regfree(&compiled_re);
                    return -1;
                }
                memcpy(uri_out + out_pos, input_num + match_groups[group_num].rm_so, (size_t)g_len);
                out_pos += (size_t)g_len;
            }
            i++; /* Пропускаємо символ цифри */
        } else {
            if (out_pos + 1 >= out_size) {
                regfree(&compiled_re);
                return -1;
            }
            uri_out[out_pos++] = replacement[i];
        }
    }
    uri_out[out_pos] = '\0';
    regfree(&compiled_re);
    return 0;
}

/* Головна точка входу: повна трансляція номера E.164 в SIP URI */
int resolve_enum_to_sip_uri(const char *e164_raw, char *sip_uri_out, size_t out_size) {
    char fqdn[256], canonical_e164[32];
    unsigned char dns_response[ENUM_BUFFER_SIZE];
    enum_naptr_record_t records[ENUM_MAX_RECORDS];
    size_t record_count = 0;

    if (e164_to_enum_fqdn(e164_raw, fqdn, sizeof(fqdn), canonical_e164, sizeof(canonical_e164)) != 0)
        return -1;

    /* Виконуємо DNS-запит типу NAPTR */
    int resp_len = res_query(fqdn, C_IN, T_NAPTR, dns_response, sizeof(dns_response));
    if (resp_len < (int)sizeof(HEADER)) return -1;

    ns_msg msg_handle;
    if (ns_initparse(dns_response, resp_len, &msg_handle) < 0) return -1;

    int answer_count = ns_msg_count(msg_handle, ns_s_an);
    for (int i = 0; i < answer_count && record_count < ENUM_MAX_RECORDS; ++i) {
        ns_rr resource_record;
        if (ns_parserr(&msg_handle, ns_s_an, i, &resource_record) < 0) continue;
        if (ns_rr_type(resource_record) != T_NAPTR) continue;

        const unsigned char *rdata = ns_rr_rdata(resource_record);
        const unsigned char *rdata_end = rdata + ns_rr_rdlen(resource_record);

        if (rdata_end - rdata < 7) continue;

        records[record_count].order = ns_get16(rdata); rdata += 2;
        records[record_count].preference = ns_get16(rdata); rdata += 2;

        rdata = extract_dns_string(rdata, rdata_end, records[record_count].flags, sizeof(records[record_count].flags));
        if (!rdata) continue;
        rdata = extract_dns_string(rdata, rdata_end, records[record_count].services, sizeof(records[record_count].services));
        if (!rdata) continue;
        rdata = extract_dns_string(rdata, rdata_end, records[record_count].regexp, sizeof(records[record_count].regexp));
        if (!rdata) continue;

        char decompressed_name[256];
        if (ns_name_uncompress(dns_response, dns_response + resp_len, rdata, decompressed_name, sizeof(decompressed_name)) >= 0) {
            strncpy(records[record_count].replacement, decompressed_name, sizeof(records[record_count].replacement) - 1);
        }

        /* Фільтрація: перевірка наявності сервісу SIP */
        if (strstr(records[record_count].services, "E2U+sip") || strstr(records[record_count].services, "E2U+voice:sip")) {
            record_count++;
        }
    }

    if (record_count == 0) return -1; /* Жодного валідного SIP запису в зоні */

    /* Сортування масиву знайдених правил */
    qsort(records, record_count, sizeof(enum_naptr_record_t), compare_naptr_records);

    /* Послідовна обробка від найбільш пріоритетного правила */
    for (size_t i = 0; i < record_count; ++i) {
        if (strchr(records[i].flags, 'u') || strchr(records[i].flags, 'U')) {
            if (execute_sed_replacement(records[i].regexp, canonical_e164, sip_uri_out, out_size) == 0)
                return 0; /* Успішно отримано SIP URI */
        }
    }

    return -1;
}
