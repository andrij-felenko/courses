#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>

#define BUFFER_SIZE 64

int main(void) {
    // 1. Відкриття символьного пристрою у режимі "тільки для читання"
    int fd = open("/dev/urandom", O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття /dev/urandom: %s (код %d)\n", 
                strerror(errno), errno);
        return EXIT_FAILURE;
    }

    unsigned char buffer[BUFFER_SIZE];
    
    // 2. Читання послідовного потоку байтів безпосередньо з cdev
    ssize_t bytes_read = read(fd, buffer, sizeof(buffer));
    
    if (bytes_read < 0) {
        fprintf(stderr, "Помилка читання з cdev: %s (код %d)\n", 
                strerror(errno), errno);
        close(fd);
        return EXIT_FAILURE;
    }

    // 3. Форматований вивід отриманих байтів у консоль
    printf("Успішно прочитано %zd байтів із символьного пристрою /dev/urandom:\n", bytes_read);
    for (ssize_t i = 0; i < bytes_read; ++i) {
        printf("%02x ", buffer[i]);
        if ((i + 1) % 16 == 0) {
            printf("\n");
        }
    }
    printf("\n");

    // 4. Закриття файлового дескриптора
    close(fd);
    return EXIT_SUCCESS;
}
