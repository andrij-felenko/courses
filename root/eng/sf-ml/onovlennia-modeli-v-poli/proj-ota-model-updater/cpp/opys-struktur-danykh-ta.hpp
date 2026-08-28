#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>
#include <string_view>

namespace emb::ml {

inline constexpr uint32_t kModelMagic = 0x4D4C5550U; // 'MLUP'
inline constexpr uint16_t kHeaderVersion = 1U;
inline constexpr uint32_t kFlashSectorSize = 4096U;
inline constexpr uint32_t kModelMaxSize = 512U * 1024U;
inline constexpr uint32_t kMetaMagic = 0x4D455441U; // 'META'
inline constexpr uint8_t  kMaxTrialBoots = 3U;

enum class SlotId : uint8_t {
    SlotA = 0,
    SlotB = 1,
    Invalid = 0xFF
};

enum class SlotState : uint8_t {
    Empty = 0,
    Trial = 1,
    Confirmed = 2,
    Failed = 3
};

enum class OtaError : uint8_t {
    InvalidMagic,
    IncompatibleSchema,
    ArenaOverflow,
    HashMismatch,
    FlashIoError,
    OffsetGap,
    InvalidState
};

#pragma pack(push, 1)
struct ModelHeader {
    uint32_t magic;
    uint16_t header_version;
    uint16_t model_version_major;
    uint16_t model_version_minor;
    uint16_t model_version_patch;
    uint32_t payload_size;
    uint32_t required_arena_size;
    uint32_t input_shape_hash;
    uint32_t output_shape_hash;
    uint16_t target_schema_version;
    uint16_t flags;
    std::array<uint8_t, 32> sha256;
    std::array<uint8_t, 64> signature;
};

struct NvMetadata {
    uint32_t meta_magic;
    uint32_t sequence_id;
    SlotId   active_slot;
    std::array<SlotState, 2> slot_state;
    uint8_t  trial_boots_remaining;
    uint32_t crc32;
};
#pragma pack(pop)

struct FlashDriver {
    bool (*read)(uint32_t addr, std::span<uint8_t> dst);
    bool (*write)(uint32_t addr, std::span<const uint8_t> src);
    bool (*erase_sector)(uint32_t sector_addr);
};

struct OtaConfig {
    uint32_t nv_meta_addr;
    std::array<uint32_t, 2> slot_addrs;
    uint32_t max_sram_arena;
};

} // namespace emb::ml
