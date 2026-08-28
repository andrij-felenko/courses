typedef struct {
    double x;           /* Осьова координата точки, м */
    double area;        /* Поперечна площа перерізу, м² */
    double mach;        /* Число Маха M */
    double pressure;    /* Статичний тиск P, Па */
    double temp;        /* Статична температура T, К */
    double density;     /* Густина ρ, кг/м³ */
    double vel;         /* Швидкість газу u, м/с */
    double P0_local;    /* Повний тиск у даній точці (ураховує втрати на скачку), Па */
} flow_point_state_t;
