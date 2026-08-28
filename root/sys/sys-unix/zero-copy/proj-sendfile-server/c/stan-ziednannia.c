#define _GNU_SOURCE
#include <sys/sendfile.h>
#include <sys/epoll.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

#define CHUNK (1 << 20)          /* стеля однієї порції, 1 МіБ */

struct conn {
    int    sock;                 /* неблокуючий, у epoll */
    int    file;                 /* відкритий звичайний файл */
    off_t  off;                  /* скільки вже віддано */
    off_t  end;                  /* розмір файлу зі stat */
    int    raw;                  /* sendfile відмовив — ідемо копією */
    int    pipe[2];              /* тільки для splice-варіанта */
    size_t in_pipe;              /* скільки байтів висить у каналі */
};

static int pump_copy(struct conn *c);
