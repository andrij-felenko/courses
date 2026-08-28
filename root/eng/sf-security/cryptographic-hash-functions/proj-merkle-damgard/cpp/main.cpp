#include <iostream>
#include <vector>
#include <array>
#include <string_view>
#include <cstdint>
#include <iomanip>
#include <bit>
#include <span>

/*
 * Ідіоматична C++20 реалізація хеш-функції Меркле — Дамґорда.
 * Використовує std::span для безпечної обробки пам'яті, std::array для фіксованих буферів,
 * та std::rotl для гарантованого циклічного зсуву.
 */
class MerkleDamgardHash {
public:
    static constexpr size_t BlockSize = 64;
    static constexpr size_t DigestSize = 16;

    MerkleDamgardHash() { reset(); }

    void reset() noexcept {
        m_state = {0x67452301U, 0xEFCDAB89U, 0x98BADCFEU, 0x10325476U};
        m_totalBits = 0;
        m_bufferLen = 0;
    }

    void update(std::span<const std::uint8_t> data) noexcept {
        m_totalBits += static_cast<std::uint64_t>(data.size()) * 8;
        for (std::uint8_t byte : data) {
            m_buffer[m_bufferLen++] = byte;
            if (m_bufferLen == BlockSize) {
                compress(m_buffer.data());
                m_bufferLen = 0;
            }
        }
    }

    void update(std::string_view str) noexcept {
        update(std::span{reinterpret_cast<const std::uint8_t*>(str.data()), str.size()});
    }

    [[nodiscard]] std::array<std::uint8_t, DigestSize> finalize() noexcept {
        m_buffer[m_bufferLen++] = 0x80;
        if (m_bufferLen > 56) {
            while (m_bufferLen < BlockSize) m_buffer[m_bufferLen++] = 0x00;
            compress(m_buffer.data());
            m_bufferLen = 0;
        }
        while (m_bufferLen < 56) m_buffer[m_bufferLen++] = 0x00;

        for (size_t i = 0; i < 8; ++i) {
            m_buffer[56 + i] = static_cast<std::uint8_t>(m_totalBits >> (i * 8));
        }
        compress(m_buffer.data());

        std::array<std::uint8_t, DigestSize> digest{};
        for (size_t i = 0; i < 4; ++i) {
            digest[i * 4 + 0] = static_cast<std::uint8_t>(m_state[i] >> 0);
            digest[i * 4 + 1] = static_cast<std::uint8_t>(m_state[i] >> 8);
            digest[i * 4 + 2] = static_cast<std::uint8_t>(m_state[i] >> 16);
            digest[i * 4 + 3] = static_cast<std::uint8_t>(m_state[i] >> 24);
        }
        return digest;
    }

    /* Можливість встановити внутрішній стан для демонстрації атаки подовження */
    void setState(const std::array<std::uint32_t, 4>& state, std::uint64_t totalBits) noexcept {
        m_state = state;
        m_totalBits = totalBits;
        m_bufferLen = 0;
    }

private:
    void compress(const std::uint8_t* block) noexcept {
        std::array<std::uint32_t, 16> w{};
        for (size_t i = 0; i < 16; ++i) {
            w[i] = static_cast<std::uint32_t>(block[i * 4 + 0]) |
                  (static_cast<std::uint32_t>(block[i * 4 + 1]) << 8) |
                  (static_cast<std::uint32_t>(block[i * 4 + 2]) << 16) |
                  (static_cast<std::uint32_t>(block[i * 4 + 3]) << 24);
        }

        auto [a, b, c, d] = m_state;
        for (size_t r = 0; r < 16; ++r) {
            std::uint32_t f = (b & c) ^ (~b & d);
            std::uint32_t temp = a + f + w[r] + 0x5A827999U;
            a = d; d = c; c = b;
            b = b + std::rotl(temp, 7);
        }
        m_state[0] += a; m_state[1] += b;
        m_state[2] += c; m_state[3] += d;
    }

    std::array<std::uint32_t, 4> m_state{};
    std::uint64_t m_totalBits{0};
    std::array<std::uint8_t, BlockSize> m_buffer{};
    size_t m_bufferLen{0};
};

/* Захищена побудова автентифікації повідомлень HMAC у C++ */
class HmacBuilder {
public:
    static std::array<std::uint8_t, MerkleDamgardHash::DigestSize>
    compute(std::span<const std::uint8_t> key, std::span<const std::uint8_t> message) {
        std::array<std::uint8_t, MerkleDamgardHash::BlockSize> kPadded{};

        if (key.size() > MerkleDamgardHash::BlockSize) {
            MerkleDamgardHash hasher;
            hasher.update(key);
            auto d = hasher.finalize();
            std::copy(d.begin(), d.end(), kPadded.begin());
        } else {
            std::copy(key.begin(), key.end(), kPadded.begin());
        }

        std::array<std::uint8_t, MerkleDamgardHash::BlockSize> ipad{}, opad{};
        for (size_t i = 0; i < MerkleDamgardHash::BlockSize; ++i) {
            ipad[i] = kPadded[i] ^ 0x36;
            opad[i] = kPadded[i] ^ 0x5C;
        }

        MerkleDamgardHash hasher;
        hasher.update(ipad);
        hasher.update(message);
        auto innerDigest = hasher.finalize();

        hasher.reset();
        hasher.update(opad);
        hasher.update(innerDigest);
        return hasher.finalize();
    }
};

int main() {
    std::string_view msg = "action=transfer&amount=100";
    MerkleDamgardHash hasher;
    hasher.update(msg);
    auto digest = hasher.finalize();

    std::cout << "Хеш вхідного повідомлення: ";
    for (auto b : digest) {
        std::cout << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(b);
    }
    std::cout << "\n";

    std::string_view key = "secret_key";
    auto hmac = HmacBuilder::compute(
        std::span{reinterpret_cast<const std::uint8_t*>(key.data()), key.size()},
        std::span{reinterpret_cast<const std::uint8_t*>(msg.data()), msg.size()}
    );

    std::cout << "HMAC захищений підпис:     ";
    for (auto b : hmac) {
        std::cout << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(b);
    }
    std::cout << "\n";

    return 0;
}
