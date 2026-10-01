#ifndef TIMELAPSE_STORAGE_HPP
#define TIMELAPSE_STORAGE_HPP

#include "esp_camera.h"
#include "FS.h"
#include "SD_MMC.h"
#include <cstdint>
#include <cstddef>

// Клас для збереження кадрів таймлапс-зйомки на карту microSD через 1-бітний/4-бітний режим SD_MMC.
class TimelapseStorage {
public:
    TimelapseStorage() : m_initialized(false), m_frameCounter(0), m_lastCaptureMs(0) {}

    // Монтує файлову систему SD_MMC та готує директорію для таймлапс-фото.
    bool begin() {
        if (!SD_MMC.begin("/sdcard", true)) { // Використовуємо 1-бітний режим для сумісності з Flash LED
            return false;
        }

        uint8_t cardType = SD_MMC.cardType();
        if (cardType == CARD_NONE) {
            return false;
        }

        // Створюємо директорію /timelapse, якщо вона відсутня
        if (!SD_MMC.exists("/timelapse")) {
            SD_MMC.mkdir("/timelapse");
        }

        m_initialized = true;
        return true;
    }

    // Зберігає кадр з камери на microSD під автоматичним іменем.
    bool saveFrame(camera_fb_t* fb) {
        if (!m_initialized || fb == nullptr) {
            return false;
        }

        char path[64];
        std::snprintf(path, sizeof(path), "/timelapse/frame_%05u.jpg", m_frameCounter++);

        fs::File file = SD_MMC.open(path, FILE_WRITE);
        if (!file) {
            return false;
        }

        std::size_t written = file.write(fb->buf, fb->len);
        file.close();

        return (written == fb->len);
    }

    // Перевіряє інтервал таймера та зберігає кадр у разі настання чергового кроку.
    void process(uint32_t intervalMs) {
        uint32_t currentMs = millis();
        if (currentMs - m_lastCaptureMs >= intervalMs) {
            m_lastCaptureMs = currentMs;

            camera_fb_t* fb = esp_camera_fb_get();
            if (fb != nullptr) {
                saveFrame(fb);
                esp_camera_fb_return(fb);
            }
        }
    }

    bool isInitialized() const { return m_initialized; }

private:
    bool m_initialized;
    uint32_t m_frameCounter;
    uint32_t m_lastCaptureMs;
};

#endif // TIMELAPSE_STORAGE_HPP
