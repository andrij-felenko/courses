#include "i2s_mic_recorder.hpp"
#include <iostream>
#include <chrono>
#include <thread>
#include <cstring>
#include <cmath>

// --- Реалізація AudioBufferGuard ---

AudioBufferGuard::AudioBufferGuard(size_t single_buffer_bytes) noexcept
    : single_buffer_bytes_(single_buffer_bytes) {}

AudioBufferGuard::~AudioBufferGuard() {
    release();
}

AudioBufferGuard::AudioBufferGuard(AudioBufferGuard&& other) noexcept
    : buffer_a_(other.buffer_a_),
      buffer_b_(other.buffer_b_),
      single_buffer_bytes_(other.single_buffer_bytes_) {
    other.buffer_a_ = nullptr;
    other.buffer_b_ = nullptr;
    other.single_buffer_bytes_ = 0;
}

AudioBufferGuard& AudioBufferGuard::operator=(AudioBufferGuard&& other) noexcept {
    if (this != &other) {
        release();
        buffer_a_ = other.buffer_a_;
        buffer_b_ = other.buffer_b_;
        single_buffer_bytes_ = other.single_buffer_bytes_;

        other.buffer_a_ = nullptr;
        other.buffer_b_ = nullptr;
        other.single_buffer_bytes_ = 0;
    }
    return *this;
}

bool AudioBufferGuard::allocate() noexcept {
    release();
    if (single_buffer_bytes_ == 0) {
        return false;
    }

#if defined(ESP_PLATFORM)
    // У середовищі ESP32 використовуємо DRAM з підтримкою DMA
    buffer_a_ = static_cast<uint8_t*>(heap_caps_malloc(single_buffer_bytes_, MALLOC_CAP_DMA | MALLOC_CAP_8BIT));
    buffer_b_ = static_cast<uint8_t*>(heap_caps_malloc(single_buffer_bytes_, MALLOC_CAP_DMA | MALLOC_CAP_8BIT));
#else
    buffer_a_ = new (std::nothrow) uint8_t[single_buffer_bytes_];
    buffer_b_ = new (std::nothrow) uint8_t[single_buffer_bytes_];
#endif

    if (!buffer_a_ || !buffer_b_) {
        release();
        return false;
    }

    std::memset(buffer_a_, 0, single_buffer_bytes_);
    std::memset(buffer_b_, 0, single_buffer_bytes_);
    return true;
}

void AudioBufferGuard::release() noexcept {
    if (buffer_a_) {
#if defined(ESP_PLATFORM)
        heap_caps_free(buffer_a_);
#else
        delete[] buffer_a_;
#endif
        buffer_a_ = nullptr;
    }

    if (buffer_b_) {
#if defined(ESP_PLATFORM)
        heap_caps_free(buffer_b_);
#else
        delete[] buffer_b_;
#endif
        buffer_b_ = nullptr;
    }
}

// --- Реалізація I2SMicRecorder ---

I2SMicRecorder::I2SMicRecorder(const I2SConfig& config)
    : config_(config), buffer_guard_(config.buffer_size) {}

I2SMicRecorder::~I2SMicRecorder() {
    if (isRecording()) {
        stopRecording();
    }

#if defined(ESP_PLATFORM) || defined(ARDUINO_ARCH_ESP32)
    i2s_driver_uninstall(static_cast<i2s_port_t>(config_.i2s_port));
    if (task_completion_sem_) {
        vSemaphoreDelete(static_cast<SemaphoreHandle_t>(task_completion_sem_));
    }
#endif
}

RecorderStatus I2SMicRecorder::init() {
    if (state_ == RecorderState::Recording) {
        return RecorderStatus::AlreadyRecording;
    }

#if defined(ESP_PLATFORM) || defined(ARDUINO_ARCH_ESP32)
    i2s_config_t i2s_config = {
        .mode = static_cast<i2s_mode_t>(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = config_.sample_rate,
        .bits_per_sample = static_cast<i2s_bits_per_sample_t>(config_.bits_per_sample),
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT, // Стандарт для INMP441 при L/R=GND
        .communication_format = static_cast<i2s_comm_format_t>(I2S_COMM_FORMAT_STAND_I2S),
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,
        .dma_buf_len = static_cast<int>(config_.buffer_size / 4),
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    i2s_pin_config_t pin_config = {
        .bck_io_num = config_.bclk_pin,
        .ws_io_num = config_.ws_pin,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = config_.data_in_pin
    };

    i2s_port_t port = static_cast<i2s_port_t>(config_.i2s_port);
    if (i2s_driver_install(port, &i2s_config, 0, NULL) != ESP_OK) {
        state_ = RecorderState::Error;
        return RecorderStatus::InitializationFailed;
    }

    if (i2s_set_pin(port, &pin_config) != ESP_OK) {
        i2s_driver_uninstall(port);
        state_ = RecorderState::Error;
        return RecorderStatus::InitializationFailed;
    }

    if (!task_completion_sem_) {
        task_completion_sem_ = xSemaphoreCreateBinary();
    }
#endif

    state_ = RecorderState::Idle;
    return RecorderStatus::Ok;
}

RecorderStatus I2SMicRecorder::startRecording(const char* file_path) {
    if (state_ == RecorderState::Recording) {
        return RecorderStatus::AlreadyRecording;
    }

    if (!file_path || std::strlen(file_path) == 0) {
        return RecorderStatus::FileOpenError;
    }

    if (!buffer_guard_.allocate()) {
        state_ = RecorderState::Error;
        return RecorderStatus::MemoryAllocationFailed;
    }

    file_ = std::fopen(file_path, "wb");
    if (!file_) {
        buffer_guard_.release();
        state_ = RecorderState::Error;
        return RecorderStatus::FileOpenError;
    }

    total_bytes_recorded_ = 0;
    RecorderStatus status = writeInitialWavHeader();
    if (status != RecorderStatus::Ok) {
        std::fclose(file_);
        file_ = nullptr;
        buffer_guard_.release();
        state_ = RecorderState::Error;
        return status;
    }

    recording_active_ = true;
    state_ = RecorderState::Recording;

#if defined(ESP_PLATFORM) || defined(ARDUINO_ARCH_ESP32)
    BaseType_t res = xTaskCreatePinnedToCore(
        recorderTaskEntry,
        "i2s_recorder_task",
        4096,
        this,
        5,
        reinterpret_cast<TaskHandle_t*>(&task_handle_),
        1
    );

    if (res != pdPASS) {
        recording_active_ = false;
        state_ = RecorderState::Error;
        std::fclose(file_);
        file_ = nullptr;
        buffer_guard_.release();
        return RecorderStatus::InitializationFailed;
    }
#else
    // Імітація запуску асинхронного фонового потоку на хості
    std::thread t(&I2SMicRecorder::recorderTaskLoop, this);
    t.detach();
#endif

    return RecorderStatus::Ok;
}

RecorderStatus I2SMicRecorder::stopRecording() {
    if (state_ != RecorderState::Recording) {
        return RecorderStatus::NotRecording;
    }

    recording_active_ = false;

#if defined(ESP_PLATFORM) || defined(ARDUINO_ARCH_ESP32)
    if (task_completion_sem_) {
        xSemaphoreTake(static_cast<SemaphoreHandle_t>(task_completion_sem_), pdMS_TO_TICKS(3000));
    }
#else
    // Даємо фоновому хостовому потоку завершити поточний ітераційний цикл
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
#endif

    RecorderStatus status = finalizeWavHeader();

    if (file_) {
        std::fclose(file_);
        file_ = nullptr;
    }

    buffer_guard_.release();
    state_ = (RecorderStatus::Ok == status) ? RecorderState::Idle : RecorderState::Error;
    return status;
}

void I2SMicRecorder::recorderTaskEntry(void* arg) {
    auto* recorder = static_cast<I2SMicRecorder*>(arg);
    if (recorder) {
        recorder->recorderTaskLoop();
    }
#if defined(ESP_PLATFORM) || defined(ARDUINO_ARCH_ESP32)
    vTaskDelete(NULL);
#endif
}

void I2SMicRecorder::recorderTaskLoop() {
    uint8_t* buffers[2] = { buffer_guard_.getBufferA(), buffer_guard_.getBufferB() };
    size_t active_idx = 0;
    size_t buf_size = buffer_guard_.getSingleBufferSize();

    while (recording_active_) {
        uint8_t* current_buf = buffers[active_idx];
        size_t bytes_read = 0;

#if defined(ESP_PLATFORM) || defined(ARDUINO_ARCH_ESP32)
        i2s_port_t port = static_cast<i2s_port_t>(config_.i2s_port);
        esp_err_t res = i2s_read(port, current_buf, buf_size, &bytes_read, pdMS_TO_TICKS(100));
        if (res != ESP_OK || bytes_read == 0) {
            continue;
        }
#else
        // Емуляція зчитування PCM-семплів синусоїди 1 кГц для тестування без заліза
        bytes_read = buf_size;
        static float phase = 0.0f;
        int16_t* pcm_ptr = reinterpret_cast<int16_t*>(current_buf);
        size_t samples = bytes_read / sizeof(int16_t);
        for (size_t i = 0; i < samples; ++i) {
            pcm_ptr[i] = static_cast<int16_t>(8000.0f * std::sin(phase));
            phase += 2.0f * 3.14159265f * 1000.0f / static_cast<float>(config_.sample_rate);
            if (phase >= 2.0f * 3.14159265f) phase -= 2.0f * 3.14159265f;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
#endif

        if (file_ && bytes_read > 0) {
            size_t written = std::fwrite(current_buf, 1, bytes_read, file_);
            if (written != bytes_read) {
                state_ = RecorderState::Error;
                recording_active_ = false;
                break;
            }
            total_bytes_recorded_ += static_cast<uint32_t>(written);
        }

        // Перемикаємо асинхронний Ping-Pong буфер
        active_idx = (active_idx + 1) % 2;
    }

#if defined(ESP_PLATFORM) || defined(ARDUINO_ARCH_ESP32)
    if (task_completion_sem_) {
        xSemaphoreGive(static_cast<SemaphoreHandle_t>(task_completion_sem_));
    }
#endif
}

RecorderStatus I2SMicRecorder::writeInitialWavHeader() {
    if (!file_) {
        return RecorderStatus::FileOpenError;
    }

    WavHeader header = WavHeader::createPcmHeader(
        config_.sample_rate,
        config_.bits_per_sample,
        1, // Моно мікрофон INMP441
        0  // Початковий розмір аудіоданих 0
    );

    std::fseek(file_, 0, SEEK_SET);
    size_t written = std::fwrite(&header, sizeof(WavHeader), 1, file_);
    if (written != 1) {
        return RecorderStatus::FileWriteError;
    }

    std::fflush(file_);
    return RecorderStatus::Ok;
}

RecorderStatus I2SMicRecorder::finalizeWavHeader() {
    if (!file_) {
        return RecorderStatus::FileOpenError;
    }

    WavHeader header = WavHeader::createPcmHeader(
        config_.sample_rate,
        config_.bits_per_sample,
        1,
        total_bytes_recorded_
    );

    if (std::fseek(file_, 0, SEEK_SET) != 0) {
        return RecorderStatus::FileWriteError;
    }

    size_t written = std::fwrite(&header, sizeof(WavHeader), 1, file_);
    if (written != 1) {
        return RecorderStatus::FileWriteError;
    }

    std::fflush(file_);
    return RecorderStatus::Ok;
}
