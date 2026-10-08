#include <iostream>
#include <chrono>
#include <thread>
#include <cstdio>
#include "i2s_mic_recorder.hpp"
#include "wav_header.hpp"

// Допоміжна функція перевірки записаного файлу WAV
static bool verifyWavFile(const char* file_path, uint32_t expected_min_bytes) {
    std::FILE* f = std::fopen(file_path, "rb");
    if (!f) {
        std::cerr << "[ERROR] Не вдалося відкрити файл для перевірки: " << file_path << "\n";
        return false;
    }

    WavHeader header;
    size_t read_bytes = std::fread(&header, 1, sizeof(WavHeader), f);
    std::fclose(f);

    if (read_bytes != sizeof(WavHeader)) {
        std::cerr << "[ERROR] Файл занадто малий для WAV заголовка!\n";
        return false;
    }

    if (!header.isValid()) {
        std::cerr << "[ERROR] Заголовок WAV файлу сигнатурно невалідний!\n";
        return false;
    }

    std::cout << "\n=== Вміст оновленого WAV Заголовка ===\n"
              << "  - Сигнатура RIFF: " << std::string(header.riff_id, 4) << "\n"
              << "  - Сигнатура WAVE: " << std::string(header.wave_id, 4) << "\n"
              << "  - Частота дискретизації: " << header.sample_rate << " Гц\n"
              << "  - Кількість каналів: " << header.num_channels << " (Моно)\n"
              << "  - Розрядність: " << header.bits_per_sample << " біт\n"
              << "  - Обсяг PCM аудіоданих: " << header.data_bytes << " байтів\n"
              << "  - Загальний розмір файлу RIFF: " << header.overall_size + 8 << " байтів\n"
              << "========================================\n\n";

    if (header.data_bytes < expected_min_bytes) {
        std::cerr << "[ERROR] Кількість записаних аудіоданих менша за очікуваний мінімум!\n";
        return false;
    }

    return true;
}

int main() {
    std::cout << "--- Запуск цифрового диктофона ESP32 (I2S MEMS Мікрофон INMP441) ---\n\n";

    // 1. Конфігурація шини I2S під мікрофон INMP441
    I2SConfig config;
    config.bclk_pin = 14;           // SCK / BCLK pin
    config.ws_pin = 15;             // WS / LRCLK pin
    config.data_in_pin = 32;        // SD / SDATA pin
    config.sample_rate = 16000;     // 16 кГц (стандарт мовного діапазону)
    config.bits_per_sample = 16;    // 16 біт PCM
    config.i2s_port = 0;            // Порт I2S_NUM_0
    config.buffer_size = 1024;      // 1 КБ розмір одного буфера

    std::cout << "[INFO] Конфігурація I2S:"
              << " BCLK=" << config.bclk_pin
              << ", WS=" << config.ws_pin
              << ", SD=" << config.data_in_pin
              << ", SampleRate=" << config.sample_rate << " Гц\n";

    // 2. Ініціалізація класу-реєстратора
    I2SMicRecorder recorder(config);
    RecorderStatus status = recorder.init();
    if (status != RecorderStatus::Ok) {
        std::cerr << "[ERROR] Помилка ініціалізації периферії I2S!\n";
        return 1;
    }
    std::cout << "[SUCCESS] Шину I2S успішно налаштовано.\n";

    // 3. Старт запису у файл
    const char* output_file = "test_record.wav";
    std::cout << "[INFO] Запуск фонового асинхронного запису у файл: " << output_file << "...\n";
    status = recorder.startRecording(output_file);
    if (status != RecorderStatus::Ok) {
        std::cerr << "[ERROR] Не вдалося розпочати запис! Код помилки: " 
                  << static_cast<int>(status) << "\n";
        return 1;
    }

    // 4. Емуляція активного запису протягом 3 секунд з індикацією прогресу
    constexpr int record_duration_ms = 3000;
    constexpr int step_ms = 500;
    int elapsed_ms = 0;

    while (elapsed_ms < record_duration_ms) {
        std::this_thread::sleep_for(std::chrono::milliseconds(step_ms));
        elapsed_ms += step_ms;
        std::cout << "[RECORDING] Час: " << (elapsed_ms / 1000.0f) << " с | Записано байтів: "
                  << recorder.getBytesRecorded() << "\n";
    }

    // 5. Зупинка запису та фіналізація файлу
    std::cout << "[INFO] Зупинка запису та закриття файлу...\n";
    status = recorder.stopRecording();
    if (status != RecorderStatus::Ok) {
        std::cerr << "[ERROR] Помилка при зупинці запису!\n";
        return 1;
    }

    std::cout << "[SUCCESS] Запис завершено. Загалом накопичено: " 
              << recorder.getBytesRecorded() << " байтів аудіоданих.\n";

    // 6. Перевірка та аналіз згенерованого WAV файлу
    if (verifyWavFile(output_file, 1000)) {
        std::cout << "[SUCCESS] Файл WAV успішно збережено та валідовано!\n";
    } else {
        std::cerr << "[ERROR] Перевірка файлу WAV завершилася невдало!\n";
        return 1;
    }

    // Видаляємо тестовий файл після успішної демонстрації
    std::remove(output_file);
    std::cout << "--- Програму успішно завершено ---\n";
    return 0;
}
