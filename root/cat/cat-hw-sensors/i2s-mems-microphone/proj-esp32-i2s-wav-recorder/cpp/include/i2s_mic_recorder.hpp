#ifndef I2S_MIC_RECORDER_HPP
#define I2S_MIC_RECORDER_HPP

#include <cstdint>
#include <cstddef>
#include <cstdio>
#include <atomic>
#include "wav_header.hpp"

// Підключення апаратно-залежних заголовків ESP32 / FreeRTOS з можливістю крос-компіляції
#if defined(ESP_PLATFORM) || defined(ARDUINO_ARCH_ESP32)
#include <driver/i2s.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/semphr.h>
#else
// Заглушки типів FreeRTOS та I2S для сумісності із загальним C++ середовищем
typedef void* TaskHandle_t;
typedef void* SemaphoreHandle_t;
typedef int i2s_port_t;
#define I2S_NUM_0 0
#define I2S_NUM_1 1
#endif

/**
 * @brief Перелічення поточних станів диктофона.
 */
enum class RecorderState : uint8_t {
    Uninitialized,  ///< Пристрій не ініціалізовано
    Idle,           ///< Готовий до запису
    Recording,      ///< Триває процес запису PCM-потоку
    Error           ///< Виникла апаратна або файлова помилка
};

/**
 * @brief Статуси виконання операцій диктофона.
 */
enum class RecorderStatus : uint8_t {
    Ok,                      ///< Операція успішна
    AlreadyRecording,        ///< Запис уже заповнений та активний
    NotRecording,            ///< Диктофон не перебуває в режимі запису
    InitializationFailed,    ///< Помилка ініціалізації шини I2S
    FileOpenError,           ///< Не вдалося відкрити файл для запису
    FileWriteError,          ///< Помилка під час запису блоку даних у файл
    MemoryAllocationFailed,  ///< Недостатньо пам'яті для DMA/Ping-Pong буферів
    I2sReadTimeout           ///< Таймаут зчитування з шини I2S
};

/**
 * @brief Структура конфігурації I2S-периферії та аудіопараметрів для ESP32.
 */
struct I2SConfig {
    int bclk_pin{14};            ///< Вивід BCLK (Bit Clock)
    int ws_pin{15};              ///< Вивід WS / LRCLK (Word Select)
    int data_in_pin{32};         ///< Вивід SD / DOUT (Serial Data In)
    uint32_t sample_rate{16000};  ///< Частота дискретизації у Гц
    uint16_t bits_per_sample{16}; ///< Розрядність аудіосемплів (16 або 32 біти)
    uint8_t i2s_port{0};         ///< Номер апаратного порту I2S (0 або 1)
    size_t buffer_size{1024};    ///< Розмір одного одиничного буфера в байтах
};

/**
 * @brief RAII-обгортка для безпечного виділення та автоматичного звільнення
 * подвійного аудіобуфера (Ping-Pong buffers) в оперативній пам'яті (DRAM/PSRAM).
 */
class AudioBufferGuard {
public:
    explicit AudioBufferGuard(size_t single_buffer_bytes = 1024) noexcept;
    ~AudioBufferGuard();

    // Забороняємо копіювання для запобігання подвійному звільненню пам'яті
    AudioBufferGuard(const AudioBufferGuard&) = delete;
    AudioBufferGuard& operator=(const AudioBufferGuard&) = delete;

    // Переміщення ресурсу дозволено
    AudioBufferGuard(AudioBufferGuard&& other) noexcept;
    AudioBufferGuard& operator=(AudioBufferGuard&& other) noexcept;

    /**
     * @brief Виділяє пам'ять під два буфери (Ping-Pong).
     * @return true у разі успішного виділення обох блоків.
     */
    bool allocate() noexcept;

    /**
     * @brief Безпечно звільняє виділену пам'ять.
     */
    void release() noexcept;

    uint8_t* getBufferA() noexcept { return buffer_a_; }
    uint8_t* getBufferB() noexcept { return buffer_b_; }
    size_t getSingleBufferSize() const noexcept { return single_buffer_bytes_; }
    bool isAllocated() const noexcept { return buffer_a_ != nullptr && buffer_b_ != nullptr; }

private:
    uint8_t* buffer_a_{nullptr};
    uint8_t* buffer_b_{nullptr};
    size_t single_buffer_bytes_{0};
};

/**
 * @brief Клас I2SMicRecorder для керування I2S MEMS-мікрофоном та асинхронного запису WAV-файлів.
 * Інкапсулює налаштування периферії ESP32, фоновий FreeRTOS-потік зчитування DMA-буферів,
 * формування та перезапис заголовків WAV на накопичувачах SD/SPIFFS.
 */
class I2SMicRecorder {
public:
    explicit I2SMicRecorder(const I2SConfig& config = I2SConfig());
    ~I2SMicRecorder();

    // Забороняємо копіювання об'єкта драйвера
    I2SMicRecorder(const I2SMicRecorder&) = delete;
    I2SMicRecorder& operator=(const I2SMicRecorder&) = delete;

    /**
     * @brief Ініціалізує апаратний драйвер I2S мікроконтролера ESP32.
     */
    RecorderStatus init();

    /**
     * @brief Запускає процес запису PCM-аудіо у WAV-файл.
     * @param file_path Шлях до цільового файлу у файловій системі (наприклад, "/spiffs/rec.wav").
     */
    RecorderStatus startRecording(const char* file_path);

    /**
     * @brief Зупиняє процес запису, фіналізує заголовок WAV та закриває файл.
     */
    RecorderStatus stopRecording();

    RecorderState getState() const noexcept { return state_; }
    bool isRecording() const noexcept { return state_ == RecorderState::Recording; }
    uint32_t getBytesRecorded() const noexcept { return total_bytes_recorded_; }
    const I2SConfig& getConfig() const noexcept { return config_; }

private:
    I2SConfig config_;
    RecorderState state_{RecorderState::Uninitialized};
    AudioBufferGuard buffer_guard_;

    std::FILE* file_{nullptr};
    uint32_t total_bytes_recorded_{0};
    std::atomic<bool> recording_active_{false};

    TaskHandle_t task_handle_{nullptr};
    SemaphoreHandle_t task_completion_sem_{nullptr};

    // Статичний метод-точка входу для потоку FreeRTOS
    static void recorderTaskEntry(void* arg);

    // Основний цикл фонової задачі читання I2S та запису у файл
    void recorderTaskLoop();

    RecorderStatus writeInitialWavHeader();
    RecorderStatus finalizeWavHeader();
};

#endif // I2S_MIC_RECORDER_HPP
