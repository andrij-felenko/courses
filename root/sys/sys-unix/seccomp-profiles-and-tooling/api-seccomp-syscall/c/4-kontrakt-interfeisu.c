#include <linux/seccomp.h>

struct seccomp_notif {
    __u64 id;                   /* Унікальний 64-бітний ідентифікатор запиту */
    __u32 pid;                  /* PID процесу, що зробив системний виклик */
    __u32 flags;                /* Прапорці сповіщення */
    struct seccomp_data data;   /* Повний пакет даних системного виклику */
};

struct seccomp_notif_resp {
    __u64 id;                   /* Ідентифікатор запиту (мусить збігатися з seccomp_notif.id) */
    __s64 val;                  /* Значення, яке поверне системний виклик (при успіху) */
    __s32 error;                /* Код помилки (від'ємне значення errno, наприклад -EPERM) */
    __u32 flags;                /* Прапорці відповіді (SECCOMP_USER_NOTIF_FLAG_CONTINUE) */
};
