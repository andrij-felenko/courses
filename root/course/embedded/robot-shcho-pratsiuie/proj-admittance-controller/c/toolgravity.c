#include "toolgravity.h"

static void cross3(const float a[3], const float b[3], float out[3])
{
    out[0] = a[1] * b[2] - a[2] * b[1];
    out[1] = a[2] * b[0] - a[0] * b[2];
    out[2] = a[0] * b[1] - a[1] * b[0];
}

void tool_gravity_wrench(const tool_inertia_t *tool, const float r_sensor[9], float w_g[6])
{
    if (!tool || !r_sensor || !w_g) {
        return;
    }

    /* Вага в базовій (горизонтованій) системі. */
    const float g_base[3] = { 0.0f, 0.0f, -tool->mass * tool->g };

    /* Rᵀ·g_base: матриця задана рядками, тож транспонована дія — це
       згортка по стовпцях. Саме цей поворот і робить вагу «блукаючою»
       по осях давача, коли кисть змінює орієнтацію. */
    float force[3];
    for (int i = 0; i < 3; ++i) {
        force[i] = r_sensor[i] * g_base[0] +
                   r_sensor[3 + i] * g_base[1] +
                   r_sensor[6 + i] * g_base[2];
    }

    /* Момент від ваги на плечі центра мас. */
    float moment[3];
    cross3(tool->com, force, moment);

    for (int i = 0; i < 3; ++i) {
        w_g[i] = force[i];
        w_g[3 + i] = moment[i];
    }
}

void tool_gravity_compensate(const tool_inertia_t *tool, const float r_sensor[9],
                             const float w_raw[6], float w_ext[6])
{
    if (!tool || !r_sensor || !w_raw || !w_ext) {
        return;
    }
    float w_g[6];
    tool_gravity_wrench(tool, r_sensor, w_g);
    for (int i = 0; i < 6; ++i) {
        w_ext[i] = w_raw[i] - w_g[i];
    }
}
