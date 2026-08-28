void demo_switch_overvolt(void)
{
    flyback_spec_t s = {
        .vin_min_V = 90.0f, .vin_max_V = 265.0f,  // мережа, широкий вхід
        .vout_V = 12.0f, .iout_A = 1.0f,
        .vdiode_V = 0.7f, .freq_Hz = 65000.0f,
        .duty_target = 0.45f, .efficiency = 0.85f,
        .core_Ae_m2 = 25e-6f, .b_work_T = 0.30f,
        .bv_switch_V = 600.0f, .j_density_Apmm2 = 5.0f,
    };
    flyback_result_t r = flyback_design(s);
    flyback_check(s, &r);

    // turns_ratio ≈ (90·0.45)/(12.7·0.55) ≈ 5.8 — велике відношення
    // reflected_V ≈ 12.7·5.8 ≈ 74 В
    // vds_peak_V  ≈ 265 + 74·1.30 ≈ 265 + 96 ≈ 361 В
    //   проти ключа 600 В·0.85 = 510 В → switch_overvolt = false (влазить)
    // А якби взяли ключ на 400 В: 361 > 400·0.85=340 → switch_overvolt = true!
}
