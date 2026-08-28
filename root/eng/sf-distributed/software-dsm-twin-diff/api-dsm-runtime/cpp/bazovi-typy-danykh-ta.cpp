#include <cstdint>
#include <cstddef>
#include <span>
#include <vector>
#include <system_error>

constexpr size_t DsmPageSize = 4096;
constexpr size_t DsmMaxNodes = 64;
constexpr size_t DsmMaxChunks = 128;

enum class DsmErrorCode : int {
    Success = 0,
    InvalidParam = -1,
    NoMemory = -2,
    MprotectFailed = -3,
    SignalFailed = -4,
    OutOfBounds = -5,
    BufferOverflow = -6
};

enum class PageAccessState : uint8_t {
    Invalid = 0,
    ReadOnly = 1,
    DirtyTwinned = 2
};

struct alignas(uint16_t) DiffChunkHeader {
    uint16_t offset{0};
    uint16_t length{0};
};

struct DiffPacket {
    uint32_t pageId{0};
    uint32_t epochId{0};
    uint16_t chunkCount{0};
    std::vector<std::byte> payload;
};

struct DsmEngineConfig {
    size_t sharedHeapSize{1024 * 1024 * 64};
    uint32_t nodeId{0};
    uint32_t totalNodes{1};
    bool enableSimdAcceleration{true};
};
