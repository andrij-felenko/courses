struct ValveResult {
    double T_out;
    double isenthalpic_cooling;
    bool condensation_occurred;
};

ValveResult simulate_expansion_valve(double T_in, double P_in, double P_out) const {
    // 1. Збереження вхідної ентальпії H_in = H(T_in, P_in)
    double H_in = compute_enthalpy(T_in, P_in);
    
    // 2. Ітераційний пошук T_out такої, що H(T_out, P_out) = H_in (метод Ньютона)
    double T_curr = T_in;
    for (int iter = 0; iter < 20; ++iter) {
        double H_curr = compute_enthalpy(T_curr, P_out);
        double dHdT = compute_Cp(T_curr, P_out);
        double f = H_curr - H_in;
        if (std::abs(f) < 1e-5) break;
        T_curr -= f / dHdT;
    }
    
    bool condensed = (T_curr < critical_temperature && P_out < critical_pressure);
    return ValveResult{
        .T_out = T_curr,
        .isenthalpic_cooling = T_in - T_curr,
        .condensation_occurred = condensed
    };
}
