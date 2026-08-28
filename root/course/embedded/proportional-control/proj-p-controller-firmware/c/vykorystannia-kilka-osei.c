static p_ctrl_t roll_p, pitch_p, alt_p;

void control_init(void)
{
    // крен/тангаж: P-на-вимірі (beta=0) — щоб різка команда пілота не смикала;
    // межі — симетричний діапазон рульового моменту в одиницях ШІМ
    p_config(&roll_p,  4.0f, 0.0f, -400.0f, 400.0f, 0.0f);
    p_config(&pitch_p, 4.0f, 0.0f, -400.0f, 400.0f, 0.0f);

    // висота: P-на-помилці (beta=1) + живлення наперед газом на висіння,
    // щоб прибити сталий зсув без інтеграла; вихід — газ у [0..1000]
    p_config(&alt_p,   6.0f, 1.0f,    0.0f, 1000.0f, /*u_bias=*/520.0f);
}

void control_tick(state_t *st, setpoint_t *sp)
{
    float u_roll  = p_step(&roll_p,  sp->roll,  st->roll);
    float u_pitch = p_step(&pitch_p, sp->pitch, st->pitch);
    float u_alt   = p_step(&alt_p,   sp->alt,   st->alt);

    motors_mix(u_alt, u_roll, u_pitch);   // звести в команди моторам
}
