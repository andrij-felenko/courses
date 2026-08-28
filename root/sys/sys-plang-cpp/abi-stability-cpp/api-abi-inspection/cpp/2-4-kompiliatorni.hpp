#include <cstddef>
#include <type_traits>

struct PacketHeader {
    uint32_t magic;
    uint16_t version;
    uint16_t payload_size;
    uint64_t sequence_id;
};

// Статичні інваріанти ABI: гарантують падіння збірки при спробі змінити структуру
static_assert(sizeof(PacketHeader) == 16, "Критична помилка: розмір PacketHeader змінився!");
static_assert(alignof(PacketHeader) == 8, "Критична помилка: вирівнювання PacketHeader змінилося!");
static_assert(offsetof(PacketHeader, magic) == 0, "Зсув поля magic порушено!");
static_assert(offsetof(PacketHeader, version) == 4, "Зсув поля version порушено!");
static_assert(offsetof(PacketHeader, payload_size) == 6, "Зсув поля payload_size порушено!");
static_assert(offsetof(PacketHeader, sequence_id) == 8, "Зсув поля sequence_id порушено!");
static_assert(std::is_standard_layout_v<PacketHeader>, "PacketHeader повинен мати стандартну розкладку!");
