#include <iostream>
#include <string_view>
#include <string>
#include <tuple>
#include <type_traits>
#include <format>
#include <sstream>

// Універсальний типізований дескриптор поля для C++
template <typename ClassType, typename MemberType>
struct FieldDescriptor {
    std::string_view name;
    MemberType ClassType::*member_ptr;

    constexpr FieldDescriptor(std::string_view n, MemberType ClassType::*ptr)
        : name(n), member_ptr(ptr) {}
};

// Допоміжний генератор для автоматичного виведення типів
template <typename ClassType, typename MemberType>
constexpr auto make_field(std::string_view name, MemberType ClassType::*ptr) {
    return FieldDescriptor<ClassType, MemberType>(name, ptr);
}

// Базовий первинний шаблон трейту рефлексії
template <typename T>
struct TypeTraits;

// Цільова структура даних
struct UserProfile {
    int id{0};
    std::string username;
    double balance{0.0};
    bool is_active{false};
};

// Спеціалізація трейту рефлексії для структури UserProfile
template <>
struct TypeTraits<UserProfile> {
    static constexpr std::string_view type_name = "UserProfile";

    static constexpr auto fields() {
        return std::make_tuple(
            make_field("id", &UserProfile::id),
            make_field("username", &UserProfile::username),
            make_field("balance", &UserProfile::balance),
            make_field("is_active", &UserProfile::is_active)
        );
    }
};

// Універсальний відвідувач полів на базі кортежу дескрипторів
template <typename T, typename Func>
constexpr void for_each_field(const T& object, Func&& visitor) {
    auto field_tuple = TypeTraits<T>::fields();
    std::apply([&](const auto&... fields) {
        (visitor(fields.name, object.*(fields.member_ptr)), ...);
    }, field_tuple);
}

// Універсальний JSON-серіалізатор без використання void* чи ручних зміщень
template <typename T>
std::string serialize_to_json(const T& object) {
    std::ostringstream ss;
    ss << "{\n  \"_type\": \"" << TypeTraits<T>::type_name << "\",\n";

    bool first = true;
    for_each_field(object, [&](std::string_view name, const auto& value) {
        if (!first) ss << ",\n";
        first = false;

        ss << "  \"" << name << "\": ";
        if constexpr (std::is_same_v<std::decay_t<decltype(value)>, std::string> ||
                      std::is_same_v<std::decay_t<decltype(value)>, std::string_view>) {
            ss << "\"" << value << "\"";
        } else if constexpr (std::is_same_v<std::decay_t<decltype(value)>, bool>) {
            ss << (value ? "true" : "false");
        } else {
            ss << value;
        }
    });

    ss << "\n}";
    return ss.str();
}

int main() {
    UserProfile user{
        .id = 1042,
        .username = "andrij_f",
        .balance = 250.75,
        .is_active = true
    };

    std::string json = serialize_to_json(user);
    std::cout << json << '\n';

    return 0;
}
