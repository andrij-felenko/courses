int main() {
    auto data = std::make_tuple(10, 3.14, std::string("core"));

    // Застосування мульти-типового трансформера (поліморфна лямбда)
    auto doubled = tuple_transform(data, [](const auto& val) {
        return val + val; // Множить числа та дублює рядок
    });

    // doubled має тип std::tuple<int, double, std::string> зі значеннями (20, 6.28, "corecore")
    std::cout << doubled << std::endl;
    return 0;
}
