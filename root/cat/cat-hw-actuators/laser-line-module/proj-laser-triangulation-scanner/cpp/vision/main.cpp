#include <opencv2/opencv.hpp>
#include <iostream>
#include <iomanip>
#include <chrono>
#include <vector>
#include <fstream>
#include <cmath>

/**
 * @brief Генератор синтетичного тестового кадру з лазерною смугою.
 * 
 * Використовується, якщо фізична камера тріангулятора не підключена,
 * що дозволяє запустити та верифікувати алгоритм на будь-якому ПК.
 * Симулює профіль сходинки деталі, гаусів розподіл променя та шум сенсора.
 */
static cv::Mat generate_synthetic_laser_frame(int width, int height, float time_sec) {
    cv::Mat frame(height, width, CV_8UC1, cv::Scalar(16)); // Базовий темновий шум 16 DN

    // Додавання гаусового шуму сенсора
    cv::Mat noise(height, width, CV_8UC1);
    cv::randn(noise, 0, 5);
    cv::add(frame, noise, frame);

    // Геометрія поверхні: хвиляста деталь зі сходинкою в центрі (репрезентація дефекту)
    const float base_y = static_cast<float>(height) * 0.5f;
    const float laser_sigma = 2.2f; // Напівширина лазерного пучка (пікселі)
    const float peak_dn = 220.0f;   // Оптимальна пікова яскравість лінії

    for (int x = 0; x < width; ++x) {
        // Симуляція рельєфу: похила площина + виступ (сходинка) у центральній зоні
        float surface_offset = std::sin(static_cast<float>(x) * 0.015f + time_sec * 2.0f) * 15.0f;
        if (x > width * 0.45 && x < width * 0.65) {
            surface_offset -= 35.0f; // Сходинка завглибшки 35 пікселів
        }

        const float line_center_y = base_y + surface_offset;

        // Лазерний профіль має гаусів розподіл вздовж стовпця
        const int scan_start = std::max(0, static_cast<int>(line_center_y - 12.0f));
        const int scan_end = std::min(height - 1, static_cast<int>(line_center_y + 12.0f));

        for (int y = scan_start; y <= scan_end; ++y) {
            const float dy = static_cast<float>(y) - line_center_y;
            const float gaussian = peak_dn * std::exp(-0.5f * (dy * dy) / (laser_sigma * laser_sigma));
            const int current_val = frame.at<uint8_t>(y, x);
            const int new_val = std::min(255, current_val + static_cast<int>(gaussian));
            frame.at<uint8_t>(y, x) = static_cast<uint8_t>(new_val);
        }
    }

    return frame;
}

/**
 * @brief Візуалізація 1D-профілю поверхні у графічному вікні.
 */
static cv::Mat render_profile_graph(const std::vector<vision::ProfilePoint>& profile,
                                    int graph_width, int graph_height, int img_height) {
    cv::Mat graph(graph_height, graph_width, CV_8UC3, cv::Scalar(30, 32, 36));

    // Малювання координатних ліній сітки
    for (int gy = 40; gy < graph_height; gy += 40) {
        cv::line(graph, cv::Point(0, gy), cv::Point(graph_width, gy), cv::Scalar(50, 54, 62), 1);
    }

    // Відображення знайдених точок висоти поверхні
    cv::Point prev_pt(-1, -1);
    const float scale_x = static_cast<float>(graph_width) / static_cast<float>(profile.size());

    for (size_t x = 0; x < profile.size(); ++x) {
        const auto& pt = profile[x];
        if (!pt.is_valid) {
            prev_pt = cv::Point(-1, -1);
            continue;
        }

        const int gx = static_cast<int>(static_cast<float>(x) * scale_x);
        // Масштабування вертикальної координати у вікно графіка
        const float norm_y = pt.subpixel_y / static_cast<float>(img_height);
        const int gy = static_cast<int>(norm_y * static_cast<float>(graph_height - 20)) + 10;

        const cv::Point curr_pt(gx, gy);
        if (prev_pt.x >= 0) {
            cv::line(graph, prev_pt, curr_pt, cv::Scalar(60, 220, 100), 2, cv::LINE_AA);
        }
        prev_pt = curr_pt;

        // Позначення пересвічених точок помаранчевим
        if (pt.is_saturated) {
            cv::circle(graph, curr_pt, 3, cv::Scalar(40, 140, 255), -1);
        }
    }

    cv::putText(graph, "Профіль висоти поверхні (Z-координата лінії)",
                cv::Point(15, 25), cv::FONT_HERSHEY_SIMPLEX, 0.55, cv::Scalar(220, 220, 220), 1, cv::LINE_AA);

    return graph;
}

/**
 * @brief Збереження реконструйованого профілю лінії у CSV-файл.
 */
static bool export_profile_to_csv(const std::string& filename,
                                  const std::vector<vision::ProfilePoint>& profile) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        return false;
    }

    file << "column_x,subpixel_y,peak_dn,integrated_mass,is_valid,is_saturated\n";
    for (size_t x = 0; x < profile.size(); ++x) {
        const auto& pt = profile[x];
        file << x << ","
             << std::fixed << std::setprecision(4) << (pt.is_valid ? pt.subpixel_y : -1.0f) << ","
             << pt.peak_intensity << ","
             << pt.integrated_mass << ","
             << (pt.is_valid ? 1 : 0) << ","
             << (pt.is_saturated ? 1 : 0) << "\n";
    }
    return true;
}

/**
 * @brief Головна точка входу застосунку відеообробки.
 */
int main(int argc, char** argv) {
    std::cout << "========================================================\n"
              << "  Vision: Субпіксельний екстрактор лазерної лінії (COG) \n"
              << "========================================================\n\n";

    // Спроба відкрити фізичну камеру (індекс 0)
    cv::VideoCapture cap;
    bool using_synthetic = false;

    if (argc > 1) {
        cap.open(argv[1]);
    } else {
        cap.open(0);
    }

    if (!cap.isOpened()) {
        std::cout << "[ІНФО] Фізичну камеру не знайдено. Перехід на вбудований емулятор лазерного сканера...\n";
        using_synthetic = true;
    } else {
        std::cout << "[УСПІХ] Відеопотік камери успішно захоплено!\n";
        cap.set(cv::CAP_PROP_FRAME_WIDTH, 640);
        cap.set(cv::CAP_PROP_FRAME_HEIGHT, 480);
    }

    const int frame_width = 640;
    const int frame_height = 480;

    // Налаштування екстрактора COG
    vision::ExtractorConfig config;
    config.noise_threshold_dn = 35;       // Відсікання фону нижче 35 DN
    config.window_half_width = 4;          // 9-піксельне вікно центрування
    config.min_integrated_mass = 50.0f;    // Поріг валідної енергії смуги
    config.roi_top = 40;                   // Ігнорування крайових артефактів камери
    config.roi_bottom = frame_height - 40;
    config.use_parallel = true;            // Багатопотоковий режим

    vision::LaserCogExtractor extractor(config);
    std::vector<vision::ProfilePoint> profile;

    std::cout << "[ПАРАМЕТРИ] Поріг шуму: " << static_cast<int>(config.noise_threshold_dn)
              << " DN | Напівширина вікна: " << config.window_half_width
              << " px | Зона ROI: [" << config.roi_top << ".." << config.roi_bottom << "]\n";
    std::cout << "[КЕРУВАННЯ] Натисніть 'q'/'ESC' для виходу, 's' для запису профілю в CSV, '+/-' зміна порогу\n\n";

    auto start_time = std::chrono::steady_clock::now();
    int frame_count = 0;
    float current_fps = 0.0f;
    float avg_latency_us = 0.0f;

    while (true) {
        cv::Mat raw_frame;
        const auto frame_start = std::chrono::steady_clock::now();
        const float time_sec = std::chrono::duration<float>(frame_start - start_time).count();

        if (using_synthetic) {
            raw_frame = generate_synthetic_laser_frame(frame_width, frame_height, time_sec);
        } else {
            cap >> raw_frame;
            if (raw_frame.empty()) {
                std::cerr << "[ПОПЕРЕДЖЕННЯ] Порожній кадр відеопотоку.\n";
                break;
            }
        }

        // Конвертація в градації сірого за потреби
        cv::Mat gray_frame;
        if (raw_frame.channels() == 3) {
            cv::cvtColor(raw_frame, gray_frame, cv::COLOR_BGR2GRAY);
        } else {
            gray_frame = raw_frame;
        }

        // --- ВИМІРЮВАННЯ ЧАСУ СУБПІКСЕЛЬНОЇ ЕКСТРАКЦІЇ ---
        const auto t0 = std::chrono::high_resolution_clock::now();
        extractor.process(gray_frame, profile);
        vision::LaserCogExtractor::filter_outliers_median(profile, 5);
        const auto t1 = std::chrono::high_resolution_clock::now();

        const float latency_us = static_cast<float>(
            std::chrono::duration_cast<std::chrono::microseconds>(t1 - t0).count());
        avg_latency_us = avg_latency_us * 0.9f + latency_us * 0.1f; // Експоненційне згладжування

        // Статистика детекції
        const float coverage = vision::LaserCogExtractor::compute_coverage_ratio(profile) * 100.0f;
        int saturated_cols = 0;
        for (const auto& pt : profile) {
            if (pt.is_saturated) saturated_cols++;
        }

        // --- ВІЗУАЛІЗАЦІЯ РЕЗУЛЬТАТІВ ---
        cv::Mat display;
        cv::cvtColor(gray_frame, display, cv::COLOR_GRAY2BGR);

        // Малювання зони ROI
        cv::line(display, cv::Point(0, config.roi_top), cv::Point(frame_width, config.roi_top),
                 cv::Scalar(60, 60, 180), 1, cv::LINE_DASH);
        cv::line(display, cv::Point(0, config.roi_bottom), cv::Point(frame_width, config.roi_bottom),
                 cv::Scalar(60, 60, 180), 1, cv::LINE_DASH);

        // Накладання реконструйованих субпіксельних точок лінії
        for (size_t x = 0; x < profile.size(); ++x) {
            const auto& pt = profile[x];
            if (pt.is_valid) {
                const int px = static_cast<int>(x);
                const int py = static_cast<int>(std::round(pt.subpixel_y));
                if (pt.is_saturated) {
                    display.at<cv::Vec3b>(py, px) = cv::Vec3b(0, 140, 255); // Помаранчевий (кліпінг)
                } else {
                    display.at<cv::Vec3b>(py, px) = cv::Vec3b(0, 255, 0);   // Зелений (субпіксель)
                }
            }
        }

        // Телеметрія поверх зображення (HUD)
        frame_count++;
        if (frame_count % 15 == 0) {
            const auto now_time = std::chrono::steady_clock::now();
            const float elapsed_sec = std::chrono::duration<float>(now_time - frame_start).count();
            if (elapsed_sec > 0.0f) {
                current_fps = 1.0f / elapsed_sec;
            }
        }

        char hud_buf[128];
        std::snprintf(hud_buf, sizeof(hud_buf), "FPS: %.1f | Latency: %.0f us | Coverage: %.1f%%",
                      current_fps, avg_latency_us, coverage);
        cv::putText(display, hud_buf, cv::Point(15, 25), cv::FONT_HERSHEY_SIMPLEX,
                    0.55, cv::Scalar(0, 255, 255), 1, cv::LINE_AA);

        std::snprintf(hud_buf, sizeof(hud_buf), "Noise Thresh: %d DN | Saturated cols: %d",
                      config.noise_threshold_dn, saturated_cols);
        cv::putText(display, hud_buf, cv::Point(15, frame_height - 15), cv::FONT_HERSHEY_SIMPLEX,
                    0.50, cv::Scalar(200, 200, 200), 1, cv::LINE_AA);

        // Вікно 1D-профілю поверхні
        cv::Mat graph_view = render_profile_graph(profile, frame_width, 160, frame_height);

        // Об'єднання кадру та графіка в єдине інформативне вікно
        cv::Mat combined_view;
        cv::vconcat(display, graph_view, combined_view);

        cv::imshow("Лазерний тріангуляційний сканер [Кадр + Профіль Z]", combined_view);

        // Обробка клавіатурних команд (1 мс затримка для обробки черги вікон)
        const int key = cv::waitKey(1);
        if (key == 'q' || key == 'Q' || key == 27) { // ESC або Q
            std::cout << "[ВИХІД] Роботу зупинено користувачем.\n";
            break;
        } else if (key == 's' || key == 'S') {
            const std::string csv_name = "laser_profile_snapshot.csv";
            if (export_profile_to_csv(csv_name, profile)) {
                std::cout << "[ЕКСПОРТ] Профіль успішно збережено у файл: " << csv_name << "\n";
            }
        } else if (key == '+' || key == '=') {
            if (config.noise_threshold_dn < 200) {
                config.noise_threshold_dn += 5;
                extractor.set_config(config);
                std::cout << "[НАЛАШТУВАННЯ] Поріг шуму збільшено до: " << static_cast<int>(config.noise_threshold_dn) << " DN\n";
            }
        } else if (key == '-' || key == '_') {
            if (config.noise_threshold_dn > 10) {
                config.noise_threshold_dn -= 5;
                extractor.set_config(config);
                std::cout << "[НАЛАШТУВАННЯ] Поріг шуму зменшено до: " << static_cast<int>(config.noise_threshold_dn) << " DN\n";
            }
        }

        // Для синтетичного режиму обмежуємо темп до ~60 кадрів/с
        if (using_synthetic) {
            std::this_thread::sleep_for(std::chrono::milliseconds(16));
        }
    }

    cv::destroyAllWindows();
    return 0;
}\n
