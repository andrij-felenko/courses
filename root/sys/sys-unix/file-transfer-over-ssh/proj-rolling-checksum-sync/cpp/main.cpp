#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <unordered_map>
#include <variant>
#include <cstdint>
#include <cstring>

namespace rsync_delta {

inline constexpr uint16_t CHAR_OFFSET = 31;
inline constexpr size_t BLOCK_SIZE = 64;

// 64-бітний сильний хеш FNV-1a над масивом байтів
[[nodiscard]] constexpr uint64_t fnv1a_64(std::span<const uint8_t> data) noexcept {
    uint64_t hash = 0xcbf29ce484222325ULL;
    for (uint8_t byte : data) {
        hash ^= byte;
        hash *= 0x100000001b3ULL;
    }
    return hash;
}

// 32-бітний ковзний хеш rollsum
class RollingChecksum {
public:
    constexpr RollingChecksum() noexcept = default;

    void init(std::span<const uint8_t> data) noexcept {
        uint32_t sum_a = 0;
        uint32_t sum_b = 0;
        const size_t len = data.size();
        for (size_t i = 0; i < len; ++i) {
            const auto val = static_cast<uint32_t>(data[i]) + CHAR_OFFSET;
            sum_a += val;
            sum_b += static_cast<uint32_t>(len - i) * val;
        }
        a_ = static_cast<uint16_t>(sum_a & 0xffff);
        b_ = static_cast<uint16_t>(sum_b & 0xffff);
    }

    void rotate(uint8_t out_byte, uint8_t in_byte, size_t block_len) noexcept {
        const auto out_val = static_cast<uint32_t>(out_byte) + CHAR_OFFSET;
        const auto in_val = static_cast<uint32_t>(in_byte) + CHAR_OFFSET;

        a_ = static_cast<uint16_t>((a_ - out_val + in_val) & 0xffff);
        b_ = static_cast<uint16_t>((b_ - static_cast<uint32_t>(block_len) * out_val + a_) & 0xffff);
    }

    [[nodiscard]] uint32_t digest() const noexcept {
        return (static_cast<uint32_t>(b_) << 16) | static_cast<uint32_t>(a_);
    }

private:
    uint16_t a_{0};
    uint16_t b_{0};
};

// Токени дельта-потоку
struct MatchToken {
    uint32_t block_index;
    size_t source_offset;
};

struct LiteralToken {
    std::vector<uint8_t> bytes;
    size_t source_offset;
};

using DeltaToken = std::variant<MatchToken, LiteralToken>;

// Генератор дельти
class DeltaEngine {
public:
    struct BlockSignature {
        uint32_t block_index;
        uint64_t strong_hash;
    };

    static std::vector<DeltaToken> generate(std::span<const uint8_t> target,
                                            std::span<const uint8_t> source) {
        std::vector<DeltaToken> delta;
        std::unordered_multimap<uint32_t, BlockSignature> sig_map;

        // 1. Індексація блоків цільового файлу
        const size_t num_blocks = (target.size() + BLOCK_SIZE - 1) / BLOCK_SIZE;
        for (size_t i = 0; i < num_blocks; ++i) {
            const size_t offset = i * BLOCK_SIZE;
            const size_t b_len = std::min(BLOCK_SIZE, target.size() - offset);
            const auto block_data = target.subspan(offset, b_len);

            RollingChecksum rsum;
            rsum.init(block_data);
            const uint64_t strong = fnv1a_64(block_data);

            sig_map.emplace(rsum.digest(), BlockSignature{static_cast<uint32_t>(i), strong});
        }

        // 2. Сканування джерела ковзним вікном
        size_t src_pos = 0;
        std::vector<uint8_t> current_literals;
        size_t literal_start = 0;

        RollingChecksum window;
        bool window_valid = false;

        while (src_pos + BLOCK_SIZE <= source_len(source)) {
            if (!window_valid) {
                window.init(source.subspan(src_pos, BLOCK_SIZE));
                window_valid = true;
            } else {
                window.rotate(source[src_pos - 1], source[src_pos + BLOCK_SIZE - 1], BLOCK_SIZE);
            }

            const uint32_t rsum = window.digest();
            int matched_block = -1;

            if (auto range = sig_map.equal_range(rsum); range.first != range.second) {
                const uint64_t strong = fnv1a_64(source.subspan(src_pos, BLOCK_SIZE));
                for (auto it = range.first; it != range.second; ++it) {
                    if (it->second.strong_hash == strong) {
                        matched_block = static_cast<int>(it->second.block_index);
                        break;
                    }
                }
            }

            if (matched_block >= 0) {
                if (!current_literals.empty()) {
                    delta.emplace_back(LiteralToken{std::move(current_literals), literal_start});
                    current_literals.clear();
                }
                delta.emplace_back(MatchToken{static_cast<uint32_t>(matched_block), src_pos});
                src_pos += BLOCK_SIZE;
                window_valid = false;
                literal_start = src_pos;
            } else {
                if (current_literals.empty()) {
                    literal_start = src_pos;
                }
                current_literals.push_back(source[src_pos]);
                src_pos++;
            }
        }

        // Залишкові байти
        while (src_pos < source.size()) {
            if (current_literals.empty()) literal_start = src_pos;
            current_literals.push_back(source[src_pos++]);
        }

        if (!current_literals.empty()) {
            delta.emplace_back(LiteralToken{std::move(current_literals), literal_start});
        }

        return delta;
    }

private:
    static size_t source_len(std::span<const uint8_t> s) noexcept {
        return s.size();
    }
};

} // namespace rsync_delta

int main() {
    using namespace std::string_view_literals;

    const auto target_str = "The quick brown fox jumps over the lazy dog. "
                            "Systems programming with rsync and ssh provides "
                            "reliable data transfer for all production systems."sv;
    const auto source_str = "PREFIX_INSERTED_DATA: "
                            "The quick brown fox jumps over the lazy dog. "
                            "Systems programming with rsync and ssh provides "
                            "MODIFIED data transfer for all production systems."sv;

    const std::span<const uint8_t> target{reinterpret_cast<const uint8_t*>(target_str.data()), target_str.size()};
    const std::span<const uint8_t> source{reinterpret_cast<const uint8_t*>(source_str.data()), source_str.size()};

    const auto delta = rsync_delta::DeltaEngine::generate(target, source);

    for (const auto& token : delta) {
        std::visit([](const auto& t) {
            using T = std::decay_t<decltype(t)>;
            if constexpr (std::is_same_v<T, rsync_delta::MatchToken>) {
                std::cout << "[MATCH блок " << t.block_index << " на зміщенні " << t.source_offset << "]\n";
            } else if constexpr (std::is_same_v<T, rsync_delta::LiteralToken>) {
                std::cout << "[LITERAL " << t.bytes.size() << " байтів на зміщенні " << t.source_offset << "]\n";
            }
        }, token);
    }

    return 0;
}
