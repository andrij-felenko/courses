/* stack.h — публічна обіцянка. Клієнт вмикає лише це.
 * Будови стека тут НЕМАЄ й ніколи не буде. */
#ifndef STACK_H
#define STACK_H

#include <stdbool.h>
#include <stddef.h>   /* для size_t */

/* Неповний тип: Stack існує, будова прихована.
 * typedef дає зручне ім'я Stack замість "struct Stack". */
typedef struct Stack Stack;

/* Створити порожній стек. Повертає NULL, якщо пам'яті бракує. */
Stack *stack_new(void);

/* Покласти v на вершину. Повертає true, якщо вдалося;
 * false — якщо місця немає (сенс "місця" залежить від реалізації). */
bool stack_push(Stack *s, int v);

/* Зняти верхнє. *out отримує зняте число.
 * Повертає false, якщо стек порожній (тоді *out не чіпається). */
bool stack_pop(Stack *s, int *out);

/* Скільки чисел зараз у стеку. */
size_t stack_size(const Stack *s);

/* Звільнити стек і всю його пам'ять. Після цього s недійсний. */
void stack_free(Stack *s);

#endif /* STACK_H */
