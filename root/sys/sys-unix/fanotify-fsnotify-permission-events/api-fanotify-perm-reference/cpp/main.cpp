#include <sys/fanotify.h>
#include <cstdint>

struct fanotify_event_metadata {
    std::uint32_t event_len;      // Загальна довжина запису в байтах
    std::uint8_t  vers;           // Версія структури
    std::uint8_t  reserved;       // Зарезервовано ядром
    std::uint16_t metadata_len;   // Довжина фіксованої частини метаданих
    std::uint64_t mask;           // Бітова маска події (FAN_OPEN_PERM)
    std::int32_t  fd;             // Відкритий анонімний дескриптор файлу або FAN_NOFD
    std::int32_t  pid;            // PID процесу, який викликав операцію VFS
};
