#include "beam_profiler.hpp"
#include <cmath>
#include <algorithm>
#include <stdexcept>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace optical {

void BeamProfilerAnalyzer::capture_dark_frame(const ImageFrame& dark_frame) {
    if (dark_frame.width == 0 || dark_frame.height == 0 || dark_frame.pixels.empty()) {
        throw std::invalid_argument("Темновий кадр не може бути порожнім.");
    }
    dark_frame_ = dark_frame;
}

BeamParams BeamProfilerAnalyzer::process_frame(const ImageFrame& raw_frame) {
    if (raw_frame.width == 0 || raw_frame.height == 0 || raw_frame.pixels.empty()) {
        throw std::invalid_argument("Сирий кадр не містить зображення.");
    }

    if (has_dark_frame()) {
        if (raw_frame.width != dark_frame_.width || raw_frame.height != dark_frame_.height) {
            throw std::invalid_argument("Розміри сирого та темнового кадрів не збігаються.");
        }
    }

    const std::size_t width = raw_frame.width;
    const std::size_t height = raw_frame.height;
    const std::size_t total_pixels = width * height;

    // Крок 1: Попіксельне віднімання темнового кадру (Ultracal subtraction)
    std::vector<double> sub_frame(total_pixels, 0.0);
    double max_intensity = 0.0;

    for (std::size_t i = 0; i < total_pixels; ++i) {
        double raw_val = static_cast<double>(raw_frame.pixels[i]);
        double dark_val = has_dark_frame() ? static_cast<double>(dark_frame_.pixels[i]) : 0.0;
        
        // max(0, I_raw - I_dark) для запобігання від'ємним значенням
        double val = std::max(0.0, raw_val - dark_val);
        sub_frame[i] = val;
        if (val > max_intensity) {
            max_intensity = val;
        }
    }

    if (max_intensity <= 0.0) {
        throw std::runtime_error("Сигнал на кадрі відсутній (інтенсивність дорівнює нулю).");
    }

    // Крок 2: Порогова фільтрація за вимогами ISO 11146 (усунення периферійного шуму)
    double threshold_val = max_intensity * threshold_pct_;
    std::vector<double> filt_frame(total_pixels, 0.0);

    for (std::size_t i = 0; i < total_pixels; ++i) {
        if (sub_frame[i] >= threshold_val) {
            filt_frame[i] = sub_frame[i] - threshold_val; // Зсув фону до чистого нуля
        }
    }

    // Крок 3: Обчислення нульового M0 та перших моментів (центроїд x0, y0)
    double m0 = 0.0;
    double m10 = 0.0;
    double m01 = 0.0;

    for (std::size_t y = 0; y < height; ++y) {
        for (std::size_t x = 0; x < width; ++x) {
            double val = filt_frame[y * width + x];
            m0 += val;
            m10 += static_cast<double>(x) * val;
            m01 += static_cast<double>(y) * val;
        }
    }

    if (m0 <= 0.0) {
        throw std::runtime_error("Корисний сигнал після порогової фільтрації порожній.");
    }

    double x0 = m10 / m0;
    double y0 = m01 / m0;

    // Крок 4: Обчислення центральних других моментів (дисперсій σx², σy²)
    double mu20 = 0.0; // σx²
    double mu02 = 0.0; // σy²

    for (std::size_t y = 0; y < height; ++y) {
        double dy = static_cast<double>(y) - y0;
        for (std::size_t x = 0; x < width; ++x) {
            double dx = static_cast<double>(x) - x0;
            double val = filt_frame[y * width + x];

            mu20 += dx * dx * val;
            mu02 += dy * dy * val;
        }
    }

    double var_x = mu20 / m0;
    double var_y = mu02 / m0;

    double sigma_x = std::sqrt(std::max(0.0, var_x));
    double sigma_y = std::sqrt(std::max(0.0, var_y));

    // Еквівалентні діаметри пучка D4σ = 4 * σ
    double d4s_x = 4.0 * sigma_x;
    double d4s_y = 4.0 * sigma_y;

    double min_d = std::min(d4s_x, d4s_y);
    double max_d = std::max(d4s_x, d4s_y);
    double ellipticity = (max_d > 0.0) ? (min_d / max_d) : 1.0;

    BeamParams params;
    params.centroid_x = x0;
    params.centroid_y = y0;
    params.sigma_x = sigma_x;
    params.sigma_y = sigma_y;
    params.d4sigma_x = d4s_x;
    params.d4sigma_y = d4s_y;
    params.ellipticity = ellipticity;
    params.total_power = m0;

    return params;
}

double BeamProfilerAnalyzer::compute_m2(const std::vector<ZScanPoint>& scan_points, double wavelength_nm) const {
    if (scan_points.size() < 3) {
        throw std::invalid_argument("Для апроксимації M² потрібно щонайменше 3 точки вимірювання уздовж осі Z.");
    }
    if (wavelength_nm <= 0.0) {
        throw std::invalid_argument("Некоректна довжина хвилі лазера.");
    }

    // Пошук мінімального діаметра (перетяжки W0) та кута розбіжності θ
    double min_d = scan_points[0].d4sigma_mm;
    double z_at_min = scan_points[0].z_mm;

    for (const auto& pt : scan_points) {
        if (pt.d4sigma_mm < min_d) {
            min_d = pt.d4sigma_mm;
            z_at_min = pt.z_mm;
        }
    }

    double w0_mm = min_d / 2.0; // Радіус перетяжки w0 = D4σ / 2
    if (w0_mm <= 0.0) {
        throw std::runtime_error("Неможливо обчислити радіус перетяжки w0.");
    }

    // Обчислення кута розбіжності θ за далекими точками від перетяжки
    double max_dz = 0.0;
    double theta_rad = 0.0;

    for (const auto& pt : scan_points) {
        double dz = std::abs(pt.z_mm - z_at_min);
        if (dz > max_dz && dz > 10.0) {
            max_dz = dz;
            double w_z = pt.d4sigma_mm / 2.0;
            theta_rad = std::sqrt(std::max(0.0, w_z * w_z - w0_mm * w0_mm)) / dz;
        }
    }

    if (theta_rad <= 0.0) {
        // Запасний варіант: оцінка кута за крайовими точками
        double dz = std::abs(scan_points.back().z_mm - scan_points.front().z_mm);
        double dw = std::abs(scan_points.back().d4sigma_mm - scan_points.front().d4sigma_mm) / 2.0;
        theta_rad = (dz > 0.0) ? (dw / dz) : 0.001;
    }

    double wavelength_mm = wavelength_nm * 1e-6; // Переведення нм у мм
    double m2 = (M_PI * w0_mm * theta_rad) / wavelength_mm;

    return std::max(1.0, m2); // M² завжди >= 1.0 за законами оптики
}

} // namespace optical
