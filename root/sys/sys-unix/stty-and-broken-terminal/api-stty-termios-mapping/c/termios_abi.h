#ifndef TERMIOS_ABI_H
#define TERMIOS_ABI_H

/* Друкує справжню розкладку struct termios на цій системі — зміщення й
   розміри полів, NCCS, _POSIX_VDISABLE — і звіряє її з ядровою
   struct termios2. Повертає 0, якщо розкладки узгоджені, інакше 1. */
int termios_abi_dump(void);

#endif /* TERMIOS_ABI_H */
