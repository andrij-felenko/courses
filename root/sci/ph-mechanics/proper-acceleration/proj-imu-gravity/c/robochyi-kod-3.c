typedef struct {
    vec3 v;   /* швидкість у світових осях, м/с */
    vec3 p;   /* положення у світових осях, м    */
} nav_state;

/* Один крок обробки: a_b — питома сила (осі корпусу), q — орієнтація, dt — крок. */
void imu_step(nav_state *s, vec3 a_b, quat q, float dt) {
    if (is_free_fall(a_b)) return;        /* у падінні інтегрувати нічого */

    vec3 a_body  = linear_accel(a_b, q);  /* прибрати тяжіння */
    vec3 a_world = quat_rotate(q, a_body);/* корпус → світ */

    s->v.x += a_world.x * dt;             /* 1) спершу швидкість */
    s->v.y += a_world.y * dt;
    s->v.z += a_world.z * dt;
    s->p.x += s->v.x * dt;                /* 2) тоді нею — положення */
    s->p.y += s->v.y * dt;
    s->p.z += s->v.z * dt;
}
