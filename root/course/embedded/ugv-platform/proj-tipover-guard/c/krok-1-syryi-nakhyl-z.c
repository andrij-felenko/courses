#include <math.h>

// Крен і тангаж (рад) із сирих осей акселерометра.
//   ax, ay, az — питома сила по осях, у будь-яких однакових одиницях (g або м/с²)
// roll  (крен)  — нахил убік (навколо осі X, уперед)
// pitch (тангаж) — нахил уперед/назад (навколо осі Y, вліво)
static void accel_to_angles(float ax, float ay, float az,
                            float *roll, float *pitch)
{
    // крен: скільки g «перелилося» на бічну вісь Y відносно вертикалі
    *roll  = atan2f(ay, sqrtf(ax * ax + az * az));
    // тангаж: скільки перелилося на поздовжню X
    *pitch = atan2f(-ax, sqrtf(ay * ay + az * az));
}
