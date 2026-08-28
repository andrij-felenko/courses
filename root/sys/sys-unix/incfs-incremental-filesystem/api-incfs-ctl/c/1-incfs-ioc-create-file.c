/* Заголовок ядра <linux/incrementalfs.h> — Команда створення файлу */
#define INCFS_IOC_CREATE_FILE _IOW(INCFS_IOCTL_BASE, 1, struct incfs_new_file_args)

struct incfs_new_file_args {
    __u64 file_id_low;         /* Нижні 64 біти UUID */
    __u64 file_id_high;        /* Верхні 64 біти UUID */
    __u64 size;                /* Повний номінальний розмір файлу у байтах */
    __u16 mode;                /* Права доступу POSIX (наприклад, 0644) */
    __u16 directory_path_len;  /* Довжина шляху до каталогу призначення */
    __u16 file_name_len;       /* Довжина імені файлу */
    __u16 metadata_len;        /* Довжина довільних метаданих */
    __u64 directory_path;      /* Вказівник на рядок шляху (const char*) */
    __u64 file_name;           /* Вказівник на рядок імені (const char*) */
    __u64 metadata;            /* Вказівник на метадані */
    __u64 signature_path;      /* Вказівник на файл підпису fs-verity */
    __u64 signature_size;      /* Розмір підпису */
};
