// Оголошення переліку статусів
enum class AccessLevel {
    Guest,
    User,
    Admin,
    Superuser
};

// Вкладена структура географічних координат
struct GeoLocation {
    double latitude;
    double longitude;
};

// Головна сутність профілю користувача
struct UserAccount {
    int id;
    std::string username;
    bool is_active;
    AccessLevel role;
    GeoLocation location;
    std::vector<std::string> tags;
};

auto main() -> int {
    // 1. Створення та ініціалізація об'єкта
    UserAccount account{
        .id = 1042,
        .username = "developer_alex",
        .is_active = true,
        .role = AccessLevel::Admin,
        .location = {
            .latitude = 50.4501,
            .longitude = 30.5234
        },
        .tags = {"cpp26", "reflection", "performance"}
    };

    // 2. Автоматична серіалізація в JSON без жодного макросу
    std::string json_payload = to_json(account);
    std::cout << "Згенерований JSON:\n" << json_payload << "\n\n";

    // 3. Зворотна десеріалізація з JSON у новий об'єкт
    UserAccount restored_account = from_json<UserAccount>(json_payload);

    std::cout << "Відновлений об'єкт:\n";
    std::cout << "ID: " << restored_account.id << "\n";
    std::cout << "Username: " << restored_account.username << "\n";
    std::cout << "Active: " << (restored_account.is_active ? "yes" : "no") << "\n";
    std::cout << "Role: " << enum_to_string(restored_account.role) << "\n";
    std::cout << "Latitude: " << restored_account.location.latitude << "\n";
    std::cout << "Longitude: " << restored_account.location.longitude << "\n";

    return 0;
}
