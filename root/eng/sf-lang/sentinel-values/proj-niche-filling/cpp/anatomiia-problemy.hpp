#include <cstdint>
#include <optional>

// У стандартному C++ std::optional<uint32_t> поводиться так само
struct ManualOptionalU32 {
    uint32_t value{0};
    bool has_value{false};
    // 3 байти сміття (padding) для збереження вирівнювання за 4 байти
};

static_assert(sizeof(ManualOptionalU32) == 8);
static_assert(sizeof(std::optional<uint32_t>) == 8);
