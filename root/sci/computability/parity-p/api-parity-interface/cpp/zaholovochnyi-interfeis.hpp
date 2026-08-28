#ifndef PARITY_ORACLE_HPP
#define PARITY_ORACLE_HPP

#include <vector>
#include <cstdint>
#include <cstddef>
#include <span>
#include <memory>
#include <optional>
#include <expected>
#include <string_view>

namespace parity {

enum class Status : int32_t {
    Success          =  0,
    NullPointer      = -1,
    InvalidVariable  = -2,
    DimensionMismatch= -3,
    MemoryError      = -4,
    Timeout          = -5,
    Unsupported      = -6
};

enum class Flags : uint32_t {
    None           = 0x00,
    UseGauss       = 0x01,
    ComponentCache = 0x02,
    IsolateValiant = 0x04,
    Verbose        = 0x08
};

// ООП обгортка щільної бітової матриці над алгебраїчним полем GF(2)
class Gf2Matrix {
public:
    Gf2Matrix(size_t rows, size_t cols);
    ~Gf2Matrix() = default;

    Gf2Matrix(const Gf2Matrix&) = default;
    Gf2Matrix& operator=(const Gf2Matrix&) = default;
    Gf2Matrix(Gf2Matrix&&) noexcept = default;
    Gf2Matrix& operator=(Gf2Matrix&&) noexcept = default;

    [[nodiscard]] size_t rows() const noexcept { return rows_; }
    [[nodiscard]] size_t cols() const noexcept { return cols_; }

    void set_bit(size_t r, size_t c, bool val);
    [[nodiscard]] bool get_bit(size_t r, size_t c) const;

    // Обчислення рангу над GF(2) за поліноміальний час O(n^3)
    [[nodiscard]] size_t compute_rank() const;

private:
    size_t rows_;
    size_t cols_;
    size_t stride_;
    std::vector<uint64_t> data_;
};

// Представлення булевої формули у КНФ
class Formula {
public:
    using Literal = int32_t;
    using Clause = std::vector<Literal>;

    explicit Formula(size_t num_vars) : num_vars_(num_vars) {}

    void add_clause(std::span<const Literal> lits) {
        clauses_.emplace_back(lits.begin(), lits.end());
    }

    [[nodiscard]] size_t num_vars() const noexcept { return num_vars_; }
    [[nodiscard]] const std::vector<Clause>& clauses() const noexcept { return clauses_; }

private:
    size_t num_vars_;
    std::vector<Clause> clauses_;
};

// Обгортка оракула парності ⊕P
class ParityOracle {
public:
    explicit ParityOracle(Flags flags = Flags::None);
    ~ParityOracle();

    // Запит парності кількості розв'язків формули (повертає true = 1 / false = 0)
    [[nodiscard]] std::expected<bool, Status> query_parity(const Formula& formula) const;

    // Пакетне обчислення парності для масиву формул
    [[nodiscard]] std::expected<std::vector<bool>, Status> query_batch(
        std::span<const Formula> formulas) const;

    // Створення ізольованої формули за лемою Валіанта–Вазірані
    [[nodiscard]] static std::expected<Formula, Status> isolate_unique_solution(
        const Formula& input_formula,
        size_t num_linear_constraints,
        uint64_t seed);
};

} // namespace parity

#endif // PARITY_ORACLE_HPP
