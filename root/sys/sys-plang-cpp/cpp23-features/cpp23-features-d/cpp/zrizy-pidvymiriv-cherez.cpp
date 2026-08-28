#include <mdspan>

void slice_3d_volume() {
    double raw_data[100 * 100 * 100];
    std::mdspan<double, std::extents<size_t, 100, 100, 100>> volume(raw_data);

    // Отримання 2D-зрізу (переріз по Z = 42)
    auto plane_2d = std::submdspan(volume, 42, std::full_extent, std::full_extent);

    // plane_2d має ранг 2 та розмірність 100x100
    plane_2d[10, 20] = 1.0; // Записує безпосередньо у вихідний масив raw_data
}
