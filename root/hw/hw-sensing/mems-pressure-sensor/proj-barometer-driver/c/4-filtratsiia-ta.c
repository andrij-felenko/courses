void baro_process_sample(MemsBarometer *dev, double raw_p_pa, double temp_c,
                         double *out_filtered_p, double *out_altitude_m) {
    if (!dev->is_initialized) {
        dev->filtered_pressure_pa = raw_p_pa;
        dev->is_initialized = true;
    } else {
        // Експоненційне IIR-згладжування: P_fil = (1 - alpha) * P_fil + alpha * P_raw
        dev->filtered_pressure_pa += dev->iir_alpha * (raw_p_pa - dev->filtered_pressure_pa);
    }

    if (out_filtered_p) {
        *out_filtered_p = dev->filtered_pressure_pa;
    }

    if (out_altitude_m) {
        double p_ratio = dev->filtered_pressure_pa / dev->qnh_pa;
        // Барометрична формула висоти ISA (ICAO)
        *out_altitude_m = 44330.77 * (1.0 - pow(p_ratio, 0.190263));
    }
}
