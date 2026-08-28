#include <linux/dm-ioctl.h>
#include <stdint.h>

/* Описувач одного діапазону секторів у C */
struct dm_target_spec_reference {
    uint64_t sector_start; /* Початковий сектор на віртуальному пристрої */
    uint64_t length;       /* Кількість секторів у цьому відрізку (1 сектор = 512 байт) */
    int32_t status;        /* Код помилки або повернений статус операції */
    uint32_t next;         /* Зсув у байтах від початку цього запису до наступного dm_target_spec */
    char target_type[16];  /* DM_MAX_TYPE_NAME: назва target-драйвера — "linear", "crypt", "striped" */
};
