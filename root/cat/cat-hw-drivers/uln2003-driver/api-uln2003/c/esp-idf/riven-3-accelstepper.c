#include <math.h>

#define VMAX   700.0    // стеля швидкості, півкроків/с
#define ACCEL  400.0    // розгін/гальмування, півкроків/с²

static long position = 0;   // поточна позиція в півкроках

// Трапеція швидкості руками. Ключ — формула гальмівного шляху v = sqrt(2·a·s):
// на кожному кроці беремо меншу зі стелі й «швидкості, з якої ще встигнемо стати».
static void move_to(long target) {
  long total = labs(target - position);
  int  dir   = (target > position) ? +1 : -1;
  double v   = 1.0;                     // поточна швидкість, півкроків/с

  for (long n = 0; n < total; n++) {
    double vt = fmin(VMAX, sqrt(2.0 * ACCEL * (total - n)));
    if (v < vt) v += ACCEL / v;         // приріст за час одного кроку (1/v секунди)
    if (v > vt) v = vt;

    idx = (idx + dir + 8) % 8;
    apply_step(idx);
    position += dir;
    esp_rom_delay_us((uint32_t)(1e6 / v));
  }
}

// Цикл блокує ЛИШЕ свою задачу FreeRTOS — Wi-Fi, кнопки й UART тим часом живі.
// Це і є відповідник неблокувальності AccelStepper на цій платформі.
