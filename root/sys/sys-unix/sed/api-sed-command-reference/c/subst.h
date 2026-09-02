/* subst.h — команда s/РЕГВИРАЗ/ЗАМІНА/ПРАПОРЦІ.
 *
 * Шаблон компілюється один раз на старті процесу (regcomp), у головному циклі
 * лишається тільки regexec: саме тому sed тримає гігабайти за прохід. */
#ifndef SUBST_H
#define SUBST_H

#include <regex.h>
#include <stdbool.h>
#include <stddef.h>

#include "sedbuf.h"

typedef struct {
    regex_t  re;
    char    *replacement;   /* сире поле заміни: &, \1..\9, \n, \U, \L, \u, \l, \E */
    bool     global;        /* прапорець g */
    unsigned occurrence;    /* ЧИСЛО: замінювати з N-го входження (0 — з першого) */
    bool     print;         /* прапорець p */
    bool     icase;         /* прапорець I */
} SedSubst;

/* Розбирає 's<роздільник>RE<роздільник>REP<роздільник>ПРАПОРЦІ'.
   false — помилка, текст лягає в err (це код виходу 1 у sed). */
bool sed_subst_compile(SedSubst *s, const char *spec, bool extended,
                       char *err, size_t errlen);
void sed_subst_free(SedSubst *s);

/* Застосовує підстановку до Pattern Space. true — була хоча б одна заміна
   (це той самий брудний біт, який читають команди t і T). */
bool sed_subst_apply(const SedSubst *s, SedBuffer *ps);

#endif /* SUBST_H */
