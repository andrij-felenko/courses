#include <iostream>
#include <array>
#include "parity_oracle.hpp"

int main() {
    using namespace parity;

    // Створення оракула з використанням прискорення Гаусса
    ParityOracle oracle(Flags::UseGauss | Flags::ComponentCache);

    Formula formula(3);
    formula.add_clause(std::array<int32_t, 2>{1, 2});
    formula.add_clause(std::array<int32_t, 2>{-1, 3});

    auto parity_result = oracle.query_parity(formula);
    if (parity_result.has_value()) {
        std::cout << "⊕P Oracle parity output: " << (*parity_result ? "1 (ODD)" : "0 (EVEN)") << '\n';
    } else {
        std::cerr << "Oracle query failed with error: "
                  << static_cast<int32_t>(parity_result.error()) << '\n';
    }

    // Обчислення рангу матриці над GF(2)
    Gf2Matrix mat(2, 2);
    mat.set_bit(0, 0, true);
    mat.set_bit(0, 1, true);
    mat.set_bit(1, 0, false);
    mat.set_bit(1, 1, true);

    size_t rank = mat.compute_rank();
    std::cout << "Matrix rank over GF(2): " << rank << '\n';

    return 0;
}
