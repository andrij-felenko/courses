// Класичний стиль C++17
std::optional<User> find_user(int id);
std::optional<Address> get_address(const User& u);
std::optional<GeoPoint> get_coords(const Address& a);

std::optional<GeoPoint> locate(int id) {
    auto u = find_user(id);
    if (!u) return std::nullopt;
    auto a = get_address(*u);
    if (!a) return std::nullopt;
    return get_coords(*a);
}
