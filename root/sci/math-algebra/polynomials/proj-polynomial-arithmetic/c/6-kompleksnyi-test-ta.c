int main(void) {
    // 1. Тест множення: A(x) = 2x + 3, B(x) = x^2 - 4x + 5
    // Очікуваний добуток: C(x) = 2x^3 - 5x^2 - 2x + 15
    Polynomial a = poly_create(1);
    a.coeffs[0] = 3.0;
    a.coeffs[1] = 2.0;

    Polynomial b = poly_create(2);
    b.coeffs[0] = 5.0;
    b.coeffs[1] = -4.0;
    b.coeffs[2] = 1.0;

    Polynomial c = poly_multiply(&a, &b);
    printf("Тест множення C(x): ");
    for (size_t i = 0; i <= c.degree; ++i) {
        printf("%+.1f*x^%zu ", c.coeffs[i], i);
    }
    printf("\n");

    // 2. Тест Горнера: C(2.0) = 2*(8) - 5*(4) - 2*(2) + 15 = 16 - 20 - 4 + 15 = 7.0
    double val = polynomial_eval_horner(c.coeffs, c.degree, 2.0);
    printf("Схема Горнера C(2.0) = %.2f (очікується 7.00)\n", val);

    // 3. Тест ділення: C(x) / A(x) має дати частку B(x) та остачу 0
    DivisionResult div = poly_divide(&c, &a);
    printf("Тест ділення C(x) / A(x) -> частка Q: ");
    for (size_t i = 0; i <= div.quotient.degree; ++i) {
        printf("%+.1f*x^%zu ", div.quotient.coeffs[i], i);
    }
    printf(", остача R: %.2f\n", div.remainder.coeffs[0]);

    // 4. Тест кривої Безьє
    Point2D ctrl[4] = {{0.0, 0.0}, {0.0, 1.0}, {1.0, 1.0}, {1.0, 0.0}};
    Point2D pt = bezier_cubic_eval(ctrl, 0.5);
    printf("Крива Безьє при t=0.5: (x=%.3f, y=%.3f) [очікується (0.500, 0.750)]\n", pt.x, pt.y);

    poly_free(&a);
    poly_free(&b);
    poly_free(&c);
    poly_free(&div.quotient);
    poly_free(&div.remainder);
    return 0;
}
