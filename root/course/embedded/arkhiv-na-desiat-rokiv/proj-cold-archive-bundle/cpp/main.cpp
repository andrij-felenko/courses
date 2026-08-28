#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <filesystem>
#include <iomanip>
#include <sstream>
#include <memory>
#include <expected>
#include <array>
#include <cstdint>

namespace fs = std::filesystem;

class Sha256Calculator {
public:
    Sha256Calculator() { reset(); }

    void reset() {
        m_state = {0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
                   0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19};
        m_count = 0;
        m_buffer.fill(0);
    }

    void update(std::span<const uint8_t> data) {
        size_t index = static_cast<size_t>(m_count & 0x3f);
        m_count += data.size();
        size_t part_len = 64 - index;
        size_t i = 0;

        if (data.size() >= part_len) {
            std::copy_n(data.data(), part_len, m_buffer.begin() + index);
            transform(m_buffer.data());
            for (i = part_len; i + 63 < data.size(); i += 64) {
                transform(data.data() + i);
            }
            index = 0;
        }
        std::copy_n(data.data() + i, data.size() - i, m_buffer.begin() + index);
    }

    [[nodiscard]] std::string finalize() {
        std::array<uint8_t, 8> bits{};
        uint64_t total_bits = m_count * 8;
        for (size_t i = 0; i < 8; ++i) {
            bits[i] = static_cast<uint8_t>(total_bits >> ((7 - i) * 8));
        }

        size_t index = static_cast<size_t>(m_count & 0x3f);
        size_t pad_len = (index < 56) ? (56 - index) : (120 - index);
        std::vector<uint8_t> padding(pad_len, 0);
        padding[0] = 0x80;

        update(padding);
        update(bits);

        std::ostringstream ss;
        ss << std::hex << std::setfill('0');
        for (uint32_t val : m_state) {
            ss << std::setw(8) << val;
        }
        return ss.str();
    }

private:
    static constexpr uint32_t ror(uint32_t x, uint32_t n) noexcept {
        return (x >> n) | (x << (32 - n));
    }
    static constexpr uint32_t ch(uint32_t x, uint32_t y, uint32_t z) noexcept {
        return (x & y) ^ (~x & z);
    }
    static constexpr uint32_t maj(uint32_t x, uint32_t y, uint32_t z) noexcept {
        return (x & y) ^ (x & z) ^ (y & z);
    }
    static constexpr uint32_t sigma0(uint32_t x) noexcept {
        return ror(x, 2) ^ ror(x, 13) ^ ror(x, 22);
    }
    static constexpr uint32_t sigma1(uint32_t x) noexcept {
        return ror(x, 6) ^ ror(x, 11) ^ ror(x, 25);
    }
    static constexpr uint32_t sig0(uint32_t x) noexcept {
        return ror(x, 7) ^ ror(x, 18) ^ (x >> 3);
    }
    static constexpr uint32_t sig1(uint32_t x) noexcept {
        return ror(x, 17) ^ ror(x, 19) ^ (x >> 10);
    }

    void transform(const uint8_t* block) {
        static constexpr std::array<uint32_t, 64> k = {
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
            0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
            0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
            0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
            0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
            0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
            0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
            0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
        };

        std::array<uint32_t, 64> w{};
        for (size_t i = 0; i < 16; ++i) {
            w[i] = (static_cast<uint32_t>(block[i * 4]) << 24) |
                   (static_cast<uint32_t>(block[i * 4 + 1]) << 16) |
                   (static_cast<uint32_t>(block[i * 4 + 2]) << 8) |
                   (static_cast<uint32_t>(block[i * 4 + 3]));
        }
        for (size_t i = 16; i < 64; ++i) {
            w[i] = sig1(w[i - 2]) + w[i - 7] + sig0(w[i - 15]) + w[i - 16];
        }

        uint32_t a = m_state[0], b = m_state[1], c = m_state[2], d = m_state[3];
        uint32_t e = m_state[4], f = m_state[5], g = m_state[6], h = m_state[7];

        for (size_t i = 0; i < 64; ++i) {
            uint32_t t1 = h + sigma1(e) + ch(e, f, g) + k[i] + w[i];
            uint32_t t2 = sigma0(a) + maj(a, b, c);
            h = g; g = f; f = e; e = d + t1;
            d = c; c = b; b = a; a = t1 + t2;
        }

        m_state[0] += a; m_state[1] += b; m_state[2] += c; m_state[3] += d;
        m_state[4] += e; m_state[5] += f; m_state[6] += g; m_state[7] += h;
    }

    std::array<uint32_t, 8> m_state{};
    uint64_t m_count{0};
    std::array<uint8_t, 64> m_buffer{};
};

enum class VerificationError {
    FileNotFound,
    ReadError,
    ChecksumMismatch
};

struct ArchiveValidator {
    static std::expected<void, VerificationError> verifyFile(
        const fs::path& basePath,
        std::string_view relPath,
        std::string_view expectedHash
    ) {
        fs::path fullPath = basePath / relPath;
        std::ifstream file(fullPath, std::ios::binary);
        if (!file) {
            std::cerr << "[ПОМИЛКА] Файл відсутній: " << fullPath << '\n';
            return std::unexpected(VerificationError::FileNotFound);
        }

        Sha256Calculator calc;
        std::vector<uint8_t> buffer(65536);

        while (file.read(reinterpret_cast<char*>(buffer.data()), buffer.size()) || file.gcount() > 0) {
            calc.update(std::span(buffer.data(), static_cast<size_t>(file.gcount())));
        }

        std::string calculated = calc.finalize();
        if (calculated != expectedHash) {
            std::cerr << "[ХЕШ НЕ ЗБІГСЯ] " << relPath
                      << "\n  Очікувано:  " << expectedHash
                      << "\n  Обчислено:  " << calculated << '\n';
            return std::unexpected(VerificationError::ChecksumMismatch);
        }

        std::cout << "[OK] " << relPath << '\n';
        return {};
    }
};
