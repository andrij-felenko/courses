#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <keyutils.h>

/* Зчитування секрету з ядра з використанням request_key та keyctl_read */
int fetch_and_read_user_key(const char *description) {
    key_serial_t key_id = request_key("user", description, NULL, 0);
    if (key_id == -1) {
        perror("request_key: ключ не знайдено");
        return -1;
    }

    /* Визначаємо необхідний розмір буфера */
    long len = keyctl(KEYCTL_READ, key_id, NULL, 0);
    if (len < 0) {
        perror("keyctl_read size check failed");
        return -1;
    }

    char *buffer = malloc(len + 1);
    if (!buffer) return -1;

    if (keyctl(KEYCTL_READ, key_id, buffer, len) < 0) {
        perror("keyctl_read failed");
        free(buffer);
        return -1;
    }

    buffer[len] = '\0';
    printf("Зчитано payload ключа: %s\n", buffer);

    free(buffer);
    return 0;
}
