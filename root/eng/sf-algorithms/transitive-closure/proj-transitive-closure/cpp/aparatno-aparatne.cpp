#include <vector>
#include <cstdint>
#include <cstddef>
#include <stdexcept>

class BitsetTransitiveClosure {
private:
    size_t vertices_;
    size_t words_per_row_;
    std::vector<uint64_t> bit_matrix_;

public:
    explicit BitsetTransitiveClosure(size_t vertices)
        : vertices_(vertices),
          words_per_row_((vertices + 63) / 64),
          bit_matrix_(vertices * ((vertices + 63) / 64), 0) {
        if (vertices == 0) {
            throw std::invalid_argument("Graph must contain at least 1 vertex");
        }
    }

    void addEdge(size_t u, size_t v) {
        if (u >= vertices_ || v >= vertices_) {
            throw std::out_of_range("Vertex index out of graph bounds");
        }
        const size_t word_idx = u * words_per_row_ + (v / 64);
        bit_matrix_[word_idx] |= (1ULL << (v % 64));
    }

    void compute() {
        const size_t v = vertices_;
        const size_t wpr = words_per_row_;
        uint64_t* m = bit_matrix_.data();

        for (size_t k = 0; k < v; ++k) {
            const size_t k_word = k / 64;
            const uint64_t k_mask = (1ULL << (k % 64));

            for (size_t i = 0; i < v; ++i) {
                if ((m[i * wpr + k_word] & k_mask) != 0) {
                    uint64_t* row_i = &m[i * wpr];
                    const uint64_t* row_k = &m[k * wpr];
                    for (size_t w = 0; w < wpr; ++w) {
                        row_i[w] |= row_k[w];
                    }
                }
            }
        }
    }

    [[nodiscard]] bool isReachable(size_t u, size_t v) const {
        if (u >= vertices_ || v >= vertices_) return false;
        const size_t word_idx = u * words_per_row_ + (v / 64);
        return (bit_matrix_[word_idx] & (1ULL << (v % 64))) != 0;
    }
};
