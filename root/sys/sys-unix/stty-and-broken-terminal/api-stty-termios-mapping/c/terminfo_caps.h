#ifndef TERMINFO_CAPS_H
#define TERMINFO_CAPS_H

/* Можливості термінала з бази terminfo — замість зашитих у код
   escape-послідовностей VT100. */
int terminfo_dump(int fd);

/* Переміщення курсора через можливість cup (координати 0-індексовані). */
int terminfo_move_cursor(int fd, int row, int col);

#endif /* TERMINFO_CAPS_H */
