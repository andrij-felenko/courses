/* Порівняння: у чистому C доводиться писати явні функції 
   ініціалізації, перевірки та ручного виклику cleanup */
#include <unistd.h>
#include <fcntl.h>
#include <stdbool.h>

typedef struct {
    int fd;
} UniqueFdC;

static inline UniqueFdC fd_wrap(int fd) {
    UniqueFdC h = { fd };
    return h;
}

static inline void fd_close(UniqueFdC* h) {
    if (h && h->fd >= 0) {
        close(h->fd);
        h->fd = -1;
    }
}

static inline bool fd_is_valid(const UniqueFdC* h) {
    return h && h->fd >= 0;
}
