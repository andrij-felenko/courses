#define VISION_COG_EXTRACTOR_HPP_

#include <opencv2/core.hpp>
#include <vector>
#include <cmath>
#include <cstdint>
#include <algorithm>

namespace vision {

/**
 * @brief Результат субпіксельного виявлення лазерної смуги в окремому стовпці кадру.
 */
struct ProfilePoint {
    float subpixel_y{0.0f};       // Обчислена субпіксельна вертикальна координата лінії
    float peak_intensity{0.0f};   // Максимальна яскравість у стовпці (0..255 DN)
    float integrated_mass{0.0f};  // Інтегральна енергія смуги за вирахуванням фону
    bool is_valid{false};         // Ознака достовірного піка (вище порогу шуму)
    bool is_saturated{false};     // Ознака пересвіту/кліпінгу пікселів (плато 255 DN)
};

/**
 * @brief Параметри конфігурації екстрактора центру мас лазерної лінії.
 */
struct ExtractorConfig {
    uint8_t noise_threshold_dn{35};        // Поріг відсікання темнового шуму та фону
    int window_half_width{4};               // Напівширина вікна розрахунку COG навколо піка (px)
    float min_integrated_mass{40.0f};       // Мінімальна інтегральна енергія для валідації лінії
    int roi_top{0};                         // Верхня межа зони сканування (0 = верх кадру)
    int roi_bottom{0};                      // Нижня межа зони сканування (0 = висота кадру)
    uint8_t saturation_threshold_dn{254};   // Поріг виявлення кліпінгу сенсора
    bool use_parallel{true};                // Дозвіл багатопотокового обчислення стовпців
};

/**
 * @brief Високошвидкісний субпіксельний детектор центру мас (Center of Gravity, COG).
 * 
 * Здійснює постовпчиковий пошук лазерного максимуму з вирахуванням фонового шуму
 * та віконною апроксимацією положення лінії з точністю до десятих/сотих часток пікселя.
 */
class LaserCogExtractor {
public:
    explicit LaserCogExtractor(const ExtractorConfig& config = ExtractorConfig{})
        : config_(config) {}

    void set_config(const ExtractorConfig& config) noexcept {
        config_ = config;
    }

    [[nodiscard]] const ExtractorConfig& config() const noexcept {
        return config_;
    }

    /**
     * @brief Обробка монохромного кадру та вилучення профілю лазерної лінії.
     * 
     * @param gray_image Вхідне 8-бітне одноканальне зображення (CV_8UC1)
     * @param out_profile Вихідний вектор профілю (розмір дорівнює ширині кадру)
     * @return true у разі успішного виконання обробки
     */
    bool process(const cv::Mat& gray_image, std::vector<ProfilePoint>& out_profile) {
        if (gray_image.empty() || gray_image.type() != CV_8UC1) {
            return false;
        }

        const int width = gray_image.cols;
        const int height = gray_image.rows;

        // Автоматичне підлаштування меж ROI
        const int actual_roi_top = std::max(0, std::min(config_.roi_top, height - 1));
        const int actual_roi_bottom = (config_.roi_bottom > actual_roi_top && config_.roi_bottom <= height)
                                          ? config_.roi_bottom
                                          : height;

        // Передвиділення вихідного буфера без повторних реаллокацій у циклі
        if (out_profile.size() != static_cast<size_t>(width)) {
            out_profile.resize(width);
        }

        // Кешування вказівників на початки рядків для швидкого доступу без викликів Mat::at()
        std::vector<const uint8_t*> row_ptrs(actual_roi_bottom - actual_roi_top);
        for (int y = actual_roi_top; y < actual_roi_bottom; ++y) {
            row_ptrs[y - actual_roi_top] = gray_image.ptr<uint8_t>(y);
        }

        const auto process_column = [&](int x) {
            ProfilePoint& point = out_profile[x];
            point = ProfilePoint{}; // Скидання стану

            // Крок 1: Пошук абсолютного максимуму інтенсивності у стовпці x
            uint8_t max_val = 0;
            int best_y = -1;

            const int roi_height = actual_roi_bottom - actual_roi_top;
            for (int r = 0; r < roi_height; ++r) {
                const uint8_t val = row_ptrs[r][x];
                if (val > max_val) {
                    max_val = val;
                    best_y = actual_roi_top + r;
                }
            }

            // Відсікання фонового шуму: якщо пік менший за поріг, лазер відсутній
            if (max_val < config_.noise_threshold_dn || best_y < 0) {
                point.is_valid = false;
                point.peak_intensity = static_cast<float>(max_val);
                return;
            }

            point.peak_intensity = static_cast<float>(max_val);
            point.is_saturated = (max_val >= config_.saturation_threshold_dn);

            // Крок 2: Віконний розрахунок центру мас навколо знайденого піка
            const int win_start = std::max(actual_roi_top, best_y - config_.window_half_width);
            const int win_end = std::min(actual_roi_bottom - 1, best_y + config_.window_half_width);

            float sum_mass = 0.0f;
            float sum_weighted_y = 0.0f;
            const float threshold_baseline = static_cast<float>(config_.noise_threshold_dn);

            for (int y = win_start; y <= win_end; ++y) {
                const uint8_t raw_val = row_ptrs[y - actual_roi_top][x];
                if (raw_val > config_.noise_threshold_dn) {
                    // Вираховуємо поріг фону (базову лінію) для усунення зміщення центроїда
                    const float effective_weight = static_cast<float>(raw_val) - threshold_baseline;
                    sum_mass += effective_weight;
                    sum_weighted_y += static_cast<float>(y) * effective_weight;
                }
            }

            // Крок 3: Перевірка достатності маси сигналу для валідного результату
            if (sum_mass >= config_.min_integrated_mass) {
                point.subpixel_y = sum_weighted_y / sum_mass;
                point.integrated_mass = sum_mass;
                point.is_valid = true;
            } else {
                point.is_valid = false;
            }
        };

        // Виконання: паралельне або послідовне обчислення
        if (config_.use_parallel) {
            cv::parallel_for_(cv::Range(0, width), [&](const cv::Range& range) {
                for (int x = range.start; x < range.end; ++x) {
                    process_column(x);
                }
            });
        } else {
            for (int x = 0; x < width; ++x) {
                process_column(x);
            }
        }

        return true;
    }

    /**
     * @brief Медіанна 1D-фільтрація профілю для усунення одиночних імпульсних викидів (noise blips).
     */
    static void filter_outliers_median(std::vector<ProfilePoint>& profile, int window_size = 5) {
        const int size = static_cast<int>(profile.size());
        if (size < window_size || window_size < 3) {
            return;
        }

        const int half = window_size / 2;
        std::vector<float> temp_vals;
        temp_vals.reserve(window_size);

        std::vector<ProfilePoint> original = profile;

        for (int i = half; i < size - half; ++i) {
            if (!original[i].is_valid) {
                continue;
            }

            temp_vals.clear();
            for (int k = -half; k <= half; ++k) {
                if (original[i + k].is_valid) {
                    temp_vals.push_back(original[i + k].subpixel_y);
                }
            }

            if (temp_vals.size() >= static_cast<size_t>(half + 1)) {
                std::sort(temp_vals.begin(), temp_vals.end());
                profile[i].subpixel_y = temp_vals[temp_vals.size() / 2];
            }
        }
    }

    /**
     * @brief Розрахунок коефіцієнта заповнення (частка стовпців з валідною лазерною лінією).
     */
    [[nodiscard]] static float compute_coverage_ratio(const std::vector<ProfilePoint>& profile) noexcept {
        if (profile.empty()) {
            return 0.0f;
        }
        size_t valid_count = 0;
        for (const auto& pt : profile) {
            if (pt.is_valid) {
                valid_count++;
            }
        }
        return static_cast<float>(valid_count) / static_cast<float>(profile.size());
    }

private:
    ExtractorConfig config_{};
};

} // namespace vision

#endif // VISION_COG_EXTRACTOR_HPP_\n
