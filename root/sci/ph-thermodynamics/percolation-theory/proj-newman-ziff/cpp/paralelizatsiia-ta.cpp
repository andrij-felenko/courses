int atomic_find_root(std::atomic<int>* parent, int i) {
    while (true) {
        int p = parent[i].load(std::memory_order_relaxed);
        if (p < 0) return i; // Знайдено корінь

        int grand_parent = parent[p].load(std::memory_order_relaxed);
        if (grand_parent >= 0) {
            // Атомарний халвінг шляху: пробуємо перенаправити на дідуся
            parent[i].compare_exchange_weak(p, grand_parent,
                                            std::memory_order_relaxed);
        }
        i = p;
    }
}
