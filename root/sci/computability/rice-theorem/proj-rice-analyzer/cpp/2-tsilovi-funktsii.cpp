#include <iostream>
#include <functional>
#include <string>

// Функція, яка ОЧЕВИДНО має властивість P
int function_has_P(int x) {
    return 42;
}

// Функція, яка ОЧЕВИДНО не має властивості P
int function_not_P(int x) {
    return x + 1;
}

// Функція з прихованою семантикою (Гіпотеза Коллатца)
// Чи зупиниться вона? Якщо зупиниться, поверне 42. Якщо ні - зависне.
int function_collatz_like(int x) {
    int n = x > 0 ? x : 27; // Використовуємо 27 як число з довгою траєкторією
    while (n > 1) {
        if (n % 2 == 0) n = n / 2;
        else n = 3 * n + 1;
    }
    return 42;
}
