// 2D кодування у C++ (constexpr, noexcept)
std::uint64_t morton_encode2d(std::uint32_t x, std::uint32_t y) noexcept;

// 2D декодування у C++ (std::pair)
std::pair<std::uint32_t, std::uint32_t> morton_decode2d(std::uint64_t z) noexcept;

// 3D кодування у C++
std::uint64_t morton_encode3d(std::uint32_t x, std::uint32_t y, std::uint32_t z) noexcept;

// 3D декодування у C++ (std::tuple)
std::tuple<std::uint32_t, std::uint32_t, std::uint32_t> morton_decode3d(std::uint64_t key) noexcept;
