#include <vector>
#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <memory>

namespace graph::analytics {

class ReachabilityEngine::Impl {
private:
    EngineConfig config_;
    size_t words_per_row_;
    bool is_computed_{false};
    bool is_frozen_{false};
    std::vector<uint64_t> bit_matrix_;

public:
    explicit Impl(const EngineConfig& config)
        : config_(config),
          words_per_row_((config.vertices + 63) / 64),
          bit_matrix_(config.vertices * ((config.vertices + 63) / 64), 0) {
        if (config.vertices == 0) {
            throw std::invalid_argument("Vertex count must be > 0");
        }
        if (config.auto_reflexive) {
            for (size_t i = 0; i < config.vertices; ++i) {
                const size_t word_idx = i * words_per_row_ + (i / 64);
                bit_matrix_[word_idx] |= (1ULL << (i % 64));
            }
        }
    }

    void addEdge(size_t u, size_t v) {
        if (u >= config_.vertices || v >= config_.vertices) {
            throw std::out_of_range("Vertex index out of range");
        }
        if (is_frozen_) {
            throw std::logic_error("Engine is frozen after computation");
        }
        const size_t word_idx = u * words_per_row_ + (v / 64);
        bit_matrix_[word_idx] |= (1ULL << (v % 64));
    }

    void compute() {
        const size_t v = config_.vertices;
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
        is_computed_ = true;
        is_frozen_ = true;
    }

    [[nodiscard]] bool isReachable(size_t u, size_t v) const {
        if (u >= config_.vertices || v >= config_.vertices) return false;
        if (!is_computed_) throw std::logic_error("Transitive closure not computed");
        const size_t word_idx = u * words_per_row_ + (v / 64);
        return (bit_matrix_[word_idx] & (1ULL << (v % 64))) != 0;
    }

    [[nodiscard]] std::vector<size_t> getReachableSet(size_t u) const {
        if (u >= config_.vertices) throw std::out_of_range("Vertex out of range");
        if (!is_computed_) throw std::logic_error("Transitive closure not computed");

        std::vector<size_t> result;
        const size_t wpr = words_per_row_;
        const uint64_t* row_u = &bit_matrix_[u * wpr];

        for (size_t v = 0; v < config_.vertices; ++v) {
            if ((row_u[v / 64] & (1ULL << (v % 64))) != 0) {
                result.push_back(v);
            }
        }
        return result;
    }

    [[nodiscard]] size_t vertexCount() const noexcept { return config_.vertices; }
    [[nodiscard]] bool isComputed() const noexcept { return is_computed_; }
};

ReachabilityEngine::ReachabilityEngine(const EngineConfig& config)
    : impl_(new Impl(config)) {}

ReachabilityEngine::~ReachabilityEngine() noexcept {
    delete impl_;
}

void ReachabilityEngine::addEdge(size_t u, size_t v) { impl_->addEdge(u, v); }
void ReachabilityEngine::compute() { impl_->compute(); }
bool ReachabilityEngine::isReachable(size_t u, size_t v) const { return impl_->isReachable(u, v); }
std::vector<size_t> ReachabilityEngine::getReachableSet(size_t u) const { return impl_->getReachableSet(u); }
size_t ReachabilityEngine::vertexCount() const noexcept { return impl_->vertexCount(); }
bool ReachabilityEngine::isComputed() const noexcept { return impl_->isComputed(); }

} // namespace graph::analytics
