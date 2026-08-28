// Ставить прапорці режиму за вже порахованими числами. Окремо від арифметики,
// щоб логіку перевірок було видно й перевіряти незалежно.
void flyback_check(flyback_spec_t s, flyback_result_t *r)
{
    if (!r->valid) return;

    // (а) чи витримає ключ пік напруги на стоку? (із запасом 15 % від BV_DSS)
    r->switch_overvolt = (s.bv_switch_V > 0.0f) &&
                         (r->vds_peak_V > s.bv_switch_V * 0.85f);

    // (б) межа DCM/CCM на НИЖНЬОМУ вході (найважчий режим).
    // Потрібна шпаруватість, щоб віддати Pвх у DCM при цій Lпр:
    //   Dпотр = √(2·Lпр·Pвх·f) / Vmin
    // Якщо вона перевищує задану D — у DCM потужність уже не влазить → CCM.
    float Pin = (s.vout_V * s.iout_A) / s.efficiency;
    r->duty_required = sqrtf(2.0f * r->lp_primary_H * Pin * s.freq_Hz) /
                       s.vin_min_V;
    // невеликий допуск, бо за побудовою Dпотр ≈ D на межі; CCM — коли помітно вище
    r->ccm_risk = (r->duty_required > s.duty_target * 1.02f);

    // (в) шпаруватість підозріло близька до 1 — паузи на скид майже нема,
    // DCM практично недосяжний; натяк переглянути ТЗ або взяти CCM свідомо.
    r->duty_unrealistic = (s.duty_target > 0.75f);
}
