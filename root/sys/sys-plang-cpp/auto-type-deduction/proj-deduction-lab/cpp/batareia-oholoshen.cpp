void battery() {
    // ── 1. Константний об'єкт ────────────────────────────────
    const int ci = 42;
    auto        a1 = ci;   SHOW(a1);
    const auto  a2 = ci;   SHOW(a2);
    auto&       a3 = ci;   SHOW(a3);
    const auto& a4 = ci;   SHOW(a4);
    auto&&      a5 = ci;   SHOW(a5);

    // ── 2. Масив ─────────────────────────────────────────────
    int arr[5] = {};
    auto        b1 = arr;  SHOW(b1);
    const auto  b2 = arr;  SHOW(b2);
    auto&       b3 = arr;  SHOW(b3);
    const auto& b4 = arr;  SHOW(b4);
    auto&&      b5 = arr;  SHOW(b5);

    // ── 3. Посередник із vector<bool> ────────────────────────
    std::vector<bool> vb{true, false, true};
    auto        c1 = vb[0];  SHOW(c1);
    const auto  c2 = vb[0];  SHOW(c2);
 // auto&       c3 = vb[0];              // не компілюється, див. нижче
    const auto& c4 = vb[0];  SHOW(c4);
    auto&&      c5 = vb[0];  SHOW(c5);
    auto        c6 = static_cast<bool>(vb[0]);  SHOW(c6);
}
