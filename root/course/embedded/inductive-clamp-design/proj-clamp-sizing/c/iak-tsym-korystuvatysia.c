void demo_solenoid(void)
{
    clamp_input_t in = {
        .inductance_H   = 0.010,   // 10 мГн
        .current_A      = 2.0,     // 2 А
        .supply_V       = 24.0,    // 24 В
        .t_off_target_s = 50e-6,   // 50 мкс
        .bv_dss_V       = 100.0,   // ключ тримає 100 В
        .winding_ohm    = 6.0,     // опір обмотки 6 Ом
        .pwm_freq_Hz    = 20000.0, // ШІМ 20 кГц
    };

    clamp_result_t r = clamp_size(in);
    clamp_classify(in, &r);

    // Очікувано (звірка з темою):
    //   delta_V       = 0.010·2/50e-6 = 400 В   (!! понад BV_DSS)
    //   clamp_V       = 424 В
    //   energy_J      = ½·0.010·4    = 0.020 Дж = 20 мДж
    //   avg_power_W   = 0.020·20000  = 400 Вт    (!!)
    //   peak_power_W  = 424·2        = 848 Вт
    //   required_eas  = 20мДж·100/76 = 26.3 мДж
    //   diode_decay   = 5·0.010/6    = 8.3 мс
    //   verdict       = CLAMP_INFEASIBLE (кламп 424 В > 100 В ключа)
    //   clamp_exceeds_bv  = true
    //   pwm_overheat_risk = true (400 Вт ≫ 5 Вт)
}
