// C++ аналог структури опису чанка
#include <cstdint>
#include <vector>

struct btrfs_stripe_cpp {
    std::uint64_t devid;
    std::uint64_t offset;
    std::uint8_t dev_uuid[16];
};

struct btrfs_chunk_cpp {
    std::uint64_t length;
    std::uint64_t owner;
    std::uint64_t stripe_len;
    std::uint64_t type;
    std::uint16_t num_stripes;
    std::uint16_t sub_stripes;
    std::vector<btrfs_stripe_cpp> stripes;
};
