#include <iostream>
#include <string>
#include <string_view>
#include <set>
#include <compare>

class UserRecord {
    uint64_t    id{0};
    std::string username;
    std::string department;

public:
    UserRecord(uint64_t uid, std::string name, std::string dept)
        : id(uid), username(std::move(name)), department(std::move(dept)) {}

    uint64_t get_id() const noexcept { return id; }
    std::string_view get_username() const noexcept { return username; }

    // 1. Однорідне порівняння двох повноцінних об'єктів UserRecord
    friend auto operator<=>(const UserRecord& a, const UserRecord& b) noexcept {
        return a.username <=> b.username;
    }
    friend bool operator==(const UserRecord& a, const UserRecord& b) noexcept {
        return a.username == b.username;
    }

    // 2. Гетерогенне порівняння з невласницьким видом std::string_view
    friend auto operator<=>(const UserRecord& a, std::string_view sv) noexcept {
        return a.username <=> sv;
    }
    friend bool operator==(const UserRecord& a, std::string_view sv) noexcept {
        return a.username == sv;
    }

    // 3. Гетерогенне порівняння з числовим первинним ключем ID
    friend auto operator<=>(const UserRecord& a, uint64_t target_id) noexcept {
        return a.id <=> target_id;
    }
    friend bool operator==(const UserRecord& a, uint64_t target_id) noexcept {
        return a.id == target_id;
    }
};
