#include <stdint.h>
#include <stdbool.h>

// Стан детектора живе між викликами (тут статикою для наочності;
// у реальному модулі — полем контексту, щоб було кілька незалежних сторожів).
static bool     active = false;           // стан автомата: ТИША / ПОДІЯ
static int      hang   = 0;               // лічильник хвоста, кадрів
static uint32_t noise  = 400;             // оцінка фону, одиниці MSE

const uint32_t K_UP   = 4;                // запас на ВХІД: поріг_ВГ = фон·K_UP  (+6 дБ)
const uint32_t K_DOWN = 2;                // запас на ВИХІД: поріг_ВН = фон·K_DOWN (+3 дБ)
const int      HANG   = 12;               // хвіст ≈ 200 мс при кадрі 16 мс
const int      S_UP   = 3;                // фон угору: α ≈ 1/8   (швидко)
const int      S_DOWN = 7;                // фон униз:  α ≈ 1/128 (повільно)

bool vad_step(uint32_t mse) {
    uint32_t thr_up   = noise * K_UP;     // множники, а не абсолюти — переносяться
    uint32_t thr_down = noise * K_DOWN;

    if (!active) {                         // ── стан ТИША ──
        if (mse > thr_up) {                // впевнено пробили верхній поріг
            active = true;
            hang   = HANG;                 // зарядили хвіст
        } else {                           // тихо — оновлюємо фон (ЛИШЕ тут!)
            if (mse > noise) noise += (mse - noise) >> S_UP;   // швидко вгору
            else             noise -= (noise - mse) >> S_DOWN; // повільно вниз
        }
    } else {                               // ── стан ПОДІЯ ──
        if (mse > thr_down) {              // ще досить гучно — продовжуємо
            hang = HANG;                   // перезарядили хвіст
        } else if (--hang <= 0) {          // тихо й хвіст вичерпано
            active = false;                // подія скінчилась
        }
        // у стані ПОДІЯ фон НЕ чіпаємо — щоб не отруїти оцінку власним сигналом
    }
    return active;
}
