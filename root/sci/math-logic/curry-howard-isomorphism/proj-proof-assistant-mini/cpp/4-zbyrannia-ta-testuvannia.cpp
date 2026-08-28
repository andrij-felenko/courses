int main() {
    Type A = BaseType{"A"};
    
    // Терм: λx:A. x
    Term id = std::make_shared<AbsTerm>(AbsTerm{
        "x", A, VarTerm{"x"}
    });

    try {
        Context emptyCtx;
        Type t = typeCheck(id, emptyCtx);
        std::cout << "Доведення коректне! Доведена теорема: ";
        printType(t); // Виведе (A -> A)
        std::cout << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "Помилка доведення: " << e.what() << std::endl;
    }

    return 0;
}
