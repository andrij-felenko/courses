#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/uio.h>
#include <stdint.h>
#include <signal.h>
#include <errno.h>

#ifndef DIAG_IOCSREG
#define DIAG_IOC_MAGIC 0x82
#define DIAG_IOCSREG _IOWR(DIAG_IOC_MAGIC, 0, struct user_reg)
#endif

struct user_reg {
    uint32_t size;
    uint8_t  enable_bit;
    uint8_t  enable_size;
    uint16_t flags;
    uint64_t name_args;
    uint32_t status_index;
    uint32_t write_index;
};

#define USER_EVENT_LOC(offset, len) (((uint32_t)(len) << 16) | ((uint32_t)(offset) & 0xFFFF))

static volatile int keep_running = 1;

static void handle_sigint(int sig) {
    (void)sig;
    keep_running = 0;
}

int main(void) {
    signal(SIGINT, handle_sigint);
    signal(SIGTERM, handle_sigint);

    const char *device_path = "/sys/kernel/tracing/user_events_data";
    int fd = open(device_path, O_RDWR);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", device_path, strerror(errno));
        fprintf(stderr, "Перевірте, чи завантажено модуль та чи є права root/CAP_PERFMON.\n");
        return EXIT_FAILURE;
    }

    /* 1. Реєстрація події з динамічним рядком */
    const char *event_spec = "app_http_request u32 status_code; u64 latency_ns; __data_loc char[] url";
    struct user_reg reg;
    memset(&reg, 0, sizeof(reg));
    reg.size = sizeof(reg);
    reg.name_args = (uint64_t)(uintptr_t)event_spec;

    if (ioctl(fd, DIAG_IOCSREG, &reg) < 0) {
        fprintf(stderr, "Помилка ioctl(DIAG_IOCSREG): %s\n", strerror(errno));
        close(fd);
        return EXIT_FAILURE;
    }

    printf("[C] Подію зареєстровано успішно!\n");
    printf("    write_index  = %u\n", reg.write_index);
    printf("    status_index = %u\n", reg.status_index);

    /* 2. Відображення сторінки статусу в пам'ять (mmap) */
    long page_size = sysconf(_SC_PAGESIZE);
    char *status_page = (char *)mmap(NULL, (size_t)page_size, PROT_READ, MAP_SHARED, fd, 0);
    if (status_page == MAP_FAILED) {
        fprintf(stderr, "Помилка mmap: %s\n", strerror(errno));
        close(fd);
        return EXIT_FAILURE;
    }

    uint32_t counter = 0;
    while (keep_running) {
        /* Zero-Overhead перевірка у користувацькому просторі */
        if (status_page[reg.status_index] != 0) {
            const char *url_str = "/api/v1/user/checkout";
            uint16_t url_len = (uint16_t)strlen(url_str) + 1; /* Включаючи нуль-термінатор */

            /* Фіксована частина payload */
            struct {
                uint32_t status_code;
                uint32_t padding; /* Вирівнювання u64 */
                uint64_t latency_ns;
                uint32_t url_loc;
            } __attribute__((packed)) fixed_header;

            fixed_header.status_code = (counter % 5 == 0) ? 500 : 200;
            fixed_header.padding = 0;
            fixed_header.latency_ns = 1500000ULL + (counter * 10000ULL);
            
            /* Зсув від початку fixed_header (16 байтів) */
            uint16_t offset = (uint16_t)sizeof(fixed_header);
            fixed_header.url_loc = USER_EVENT_LOC(offset, url_len);

            /* Збірка iovec: 
             * iov[0] - 4 байти write_index
             * iov[1] - fixed_header
             * iov[2] - динамічні дані рядка url
             */
            struct iovec iov[3];
            iov[0].iov_base = &reg.write_index;
            iov[0].iov_len = sizeof(reg.write_index);

            iov[1].iov_base = &fixed_header;
            iov[1].iov_len = sizeof(fixed_header);

            iov[2].iov_base = (void *)url_str;
            iov[2].iov_len = url_len;

            ssize_t ret = writev(fd, iov, 3);
            if (ret < 0) {
                fprintf(stderr, "Помилка writev: %s\n", strerror(errno));
            } else {
                printf("[C] [ПОДІЯ НАДІСЛАНА] #%u status=%u latency=%lu ns url=%s (bytes=%zd)\n",
                       counter, fixed_header.status_code, fixed_header.latency_ns, url_str, ret);
            }
        } else {
            printf("[C] [ПРОПУСК] Подію вимкнено у ftrace (status_index byte is 0)\n");
        }

        counter++;
        sleep(1);
    }

    printf("\nЗавершення роботи. Звільнення ресурсів...\n");
    munmap(status_page, (size_t)page_size);
    close(fd);
    return EXIT_SUCCESS;
}
