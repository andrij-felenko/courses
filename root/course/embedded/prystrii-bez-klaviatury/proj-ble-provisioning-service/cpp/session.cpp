#include "session.hpp"

#include <algorithm>
#include <vector>

namespace prov {
namespace {

// Найдовший осмислений відкритий текст: [len][SSID][len][пароль].
constexpr std::size_t PlaintextMax = 1 + MaxSsidLen + 1 + MaxPassLen;

std::uint64_t read_be64(std::span<const std::uint8_t, 8> bytes) noexcept
{
    std::uint64_t value = 0;
    for (std::uint8_t byte : bytes) {
        value = (value << 8) | byte;
    }
    return value;
}

// Розбір [ssid_len][SSID][pass_len][пароль] із перевіркою кожної межі.
std::expected<WifiCredentials, Status> parse_credentials(std::span<const std::uint8_t> pt)
{
    if (pt.size() < 2) {
        return std::unexpected(Status::InvalidLength);
    }

    const std::size_t ssid_len = pt[0];
    if (ssid_len == 0 || ssid_len > MaxSsidLen || 1 + ssid_len >= pt.size()) {
        return std::unexpected(Status::InvalidLength);  // потрібен ще байт довжини пароля
    }

    auto ssid_bytes = pt.subspan(1, ssid_len);
    if (std::ranges::find(ssid_bytes, 0) != ssid_bytes.end()) {
        return std::unexpected(Status::InvalidLength);  // нуль обрізав би імʼя мережі
    }

    const std::size_t pass_offset = 1 + ssid_len;
    const std::size_t pass_len = pt[pass_offset];
    if (pass_len > MaxPassLen || pass_offset + 1 + pass_len != pt.size()) {
        return std::unexpected(Status::InvalidLength);  // хвіст після пароля — привід відмовити
    }
    // WPA2: або відкрита мережа, або 8–63 символи парольної фрази, або 64 hex.
    if (pass_len != 0 && pass_len < 8) {
        return std::unexpected(Status::InvalidLength);
    }

    auto pass_bytes = pt.subspan(pass_offset + 1, pass_len);
    if (std::ranges::find(pass_bytes, 0) != pass_bytes.end()) {
        return std::unexpected(Status::InvalidLength);
    }

    WifiCredentials creds;
    creds.ssid.assign(reinterpret_cast<const char*>(ssid_bytes.data()), ssid_bytes.size());
    creds.password.assign(reinterpret_cast<const char*>(pass_bytes.data()), pass_bytes.size());
    return creds;
}

}  // namespace

void wipe_credentials(WifiCredentials& creds) noexcept
{
    secure_wipe({reinterpret_cast<std::uint8_t*>(creds.ssid.data()), creds.ssid.size()});
    secure_wipe({reinterpret_cast<std::uint8_t*>(creds.password.data()), creds.password.size()});
    creds.ssid.clear();
    creds.password.clear();
}

void ProvisioningSession::reset() noexcept
{
    priv_key_.wipe();
    session_key_.wipe();
    device_pub_.fill(0);
    salt_.fill(0);
    nonce_prefix_.fill(0);
    last_counter_.reset();
    established_ = false;
}

bool ProvisioningSession::locked() noexcept
{
    if (!locked_until_) {
        return false;
    }
    if (platform::uptime() >= *locked_until_) {
        locked_until_.reset();
        pop_failures_ = 0;
        return false;
    }
    return true;
}

void ProvisioningSession::lock() noexcept
{
    locked_until_ = platform::uptime() + LockoutDuration;
    reset();   // ефемерні ключі — геть
}

std::expected<ProvisioningSession::HandshakeResponse, Status>
ProvisioningSession::handshake(std::span<const std::uint8_t> request)
{
    if (locked()) {
        return std::unexpected(Status::Locked);
    }
    if (request.size() != SessionRequestSize) {
        return std::unexpected(Status::InvalidLength);
    }

    auto client_pub = request.first<KeySize>();
    auto proof = request.subspan<KeySize, ProofSize>();

    if (!public_key_acceptable(client_pub)) {
        return std::unexpected(Status::CryptoFailure);
    }

    // Доказ володіння звіряємо ДО того, як витрачати ECDH: інакше кожен
    // перехожий змушував би нас рахувати скалярне множення.
    if (!pop_proof_valid(pop_, client_pub, proof)) {
        if (++pop_failures_ >= MaxPopFailures) {
            lock();
            return std::unexpected(Status::Locked);
        }
        reset();
        return std::unexpected(Status::AuthenticationFailed);
    }

    // Пара ефемерна: кожне рукостискання починає з нових ключів, тож запис
    // старої сесії сніфером не розшифрує наступну.
    generate_keypair(priv_key_, device_pub_);
    platform::random_bytes(salt_);

    if (!derive_session_key(priv_key_, client_pub, device_pub_, salt_, pop_, session_key_)) {
        reset();
        return std::unexpected(Status::CryptoFailure);
    }

    pop_failures_ = 0;
    last_counter_.reset();
    established_ = true;

    return HandshakeResponse{device_pub_, salt_};
}

std::expected<WifiCredentials, Status>
ProvisioningSession::decrypt_config(std::span<const std::uint8_t> payload)
{
    if (locked()) {
        return std::unexpected(Status::Locked);
    }
    if (!established_) {
        return std::unexpected(Status::AuthenticationFailed);
    }

    // Кадр: [nonce 12][tag 16][шифротекст].
    constexpr std::size_t HeaderSize = NonceSize + TagSize;
    if (payload.size() <= HeaderSize || payload.size() - HeaderSize > PlaintextMax) {
        return std::unexpected(Status::InvalidLength);
    }

    auto nonce = payload.first<NonceSize>();
    auto tag = payload.subspan<NonceSize, TagSize>();
    auto ciphertext = payload.subspan(HeaderSize);

    // Nonce під одним ключем не повторюється — це вимога GCM, а не побажання.
    // Перевіряємо ДО розшифрування, а стан рухаємо лише після успіху, щоб
    // сміттєвим пакетом не можна було зафіксувати чужий префікс.
    const auto prefix = nonce.first<4>();
    const std::uint64_t counter = read_be64(nonce.subspan<4, 8>());
    if (last_counter_) {
        const bool same_prefix = std::equal(prefix.begin(), prefix.end(), nonce_prefix_.begin());
        if (!same_prefix || counter <= *last_counter_) {
            return std::unexpected(Status::Replay);
        }
    } else if (counter == 0) {
        return std::unexpected(Status::Replay);
    }

    std::vector<std::uint8_t> plaintext(ciphertext.size());
    if (!platform::aes_gcm_decrypt(session_key_.bytes(), nonce, tag, ciphertext, plaintext)) {
        secure_wipe(plaintext);
        // Тег GMAC не зійшовся: пакет підроблено, побито або зашифровано чужим ключем.
        return std::unexpected(Status::CryptoFailure);
    }

    auto creds = parse_credentials(plaintext);
    secure_wipe(plaintext);
    if (!creds) {
        return creds;
    }

    std::copy(prefix.begin(), prefix.end(), nonce_prefix_.begin());
    last_counter_ = counter;
    return creds;
}

}  // namespace prov
