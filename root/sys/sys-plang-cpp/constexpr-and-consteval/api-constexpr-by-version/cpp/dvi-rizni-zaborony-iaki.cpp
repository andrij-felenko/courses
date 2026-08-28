constexpr int f(int x) {
    try { return x; } catch (...) { return 0; }   // тіло: помилка до C++20
}

constexpr int g(int x) {
    if (x < 0) throw "від'ємне";      // тіло: законне в усіх редакціях
    return x;                          // обчислення: падає лише коли x < 0
}

constexpr int a = g(5);               // 5
constexpr int b = g(-5);              // помилка: виклик не сталий
