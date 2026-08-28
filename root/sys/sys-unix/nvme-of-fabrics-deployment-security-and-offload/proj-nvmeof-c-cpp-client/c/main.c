/* c — реалізація мовою C із використанням низькорівневих системних викликів ioctl */
#define _GNU_SOURCE   /* O_DIRECT у glibc відкривається лише з цим макросом */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <errno.h>
#include <stdint.h>
#include <linux/nvme_ioctl.h>

#define NVME_FABRICS_DEV "/dev/nvme-fabrics"
#define PAGE_SIZE 4096

/* Константи підсистеми Fabrics у ядрі Linux */
#define NVME_SC_SUCCESS 0x0

/* Прототип функції виконання прямого читання секторів з блокового пристрою */
static int read_nvme_block_c(const char *dev_path, uint64_t lba, void *buffer, size_t size) {
    int fd = open(dev_path, O_RDWR | O_DIRECT);
    if (fd < 0) {
        perror("Помилка відкриття блокового пристрою NVMe");
        return -1;
    }

    struct nvme_user_io io_cmd;
    memset(&io_cmd, 0, sizeof(io_cmd));
    io_cmd.opcode = 0x02; /* NVMe Read command */
    io_cmd.flags = 0;
    io_cmd.control = 0;
    io_cmd.metadata = 0;
    io_cmd.addr = (uint64_t)buffer;
    io_cmd.slba = lba;
    io_cmd.nblocks = (size / 512) - 1; /* 0-based count */

    int ret = ioctl(fd, NVME_IOCTL_SUBMIT_IO, &io_cmd);
    close(fd);

    if (ret < 0) {
        perror("Помилка виконання NVME_IOCTL_SUBMIT_IO");
        return -1;
    }

    return 0;
}

int main(int argc, char *argv[]) {
    printf("[C-Client] Ініціалізація підключення до NVMe-oF Target...\n");

    /* 1. Відкриття контрольного пристрою fabrics */
    int fabrics_fd = open(NVME_FABRICS_DEV, O_RDWR);
    if (fabrics_fd < 0) {
        perror("Не вдалося відкрити " NVME_FABRICS_DEV ". Перевірте модуль nvme-fabrics");
        return EXIT_FAILURE;
    }

    /* 2. Формування рядка параметрів для команди connect */
    char options[512];
    snprintf(options, sizeof(options),
             "nqn=nqn.2024-08.com.example:nvme.target1,transport=tcp,traddr=192.168.1.100,trsvcid=4420");

    printf("[C-Client] Відправка параметрів у /dev/nvme-fabrics: %s\n", options);

    ssize_t written = write(fabrics_fd, options, strlen(options));
    if (written < 0) {
        perror("Помилка запису у /dev/nvme-fabrics (Connect failed)");
        close(fabrics_fd);
        return EXIT_FAILURE;
    }

    close(fabrics_fd);
    printf("[C-Client] Успішно підключено віддалений контролер NVMe-oF.\n");

    /* 3. Виділення вирівняного буфера пам'яті під Direct IO */
    void *buf = NULL;
    if (posix_memalign(&buf, PAGE_SIZE, PAGE_SIZE) != 0) {
        perror("Помилка виділення вирівняної пам'яті posix_memalign");
        return EXIT_FAILURE;
    }

    /* 4. Читання першого сектора з пристрою /dev/nvme0n1 */
    const char *target_dev = "/dev/nvme0n1";
    if (read_nvme_block_c(target_dev, 0, buf, PAGE_SIZE) == 0) {
        printf("[C-Client] Успішно прочитано LBA 0 з %s. Сигнатура: 0x%02x%02x\n",
               target_dev, ((unsigned char *)buf)[0], ((unsigned char *)buf)[1]);
    }

    free(buf);
    return EXIT_SUCCESS;
}
