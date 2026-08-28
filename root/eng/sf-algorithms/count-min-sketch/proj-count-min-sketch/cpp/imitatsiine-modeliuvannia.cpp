int main() {
    // Ініціалізація ескізу з параметрами epsilon = 0.001, delta = 0.01
    CountMinSketch sketch(0.001, 0.01);
    
    std::cout << "Розмір матриці Count-Min Sketch: "
              << sketch.width() << " стовпців x " << sketch.depth()
              << " рядків (пам'ять: "
              << (sketch.width() * sketch.depth() * sizeof(uint32_t)) / 1024.0
              << " КБ)\n\n";
    
    const std::string heavy_ip = "192.168.1.100";
    const std::string medium_ip = "10.0.0.5";
    const std::string rare_ip = "172.16.0.1";
    
    sketch.update_conservative(heavy_ip, 50000);
    sketch.update_conservative(medium_ip, 5000);
    sketch.update_conservative(rare_ip, 10);
    
    // Додавання фонового шуму
    for (int i = 0; i < 944990; ++i) {
        std::string noise_ip = "10.1." + std::to_string((i / 256) % 256) + "." + std::to_string(i % 256);
        sketch.update_conservative(noise_ip, 1);
    }
    
    std::cout << "Результати оцінки частот:\n";
    std::cout << "IP " << heavy_ip << " | Істинна: 50000 | Оцінка: " << sketch.estimate(heavy_ip) << "\n";
    std::cout << "IP " << medium_ip << " | Істинна: 5000  | Оцінка: " << sketch.estimate(medium_ip) << "\n";
    std::cout << "IP " << rare_ip   << " | Істинна: 10    | Оцінка: " << sketch.estimate(rare_ip) << "\n";
    
    return 0;
}
