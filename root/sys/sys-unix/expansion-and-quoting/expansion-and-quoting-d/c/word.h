/* word.h — слово разом із маскою походження кожного байта.
 *
 * Лапки в текст слова не потрапляють узагалі: замість них кожен байт несе
 * прапорець, чи був він захищений. Інакше після фази 6 зірочку з лапок не
 * відрізнити від живої маски — а вирішувати це доводиться пізніше, аж на
 * фазі глобінгу. Сама оболонка робить так само: тримає службові позначки
 * поруч із текстом до самого кінця конвеєра.
 */
#ifndef WORD_H
#define WORD_H

#include <stddef.h>

enum {
    WORD_QUOTED = 1u,  /* байт був у лапках або за зворотним слешем */
    WORD_SUBST  = 2u   /* байт прийшов з підстановки, а не набраний руками */
};

typedef struct {
    char          *text;   /* байти слова, лапок тут уже немає */
    unsigned char *mark;   /* прапорці WORD_* на кожен байт тексту */
    size_t         len;
    size_t         cap;
    int            quotes; /* у записі були лапки — навіть якщо порожні */
} word;

void word_init(word *w);
void word_free(word *w);
int  word_append(word *w, const char *bytes, size_t n, unsigned flags);

/* Текст слова; ніколи не NULL. */
const char *word_text(const word *w);

/* Чи лишився в слові живий (незахищений) байт із набору set. */
int word_has_active(const word *w, const char *set);

/* Рядок для glob(3): захищені метасимволи екрановано зворотним слешем. */
char *word_glob_pattern(const word *w);

typedef struct {
    word  *item;
    size_t count;
    size_t cap;
} wordlist;

void wordlist_init(wordlist *l);
void wordlist_free(wordlist *l);

/* Переносить слово в список; після виклику *w порожній. */
int wordlist_adopt(wordlist *l, word *w);

/* Фази 2, 3 і 6: тильда, параметри з оточення, зняття лапок.
   0 — гаразд; -1 — бракує пам'яті; -2 — запис відхилено, пояснення в err. */
int word_expand(const char *raw, word *out, char *err, size_t errlen);

#endif /* WORD_H */
