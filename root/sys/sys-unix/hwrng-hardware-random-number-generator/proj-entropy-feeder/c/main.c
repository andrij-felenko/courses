#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/random.h>

#define BLOCK_BYTES 2500
#define BLOCK_BITS (BLOCK_BYTES * 8)
#define MONOBIT_MIN 9725
#define MONOBIT_MAX 10275

static bool fips_monobit_test(const uint8_t *buffer, size_t size) {
    size_t ones = 0;
    for (size_t i = 0; i < size; ++i) {
        uint8_t byte = buffer[i];
        while (byte > 0) {
            ones += (byte & 1);
            byte >>= 1;
        }
    }
    return (ones >= MONOBIT_MIN && ones <= MONOBIT_MAX);
}

int main(void) {
    int hwrng_fd = -1;
    int random_fd = -1;
    int ret = EXIT_FAILURE;

    hwrng_fd = open("/dev/hwrng", O_RDONLY);
    if (hwrng_fd < 0) {
        perror("Не вдалося відкрити /dev/hwrng");
        goto out;
    }

    random_fd = open("/dev/random", O_WRONLY);
    if (random_fd < 0) {
        perror("Не вдалося відкрити /dev/random");
        goto out;
    }

    uint8_t buffer[BLOCK_BYTES];
    size_t total_read = 0;
    while (total_read < BLOCK_BYTES) {
        ssize_t bytes = read(hwrng_fd, buffer + total_read, BLOCK_BYTES - total_read);
        if (bytes <= 0) {
            perror("Помилка зчитування з /dev/hwrng");
            goto out;
        }
        total_read += (size_t)bytes;
    }

    if (!fips_monobit_test(buffer, BLOCK_BYTES)) {
        fprintf(stderr, "Помилка: блок відкинуто, FIPS Monobit test провалився!\n");
        goto out;
    }

    size_t info_size = sizeof(struct rand_pool_info) + BLOCK_BYTES;
    struct rand_pool_info *info = (struct rand_pool_info *)malloc(info_size);
    if (!info) {
        perror("Помилка виділення пам'яті");
        goto out;
    }

    info->entropy_count = BLOCK_BITS;
    info->buf_size = BLOCK_BYTES;
    for (size_t i = 0; i < BLOCK_BYTES; ++i) {
        ((uint8_t *)info->buf)[i] = buffer[i];
    }

    if (ioctl(random_fd, RNDADDENTROPY, info) < 0) {
        perror("Помилка ioctl(RNDADDENTROPY)");
        free(info);
        goto out;
    }

    printf("Успішно перевірено та додано %d біт ентропії до ядра Linux.\n", BLOCK_BITS);
    free(info);
    ret = EXIT_SUCCESS;

out:
    if (hwrng_fd >= 0) close(hwrng_fd);
    if (random_fd >= 0) close(random_fd);
    return ret;
}
