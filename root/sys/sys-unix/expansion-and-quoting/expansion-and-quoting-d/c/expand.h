/* expand.h — безпечне розгортання рядка засобами wordexp(3).
 *
 * Прапори фіксовані й не налаштовуються:
 *   WRDE_NOCMD — будь-яка спроба $(cmd) чи `cmd` відхиляється замість виконання;
 *   WRDE_UNDEF — звертання до невизначеної змінної це помилка, а не порожнє слово.
 * Саме ця пара робить розгортання чужого рядка безпечним.
 */
#ifndef EXPAND_H
#define EXPAND_H

#include <stddef.h>
#include <wordexp.h>

/* Результат розгортання. Поля words/count дійсні лише після expand_line() == 0. */
typedef struct {
    wordexp_t we;    /* внутрішній стан wordexp(3) */
    char    **words; /* вектор слів, завершений NULL — те саме, що argv[] */
    size_t    count; /* скільки слів утворилося */
    int       held;  /* 1, якщо є що звільняти через wordfree(3) */
} expansion;

/* Розгортає рядок. Повертає 0 або код помилки wordexp(3) (WRDE_*). */
int expand_line(const char *line, expansion *out);

/* Звільняє пам'ять, захоплену вдалим розгортанням. Викликати можна двічі. */
void expansion_free(expansion *e);

/* Текстове пояснення коду помилки wordexp(3). */
const char *expand_strerror(int status);

#endif /* EXPAND_H */
