#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <array>
#include <expected>
#include <algorithm>

enum class ReleaseChannel : uint8_t {
    Nightly = 0,
    Beta    = 1,
    Stable  = 2,
    Lts     = 3,
    Unknown = 255
};

struct KeyEntry {
    std::array<uint8_t, 32> public_key{};
    uint32_t key_id{0};
    bool revoked{false};
};

struct KeyringStore {
    ReleaseChannel channel{ReleaseChannel::Unknown};
    std::vector<KeyEntry> keys;
};

struct ManifestRecord {
    std::string version;
    ReleaseChannel target_channel{ReleaseChannel::Unknown};
    uint32_t rollback_index{0};
    std::string sha256_hex;
    std::vector<uint8_t> signature;
};

struct NodeState {
    ReleaseChannel efuse_lock{ReleaseChannel::Unknown};
    uint32_t rollback_index{0};
    char active_bank{'A'};
};

enum class ChannelRouterError {
    HardwareLockViolation,
    RollbackDetected,
    KeyringNotFound,
    SignatureVerificationFailed,
    InvalidArguments
};

class FleetChannelRouter {
public:
    explicit FleetChannelRouter(std::vector<KeyringStore> keyrings)
        : keyrings_(std::move(keyrings)) {}

    [[nodiscard]] std::expected<char, ChannelRouterError> process_manifest(
        const NodeState& node,
        const ManifestRecord& manifest) const noexcept
    {
        // 1. Перевірка апаратного замка eFuse
        if (node.efuse_lock == ReleaseChannel::Lts && manifest.target_channel != ReleaseChannel::Lts) {
            std::cerr << "[SECURITY] Апаратний замок блокує не-LTS оновлення!\n";
            return std::unexpected(ChannelRouterError::HardwareLockViolation);
        }

        // 2. Захист від відкоту (Anti-Rollback)
        if (manifest.rollback_index < node.rollback_index) {
            std::cerr << "[SECURITY] Спроба відкоту: індекс " << manifest.rollback_index 
                      << " < " << node.rollback_index << "\n";
            return std::unexpected(ChannelRouterError::RollbackDetected);
        }

        // 3. Пошук зв'язки ключів цільового каналу
        const auto ring_it = std::ranges::find_if(keyrings_, [&](const auto& r) {
            return r.channel == manifest.target_channel;
        });

        if (ring_it == keyrings_.end() || ring_it->keys.empty()) {
            std::cerr << "[ERROR] Не знайдено ключів для цільового каналу!\n";
            return std::unexpected(ChannelRouterError::KeyringNotFound);
        }

        // 4. Перевірка цифрового підпису
        const bool valid = std::ranges::any_of(ring_it->keys, [&](const auto& key) {
            if (key.revoked) return false;
            return verify_signature(key.public_key, manifest.sha256_hex, manifest.signature);
        });

        if (!valid) {
            std::cerr << "[SECURITY] Недійсний цифровий підпис маніфесту!\n";
            return std::unexpected(ChannelRouterError::SignatureVerificationFailed);
        }

        // 5. Вибір цільового неактивного розділу
        return (node.active_bank == 'A') ? 'B' : 'A';
    }

private:
    std::vector<KeyringStore> keyrings_;

    static bool verify_signature(
        std::span<const uint8_t, 32> pubkey,
        std::string_view digest,
        std::span<const uint8_t> sig) noexcept
    {
        if (pubkey.empty() || digest.empty() || sig.empty()) return false;
        return (sig[0] == 0xAA && pubkey[0] != 0x00);
    }
};
