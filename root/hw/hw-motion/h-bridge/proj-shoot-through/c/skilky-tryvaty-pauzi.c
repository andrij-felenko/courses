// Розрахунок мертвого часу й переведення в такти регістра DTG.
const double Qgd   = 15e-9;     // заряд активної ділянки затвора, Кл
const double Rg    = 10.0;      // опір розряду затвора, Ом
const double Vdrv  = 10.0;      // напруга привода затвора, В
const double f_tim = 168e6;     // частота лічби таймера, Гц

double i_discharge = Vdrv / Rg;             // = 1.0 А  — струм розряду затвора
double t_off       = Qgd / i_discharge;     // = 15 нс  — час вимикання ключа
double t_dead      = 2.0 * t_off;           // = 30 нс  — пауза з 2× запасом
uint8_t dtg = (uint8_t)(t_dead * f_tim + 0.5);  // = round(30e-9 * 168e6) = 5 тактів
