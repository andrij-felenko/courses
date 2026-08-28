#include <linux/dm-ioctl.h>
#include <cstdint>

// Описувач запису таблиці секторів у C++
struct DmTargetSpecHeader {
    std::uint64_t sector_start; /* Початковий сектор віртуального тома */
    std::uint64_t length;       /* Довжина відрізка в секторах */
    std::int32_t status;        /* Повернений код статусу */
    std::uint32_t next;         // Зсув у буфері до наступного сегмента
    char target_type[16];       // DM_MAX_TYPE_NAME: "linear", "crypt", ...
};
