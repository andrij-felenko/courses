class NamedItem {
public:
    std::string name;

    // Універсальний конструктор для ініціалізації рядком або типами, що перетворюються на string
    template<typename T>
    explicit NamedItem(T&& str) : name(std::forward<T>(str)) {}

    NamedItem(const NamedItem& other) = default;
    NamedItem(NamedItem&& other) noexcept = default;
};
