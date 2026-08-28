#include <curses.h>

int main(void)
{
    initscr();              /* прочитати опис термінала, зайняти екран, створити stdscr */
    cbreak();               /* байти віддавати одразу, не чекаючи Enter */
    noecho();               /* ядро більше не друкує натиснуте */
    keypad(stdscr, TRUE);   /* послідовності функційних клавіш → один код */
    curs_set(0);            /* курсор прибрати з очей */

    int y = 0;
    for (;;) {
        werase(stdscr);                       /* стерти МОДЕЛЬ, не екран */
        mvwprintw(stdscr, y, 0, "рядок %d — стрілки рухають, q виходить", y);
        wrefresh(stdscr);                     /* єдина мить, коли байти йдуть у термінал */

        int ch = wgetch(stdscr);
        if (ch == 'q')                        break;
        if (ch == KEY_UP   && y > 0)          y--;
        if (ch == KEY_DOWN && y < LINES - 1)  y++;
        if (ch == KEY_RESIZE && y > LINES - 1) y = LINES - 1;
    }

    endwin();               /* повернути термінал у стан, у якому його взяли */
    return 0;
}
