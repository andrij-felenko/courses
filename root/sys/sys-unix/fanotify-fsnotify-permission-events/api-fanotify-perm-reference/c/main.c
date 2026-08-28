#include <sys/fanotify.h>

struct fanotify_event_metadata {
    uint32_t event_len;      /* Загальна довжина даного запису в байтах */
    uint8_t  vers;           /* Версія структури (поточна FANOTIFY_METADATA_VERSION) */
    uint8_t  reserved;       /* Зарезервовано, ядро завжди подає 0 */
    uint16_t metadata_len;   /* Довжина фіксованої частини метаданих */
    uint64_t mask;           /* Бітова маска події (наприклад, FAN_OPEN_PERM) */
    int32_t  fd;             /* Відкритий анонімний дескриптор файлу АБО FAN_NOFD */
    int32_t  pid;            /* PID процесу, який викликав операцію VFS */
};
