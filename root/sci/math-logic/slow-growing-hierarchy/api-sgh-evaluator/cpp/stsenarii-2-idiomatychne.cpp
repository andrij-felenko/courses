#include "sgh_engine.hpp"
#include <iostream>

void run_cpp_parser_example() {
    try {
        std::string expr = "w^3 * 2 + w^2 * 5 + 7";
        auto ordinal = sgh::OrdinalParser::parse(expr);

        constexpr uint64_t n = 3;
        uint64_t value = ordinal->evaluate(n);

        std::cout << "Вираз: " << ordinal->to_string() << "\n";
        std::cout << "G_alpha(" << n << ") = " << value << "\n";

        auto next_step = ordinal->fundamental_step(n);
        std::cout << "Після редукції [3]: " << next_step->to_string() << "\n";

    } catch (const sgh::ParseException& e) {
        std::cerr << "Синтаксична помилка: " << e.what() << " на позиції " << e.position() << "\n";
    } catch (const sgh::OverflowException& e) {
        std::cerr << "Арифметичне переповнення: " << e.what() << "\n";
    } catch (const std::exception& e) {
        std::cerr << "Стандартний виняток: " << e.what() << "\n";
    }
}
