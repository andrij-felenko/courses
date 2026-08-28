#include <curses.h>
#include <term.h>
#include <stdio.h>

int main(void)
{
    int err;
    if (setupterm(NULL, 1, &err) == ERR) {          /* NULL → узяти з TERM */
        fprintf(stderr, "terminfo: стан %d\n", err);
        return 1;
    }

    char *cup = tigetstr("cup");
    if (cup == NULL || cup == (char *)-1) {
        fprintf(stderr, "термінал не вміє ставити курсор\n");
        return 1;
    }

    char *s = tparm(cup, 9L, 2L);                   /* рядок 9, стовпець 2, від нуля */
    if (s == NULL)                                  /* рецепт хотів інших параметрів */
        return 1;
    tputs(s, 1, putchar);                           /* тут-таки домішається заповнення */

    printf("кольорів: %d\n", tigetnum("colors"));   /* -1 — нема, -2 — не числова */

    del_curterm(cur_term);
    return 0;
}
