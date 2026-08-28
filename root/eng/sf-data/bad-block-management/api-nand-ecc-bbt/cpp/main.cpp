#include <cstdint>
#include <string_view>
#include <array>

namespace mtd {

enum class BbtOption : uint32_t {
    CreateOnDemand = 0x00000001,
    StoreVersion   = 0x00000020,
    ScanAllPages   = 0x00000400,
    UseFlashMemory = 0x00020000,
    StoreInMainArea= 0x00040000
};

constexpr uint32_t operator|(BbtOption a, BbtOption b) noexcept {
    return static_cast<uint32_t>(a) | static_cast<uint32_t>(b);
}

template <size_t MaxChips = 8>
struct NandBbtDescriptor {
    uint32_t                      options{0};
    std::array<int32_t, MaxChips> pages{};
    int32_t                       offset{0};
    int32_t                       versionOffset{0};
    std::array<uint8_t, MaxChips> version{};
    int32_t                       patternLength{4};
    int32_t                       maxSearchBlocks{4};
    std::string_view              pattern{"Bbt0"};
};

} // namespace mtd
