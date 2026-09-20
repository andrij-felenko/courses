#include <array>
#include <algorithm>

template <std::size_t N>
class RvdtLutCalibrator {
public:
    using NodeArray = std::array<float, N>;

    RvdtLutCalibrator(NodeArray x_nodes, NodeArray y_nodes)
        : x_nodes_(x_nodes), y_nodes_(y_nodes) {}

    float correctAngle(float raw_angle) const noexcept {
        if (raw_angle <= x_nodes_.front()) return y_nodes_.front();
        if (raw_angle >= x_nodes_.back())  return y_nodes_.back();

        auto it = std::upper_bound(x_nodes_.begin(), x_nodes_.end(), raw_angle);
        std::size_t idx = std::distance(x_nodes_.begin(), it) - 1;

        const float dx = raw_angle - x_nodes_[idx];
        const float dx_span = x_nodes_[idx + 1] - x_nodes_[idx];
        const float dy_span = y_nodes_[idx + 1] - y_nodes_[idx];
        const float slope = dy_span / dx_span;

        return y_nodes_[idx] + dx * slope;
    }

private:
    NodeArray x_nodes_;
    NodeArray y_nodes_;
};
