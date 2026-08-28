#include <vector>
#include <cstddef>

namespace physics::nonlinear::api {

class LookupTable {
public:
    explicit LookupTable(std::size_t size = 4096);
    [[nodiscard]] double fast_sin(double phase) const noexcept;

private:
    std::vector<double> table_;
};

} // namespace physics::nonlinear::api
