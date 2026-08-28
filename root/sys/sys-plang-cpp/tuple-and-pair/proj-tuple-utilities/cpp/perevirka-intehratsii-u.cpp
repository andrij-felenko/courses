int main() {
    GeoPoint point(50.4501, 30.5234, "Kyiv Central");

    // Розкладання об'єкта GeoPoint через структуровані зв'язування C++17
    auto [lat, lon, name] = point;

    std::cout << "Широта: " << lat << "\n"
              << "Довгота: " << lon << "\n"
              << "Місто: " << name << std::endl;

    // Розкладання за мінливим посиланням
    auto& [mut_lat, mut_lon, mut_name] = point;
    mut_name = "Kyiv Main Station"; // Змінює поле усередині об'єкта point!

    std::cout << "Оновлена назва: " << point.label() << std::endl;
    return 0;
}
