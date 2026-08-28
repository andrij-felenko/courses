#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>
#include <string_view>
#include <algorithm>

namespace mcuboot {

inline constexpr uint32_t ImageMagic = 0x96f3b83dU;
inline constexpr uint16_t ProtectedTlvMagic = 0x6908U;
inline constexpr uint16_t NonProtectedTlvMagic = 0x6907U;

enum class TlvType : uint16_t {
    KeyHash   = 0x0001U,
    Sha256    = 0x0010U,
    EcdsaP256 = 0x0022U,
    Ed25519   = 0x0024U,
    SecCount  = 0x0050U
};

enum class VerifyError {
    InvalidMagic,
    ImageOutOfBounds,
    CorruptedTlvStructure,
    SecurityCounterDowngrade,
    HashMismatch,
    SignatureInvalid,
    MissingSignatureOrHash
};

#pragma pack(push, 1)
struct ImageHeader {
    uint32_t magic;
    uint32_t load_addr;
    uint16_t hdr_size;
    uint16_t protect_tlv_size;
    uint32_t img_size;
    uint32_t flags;
    uint8_t  ver_major;
    uint8_t  ver_minor;
    uint16_t ver_revision;
    uint32_t ver_build_num;
    uint32_t pad;
};

struct TlvInfo {
    uint16_t magic;
    uint16_t total_len;
};

struct TlvItem {
    uint16_t type;
    uint16_t len;
};
#pragma pack(pop)

/* Абстрактні апаратні залежності */
struct CryptoDriver {
    virtual void sha256_start() = 0;
    virtual void sha256_update(std::span<const uint8_t> data) = 0;
    virtual std::array<uint8_t, 32> sha256_finish() = 0;

    virtual bool verify_sig(TlvType type, std::span<const uint8_t> pubkey,
                            const std::array<uint8_t, 32>& hash,
                            std::span<const uint8_t> signature) = 0;

    virtual uint32_t read_hw_security_counter() = 0;
    virtual bool burn_hw_security_counter(uint32_t new_val) = 0;
    virtual ~CryptoDriver() = default;
};

class ImageVerifier {
public:
    explicit ImageVerifier(CryptoDriver& crypto, std::span<const uint8_t> root_pubkey) noexcept
        : crypto_{crypto}, root_pubkey_{root_pubkey} {}

    [[nodiscard]] std::expected<uint32_t, VerifyError>
    verify(std::span<const uint8_t> flash_image) noexcept {
        if (flash_image.size() < sizeof(ImageHeader)) {
            return std::unexpected(VerifyError::InvalidMagic);
        }

        const auto* hdr = reinterpret_cast<const ImageHeader*>(flash_image.data());
        if (hdr->magic != ImageMagic) {
            return std::unexpected(VerifyError::InvalidMagic);
        }

        const size_t total_payload_offset = static_cast<size_t>(hdr->hdr_size) + hdr->img_size;
        const size_t protected_tlv_sz = hdr->protect_tlv_size;

        if (total_payload_offset + protected_tlv_sz > flash_image.size()) {
            return std::unexpected(VerifyError::ImageOutOfBounds);
        }

        uint32_t img_sec_counter = 0;
        bool has_sec_counter = false;

        // 1. Парсинг захищених метаданих Protected TLV
        if (protected_tlv_sz > 0) {
            if (protected_tlv_sz < sizeof(TlvInfo)) {
                return std::unexpected(VerifyError::CorruptedTlvStructure);
            }

            auto prot_slice = flash_image.subspan(total_payload_offset, protected_tlv_sz);
            const auto* p_info = reinterpret_cast<const TlvInfo*>(prot_slice.data());

            if (p_info->magic != ProtectedTlvMagic || p_info->total_len != protected_tlv_sz) {
                return std::unexpected(VerifyError::CorruptedTlvStructure);
            }

            size_t offset = sizeof(TlvInfo);
            while (offset + sizeof(TlvItem) <= protected_tlv_sz) {
                const auto* item = reinterpret_cast<const TlvItem*>(prot_slice.data() + offset);
                if (offset + sizeof(TlvItem) + item->len > protected_tlv_sz) {
                    return std::unexpected(VerifyError::CorruptedTlvStructure);
                }

                if (static_cast<TlvType>(item->type) == TlvType::SecCount && item->len == sizeof(uint32_t)) {
                    std::copy_n(prot_slice.data() + offset + sizeof(TlvItem),
                                sizeof(uint32_t),
                                reinterpret_cast<uint8_t*>(&img_sec_counter));
                    has_sec_counter = true;
                }
                offset += sizeof(TlvItem) + item->len;
            }
        }

        // 2. Апаратна перевірка захисту від відкату (Anti-Rollback)
        const uint32_t hw_sec_cnt = crypto_.read_hw_security_counter();
        if (has_sec_counter && img_sec_counter < hw_sec_cnt) {
            return std::unexpected(VerifyError::SecurityCounterDowngrade);
        }

        // 3. Обчислення SHA-256 над Header + Payload + Protected TLVs
        crypto_.sha256_start();
        const size_t signed_len = total_payload_offset + protected_tlv_sz;
        crypto_.sha256_update(flash_image.subspan(0, signed_len));
        const auto calc_hash = crypto_.sha256_finish();

        // 4. Парсинг трейлера TLV підпису
        const size_t trailer_offset = signed_len;
        if (trailer_offset + sizeof(TlvInfo) > flash_image.size()) {
            return std::unexpected(VerifyError::CorruptedTlvStructure);
        }

        auto trailer_slice = flash_image.subspan(trailer_offset);
        const auto* t_info = reinterpret_cast<const TlvInfo*>(trailer_slice.data());

        if (t_info->magic != NonProtectedTlvMagic || trailer_offset + t_info->total_len > flash_image.size()) {
            return std::unexpected(VerifyError::CorruptedTlvStructure);
        }

        std::span<const uint8_t> expected_hash;
        std::span<const uint8_t> signature;
        TlvType sig_type{};

        size_t t_off = sizeof(TlvInfo);
        while (t_off + sizeof(TlvItem) <= t_info->total_len) {
            const auto* item = reinterpret_cast<const TlvItem*>(trailer_slice.data() + t_off);
            if (t_off + sizeof(TlvItem) + item->len > t_info->total_len) {
                return std::unexpected(VerifyError::CorruptedTlvStructure);
            }

            auto val_span = trailer_slice.subspan(t_off + sizeof(TlvItem), item->len);
            auto type = static_cast<TlvType>(item->type);

            if (type == TlvType::Sha256 && item->len == 32) {
                expected_hash = val_span;
            } else if (type == TlvType::EcdsaP256 || type == TlvType::Ed25519) {
                sig_type = type;
                signature = val_span;
            }
            t_off += sizeof(TlvItem) + item->len;
        }

        if (expected_hash.empty() || signature.empty()) {
            return std::unexpected(VerifyError::MissingSignatureOrHash);
        }

        // Порівняння за сталий час
        uint8_t diff = 0;
        for (size_t i = 0; i < 32; ++i) {
            diff |= (calc_hash[i] ^ expected_hash[i]);
        }
        if (diff != 0) {
            return std::unexpected(VerifyError::HashMismatch);
        }

        // 5. Перевірка цифрового підпису відкритим ключем
        if (!crypto_.verify_sig(sig_type, root_pubkey_, calc_hash, signature)) {
            return std::unexpected(VerifyError::SignatureInvalid);
        }

        return img_sec_counter;
    }

private:
    CryptoDriver& crypto_;
    std::span<const uint8_t> root_pubkey_;
};

} // namespace mcuboot
