// Поріг середньої потужності (Вт), вище якого окремий супресор (Зенер/TVS)
// як основний шлях розсіяння перегріється. Орієнтир для дрібних SMD-супресорів;
// під конкретну деталь і тепловідвід підправте за даташитом.
#define SUPPRESSOR_AVG_POWER_LIMIT_W  5.0

// Запас між потрібним клампом і пробивною напругою ключа: лишаємо 15 %.
#define BV_DERATING  0.85

clamp_result_t clamp_size(clamp_input_t in)
{
    clamp_result_t r = {0};
    r.valid = false;

    // --- захист від безглуздих вхідних: не вгадуємо ---
    if (in.inductance_H <= 0.0 || in.current_A <= 0.0 ||
        in.t_off_target_s <= 0.0 || in.bv_dss_V <= 0.0 ||
        in.supply_V < 0.0 || in.bv_dss_V <= in.supply_V) {
        return r;            // bv_dss <= supply теж безглуздя: ключ не тримає й живлення
    }

    // --- 1. енергія поля (одинична) ---
    r.energy_J = 0.5 * in.inductance_H * in.current_A * in.current_A;

    // --- 2. різниця напруг і напруга клампу під заданий t_off ---
    r.delta_V = in.inductance_H * in.current_A / in.t_off_target_s;
    r.clamp_V = in.supply_V + r.delta_V;

    // --- 3. пікова потужність: повний струм за повної напруги затиску ---
    r.peak_power_W = r.clamp_V * in.current_A;

    // --- 4. середня потужність: тільки якщо це ШІМ (f > 0) ---
    r.avg_power_W = (in.pwm_freq_Hz > 0.0)
                  ? r.energy_J * in.pwm_freq_Hz
                  : 0.0;

    // --- 5. потрібна лавинна енергія ключа: з множником підкачки ---
    //     E_AS = ½·L·I² · BV_DSS/(BV_DSS − V_жив)
    r.required_eas_J = r.energy_J * in.bv_dss_V / (in.bv_dss_V - in.supply_V);

    // --- природний час спаду з простим діодом ≈ 5·L/R (3…5 τ; беремо 5 з запасом) ---
    r.diode_decay_s = (in.winding_ohm > 0.0)
                    ? 5.0 * in.inductance_H / in.winding_ohm
                    : INFINITY;          // R=0 (надпровідник) — спад нескінченний

    r.valid = true;
    return r;
}
