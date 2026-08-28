double compute_speed_of_sound(double T, double V, double molar_mass) const {
    double dPdT = compute_dPdT(T, V);
    double dPdV = (gas_.pressure(T, V + step_V_) - gas_.pressure(T, V - step_V_)) / (2.0 * step_V_);
    
    double term_iso = -dPdV;
    double term_ad  = (T / gas_.Cv_ideal) * (dPdT * dPdT);
    
    double c2 = (V * V / molar_mass) * (term_iso + term_ad);
    return std::sqrt(c2);
}
