#include <iostream>

int main() {
    std::cout << "=== Демонстрація DiophBuilder API (C++) ===\n";
    DiophantineContext ctx;

    auto x = ctx.make_var("x");
    auto y = ctx.make_var("y");
    auto z = ctx.make_var("z");

    // Використання перевантажених операторів та ґаджетів
    auto pythagoras = (x * x + y * y == z * z);
    auto divides = DiophantineGadgets::divides(ctx, x, y);

    auto system = pythagoras && divides;

    auto compiled_poly = DiophantineCompiler::compile_to_poly(ctx, system);
    auto opt_poly = DiophantineOptimizer::optimize(ctx, compiled_poly);

    if (opt_poly) {
        std::cout << "Многочлен успішно скомпільовано та оптимізовано.\n"
                  << "Вираз: " << DiophantinePrinter::to_string(ctx, opt_poly) << "\n"
                  << "Загальна кількість змінних у системі: " << ctx.variables().size() << "\n";
        for (const auto& v : ctx.variables()) {
            std::cout << "  Змінна [" << v.id << "]: " << v.name 
                      << (v.is_existential ? " (екзистенційна)" : " (вільна)") << "\n";
        }
    }

    return 0;
}
