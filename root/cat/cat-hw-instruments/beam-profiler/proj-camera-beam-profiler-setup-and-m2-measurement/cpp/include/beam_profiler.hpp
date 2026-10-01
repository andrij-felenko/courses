#ifndef BEAM_PROFILER_HPP
#define BEAM_PROFILER_HPP

#include <vector>
#include <cstdint>
#include <cstddef>
#include <stdexcept>
#include <string>

namespace optical {

// Структура для збереження двовимірного кадру зображення з матриці
struct ImageFrame {
    std::size_t width{0};
    std::size_t height{0};
    std::vector<uint16_t> pixels; // 16-бітні відліки АЦП сенсора

    ImageFrame() = default;
    ImageFrame(std::size_t w, std::size_t h, uint16_t fill_val = 0)
        : width(w), height(h), pixels(w * h, fill_val) {}

    uint16_t at(std::size_t x, std::size_t y) const {
        return pixels[y * width + x];
    }

    uint16_t& at(std::size_t x, std::size_t y) {
        return pixels[y * width + x];
    }
};

// Структура результатів вимірювання просторових параметрів пучка за ISO 11146
struct BeamParams {
    double centroid_x{0.0};     // Координата X центроїда (пікселі)
    double centroid_y{0.0};     // Координата Y центроїда (пікселі)
    double sigma_x{0.0};        // Середньоквадратичне відхилення по X (пікселі)
    double sigma_y{0.0};        // Середньоквадратичне відхилення по Y (пікселі)
    double d4sigma_x{0.0};      // Діаметр D4σ по X (пікселі)
    double d4sigma_y{0.0};      // Діаметр D4σ по Y (пікселі)
    double ellipticity{0.0};    // Еліптичність променя (D4σ_min / D4σ_max)
    double total_power{0.0};    // Сумарна інтенсивність (M0)
};

// Виміряна перетяжка на певній координаті Z вздовж оптичної осі
struct ZScanPoint {
    double z_mm{0.0};           // Положення вздовж осі Z (мм)
    double d4sigma_mm{0.0};     // Виміряний діаметр D4σ (мм)
};

// Клас аналізатора профілю лазерного пучка
class BeamProfilerAnalyzer {
public:
    explicit BeamProfilerAnalyzer(double pixel_pitch_um = 3.45, double threshold_pct = 0.015)
        : pixel_pitch_um_(pixel_pitch_um), threshold_pct_(threshold_pct) {}

    // Захоплення та збереження темнового кадру (Ultracal / Dark Frame)
    void capture_dark_frame(const ImageFrame& dark_frame);

    // Перевірка наявності калібрувального темнового кадру
    bool has_dark_frame() const { return !dark_frame_.pixels.empty(); }

    // Обробка сирого кадру: Ultracal віднімання, порогова фільтрація та розрахунок моментів D4σ
    BeamParams process_frame(const ImageFrame& raw_frame);

    // Апроксимація фактора якості M² за серією вимірювань D4σ(z) та довжиною хвилі λ (нм)
    double compute_m2(const std::vector<ZScanPoint>& scan_points, double wavelength_nm) const;

private:
    double pixel_pitch_um_;   // Фізичний розмір пікселя сенсора (мікрометри)
    double threshold_pct_;     // Відносний поріг відсікання фону (наприклад 0.015 = 1.5% від I_max)
    ImageFrame dark_frame_;    // Збережений темновий кадр
};

} // namespace optical

#endif // BEAM_PROFILER_HPP
