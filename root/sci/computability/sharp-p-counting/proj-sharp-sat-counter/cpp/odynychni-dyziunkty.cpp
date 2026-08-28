// Точний лічильник: розгалуження за змінною + додавання гілок, з поширенням
// одиничних диз'юнктів. assigned — скільки змінних уже зафіксовано.
Count countDPLL(CNF F, int n, int assigned) {
    for (bool changed = true; changed; ) {             // 1. поширення одиничних диз'юнктів
        changed = false;
        for (const Clause& c : F)
            if (c.size() == 1) {                       // клауза з одного літерала форсує його
                bool conflict = false;
                F = assign(F, c[0], conflict);
                ++assigned;                            // ця змінна тепер зафіксована
                if (conflict) return 0;                // суперечність → 0 моделей у цій гілці
                changed = true;
                break;                                 // F змінилась — переглянути заново
            }
    }
    if (F.empty())                                     // 2. база: клауз нема — решта змінних вільні
        return (Count)1 << (n - assigned);             //    2^(вільні),   n - assigned < 64

    int v = var(F[0][0]);                              // 3. розвилка за першою-ліпшою змінною
    bool cf1 = false, cf0 = false;
    CNF F1 = assign(F,  v, cf1);                        //    xᵥ = 1
    CNF F0 = assign(F, -v, cf0);                        //    xᵥ = 0
    Count s1 = cf1 ? 0 : countDPLL(std::move(F1), n, assigned + 1);
    Count s0 = cf0 ? 0 : countDPLL(std::move(F0), n, assigned + 1);
    return s1 + s0;                                     //    СКЛАДАЄМО обидві гілки
}
