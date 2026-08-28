/* cpio_newc_header.h — Специфікація заголовка мовою C */
#include <stdint.h>

struct cpio_newc_header {
    char c_magic[6];     /* Магічний маркер: "070701" (без CRC) або "070702" (з CRC) */
    char c_ino[8];       /* Номер іноди джерела у hex ASCII */
    char c_mode[8];      /* Тип файлу та права доступу у hex ASCII */
    char c_uid[8];       /* Ідентифікатор користувача-власника (UID) у hex ASCII */
    char c_gid[8];       /* Ідентифікатор групи-власника (GID) у hex ASCII */
    char c_nlink[8];     /* Кількість посилань на іноду у hex ASCII */
    char c_mtime[8];     /* Штамп часу модифікації POSIX timestamp у hex ASCII */
    char c_filesize[8];  /* Розмір бінарних даних файлу в байтах у hex ASCII */
    char c_maj[8];       /* Major номер пристрою носія іноди у hex ASCII */
    char c_min[8];       /* Minor номер пристрою носія іноди у hex ASCII */
    char c_rmaj[8];      /* Major номер спеціального пристрою у hex ASCII */
    char c_rmin[8];      /* Minor номер спеціального пристрою у hex ASCII */
    char c_namesize[8];  /* Довжина шляху файлу з урахуванням NUL-байта у hex ASCII */
    char c_chksum[8];    /* Контрольна сума ("00000000" для 070701) у hex ASCII */
};
