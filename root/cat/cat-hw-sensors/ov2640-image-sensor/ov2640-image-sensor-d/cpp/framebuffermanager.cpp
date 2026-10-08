#include "esp_camera.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"

class FrameBufferManager {
private:
    camera_fb_t* m_current_fb;
    SemaphoreHandle_t m_frame_mutex;
    volatile bool m_is_processing;

public:
    FrameBufferManager() : m_current_fb(nullptr), m_is_processing(false) {
        m_frame_mutex = xSemaphoreCreateMutex();
    }

    camera_fb_t* capture_frame() {
        if (m_is_processing) {
            // Запобігання переповненню: відкидаємо новий кадр, якщо попередній у роботі
            return nullptr;
        }

        xSemaphoreTake(m_frame_mutex, portMAX_DELAY);
        m_is_processing = true;

        // Захоплення кадру через DVP DMA буфер ESP32
        m_current_fb = esp_camera_fb_get();
        
        if (!m_current_fb) {
            m_is_processing = false;
            xSemaphoreGive(m_frame_mutex);
            return nullptr;
        }

        // Перевірка цілісності JPEG маркера EOI (0xFFD9) у кінці буфера
        if (m_current_fb->format == PIXFORMAT_JPEG) {
            if (m_current_fb->buf[m_current_fb->len - 2] != 0xFF ||
                m_current_fb->buf[m_current_fb->len - 1] != 0xD9) {
                // Пошкоджений кадр через втрату стробів DVP
                esp_camera_fb_return(m_current_fb);
                m_current_fb = nullptr;
            }
        }

        return m_current_fb;
    }

    void release_frame() {
        if (m_current_fb) {
            esp_camera_fb_return(m_current_fb);
            m_current_fb = nullptr;
        }
        m_is_processing = false;
        xSemaphoreGive(m_frame_mutex);
    }
};
