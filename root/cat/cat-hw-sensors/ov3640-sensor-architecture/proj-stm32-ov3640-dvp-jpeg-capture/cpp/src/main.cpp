#include "ov3640_camera.hpp"
#include <iostream>
#include <vector>

// Симуляція генерації синтетичного JPEG-кадру з маркерами SOI та EOI
std::vector<uint8_t> generate_mock_jpeg_frame() {
    std::vector<uint8_t> mock_data;
    // Маркер SOI (Start of Image)
    mock_data.push_back(0xFF);
    mock_data.push_back(0xD8);

    // Заповнення контентом (симуляція стисненого зображення)
    for (int i = 0; i < 512; ++i) {
        mock_data.push_back(static_cast<uint8_t>(i & 0xFF));
    }

    // Маркер EOI (End of Image)
    mock_data.push_back(0xFF);
    mock_data.push_back(0xD9);

    return mock_data;
}

int main() {
    std::cout << "Ініціалізація системи захоплення зображень OV3640...\n";

    // Створення екземпляра фасаду камери OV3640 з I2C адресою 0x3C
    camera::Ov3640Camera camera(0x3C);

    if (!camera.init()) {
        std::cerr << "Помилка: Не вдалося ініціалізувати камеру OV3640 (перевірте PID/VER).\n";
        return 1;
    }
    std::cout << "Сенсор OV3640 успішно ідентифіковано (PID/VER: 0x3640).\n";

    // Конфігурація параметрів зйомки: роздільність Full HD та формат JPEG
    camera.set_resolution(camera::Resolution::FHD_1920x1080);
    camera.set_format(camera::ImageFormat::JPEG);
    camera.set_auto_exposure(true);
    camera.set_auto_white_balance(true);

    // Реєстрація асинхронного колбека готовності кадру
    uint32_t received_frames_count = 0;
    camera.on_frame_ready([&received_frames_count](const camera::FrameBuffer& frame) {
        received_frames_count++;
        std::cout << "[УСПІХ] Отримано новий кадр #" << frame.sequence_id
                  << " | Розмір: " << frame.size << " байтів"
                  << " | Формат: " << (frame.format == camera::ImageFormat::JPEG ? "JPEG" : "YUV422")
                  << " | Валідність: " << (frame.is_valid ? "OK" : "ERROR") << "\n";
    });

    // Запуск захоплення потоку DCMI + DMA
    if (!camera.start()) {
        std::cerr << "Помилка: Не вдалося запустити захоплення DCMI DMA.\n";
        return 1;
    }
    std::cout << "Потокове захоплення відео успішно запущено.\n";

    // Емуляція роботи DMA: створення синтетичного JPEG кадру та передача у парсер
    std::vector<uint8_t> mock_frame = generate_mock_jpeg_frame();

    // Симуляція приходу даних від DMA через обробник переривання
    camera.inject_dma_data(mock_frame.data(), mock_frame.size(), 0);

    std::cout << "Всього успішно оброблено кадрів: " << received_frames_count << "\n";

    // Завершення роботи та деактивація периферії
    camera.stop();
    std::cout << "Захоплення відеозапису завершено.\n";

    return 0;
}
