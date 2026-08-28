struct Point {
    float x, y, z;
};

Point cloud[100];
std::span<Point, 100> point_span{cloud};

// Перетворення у константний байтовий зріз
std::span<const std::byte, 1200> byte_view = std::as_bytes(point_span);

// Перетворення у модифікований байтовий зріз для запису з мережі чи файлу
std::span<std::byte, 1200> writable_byte_view = std::as_writable_bytes(point_span);
