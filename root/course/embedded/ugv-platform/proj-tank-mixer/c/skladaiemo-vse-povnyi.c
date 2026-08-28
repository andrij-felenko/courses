// ── Параметри драйвера (підбирати під конкретне шасі) ──
#define SLEW_PER_TICK   20      // приріст швидкості за цикл (розгін ~0.5 с при 10 мс)
#define I_LIMIT_A       6.0f    // поріг сумарного струму бортів, А
#define I_FOLD_A        8.0f    // тут душимо команду повністю (foldback у нуль)

// Сторони H-мостів
enum { SIDE_LEFT = 0, SIDE_RIGHT = 1 };

static int cmd_left  = 0;       // поточна (згладжена) швидкість лівого борту
static int cmd_right = 0;       // ... правого

static int clampi(int v, int lo, int hi) {
    return v < lo ? lo : (v > hi ? hi : v);
}

// Плавно підвести val до target не більше ніж на SLEW_PER_TICK за виклик.
static int slew(int val, int target) {
    if (target - val >  SLEW_PER_TICK) return val + SLEW_PER_TICK;
    if (target - val < -SLEW_PER_TICK) return val - SLEW_PER_TICK;
    return target;
}

// Головна функція драйвера. Викликати кожні ~10 мс.
//   ch_throttle, ch_steer : сирі канали з приймача, мкс (1000..2000)
//   i_total               : виміряний сумарний струм обох бортів, А
//   now_ms                : монотонний час, мс
void chassis_update(uint16_t ch_throttle, uint16_t ch_steer,
                    float i_total, uint32_t now_ms)
{
    int throttle, steer;

    // 0) FAILSAFE НАД УСІМ: нема свіжого лінка → ціль обох бортів = 0.
    //    Не «застигаємо» на останній команді, а свідомо гальмуємо.
    if (!link_alive(now_ms)) {
        throttle = 0;
        steer    = 0;
    } else {
        // 1) Сирі канали → чисті знакові газ і поворот (дедзона + межі)
        throttle = rc_to_signed(ch_throttle);
        steer    = rc_to_signed(ch_steer);
    }

    // 2) Танкове змішування: поворот додаємо лівому, віднімаємо правому
    int left  = throttle + steer;
    int right = throttle - steer;

    // 3) Переповнення → стиснути ОБИДВА пропорційно (береже курс, не борт)
    int peak = (abs(left) > abs(right)) ? abs(left) : abs(right);
    if (peak > DRIVE_MAX) {
        left  = left  * DRIVE_MAX / peak;
        right = right * DRIVE_MAX / peak;
    }

    // 4) Струмовий foldback: що ближче до I_FOLD_A, то сильніше глушимо.
    //    Колесо вперлося/буксує → команда плавно сідає, струм тримається в межах.
    if (i_total > I_LIMIT_A) {
        float k = (I_FOLD_A - i_total) / (I_FOLD_A - I_LIMIT_A); // 1 → 0
        if (k < 0.0f) k = 0.0f;
        left  = (int)(left  * k);
        right = (int)(right * k);
    }

    // 5) Slew-rate: плавно вести реальні команди до цілей (без ривка струму).
    //    ВАЖЛИВО: при failsafe ціль = 0, і slew м'яко зводить газ у нуль,
    //    а не рубає різко — це і безпечно, і не б'є механіку.
    cmd_left  = slew(cmd_left,  clampi(left,  -DRIVE_MAX, DRIVE_MAX));
    cmd_right = slew(cmd_right, clampi(right, -DRIVE_MAX, DRIVE_MAX));

    // 6) На залізо: знак = напрям обертання, модуль = шпаруватість ШІМ.
    hbridge_set(SIDE_LEFT,  cmd_left);
    hbridge_set(SIDE_RIGHT, cmd_right);
}
