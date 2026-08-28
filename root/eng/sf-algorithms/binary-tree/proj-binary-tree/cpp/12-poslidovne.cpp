// Двійковий пошук за розкладом Ейтцингера у C++ з префетчингом кешу
int eytzinger_search(const std::vector<int>& eytzinger, int target) {
    int k = 1;
    int n = (int)eytzinger.size() - 1;

    while (k <= n) {
        // Завантажуємо потенційні лінії кешу для дітей на крок уперед
        __builtin_prefetch(&eytzinger[2 * k]);
        __builtin_prefetch(&eytzinger[2 * k + 1]);

        if (eytzinger[k] >= target) {
            k = 2 * k;       // Перехід у ліве піддерево
        } else {
            k = 2 * k + 1;   // Перехід у праве піддерево
        }
    }
    return k >> __builtin_ffs(~k);
}
