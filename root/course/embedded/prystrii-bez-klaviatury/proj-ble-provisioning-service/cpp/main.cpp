#include <array>
#include <string>
#include <string_view>
#include <span>
#include <optional>
#include <expected>
#include <vector>
#include <algorithm>

namespace prov {

inline constexpr size_t KeySize   = 32;
inline constexpr size_t NonceSize = 12;
inline constexpr size_t TagSize   = 16;
inline constexpr size_t MaxSsidLen = 32;
inline constexpr size_t MaxPassLen = 64;

enum class Status {
    Success = 0,
    InvalidLength,
    CryptoFailure,
    AuthenticationRequired,
    StationTimeout
};

struct WifiCredentials {
    std::string ssid;
    std::string password;
};

namespace crypto {
    void generate_x25519_keypair(std::span<uint8_t, KeySize> pub, std::span<uint8_t, KeySize> priv);
    bool x25519_shared_secret(std::span<const uint8_t, KeySize> peer_pub,
                             std::span<const uint8_t, KeySize> our_priv,
                             std::span<uint8_t, KeySize> shared);
    void hkdf_sha256(std::span<const uint8_t> salt,
                     std::span<const uint8_t> ikm,
                     std::span<const uint8_t> info,
                     std::span<uint8_t, KeySize> okm);
    bool aes_gcm_decrypt(std::span<const uint8_t, KeySize> key,
                         std::span<const uint8_t, NonceSize> nonce,
                         std::span<const uint8_t, TagSize> tag,
                         std::span<const uint8_t> ciphertext,
                         std::span<uint8_t> plaintext);
}

class BleProvisioningSession {
public:
    struct HandshakeResponse {
        std::array<uint8_t, KeySize>   device_public_key;
        std::array<uint8_t, NonceSize> nonce_salt;
    };

    std::expected<HandshakeResponse, Status> establish_session(
        std::span<const uint8_t> client_public_key,
        std::string_view proof_of_possession)
    {
        if (client_public_key.size() != KeySize || is_zero_vector(client_public_key)) {
            return std::unexpected(Status::InvalidLength);
        }

        HandshakeResponse response{};
        crypto::generate_x25519_keypair(response.device_public_key, priv_key_);

        std::array<uint8_t, KeySize> client_pub_arr{};
        std::copy_n(client_public_key.begin(), KeySize, client_pub_arr.begin());

        std::array<uint8_t, KeySize> shared_secret{};
        if (!crypto::x25519_shared_secret(client_pub_arr, priv_key_, shared_secret)) {
            return std::unexpected(Status::CryptoFailure);
        }

        response.nonce_salt.fill(0xA5);

        auto pop_span = std::as_bytes(std::span(proof_of_possession));
        crypto::hkdf_sha256(
            response.nonce_salt,
            shared_secret,
            std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(pop_span.data()), pop_span.size()),
            session_key_
        );

        shared_secret.fill(0); // Очищення конфіденційного секрету
        session_active_ = true;
        return response;
    }

    std::expected<WifiCredentials, Status> decrypt_credentials(std::span<const uint8_t> encrypted_payload) const {
        if (!session_active_) {
            return std::unexpected(Status::AuthenticationRequired);
        }

        constexpr size_t HeaderSize = NonceSize + TagSize;
        if (encrypted_payload.size() <= HeaderSize) {
            return std::unexpected(Status::InvalidLength);
        }

        std::span<const uint8_t, NonceSize> nonce(encrypted_payload.data(), NonceSize);
        std::span<const uint8_t, TagSize> tag(encrypted_payload.data() + NonceSize, TagSize);
        auto ciphertext = encrypted_payload.subspan(HeaderSize);

        std::vector<uint8_t> plaintext(ciphertext.size());
        if (!crypto::aes_gcm_decrypt(session_key_, nonce, tag, ciphertext, plaintext)) {
            return std::unexpected(Status::CryptoFailure);
        }

        if (plaintext.empty()) {
            return std::unexpected(Status::InvalidLength);
        }

        size_t ssid_len = plaintext[0];
        if (ssid_len > MaxSsidLen || (1 + ssid_len) >= plaintext.size()) {
            return std::unexpected(Status::InvalidLength);
        }

        std::string ssid(reinterpret_cast<char*>(&plaintext[1]), ssid_len);

        size_t pass_offset = 1 + ssid_len;
        size_t pass_len = plaintext[pass_offset];
        if (pass_len > MaxPassLen || (pass_offset + 1 + pass_len) > plaintext.size()) {
            return std::unexpected(Status::InvalidLength);
        }

        std::string password(reinterpret_cast<char*>(&plaintext[pass_offset + 1]), pass_len);

        std::fill(plaintext.begin(), plaintext.end(), 0);
        return WifiCredentials{ std::move(ssid), std::move(password) };
    }

    void reset() noexcept {
        priv_key_.fill(0);
        session_key_.fill(0);
        session_active_ = false;
    }

    ~BleProvisioningSession() {
        reset();
    }

private:
    static bool is_zero_vector(std::span<const uint8_t> span) noexcept {
        return std::all_of(span.begin(), span.end(), [](uint8_t b) { return b == 0; });
    }

    std::array<uint8_t, KeySize> priv_key_{};
    std::array<uint8_t, KeySize> session_key_{};
    bool session_active_{false};
};

} // namespace prov
