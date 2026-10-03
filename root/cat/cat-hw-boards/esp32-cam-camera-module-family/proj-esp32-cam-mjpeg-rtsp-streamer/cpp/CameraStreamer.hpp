#ifndef CAMERA_STREAMER_HPP
#define CAMERA_STREAMER_HPP

#include <Arduino.h>
#include "PsramFrameBuffer.hpp"
#include "FlashPwmController.hpp"
#include "MjpegAsyncServer.hpp"

/**
 * @brief Головний клас-оркестратор автономного відеострімера ESP32-CAM.
 * 
 * Об'єднує роботу з кадровими буферами PSRAM, ШІМ-контролером підсвічування спалаху
 * та асинхронним вебсервером MJPEG у єдину узгоджену систему.
 */
class CameraStreamer {
public:
    CameraStreamer()
        : cameraBuffer_(),
          flashController_(),
          server_(cameraBuffer_, flashController_) {}

    ~CameraStreamer() = default;

    CameraStreamer(const CameraStreamer&) = delete;
    CameraStreamer& operator=(const CameraStreamer&) = delete;

    /**
     * @brief Запускає та інтегрує всі модулі системи відеострімера.
     * 
     * @param resolution Бажана роздільна здатність відео (FRAMESIZE_VGA тощо).
     * @param jpegQuality Якість стиснення JPEG (від 10 до 63).
     * @param port Мережевий порт HTTP вебсервера (80).
     * @return true у разі успішного запуску всіх периферійних модулів.
     */
    bool begin(framesize_t resolution = FRAMESIZE_VGA, 
               int jpegQuality = 10, 
               uint16_t port = 80) {
        
        Serial.println(F("[CameraStreamer] Ініціалізація ШІМ-спалаху (GPIO4)..."));
        if (!flashController_.begin(FlashPwmController::DEFAULT_FLASH_PIN)) {
            Serial.println(F("[CameraStreamer] Помилка ініціалізації LEDC для спалаху!"));
            return false;
        }

        Serial.println(F("[CameraStreamer] Ініціалізація камери та PSRAM буферів..."));
        PsramFrameBuffer::PinConfig pins;
        if (!cameraBuffer_.begin(pins, resolution, jpegQuality)) {
            Serial.println(F("[CameraStreamer] Помилка ініціалізації сенсора камери!"));
            return false;
        }

        Serial.printf("[CameraStreamer] PSRAM доступна: %s | Вільний обсяг: %u байт\n", 
                      cameraBuffer_.isPsramAvailable() ? "ТАК" : "НІ", 
                      (unsigned int)cameraBuffer_.getFreePsram());

        Serial.println(F("[CameraStreamer] Запуск асинхронного MJPEG HTTP-сервера..."));
        if (!server_.start(port)) {
            Serial.println(F("[CameraStreamer] Помилка запуску вебсервера!"));
            return false;
        }

        isReady_ = true;
        Serial.println(F("[CameraStreamer] Відеострімер успішно активовано та готовий до роботи."));
        return true;
    }

    /**
     * @brief Періодичне оновлення стану та моніторинг телеметрії.
     * Викликається з основного циклу loop().
     */
    void update() {
        if (!isReady_) return;

        uint32_t now = millis();
        if (now - lastTelemetryTime_ >= TELEMETRY_INTERVAL_MS) {
            lastTelemetryTime_ = now;
            printDiagnostics();
        }
    }

    /**
     * @brief Встановлює яскравість світлодіода спалаху (0..100%).
     */
    void setFlashBrightness(uint8_t percentage) {
        flashController_.setBrightnessPercent(percentage);
    }

    /**
     * @brief Виводить поточний стан пам'яті та периферії у консоль.
     */
    void printDiagnostics() const {
        if (!isReady_) return;

        Serial.println(F("--- [Телеметрія ESP32-CAM] ---"));
        Serial.printf("Вільна пам'ять SRAM : %u байт\n", (unsigned int)ESP.getFreeHeap());
        if (cameraBuffer_.isPsramAvailable()) {
            Serial.printf("Вільна пам'ять PSRAM: %u / %u байт\n", 
                          (unsigned int)cameraBuffer_.getFreePsram(), 
                          (unsigned int)cameraBuffer_.getTotalPsram());
        }
        Serial.printf("Яскравість спалаху (LEDC Duty): %u / 255\n", flashController_.getDuty());
        Serial.println(F("--------------------------------"));
    }

    /**
     * @brief Отримує посилання на контролер буферів пам'яті.
     */
    PsramFrameBuffer& getCameraBuffer() { return cameraBuffer_; }

    /**
     * @brief Отримує посилання на контролер ШІМ-спалаху.
     */
    FlashPwmController& getFlashController() { return flashController_; }

    /**
     * @brief Отримує посилання на вебсервер.
     */
    MjpegAsyncServer& getServer() { return server_; }

    /**
     * @brief Перевіряє статус готовності системи.
     */
    bool isReady() const { return isReady_; }

private:
    PsramFrameBuffer cameraBuffer_;
    FlashPwmController flashController_;
    MjpegAsyncServer server_;
    
    bool isReady_{false};
    uint32_t lastTelemetryTime_{0};
    static constexpr uint32_t TELEMETRY_INTERVAL_MS = 10000; // 10 секунд
};

#endif // CAMERA_STREAMER_HPP
