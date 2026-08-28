void demo_aux_rail(void)
{
    flyback_spec_t s = {
        .vin_min_V       = 18.0f,
        .vin_max_V       = 30.0f,
        .vout_V          = 12.0f,
        .iout_A          = 0.5f,
        .vdiode_V        = 0.7f,
        .freq_Hz         = 65000.0f,
        .duty_target     = 0.45f,
        .efficiency      = 0.85f,
        .core_Ae_m2      = 20e-6f,   // 20 мм²
        .b_work_T        = 0.30f,    // обережний робочий потік
        .bv_switch_V     = 100.0f,   // ключ тримає 100 В
        .j_density_Apmm2 = 5.0f,     // 5 А/мм²
    };

    flyback_result_t r = flyback_design(s);
    flyback_check(s, &r);

    // Очікувано (звірка з темою, по кроках):
    //   Pin          = 12·0.5/0.85   ≈ 7.06 Вт
    //   lp_primary_H = (18·0.45)²/(2·7.06·65000) ≈ 71 мкГн
    //   i_peak_A     = 18·0.45/(71e-6·65000)     ≈ 1.75 А
    //   turns_ratio  = (18·0.45)/(12.7·0.55)     ≈ 1.16
    //   np_turns     = ceil(71e-6·1.75/(0.30·20e-6)) = ceil(20.7) = 21
    //   ns_turns     = ceil(21/1.16) = ceil(18.1) = 19
    //   al_nH_per_t2 = 71000/21²     ≈ 161 нГн/виток²
    //   i_pri_rms_A  = 1.75·√(0.45/3) ≈ 0.68 А  → провід ≈ 0.14 мм² (Ø0.4 мм)
    //   i_sec_rms_A  = (1.75·1.16)·√(0.55/3) ≈ 2.03·0.428 ≈ 0.87 А → ≈0.17 мм²
    //   reflected_V  = 12.7·1.16     ≈ 14.7 В
    //   vds_peak_V   = 30 + 14.7·1.30 ≈ 30 + 19.1 ≈ 49 В  (< 85 В: влізає)
    //   i_peak_threshold_A = 1.75 А  → у прошивку як I_PEAK_MAX
    //   duty_required = √(2·71e-6·7.06·65000)/18 ≈ 0.45 (= задана: на межі за побудовою)
    //   switch_overvolt = false; ccm_risk = false; duty_unrealistic = false
}
