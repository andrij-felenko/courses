#ifndef TERMIOS_FLAGS_H
#define TERMIOS_FLAGS_H

#include <termios.h>

/* Рядок таблиці відповідності: як прапорець зветься в stty і який це біт
   у відповідному полі struct termios. */
struct tty_flag {
    const char *stty_name;
    tcflag_t    bit;
};

/* Рядок таблиці спецсимволів: ім'я аргументу stty й індекс у c_cc. */
struct tty_cchar {
    const char *stty_name;
    int         index;
};

/* Швидкість лінії в бодах. Для BOTHER (довільна швидкість termios2)
   повертає число прямо з c_ospeed. */
unsigned long tty_flags_baud(const struct termios *t);

/* Розбір усіх чотирьох полів і масиву c_cc у словах stty. */
void tty_flags_dump(const struct termios *t);

/* Шукає типові поломки («сліпий термінал», «ефект сходів», мертвий Enter…)
   і друкує, чим кожну лікувати. Повертає кількість знайдених. */
int tty_flags_diagnose(const struct termios *t);

#endif /* TERMIOS_FLAGS_H */
