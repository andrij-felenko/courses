// Прогноз глибини просадки під імпульсом струму.
// Обидва опори — з паспорта/fuel-gauge, у мілліомах.
float ocv_mV       = 3700.0f;   // напруга в спокої
float pulse_mA     = 2000.0f;   // амплітуда імпульсу, 2 А
float brownout_mV  = 3000.0f;   // поріг ресету процесора

float r_acir_mohm  = 36.0f;     // те, що дав вимір на 1 кГц
float r_dcir_mohm  = 110.0f;    // те, що дав 2-секундний імпульс

// Просадка = I * R.  (мА * мОм = мкВ, ділимо на 1000 -> мВ)
float sag_acir_mV = pulse_mA * r_acir_mohm / 1000.0f;   // 72 мВ
float sag_dcir_mV = pulse_mA * r_dcir_mohm / 1000.0f;   // 220 мВ

float v_under_acir = ocv_mV - sag_acir_mV;   // 3628 мВ — «усе гаразд»
float v_under_dcir = ocv_mV - sag_dcir_mV;   // 3480 мВ — реальність

bool safe_by_acir = v_under_acir > brownout_mV;   // true  — оманливо
bool safe_by_dcir = v_under_dcir > brownout_mV;   // true  — чесно
