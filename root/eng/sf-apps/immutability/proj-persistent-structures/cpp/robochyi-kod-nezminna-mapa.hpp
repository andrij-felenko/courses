Tree<int, const char*> v0;                       // порожня мапа (версія 0)
auto v1 = insert(v0, 5, "five");
auto v2 = insert(v1, 3, "three");
auto v3 = insert(v2, 8, "eight");
auto v4 = insert(v3, 5, "FIVE-updated");         // оновили значення ключа 5

// v3 і v4 — РІЗНІ мапи, обидві живі:
*find(v3, 5);   // "five"           — стара версія недоторкана
*find(v4, 5);   // "FIVE-updated"   — нова версія з оновленим ключем
*find(v3, 3);   // "three"          — цей вузол ФІЗИЧНО спільний між v3 і v4
