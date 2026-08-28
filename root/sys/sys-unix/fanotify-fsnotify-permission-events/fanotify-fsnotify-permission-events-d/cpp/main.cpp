#include <cstdint>

struct fanotify_event_metadata {
    std::uint32_t event_len;      // Загальний розмір запису
    std::uint8_t  vers;           // Версія метаданих
    std::uint8_t  reserved;       
    std::uint16_t metadata_len;   
    std::uint64_t mask;           // Маска події (FAN_OPEN_PERM)
    std::int32_t  fd;             // Дескриптор файлу від ядра
    std::int32_t  pid;            // PID викликача
};
