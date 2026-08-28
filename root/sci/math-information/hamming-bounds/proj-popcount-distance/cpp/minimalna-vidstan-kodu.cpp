#include <span>
#include <limits>
// d_min малого коду: перебір усіх пар. Слова — у code.
int min_distance(std::span<const uint32_t> code) {
    int best = std::numeric_limits<int>::max();
    for (size_t i = 0; i < code.size(); i++)
        for (size_t j = i + 1; j < code.size(); j++) {  // кожну пару — один раз
            int d = hamming_distance(code[i], code[j]);
            if (d < best) best = d;
        }
    return best;                                 // менш ніж 2 слова → лишиться max
}
