// Властивості міді (СІ), усталені довідкові значення
float rho_m = 8960.0f;    // густина, кг/м³
float c     = 385.0f;     // питома теплоємність при 20 °C, Дж/(кг·К)
float Lf    = 205000.0f;  // прихована теплота плавлення, Дж/кг
float Tmelt = 1085.0f;    // точка плавлення, °C
float T0    = 20.0f;      // старт, °C
// Питомий опір: ρ(T) = ρ20·(1 + α·(T−20)), ρ20 = 1.68e−8 Ом·м, α = 0.00393/К
float rho20 = 1.68e-8f;
float alpha = 0.00393f;

// Інтеграл ∫ (δ·c / ρ(T)) dT  чисельно, у А²·с/м⁴
double action = 0.0;
int N = 100000;
double dT = (Tmelt - T0) / N;
for (int i = 0; i < N; i++) {
    double T   = T0 + (i + 0.5) * dT;
    double rho = rho20 * (1.0 + alpha * (T - 20.0));
    action += (rho_m * c / rho) * dT;         // ~8.50e16 А²·с/м⁴
}
// А²·с/м⁴ → А²·с/мм⁴ : поділити на 1e12 (1 м⁴ = 1e12 мм⁴)
double K_melt = action / 1e12;                // ≈ 85 000 А²·с/мм⁴

// Додатковий член: щоб не просто дійти до 1085 °C, а й РОЗПЛАВИТИ
double rho_at_melt = rho20 * (1.0 + alpha * (Tmelt - 20.0));
double K_latent = (rho_m * Lf / rho_at_melt) / 1e12;   // ≈ 21 000 А²·с/мм⁴
double K_total  = K_melt + K_latent;                    // ≈ 106 000 А²·с/мм⁴
