#include <linux/dm-ioctl.h>
#include <cstdint>
#include <cstddef>

// Обгортка структури dm_ioctl у C++ з підтримкою вирівнювання пам'яті
struct alignas(8) DmIoctlHeader {
    std::uint32_t version[3];   // Версія API: {MAJOR, MINOR, PATCH}
    std::uint32_t data_size;    // Повний розмір виділеного буфера
    std::uint32_t data_start;   // Зсув до таблиць dm_target_spec

    std::uint32_t target_count; // Кількість записів dm_target_spec у буфері
    std::int32_t  open_count;   // Кількість активних відкриттів пристрою (з ядра)
    std::uint32_t flags;        // Статусні прапорці Device Mapper

    std::uint32_t event_nr;     // Номер події / udev-cookie
    std::uint32_t padding;      // Не використовується

    std::uint64_t dev;          // Ідентифікатор пристрою (dev_t)

    char name[128];             // DM_NAME_LEN
    char uuid[129];             // DM_UUID_LEN
    char data[7];               // Вирівнювання або початок даних
};
