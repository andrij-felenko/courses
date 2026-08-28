int main() {
    const std::vector<Point> raw = {
        {0.0, 0.0}, {1.0, 0.1}, {2.0, -0.1}, {3.0, 5.0},
        {4.0, 5.2}, {5.0, 0.0}, {6.0, 0.2},  {7.0, 0.0}
    };
    constexpr double eps = 1.0;

    const auto rdp = simplifyDouglasPeucker(raw, eps);
    std::cout << "Douglas-Peucker: " << rdp.size() << " точок з " << raw.size() << " збережено\n";

    const auto rw = simplifyReumannWitkam(raw, eps);
    std::cout << "Reumann-Witkam:  " << rw.size() << " точок з " << raw.size() << " збережено\n";

    const auto vw = simplifyVisvalingamWhyatt(raw, 4);
    std::cout << "Visvalingam:     " << vw.size() << " точок збережено (target=4)\n";

    return 0;
}
