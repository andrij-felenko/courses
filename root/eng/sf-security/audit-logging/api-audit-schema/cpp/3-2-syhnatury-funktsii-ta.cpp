#include <string_view>
#include <span>
#include <memory>
#include <expected>
#include <cstdint>

namespace security::audit {

enum class WormError {
    InvalidParam = -1,
    DiskFull = -2,
    ChainBroken = -3,
    SignatureFailed = -4,
    KeyExhausted = -5,
    IoError = -6
};

class IWormAuditStorage {
public:
    virtual ~IWormAuditStorage() = default;

    virtual std::expected<uint64_t, WormError> append(std::span<const uint8_t> payload) = 0;
    virtual std::expected<void, WormError> flush() = 0;
    virtual std::expected<void, WormError> verifyRange(uint64_t from_seq, uint64_t to_seq) const = 0;
};

std::expected<std::unique_ptr<IWormAuditStorage>, WormError>
createWormStorage(std::string_view storage_path, std::span<const uint8_t, 32> master_key);

} // namespace security::audit
