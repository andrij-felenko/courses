#include <cstddef>
#include <cstdint>
#include <string>

struct Summary {
    std::size_t words = 0;   // кількість слів
    std::string digest;      // геш тексту, шістнадцятковим рядком
};

// FNV-1a, 64 біти: одна з найпростіших пристойних некриптографічних геш-функцій
std::string to_hex(std::uint64_t v) {
    static const char* d = "0123456789abcdef";
    std::string out(16, '0');
    for (int i = 15; i >= 0; --i, v >>= 4) out[i] = d[v & 0xF];
    return out;
}

Summary compute_summary(const std::string& text) {
    std::uint64_t h = 0xcbf29ce484222325ull;      // FNV offset basis
    std::size_t words = 0;
    bool in_word = false;

    for (unsigned char c : text) {
        h = (h ^ c) * 0x100000001b3ull;           // FNV prime
        const bool space = (c == ' ' || c == '\n' || c == '\t' || c == '\r');
        if (space)            in_word = false;
        else if (!in_word)  { ++words; in_word = true; }
    }
    return Summary{words, to_hex(h)};
}
