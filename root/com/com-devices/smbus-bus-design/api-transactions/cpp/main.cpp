#include <cstdint>
#include <cstddef>
#include <array>

namespace smbus::uapi {

inline constexpr size_t BLOCK_MAX = 32;

enum class Direction : uint8_t {
    Write = 0,
    Read  = 1
};

enum class TransactionSize : uint32_t {
    Quick           = 0,
    Byte            = 1,
    ByteData        = 2,
    WordData        = 3,
    ProcCall        = 4,
    BlockData       = 5,
    I2cBlockData    = 8,
    BlockProcCall   = 9
};

union SmbusDataBuffer {
    uint8_t  byte;
    uint16_t word;
    std::array<uint8_t, BLOCK_MAX + 2> block;
};

struct SmbusIoctlArgs {
    Direction        direction{Direction::Read};
    uint8_t          command{0};
    TransactionSize  size{TransactionSize::ByteData};
    SmbusDataBuffer* data{nullptr};
};

} // namespace smbus::uapi
