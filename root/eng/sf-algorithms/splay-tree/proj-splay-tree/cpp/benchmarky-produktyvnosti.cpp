// Тестування у сучасній системі кешування
void benchmark_zipfian_access() {
    constexpr int N = 100'000;
    constexpr int OPERATIONS = 1'000'000;
    
    SplayTree<int, int> splay;
    for (int i = 0; i < N; ++i) splay.insert(i, i * 2);

    // Доступ до гарячої робочої множини розміром 50 елементів
    for (int op = 0; op < OPERATIONS; ++op) {
        int key = (op % 10 < 8) ? (op % 50) : (rand() % N);
        splay.find(key);
    }
}
