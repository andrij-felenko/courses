#include <math.h>

// Межі й темпи (підібрати під конкретне шасі)
#define DRIVE_MAX     1000     // повний хід ШІМ, безрозмірно
#define SLEW_PER_TICK  40      // макс. приріст швидкості за один цикл (розгін)
#define I_LIMIT_A      6.0f    // поріг сумарного струму бортів, А
#define I_FOLD_A       8.0f    // тут душимо повністю (foldback)

static int cmd_left  = 0;      // поточна (згладжена) швидкість лівого борту
static int cmd_right = 0;      // ... правого

// Плавно підвести val до target не більше ніж на SLEW_PER_TICK за виклик
static int slew(int val, int target) {
    if (target - val >  SLEW_PER_TICK) return val + SLEW_PER_TICK;
    if (target - val < -SLEW_PER_TICK) return val - SLEW_PER_TICK;
    return target;
}

static int clampi(int v, int lo, int hi) {
    return v < lo ? lo : (v > hi ? hi : v);
}

// Головна функція: викликати кожні ~10 мс.
// throttle, steer: −1000..+1000. i_total: виміряний сумарний струм бортів, А.
void chassis_drive(int throttle, int steer, float i_total) {
    // 1) Танкове змішування: поворот додаємо/віднімаємо
    int left  = throttle + steer;
    int right = throttle - steer;

    // 2) Якщо сума вийшла за межу — стиснути ОБИДВА пропорційно,
    //    щоб зберегти співвідношення (курс), а не обрізати один борт
    int peak = (abs(left) > abs(right)) ? abs(left) : abs(right);
    if (peak > DRIVE_MAX) {
        left  = left  * DRIVE_MAX / peak;
        right = right * DRIVE_MAX / peak;
    }

    // 3) Струмовий запобіжник (foldback): що ближче до I_FOLD_A,
    //    то сильніше глушимо команду — колесо буксує чи впав у камінь
    if (i_total > I_LIMIT_A) {
        float k = (I_FOLD_A - i_total) / (I_FOLD_A - I_LIMIT_A); // 1→0
        k = k < 0.0f ? 0.0f : k;
        left  = (int)(left  * k);
        right = (int)(right * k);
    }

    // 4) Плавно вести реальні команди до цілей (без ривка струму)
    cmd_left  = slew(cmd_left,  clampi(left,  -DRIVE_MAX, DRIVE_MAX));
    cmd_right = slew(cmd_right, clampi(right, -DRIVE_MAX, DRIVE_MAX));

    // 5) Віддати на H-мости (знак = напрям, модуль = шпаруватість ШІМ)
    hbridge_set(SIDE_LEFT,  cmd_left);
    hbridge_set(SIDE_RIGHT, cmd_right);
}
