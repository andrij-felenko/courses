#include <cstdint>
#include <array>

namespace msckf {

struct Vector3d {
    double x{0.0}, y{0.0}, z{0.0};
};

struct Quaterniond {
    double w{1.0}, x{0.0}, y{0.0}, z{0.0};
};

struct MsckfConfig {
    // Геометричне калібрування екстринсиків (Body -> Camera)
    Vector3d body_T_cam{0.0, 0.0, 0.0};
    Quaterniond body_R_cam{1.0, 0.0, 0.0, 0.0};
    
    // Параметри ковзного вікна
    uint32_t max_window_size{20};
    uint32_t min_track_length{3};
    
    // Шумові характеристики давачів
    double gyro_noise_density{1.5e-4};      // рад/(с·√Гц)
    double accel_noise_density{2.0e-3};     // м/(с²·√Гц)
    double gyro_bias_random_walk{1.0e-5};   // рад/(с²·√Гц)
    double accel_bias_random_walk{1.0e-4};  // м/(с³·√Гц)
    double pixel_noise_std{1.0 / 500.0};    // нормовані пікселі
    
    // Чисельні пороги
    double min_triangulation_deg{2.0};      // градуси
    double chi2_rejection_prob{0.95};
    bool enable_fej{true};                  // конзистентність FEJ
};

} // namespace msckf
