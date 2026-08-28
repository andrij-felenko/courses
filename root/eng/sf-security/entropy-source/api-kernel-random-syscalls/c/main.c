#include <sys/random.h>
#include <unistd.h>
#include <errno.h>
#include <stdint.h>
#include <stdbool.h>

/* Безпечне наповнення буфера довільного розміру через getrandom з обробкою сигналів */
bool secure_random_bytes(void *buf, size_t len) {
    uint8_t *ptr = (uint8_t *)buf;
    size_t remaining = len;

    while (remaining > 0) {
        ssize_t ret = getrandom(ptr, remaining, 0);
        if (ret < 0) {
            if (errno == EINTR) {
                continue; /* Перервано сигналом ОС — повторити спробу */
            }
            return false; /* Критична системна помилка */
        }
        ptr += ret;
        remaining -= (size_t)ret;
    }
    return true;
}
