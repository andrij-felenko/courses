namespace user_data {
    struct Account {
        int id;
        std::string email;
    };
}

// Спеціалізація шаблону у просторі std
namespace std {
    template<>
    struct hash<user_data::Account> {
        std::size_t operator()(const user_data::Account& acc) const noexcept {
            return std::hash<int>{}(acc.id);
        }
    };
}
