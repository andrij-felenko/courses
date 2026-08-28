#include <functional>
#include <cstddef>

namespace physics::nonlinear::api {

/**
 * @brief Псевдонім C++20 для зворотного виклику прогресу.
 */
using ProgressCallback = std::function<bool(std::size_t completed, std::size_t total)>;

} // namespace physics::nonlinear::api
