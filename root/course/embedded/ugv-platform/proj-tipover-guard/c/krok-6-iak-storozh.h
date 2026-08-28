// Усередині головного циклу ровера, поряд із читанням IMU:

// (десь у циклі IMU, ~100 Гц) — оновлюємо сторожа свіжим IMU:
guard_gain_t g = tipover_step(&guard, ax, ay, az, gx, gy, now);

// ... а в такті драйвера шасі, одразу після очищення каналів:
int throttle = rc_to_signed(ch_throttle);
int steer    = rc_to_signed(ch_steer);

// ★ СТОРОЖ ПЕРЕКИДУ: душимо волю оператора до безпечної.
//   газ  × g.throttle  (лінійно),  поворот × g.turn (= k², жорсткіше)
throttle = (int)(throttle * g.throttle);
steer    = (int)(steer    * g.turn);

// далі — як і було: змішування → затиск → foldback → slew → залізо
int left  = throttle + steer;
int right = throttle - steer;
// ...
