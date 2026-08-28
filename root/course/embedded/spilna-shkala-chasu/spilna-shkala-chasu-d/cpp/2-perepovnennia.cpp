#include <cstdint>
#include <chrono>

using namespace std::chrono_literals;

// Беззнакове модульне віднімання переповнення
constexpr std::uint32_t t_prev = 4'294'967'200U;
constexpr std::uint32_t t_now  = 50U;
constexpr std::uint32_t dt_raw = t_now - t_prev; // Рівно 145 мкс
const auto dt = std::chrono::microseconds(dt_raw);
