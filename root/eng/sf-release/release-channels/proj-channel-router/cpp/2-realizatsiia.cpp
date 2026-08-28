#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <optional>
#include <expected>
#include <array>
#include <algorithm>

enum class Channel : uint8_t {
    Nightly = 0,
    Beta    = 1,
    Stable  = 2,
    Lts     = 3,
    Unknown = 255
};

struct CryptoKey {
    std::array<uint8_t, 32> key_data{};
    uint32_t key_id{0};
    bool is_revoked{false};
};

struct ChannelKeyring {
    Channel channel{Channel::Unknown};
    std::vector<CryptoKey> keys;
};

struct ReleaseManifest {
    std::string version;
    Channel channel{Channel::Unknown};
    uint32_t rollback_counter{0};
    std::string sha256_hex;
    std::vector<uint8_t> signature;
    size_t image_size_bytes{0};
};

struct DeviceState {
    std::string current_version;
    Channel subscribed_channel{Channel::Stable};
    Channel hardware_lock_channel{Channel::Unknown}; // Апаратний замок eFuse
    uint32_t hw_rollback_counter{0};
    char active_partition{'A'};
};

enum class RouterError {
    ChannelForbidden,
    RollbackDetected,
    SignatureInvalid,
    NoValidKeyring,
    StorageFailure
};

class ChannelRouter {
public:
    explicit ChannelRouter(std::vector<ChannelKeyring> keyrings)
        : keyrings_(std::move(keyrings)) {}

    [[nodiscard]] std::expected<char, RouterError> evaluate_and_route(
        const DeviceState& device,
        const ReleaseManifest& manifest) const noexcept 
    {
        // 1. Перевірка апаратного eFuse обмеження
        if (device.hardware_lock_channel == Channel::Lts && manifest.channel != Channel::Lts) {
            std::cerr << "[SECURITY ALERT] eFuse захист: пристрій заблоковано виключно на LTS!\n";
            return std::unexpected(RouterError::ChannelForbidden);
        }

        // 2. Захист від відкоту (Anti-Rollback)
        if (manifest.rollback_counter < device.hw_rollback_counter) {
            std::cerr << "[SECURITY ALERT] Спроба Downgrade: лічильник маніфесту " 
                      << manifest.rollback_counter << " < апаратного " 
                      << device.hw_rollback_counter << "\n";
            return std::unexpected(RouterError::RollbackDetected);
        }

        // 3. Пошук зв'язки ключів цільового каналу
        const auto it = std::ranges::find_if(keyrings_, [&](const auto& kr) {
            return kr.channel == manifest.channel;
        });

        if (it == keyrings_.end() || it->keys.empty()) {
            std::cerr << "[ERROR] Не знайдено довірених ключів для цільового каналу!\n";
            return std::unexpected(RouterError::NoValidKeyring);
        }

        // 4. Перевірка цифрового підпису Ed25519
        const bool verified = std::ranges::any_of(it->keys, [&](const auto& key) {
            if (key.is_revoked) return false;
            return verify_signature(key.key_data, manifest.sha256_hex, manifest.signature);
        });

        if (!verified) {
            std::cerr << "[SECURITY ALERT] Цифровий підпис не відповідає жодному ключу каналу!\n";
            return std::unexpected(RouterError::SignatureInvalid);
        }

        // 5. Вибір пасивного розділу
        const char target_bank = (device.active_partition == 'A') ? 'B' : 'A';
        return target_bank;
    }

private:
    std::vector<ChannelKeyring> keyrings_;

    static bool verify_signature(
        std::span<const uint8_t, 32> pubkey,
        std::string_view hash_hex,
        std::span<const uint8_t> signature) noexcept 
    {
        if (pubkey.empty() || hash_hex.empty() || signature.empty()) {
            return false;
        }
        // Імітація криптографічної перевірки
        return (signature[0] == 0xAA && pubkey[0] != 0x00);
    }
};
