void demo_reused_transformer(void)
{
    // 1) проєктуємо й мотаємо трансформатор під 0.5 А (як вище):
    flyback_spec_t light = { /* …те саме ТЗ, iout_A = 0.5f… */
        .vin_min_V = 18.0f, .vin_max_V = 30.0f, .vout_V = 12.0f, .iout_A = 0.5f,
        .vdiode_V = 0.7f, .freq_Hz = 65000.0f, .duty_target = 0.45f,
        .efficiency = 0.85f, .core_Ae_m2 = 20e-6f, .b_work_T = 0.30f,
        .bv_switch_V = 100.0f, .j_density_Apmm2 = 5.0f,
    };
    flyback_result_t r = flyback_design(light);   // r.lp_primary_H ≈ 71 мкГн (намотано)

    // 2) а тепер хочемо зняти з ТОГО САМОГО трансформатора 2 А — лишаємо Lпр,
    //    але перевіряємо проти важчого ТЗ:
    flyback_spec_t heavy = light;
    heavy.iout_A = 2.0f;                  // 4× навантаження, осердя те саме
    flyback_check(heavy, &r);            // НЕ flyback_design — Lпр не чіпаємо

    // duty_required = √(2·71e-6·28.2·65000)/18 ≈ 0.90  ≫  задана 0.45
    //   ccm_risk = true → цим осердям 2 А в DCM не зняти: щоб віддати вчетверо
    //   більше пакетами тієї самої енергії, потрібна шпаруватість ~0.9 —
    //   струм не встигне спасти в нуль, перетворювач у CCM, формули DCM брешуть.
    //   Лікування: перемотати під більшу Lпр (свіжий flyback_design на 2 А)
    //   або свідомо перейти на CCM з його іншими формулами.
}
