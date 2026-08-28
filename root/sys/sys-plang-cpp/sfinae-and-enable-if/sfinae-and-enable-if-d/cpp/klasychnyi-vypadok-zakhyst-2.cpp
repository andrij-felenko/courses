class NamedItem {
public:
    std::string name;

    template<typename T,
             std::enable_if_t<!std::is_same_v<std::decay_t<T>, NamedItem>, int> = 0>
    explicit NamedItem(T&& str) : name(std::forward<T>(str)) {}

    NamedItem(const NamedItem& other) = default;
    NamedItem(NamedItem&& other) noexcept = default;
};
