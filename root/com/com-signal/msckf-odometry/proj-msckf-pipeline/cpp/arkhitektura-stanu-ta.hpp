#include <vector>
#include <array>
#include <optional>
#include <cmath>
#include <cstdint>
#include <span>
#include <algorithm>

namespace msckf {

constexpr size_t MaxSlidingWindow = 20;
constexpr size_t ImuStateDim = 15;
constexpr size_t PoseStateDim = 6;

struct Vec3 {
    double x{0.0}, y{0.0}, z{0.0};
    
    constexpr Vec3 operator+(const Vec3& o) const noexcept { return {x + o.x, y + o.y, z + o.z}; }
    constexpr Vec3 operator-(const Vec3& o) const noexcept { return {x - o.x, y - o.y, z - o.z}; }
    constexpr Vec3 operator*(double s) const noexcept { return {x * s, y * s, z * s}; }
    double dot(const Vec3& o) const noexcept { return x * o.x + y * o.y + z * o.z; }
    Vec3 cross(const Vec3& o) const noexcept {
        return { y * o.z - z * o.y, z * o.x - x * o.z, x * o.y - y * o.x };
    }
};

struct Quat {
    double w{1.0}, x{0.0}, y{0.0}, z{0.0};
    
    Quat operator*(const Quat& r) const noexcept {
        return {
            w * r.w - x * r.x - y * r.y - z * r.z,
            w * r.x + x * r.w + y * r.z - z * r.y,
            w * r.y - x * r.z + y * r.w + z * r.x,
            w * r.z + x * r.y - y * r.x + z * r.w
        };
    }
};

struct ImuState {
    Vec3 pos;       // положення у світовій системі, м
    Vec3 vel;       // лінійна швидкість, м/с
    Quat att;       // орієнтація корпусу (кватерніон)
    Vec3 bg;        // зсув нуля гіроскопа, рад/с
    Vec3 ba;        // зсув нуля акселерометра, м/с²
};

struct CameraPose {
    double timestamp{0.0};
    Vec3 pos;       // положення камери у світовій системі
    Quat att;       // орієнтація камери
};

struct FeatureObservation {
    size_t pose_idx{0};
    double u{0.0}, v{0.0}; // нормовані координати камери
};

struct FeatureTrack {
    int32_t id{-1};
    std::vector<FeatureObservation> observations;
};

class MsckfEstimator {
public:
    MsckfEstimator();
    
    void propagateImu(const Vec3& acc, const Vec3& gyro, double dt);
    void augmentState(double timestamp, const Vec3& p_bc, const Quat& q_bc);
    void updateFeature(const FeatureTrack& track);
    void marginalizeOldestPose();

    const ImuState& getImuState() const noexcept { return imu_; }
    size_t getWindowSize() const noexcept { return window_.size(); }

private:
    ImuState imu_;
    std::vector<CameraPose> window_;
    std::vector<double> cov_matrix_; // розмір (15 + 6N) * (15 + 6N)
    
    void resizeCovariance(size_t new_dim);
};

} // namespace msckf
