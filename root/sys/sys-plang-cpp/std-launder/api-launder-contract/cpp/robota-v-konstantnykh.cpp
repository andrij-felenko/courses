constexpr int evaluate_at_compile_time() {
    struct Item {
        const int value;
    };

    alignas(Item) std::byte storage[sizeof(Item)];
    
    // Створення об'єкта в constexpr-контексті (C++20 через std::construct_at)
    Item* p = std::construct_at(reinterpret_cast<Item*>(storage), 42);
    
    // Отримання через launder у constexpr
    Item* clean_p = std::launder(reinterpret_cast<Item*>(storage));
    return clean_p->value;
}

static_assert(evaluate_at_compile_time() == 42);
