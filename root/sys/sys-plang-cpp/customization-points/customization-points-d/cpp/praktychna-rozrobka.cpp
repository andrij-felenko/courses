#include <iostream>
#include <string>
#include <vector>
#include <concepts>
#include <utility>

namespace json_lib {
    namespace __to_json_detail {
        // Отруєний контекст
        void to_json() = delete;

        template<typename T>
        concept has_member_to_json = requires(const T& t) {
            t.to_json();
        };

        template<typename T>
        concept has_adl_to_json = !has_member_to_json<T> && requires(const T& t) {
            to_json(t);
        };

        struct __to_json_fn {
            // Гілка 1: Метод-член
            template<has_member_to_json T>
            constexpr std::string operator()(const T& t) const {
                return t.to_json();
            }

            // Гілка 2: ADL у отруєному контексті
            template<has_adl_to_json T>
            constexpr std::string operator()(const T& t) const {
                return to_json(t);
            }

            // Гілка 3: Фолбек для числово-текстових типів
            template<typename T>
                requires (!has_member_to_json<T> && !has_adl_to_json<T> && std::integral<T>)
            constexpr std::string operator()(const T& t) const {
                return std::to_string(t);
            }

            template<typename T>
                requires (!has_member_to_json<T> && !has_adl_to_json<T> && std::same_as<T, std::string>)
            constexpr std::string operator()(const T& t) const {
                return "\"" + t + "\"";
            }
        };
    }

    // Публічний CPO
    inline constexpr __to_json_detail::__to_json_fn to_json{};

    // Концепт перевірки підключення типу
    template<typename T>
    concept json_serializable = std::invocable<decltype(to_json), T>;
}

// Користувацький тип
namespace app {
    struct UserProfile {
        int id;
        std::string username;

        // Розширення через дружню функцію ADL
        friend std::string to_json(const UserProfile& u) {
            return "{\"id\":" + json_lib::to_json(u.id) + 
                   ",\"username\":" + json_lib::to_json(u.username) + "}";
        }
    };
}

int main() {
    app::UserProfile user{101, "alex_dev"};

    // Прямий виклик CPO
    if constexpr (json_lib::json_serializable<app::UserProfile>) {
        std::cout << json_lib::to_json(user) << "\n";
        // Виводить: {"id":101,"username":"alex_dev"}
    }
}
