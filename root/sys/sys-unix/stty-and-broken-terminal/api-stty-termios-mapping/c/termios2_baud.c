/* Єдина одиниця трансляції, де живе ядрова struct termios2.
   <asm/termbits.h> і <termios.h> разом не збираються: обидва оголошують
   struct termios і struct termio, і компілятор скаже «redefinition».
   Тому все ядрове замкнене тут, а решта програми працює зі звичайним
   POSIX-заголовком і бачить звідси самі числа. */
#include "termios2_baud.h"

#include <errno.h>

#ifdef __linux__

#include <asm/termbits.h>   /* struct termios2, BOTHER, TCGETS2/TCSETS2 */
#include <stddef.h>

/* ioctl() оголошуємо самі з тієї ж причини: <sys/ioctl.h> притягнув би
   bits/ioctl-types.h із власними struct termio й struct winsize. */
extern int ioctl(int fd, unsigned long request, ...);

int termios2_layout(struct termios2_layout *out)
{
    out->size       = (unsigned long)sizeof(struct termios2);
    out->nccs       = (unsigned long)NCCS;
    out->off_cc     = (unsigned long)offsetof(struct termios2, c_cc);
    out->off_ispeed = (unsigned long)offsetof(struct termios2, c_ispeed);
    out->off_ospeed = (unsigned long)offsetof(struct termios2, c_ospeed);
    out->cbaud      = (unsigned long)CBAUD;
    out->bother     = (unsigned long)BOTHER;
    return 0;
}

long termios2_get_baud(int fd)
{
    struct termios2 t;

    if (ioctl(fd, TCGETS2, &t) < 0)
        return -1;
    /* У termios2 ядро тримає в c_ospeed справжнє число незалежно від того,
       кодом із CBAUD чи через BOTHER задавали швидкість. Саме тому цей
       запит відповідає й там, де cfgetospeed() віддав би самий лише код. */
    return (long)t.c_ospeed;
}

long termios2_set_baud(int fd, unsigned long baud)
{
    struct termios2 t;

    if (baud == 0) {
        errno = EINVAL;   /* нуль — це «покласти слухавку», не швидкість */
        return -1;
    }
    if (ioctl(fd, TCGETS2, &t) < 0)
        return -1;

    /* Код швидкості з поля CBAUD геть, замість нього BOTHER: «дивись не
       в таблицю констант Bxxx, а прямо в c_ispeed/c_ospeed». */
    t.c_cflag &= ~(tcflag_t)CBAUD;
    t.c_cflag |= BOTHER;
    t.c_ispeed = (speed_t)baud;
    t.c_ospeed = (speed_t)baud;

    /* TCSETS2 — негайно, як TCSANOW. Чекати спустошення черги (TCSETSW2)
       на зупиненому по ^S виводі означало б зависнути просто тут. */
    if (ioctl(fd, TCSETS2, &t) < 0)
        return -1;

    /* Дільник тактової частоти цілий, тож ядро ставить найближче досяжне:
       250000 бод для DMX512 лягає точно, а 31250 для MIDI на дешевому
       перетворювачі може стати 31249. Перепитуємо, що вийшло насправді. */
    if (ioctl(fd, TCGETS2, &t) < 0)
        return -1;
    return (long)t.c_ospeed;
}

#else  /* termios2 — розширення саме ядра Linux */

int termios2_layout(struct termios2_layout *out)
{
    (void)out;
    errno = ENOSYS;
    return -1;
}

long termios2_get_baud(int fd)
{
    (void)fd;
    errno = ENOSYS;
    return -1;
}

long termios2_set_baud(int fd, unsigned long baud)
{
    (void)fd;
    (void)baud;
    errno = ENOSYS;
    return -1;
}

#endif
