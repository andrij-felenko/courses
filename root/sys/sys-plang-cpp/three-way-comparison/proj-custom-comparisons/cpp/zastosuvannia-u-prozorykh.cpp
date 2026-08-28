using namespace std::string_view_literals;

void demonstrate_zero_allocation_lookup() {
    std::set<UserRecord, std::less<>> user_directory;

    user_directory.emplace(1001, "artem_s", "Core-Engineering");
    user_directory.emplace(1002, "diana_v", "Security-Ops");
    user_directory.emplace(1003, "ivan_k", "Infrastructure");

    // Пошук за string_view: жодного виділення пам'яті в купі!
    std::string_view target_user = "diana_v"sv;
    auto it = user_directory.find(target_user);

    if (it != user_directory.end()) {
        std::cout << "Знайдено користувача ID: " << it->get_id() << "\n";
    }

    // Демонстрація симетрії C++20:
    // Вираз target_user == *it автоматично перетворюється компілятором
    // у виклик дружньої функції *it == target_user без необхідності
    // писати дзеркальне перевантаження operator==(std::string_view, const UserRecord&)!
    if (target_user == *it) {
        std::cout << "Симетрична перевірка рівності успішна.\n";
    }
}
