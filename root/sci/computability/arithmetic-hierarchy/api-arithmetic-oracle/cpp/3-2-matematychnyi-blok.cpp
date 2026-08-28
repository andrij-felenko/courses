/**
 * @brief Пряме кодування паруванням Кантора у C++ (constexpr).
 */
[[nodiscard]] constexpr std::expected<std::uint64_t, std::string_view>
cantor_encode(std::uint64_t x, std::uint64_t y) noexcept;

/**
 * @brief Декодування коду Кантора у C++23.
 */
[[nodiscard]] constexpr std::pair<std::uint64_t, std::uint64_t>
cantor_decode(std::uint64_t code) noexcept;
