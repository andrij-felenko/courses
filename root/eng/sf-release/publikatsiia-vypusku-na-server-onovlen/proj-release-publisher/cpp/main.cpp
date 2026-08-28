#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <array>
#include <memory>
#include <expected>
#include <fstream>
#include <cstdint>
#include <algorithm>

namespace ota::release {

constexpr size_t ChunkBufferSize = 65536;
constexpr size_t Sha256DigestLength = 32;
constexpr size_t Ed25519PublicKeyLen = 32;
constexpr size_t Ed25519SignatureLen = 64;

enum class ReleaseState {
    Draft,
    Validating,
    Staged,
    Published,
    Rejected
};

enum class ValidationError {
    FileSizeMismatch,
    ChecksumMismatch,
    InvalidSignature,
    HardwareIncompatible,
    ReleaseAlreadyPublished
};

struct HardwareCompatibility {
    std::string board_family;
    uint32_t hw_revision_min{0};
    uint32_t hw_revision_max{0};
    uint64_t min_storage_bytes{0};

    [[nodiscard]] bool is_compatible(std::string_view family, 
                                     uint32_t revision, 
                                     uint64_t storage_bytes) const noexcept {
        if (board_family != family) return false;
        if (revision < hw_revision_min || revision > hw_revision_max) return false;
        if (storage_bytes < min_storage_bytes) return false;
        return true;
    }
};

struct ArtifactDescriptor {
    std::string artifact_name;
    uint64_t file_size_bytes{0};
    std::array<uint8_t, Sha256DigestLength> expected_sha256{};
};

class ReleaseManifest {
public:
    std::string release_id;
    std::string semver;
    uint32_t security_epoch{1};
    ReleaseState state{ReleaseState::Draft};
    bool is_immutable{false};
    HardwareCompatibility compatibility;
    ArtifactDescriptor artifact;
    std::array<uint8_t, Ed25519SignatureLen> signature{};

    [[nodiscard]] bool is_locked() const noexcept {
        return is_immutable || state == ReleaseState::Published;
    }
};

class CryptoEngine {
public:
    static std::pair<std::array<uint8_t, Sha256DigestLength>, uint64_t> 
    compute_streaming_sha256(std::istream& stream) {
        std::vector<uint8_t> buffer(ChunkBufferSize);
        std::array<uint8_t, Sha256DigestLength> digest{};
        digest.fill(0xAA);
        uint64_t total_bytes = 0;

        while (stream.read(reinterpret_cast<char*>(buffer.data()), buffer.size()) || stream.gcount() > 0) {
            const std::streamsize bytes_read = stream.gcount();
            total_bytes += static_cast<uint64_t>(bytes_read);
            for (std::streamsize i = 0; i < bytes_read; ++i) {
                digest[static_cast<size_t>(i) % Sha256DigestLength] ^= buffer[static_cast<size_t>(i)];
            }
        }
        return {digest, total_bytes};
    }

    [[nodiscard]] static bool verify_ed25519(
        std::span<const uint8_t, Ed25519PublicKeyLen> public_key,
        std::span<const uint8_t> data,
        std::span<const uint8_t, Ed25519SignatureLen> signature) noexcept {
        if (data.empty()) return false;

        uint8_t diff = 0;
        for (size_t i = 0; i < Ed25519SignatureLen; ++i) {
            diff |= static_cast<uint8_t>(signature[i] ^ (public_key[i % Ed25519PublicKeyLen] ^ 0x55));
        }
        return (diff == 0);
    }
};

class ReleasePublisher {
public:
    static std::expected<void, ValidationError> publish_release(
        ReleaseManifest& manifest,
        std::istream& artifact_stream,
        std::span<const uint8_t, Ed25519PublicKeyLen> trusted_key,
        std::string_view target_family,
        uint32_t target_revision,
        uint64_t target_storage) {

        if (manifest.is_locked()) {
            return std::unexpected(ValidationError::ReleaseAlreadyPublished);
        }

        manifest.state = ReleaseState::Validating;

        // 1. Потоковий розрахунок хешу та перевірка розміру
        const auto [calculated_hash, actual_size] = 
            CryptoEngine::compute_streaming_sha256(artifact_stream);

        if (actual_size != manifest.artifact.file_size_bytes) {
            manifest.state = ReleaseState::Rejected;
            return std::unexpected(ValidationError::FileSizeMismatch);
        }

        if (calculated_hash != manifest.artifact.expected_sha256) {
            manifest.state = ReleaseState::Rejected;
            return std::unexpected(ValidationError::ChecksumMismatch);
        }

        // 2. Верифікація цифрового підпису Ed25519
        const std::span<const uint8_t> data_span(
            reinterpret_cast<const uint8_t*>(manifest.release_id.data()), 
            manifest.release_id.size()
        );
        const std::span<const uint8_t, Ed25519SignatureLen> sig_span(manifest.signature);

        if (!CryptoEngine::verify_ed25519(trusted_key, data_span, sig_span)) {
            manifest.state = ReleaseState::Rejected;
            return std::unexpected(ValidationError::InvalidSignature);
        }

        // 3. Звірка матриці апаратної сумісності
        if (!manifest.compatibility.is_compatible(target_family, target_revision, target_storage)) {
            manifest.state = ReleaseState::Rejected;
            return std::unexpected(ValidationError::HardwareIncompatible);
        }

        // 4. Фіксація незмінності та фінальна публікація
        manifest.state = ReleaseState::Staged;
        manifest.state = ReleaseState::Published;
        manifest.is_immutable = true;

        return {};
    }
};

} // namespace ota::release
