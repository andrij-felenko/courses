#include <iostream>
#include <vector>
#include "horseshoe.hpp"

int main() {
    using namespace physics::mechanics;

    Config cfg{.alpha = 0.35, .beta = 2.4};
    HorseshoeMap map(cfg);

    std::vector<Point2D> ensemble{
        {.x = 0.2, .y = 0.1},
        {.x = 0.5, .y = 0.5},
        {.x = 0.8, .y = 0.9}
    };

    std::cout << "--- Драйвер симуляції відображення підкови (C++) ---\n";
    for (size_t i = 0; i < ensemble.size(); ++i) {
        auto result = map.forward(ensemble[i]);
        if (result) {
            std::cout << "Точка #" << i << ": (" << ensemble[i].x << ", " << ensemble[i].y
                      << ") -> (" << result->x << ", " << result->y << ")\n";
        } else if (result.error() == MappingStatus::EscapedDomain) {
            std::cout << "Точка #" << i << ": (" << ensemble[i].x << ", " << ensemble[i].y
                      << ") -> Вилетіла з квадрата S\n";
        } else {
            std::cout << "Точка #" << i << ": Помилка відображення\n";
        }
    }

    auto [lx, ly] = map.lyapunovExponents();
    std::cout << "Показники Ляпунова: lambda_x = " << lx << ", lambda_y = " << ly << "\n";
    std::cout << "Фрактальна вимірність інваріантної множини: D_box = " << map.capacityDimension() << "\n";

    return 0;
}
