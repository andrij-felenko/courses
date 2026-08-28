struct UserAccount {
    std::string username;
    uint32_t    user_id{0};

    // Однорідне порівняння
    friend auto operator<=>(const UserAccount& a, const UserAccount& b) = default;

    // Гетерогенне порівняння зі string_view
    friend auto operator<=>(const UserAccount& a, std::string_view sv) noexcept {
        return a.username <=> sv;
    }
};

void lookup_example(const std::set<UserAccount, std::less<>>& db) {
    using namespace std::string_view_literals;

    // Пошук за string_view: жодного виділення пам'яті в купі!
    auto it = db.find("admin_root"sv);
}
