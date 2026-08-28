template <typename... Args>
auto safe_sum(Args... args) {
    return (0 + ... + args); // Для порожнього пакета повертає точно 0
}

template <typename... Strings>
std::string concatenate(Strings&&... strs) {
    return (std::string{} + ... + std::forward<Strings>(strs));
    // Для 0 аргументів повертає порожній об'єкт std::string{}
}
