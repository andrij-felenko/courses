#include <stdint.h>
#include <stdbool.h>

typedef struct {
    // --- згасання за бездіяльності ---
    uint32_t last_activity_ms;   // коли востаннє була взаємодія
    uint16_t bright_target;      // куди хочемо (0..1000, перцептивна шкала)
    uint16_t bright_now;         // де яскравість зараз (плавно повзе до target)
    uint16_t bright_full;        // «повна» яскравість інтерфейсу
    uint16_t dim_ms;             // за скільки бездіяльності притемнити
    uint32_t off_ms;             // за скільки — згасити зовсім

    // --- зсув картинки (pixel-shift) ---
    int8_t   shift_x, shift_y;   // поточний зсув усього екрана, пікселі
    uint8_t  shift_span;         // піврозмах: зсув гуляє в [-span, +span]
    uint32_t last_shift_ms;      // коли востаннє зсунули
    uint16_t shift_period_ms;    // як часто робити крок зсуву

    // --- облік зносу (світло-години на канал) ---
    // одиниці умовні: (середня яскравість каналу) × (час), накопичено
    uint64_t wear_r, wear_g, wear_b;
    uint16_t blue_scale;         // масштаб синього (0..256, 256 = ×1.0) за зносом
} disp_guard_t;
