#include <sstream>
#include <charconv>

// Простий парсер токенів JSON для демонстрації
struct JsonParser {
    std::string_view src;
    size_t pos = 0;

    void skip_whitespace() {
        while (pos < src.size() && (src[pos] == ' ' || src[pos] == '\t' || src[pos] == '\n' || src[pos] == '\r')) {
            pos++;
        }
    }

    bool consume(char expected) {
        skip_whitespace();
        if (pos < src.size() && src[pos] == expected) {
            pos++;
            return true;
        }
        return false;
    }

    auto parse_string() -> std::string {
        skip_whitespace();
        if (!consume('"')) throw std::runtime_error("Очікувався символ '\"'");
        size_t start = pos;
        while (pos < src.size() && src[pos] != '"') {
            if (src[pos] == '\\') pos++; // пропуск екранованого символу
            pos++;
        }
        std::string result(src.substr(start, pos - start));
        consume('"');
        return result;
    }

    template <typename NumberType>
    auto parse_number() -> NumberType {
        skip_whitespace();
        size_t start = pos;
        if (pos < src.size() && (src[pos] == '-' || src[pos] == '+')) pos++;
        while (pos < src.size() && ((src[pos] >= '0' && src[pos] <= '9') || src[pos] == '.')) {
            pos++;
        }
        std::string_view num_str = src.substr(start, pos - start);
        NumberType val{};
        auto [ptr, ec] = std::from_chars(num_str.data(), num_str.data() + num_str.size(), val);
        if (ec != std::errc{}) throw std::runtime_error("Помилка парсингу числа");
        return val;
    }

    auto parse_bool() -> bool {
        skip_whitespace();
        if (src.substr(pos, 4) == "true") { pos += 4; return true; }
        if (src.substr(pos, 5) == "false") { pos += 5; return false; }
        throw std::runtime_error("Очікувалося логічне значення true/false");
    }
};

// Десеріалізація примітивних значень
template <typename T>
void parse_into(JsonParser& parser, T& target) {
    if constexpr (std::same_as<T, int> || std::same_as<T, uint32_t> || std::same_as<T, size_t>) {
        target = parser.parse_number<T>();
    } else if constexpr (std::same_as<T, double> || std::same_as<T, float>) {
        target = parser.parse_number<T>();
    } else if constexpr (std::same_as<T, bool>) {
        target = parser.parse_bool();
    } else if constexpr (std::same_as<T, std::string>) {
        target = parser.parse_string();
    } else if constexpr (std::is_enum_v<T>) {
        std::string str = parser.parse_string();
        auto opt = string_to_enum<T>(str);
        if (!opt) throw std::runtime_error("Невідоме значення enum у JSON: " + str);
        target = *opt;
    } else if constexpr (std::is_class_v<T>) {
        // Десеріалізація вкладеної структури через рефлексію
        constexpr auto type_info = ^^T;
        constexpr auto members = std::meta::nonstatic_data_members_of(type_info);

        if (!parser.consume('{')) throw std::runtime_error("Очікувався початок об'єкта '{'");

        while (!parser.consume('}')) {
            std::string key = parser.parse_string();
            if (!parser.consume(':')) throw std::runtime_error("Очікувалося двоеточие ':' після ключа");

            bool field_found = false;
            template for (constexpr auto member : members) {
                if (key == std::meta::name_of(member)) {
                    parse_into(parser, target.[: member :]);
                    field_found = true;
                }
            }

            if (!field_found) {
                // Пропуск невідомого поля (або генерація помилки)
                parser.parse_string();
            }

            parser.consume(',');
        }
    }
}

// Головна функція десеріалізації
template <typename T>
auto from_json(std::string_view json_text) -> T {
    JsonParser parser{.src = json_text};
    T result{};
    parse_into(parser, result);
    return result;
}
