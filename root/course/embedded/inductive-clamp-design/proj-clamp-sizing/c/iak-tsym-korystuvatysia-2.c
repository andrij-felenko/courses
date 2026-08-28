void demo_solenoid_single_shot(void)
{
    clamp_input_t in = {
        .inductance_H = 0.010, .current_A = 2.0, .supply_V = 24.0,
        .t_off_target_s = 400e-6,   // вже реалістичні 400 мкс
        .bv_dss_V = 100.0, .winding_ohm = 6.0,
        .pwm_freq_Hz = 0.0,         // разове спрацювання, не ШІМ
    };
    clamp_result_t r = clamp_size(in);
    clamp_classify(in, &r);

    // delta_V = 0.010·2/400e-6 = 50 В;  clamp_V = 74 В  (< 85 В = 100·0.85: влізає)
    // avg_power_W = 0 (f=0);  required_eas = 26.3 мДж
    // diode_decay = 8.3 мс ≫ 400 мкс → діода НЕ досить за швидкістю
    // verdict = CLAMP_AVALANCHE_OK: разовий викид, кламп 74 В терпить ключ.
    //   → звір: паспортна E_AS ключа має бути > required_eas (26.3 мДж) із запасом.
}
