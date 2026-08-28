// Вердикт: який клас клампу підходить за порахованими числами.
typedef enum {
    CLAMP_SIMPLE_DIODE = 0, // простого гасного діода досить за швидкістю
    CLAMP_NEED_ZENER_TVS,   // діод не встигає; потрібен Зенер/TVS (швидке вимкнення)
    CLAMP_AVALANCHE_OK,     // можна без зовнішнього клампу: ключ переживе лавину
    CLAMP_INFEASIBLE        // вимогу не вдовольнити цим ключем (див. прапорці)
} clamp_verdict_t;

// Підсумок розрахунку клампу.
typedef struct {
    double delta_V;          // потрібна різниця V_кламп − V_жив, В
    double clamp_V;          // напруга клампу V_кламп, В
    double energy_J;         // одинична енергія поля ½·L·I², Дж
    double avg_power_W;      // середня потужність у ШІМ ½·L·I²·f, Вт (0 якщо f=0)
    double peak_power_W;     // пікова потужність V_кламп·I₀, Вт
    double required_eas_J;   // потрібна лавинна енергія ключа (з множником), Дж
    double diode_decay_s;    // природний час спаду з простим діодом ≈ 5·L/R, с

    clamp_verdict_t verdict; // рекомендований клас клампу

    bool clamp_exceeds_bv;   // ПРАПОРЕЦЬ: потрібний кламп вищий за BV_DSS ключа
    bool pwm_overheat_risk;  // ПРАПОРЕЦЬ: середня потужність надто велика для супресора
    bool valid;              // false = вхідні безглузді, решта полів недійсна
} clamp_result_t;
