int g(int a, int b) {
    int sum = a + b;        // 'sum' — локальна: живе в кадрі g
    return sum;             // повернення: pop кадру g, адреса → PC
}

int f(int x) {
    int bias = 100;         // 'bias' — локальна: живе в кадрі f
    return g(x, bias);      // виклик g: push кадру g поверх кадру f
}

int main(void) {
    int r = f(7);           // виклик f: push кадру f поверх кадру main
    return r;               // r == 107
}
