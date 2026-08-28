int main() {
    int n = 7; // Множина A = {0, 1, 2, 3, 4, 5, 6}
    EquivalencePartitioner dsu(n);

    // Додаємо відношення еквівалентності
    dsu.add_relation(0, 1);
    dsu.add_relation(1, 2); // Транзитивність: тепер 0, 1, 2 в одному класі
    
    dsu.add_relation(4, 5);
    dsu.add_relation(5, 6); // 4, 5, 6 в іншому класі
    // Елемент 3 залишається ізольованим.

    // Формуємо [Фактор-множини](root:math-logic/quotient-sets)у (класи еквівалентності)
    std::map<int, std::vector<int>> quotient_set;
    for (int i = 0; i < n; i++) {
        int rep = dsu.find_representative(i);
        quotient_set[rep].push_back(i);
    }

    // Вивід результатів
    std::cout << "[Фактор-множини](root:math-logic/quotient-sets)а A/R (класи еквівалентності):\n";
    for (const auto& pair : quotient_set) {
        std::cout << "[Представник " << pair.first << "] : { ";
        for (int val : pair.second) {
            std::cout << val << " ";
        }
        std::cout << "}\n";
    }

    return 0;
}
