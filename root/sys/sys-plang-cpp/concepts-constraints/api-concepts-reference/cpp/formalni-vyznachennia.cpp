// 1. Переміщуваний тип: можна перемістити конструктором та оператором присвоєння
template<typename T>
concept movable = 
    std::is_object_v<T> &&
    std::move_constructible<T> &&
    std::assignable_from<T&, T> &&
    std::swappable<T>;

// 2. Копійовний тип: можна дублювати в пам'яті без руйнування оригіналу
template<typename T>
concept copyable = 
    std::copy_constructible<T> &&
    std::movable<T> &&
    std::assignable_from<T&, T&> &&
    std::assignable_from<T&, const T&> &&
    std::assignable_from<T&, const T>;

// 3. Напіврегулярний тип: копійовний тип з можливістю створення за замовчуванням
template<typename T>
concept semiregular = 
    std::copyable<T> && 
    std::default_initializable<T>;

// 4. Регулярний тип: напіврегулярний тип із математичною рівністю значень
template<typename T>
concept regular = 
    std::semiregular<T> && 
    std::equality_comparable<T>;
