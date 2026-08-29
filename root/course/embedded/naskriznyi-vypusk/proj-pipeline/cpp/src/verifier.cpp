#include "release/verifier.hpp"

#include <algorithm>

#include <mbedtls/bignum.h>
#include <mbedtls/ecdsa.h>
#include <mbedtls/ecp.h>
#include <mbedtls/sha256.h>

namespace release {
namespace {

// 256 КіБ одним викликом — десятки мілісекунд без єдиного погладжування
// сторожового таймера, тому хешуємо блоками.
constexpr std::size_t kHashChunk = 4096;

// Обгортки без жодної логіки: їхня єдина робота — звільнити контекст,
// хоч би через яку гілку ми вийшли.
struct Sha256Context {
    mbedtls_sha256_context ctx{};
    Sha256Context() noexcept { mbedtls_sha256_init(&ctx); }
    ~Sha256Context() { mbedtls_sha256_free(&ctx); }
    Sha256Context(const Sha256Context&) = delete;
    Sha256Context& operator=(const Sha256Context&) = delete;
};

struct EcGroup {
    mbedtls_ecp_group grp{};
    EcGroup() noexcept { mbedtls_ecp_group_init(&grp); }
    ~EcGroup() { mbedtls_ecp_group_free(&grp); }
    EcGroup(const EcGroup&) = delete;
    EcGroup& operator=(const EcGroup&) = delete;
};

struct EcPoint {
    mbedtls_ecp_point point{};
    EcPoint() noexcept { mbedtls_ecp_point_init(&point); }
    ~EcPoint() { mbedtls_ecp_point_free(&point); }
    EcPoint(const EcPoint&) = delete;
    EcPoint& operator=(const EcPoint&) = delete;
};

struct Mpi {
    mbedtls_mpi value{};
    Mpi() noexcept { mbedtls_mpi_init(&value); }
    ~Mpi() { mbedtls_mpi_free(&value); }
    Mpi(const Mpi&) = delete;
    Mpi& operator=(const Mpi&) = delete;
};

// Порівняння за сталий час: звичайне == вийшло б на першому розбіжному
// байті й підказало б, скільки зловмисник уже вгадав.
[[nodiscard]] bool equalConstantTime(std::span<const std::uint8_t> lhs,
                                     std::span<const std::uint8_t> rhs) noexcept
{
    if (lhs.size() != rhs.size()) {
        return false;
    }
    std::uint8_t diff = 0;
    for (std::size_t i = 0; i < lhs.size(); ++i) {
        diff |= static_cast<std::uint8_t>(lhs[i] ^ rhs[i]);
    }
    return diff == 0;
}

}  // namespace

Verifier::Verifier(std::span<const std::uint8_t> rootPublicKey,
                   WatchdogKick watchdogKick) noexcept
    : rootKey_{rootPublicKey}, watchdogKick_{std::move(watchdogKick)}
{
}

void Verifier::kick() const
{
    if (watchdogKick_) {
        watchdogKick_();
    }
}

std::expected<Verifier::Digest, Error> Verifier::sha256(
    std::span<const std::uint8_t> head, std::span<const std::uint8_t> tail) const
{
    Sha256Context sha;
    if (mbedtls_sha256_starts(&sha.ctx, 0) != 0) {
        return std::unexpected(Error::Crypto);
    }

    for (auto part : {head, tail}) {
        while (!part.empty()) {
            const auto take = std::min(part.size(), kHashChunk);
            if (mbedtls_sha256_update(&sha.ctx, part.data(), take) != 0) {
                return std::unexpected(Error::Crypto);
            }
            part = part.subspan(take);
            kick();
        }
    }

    Digest digest{};
    if (mbedtls_sha256_finish(&sha.ctx, digest.data()) != 0) {
        return std::unexpected(Error::Crypto);
    }
    return digest;
}

std::expected<void, Error> Verifier::checkSignature(
    const Digest& digest,
    std::span<const std::uint8_t, kSignatureSize> signature) const
{
    if (rootKey_.size() != kPublicKeySize) {
        return std::unexpected(Error::Crypto);
    }

    EcGroup group;
    EcPoint pub;
    Mpi r;
    Mpi s;

    if (mbedtls_ecp_group_load(&group.grp, MBEDTLS_ECP_DP_SECP256R1) != 0
        || mbedtls_ecp_point_read_binary(&group.grp, &pub.point,
                                         rootKey_.data(), rootKey_.size()) != 0
        // Точка не з кривої — це зіпсований корінь довіри, а не поганий підпис.
        || mbedtls_ecp_check_pubkey(&group.grp, &pub.point) != 0
        // HSM віддає сирі r||s по 32 байти, без обгортки ASN.1.
        || mbedtls_mpi_read_binary(&r.value, signature.data(), 32) != 0
        || mbedtls_mpi_read_binary(&s.value, signature.data() + 32, 32) != 0) {
        return std::unexpected(Error::Crypto);
    }

    kick();

    if (mbedtls_ecdsa_verify(&group.grp, digest.data(), digest.size(),
                             &pub.point, &r.value, &s.value) != 0) {
        return std::unexpected(Error::Signature);
    }
    return {};
}

std::expected<ImageView, Error> Verifier::verify(
    std::span<const std::uint8_t> image, const Policy& policy) const
{
    auto view = parseHeader(image, policy);
    if (!view) {
        return view;
    }

    kick();  // далі йде рахунок, під час якого таймер лишається без уваги

    const auto payloadDigest = sha256({}, view->payload);
    if (!payloadDigest) {
        return std::unexpected(payloadDigest.error());
    }
    if (!equalConstantTime(*payloadDigest, view->header.payloadSha256)) {
        return std::unexpected(Error::Digest);
    }

    // Підписано заголовок разом із тілом, інакше підписане тіло можна було б
    // підставити під чужий заголовок і збити маску чи лічильник відкату.
    const auto signedDigest = sha256(image.subspan(0, kSignedPrefix), view->payload);
    if (!signedDigest) {
        return std::unexpected(signedDigest.error());
    }

    const auto ok = checkSignature(
        *signedDigest,
        std::span<const std::uint8_t, kSignatureSize>{view->header.signature});
    if (!ok) {
        return std::unexpected(ok.error());
    }

    return view;
}

}  // namespace release
