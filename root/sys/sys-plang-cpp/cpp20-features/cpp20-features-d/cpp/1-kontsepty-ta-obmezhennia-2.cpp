template<typename T>
concept PrintableContainer = requires(T container) {
    // 1. Проста вимога
    container.clear();

    // 2. Типова вимога
    typename T::value_type;

    // 3. Складена вимога
    { container.size() } noexcept -> std::convertible_to<std::size_t>;
    { container.begin() } -> std::input_or_output_iterator;
    { container.end() }   -> std::sentinel_for<decltype(container.begin())>;

    // 4. Вкладена вимога
    requires sizeof(typename T::value_type) <= 64;
};
