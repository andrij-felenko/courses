int main() {
    // 1. Тест множення: A(x) = 2x + 3, B(x) = x^2 - 4x + 5
    Polynomial a({3.0, 2.0});
    Polynomial b({5.0, -4.0, 1.0});
    Polynomial c = a * b;

    std::cout << "Тест множення C(x): ";
    for (size_t i = 0; i <= c.degree(); ++i) {
        std::cout << (c.coeffs[i] >= 0 ? "+" : "") << c.coeffs[i] << "*x^" << i << " ";
    }
    std::cout << "\n";

    // 2. Тест Горнера: C(2.0)
    double val = evaluate_horner(c.coeffs, 2.0);
    std::cout << "Схема Горнера C(2.0) = " << val << " (очікується 7.0)\n";

    // 3. Тест ділення
    auto [quotient, remainder] = divide(c, a);
    std::cout << "Тест ділення -> частка Q: ";
    for (size_t i = 0; i <= quotient.degree(); ++i) {
        std::cout << (quotient.coeffs[i] >= 0 ? "+" : "") << quotient.coeffs[i] << "*x^" << i << " ";
    }
    std::cout << ", остача R: " << remainder.coeffs.front() << "\n";

    // 4. Тест Безьє
    std::vector<Point2D> ctrl{{0.0, 0.0}, {0.0, 1.0}, {1.0, 1.0}, {1.0, 0.0}};
    Point2D pt = evaluate_bezier_de_casteljau(ctrl, 0.5);
    std::cout << "Крива Безьє при t=0.5: (x=" << pt.x << ", y=" << pt.y << ") [очікується (0.5, 0.75)]\n";

    return 0;
}
