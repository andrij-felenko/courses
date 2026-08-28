#include <linux/dm-ioctl.h>
#include <stdint.h>

/* Заголовок виклику ioctl для /dev/mapper/control у C
   (розкладка полів — як у struct dm_ioctl з <linux/dm-ioctl.h>) */
struct dm_ioctl_reference {
    uint32_t version[3];   /* Версія API: {DM_VERSION_MAJOR, DM_VERSION_MINOR, DM_VERSION_PATCH} */
    uint32_t data_size;    /* Загальний розмір буфера в байтах, включаючи структуру та параметри */
    uint32_t data_start;   /* Зсув у буфері до початку корисного навантаження (sizeof(struct dm_ioctl)) */

    uint32_t target_count; /* Скільки записів dm_target_spec іде за заголовком */
    int32_t  open_count;   /* Скільки відкритих дескрипторів має пристрій (заповнює ядро) */
    uint32_t flags;        /* Прапорці стану пристрою: DM_SUSPEND_FLAG, DM_READONLY_FLAG тощо */

    uint32_t event_nr;     /* Номер події або udev-cookie */
    uint32_t padding;      /* Не використовується */

    uint64_t dev;          /* Номер пристрою dev_t (major/minor), якщо пристрій існує */

    char name[128];        /* DM_NAME_LEN: ім'я пристрою в /dev/mapper/ (наприклад "vg0-lv_root") */
    char uuid[129];        /* DM_UUID_LEN: унікальний UUID пристрою для LVM або LUKS */
    char data[7];          /* Вирівнювання або початок даних */
};
