#include <math.h>
#include <stdbool.h>

// Вхідне ТЗ на трансформатор flyback (DCM). Одиниці СІ, крім частоти (Гц)
// і густини струму (А/мм²) — як підписано.
typedef struct {
    float vin_min_V;     // найнижчий вхід Vвх(min), В — найважчий режим
    float vin_max_V;     // найвищий вхід Vвх(max), В — найвища напруга на ключі
    float vout_V;        // бажаний вихід Vвих, В
    float iout_A;        // бажаний вихідний струм Iвих, А
    float vdiode_V;      // падіння на вторинному діоді Vд, В (≈0.5…0.7)
    float freq_Hz;       // частота перемикання f, Гц
    float duty_target;   // цільова шпаруватість D на нижньому вході (0…1)
    float efficiency;    // ККД η (0…1)
    float core_Ae_m2;    // переріз осердя Ae, м² (з паспорта осердя)
    float b_work_T;      // робоча межа потоку Bроб, Тл (нижче Bнас, із запасом)
    float bv_switch_V;   // що тримає ключ BV_DSS, В — для перевірки відбитої напруги
    float j_density_Apmm2; // допустима густина струму J, А/мм² (зазвичай 4…6)
} flyback_spec_t;
