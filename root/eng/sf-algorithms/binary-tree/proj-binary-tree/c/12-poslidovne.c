// Перетворення відсортованого масиву у розклад Ейтцингера на C
void eytzinger_helper(const int* sorted, int* eytzinger, int n, int k, int* idx) {
    if (k > n) return;
    eytzinger_helper(sorted, eytzinger, n, 2 * k, idx);
    eytzinger[k] = sorted[(*idx)++];
    eytzinger_helper(sorted, eytzinger, n, 2 * k + 1, idx);
}

void build_eytzinger(const int* sorted, int* eytzinger, int n) {
    int idx = 0;
    eytzinger_helper(sorted, eytzinger, n, 1, &idx);
}
