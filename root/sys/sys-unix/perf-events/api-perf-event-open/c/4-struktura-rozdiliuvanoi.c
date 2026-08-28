/* Заголовочна сторінка mmap буфера у C UAPI header <linux/perf_event.h> */
struct perf_event_mmap_page {
    __u32 version;              /* Версія структури ядра */
    __u32 compat_version;       /* Найменша сумісна версія */
    __u32 lock;                 /* Атомарний замок оновлення */
    __u32 index;                /* Апаратний індекс PMC регістру */
    __s64 offset;               /* Зсув для обчислення значення без syscall */
    __u64 time_enabled;         /* Загальний час активності події (наносекунди) */
    __u64 time_running;         /* Час фактичного виконання події на HW PMC */
    union {
        __u64 capabilities;
        struct {
            __u64 cap_bit0 : 1,
                  cap_user_rdpmc : 1, /* Дозволено пряме читання RDPMC з user-space */
                  cap_user_time  : 1, /* Дозволено пряме читання TSC з user-space */
                  cap_user_time_zero : 1,
                  cap_user_time_short: 1,
                  cap_cap_user_time_zero: 1,
                  cap_architectural_bits: 58;
        };
    };
    __u16 pmc_width;            /* Бітова ширина апаратного лічильника (наприклад, 48 біт) */
    __u16 time_shift;           /* Коефіцієнт зсуву для конвертації TSC у наносекунди */
    __u32 time_mult;            /* Множник для конвертації TSC у наносекунди */
    __u64 time_zero;            /* Базовий час для конвертації TSC */
    __u32 size;                 /* Розмір структури perf_event_mmap_page */

    __u64 data_head;            /* Курсор запису ядра (monotonically increasing) */
    __u64 data_tail;            /* Курсор читання користувача (підтримується user-space) */
    __u64 data_offset;          /* Зсув початку буфера даних (4096 байтів) */
    __u64 data_size;            /* Розмір буфера даних у байтах (2^N сторінок) */
    __u64 aux_head;             /* Курсор запису AUX буфера */
    __u64 aux_tail;             /* Курсор читання AUX буфера */
    __u64 aux_offset;           /* Зсув AUX буфера */
    __u64 aux_size;             /* Розмір AUX буфера */
};
