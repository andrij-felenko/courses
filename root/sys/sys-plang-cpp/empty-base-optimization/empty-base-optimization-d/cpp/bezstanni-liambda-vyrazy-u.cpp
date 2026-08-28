// Оголошуємо унікальний тип лямбди без збереження екземпляра
auto custom_deleter = [](int* p) noexcept {
    std::cout << "Вилучення ресурсу\n";
    delete p;
};

template <typename T, typename Callback>
struct EventListener {
    T* target;
    [[no_unique_address]] Callback on_event;
};

// Екземпляр структури зі stateless-функтором:
EventListener<int, decltype(custom_deleter)> listener{nullptr, {}};
static_assert(sizeof(listener) == sizeof(int*)); // Рівно 8 байтів!
