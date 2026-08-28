#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <errno.h>

/* Друкує межі всіх ділянок із даними. Файл не читається жодного разу. */
int print_data_map(int fd)
{
    off_t end = lseek(fd, 0, SEEK_END);
    if (end < 0) return -1;

    off_t pos = 0;
    while (pos < end) {
        off_t data = lseek(fd, pos, SEEK_DATA);
        if (data < 0) {
            if (errno == ENXIO) break;   /* далі до кінця сама діра */
            return -1;
        }
        off_t hole = lseek(fd, data, SEEK_HOLE);
        if (hole < 0) return -1;         /* не станеться: кінець файлу — теж діра */

        printf("дані: %lld .. %lld (%lld байтів)\n",
               (long long)data, (long long)hole, (long long)(hole - data));
        pos = hole;
    }
    return 0;
}
