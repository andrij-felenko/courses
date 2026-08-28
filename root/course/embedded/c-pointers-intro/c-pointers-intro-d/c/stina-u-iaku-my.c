void swap(int x, int y) {
    int t = x;
    x = y;
    y = t;
}

int main(void) {
    int a = 3, b = 7;
    swap(a, b);
    // a досі 3, b досі 7 — обмін НЕ спрацював!
}
