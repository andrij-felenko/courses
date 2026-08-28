// 1. Загальний концепт викликабельного об'єкта
template<typename F, typename... Args>
concept invocable = 
    requires(F&& f, Args&&... args) {
        std::invoke(std::forward<F>(f), std::forward<Args>(args)...);
    };

// 2. Регулярний викликабельний об'єкт (детермінована функція без побічних ефектів)
template<typename F, typename... Args>
concept regular_invocable = 
    std::invocable<F, Args...>;

// 3. Булевий предикат
template<typename F, typename... Args>
concept predicate = 
    std::regular_invocable<F, Args...> &&
    requires(F&& f, Args&&... args) {
        { std::invoke(std::forward<F>(f), std::forward<Args>(args)...) } 
            -> std::convertible_to<bool>;
    };

// 4. Бінарне відношення
template<typename R, typename T, typename U>
concept relation = 
    std::predicate<R, T, T> &&
    std::predicate<R, U, U> &&
    std::predicate<R, T, U> &&
    std::predicate<R, U, T>;

// 5. Відношення еквівалентності
template<typename R, typename T, typename U>
concept equivalence_relation = 
    std::relation<R, T, U>;

// 6. Строгий слабкий порядок (Strict Weak Ordering — вимога для std::ranges::sort)
template<typename R, typename T, typename U>
concept strict_weak_order = 
    std::relation<R, T, U>;
