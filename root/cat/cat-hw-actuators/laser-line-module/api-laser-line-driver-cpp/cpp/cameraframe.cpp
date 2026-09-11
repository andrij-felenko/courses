// production_profilometer_pipeline.cpp
#include "laser_line_driver.hpp"
#include <cstdio>
#include <thread>
#include <chrono>

// Імітація інтерфейсу камери машинного зору
struct CameraFrame {
    uint32_t frame_id;
    const uint8_t* pixel_buffer;
    bool is_valid;
};

// Виробничий конвеєр оптичного профілометра
class ProfilometerEngine {
public:
    explicit ProfilometerEngine(Laser::LaserLineDriver& laser)
        : laser_(laser), running_(false), processed_frames_(0) {}

    void run_scan_loop(uint32_t total_profiles_to_acquire) {
        running_ = true;

        // Крок 1: Налаштування оптичних параметрів відповідно до матеріалу деталі
        // 45% яскравості (ШІМ 30 кГц) для матового алюмінію, тривалість стробу 1500 мкс
        constexpr uint32_t STROBE_EXPOSURE_US = 1500;
        constexpr float OPTIMAL_BRIGHTNESS    = 45.0f;

        laser_.set_optical_parameters(OPTIMAL_BRIGHTNESS);

        printf("[Конвеєр] Старт сканування: експозиція %u мкс, потужність %.1f%%\n",
               STROBE_EXPOSURE_US, OPTIMAL_BRIGHTNESS);

        for (uint32_t i = 0; i < total_profiles_to_acquire && running_; ++i) {
            // Крок 2: Асинхронний запуск стробу синхронно з відкриттям затвора камери
            if (!laser_.trigger_strobe_async(STROBE_EXPOSURE_US)) {
                if (laser_.is_locked()) {
                    handle_recovery("Запуск неможливий: драйвер у стані FaultLockout!");
                    break;
                }
            }

            // Крок 3: Очікування завершення експозиції та прийому кадру через DMA (неблокуюче)
            CameraFrame frame = capture_frame_dma(STROBE_EXPOSURE_US);

            if (!frame.is_valid) {
                // Збій шини камери: відсутність сигналу готовності кадру
                printf("[УВАГА] Втрачено кадр %u! Не скидаємо watchdog!\n", i);
                // Пропускаємо виклик pet_safety_watchdog() — якщо затримка повториться,
                // сторожовий таймер апаратно знеструмить лазер
                continue;
            }

            // Крок 4: Кадр успішно отримано — підтверджуємо життєздатність конвеєра
            laser_.pet_safety_watchdog();

            // Крок 5: Обробка лазерного профілю (субпіксельна тріангуляція)
            process_laser_stripe(frame);
            processed_frames_++;
        }

        printf("[Конвеєр] Сканування завершено. Оброблено профілів: %u\n", processed_frames_);
    }

private:
    CameraFrame capture_frame_dma(uint32_t timeout_us) {
        // Симуляція прийому кадру від драйвера сенсора
        std::this_thread::sleep_for(std::chrono::microseconds(timeout_us));
        return CameraFrame{processed_frames_ + 1, nullptr, true};
    }

    void process_laser_stripe(const CameraFrame& frame) {
        // Тут виконується субпіксельне визначення піка інтенсивності лазерної лінії
    }

    void handle_recovery(const char* reason) {
        printf("[Аварія] %s Помилка: 0x%X\n", reason, laser_.get_error_code());
        printf("[Відновлення] Виконуємо очищення конвеєра та failsafe_reset()...\n");

        // Очищення черг, перезапуск з'єднання камери
        std::this_thread::sleep_for(std::chrono::milliseconds(50));

        if (laser_.failsafe_reset()) {
            printf("[Відновлення] Драйвер повернуто у робочий стан Ready.\n");
        } else {
            printf("[Критична відмова] Скидання блокування відхилено апаратурою!\n");
        }
    }

    Laser::LaserLineDriver& laser_;
    bool running_;
    uint32_t processed_frames_;
};
