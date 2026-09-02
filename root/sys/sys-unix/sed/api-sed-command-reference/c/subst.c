#include "subst.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Копіює поле до неекранованого роздільника, знімаючи '\<роздільник>'.
   Повертає позицію роздільника або NULL, якщо поле не закрите. */
static const char *scan_field(const char *p, char delim, SedBuffer *out) {
    for (; *p; ++p) {
        if (*p == '\\' && p[1] == delim) {   /* \/ всередині поля — звичайний / */
            sedbuf_append_byte(out, delim);
            ++p;
            continue;
        }
        if (*p == '\\' && p[1]) {            /* решту екранувань лишаємо рушію */
            sedbuf_append_byte(out, *p);
            sedbuf_append_byte(out, p[1]);
            ++p;
            continue;
        }
        if (*p == delim) return p;
        sedbuf_append_byte(out, *p);
    }
    return NULL;
}

bool sed_subst_compile(SedSubst *s, const char *spec, bool extended,
                       char *err, size_t errlen) {
    memset(s, 0, sizeof *s);

    if (spec[0] != 's' || !spec[1]) {
        snprintf(err, errlen, "очікувалась команда s/РЕГВИРАЗ/ЗАМІНА/");
        return false;
    }
    char delim = spec[1];
    if (delim == '\\' || delim == '\n') {
        snprintf(err, errlen, "неприпустимий роздільник команди s");
        return false;
    }

    SedBuffer pattern, replacement;
    sedbuf_init(&pattern);
    sedbuf_init(&replacement);

    const char *p = scan_field(spec + 2, delim, &pattern);
    if (!p) {
        snprintf(err, errlen, "незакритий регулярний вираз");
        goto fail;
    }
    p = scan_field(p + 1, delim, &replacement);
    if (!p) {
        snprintf(err, errlen, "незакрите поле заміни");
        goto fail;
    }

    for (++p; *p; ++p) {
        if (*p == 'g') {
            s->global = true;
        } else if (*p == 'p') {
            s->print = true;
        } else if (*p == 'I' || *p == 'i') {
            s->icase = true;
        } else if (isdigit((unsigned char)*p)) {
            char *endp = NULL;
            unsigned long n = strtoul(p, &endp, 10);
            if (n == 0 || n > 65535u) {
                snprintf(err, errlen, "номер входження поза межами 1..65535");
                goto fail;
            }
            s->occurrence = (unsigned)n;
            p = endp - 1;                    /* цикл сам зробить ++p */
        } else {
            snprintf(err, errlen, "невідомий прапорець команди s: %c", *p);
            goto fail;
        }
    }

    int cflags = 0;
    if (extended) cflags |= REG_EXTENDED;
    if (s->icase) cflags |= REG_ICASE;
    /* REG_NEWLINE НЕ ставимо: у Pattern Space '\n' — звичайний байт даних,
       і '.' мусить з ним збігатися (інакше N;P;D перестане працювати). */
    int rc = regcomp(&s->re, pattern.data ? pattern.data : "", cflags);
    if (rc != 0) {
        char msg[256];
        regerror(rc, &s->re, msg, sizeof msg);
        snprintf(err, errlen, "не компілюється регулярний вираз: %s", msg);
        goto fail;
    }

    s->replacement = replacement.data ? replacement.data : strdup("");
    if (!s->replacement) sed_fatal("бракує пам'яті на поле заміни");
    sedbuf_free(&pattern);
    return true;

fail:
    sedbuf_free(&pattern);
    sedbuf_free(&replacement);
    return false;
}

void sed_subst_free(SedSubst *s) {
    regfree(&s->re);
    free(s->replacement);
    s->replacement = NULL;
}

/* Стан перетворення регістру: \U і \L діють до \E, \u і \l — рівно на символ. */
static void append_cased(SedBuffer *out, char c, int *all, int *one) {
    unsigned char ch = (unsigned char)c;
    if (*one) {
        ch = (*one == 'u') ? (unsigned char)toupper(ch) : (unsigned char)tolower(ch);
        *one = 0;
    } else if (*all) {
        ch = (*all == 'U') ? (unsigned char)toupper(ch) : (unsigned char)tolower(ch);
    }
    sedbuf_append_byte(out, (char)ch);
}

static void expand_replacement(const SedSubst *s, const char *base,
                               const regmatch_t *m, SedBuffer *out) {
    int all = 0, one = 0;
    for (const char *p = s->replacement; *p; ++p) {
        const char *chunk = NULL;
        size_t chunk_len = 0;
        char literal = 0;
        bool have_literal = false;

        if (*p == '&') {                       /* увесь збіг */
            chunk = base + m[0].rm_so;
            chunk_len = (size_t)(m[0].rm_eo - m[0].rm_so);
        } else if (*p == '\\' && p[1]) {
            char e = *++p;
            if (e >= '0' && e <= '9') {        /* зворотне посилання \1..\9 */
                int g = e - '0';
                if (m[g].rm_so < 0) continue;  /* група не брала участі у збігу */
                chunk = base + m[g].rm_so;
                chunk_len = (size_t)(m[g].rm_eo - m[g].rm_so);
            } else switch (e) {
                case 'n': literal = '\n'; have_literal = true; break;
                case 't': literal = '\t'; have_literal = true; break;
                case 'U': case 'L': all = e; one = 0; continue;
                case 'u': case 'l': one = e; continue;
                case 'E': all = 0; one = 0; continue;
                default:  literal = e; have_literal = true; break;  /* \\ , \& , \/ */
            }
        } else {
            literal = *p;
            have_literal = true;
        }

        if (have_literal) {
            append_cased(out, literal, &all, &one);
        } else {
            for (size_t i = 0; i < chunk_len; ++i)
                append_cased(out, chunk[i], &all, &one);
        }
    }
}

bool sed_subst_apply(const SedSubst *s, SedBuffer *ps) {
    if (!ps->data) return false;

    regmatch_t m[10];
    SedBuffer out;
    sedbuf_init(&out);

    const unsigned first = s->occurrence ? s->occurrence : 1;
    unsigned seen = 0;
    size_t pos = 0;
    bool changed = false;

    while (pos <= ps->len) {
        /* REG_NOTBOL: після першого збігу '^' більше не має права спрацювати,
           бо ps->data + pos — це вже середина запису, а не його початок. */
        int flags = pos ? REG_NOTBOL : 0;
        if (regexec(&s->re, ps->data + pos, 10, m, flags) != 0) break;

        size_t start = pos + (size_t)m[0].rm_so;
        size_t end   = pos + (size_t)m[0].rm_eo;
        ++seen;

        sedbuf_append(&out, ps->data + pos, start - pos);
        if (seen == first || (s->global && seen > first)) {
            expand_replacement(s, ps->data + pos, m, &out);
            changed = true;
        } else {
            sedbuf_append(&out, ps->data + start, end - start);
        }

        if (end == start) {          /* порожній збіг: рухаємось на байт уперед */
            if (end < ps->len) sedbuf_append_byte(&out, ps->data[end]);
            pos = end + 1;
        } else {
            pos = end;
        }
        if (!s->global && seen >= first) break;
    }

    if (!changed) {
        sedbuf_free(&out);
        return false;
    }
    if (pos < ps->len) sedbuf_append(&out, ps->data + pos, ps->len - pos);
    sedbuf_free(ps);
    *ps = out;                        /* перехоплюємо буфер, не копіюючи його */
    return true;
}
