#include "braces.h"

#include "quoting.h"

#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Дужки множаться комбінаторно: {1..99}{1..99} це майже десять тисяч слів,
   а {1..1000000} з'їсть пам'ять цілком. Стеля тут не з делікатності. */
#define BRACES_LIMIT 4096

static char *substring(const char *s, size_t from, size_t to)
{
    const size_t len = to - from;
    char *out = malloc(len + 1);
    if (out == NULL) {
        return NULL;
    }
    memcpy(out, s + from, len);
    out[len] = '\0';
    return out;
}

static char *concat_parts(const char *const *parts, size_t n)
{
    size_t total = 0;
    for (size_t i = 0; i < n; ++i) {
        total += strlen(parts[i]);
    }

    char *out = malloc(total + 1);
    if (out == NULL) {
        return NULL;
    }

    char *w = out;
    for (size_t i = 0; i < n; ++i) {
        const size_t len = strlen(parts[i]);
        memcpy(w, parts[i], len);
        w += len;
    }
    *w = '\0';
    return out;
}

/* Перша незахищена '{'; (size_t)-1, якщо її немає. */
static size_t find_open(const char *s)
{
    for (size_t i = 0; s[i] != '\0'; ) {
        const size_t next = quoting_skip(s, i);
        if (next == i + 1 && s[i] == '{') {
            return i;
        }
        i = next;
    }
    return (size_t)-1;
}

/* Індекс '}', парної до дужки на позиції open. */
static size_t match_close(const char *s, size_t open)
{
    int depth = 0;
    for (size_t i = open; s[i] != '\0'; ) {
        const size_t next = quoting_skip(s, i);
        if (next == i + 1) {
            if (s[i] == '{') {
                ++depth;
            } else if (s[i] == '}' && --depth == 0) {
                return i;
            }
        }
        i = next;
    }
    return (size_t)-1;
}

/* Ділить тіло дужок комами ВЕРХНЬОГО рівня: кома всередині вкладених
   дужок чи в лапках роздільником не є. */
static int split_commas(const char *body, strvec *parts)
{
    int depth = 0;
    size_t start = 0;
    size_t i = 0;

    for (; body[i] != '\0'; ) {
        const size_t next = quoting_skip(body, i);
        if (next == i + 1) {
            if (body[i] == '{') {
                ++depth;
            } else if (body[i] == '}') {
                --depth;
            } else if (body[i] == ',' && depth == 0) {
                if (strvec_push_n(parts, body + start, i - start) != 0) {
                    return -1;
                }
                start = i + 1;
            }
        }
        i = next;
    }
    return strvec_push_n(parts, body + start, i - start);
}

static int parse_long(const char *s, long *out)
{
    if (s[0] == '\0') {
        return 0;
    }
    char *end = NULL;
    const long value = strtol(s, &end, 10);
    /* Діапазоном вважаємо лише те, що розібралося ЦІЛКОМ: «1x» це текст. */
    if (end == s || *end != '\0') {
        return 0;
    }
    *out = value;
    return 1;
}

static int has_leading_zero(const char *s)
{
    if (*s == '-') {
        ++s;
    }
    return s[0] == '0' && s[1] != '\0';
}

/* Ширина поля для {01..05}: провідний нуль бодай з одного боку означає,
   що всі згенеровані числа вирівнюють нулями до найдовшого запису. */
static int pad_width(const char *a, const char *b)
{
    if (!has_leading_zero(a) && !has_leading_zero(b)) {
        return 0;
    }
    const int la = (int)strlen(a);
    const int lb = (int)strlen(b);
    return (la > lb) ? la : lb;
}

static int gen_numeric(long from, long to, long step, int width, strvec *out)
{
    const unsigned long mag = (step < 0)
        ? 0UL - (unsigned long)step
        : (unsigned long)step;
    if (mag == 0 || mag > (unsigned long)LONG_MAX) {
        return 0;   /* {1..5..0} діапазоном не є — лишиться текстом */
    }

    /* Різницю рахуємо беззнаковою: {-9223372036854775808..0} інакше
       переповнив би long ще до першого кроку. */
    const unsigned long span = (from <= to)
        ? (unsigned long)to - (unsigned long)from
        : (unsigned long)from - (unsigned long)to;

    const unsigned long steps = span / mag;
    if (steps + 1 > BRACES_LIMIT) {
        return -2;
    }

    const long inc = (from <= to) ? (long)mag : -(long)mag;
    long value = from;
    for (unsigned long k = 0; k <= steps; ++k) {
        char buf[32];
        snprintf(buf, sizeof buf, "%0*ld", width, value);
        if (strvec_push(out, buf) != 0) {
            return -1;
        }
        if (k < steps) {
            value += inc;   /* останній крок не робимо: він міг би переповнити */
        }
    }
    return 1;
}

static int gen_chars(char from, char to, long step, strvec *out)
{
    const long mag = (step < 0) ? -step : step;
    if (mag == 0 || mag > 255) {
        return 0;
    }
    const long inc = (from <= to) ? mag : -mag;

    for (long c = from; (inc > 0) ? (c <= to) : (c >= to); c += inc) {
        const char buf[2] = { (char)c, '\0' };
        if (strvec_push(out, buf) != 0) {
            return -1;
        }
    }
    return 1;
}

/* Ділить тіло на сегменти за «..». Лапки й екрани означають, що це
   звичайний текст, а не діапазон. */
static int range_segments(const char *body, strvec *segs)
{
    size_t start = 0;
    size_t i = 0;

    while (body[i] != '\0') {
        if (body[i] == '\'' || body[i] == '"' || body[i] == '\\') {
            return 0;
        }
        if (body[i] == '.' && body[i + 1] == '.') {
            if (strvec_push_n(segs, body + start, i - start) != 0) {
                return -1;
            }
            i += 2;
            start = i;
            continue;
        }
        ++i;
    }
    return (strvec_push_n(segs, body + start, i - start) != 0) ? -1 : 1;
}

/* 1 — діапазон розібрано й слова вже в out; 0 — це не діапазон. */
static int parse_range(const char *body, strvec *out)
{
    strvec segs;
    strvec_init(&segs);

    int rc = range_segments(body, &segs);
    if (rc <= 0 || segs.count < 2 || segs.count > 3) {
        strvec_free(&segs);
        return (rc < 0) ? rc : 0;
    }

    const char *a = segs.item[0];
    const char *b = segs.item[1];
    long step = 1;

    if (a[0] == '\0' || b[0] == '\0'
        || (segs.count == 3 && !parse_long(segs.item[2], &step))) {
        strvec_free(&segs);
        return 0;
    }

    long from = 0;
    long to = 0;
    if (parse_long(a, &from) && parse_long(b, &to)) {
        rc = gen_numeric(from, to, step, pad_width(a, b), out);
    } else if (a[1] == '\0' && b[1] == '\0') {
        rc = gen_chars(a[0], b[0], step, out);
    } else {
        rc = 0;
    }

    strvec_free(&segs);
    return rc;
}

static int expand_into(const char *word, strvec *out)
{
    if (out->count >= BRACES_LIMIT) {
        return -2;
    }

    const size_t open = find_open(word);
    const size_t close = (open == (size_t)-1) ? (size_t)-1 : match_close(word, open);
    if (close == (size_t)-1) {
        /* Ні дужок, ні закритої пари — слово йде далі як є. */
        return strvec_push(out, word) == 0 ? 0 : -1;
    }

    char *pre = substring(word, 0, open);
    char *body = substring(word, open + 1, close);
    if (pre == NULL || body == NULL) {
        free(pre);
        free(body);
        return -1;
    }

    strvec mids;
    strvec posts;
    strvec_init(&mids);
    strvec_init(&posts);

    /* Хвіст після '}' розгортається сам по собі: {a,b}{1,2} дає добуток. */
    int rc = expand_into(word + close + 1, &posts);

    int is_list = 0;
    if (rc == 0) {
        rc = parse_range(body, &mids);
        if (rc > 0) {
            is_list = 1;
            rc = 0;
        } else if (rc == 0) {
            rc = split_commas(body, &mids);
            is_list = (rc == 0 && mids.count >= 2);
        }
    }

    if (rc == 0 && is_list) {
        for (size_t i = 0; rc == 0 && i < mids.count; ++i) {
            strvec grown;
            strvec_init(&grown);
            rc = expand_into(mids.item[i], &grown);   /* частина теж може мати дужки */

            for (size_t g = 0; rc == 0 && g < grown.count; ++g) {
                for (size_t j = 0; rc == 0 && j < posts.count; ++j) {
                    if (out->count >= BRACES_LIMIT) {
                        rc = -2;
                        break;
                    }
                    const char *parts[3] = { pre, grown.item[g], posts.item[j] };
                    char *joined = concat_parts(parts, 3);
                    rc = (joined == NULL) ? -1 : strvec_adopt(out, joined);
                }
            }
            strvec_free(&grown);
        }
    } else if (rc == 0) {
        /* Ні коми, ні діапазону: дужки лишаються буквально, але вміст усе
           одно проходить фазу. Так поводиться й Bash — {single} лишається
           собою, а {a{b,c}} дає {ab} {ac}. */
        strvec inner;
        strvec_init(&inner);
        rc = expand_into(body, &inner);

        for (size_t i = 0; rc == 0 && i < inner.count; ++i) {
            for (size_t j = 0; rc == 0 && j < posts.count; ++j) {
                if (out->count >= BRACES_LIMIT) {
                    rc = -2;
                    break;
                }
                const char *parts[5] = { pre, "{", inner.item[i], "}", posts.item[j] };
                char *joined = concat_parts(parts, 5);
                rc = (joined == NULL) ? -1 : strvec_adopt(out, joined);
            }
        }
        strvec_free(&inner);
    }

    free(pre);
    free(body);
    strvec_free(&mids);
    strvec_free(&posts);
    return rc;
}

int braces_expand(const char *word, strvec *out)
{
    return expand_into(word, out);
}

const char *braces_strerror(int rc)
{
    switch (rc) {
    case 0:  return "гаразд";
    case -1: return "бракує пам'яті";
    case -2: return "запис породжує забагато слів";
    default: return "невідома помилка розгортання дужок";
    }
}
