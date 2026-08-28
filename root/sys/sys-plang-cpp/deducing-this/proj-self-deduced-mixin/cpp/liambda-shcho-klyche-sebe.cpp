    // ── те саме main, продовження ──
    Node root{"root", {{"a", {{"a1", {}}}}, {"b", {}}}};

    auto depth = [](this auto&& self, const Node& x) -> int {
        int deepest = 0;
        for (const Node& k : x.kids) deepest = std::max(deepest, self(k));
        return deepest + 1;
    };
    std::cout << depth(root) << '\n';                       // 3

    std::string taken = Note{"чернетка", "текст"}.body();   // ✔ безпечно: переміщення
    std::cout << taken << '\n';                             // ДО смерті тимчасового Note
}
