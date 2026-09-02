#ifndef TERMIOS2_BAUD_H
#define TERMIOS2_BAUD_H

/* Ядрова struct termios2 і <termios.h> в одному файлі не уживаються, тож
   назовні звідси стирчать лише числа: жодного ядрового типу в цьому
   заголовку немає навмисно. */
struct termios2_layout {
    unsigned long size;        /* sizeof(struct termios2)                 */
    unsigned long nccs;        /* NCCS ядрового заголовка (19, не 32)     */
    unsigned long off_cc;
    unsigned long off_ispeed;
    unsigned long off_ospeed;
    unsigned long cbaud;       /* маска поля швидкості в c_cflag          */
    unsigned long bother;      /* «швидкість задано числом, а не кодом»   */
};

/* 0 — розкладку заповнено; -1 — termios2 на цій системі немає (errno). */
int termios2_layout(struct termios2_layout *out);

/* Справжня швидкість лінії числом (а не константою Bxxx) або -1. */
long termios2_get_baud(int fd);

/* Ставить довільну швидкість через BOTHER і повертає ту, яку ядро
   насправді змогло виставити, або -1. */
long termios2_set_baud(int fd, unsigned long baud);

#endif /* TERMIOS2_BAUD_H */
