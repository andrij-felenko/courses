#include <meta>
#include <string_view>
#include <optional>
#include <array>

enum class NetworkProtocol {
    Http11,
    Http2,
    Http3,
    WebSocket,
    Grpc
};

// 1. Конвертація Enum -> String часу компіляції
template <typename E>
requires std::is_enum_v<E>
constexpr std::string_view enum_to_string(E value) noexcept {
    constexpr auto enum_meta = ^^E;
    constexpr auto enumerators = std::meta::enumerators_of(enum_meta);

    std::string_view result = "UNKNOWN";
    [: expand(enumerators) :] >> [&]<auto enum_item_meta>() {
        if (value == [: enum_item_meta :]) {
            result = std::meta::name_of(enum_item_meta);
        }
    };
    return result;
}

// 2. Зворотна конвертація String -> Enum
template <typename E>
requires std::is_enum_v<E>
constexpr std::optional<E> string_to_enum(std::string_view name) noexcept {
    constexpr auto enum_meta = ^^E;
    constexpr auto enumerators = std::meta::enumerators_of(enum_meta);

    std::optional<E> result = std::nullopt;
    [: expand(enumerators) :] >> [&]<auto enum_item_meta>() {
        if (name == std::meta::name_of(enum_item_meta)) {
            result = [: enum_item_meta :];
        }
    };
    return result;
}

void test_enum_reflection() {
    constexpr auto name = enum_to_string(NetworkProtocol::Http3);
    static_assert(name == "Http3", "Помилка конвертації переліку у рядок!");

    constexpr auto proto = string_to_enum<NetworkProtocol>("WebSocket");
    static_assert(proto.has_value() && *proto == NetworkProtocol::WebSocket, "Помилка парсингу рядка у перелік!");
}
