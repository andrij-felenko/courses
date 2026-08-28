// ✓ КОРЕКТНИЙ ПОРЯДОК: Спеціалізовані обробники попереду
try {
    std::vector<int> v;
    v.at(10);
} catch (const std::out_of_range& e) {
    // Обробка конкретно виходу за межі діапазону
} catch (const std::runtime_error& e) {
    // Обробка помилок виконання
} catch (const std::exception& e) {
    // Базовий обробник для всіх інших стандартних винятків
}
