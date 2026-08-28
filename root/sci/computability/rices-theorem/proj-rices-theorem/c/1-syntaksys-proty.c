// func_trivial: очевидне ділення на нуль у синтаксисі коду
int func_trivial(int x) {
    int y = 0;
    return x / y; // Синтаксично видно: ділення на нульовий літерал
}

// func_semantic: ділення на нуль залежить від динамічної траєкторії
int collatz_step(int n) {
    while (n > 1) {
        if (n % 2 == 0) n = n / 2;
        else n = 3 * n + 1;
    }
    return 0; // Повертає 0, якщо послідовність Коллатца досягає 1
}

int func_semantic(int x, int start_n) {
    int denom = collatz_step(start_n);
    return x / denom; // Ділення на нуль відбудеться ⟺ collatz_step зупиниться
}
