#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <string_view>
#include <optional>
#include <cstring>
#include <utility>

class CountingBloomFilter {
public:
    static constexpr uint8_t MaxCounter = 15;

    CountingBloomFilter(size_t capacity, uint32_t numHashes)
        : m_capacity(capacity)
        , m_numHashes(numHashes)
        , m_storage((capacity + 1) / 2, 0)
        , m_count(0)
    {
    }

    /* Додавання ключа (Insert) */
    void insert(std::string_view key) noexcept {
        auto [h1, h2] = computeHashes(key);

        for (uint32_t i = 0; i < m_numHashes; ++i) {
            size_t idx = (h1 + static_cast<size_t>(i) * h2) % m_capacity;
            uint8_t cur = getCounter(idx);
            if (cur < MaxCounter) {
                setCounter(idx, cur + 1);
            }
        }
        ++m_count;
    }

    /* Перевірка наявності (Lookup / Contains) */
    [[nodiscard]] bool contains(std::string_view key) const noexcept {
        auto [h1, h2] = computeHashes(key);

        for (uint32_t i = 0; i < m_numHashes; ++i) {
            size_t idx = (h1 + static_cast<size_t>(i) * h2) % m_capacity;
            if (getCounter(idx) == 0) {
                return false; /* Гарантовано відсутній */
            }
        }
        return true; /* Можливо присутній */
    }

    /* Безпечне видалення (Remove) */
    bool remove(std::string_view key) noexcept {
        if (!contains(key)) {
            return false;
        }

        auto [h1, h2] = computeHashes(key);

        for (uint32_t i = 0; i < m_numHashes; ++i) {
            size_t idx = (h1 + static_cast<size_t>(i) * h2) % m_capacity;
            uint8_t cur = getCounter(idx);
            /* Насичений лічильник не зменшується */
            if (cur > 0 && cur < MaxCounter) {
                setCounter(idx, cur - 1);
            }
        }

        if (m_count > 0) {
            --m_count;
        }
        return true;
    }

    [[nodiscard]] uint8_t getCounter(size_t index) const noexcept {
        size_t byteIdx = index >> 1;
        if ((index & 1) == 0) {
            return m_storage[byteIdx] & 0x0F;
        } else {
            return (m_storage[byteIdx] >> 4) & 0x0F;
        }
    }

    [[nodiscard]] bool isSaturated(size_t index) const noexcept {
        return getCounter(index) == MaxCounter;
    }

    [[nodiscard]] size_t capacity() const noexcept { return m_capacity; }
    [[nodiscard]] size_t size() const noexcept { return m_count; }
    [[nodiscard]] size_t byteSize() const noexcept { return m_storage.size(); }

private:
    size_t m_capacity;
    uint32_t m_numHashes;
    std::vector<uint8_t> m_storage;
    size_t m_count;

    void setCounter(size_t index, uint8_t val) noexcept {
        size_t byteIdx = index >> 1;
        val &= 0x0F;
        if ((index & 1) == 0) {
            m_storage[byteIdx] = (m_storage[byteIdx] & 0xF0) | val;
        } else {
            m_storage[byteIdx] = (m_storage[byteIdx] & 0x0F) | (val << 4);
        }
    }

    static uint32_t murmurhash3(std::string_view key, uint32_t seed) noexcept {
        const auto* data = reinterpret_cast<const uint8_t*>(key.data());
        size_t len = key.size();
        const int nblocks = static_cast<int>(len / 4);
        uint32_t h1 = seed;
        constexpr uint32_t c1 = 0xcc9e2d51;
        constexpr uint32_t c2 = 0x1b873593;

        for (int i = 0; i < nblocks; ++i) {
            uint32_t k1;
            std::memcpy(&k1, data + i * 4, sizeof(uint32_t));

            k1 *= c1;
            k1 = (k1 << 15) | (k1 >> 17);
            k1 *= c2;

            h1 ^= k1;
            h1 = (h1 << 13) | (h1 >> 19);
            h1 = h1 * 5 + 0xe6546b64;
        }

        const uint8_t* tail = data + nblocks * 4;
        uint32_t k1 = 0;
        switch (len & 3) {
            case 3: k1 ^= static_cast<uint32_t>(tail[2]) << 16; [[fallthrough]];
            case 2: k1 ^= static_cast<uint32_t>(tail[1]) << 8;  [[fallthrough]];
            case 1: k1 ^= static_cast<uint32_t>(tail[0]);
                    k1 *= c1;
                    k1 = (k1 << 15) | (k1 >> 17);
                    k1 *= c2;
                    h1 ^= k1;
                    break;
        }

        h1 ^= static_cast<uint32_t>(len);
        h1 ^= h1 >> 16;
        h1 *= 0x85ebca6b;
        h1 ^= h1 >> 13;
        h1 *= 0xc2b2ae35;
        h1 ^= h1 >> 16;

        return h1;
    }

    [[nodiscard]] std::pair<uint32_t, uint32_t> computeHashes(std::string_view key) const noexcept {
        uint32_t h1 = murmurhash3(key, 0x9747b28c);
        uint32_t h2 = murmurhash3(key, 0xee6b27eb);
        if (h2 == 0) h2 = 1;
        return {h1, h2};
    }
};
