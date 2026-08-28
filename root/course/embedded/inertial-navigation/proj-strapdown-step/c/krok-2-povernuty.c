/* Повернути вектор v з осей апарата у світові осі кватерніоном q.
   Це v' = q ⊗ (0,v) ⊗ q*, розгорнуте без зайвих множень. */
static vec3 quat_rotate(quat q, vec3 v) {
    /* t = 2·(q_vec × v) */
    float tx = 2.0f * (q.y*v.z - q.z*v.y);
    float ty = 2.0f * (q.z*v.x - q.x*v.z);
    float tz = 2.0f * (q.x*v.y - q.y*v.x);
    /* v' = v + q.w·t + q_vec × t */
    vec3 r;
    r.x = v.x + q.w*tx + (q.y*tz - q.z*ty);
    r.y = v.y + q.w*ty + (q.z*tx - q.x*tz);
    r.z = v.z + q.w*tz + (q.x*ty - q.y*tx);
    return r;
}
