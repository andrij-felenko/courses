#include <stdint.h>

typedef enum {
    ANIM_OFF = 0,   // слот вільний
    ANIM_ONCE,      // один прохід 0→1 і стоп
    ANIM_LOOP,      // 0→1, стрибок на 0, нескінченно
    ANIM_PINGPONG   // 0→1→0→1… нескінченно, дзеркально
} AnimMode;

typedef uint16_t (*ShapeFn)(uint16_t phase);   // фаза 0..4095 → яскравість 0..4095

typedef struct {
    uint8_t       pin;        // канал LEDC
    AnimMode      mode;
    ShapeFn       shape;      // форма руху
    uint32_t      start;      // millis() запуску (база відліку фази)
    uint32_t      duration;   // тривалість одного проходу фази, мс
    uint32_t      pausedAt;   // millis() моменту паузи; 0 = біжить
    bool          invert;     // активно-низьке підключення
} Anim;

#define ANIM_SLOTS 16
static Anim anims[ANIM_SLOTS];
