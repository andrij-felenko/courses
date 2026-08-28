#include <cmath>
#include <numbers>
#include <vector>
#include <fstream>
#include <string_view>
#include <optional>
#include <span>
#include <algorithm>

struct Point3D {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
    float intensity{0.0f};
};

struct CalibrationParams {
    float baseline_mm{120.0f};       // Базова лінія B
    float focal_length_px{1050.0f};   // Фокусна відстань камери f_c
    float cx{640.0f};                 // Головна точка x
    float cy{360.0f};                 // Головна точка y
    int   proj_width_px{1920};        // Горизонтальна роздільність проектора
    int   fringe_periods{16};         // Кількість періодів високої частоти
    float min_modulation{10.0f};      // Поріг надійності модуляції
    float min_z_mm{200.0f};           // Близька межа вимірювання
    float max_z_mm{2500.0f};          // Далека межа вимірювання
};

class StructuredLightReconstructor {
public:
    explicit StructuredLightReconstructor(CalibrationParams calib) 
        : calib_(calib) {}

    // Обчислення загорнутої фази та амплітуди модуляції
    static void compute4StepPhase(std::span<const float> i0, std::span<const float> i1,
                                 std::span<const float> i2, std::span<const float> i3,
                                 std::span<float> phase_out, std::span<float> mod_out) {
        const size_t n = phase_out.size();
        for (size_t i = 0; i < n; ++i) {
            const float num = i3[i] - i1[i];
            const float den = i0[i] - i2[i];
            phase_out[i] = std::atan2(num, den);
            mod_out[i]   = 0.5f * std::sqrt(den * den + num * num);
        }
    }

    // Двочастотне розгортання фази
    static void temporalUnwrap(std::span<const float> coarse_phase,
                               std::span<const float> fine_phase,
                               std::span<float> abs_phase_out,
                               int n_periods) {
        constexpr float two_pi = 2.0f * std::numbers::pi_v<float>;
        const size_t n = abs_phase_out.size();

        for (size_t i = 0; i < n; ++i) {
            float phi1 = coarse_phase[i];
            if (phi1 < 0.0f) phi1 += two_pi;

            float phi2 = fine_phase[i];
            if (phi2 < 0.0f) phi2 += two_pi;

            const float k_est = (n_periods * phi1 - phi2) / two_pi;
            const int k = std::clamp(static_cast<int>(std::round(k_est)), 0, n_periods - 1);

            abs_phase_out[i] = phi2 + two_pi * static_cast<float>(k);
        }
    }

    // Тріангуляція у хмару точок
    [[nodiscard]] std::vector<Point3D> reconstruct(std::span<const float> abs_phase,
                                                   std::span<const float> modulation,
                                                   int width, int height) const {
        std::vector<Point3D> cloud;
        cloud.reserve(width * height / 4);

        const float max_abs_phase = 2.0f * std::numbers::pi_v<float> * static_cast<float>(calib_.fringe_periods);

        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                const size_t idx = static_cast<size_t>(y * width + x);

                if (modulation[idx] < calib_.min_modulation) {
                    continue; // Відсікання тіней
                }

                const float u_proj = (abs_phase[idx] / max_abs_phase) * static_cast<float>(calib_.proj_width_px);
                const float disparity = static_cast<float>(x) - u_proj;

                if (disparity <= 0.001f) {
                    continue;
                }

                const float z = (calib_.baseline_mm * calib_.focal_length_px) / disparity;
                if (z < calib_.min_z_mm || z > calib_.max_z_mm) {
                    continue;
                }

                const float x_mm = (static_cast<float>(x) - calib_.cx) * z / calib_.focal_length_px;
                const float y_mm = (static_cast<float>(y) - calib_.cy) * z / calib_.focal_length_px;

                cloud.push_back({x_mm, y_mm, z, modulation[idx]});
            }
        }
        return cloud;
    }

    // Експорт у формат PLY
    static bool exportPly(std::string_view filepath, std::span<const Point3D> cloud) {
        std::ofstream ofs(filepath.data());
        if (!ofs.is_open()) return false;

        ofs << "ply\n"
            << "format ascii 1.0\n"
            << "element vertex " << cloud.size() << "\n"
            << "property float x\n"
            << "property float y\n"
            << "property float z\n"
            << "property float intensity\n"
            << "end_header\n";

        for (const auto& pt : cloud) {
            ofs << pt.x << ' ' << pt.y << ' ' << pt.z << ' ' << pt.intensity << '\n';
        }
        return true;
    }

private:
    CalibrationParams calib_;
};
