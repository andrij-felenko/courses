#include <math.h>

typedef struct { float x, y, z; } vec3_t;

/* Перетворення вектора позиції/швидкості ENU (ROS) -> NED (PX4) */
vec3_t enu_to_ned(vec3_t enu) {
    vec3_t ned;
    ned.x =  enu.y;
    ned.y =  enu.x;
    ned.z = -enu.z;
    return ned;
}

/* Перетворення кута курсу yaw (радіани) */
float yaw_enu_to_ned(float yaw_enu) {
    float yaw_ned = (float)(M_PI / 2.0) - yaw_enu;
    while (yaw_ned >  M_PI) yaw_ned -= (float)(2.0 * M_PI);
    while (yaw_ned < -M_PI) yaw_ned += (float)(2.0 * M_PI);
    return yaw_ned;
}
