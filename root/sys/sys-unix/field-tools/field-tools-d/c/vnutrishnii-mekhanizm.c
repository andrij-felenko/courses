/* Гарячий цикл табличної трансляції байтів на C */
#include <unistd.h>
#include <stddef.h>

#define BUF_SIZE 65536

void fast_tr_loop(const unsigned char map[256]) {
    unsigned char in_buf[BUF_SIZE];
    unsigned char out_buf[BUF_SIZE];
    ssize_t n_read;

    while ((n_read = read(0, in_buf, BUF_SIZE)) > 0) {
        for (ssize_t i = 0; i < n_read; ++i) {
            out_buf[i] = map[in_buf[i]];
        }
        write(1, out_buf, (size_t)n_read);
    }
}
