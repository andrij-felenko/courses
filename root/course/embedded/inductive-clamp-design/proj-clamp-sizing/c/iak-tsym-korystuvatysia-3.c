void demo_relay(void)
{
    clamp_input_t in = {
        .inductance_H = 0.080, .current_A = 0.060, .supply_V = 12.0,
        .t_off_target_s = 0.005,    // реле може відпускати до 5 мс — не поспішаємо
        .bv_dss_V = 60.0, .winding_ohm = 200.0,
        .pwm_freq_Hz = 0.0,
    };
    clamp_result_t r = clamp_size(in);
    clamp_classify(in, &r);

    // diode_decay = 5·0.080/200 = 2.0 мс  ≤  5 мс бюджету → діода ДОСИТЬ
    // verdict = CLAMP_SIMPLE_DIODE: найдешевший гасний діод, жодних прапорців.
}
