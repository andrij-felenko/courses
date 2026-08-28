#ifndef DRAT_PROOF_LOGGER_HPP
#define DRAT_PROOF_LOGGER_HPP

#include <fstream>
#include <filesystem>
#include <vector>
#include <span>

namespace drat {

class ProofLogger {
private:
    std::ofstream file_;
    bool binary_mode_{false};
    size_t added_clauses_{0};
    size_t deleted_clauses_{0};

public:
    explicit ProofLogger(const std::filesystem::path& path, bool binary_mode = false);
    ~ProofLogger();

    ProofLogger(const ProofLogger&) = delete;
    ProofLogger& operator=(const ProofLogger&) = delete;
    ProofLogger(ProofLogger&&) noexcept = default;
    ProofLogger& operator=(ProofLogger&&) noexcept = default;

    void add_clause(std::span<const int> lits);
    void delete_clause(std::span<const int> lits);
    void close();

    [[nodiscard]] size_t added_count() const noexcept { return added_clauses_; }
    [[nodiscard]] size_t deleted_count() const noexcept { return deleted_clauses_; }
};

} // namespace drat

#endif // DRAT_PROOF_LOGGER_HPP
