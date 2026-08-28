#include <iostream>
#include <string_view>

void evaluate_conditions_cpp(TriBool cond) {
    /* WHERE: пропускає лише якщо результат строго TRUE */
    const bool where_passed = cond.is_true();

    /* CHECK: відхиляє лише якщо результат строго FALSE (Unknown дозволено!) */
    const bool check_passed = !cond.is_false();

    std::string_view state_str = "UNKNOWN";
    if (cond.is_true()) state_str = "TRUE";
    else if (cond.is_false()) state_str = "FALSE";

    std::cout << "Результат 3VL: " << state_str << '\n';
    std::cout << "  Фільтр WHERE (пропуск кортежу): " << (where_passed ? "ПРИЙНЯТО" : "ВІДХИЛЕНО") << '\n';
    std::cout << "  Обмеження CHECK (валідація):   " << (check_passed ? "ДОЗВОЛЕНО" : "ПОМИЛКА") << '\n';
}
