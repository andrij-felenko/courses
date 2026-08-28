// Концептуальне відображення стану зон вузла в C++
#include <vector>
#include <string>
#include <cstdint>

struct NumaZoneDescriptor {
    std::string zone_name;
    std::uint64_t free_pages{0};
    std::uint64_t watermark_min{0};
    std::uint64_t watermark_low{0};
    std::uint64_t watermark_high{0};
};
