template <typename E>
    requires std::is_enum_v<E>
constexpr auto enum_to_string(E val) -> std::string_view {
    template for (constexpr auto e : std::meta::enumerators_of(^^E)) {
        if (val == [: e :]) {
            return std::meta::name_of(e);
        }
    }
    return "Unknown";
}
