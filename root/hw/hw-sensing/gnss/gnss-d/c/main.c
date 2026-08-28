// Час польоту приймач тримає в наносекундах (ціле — без втрати точності).
// Швидкість світла у вакуумі — метри за наносекунду.
static const double C_M_PER_NS = 0.299792458;   // 1 нс світла ≈ 30 см

double range_from_tof(uint64_t tof_ns) {
    return (double)tof_ns * C_M_PER_NS;          // дальність у метрах
}

uint64_t tof_ns = 67128450ULL;                   // ~67 мс — типова дальність
double range_m  = range_from_tof(tof_ns);        // = 20 124 603 м ≈ 20 125 км

double clock_err_ns = 10.0;                       // годинник збився на 10 нс
double range_bias_m = clock_err_ns * C_M_PER_NS;  // = 3.0 м похибки дальності
