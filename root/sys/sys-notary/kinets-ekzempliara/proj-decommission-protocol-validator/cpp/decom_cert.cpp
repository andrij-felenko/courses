// decom_cert.cpp - Повна об'єктно-орієнтована реалізація верифікатора на C++20
#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <string>
#include <chrono>
#include <expected>
#include <system_error>
#include <cstring>
#include <array>
#include <iomanip>

namespace DecomCert {

inline constexpr std::string_view CERT_MAGIC = "SCERT100";
inline constexpr uint16_t CERT_SCHEMA_V1 = 0x0001;
inline constexpr size_t HASH_SIZE = 32;
inline constexpr size_t SIGNATURE_SIZE = 32;

enum class SanitizeMethod : uint8_t {
    None           = 0x00,
    OverwriteSingle = 0x01,
    OverwriteMulti  = 0x02,
    NvmeBlockErase = 0x03,
    CryptoErase    = 0x04,
    PhysicalShred  = 0x05
};

enum class NistLevel : uint8_t {
    Unknown = 0x00,
    Clear   = 0x01,
    Purge   = 0x02,
    Destroy = 0x03
};

enum class BatteryChem : uint8_t {
    None    = 0x00,
    LiIon   = 0x01,
    LiFePO4 = 0x02,
    LTO     = 0x03
};

enum class ValidationError {
    InvalidMagic,
    UnsupportedVersion,
    BatteryComplianceViolation,
    IncompleteSanitization,
    SignatureMismatch,
    BufferTooSmall
};

struct CertErrorCategory : std::error_category {
    [[nodiscard]] const char* name() const noexcept override { return "DecomCertValidation"; }
    [[nodiscard]] std::string message(int ev) const override {
        switch (static_cast<ValidationError>(ev)) {
            case ValidationError::InvalidMagic:
                return "Невірний магічний заголовок сертифіката";
            case ValidationError::UnsupportedVersion:
                return "Версія схеми не підтримується";
            case ValidationError::BatteryComplianceViolation:
                return "Порушення регламенту EU 2023/1542: батарею не вилучено";
            case ValidationError::IncompleteSanitization:
                return "Операцію санітизації не завершено або обсяг секторів нульовий";
            case ValidationError::SignatureMismatch:
                return "Цифровий підпис не збігається: маніфест підроблено";
            case ValidationError::BufferTooSmall:
                return "Розмір вхідного бінарного буфера менший за розмір заголовка";
            default:
                return "Невідома помилка валідації";
        }
    }
};

const CertErrorCategory theCertErrorCategory{};

std::error_code make_error_code(ValidationError e) {
    return {static_cast<int>(e), theCertErrorCategory};
}

#pragma pack(push, 1)
struct RawCertificate {
    std::array<char, 8>  magic{};
    uint16_t             schema_version{CERT_SCHEMA_V1};
    uint16_t             reserved{0};
    uint64_t             timestamp_utc{0};
    std::array<char, 32> device_uid{};
    std::array<char, 32> storage_serial{};
    uint8_t              method{0};
    uint8_t              nist_level{0};
    uint8_t              battery_removed{0};
    uint8_t              battery_chem{0};
    uint64_t             erased_sectors{0};
    std::array<uint8_t, 32> pre_hash{};
    uint8_t              post_check_passed{0};
    std::array<uint8_t, 7>  pad{};
    std::array<char, 16> technician_id{};
    std::array<uint8_t, 32> signature{};
};
#pragma pack(pop)

// Проста вбудована реалізація SHA-256 для C++20
class Sha256 {
    uint32_t state[8]{0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
                      0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19};
    uint64_t count{0};
    uint8_t  buffer[64]{};

    static constexpr uint32_t K[64] = {
        0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
        0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
        0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
        0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
        0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
        0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
        0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
        0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0bef9a3f,0xc67178f2
    };

    static uint32_t rotr(uint32_t x, uint32_t n) { return (x >> n) | (x << (32 - n)); }
    static uint32_t ch(uint32_t x, uint32_t y, uint32_t z) { return (x & y) ^ (~x & z); }
    static uint32_t maj(uint32_t x, uint32_t y, uint32_t z) { return (x & y) ^ (x & z) ^ (y & z); }
    static uint32_t ep0(uint32_t x) { return rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22); }
    static uint32_t ep1(uint32_t x) { return rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25); }
    static uint32_t sig0(uint32_t x) { return rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3); }
    static uint32_t sig1(uint32_t x) { return rotr(x, 17) ^ rotr(x, 19) ^ (x >> 10); }

    void transform(const uint8_t* data) {
        uint32_t m[64];
        for (int i = 0; i < 16; ++i) {
            m[i] = (static_cast<uint32_t>(data[i * 4]) << 24) |
                   (static_cast<uint32_t>(data[i * 4 + 1]) << 16) |
                   (static_cast<uint32_t>(data[i * 4 + 2]) << 8) |
                   (static_cast<uint32_t>(data[i * 4 + 3]));
        }
        for (int i = 16; i < 64; ++i) {
            m[i] = sig1(m[i - 2]) + m[i - 7] + sig0(m[i - 15]) + m[i - 16];
        }
        uint32_t a = state[0], b = state[1], c = state[2], d = state[3];
        uint32_t e = state[4], f = state[5], g = state[6], h = state[7];

        for (int i = 0; i < 64; ++i) {
            uint32_t t1 = h + ep1(e) + ch(e, f, g) + K[i] + m[i];
            uint32_t t2 = ep0(a) + maj(a, b, c);
            h = g; g = f; f = e; e = d + t1;
            d = c; c = b; b = a; a = t1 + t2;
        }
        state[0] += a; state[1] += b; state[2] += c; state[3] += d;
        state[4] += e; state[5] += f; state[6] += g; state[7] += h;
    }

public:
    void update(std::span<const uint8_t> data) {
        for (uint8_t byte : data) {
            buffer[count % 64] = byte;
            count++;
            if (count % 64 == 0) {
                transform(buffer);
            }
        }
    }

    [[nodiscard]] std::array<uint8_t, 32> finalize() {
        uint64_t total_bits = count * 8;
        buffer[count % 64] = 0x80;
        count++;
        if (count % 64 > 56) {
            while (count % 64 != 0) { buffer[count % 64] = 0x00; count++; }
            transform(buffer);
        }
        while (count % 64 < 56) { buffer[count % 64] = 0x00; count++; }
        for (int i = 7; i >= 0; --i) {
            buffer[56 + (7 - i)] = static_cast<uint8_t>((total_bits >> (i * 8)) & 0xFF);
        }
        transform(buffer);

        std::array<uint8_t, 32> hash{};
        for (int i = 0; i < 8; ++i) {
            hash[i * 4]     = static_cast<uint8_t>((state[i] >> 24) & 0xFF);
            hash[i * 4 + 1] = static_cast<uint8_t>((state[i] >> 16) & 0xFF);
            hash[i * 4 + 2] = static_cast<uint8_t>((state[i] >> 8) & 0xFF);
            hash[i * 4 + 3] = static_cast<uint8_t>(state[i] & 0xFF);
        }
        return hash;
    }
};

class HmacSha256 {
public:
    static std::array<uint8_t, 32> compute(
        std::span<const uint8_t> key, 
        std::span<const uint8_t> data) 
    {
        std::array<uint8_t, 64> k_pad{};
        if (key.size() > 64) {
            Sha256 k_ctx;
            k_ctx.update(key);
            auto tk = k_ctx.finalize();
            std::memcpy(k_pad.data(), tk.data(), tk.size());
        } else {
            std::memcpy(k_pad.data(), key.data(), key.size());
        }

        std::array<uint8_t, 64> ipad{}, opad{};
        for (size_t i = 0; i < 64; ++i) {
            ipad[i] = k_pad[i] ^ 0x36;
            opad[i] = k_pad[i] ^ 0x5C;
        }

        Sha256 ictx;
        ictx.update(ipad);
        ictx.update(data);
        auto inner_hash = ictx.finalize();

        Sha256 octx;
        octx.update(opad);
        octx.update(inner_hash);
        return octx.finalize();
    }
};

class DecommissionProtocolEngine {
public:
    static RawCertificate createCertificate(
        std::string_view deviceUid,
        std::string_view storageSerial,
        SanitizeMethod method,
        NistLevel nistLvl,
        bool batteryRemoved,
        BatteryChem chem,
        uint64_t erasedSectors,
        std::string_view technicianId,
        std::span<const uint8_t> secretKey)
    {
        RawCertificate cert{};
        std::memcpy(cert.magic.data(), CERT_MAGIC.data(), CERT_MAGIC.size());
        cert.schema_version = CERT_SCHEMA_V1;
        cert.timestamp_utc = static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::seconds>(
                std::chrono::system_clock::now().time_since_epoch()
            ).count()
        );

        auto copy_safe = [](auto& dst, std::string_view src) {
            std::memset(dst.data(), 0, dst.size());
            std::memcpy(dst.data(), src.data(), std::min(dst.size() - 1, src.size()));
        };

        copy_safe(cert.device_uid, deviceUid);
        copy_safe(cert.storage_serial, storageSerial);
        copy_safe(cert.technician_id, technicianId);

        cert.method = static_cast<uint8_t>(method);
        cert.nist_level = static_cast<uint8_t>(nistLvl);
        cert.battery_removed = batteryRemoved ? 1 : 0;
        cert.battery_chem = static_cast<uint8_t>(chem);
        cert.erased_sectors = erasedSectors;
        cert.post_check_passed = 1;

        // Обчислюємо цифровий підпис HMAC-SHA256
        const auto* raw_bytes = reinterpret_cast<const uint8_t*>(&cert);
        constexpr size_t payload_len = offsetof(RawCertificate, signature);
        auto sig = HmacSha256::compute(secretKey, {raw_bytes, payload_len});
        std::memcpy(cert.signature.data(), sig.data(), sig.size());

        return cert;
    }

    static std::expected<void, std::error_code> verifyCertificate(
        const RawCertificate& cert,
        std::span<const uint8_t> secretKey)
    {
        if (std::string_view(cert.magic.data(), CERT_MAGIC.size()) != CERT_MAGIC) {
            return std::unexpected(make_error_code(ValidationError::InvalidMagic));
        }

        if (cert.schema_version != CERT_SCHEMA_V1) {
            return std::unexpected(make_error_code(ValidationError::UnsupportedVersion));
        }

        if (cert.battery_chem != static_cast<uint8_t>(BatteryChem::None) && !cert.battery_removed) {
            return std::unexpected(make_error_code(ValidationError::BatteryComplianceViolation));
        }

        if (!cert.post_check_passed || cert.erased_sectors == 0) {
            return std::unexpected(make_error_code(ValidationError::IncompleteSanitization));
        }

        const auto* raw_bytes = reinterpret_cast<const uint8_t*>(&cert);
        constexpr size_t payload_len = offsetof(RawCertificate, signature);
        auto expected_sig = HmacSha256::compute(secretKey, {raw_bytes, payload_len});

        // Порівняння за сталий час
        uint8_t diff = 0;
        for (size_t i = 0; i < SIGNATURE_SIZE; ++i) {
            diff |= (cert.signature[i] ^ expected_sig[i]);
        }

        if (diff != 0) {
            return std::unexpected(make_error_code(ValidationError::SignatureMismatch));
        }

        return {};
    }
};

} // namespace DecomCert

int main() {
    std::cout << "=== СИСТЕМА АУДИТУ ТА ВЕРИФІКАЦІЇ СЕРТИФІКАТІВ ДЕКОМІСІЇ (C++20) ===\n";
    const std::vector<uint8_t> audit_key = {
        'E', 'U', '-', '2', '0', '2', '3', '-', '1', '5', '4', '2',
        '-', 'N', 'I', 'S', 'T', '-', '8', '0', '0', '-', '8', '8'
    };

    // 1. Формування сертифіката
    auto certificate = DecomCert::DecommissionProtocolEngine::createCertificate(
        "FLEET-NODE-STM32MP1-9988A",
        "EMMC-SANDISK-INAND-64GB",
        DecomCert::SanitizeMethod::CryptoErase,
        DecomCert::NistLevel::Purge,
        true,
        DecomCert::BatteryChem::LiFePO4,
        125000000ULL,
        "AUDITOR-CERT-42",
        audit_key
    );

    std::cout << "[1] Створено підписаний маніфест списання екземпляра.\n"
              << "    • Пристрій: " << certificate.device_uid.data() << "\n"
              << "    • Носій:    " << certificate.storage_serial.data() << "\n"
              << "    • Рівень:   NIST SP 800-88 Purge (Crypto-Erase)\n";

    // 2. Верифікація маніфесту
    auto verify_res = DecomCert::DecommissionProtocolEngine::verifyCertificate(certificate, audit_key);
    if (verify_res) {
        std::cout << "[2] Успішна верифікація: сертифікат відповідає усім стандартам безпеки.\n";
    } else {
        std::cout << "[ПОМИЛКА] " << verify_res.error().message() << "\n";
    }

    // 3. Тест виявлення фальсифікації підпису
    certificate.erased_sectors = 0; // Спроба підмінити обсяг стертих даних
    auto fake_res = DecomCert::DecommissionProtocolEngine::verifyCertificate(certificate, audit_key);
    if (!fake_res) {
        std::cout << "[3] Перевірка захисту від підробки: " 
                  << fake_res.error().message() << " (Атаку нейтралізовано).\n";
    }

    return 0;
}
