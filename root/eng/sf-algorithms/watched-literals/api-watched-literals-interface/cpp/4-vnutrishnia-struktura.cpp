// cpp
#include <vector>
#include <span>

class Clause {
    uint32_t flags_{0};
    std::vector<Literal> lits_;
public:
    explicit Clause(std::span<const Literal> lits, bool is_learned = false)
        : flags_(is_learned ? 1u : 0u), lits_(lits.begin(), lits.end()) {}
    
    [[nodiscard]] size_t size() const noexcept { return lits_.size(); }
    [[nodiscard]] bool is_learned() const noexcept { return (flags_ & 1u) != 0; }
    [[nodiscard]] Literal& operator[](size_t idx) noexcept { return lits_[idx]; }
    [[nodiscard]] const Literal& operator[](size_t idx) const noexcept { return lits_[idx]; }
};
