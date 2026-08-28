int add(int a, int b);   // прототип: анонс наперед, тіла ще нема

int main() {
    int s = add(2, 3);   // тепер компілятор спокійний: він знає add
    return s;
}

int add(int a, int b) {  // а ось і саме тіло, нижче
    return a + b;
}
