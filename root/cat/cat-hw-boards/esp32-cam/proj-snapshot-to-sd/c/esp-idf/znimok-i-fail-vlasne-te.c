#include <stdio.h>
#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "snapshot";

static bool save_photo(const char *path) {
    // 1. Просимо драйвер камери віддати готовий кадр.
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGE(TAG, "Не вдалося зняти кадр");
        return false;
    }

    // 2. Відкриваємо файл на картці: FAT примонтована у VFS, тож звичайний fopen.
    FILE *f = fopen(path, "wb");    // шлях ПОВНИЙ, від точки монтування: "/sdcard/…"
    if (!f) {
        ESP_LOGE(TAG, "Не відкрити файл %s", path);
        esp_camera_fb_return(fb);   // буфер усе одно ПОВЕРНУТИ
        return false;
    }

    // 3. Ллємо стиснені байти JPEG у файл одним махом.
    size_t written = fwrite(fb->buf, 1, fb->len, f);   // fb->buf — адреса, fb->len — довжина
    bool ok = (written == fb->len);
    fclose(f);

    ESP_LOGI(TAG, "Збережено %s  (%u байт)", path, (unsigned)written);

    // 4. ОБОВ'ЯЗКОВО повертаємо буфер драйверу.
    esp_camera_fb_return(fb);
    return ok;
}
