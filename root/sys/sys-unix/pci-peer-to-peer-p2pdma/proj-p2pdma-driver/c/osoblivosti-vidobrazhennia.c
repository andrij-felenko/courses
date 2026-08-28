/* C Implementation: Системні виклики POSIX та mmap */

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <string.h>
#include <errno.h>

#define P2P_DEV_PATH "/dev/p2pmem0"
#define TEST_SIZE 4096

int main(void)
{
    int fd = -1;
    char *buf = NULL;
    int ret = 0;

    printf("[C] Відкриття символьного пристрою P2PMEM: %s\n", P2P_DEV_PATH);
    fd = open(P2P_DEV_PATH, O_RDWR);
    if (fd < 0) {
        fprintf(stderr, "[C] Помилка відкриття %s: %s\n", P2P_DEV_PATH, strerror(errno));
        return 1;
    }

    // Відображення P2P MMIO пам'яті в адресний простір процесу
    buf = (char *)mmap(NULL, TEST_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (buf == MAP_FAILED) {
        fprintf(stderr, "[C] Помилка mmap P2P буфера: %s\n", strerror(errno));
        close(fd);
        return 1;
    }

    printf("[C] Успішно замаповано P2P буфер за адресою %p\n", (void *)buf);

    // Запис тестового патерну безпосередньо в CMB контролера
    const char *test_str = "P2PDMA direct write payload";
    memcpy(buf, test_str, strlen(test_str) + 1);

    printf("[C] Прочитано з P2P буфера: '%s'\n", buf);

    munmap(buf, TEST_SIZE);
    close(fd);
    printf("[C] Тест завершено успішно.\n");
    return 0;
}
