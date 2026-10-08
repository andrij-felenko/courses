#pragma once

#include <Arduino.h>
#include "esp_camera.h"
#include "camera_config.hpp"

/**
 * @class FrameBufferGuard
 * @brief RAII-обгортка довкола вказівника на кадровий буфер camera_fb_t*.
 *
 * Гарантує автоматичне вивільнення кадрового буфера через esp_camera_fb_return()
 * при виході з області видимості, що запобігає витокам пам'яті PSRAM/DRAM.
 */
class FrameBufferGuard {
public:
    /**
     * @brief Конструктор, який приймає сирий вказівник на кадр.
     * @param fb Вказівник на захоплений кадр camera_fb_t*.
     */
    explicit FrameBufferGuard(camera_fb_t* fb = nullptr) noexcept : fb_(fb) {}

    /**
     * @brief Деструктор, що автоматично повертає кадровий буфер драйверу.
     */
    ~FrameBufferGuard() {
        release();
    }

    /* Забороняємо копіювання, щоб уникнути подвійного вивільнення пам'яті */
    FrameBufferGuard(const FrameBufferGuard&) = delete;
    FrameBufferGuard& operator=(const FrameBufferGuard&) = delete;

    /**
     * @brief Конструктор переміщення.
     */
    FrameBufferGuard(FrameBufferGuard&& other) noexcept : fb_(other.fb_) {
        other.fb_ = nullptr;
    }

    /**
     * @brief Оператор присвоєння переміщенням.
     */
    FrameBufferGuard& operator=(FrameBufferGuard&& other) noexcept {
        if (this != &other) {
            release();
            fb_ = other.fb_;
            other.fb_ = nullptr;
        }
        return *this;
    }

    /**
     * @brief Явне вивільнення буфера кадру.
     */
    void release() {
        if (fb_ != nullptr) {
            esp_camera_fb_return(fb_);
            fb_ = nullptr;
        }
    }

    /**
     * @brief Перевірка наявності дійсного кадрового буфера.
     */
    bool isValid() const noexcept {
        return fb_ != nullptr && fb_->buf != nullptr && fb_->len > 0;
    }

    explicit operator bool() const noexcept {
        return isValid();
    }

    /**
     * @brief Отримання сирого вказівника на буфер даних.
     */
    const uint8_t* getBuffer() const noexcept {
        return fb_ ? fb_->buf : nullptr;
    }

    /**
     * @brief Отримання розміру даних кадру в байтах.
     */
    size_t getSize() const noexcept {
        return fb_ ? fb_->len : 0;
    }

    /**
     * @brief Отримання ширини кадру в пікселях.
     */
    size_t getWidth() const noexcept {
        return fb_ ? fb_->width : 0;
    }

    /**
     * @brief Отримання висоти кадру в пікселях.
     */
    size_t getHeight() const noexcept {
        return fb_ ? fb_->height : 0;
    }

    /**
     * @brief Доступ до внутрішньої структури camera_fb_t через оператор стрілки.
     */
    camera_fb_t* operator->() const noexcept {
        return fb_;
    }

    /**
     * @brief Отримання сирого вказівника camera_fb_t*.
     */
    camera_fb_t* get() const noexcept {
        return fb_;
    }

private:
    camera_fb_t* fb_ = nullptr;
};

/**
 * @class EspCamera
 * @brief Об'єктно-орієнтований C++ клас керування драйвером esp32-camera.
 *
 * Відповідає за ініціалізацію камери OV2640, перевірку та конфігурацію PSRAM,
 * захоплення кадрів із поверненням RAII-обгортки FrameBufferGuard, а також
 * налаштування оптик і регістрів сенсора (яскравість, контраст, vflip, hmirror тощо).
 */
class EspCamera {
public:
    /**
     * @brief Конструктор класу EspCamera.
     * @param pin_config Налаштування апаратних виводів DVP/SCCB.
     */
    explicit EspCamera(const CameraPinConfig& pin_config = CameraPinConfig::getAiThinkerConfig());

    /**
     * @brief Деструктор, що деініціалізує драйвер камери при знищенні об'єкта.
     */
    ~EspCamera();

    /**
     * @brief Ініціалізація підсистеми камери.
     * @param frame_size Бажана роздільна здатність кадру.
     * @param pixel_format Бажаний піксельний формат (типово PIXFORMAT_JPEG).
     * @return true у разі успішної ініціалізації, false при помилці.
     */
    bool init(framesize_t frame_size = FRAMESIZE_VGA, pixformat_t pixel_format = PIXFORMAT_JPEG);

    /**
     * @brief Деініціалізація камери та вивільнення апаратних ресурсів.
     */
    void deinit();

    /**
     * @brief Перевірка працездатності та стану ініціалізації камери.
     */
    bool isInitialized() const noexcept { return initialized_; }

    /**
     * @brief Перевірка доступності зовнішньої пам'яті PSRAM.
     */
    bool isPsramAvailable() const noexcept { return psram_available_; }

    /**
     * @brief Захоплення нового кадру з поверненням RAII-обгортки.
     * @return Об'єкт FrameBufferGuard із вказівником на буфер.
     */
    FrameBufferGuard captureFrame();

    /* Динамічні регулювання параметрів сенсора OV2640 */
    bool setBrightness(int level);        ///< Яскравість (-2..2)
    bool setContrast(int level);          ///< Контрастність (-2..2)
    bool setSaturation(int level);        ///< Насиченість (-2..2)
    bool setQuality(int quality);         ///< Якість JPEG (10..63)
    bool setFrameSize(framesize_t size);  ///< Роздільна здатність кадру
    bool setVFlip(bool enable);           ///< Вертикальний розворот
    bool setHMirror(bool enable);         ///< Горизонтальне віддзеркалення
    bool setSpecialEffect(int effect);    ///< Ефекти зображення (0 - вимк, 1 - негатив, 2 - Ч/Б)

private:
    CameraPinConfig pin_config_;
    CameraModeConfig mode_config_;
    bool initialized_ = false;
    bool psram_available_ = false;

    /**
     * @brief Допоміжний метод для отримання структури сенсора.
     */
    sensor_t* getSensor() const;
};
