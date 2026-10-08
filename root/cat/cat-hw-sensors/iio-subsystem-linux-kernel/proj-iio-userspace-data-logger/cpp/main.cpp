#include "iio_device.hpp"
#include <iostream>
#include <fstream>
#include <csignal>
#include <atomic>
#include <iomanip>

namespace {
    std::atomic<bool> g_running{true};

    void signal_handler(int signal) {
        if (signal == SIGINT || signal == SIGTERM) {
            g_running = false;
        }
    }
}

int main(int argc, char* argv[]) {
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    std::string device_name = "mpu6050";
    if (argc > 1) {
        device_name = argv[1];
    }

    std::string csv_filename = "sensor_data.csv";
    if (argc > 2) {
        csv_filename = argv[2];
    }

    std::cout << "[IIO App] Ініціалізація IIO пристрою: " << device_name << std::endl;

    try {
        IioInertialSensor sensor(device_name);

        std::cout << "[IIO App] Конфігурування каналів акселерометра та гіроскопа..." << std::endl;
        sensor.configure_channels();

        std::cout << "[IIO App] Створення кільцевого буфера на 1024 семпли..." << std::endl;
        sensor.create_buffer(1024);

        std::ofstream csv_file(csv_filename);
        if (!csv_file.is_open()) {
            std::cerr << "[IIO App] Помилка відкриття файлу для запису CSV: " << csv_filename << std::endl;
            return 1;
        }

        // Запис заголовка CSV
        csv_file << "timestamp_sec,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z\n";

        FrameRateCalculator fps_calc(500);
        std::size_t total_samples = 0;

        std::cout << "[IIO App] Запуск потокового зчитування даних (натисніть Ctrl+C для зупинки)..." << std::endl;

        while (g_running) {
            std::vector<InertialSample> samples = sensor.read_samples();
            if (samples.empty()) {
                continue;
            }

            for (const auto& s : samples) {
                csv_file << std::fixed << std::setprecision(6)
                         << s.timestamp_sec << ","
                         << s.accel_x << ","
                         << s.accel_y << ","
                         << s.accel_z << ","
                         << s.gyro_x << ","
                         << s.gyro_y << ","
                         << s.gyro_z << "\n";
            }

            total_samples += samples.size();
            fps_calc.update(samples.size());

            if (fps_calc.is_ready()) {
                std::cout << "[IIO App] Всього семплів: " << total_samples
                          << " | Поточна частота: " << std::fixed << std::setprecision(2)
                          << fps_calc.current_fps() << " Гц" << std::endl;
            }
        }

        std::cout << "\n[IIO App] Завершення роботи. Записано семплів: " << total_samples << std::endl;
        std::cout << "[IIO App] Дані збережено у файл: " << csv_filename << std::endl;

    } catch (const std::exception& ex) {
        std::cerr << "[IIO App] Помилка виконання: " << ex.what() << std::endl;
        return 1;
    }

    return 0;
}
