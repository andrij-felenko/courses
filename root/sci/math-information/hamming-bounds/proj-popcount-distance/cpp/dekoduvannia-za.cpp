#include <span>
#include <limits>
// Повертає {індекс найближчого слова, його відстань}.
std::pair<int, int> decode_nearest(std::span<const uint32_t> code, uint32_t got) {
    int best_i = 0, best_d = std::numeric_limits<int>::max();
    for (size_t i = 0; i < code.size(); i++) {
        int d = hamming_distance(got, code[i]);
        if (d < best_d) { best_d = d; best_i = i; }   // ближчий — запам'ятати
    }
    return {best_i, best_d};
}
