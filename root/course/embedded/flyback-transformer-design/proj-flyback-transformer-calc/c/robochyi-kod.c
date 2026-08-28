// Запас на сплеск індуктивності витоку понад відбиту напругу, частка.
// Реальна голка залежить від снабера; 0.30 — поміркований орієнтир «накинь третину».
#define LEAKAGE_SPIKE_MARGIN  0.30f

flyback_result_t flyback_design(flyback_spec_t s)
{
    flyback_result_t r = {0};
    r.valid = false;

    // --- захист від безглуздого ТЗ: не вгадуємо ---
    if (s.vin_min_V <= 0.0f || s.vin_max_V < s.vin_min_V ||
        s.vout_V <= 0.0f || s.iout_A <= 0.0f ||
        s.freq_Hz <= 0.0f || s.efficiency <= 0.0f || s.efficiency > 1.0f ||
        s.duty_target <= 0.0f || s.duty_target >= 1.0f ||
        s.core_Ae_m2 <= 0.0f || s.b_work_T <= 0.0f ||
        s.j_density_Apmm2 <= 0.0f) {
        return r;
    }

    float Vmin = s.vin_min_V;
    float D    = s.duty_target;
    float Vsec = s.vout_V + s.vdiode_V;     // вторинна мусить дати вихід + діод

    // --- потужність, яку тягнемо зі входу (з поправкою на ККД) ---
    float Pout = s.vout_V * s.iout_A;
    float Pin  = Pout / s.efficiency;

    // --- 1) індуктивність первинної: Lпр = (Vmin·D)² / (2·Pin·f) ---
    float VD = Vmin * D;
    r.lp_primary_H = (VD * VD) / (2.0f * Pin * s.freq_Hz);

    // піковий струм: Iпік = Vmin·D / (Lпр·f) — тягнеться далі скрізь
    r.i_peak_A = VD / (r.lp_primary_H * s.freq_Hz);

    // --- 2) відношення витків: Np/Ns = (Vmin·D) / (Vsec·(1−D)) ---
    r.turns_ratio = VD / (Vsec * (1.0f - D));

    // --- 3) витки первинної на НЕнасичення (угору — виток лише цілий) ---
    float np_min = (r.lp_primary_H * r.i_peak_A) / (s.b_work_T * s.core_Ae_m2);
    r.np_turns = (int)ceilf(np_min);

    // вторинна за відношенням (теж угору) і параметр осердя AL
    r.ns_turns = (int)ceilf((float)r.np_turns / r.turns_ratio);
    r.al_nH_per_t2 = (r.lp_primary_H * 1e9f) / ((float)r.np_turns * r.np_turns);

    // --- 4) діючі струми трикутних імпульсів і перерізи проводу ---
    r.i_pri_rms_A = r.i_peak_A * sqrtf(D / 3.0f);
    float i_sec_peak = r.i_peak_A * r.turns_ratio;     // пік вторинної
    r.i_sec_rms_A = i_sec_peak * sqrtf((1.0f - D) / 3.0f);
    r.wire_pri_mm2 = r.i_pri_rms_A / s.j_density_Apmm2;
    r.wire_sec_mm2 = r.i_sec_rms_A / s.j_density_Apmm2;

    // --- відбита напруга на ключі (на найвищому вході) ---
    r.reflected_V = Vsec * r.turns_ratio;
    r.vds_peak_V  = s.vin_max_V + r.reflected_V * (1.0f + LEAKAGE_SPIKE_MARGIN);

    // --- поріг для прошивки: це і є піковий струм, під який мотали витки ---
    r.i_peak_threshold_A = r.i_peak_A;

    r.valid = true;
    return r;
}
