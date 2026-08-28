template <typename T>
T find_max(T a, T b) {
    return (a < b) ? b : a;
}

void demo_functions() {
    auto x = find_max(10, 20);         // Неявне виведення: T = int
    auto y = find_max(3.14, 2.71);     // Неявне виведення: T = double
    
    // auto z = find_max(10, 3.14);    // Помилка! Неоднозначність: T = int чи double?
    auto z = find_max<double>(10, 3.14); // Явна передача: аргумент 10 неявно приводиться до double
}
