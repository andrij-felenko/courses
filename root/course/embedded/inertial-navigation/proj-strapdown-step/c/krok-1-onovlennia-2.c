/* Оновити орієнтацію q за один такт гіроскопа.
   wx,wy,wz — кутова швидкість (рад/с) в осях апарата;
   bias     — виміряний у спокої зсув нуля гіроскопа (рад/с);
   dt       — крок такту (с). */
static quat orientation_step(quat q, vec3 w_raw, vec3 bias, float dt) {
    /* 1) прибрати зсув нуля — інакше інтеграл повзе */
    vec3 w = { w_raw.x - bias.x, w_raw.y - bias.y, w_raw.z - bias.z };

    /* 2) кватерніон приросту за такт */
    float ang = sqrtf(w.x*w.x + w.y*w.y + w.z*w.z) * dt;   /* кут за такт, рад */
    quat dq;
    if (ang > 1e-6f) {                 /* точна гілка: відчутний оберт */
        float s = sinf(ang * 0.5f) / (ang / dt);  /* = sin(θ/2)/|ω| */
        dq.w = cosf(ang * 0.5f);
        dq.x = w.x * s;                /* ωx·sin(θ/2)/|ω| = sin(θ/2)·nx */
        dq.y = w.y * s;
        dq.z = w.z * s;
    } else {                           /* безпечна гілка: майже спокій */
        dq.w = 1.0f;                   /* cos(θ/2) ≈ 1 */
        dq.x = 0.5f * w.x * dt;        /* sin(θ/2)·n ≈ ½·ω·dt */
        dq.y = 0.5f * w.y * dt;
        dq.z = 0.5f * w.z * dt;
    }

    /* 3) скласти повороти й повернути результат на сферу */
    q = quat_mul(q, dq);
    return quat_normalize(q);
}
