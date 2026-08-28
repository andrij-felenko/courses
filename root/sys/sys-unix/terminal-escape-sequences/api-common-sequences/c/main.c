#include <curses.h>
#include <term.h>
#include <stdio.h>

/* збирати: cc prog.c -lncurses   (або -ltinfo) */
int main(void) {
    int err;
    if (setupterm(NULL, 1, &err) != OK)   /* NULL → узяти запис за $TERM */
        return 1;

    char *cup = tigetstr("cup");
    char *el  = tigetstr("el");

    /* дві перевірки, і обидві потрібні: */
    if (cup == NULL || cup == (char *)-1)  /* NULL — запис такого не вміє;   */
        return 1;                          /* (char*)-1 — ім'я не рядкове    */

    tputs(tparm(cup, 9, 2), 1, putchar);   /* аргументи від нуля → рядок 10, стовпець 3 */
    tputs(el, 1, putchar);
    fputs("тут", stdout);
    fflush(stdout);
    return 0;
}
