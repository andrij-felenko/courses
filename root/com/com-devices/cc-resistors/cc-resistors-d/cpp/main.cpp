// Поріги на вході АЦП після дільника 1:1 (мВ)
#define CC_TH_LOW   330   // межа «типова» / «1.5 А»
#define CC_TH_HIGH  620   // межа «1.5 А» / «3.0 А»

#define CC1_ADC_PIN  34
#define CC2_ADC_PIN  35

// Повертає стелю струму порту в міліамперах
int read_cc_current_limit(void) {
    // Беремо більшу з двох CC: активна та, де кабель з'єднав CC джерела.
    int v1 = analogReadMilliVolts(CC1_ADC_PIN);
    int v2 = analogReadMilliVolts(CC2_ADC_PIN);
    int v  = (v1 > v2) ? v1 : v2;

    if (v >= CC_TH_HIGH) return 3000;   // 3.0 А
    if (v >= CC_TH_LOW)  return 1500;   // 1.5 А
    return 900;                         // типовий USB: 0.5–0.9 А
}

void setup() {
    int limit_mA = read_cc_current_limit();

    // Зарядка тягне 1200 мА — вмикаємо лише якщо порт обіцяє запас.
    if (limit_mA >= 1500) {
        enable_battery_charger();       // безпечно: 1.2 А < 1.5 А
    } else {
        // Порт дає максимум 0.9 А — заряджати не можна, просяде VBUS.
        run_low_power_only();
    }
}
