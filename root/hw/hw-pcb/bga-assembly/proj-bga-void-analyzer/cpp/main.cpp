#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <cmath>
#include <numeric>
#include <numbers>
#include <iomanip>
#include <span>
#include <expected>
#include <algorithm>

namespace bga::inspection {

enum class IpcClass : uint8_t {
    Class1 = 1, // Споживча електроніка
    Class2 = 2, // Промислові системи
    Class3 = 3  // Високонадійна / Автомобільна / Аерокосмічна
};

enum class DefectType {
    None,
    ExcessiveTotalVoid,
    ExcessiveSingleVoid,
    InterfacialVoid,
    ContourDeformationHiP,
    SolderBridging
};

struct Point2D {
    double x{0.0};
    double y{0.0};
};

struct VoidMetric {
    Point2D center{};
    double area_px{0.0};
    bool is_interfacial{false};
};

struct BallInspectionResult {
    uint32_t id{0};
    Point2D center{};
    double radius_px{0.0};
    double area_px{0.0};
    double circularity{0.0};
    
    std::vector<VoidMetric> detected_voids{};
    double total_void_percent{0.0};
    double max_single_void_percent{0.0};
    double interfacial_void_percent{0.0};
    
    DefectType defect{DefectType::None};
    [[nodiscard]] constexpr bool is_pass() const noexcept {
        return defect == DefectType::None;
    }
};

struct InspectionSummary {
    size_t total_joints{0};
    size_t passed_joints{0};
    size_t failed_joints{0};
    double mean_void_percent{0.0};
    double peak_void_percent{0.0};
    bool overall_board_accepted{false};
};

class GrayscaleFrame {
private:
    int width_{0};
    int height_{0};
    std::vector<uint8_t> buffer_{};

public:
    GrayscaleFrame(int width, int height, uint8_t fill_val = 0)
        : width_(width), height_(height), buffer_(static_cast<size_t>(width * height), fill_val) {}

    [[nodiscard]] constexpr int width() const noexcept { return width_; }
    [[nodiscard]] constexpr int height() const noexcept { return height_; }
    [[nodiscard]] std::span<const uint8_t> data() const noexcept { return buffer_; }
    [[nodiscard]] std::span<uint8_t> mutable_data() noexcept { return buffer_; }

    [[nodiscard]] uint8_t get(int x, int y) const noexcept {
        if (x < 0 || x >= width_ || y < 0 || y >= height_) return 0;
        return buffer_[static_cast<size_t>(y * width_ + x)];
    }

    void set(int x, int y, uint8_t val) noexcept {
        if (x >= 0 && x < width_ && y >= 0 && y < height_) {
            buffer_[static_cast<size_t>(y * width_ + x)] = val;
        }
    }
};

class BgaVoidAnalyzer {
public:
    static void generate_synthetic_scene(GrayscaleFrame& frame, int cols, int rows, double pitch, double radius) {
        // Тло рентгенівського шуму
        for (int y = 0; y < frame.height(); ++y) {
            for (int x = 0; x < frame.width(); ++x) {
                const int noise = (rand() % 11) - 5;
                frame.set(x, y, static_cast<uint8_t>(std::clamp(210 + noise, 0, 255)));
            }
        }

        const double start_x = (frame.width() - (cols - 1) * pitch) / 2.0;
        const double start_y = (frame.height() - (rows - 1) * pitch) / 2.0;

        int ball_count = 0;
        for (int r = 0; r < rows; ++r) {
            for (int c = 0; c < cols; ++c) {
                const double cx = start_x + c * pitch;
                const double cy = start_y + r * pitch;

                // Малюємо кульку BGA
                for (int y = static_cast<int>(cy - radius - 2); y <= static_cast<int>(cy + radius + 2); ++y) {
                    for (int x = static_cast<int>(cx - radius - 2); x <= static_cast<int>(cx + radius + 2); ++x) {
                        const double dist = std::hypot(x - cx, y - cy);
                        if (dist <= radius) {
                            const double depth = std::sqrt(1.0 - (dist / radius) * (dist / radius));
                            const int val = static_cast<int>(110 - 70 * depth + (rand() % 7 - 3));
                            frame.set(x, y, static_cast<uint8_t>(std::clamp(val, 0, 255)));
                        }
                    }
                }

                // Впровадження контрольних дефектів
                if (ball_count == 0) {
                    // Нормальна пористість 7%
                    const double vr = radius * 0.26;
                    draw_void(frame, cx, cy, vr);
                } else if (ball_count == 1) {
                    // Критична пористість 26%
                    const double vr = radius * 0.51;
                    draw_void(frame, cx, cy, vr);
                } else if (ball_count == 2) {
                    // Крайова каверна на контактному кільці
                    const double vx = cx + radius * 0.74;
                    const double vy = cy + radius * 0.42;
                    draw_void(frame, vx, vy, radius * 0.21);
                }
                ball_count++;
            }
        }
    }

    [[nodiscard]] static std::vector<BallInspectionResult> analyze(
        const GrayscaleFrame& frame, 
        IpcClass standard_class
    ) {
        std::vector<BallInspectionResult> results{};
        const int otsu_th = compute_otsu(frame);

        std::vector<int> labels(static_cast<size_t>(frame.width() * frame.height()), 0);
        int current_label = 0;

        for (int y = 5; y < frame.height() - 5; ++y) {
            for (int x = 5; x < frame.width() - 5; ++x) {
                const int idx = y * frame.width() + x;
                if (frame.get(x, y) <= otsu_th && labels[static_cast<size_t>(idx)] == 0) {
                    current_label++;
                    
                    std::vector<Point2D> component_pts{};
                    std::vector<Point2D> queue{ {static_cast<double>(x), static_cast<double>(y)} };
                    labels[static_cast<size_t>(idx)] = current_label;
                    
                    size_t head = 0;
                    int perimeter = 0;
                    double sum_x = 0.0, sum_y = 0.0;

                    while (head < queue.size()) {
                        const auto [cx, cy] = queue[head++];
                        const int ix = static_cast<int>(cx);
                        const int iy = static_cast<int>(cy);
                        sum_x += cx; sum_y += cy;

                        constexpr int dx[4] = {1, -1, 0, 0};
                        constexpr int dy[4] = {0, 0, 1, -1};
                        bool is_border = false;

                        for (int k = 0; k < 4; ++k) {
                            const int nx = ix + dx[k];
                            const int ny = iy + dy[k];
                            if (nx >= 0 && nx < frame.width() && ny >= 0 && ny < frame.height()) {
                                const size_t n_idx = static_cast<size_t>(ny * frame.width() + nx);
                                if (frame.get(nx, ny) <= otsu_th) {
                                    if (labels[n_idx] == 0) {
                                        labels[n_idx] = current_label;
                                        queue.push_back({static_cast<double>(nx), static_cast<double>(ny)});
                                    }
                                } else {
                                    is_border = true;
                                }
                            } else {
                                is_border = true;
                            }
                        }
                        if (is_border) perimeter++;
                    }

                    const double area = static_cast<double>(queue.size());
                    if (area >= 150.0) {
                        BallInspectionResult ball{};
                        ball.id = static_cast<uint32_t>(results.size());
                        ball.center = {sum_x / area, sum_y / area};
                        ball.area_px = area;
                        ball.radius_px = std::sqrt(area / std::numbers::pi);
                        ball.circularity = perimeter > 0 
                            ? std::min(1.0, (4.0 * std::numbers::pi * area) / (perimeter * perimeter))
                            : 0.0;

                        // Аналіз пустот
                        const double r_interface = ball.radius_px * 0.85;
                        const int void_th = otsu_th + 35;
                        
                        double total_void_area = 0.0;
                        double interfacial_void_area = 0.0;
                        double interfacial_annulus_area = 0.0;

                        for (int py = static_cast<int>(ball.center.y - ball.radius_px - 2); 
                             py <= static_cast<int>(ball.center.y + ball.radius_px + 2); ++py) {
                            for (int px = static_cast<int>(ball.center.x - ball.radius_px - 2); 
                                 px <= static_cast<int>(ball.center.x + ball.radius_px + 2); ++px) {
                                const double dist = std::hypot(px - ball.center.x, py - ball.center.y);
                                if (dist <= ball.radius_px) {
                                    if (dist >= r_interface) interfacial_annulus_area += 1.0;
                                    if (frame.get(px, py) >= void_th) {
                                        total_void_area += 1.0;
                                        if (dist >= r_interface) interfacial_void_area += 1.0;
                                    }
                                }
                            }
                        }

                        ball.total_void_percent = (total_void_area / ball.area_px) * 100.0;
                        ball.max_single_void_percent = ball.total_void_percent;
                        ball.interfacial_void_percent = interfacial_annulus_area > 0.0 
                            ? (interfacial_void_area / interfacial_annulus_area) * 100.0 
                            : 0.0;

                        classify_joint(ball, standard_class);
                        results.push_back(ball);
                    }
                }
            }
        }

        return results;
    }

private:
    static void draw_void(GrayscaleFrame& frame, double cx, double cy, double r) {
        for (int y = static_cast<int>(cy - r); y <= static_cast<int>(cy + r); ++y) {
            for (int x = static_cast<int>(cx - r); x <= static_cast<int>(cx + r); ++x) {
                if (std::hypot(x - cx, y - cy) <= r) {
                    frame.set(x, y, static_cast<uint8_t>(std::clamp(185 + rand() % 10, 0, 255)));
                }
            }
        }
    }

    [[nodiscard]] static int compute_otsu(const GrayscaleFrame& frame) noexcept {
        int hist[256] = {0};
        for (uint8_t val : frame.data()) hist[val]++;

        const double total = static_cast<double>(frame.width() * frame.height());
        double sum = 0.0;
        for (int i = 0; i < 256; ++i) sum += i * hist[i];

        double sum_b = 0.0;
        int w_b = 0;
        double max_var = 0.0;
        int threshold = 128;

        for (int t = 0; t < 256; ++t) {
            w_b += hist[t];
            if (w_b == 0) continue;
            const int w_f = static_cast<int>(total) - w_b;
            if (w_f == 0) break;

            sum_b += t * hist[t];
            const double m_b = sum_b / w_b;
            const double m_f = (sum - sum_b) / w_f;
            const double var = static_cast<double>(w_b) * w_f * (m_b - m_f) * (m_b - m_f);

            if (var > max_var) {
                max_var = var;
                threshold = t;
            }
        }
        return threshold;
    }

    static void classify_joint(BallInspectionResult& b, IpcClass cls) noexcept {
        double lim_total = 15.0, lim_single = 8.0, lim_inter = 10.0, min_circ = 0.85;
        if (cls == IpcClass::Class1) {
            lim_total = 25.0; lim_single = 15.0; lim_inter = 15.0; min_circ = 0.75;
        } else if (cls == IpcClass::Class2) {
            lim_total = 20.0; lim_single = 10.0; lim_inter = 12.0; min_circ = 0.80;
        }

        if (b.circularity < min_circ) {
            b.defect = DefectType::ContourDeformationHiP;
        } else if (b.total_void_percent > lim_total) {
            b.defect = DefectType::ExcessiveTotalVoid;
        } else if (b.max_single_void_percent > lim_single) {
            b.defect = DefectType::ExcessiveSingleVoid;
        } else if (b.interfacial_void_percent > lim_inter) {
            b.defect = DefectType::InterfacialVoid;
        } else {
            b.defect = DefectType::None;
        }
    }
};

} // namespace bga::inspection

int main() {
    using namespace bga::inspection;

    std::cout << std::string(67, '=') << "\n";
    std::cout << "     C++20 BGA AUTOMATED X-RAY INSPECTION PIPELINE\n";
    std::cout << "     IPC-7095 Class 3 High-Reliability Verification\n";
    std::cout << std::string(67, '=') << "\n\n";

    GrayscaleFrame frame(400, 300);
    BgaVoidAnalyzer::generate_synthetic_scene(frame, 3, 3, 65.0, 22.0);

    const auto results = BgaVoidAnalyzer::analyze(frame, IpcClass::Class3);
    std::cout << "Успішно розпізнано та перевірено кульок BGA: " << results.size() << "\n\n";

    size_t passed = 0;
    double void_sum = 0.0;

    std::cout << std::fixed << std::setprecision(1);
    for (const auto& b : results) {
        void_sum += b.total_void_percent;
        if (b.is_pass()) passed++;

        std::string_view verdict_text = "PASS (Придатний)";
        switch (b.defect) {
            case DefectType::ExcessiveTotalVoid:
                verdict_text = "FAIL (Загальна пористість > 15%)";
                break;
            case DefectType::ExcessiveSingleVoid:
                verdict_text = "FAIL (Одиночна порожнина > 8%)";
                break;
            case DefectType::InterfacialVoid:
                verdict_text = "FAIL (Порожнина в інтерфейсі > 10%)";
                break;
            case DefectType::ContourDeformationHiP:
                verdict_text = "FAIL (Деформація Head-in-Pillow)";
                break;
            default:
                break;
        }

        std::cout << "Кулька #" << std::setw(2) << std::setfill('0') << b.id 
                  << " | Центр: (" << std::setw(5) << b.center.x << ", " << std::setw(5) << b.center.y << ")"
                  << " | R: " << b.radius_px << "px"
                  << " | Круглість: " << b.circularity
                  << " | Пустоти: " << std::setw(4) << b.total_void_percent << "%"
                  << " | " << verdict_text << "\n";
    }

    std::cout << "\n" << std::string(67, '-') << "\n";
    std::cout << "ПІДСУМОК АВТОМАТИЗОВАНОЇ ІНСПЕКЦІЇ:\n";
    std::cout << "Усього кульок у матриці: " << results.size() << "\n";
    std::cout << "Успішно прийнято:        " << passed << "\n";
    std::cout << "Виявлено дефектів:       " << results.size() - passed << "\n";
    std::cout << "Середня пористість:      " << (results.empty() ? 0.0 : void_sum / results.size()) << "%\n";
    std::cout << "ВЕРДИКТ ПЛАТИ:           " << (passed == results.size() ? "ПРИЙНЯТО (PASS)" : "ВІДХИЛЕНО (REJECT)") << "\n";
    std::cout << std::string(67, '-') << "\n";

    return 0;
}
