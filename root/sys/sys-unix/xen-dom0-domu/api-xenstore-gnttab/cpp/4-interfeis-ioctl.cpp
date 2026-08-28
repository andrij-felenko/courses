// C++ структура запиту відображення грантів
struct GntdevMapGrantRef {
    std::uint32_t count; // Кількість грантів у масиві
    std::uint32_t pad;
    struct GrantRef {
        std::uint32_t domid; // ID домену-власника
        std::uint32_t ref;   // Індекс grant reference (gref)
    } refs[1];

    std::uint64_t index; // Віртуальне зміщення для виклику mmap()
};

struct GntdevUnmapGrantRef {
    std::uint64_t index; // Зміщення, отримане під час map
    std::uint32_t count; // Кількість сторінок для unmap
    std::uint32_t pad;
};
