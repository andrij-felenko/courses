#include "sgh_engine.hpp"
#include <iostream>

void run_cpp_example() {
    auto sum = std::make_unique<sgh::SumNode>();
    sum->add_term(std::make_unique<sgh::OmegaTermNode>(std::make_unique<sgh::ConstantNode>(2), 3));
    sum->add_term(std::make_unique<sgh::OmegaTermNode>(std::make_unique<sgh::ConstantNode>(1), 4));
    sum->add_term(std::make_unique<sgh::ConstantNode>(5));

    constexpr uint64_t n = 4;
    const uint64_t result = sum->evaluate(n);
    std::cout << "G_alpha(" << n << ") = " << result << "\n";
}
