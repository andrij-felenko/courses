#include <iostream>
#include <cstddef>
#include <cstdint>
#include <type_traits>

struct alignas(8) NetworkPacket {
    uint32_t header;
    uint64_t payload;
    uint16_t footer;
};

static_assert(std::is_standard_layout_v<NetworkPacket>, "Структура повинна мати Standard Layout!");
static_assert(sizeof(NetworkPacket) == 24, "Розмір NetworkPacket має бути рівно 24 байти!");
static_assert(offsetof(NetworkPacket, payload) == 8, "Зміщення payload повинно дорівнювати 8!");
static_assert(alignof(NetworkPacket) == 8, "Вирівнювання NetworkPacket має дорівнювати 8!");
