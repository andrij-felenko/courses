#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <regex.h>

#define MAX_E164_DIGITS 15
#define MAX_DOMAIN_LEN  255
#define MAX_URI_LEN     512

typedef struct {
    unsigned short order;
    unsigned short preference;
    char flags[4];
    char service[32];
    char regexp[256];
    char replacement[MAX_DOMAIN_LEN];
} NaptrRecord;

/* 1. Побудова доменного імені e164.arpa за номером */
int e164_to_enum_domain(const char *e164_in, char *domain_out, size_t max_len) {
    char digits[MAX_E164_DIGITS + 1];
    size_t d_count = 0;

    if (!e164_in || !domain_out) return -1;

    for (size_t i = 0; e164_in[i] != '\0'; ++i) {
        if (isdigit((unsigned char)e164_in[i])) {
            if (d_count >= MAX_E164_DIGITS) return -2; /* Перевищення ліміту E.164 */
            digits[d_count++] = e164_in[i];
        }
    }
    if (d_count == 0) return -3;
    digits[d_count] = '\0';

    /* Перевірка місткості буфера: кожна цифра дає 2 символи + суфікс + нуль-термінатор */
    const char suffix[] = "e164.arpa";
    if (d_count * 2 + sizeof(suffix) > max_len) return -4;

    size_t out_idx = 0;
    for (int i = (int)d_count - 1; i >= 0; --i) {
        domain_out[out_idx++] = digits[i];
        domain_out[out_idx++] = '.';
    }
    memcpy(&domain_out[out_idx], suffix, sizeof(suffix));
    return 0;
}

/* 2. Порівняння NAPTR-записів за Order та Preference */
int compare_naptr(const void *a, const void *b) {
    const NaptrRecord *rec_a = (const NaptrRecord *)a;
    const NaptrRecord *rec_b = (const NaptrRecord *)b;
    if (rec_a->order != rec_b->order) {
        return (rec_a->order < rec_b->order) ? -1 : 1;
    }
    if (rec_a->preference != rec_b->preference) {
        return (rec_a->preference < rec_b->preference) ? -1 : 1;
    }
    return 0;
}

/* 3. Застосування регулярного виразу типу !pattern!replacement! */
int evaluate_naptr_regexp(const char *regexp_field, const char *e164_source, char *uri_out, size_t max_uri) {
    if (!regexp_field || !e164_source || !uri_out) return -1;

    char delim = regexp_field[0];
    if (delim == '\0') return -2;

    const char *p1 = regexp_field + 1;
    const char *p2 = strchr(p1, delim);
    if (!p2) return -3;

    char pattern[256];
    size_t pat_len = (size_t)(p2 - p1);
    if (pat_len >= sizeof(pattern)) return -4;
    memcpy(pattern, p1, pat_len);
    pattern[pat_len] = '\0';

    const char *r1 = p2 + 1;
    const char *r2 = strchr(r1, delim);
    if (!r2) return -5;

    char replace_tmpl[256];
    size_t rep_len = (size_t)(r2 - r1);
    if (rep_len >= sizeof(replace_tmpl)) return -6;
    memcpy(replace_tmpl, r1, rep_len);
    replace_tmpl[rep_len] = '\0';

    regex_t re;
    if (regcomp(&re, pattern, REG_EXTENDED) != 0) {
        return -7;
    }

    regmatch_t pmatch[10];
    int match_res = regexec(&re, e164_source, 10, pmatch, 0);
    if (match_res != 0) {
        regfree(&re);
        return -8; /* Регулярний вираз не збігся */
    }

    /* Формування результату з розкриттям зворотних посилань \1..\9 */
    size_t out_idx = 0;
    for (size_t i = 0; i < rep_len; ++i) {
        if (replace_tmpl[i] == '\\' && isdigit((unsigned char)replace_tmpl[i + 1])) {
            int group = replace_tmpl[++i] - '0';
            if (group < 10 && pmatch[group].rm_so != -1) {
                regoff_t g_len = pmatch[group].rm_eo - pmatch[group].rm_so;
                if (out_idx + g_len >= max_uri) {
                    regfree(&re);
                    return -9;
                }
                memcpy(&uri_out[out_idx], &e164_source[pmatch[group].rm_so], (size_t)g_len);
                out_idx += (size_t)g_len;
            }
        } else {
            if (out_idx + 1 >= max_uri) {
                regfree(&re);
                return -9;
            }
            uri_out[out_idx++] = replace_tmpl[i];
        }
    }
    uri_out[out_idx] = '\0';
    regfree(&re);
    return 0;
}
