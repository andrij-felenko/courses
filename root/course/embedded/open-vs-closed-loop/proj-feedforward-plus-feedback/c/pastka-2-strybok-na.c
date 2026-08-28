// перехід ручний → авто без стрибка, з урахуванням ОБОХ гілок.
// хочемо, щоб у першу мить: u_ff + KP·e + KI·integ == u_manual
void bumpless_arm(float r, float u_manual, float dt) {
    float y = read_temp();
    float e = r - y;

    float dr_dt = (r - r_prev) / dt;
    float u_ff  = K_LOSS * (r - T_ROOM) + C_TH * dr_dt;   // те саме, що в такті

    // преднавантажуємо інтеграл на ЛИШОК, який не дали ні u_ff, ні KP·e:
    integ = (u_manual - u_ff - KP * e) / KI;

    r_prev = r;
    was_active = true;
}
