#include "field.h"

#include <string.h>

static int delim_here(const word *w, size_t i, const char *ifs)
{
    const unsigned m = w->mark[i];
    if ((m & WORD_QUOTED) != 0 || (m & WORD_SUBST) == 0) {
        return 0;
    }
    return strchr(ifs, w->text[i]) != NULL;
}

/* Білий простір IFS має окремі правила: його послідовності злипаються
   в один роздільник, а на краях слова просто зникають. */
static int delim_ws(const word *w, size_t i, const char *ifs)
{
    const char c = w->text[i];
    return delim_here(w, i, ifs) && (c == ' ' || c == '\t' || c == '\n');
}

static int emit(const word *src, size_t from, size_t to, wordlist *out)
{
    word cur;
    word_init(&cur);
    cur.quotes = src->quotes;

    for (size_t i = from; i < to; ++i) {
        if (word_append(&cur, src->text + i, 1, src->mark[i]) != 0) {
            word_free(&cur);
            return -1;
        }
    }
    if (from == to && word_append(&cur, "", 0, 0) != 0) {
        word_free(&cur);
        return -1;
    }
    return wordlist_adopt(out, &cur);
}

int field_split(const word *src, const char *ifs, wordlist *out)
{
    if (ifs == NULL) {
        ifs = " \t\n";
    }

    /* Порожній IFS вимикає фазу цілком: результат підстановки лишається
       одним шматком, хай там хоч скільки пробілів. */
    if (ifs[0] == '\0') {
        return emit(src, 0, src->len, out);
    }

    if (src->len == 0) {
        /* Порожнє слово доживає до argv[] лише тоді, коли в записі були
           лапки: "" це аргумент, а голий $EMPTY зникає безслідно. */
        return src->quotes ? emit(src, 0, 0, out) : 0;
    }

    size_t i = 0;
    while (i < src->len && delim_ws(src, i, ifs)) {
        ++i;
    }

    while (i < src->len) {
        const size_t start = i;
        while (i < src->len && !delim_here(src, i, ifs)) {
            ++i;
        }
        if (emit(src, start, i, out) != 0) {
            return -1;
        }
        if (i >= src->len) {
            break;
        }

        /* Роздільник: білий простір, щонайбільше один небілий символ IFS,
           знову білий простір. Дві сусідні коми лишають між собою порожнє
           поле, а хвостовий роздільник зайвого слова не породжує. */
        while (i < src->len && delim_ws(src, i, ifs)) {
            ++i;
        }
        if (i < src->len && delim_here(src, i, ifs)) {
            ++i;
            while (i < src->len && delim_ws(src, i, ifs)) {
                ++i;
            }
        }
    }
    return 0;
}
