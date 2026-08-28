int main() {
    std::cout << "Line (0,0) -> (7,3):\n";
    auto line_pixels = BresenhamRasterizer::rasterize_line({0, 0}, {7, 3});
    for (const auto& p : line_pixels) {
        std::cout << "(" << p.x << ", " << p.y << ") ";
    }
    
    std::cout << "\n\nCircle R=6 at (0,0):\n";
    auto circle_pixels = BresenhamCircle::rasterize_circle({0, 0}, 6);
    for (const auto& p : circle_pixels) {
        std::cout << "(" << p.x << ", " << p.y << ") ";
    }
    std::cout << "\n";
    return 0;
}
