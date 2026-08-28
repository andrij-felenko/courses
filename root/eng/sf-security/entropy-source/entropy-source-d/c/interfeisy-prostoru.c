#include <sys/random.h>
#include <stdio.h>
#include <stdint.h>

int main(void) {
    uint8_t key[32];

    /* Блокує процес, якщо ядро ще не накопичило 256 бітів ентропії */
    ssize_t res = getrandom(key, sizeof(key), 0);
    if (res != sizeof(key)) {
        perror("getrandom failed");
        return 1;
    }

    printf("Криптографічний ключ успішно згенеровано.\n");
    return 0;
}
