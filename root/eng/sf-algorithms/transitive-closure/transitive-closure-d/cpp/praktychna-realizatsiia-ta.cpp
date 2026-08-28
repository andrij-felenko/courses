#include <vector>
#include <bitset>
#include <cstddef>
#include <iostream>

template <size_t N>
class TransitiveClosureBitset {
private:
    std::vector<std::bitset<N>> T_;

public:
    explicit TransitiveClosureBitset(size_t vertices) : T_(vertices) {}

    void addEdge(size_t u, size_t v) {
        T_[u].set(v);
    }

    void compute() {
        const size_t n = T_.size();
        for (size_t k = 0; k < n; ++k) {
            for (size_t i = 0; i < n; ++i) {
                if (T_[i].test(k)) {
                    T_[i] |= T_[k]; // Побітова OR-векторизація всього рядка
                }
            }
        }
    }

    [[nodiscard]] bool isReachable(size_t u, size_t v) const {
        return T_[u].test(v);
    }
};
