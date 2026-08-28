#include <linux/types.h>
#include <linux/ioctl.h>

#ifndef DIAG_IOCSREG
#define DIAG_IOC_MAGIC 0x82
#define DIAG_IOCSREG _IOWR(DIAG_IOC_MAGIC, 0, struct user_reg)
#define DIAG_IOCSDEL _IOW(DIAG_IOC_MAGIC, 1, char*)
#endif

struct user_reg {
    __u32 size;            /* [IN]  Розмір структури в байтах: sizeof(struct user_reg) */
    __u8  enable_bit;      /* [OUT] Порядковий номер біта у байті статусу (зазвичай 0) */
    __u8  enable_size;     /* [OUT] Розмір поля статусу в байтах (1, 2 або 4) */
    __u16 flags;           /* [IN]  Прапорці конфігурації реєстрації (за замовчуванням 0) */
    __u64 name_args;       /* [IN]  Вказівник на нуль-термінований C-рядок специфікації */
    __u32 status_index;    /* [OUT] Зсув у байтах у mmap-сторінці статусу */
    __u32 write_index;     /* [OUT] 32-бітний ID події для перших 4 байтів writev() */
};
