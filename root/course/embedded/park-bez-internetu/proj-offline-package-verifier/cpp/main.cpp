#include <span>
#include <array>
#include <expected>
#include <cstdint>
#include <cstring>
#include <functional>

namespace offline_update {

inline constexpr uint32_t UpkgMagic = 0x47504B55; // "UPKG"
inline constexpr std::size_t HashSize = 32;
inline constexpr std::size_t SignatureSize = 64;
inline constexpr std::size_t ChunkSize = 4096;

enum class UpdateError : uint8_t {
    InvalidMagic,
    HardwareMismatch,
    RollbackDetected,
    SignatureInvalid,
    ChunkHashMismatch,
    FinalHashMismatch,
    FlashWriteFailure
};

struct [[gnu::packed]] PackageHeader {
    uint32_t magic;
    uint16_t format_version;
    uint16_t target_hw_id;
    uint32_t version_monotonic;
    uint32_t payload_size;
    uint32_t chunk_count;
    std::array<uint8_t, HashSize> final_sha256;
    std::array<uint8_t, 40> reserved;
    std::array<uint8_t, SignatureSize> signature;
};

struct DeviceSecurityPolicy {
    uint16_t hardware_id;
    uint32_t min_allowed_version;
    std::span<const uint8_t, 32> root_public_key;
};

class PackageVerifier {
public:
    using VerifyFn = std::function<bool(std::span<const uint8_t>,
                                         std::span<const uint8_t, SignatureSize>,
                                         std::span<const uint8_t, 32>)>;
    using HashFn = std::function<void(std::span<const uint8_t>, std::span<uint8_t, HashSize>)>;
    using FlashWriteFn = std::function<bool(uint32_t offset, std::span<const uint8_t>)>;

    PackageVerifier(DeviceSecurityPolicy policy,
                    VerifyFn verify_sig,
                    HashFn hash_calc,
                    FlashWriteFn flash_writer)
        : policy_(policy),
          verify_sig_(std::move(verify_sig)),
          hash_calc_(std::move(hash_calc)),
          flash_writer_(std::move(flash_writer)) {}

    [[nodiscard]] std::expected<void, UpdateError>
    validateHeader(const PackageHeader& hdr) const {
        if (hdr.magic != UpkgMagic) {
            return std::unexpected(UpdateError::InvalidMagic);
        }
        if (hdr.target_hw_id != policy_.hardware_id) {
            return std::unexpected(UpdateError::HardwareMismatch);
        }
        if (hdr.version_monotonic <= policy_.min_allowed_version) {
            return std::unexpected(UpdateError::RollbackDetected);
        }

        constexpr std::size_t signed_len = sizeof(PackageHeader) - SignatureSize;
        auto signed_bytes = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&hdr), signed_len
        );

        if (!verify_sig_(signed_bytes, hdr.signature, policy_.root_public_key)) {
            return std::unexpected(UpdateError::SignatureInvalid);
        }

        return {};
    }

    [[nodiscard]] std::expected<void, UpdateError>
    processChunk(uint32_t chunk_index,
                 std::span<const uint8_t> chunk_data,
                 std::span<const uint8_t, HashSize> expected_hash) const {
        std::array<uint8_t, HashSize> calculated{};
        hash_calc_(chunk_data, calculated);

        if (std::memcmp(calculated.data(), expected_hash.data(), HashSize) != 0) {
            return std::unexpected(UpdateError::ChunkHashMismatch);
        }

        const uint32_t offset = chunk_index * ChunkSize;
        if (!flash_writer_(offset, chunk_data)) {
            return std::unexpected(UpdateError::FlashWriteFailure);
        }

        return {};
    }

private:
    DeviceSecurityPolicy policy_;
    VerifyFn verify_sig_;
    HashFn hash_calc_;
    FlashWriteFn flash_writer_;
};

} // namespace offline_update
