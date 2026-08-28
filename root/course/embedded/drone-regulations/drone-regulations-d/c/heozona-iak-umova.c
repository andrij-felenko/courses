#include <stdint.h>

// Поточний стан захисту геозони (щоб не сіпатися на межі).
static int geofence_engaged = 0;

// dist_to_border_m — відстань до межі зони (>0 усередині дозволеного, <0 уже за нею).
// speed_ms         — поточна горизонтальна швидкість апарата.
// Повертає 1, якщо треба ввімкнути захисну реакцію (гальмувати/розвертати).
int geofence_should_engage(float dist_to_border_m, float speed_ms) {
    // Гальмівний шлях: скільки апарат пройде, поки зупиниться.
    // Консервативно беремо сталу межу гальмування (напр. 3 м/с²).
    const float BRAKE_ACCEL = 3.0f;                 // м/с², типове безпечне гальмування
    float stop_dist = (speed_ms * speed_ms) / (2.0f * BRAKE_ACCEL);

    // Пороги гістерезису: вмикаємо РАНІШЕ (з випередженням на гальмівний шлях
    // плюс запас), вимикаємо лише коли добре відійшли назад.
    float d_on  = stop_dist + 5.0f;                 // почни реагувати за stop_dist + 5 м
    float d_off = stop_dist + 15.0f;                // відпусти, лише відійшовши на +15 м

    if (!geofence_engaged) {
        // Ще не втручаємось: вмикаємось, коли підлетіли ближче за d_on.
        if (dist_to_border_m <= d_on)
            geofence_engaged = 1;
    } else {
        // Уже втручаємось: відпускаємо, лише відійшовши далі за d_off (зазор!).
        if (dist_to_border_m >= d_off)
            geofence_engaged = 0;
    }
    return geofence_engaged;
}
