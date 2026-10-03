#include "FS.h"
#include "SD_MMC.h"
#include "esp_camera.h"

bool saveFrameToSDMMC(camera_fb_t *fb, const String &path) {
    // Ініціалізація SDMMC в 4-бітному режимі (onebit = false)
    if (!SD_MMC.begin("/sdcard", false)) {
        Serial.println("Помилка монтування картки MicroSD через SDMMC 4-bit");
        return false;
    }

    // Відкриття файла для бінарного запису
    File file = SD_MMC.open(path.c_str(), FILE_WRITE);
    if (!file) {
        Serial.println("Помилка відкриття файла для запису");
        SD_MMC.end();
        return false;
    }

    // Запис усього кадрового буфера одним викликом
    size_t written = file.write(fb->buf, fb->len);
    file.close();
    SD_MMC.end(); // Завершення сесії для безпечного вимкнення живлення

    if (written != fb->len) {
        Serial.printf("Помилка: записано %u байт з %u\n", written, fb->len);
        return false;
    }

    Serial.printf("Файл %s збережено успішно!\n", path.c_str());
    return true;
}
