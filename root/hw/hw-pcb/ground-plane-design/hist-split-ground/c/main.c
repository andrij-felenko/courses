// стрибок цифрового струму на перемичці кристал→ніжка
const double L_bond = 2e-9;      // нГн, типова перемичка
const double dI      = 20e-3;    // А, сплеск цифрового струму
const double t_r     = 4e-9;     // с, фронт

double didt = dI / t_r;          // = 5.0e6 А/с
double V_bond = L_bond * didt;   // = 1.0e-2 В = 10 мВ стрибка «землі»

// ціна для 16-бітного АЦП з опорними 4 В:
double LSB = 4.0 / 65536.0;      // = 6.1e-5 В ≈ 61 мкВ — один молодший розряд
double lost = V_bond / LSB;      // ≈ 164 LSB
