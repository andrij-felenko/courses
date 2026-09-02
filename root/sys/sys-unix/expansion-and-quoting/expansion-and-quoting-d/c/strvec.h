/* strvec.h — вектор рядків, що росте.
 *
 * Кожна фаза розгортання перетворює одне слово на кілька, тож усе, що
 * тут відбувається, — це нескінченне «додай рядок до списку». У C цю
 * дрібницю доводиться писати руками; сусідній приклад на C++ бере готовий
 * std::vector<std::string> і тому коротший рівно на цей файл.
 */
#ifndef STRVEC_H
#define STRVEC_H

#include <stddef.h>

typedef struct {
    char **item;   /* count живих рядків; усі належать вектору */
    size_t count;
    size_t cap;
} strvec;

void strvec_init(strvec *v);
void strvec_free(strvec *v);

/* Бере ГОТОВИЙ рядок у володіння. Навіть коли місця забракло, s буде
   звільнено: інакше кожне місце виклику мусило б робити це саме. */
int strvec_adopt(strvec *v, char *s);

int strvec_push(strvec *v, const char *s);
int strvec_push_n(strvec *v, const char *s, size_t n);

#endif /* STRVEC_H */
