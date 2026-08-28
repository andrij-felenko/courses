#include <errno.h>

/* Де починаються дані після зсуву pos? Повертає -1, якщо далі їх немає. */
off_t next_data(int fd, off_t pos)
{
    off_t d = lseek(fd, pos, SEEK_DATA);
    if (d < 0 && errno == ENXIO) return -1;   /* далі до кінця сама діра */
    if (d < 0 && errno == EINVAL) return pos; /* ядро/ФС не вміє — вважаємо все даними */
    return d;
}
