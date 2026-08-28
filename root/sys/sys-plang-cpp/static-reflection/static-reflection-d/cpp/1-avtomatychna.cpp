template <typename T>
    requires std::is_class_v<T>
auto to_json(const T& obj) -> std::string {
    constexpr auto type_info = ^^T;
    constexpr auto members = std::meta::nonstatic_data_members_of(type_info);

    std::string result = "{";
    bool first = true;

    template for (constexpr auto member : members) {
        if (!first) result += ", ";
        result += std::format("\"{}\": {}", std::meta::name_of(member), serialize_val(obj.[: member :]));
        first = false;
    }

    result += "}";
    return result;
}
