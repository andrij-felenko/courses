#include <linux/fuse.h>
#include <string.h>
#include <unistd.h>

#define OUR_MINOR 31            /* мінорна версія, яку вміє наш демон */
#define OUR_MAX_WRITE (128 * 1024)

/* fd — дескриптор /dev/fuse, уже переданий у mount(2) опцією fd=N.
   Повертає розмір буфера, з яким далі треба ходити по запити, або −1. */
ssize_t fuse_handshake(int fd)
{
    /* вирівнювання на 8 обов'язкове: у заголовку є 64-бітові поля */
    char buf[FUSE_MIN_READ_BUFFER] __attribute__((aligned(8)));
    ssize_t n = read(fd, buf, sizeof buf);
    if (n < (ssize_t)(sizeof(struct fuse_in_header) + sizeof(struct fuse_init_in)))
        return -1;

    struct fuse_in_header *in  = (void *)buf;
    struct fuse_init_in   *arg = (void *)(buf + sizeof *in);
    if (in->opcode != FUSE_INIT)              /* INIT завжди перший */
        return -1;

    struct {
        struct fuse_out_header h;
        struct fuse_init_out   o;
    } r;
    memset(&r, 0, sizeof r);

    r.h.len    = sizeof r;                    /* 16 + 64 = 80 */
    r.h.error  = 0;
    r.h.unique = in->unique;                  /* байт у байт, інакше −ENOENT */

    r.o.major = FUSE_KERNEL_VERSION;          /* 7; будь-що інше вбиває з'єднання */
    r.o.minor = arg->minor < OUR_MINOR ? arg->minor : OUR_MINOR;

    /* ПЕРЕТИН, а не об'єднання: беремо лише те, що вміємо обидва */
    r.o.flags = arg->flags & (FUSE_ASYNC_READ | FUSE_BIG_WRITES |
                              FUSE_DO_READDIRPLUS);

    r.o.max_readahead        = arg->max_readahead;
    r.o.max_write            = OUR_MAX_WRITE; /* мусить бути не менше за 4096  */
    r.o.max_background       = 12;
    r.o.congestion_threshold = 9;
    r.o.time_gran            = 1;             /* наносекундна точність часів */

    if (write(fd, &r, r.h.len) != (ssize_t)r.h.len)
        return -1;

    /* відтепер буфер мусить умістити найбільший запис */
    return sizeof(struct fuse_in_header) + sizeof(struct fuse_write_in)
           + OUR_MAX_WRITE;
}
