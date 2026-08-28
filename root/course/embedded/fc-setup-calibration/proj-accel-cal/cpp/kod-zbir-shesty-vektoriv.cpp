#include <stdint.h>
#include <math.h>

#define GRAVITY_MSS   9.80665f     // еталон: величина тяжіння, м/с²
#define ACC_SAMPLES   400          // скільки відліків усереднюємо на грань (~кілька секунд @ сотні Гц)
#define ACC_MOVE_TOL  0.35f        // поріг «апарат рухається», м/с²

typedef struct { float x, y, z; } vec3_t;

// сирий вектор акселерометра, м/с² (уже з тракту IMU, ще некалібрований)
extern vec3_t accel_read_raw(void);

// Усереднити ACC_SAMPLES відліків на одній грані.
// Повертає true й кладе середнє в *out, якщо апарат був нерухомий;
// false — якщо під час зняття вектор «дрижав» (рух зіпсував би точку).
static bool accel_capture_face(vec3_t *out)
{
    vec3_t sum = {0, 0, 0};
    vec3_t vmin = { +1e9f, +1e9f, +1e9f };
    vec3_t vmax = { -1e9f, -1e9f, -1e9f };

    for (int i = 0; i < ACC_SAMPLES; i++) {
        vec3_t s = accel_read_raw();
        sum.x += s.x;  sum.y += s.y;  sum.z += s.z;
        // заразом стежимо за розкидом — це детектор руху
        if (s.x < vmin.x) vmin.x = s.x;   if (s.x > vmax.x) vmax.x = s.x;
        if (s.y < vmin.y) vmin.y = s.y;   if (s.y > vmax.y) vmax.y = s.y;
        if (s.z < vmin.z) vmin.z = s.z;   if (s.z > vmax.z) vmax.z = s.z;
        delay_one_sample();            // чекаємо наступний відлік давача
    }

    // якщо хоч по одній осі розкид більший за поріг — апарат рухався, точка бита
    if ((vmax.x - vmin.x) > ACC_MOVE_TOL ||
        (vmax.y - vmin.y) > ACC_MOVE_TOL ||
        (vmax.z - vmin.z) > ACC_MOVE_TOL) {
        return false;
    }

    out->x = sum.x / ACC_SAMPLES;
    out->y = sum.y / ACC_SAMPLES;
    out->z = sum.z / ACC_SAMPLES;
    return true;
}
