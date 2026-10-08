#include <stdint.h>
#include <stddef.h>

typedef enum {
    FRAME_FMT_YUV422 = 0,
    FRAME_FMT_RGB565 = 1,
    FRAME_FMT_JPEG   = 2
} frame_format_t;

typedef struct {
    uint16_t width;
    uint16_t height;
    frame_format_t format;
    uint8_t jpeg_quality; // 1 (найвища) .. 63 (найнижча)
} camera_config_t;

// Розрахунок необхідного розміру буфера пам'яті для кадру
size_t calculate_required_buffer_bytes(const camera_config_t *cfg) {
    if (!cfg) return 0;
    
    size_t raw_pixels = (size_t)cfg->width * cfg->height;
    
    switch (cfg->format) {
        case FRAME_FMT_YUV422:
        case FRAME_FMT_RGB565:
            // 2 байти на піксель для нестиснених форматів
            return raw_pixels * 2;
            
        case FRAME_FMT_JPEG:
            // Приблизна оцінка розміру JPEG: 10% .. 25% від несжиманого кадру
            // залежно від налаштування якості
            if (cfg->jpeg_quality < 10) {
                return (raw_pixels * 2) / 4; // ~25%
            } else {
                return (raw_pixels * 2) / 10; // ~10%
            }
            
        default:
            return 0;
    }
}
