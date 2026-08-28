#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <asm/sgx.h>

#define PAGE_SIZE 4096

/* Функція створення та ініціалізації порожнього енклава */
int load_sgx_enclave(const char *sigstruct_path, size_t enclave_size) {
    int sgx_fd = -1;
    void *enclave_addr = MAP_FAILED;
    struct sgx_enclave_create create_req;
    struct sgx_enclave_add_pages add_req;
    struct sgx_enclave_init init_req;
    struct sgx_secinfo secinfo;
    uint8_t sigstruct_buf[1808];
    uint8_t dummy_page[PAGE_SIZE];

    /* 1. Відкриття символьного пристрою SGX */
    sgx_fd = open("/dev/sgx_enclave", O_RDWR);
    if (sgx_fd < 0) {
        perror("Помилка відкриття /dev/sgx_enclave");
        return -1;
    }

    /* 2. Завантаження структури SIGSTRUCT з файлу */
    int sig_fd = open(sigstruct_path, O_RDONLY);
    if (sig_fd < 0) {
        perror("Помилка відкриття SIGSTRUCT файлу");
        close(sgx_fd);
        return -1;
    }
    if (read(sig_fd, sigstruct_buf, sizeof(sigstruct_buf)) != sizeof(sigstruct_buf)) {
        perror("Помилка читання SIGSTRUCT");
        close(sig_fd);
        close(sgx_fd);
        return -1;
    }
    close(sig_fd);

    /* 3. Ініціалізація та виклик SGX_IOC_ENCLAVE_CREATE */
    memset(&create_req, 0, sizeof(create_req));
    /* Потрібно підготувати вирівняну SECS структуру */
    uint8_t secs_buf[4096] __attribute__((aligned(4096)));
    memset(secs_buf, 0, sizeof(secs_buf));

    /* Налаштування полів SECS: розмір енклава повинен бути ступенем двійки */
    *(uint64_t *)(secs_buf + 8) = enclave_size; /* size */
    create_req.src = (uint64_t)secs_buf;

    if (ioctl(sgx_fd, SGX_IOC_ENCLAVE_CREATE, &create_req) < 0) {
        perror("Помилка SGX_IOC_ENCLAVE_CREATE");
        close(sgx_fd);
        return -1;
    }

    /* 4. Відображення пам'яті енклава у віртуальний простір */
    enclave_addr = mmap(NULL, enclave_size, PROT_READ | PROT_WRITE | PROT_EXEC,
                        MAP_SHARED, sgx_fd, 0);
    if (enclave_addr == MAP_FAILED) {
        perror("Помилка mmap енклава");
        close(sgx_fd);
        return -1;
    }

    /* 5. Додавання сторінки коду/даних через SGX_IOC_ENCLAVE_ADD_PAGES */
    memset(&secinfo, 0, sizeof(secinfo));
    secinfo.flags = SGX_SECINFO_REG | SGX_SECINFO_R | SGX_SECINFO_W | SGX_SECINFO_X;

    memset(dummy_page, 0x90, sizeof(dummy_page)); /* NOP інструкції */

    memset(&add_req, 0, sizeof(add_req));
    add_req.src = (uint64_t)dummy_page;
    add_req.offset = 0; /* Перша сторінка за адресою enclave_addr */
    add_req.length = PAGE_SIZE;
    add_req.secinfo = (uint64_t)&secinfo;
    add_req.flags = SGX_PAGE_MEASURE; /* Драйвер виконає EEXTEND для кожного 256-байтового блоку */

    if (ioctl(sgx_fd, SGX_IOC_ENCLAVE_ADD_PAGES, &add_req) < 0) {
        perror("Помилка SGX_IOC_ENCLAVE_ADD_PAGES");
        munmap(enclave_addr, enclave_size);
        close(sgx_fd);
        return -1;
    }

    /* 6. Активація енклава через SGX_IOC_ENCLAVE_INIT */
    memset(&init_req, 0, sizeof(init_req));
    init_req.sigstruct = (uint64_t)sigstruct_buf;

    if (ioctl(sgx_fd, SGX_IOC_ENCLAVE_INIT, &init_req) < 0) {
        perror("Помилка SGX_IOC_ENCLAVE_INIT (EINIT)");
        munmap(enclave_addr, enclave_size);
        close(sgx_fd);
        return -1;
    }

    printf("Енклав успішно створено та ініціалізовано за адресою: %p\n", enclave_addr);
    
    /* Очищення ресурсів після завершення демонстрації */
    munmap(enclave_addr, enclave_size);
    close(sgx_fd);
    return 0;
}
