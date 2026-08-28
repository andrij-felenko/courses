#include <cstdint>
#include <sys/ioctl.h>

#ifndef DIAG_IOCSREG
#define DIAG_IOC_MAGIC 0x82
#define DIAG_IOCSREG _IOWR(DIAG_IOC_MAGIC, 0, struct user_reg)
#define DIAG_IOCSDEL _IOW(DIAG_IOC_MAGIC, 1, char*)
#endif

struct user_reg {
    std::uint32_t size;            // [IN]  Розмір структури sizeof(user_reg)
    std::uint8_t  enable_bit;      // [OUT] Номер біта в байті статусу
    std::uint8_t  enable_size;     // [OUT] Розмір поля статусу в байтах
    std::uint16_t flags;           // [IN]  Прапорці конфігурації реєстрації
    std::uint64_t name_args;       // [IN]  Вказівник на рядок специфікації події
    std::uint32_t status_index;    // [OUT] Зсув у байтах у mmap-масиві статусу
    std::uint32_t write_index;     // [OUT] 32-бітний ID події для заголовка writev()
};
