/* braces.h — фаза 1 конвеєра: розгортання фігурних дужок.
 *
 * wordexp(3) її не виконує: дужки не входять у POSIX, це розширення
 * Bash, Zsh і Ksh. Тому пишемо самі — списки {a,b}, довільне вкладення
 * {a,b{1,2}}, діапазони {1..9..2}, {a..e} і {01..05} з шириною поля.
 */
#ifndef BRACES_H
#define BRACES_H

#include "strvec.h"

/* Дописує в out усі слова, породжені записом word.
   0 — гаразд, -1 — бракує пам'яті, -2 — слів забагато. */
int braces_expand(const char *word, strvec *out);

const char *braces_strerror(int rc);

#endif /* BRACES_H */
