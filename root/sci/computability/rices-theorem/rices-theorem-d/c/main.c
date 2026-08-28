// Варіант A: пряме додавання
int compute_a(int x) {
    return x + x;
}

// Варіант B: цикл з акумулятором
int compute_b(int x) {
    int sum = 0;
    for (int i = 0; i < x; ++i) {
        sum += 2;
    }
    return sum;
}
