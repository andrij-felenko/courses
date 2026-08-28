#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <cstdint>
#include <algorithm>
#include <format>

namespace db {

struct FuncDep {
    uint32_t lhs{0};
    uint32_t rhs{0};
};

enum class NormalForm {
    Violates1NF,
    Form1NF,
    Form2NF,
    Form3NF,
    FormBCNF
};

class SchemaAnalyzer {
public:
    explicit SchemaAnalyzer(std::vector<std::string> attributes)
        : m_attributes(std::move(attributes))
        , m_all_mask((1U << m_attributes.size()) - 1) {}

    void add_functional_dependency(uint32_t lhs, uint32_t rhs) {
        m_fds.push_back({lhs, rhs});
    }

    [[nodiscard]] uint32_t closure(uint32_t mask) const noexcept {
        uint32_t res = mask;
        bool changed = true;
        while (changed) {
            changed = false;
            for (const auto& [lhs, rhs] : m_fds) {
                if ((lhs & res) == lhs) {
                    const uint32_t next = res | rhs;
                    if (next != res) {
                        res = next;
                        changed = true;
                    }
                }
            }
        }
        return res;
    }

    void compute_candidate_keys() {
        m_candidate_keys.clear();
        for (uint32_t mask = 1; mask <= m_all_mask; ++mask) {
            bool superset = false;
            for (const auto key : m_candidate_keys) {
                if ((key & mask) == key) {
                    superset = true;
                    break;
                }
            }
            if (superset) continue;

            if (closure(mask) == m_all_mask) {
                m_candidate_keys.push_back(mask);
            }
        }
    }

    [[nodiscard]] const std::vector<uint32_t>& candidate_keys() const noexcept {
        return m_candidate_keys;
    }

    [[nodiscard]] std::pair<NormalForm, std::string> analyze_normal_form() const {
        uint32_t prime_mask = 0;
        for (const auto key : m_candidate_keys) {
            prime_mask |= key;
        }
        const uint32_t non_prime_mask = m_all_mask & ~prime_mask;

        // Перевірка 2NF: часткові залежності непервинних атрибутів
        for (const auto& [lhs, rhs] : m_fds) {
            const uint32_t non_prime_rhs = rhs & non_prime_mask;
            if (non_prime_rhs == 0) continue;

            for (const auto key : m_candidate_keys) {
                if ((lhs & key) == lhs && lhs != key) {
                    return {NormalForm::Form1NF, "Порушення 2NF: непервинний атрибут залежить від частини складеного ключа."};
                }
            }
        }

        // Перевірка 3NF та BCNF
        bool is_bcnf = true;
        for (const auto& [lhs, rhs] : m_fds) {
            const uint32_t non_trivial_rhs = rhs & ~lhs;
            if (non_trivial_rhs == 0) continue;

            const bool is_superkey = (closure(lhs) == m_all_mask);
            if (!is_superkey) {
                is_bcnf = false;
                if ((non_trivial_rhs & ~prime_mask) != 0) {
                    return {NormalForm::Form2NF, "Порушення 3NF: знайдено транзитивну залежність непервинного атрибута."};
                }
            }
        }

        if (is_bcnf) {
            return {NormalForm::FormBCNF, "Схема відповідає найвищій нормальній формі Бойса–Кодда (BCNF)."};
        }
        return {NormalForm::Form3NF, "Схема перебуває у 3NF (існують надлишкові детермінанти серед перекривних ключів)."};
    }

private:
    std::vector<std::string> m_attributes;
    uint32_t m_all_mask{0};
    std::vector<FuncDep> m_fds;
    std::vector<uint32_t> m_candidate_keys;
};

} // namespace db
