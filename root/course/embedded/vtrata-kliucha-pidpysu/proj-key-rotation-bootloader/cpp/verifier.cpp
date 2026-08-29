#include "verifier.hpp"

#include <algorithm>
#include <array>

#include "mbedtls/bignum.h"
#include "mbedtls/ecdsa.h"
#include "mbedtls/ecp.h"
#include "mbedtls/memory_buffer_alloc.h"
#include "mbedtls/sha256.h"

namespace boot {
namespace {

// Купи в завантажувачі немає, а mbedtls_ecdsa_verify() заводить великі числа
// через calloc(). Тому mbedTLS збирають із MBEDTLS_MEMORY_BUFFER_ALLOC_C,
// і всі його виділення йдуть у цей статичний масив.
alignas(8) std::array<std::uint8_t, 6144> g_cryptoArena{};

// Кожен об'єкт mbedTLS вимагає парного _init/_free. Тримати цю пару руками
// в коді з десятком ранніх виходів — гарантована витік-помилка, тож пару
// тримає деструктор.
class Sha256 {
public:
    Sha256() noexcept { mbedtls_sha256_init(&ctx_); }
    ~Sha256() noexcept { mbedtls_sha256_free(&ctx_); }
    Sha256(const Sha256&) = delete;
    Sha256& operator=(const Sha256&) = delete;

    [[nodiscard]] bool start() noexcept { return mbedtls_sha256_starts(&ctx_, 0) == 0; }

    [[nodiscard]] bool update(std::span<const std::uint8_t> data) noexcept
    {
        return mbedtls_sha256_update(&ctx_, data.data(), data.size()) == 0;
    }

    [[nodiscard]] bool finish(Digest& out) noexcept
    {
        return mbedtls_sha256_finish(&ctx_, out.data()) == 0;
    }

private:
    mbedtls_sha256_context ctx_{};
};

class EcGroup {
public:
    EcGroup() noexcept { mbedtls_ecp_group_init(&group_); }
    ~EcGroup() noexcept { mbedtls_ecp_group_free(&group_); }
    EcGroup(const EcGroup&) = delete;
    EcGroup& operator=(const EcGroup&) = delete;

    [[nodiscard]] bool load(mbedtls_ecp_group_id id) noexcept
    {
        return mbedtls_ecp_group_load(&group_, id) == 0;
    }

    [[nodiscard]] mbedtls_ecp_group* raw() noexcept { return &group_; }

private:
    mbedtls_ecp_group group_{};
};

class EcPoint {
public:
    EcPoint() noexcept { mbedtls_ecp_point_init(&point_); }
    ~EcPoint() noexcept { mbedtls_ecp_point_free(&point_); }
    EcPoint(const EcPoint&) = delete;
    EcPoint& operator=(const EcPoint&) = delete;

    [[nodiscard]] mbedtls_ecp_point* raw() noexcept { return &point_; }

private:
    mbedtls_ecp_point point_{};
};

class Mpi {
public:
    Mpi() noexcept { mbedtls_mpi_init(&value_); }
    ~Mpi() noexcept { mbedtls_mpi_free(&value_); }
    Mpi(const Mpi&) = delete;
    Mpi& operator=(const Mpi&) = delete;

    [[nodiscard]] bool read(std::span<const std::uint8_t> bytes) noexcept
    {
        return mbedtls_mpi_read_binary(&value_, bytes.data(), bytes.size()) == 0;
    }

    [[nodiscard]] mbedtls_mpi* raw() noexcept { return &value_; }

private:
    mbedtls_mpi value_{};
};

[[nodiscard]] std::expected<Digest, Status> digestOf(std::span<const std::uint8_t> header,
                                                     std::span<const std::uint8_t> payload) noexcept
{
    Sha256 sha;
    Digest digest{};

    // Заголовок мусить бути під підписом разом із тілом: інакше зловмисник
    // бере старий вразливий образ із його ЧИННИМ підписом, підмінює в
    // заголовку версію безпеки — і анти-відкат пропускає підробку.
    if (!sha.start() || !sha.update(header) || !sha.update(payload) || !sha.finish(digest)) {
        return std::unexpected(Status::CryptoEngineFailure);
    }

    return digest;
}

[[nodiscard]] std::expected<Digest, Status> digestOf(std::span<const std::uint8_t> data) noexcept
{
    Sha256 sha;
    Digest digest{};

    if (!sha.start() || !sha.update(data) || !sha.finish(digest)) {
        return std::unexpected(Status::CryptoEngineFailure);
    }

    return digest;
}

[[nodiscard]] std::expected<void, Status>
verifySignature(std::span<const std::uint8_t, kPublicKeySize> publicKey,
                const Digest& digest,
                std::span<const std::uint8_t, kSignatureSize> signature) noexcept
{
    EcGroup group;
    if (!group.load(MBEDTLS_ECP_DP_SECP256R1)) {
        return std::unexpected(Status::CryptoEngineFailure);
    }

    // Нестиснена форма точки: 0x04 || X || Y.
    std::array<std::uint8_t, 1 + kPublicKeySize> encoded{};
    encoded[0] = 0x04;
    std::ranges::copy(publicKey, encoded.begin() + 1);

    EcPoint point;
    if (mbedtls_ecp_point_read_binary(group.raw(), point.raw(),
                                      encoded.data(), encoded.size()) != 0) {
        return std::unexpected(Status::SignatureInvalid);
    }
    // Точка мусить лежати на кривій і в потрібній підгрупі: без цієї перевірки
    // підсунутий «ключ» поза кривою відкриває атаку невірної кривої.
    if (mbedtls_ecp_check_pubkey(group.raw(), point.raw()) != 0) {
        return std::unexpected(Status::SignatureInvalid);
    }

    Mpi r;
    Mpi s;
    if (!r.read(signature.first(32)) || !s.read(signature.subspan(32, 32))) {
        return std::unexpected(Status::CryptoEngineFailure);
    }

    if (mbedtls_ecdsa_verify(group.raw(), digest.data(), digest.size(),
                             point.raw(), r.raw(), s.raw()) != 0) {
        return std::unexpected(Status::SignatureInvalid);
    }

    return {};
}

} // namespace

void initCryptoArena() noexcept
{
    mbedtls_memory_buffer_alloc_init(reinterpret_cast<unsigned char*>(g_cryptoArena.data()),
                                     g_cryptoArena.size());
}

std::expected<void, Status>
SecureBootVerifier::verify(const Manifest& manifest,
                           std::span<const std::uint8_t> payload) const noexcept
{
    const std::uint8_t slot = manifest.keySlotIndex();
    if (slot >= kKeySlots) {
        return std::unexpected(Status::InvalidSlot);
    }

    // 1. Відкликання: слот могли спалити після витоку ключа.
    if (efuse_.isRevoked(slot)) {
        return std::unexpected(Status::KeyRevoked);
    }

    // 2. Корінь довіри: у перемички зашито не сам ключ, а його хеш — 32 байти
    // на слот замість 64, і ключ можна змінити, не міняючи залізо.
    const auto keyDigest = digestOf(manifest.publicKey());
    if (!keyDigest) {
        return std::unexpected(keyDigest.error());
    }
    if (!constantTimeEqual(*keyDigest, efuse_.rootKeyDigest[slot])) {
        return std::unexpected(Status::RootMismatch);
    }

    // 3. Анти-відкат: версія нижча за апаратний лічильник — образ мертвий.
    if (manifest.securityVersion() < efuse_.monotonicCounter) {
        return std::unexpected(Status::RollbackDetected);
    }

    // 4. Найдорожча перевірка — останньою, коли дешеві вже пройшли.
    const auto imageDigest = digestOf(manifest.signedHeader(), payload);
    if (!imageDigest) {
        return std::unexpected(imageDigest.error());
    }

    return verifySignature(manifest.publicKey(), *imageDigest, manifest.signature());
}

} // namespace boot
