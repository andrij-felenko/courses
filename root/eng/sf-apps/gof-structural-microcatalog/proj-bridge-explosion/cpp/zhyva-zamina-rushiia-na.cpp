int main() {
    SvgRenderer svg;
    std::vector<std::unique_ptr<Shape>> shapes;
    shapes.push_back(std::make_unique<Rect>(&svg, 2, 2, 76, 36));
    shapes.push_back(std::make_unique<Circle>(&svg, 16, 20, 10));
    shapes.push_back(std::make_unique<Triangle>(&svg, Point{40, 8}, Point{50, 32}, Point{30, 32}));
    shapes.push_back(std::make_unique<Star>(&svg, 64, 20, 12, 5, 5));
    Scene scene(&svg, std::move(shapes));
    std::cout << scene.draw(80, 40) << '\n';    // SVG

    AsciiRenderer ascii;
    scene.use(&ascii);                          // ← ті самі об'єкти фігур, інший носій
    std::cout << scene.draw(80, 40) << '\n';    // прев'ю в терміналі

    StatsRenderer stats;
    scene.use(&stats);
    std::cout << scene.draw(80, 40) << '\n';    // обмір для тесту
}
