#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* ── Типи даних для аналізу кварцового генератора ───────────────────── */
typedef struct {
    double freq_hz;            /* Номінальна частота генератора, Гц */
    double load_cap_pf;        /* Паспортна ємність навантаження CL, пФ */
    double esr_ohm;            /* Еквівалентний послідовний опір ESR, Ом */
    double shunt_cap_pf;       /* Статична ємність корпусу та пластини C0, пФ */
    double drive_level_max_uw; /* Максимальна допустима потужність, мкВт */
} PcbCrystalSpec;

typedef struct {
    double gm_uA_per_V;        /* Крутизна інвертора gm, мкА/В */
    double vdd_volts;          /* Напруга живлення VDD, В */
    double pcb_stray_pf;       /* Паразитна ємність монтажу на платі, пФ */
} PcbDriverSpec;

typedef struct {
    double c_ext_pf;           /* Розрахунковий номінал C1 = C2, пФ */
    double gm_crit_uA_per_V;   /* Критична крутизна збудження, мкА/В */
    double gain_margin;        /* Коефіцієнт запасу підсилення */
    double drive_level_uw;     /* Оціночна розсіювана потужність, мкВт */
    double rd_opt_ohm;         /* Оптимальний послідовний демпфер Rd, Ом */
    bool is_startup_reliable;  /* Критерій стійкого старту (Gain Margin >= 5) */
    bool is_drive_safe;        /* Критерій безпеки за потужністю (P <= P_max) */
} PcbCrystalDiagnostic;

/* ── Типи даних для аналізу вхідного тракту АЦП ─────────────────────── */
typedef struct {
    unsigned int resolution_bits; /* Розрядність перетворювача (10..24 біт) */
    double c_sample_pf;           /* Внутрішня ємність S&H C_sample, пФ */
    double r_on_ohm;              /* Внутрішній опір ключа вибірки, Ом */
    double t_acq_configured_ns;   /* Сконфігурований час фази вибірки, нс */
    double r_ext_ohm;             /* Зовнішній резистор фільтра R_ext, Ом */
    double c_ext_pf;              /* Зовнішній конденсатор фільтра C_ext, пФ */
} PcbAdcSpec;

typedef struct {
    double cap_ratio;             /* Співвідношення ємностей C_ext / C_sample */
    double tau_ns;                /* Стала часу контуру заряду, нс */
    double t_acq_min_ns;          /* Мінімальний час вибірки для похибки <0.5 LSB, нс */
    double settling_error_lsb;    /* Фактична похибка встановлення в LSB */
    double cutoff_freq_khz;       /* Частота зрізу RC-фільтра, кГц */
    bool is_cap_ratio_ok;         /* Чи достатня зовнішня ємність (Ratio >= 20) */
    bool is_settling_complete;    /* Чи завершено перехідний процес (<0.5 LSB) */
} PcbAdcDiagnostic;

/* ── Типи даних для аналізу феритового фільтра VDDA ─────────────────── */
typedef struct {
    double bead_inductance_uh;    /* Низькочастотна індуктивність L, мкГн */
    double bead_rdc_ohm;          /* Активний опір постійному струму R_dc, Ом */
    double cap_uf;                /* Ємність блокувального конденсатора, мкФ */
    double cap_esr_ohm;           /* Власний ESR конденсатора, Ом */
} PcbFerriteSpec;

typedef struct {
    double f_res_khz;             /* Резонансна частота коливального контуру, кГц */
    double q_factor;              /* Коефіцієнт добротності контуру Q */
    double peak_gain_db;          /* Пік підсилення завад на резонансі, дБ */
    double rdamp_needed_ohm;      /* Необхідний додатковий опір демпфування, Ом */
    bool is_damped;               /* Чи задемпфовано контур (Q <= 0.707) */
} PcbFerriteDiagnostic;

/* ── Обчислювальні функції ──────────────────────────────────────────── */
bool pcb_calc_crystal(const PcbCrystalSpec *xtal,
                      const PcbDriverSpec *drv,
                      PcbCrystalDiagnostic *out)
{
    if (!xtal || !drv || !out) return false;
    if (xtal->freq_hz <= 0.0 || xtal->load_cap_pf <= drv->pcb_stray_pf) return false;

    /* Розрахунок зовнішніх ємностей */
    out->c_ext_pf = 2.0 * (xtal->load_cap_pf - drv->pcb_stray_pf);

    /* Розрахунок критичної крутизни */
    double omega = 2.0 * M_PI * xtal->freq_hz;
    double c_tot_f = (xtal->shunt_cap_pf + xtal->load_cap_pf) * 1e-12;
    double gm_crit_si = 4.0 * xtal->esr_ohm * (omega * omega) * (c_tot_f * c_tot_f);
    out->gm_crit_uA_per_V = gm_crit_si * 1e6;

    /* Запас по підсиленню */
    out->gain_margin = drv->gm_uA_per_V / out->gm_crit_uA_per_V;
    out->is_startup_reliable = (out->gain_margin >= 5.0);

    /* Оптимальний послідовний демпфер Rd */
    double c2_f = out->c_ext_pf * 1e-12;
    out->rd_opt_ohm = 1.0 / (omega * c2_f);

    /* Оцінка розсіюваної потужності */
    double i_drive = M_PI * xtal->freq_hz * c_tot_f * drv->vdd_volts;
    out->drive_level_uw = (2.0 * xtal->esr_ohm * i_drive * i_drive) * 1e6;
    out->is_drive_safe = (out->drive_level_uw <= xtal->drive_level_max_uw);

    return true;
}

bool pcb_calc_adc(const PcbAdcSpec *adc, PcbAdcDiagnostic *out)
{
    if (!adc || !out) return false;
    if (adc->resolution_bits == 0 || adc->c_sample_pf <= 0.0) return false;

    out->cap_ratio = adc->c_ext_pf / adc->c_sample_pf;
    out->is_cap_ratio_ok = (out->cap_ratio >= 20.0);

    double r_tot = adc->r_ext_ohm + adc->r_on_ohm;
    double c_sample_f = adc->c_sample_pf * 1e-12;
    double tau_s = r_tot * c_sample_f;
    out->tau_ns = tau_s * 1e9;

    double k_settle = (adc->resolution_bits + 1) * 0.69314718056;
    out->t_acq_min_ns = k_settle * out->tau_ns;

    double t_acq_s = adc->t_acq_configured_ns * 1e-9;
    double exp_val = exp(-t_acq_s / tau_s);
    double quantums = pow(2.0, (double)adc->resolution_bits);
    out->settling_error_lsb = quantums * exp_val;
    out->is_settling_complete = (out->settling_error_lsb < 0.5);

    double c_ext_f = adc->c_ext_pf * 1e-12;
    if (adc->r_ext_ohm > 0.0 && c_ext_f > 0.0) {
        out->cutoff_freq_khz = (1.0 / (2.0 * M_PI * adc->r_ext_ohm * c_ext_f)) / 1e3;
    } else {
        out->cutoff_freq_khz = 0.0;
    }

    return true;
}

bool pcb_calc_ferrite(const PcbFerriteSpec *fb, PcbFerriteDiagnostic *out)
{
    if (!fb || !out) return false;
    if (fb->bead_inductance_uh <= 0.0 || fb->cap_uf <= 0.0) return false;

    double l_h = fb->bead_inductance_uh * 1e-6;
    double c_f = fb->cap_uf * 1e-6;
    double r_tot = fb->bead_rdc_ohm + fb->cap_esr_ohm;

    out->f_res_khz = (1.0 / (2.0 * M_PI * sqrt(l_h * c_f))) / 1e3;
    out->q_factor = (1.0 / r_tot) * sqrt(l_h / c_f);
    out->is_damped = (out->q_factor <= 0.70710678);

    out->peak_gain_db = (out->q_factor > 1.0) ? (20.0 * log10(out->q_factor)) : 0.0;

    double r_crit = sqrt(2.0 * l_h / c_f);
    out->rdamp_needed_ohm = (r_crit > fb->bead_rdc_ohm) ? (r_crit - fb->bead_rdc_ohm) : 0.0;

    return true;
}

/* ── Головна демонстраційна програма ────────────────────────────────── */
int main(void)
{
    printf("=======================================================================\n");
    printf("     ПОВНИЙ ІНЖЕНЕРНИЙ ЗВІТ ДІАГНОСТИКИ АНАЛОГОВОГО ТРАКТУ (C99)      \n");
    printf("=======================================================================\n\n");

    /* 1. Автомобільний резонатор HSE 16.0 МГц */
    PcbCrystalSpec hse_spec = {
        .freq_hz = 16.0e6,
        .load_cap_pf = 12.0,
        .esr_ohm = 35.0,
        .shunt_cap_pf = 3.0,
        .drive_level_max_uw = 100.0
    };
    PcbDriverSpec hse_driver = {
        .gm_uA_per_V = 2500.0,
        .vdd_volts = 3.3,
        .pcb_stray_pf = 3.5
    };
    PcbCrystalDiagnostic hse_diag;
    if (pcb_calc_crystal(&hse_spec, &hse_driver, &hse_diag)) {
        printf("▼ [МОДУЛЬ 1: Кварцовий резонатор HSE 16.0 МГц]\n");
        printf("  - Розрахункові C1, C2:     %.2f пФ (рекомендований E24: 18 пФ C0G)\n", hse_diag.c_ext_pf);
        printf("  - Критична крутизна:       %.2f мкА/В\n", hse_diag.gm_crit_uA_per_V);
        printf("  - Коефіцієнт Gain Margin:  %.2f (вимога >= 5.0: %s)\n",
               hse_diag.gain_margin, hse_diag.is_startup_reliable ? "СТІЙКИЙ" : "ЗРИВ");
        printf("  - Послідовний демпфер Rd:  %.1f Ом (рекомендовано 470 Ом 0402)\n", hse_diag.rd_opt_ohm);
        printf("  - Потужність збудження:    %.2f мкВт (ліміт: %.1f мкВт, %s)\n\n",
               hse_diag.drive_level_uw, hse_spec.drive_level_max_uw,
               hse_diag.is_drive_safe ? "НОРМА" : "ПЕРЕВАНТАЖЕННЯ");
    }

    /* 2. Вхідний тракт 16-розрядного SAR АЦП AD7685 */
    PcbAdcSpec adc_spec = {
        .resolution_bits = 16,
        .c_sample_pf = 15.0,
        .r_on_ohm = 400.0,
        .t_acq_configured_ns = 150.0,
        .r_ext_ohm = 47.0,
        .c_ext_pf = 1000.0
    };
    PcbAdcDiagnostic adc_diag;
    if (pcb_calc_adc(&adc_spec, &adc_diag)) {
        printf("▼ [МОДУЛЬ 2: Вхідний тракт 16-розрядного SAR АЦП]\n");
        printf("  - Співвідношення Cext/Csample: %.1f (вимога >= 20: %s)\n",
               adc_diag.cap_ratio, adc_diag.is_cap_ratio_ok ? "НОРМА" : "МАЛА ЄМНІСТЬ");
        printf("  - Постійна часу вибірки tau:   %.2f нс\n", adc_diag.tau_ns);
        printf("  - Мін. необхідний час t_acq:   %.2f нс (сконфігуровано: %.1f нс)\n",
               adc_diag.t_acq_min_ns, adc_spec.t_acq_configured_ns);
        printf("  - Похибка встановлення:        %.6f LSB (вимога < 0.5 LSB: %s)\n",
               adc_diag.settling_error_lsb, adc_diag.is_settling_complete ? "ТОЧНО" : "ПОХИБКА");
        printf("  - Смуга RC-фільтра:            %.2f кГц\n\n", adc_diag.cutoff_freq_khz);
    }

    /* 3. Фільтр живлення VDDA на феритовій намистині */
    PcbFerriteSpec fb_spec = {
        .bead_inductance_uh = 2.2,
        .bead_rdc_ohm = 0.08,
        .cap_uf = 10.0,
        .cap_esr_ohm = 0.005
    };
    PcbFerriteDiagnostic fb_diag;
    if (pcb_calc_ferrite(&fb_spec, &fb_diag)) {
        printf("▼ [МОДУЛЬ 3: Фільтр живлення VDDA на феритовій намистині]\n");
        printf("  - Резонансна частота f_res:    %.2f кГц\n", fb_diag.f_res_khz);
        printf("  - Добротність контуру Q:       %.2f (вимога <= 0.707: %s)\n",
               fb_diag.q_factor, fb_diag.is_damped ? "ЗАКРИТИЧНО" : "РЕЗОНАНСНИЙ СПЛЕСК");
        printf("  - Пік підсилення завад:        +%.2f дБ\n", fb_diag.peak_gain_db);
        printf("  - Необхідний демпфер Rdamp:    %.3f Ом (додати танталовий конденсатор)\n",
               fb_diag.rdamp_needed_ohm);
    }

    printf("=======================================================================\n");
    return 0;
}
