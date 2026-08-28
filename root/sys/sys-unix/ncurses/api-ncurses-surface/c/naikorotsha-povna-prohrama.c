#define _XOPEN_SOURCE_EXTENDED
#include <locale.h>
#include <ncursesw/curses.h>

int main(void)
{
    setlocale(LC_ALL, "");                        /* ДО initscr, інакше широкі символи мовчать */
    initscr();
    cbreak();
    noecho();
    curs_set(0);

    if (has_colors()) {
        start_color();
        init_pair(1, COLOR_YELLOW, COLOR_BLUE);
    }

    WINDOW *frame = newwin(7, 40, 2, 4);          /* координати ЕКРАННІ */
    WINDOW *inner = derwin(frame, 5, 38, 1, 1);   /* координати відносно frame */
    keypad(inner, TRUE);

    box(frame, 0, 0);                             /* 0 = типовий знак рамки */
    wattr_set(inner, A_BOLD, 1, NULL);
    mvwaddnstr(inner, 0, 0, "пара 1, жирний", -1);

    cchar_t cell;
    wchar_t glyph[2] = { L'█', L'\0' };
    setcchar(&cell, glyph, A_NORMAL, 1, NULL);
    mvwadd_wch(inner, 2, 0, &cell);

    wnoutrefresh(frame);                          /* обидва — лише в newscr */
    wnoutrefresh(inner);
    doupdate();                                   /* один прохід оптимізатора, один сплеск байтів */

    int ch;
    while ((ch = wgetch(inner)) != 'q') {
        if (ch == KEY_RESIZE) {                   /* LINES і COLS уже нові */
            touchwin(frame);                      /* батько не знає про малювання в inner */
            wnoutrefresh(frame);
            doupdate();
        }
    }

    delwin(inner);                                /* спершу похідне, потім батьківське */
    delwin(frame);
    endwin();
    return 0;
}
