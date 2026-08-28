template <typename... Args>
void demo_patterns(Args... args) {
    // Патерн 1: Просте розпакування імен аргументів
    // Патерн: args
    // Результат: consume(a1, a2, a3);
    consume(args...);

    // Патерн 2: Виклик функції для кожного елемента
    // Патерн: transform(args)
    // Результат: consume(transform(a1), transform(a2), transform(a3));
    consume(transform(args)...);

    // Патерн 3: Виклик функції над усім розпакованим пакетом
    // Патерн: args
    // Результат: consume(transform(a1, a2, a3));
    consume(transform(args...));

    // Патерн 4: Взяття адреси кожного аргументу
    // Патерн: &args
    // Результат: consume(&a1, &a2, &a3);
    consume((&args)...);

    // Патерн 5: Ідеальна передача з приведенням типів
    // Патерн: std::forward<Args>(args)
    // Результат: consume(std::forward<T1>(a1), std::forward<T2>(a2), std::forward<T3>(a3));
    consume(std::forward<Args>(args)...);
}
