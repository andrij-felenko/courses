/* Структура експериментального вимірювання точки діаграми Рагоне (C) */
typedef struct {
    double discharge_current_a;     /* Струм розряджання (Ампер) */
    double terminal_voltage_v;      /* Середня робоча напруга під навантаженням (Вольт) */
    double c_rate;                  /* Кратність розрядного струму (C) */
    double specific_power_w_kg;     /* Виміряна питома потужність (Вт/кг) */
    double specific_energy_wh_kg;   /* Виміряна питома енергія (Вт·год/кг) */
    double volumetric_power_w_l;    /* Об'ємна густина потужності (Вт/л) */
    double volumetric_energy_wh_l;  /* Об'ємна густина енергії (Вт·год/л) */
    double internal_resistance_ohm; /* Виміряний омічний опір при імпульсі (Ом) */
    double discharge_time_seconds;  /* Час розряджання до напруги відсічки (с) */
    double temperature_celsius;     /* Температура осередку під час тесту (°C) */
    int cutoff_reached;             /* Прапорець досягнення напруги відсічки (1/0) */
} RagoneDataPoint;

/* Структура паспортного опису накопичувального осередку */
typedef struct {
    char cell_id[64];               /* Унікальний ідентифікатор моделі */
    char chemistry_type[32];        /* Хімічний тип (наприклад, "NMC_811", "LFP", "EDLC") */
    double nominal_voltage_v;       /* Номінальна напруга (В) */
    double max_voltage_v;           /* Напруга повного заряду (В) */
    double cutoff_voltage_v;        /* Напруга відсічки (В) */
    double capacity_ah;             /* Номінальна ємність (А·год) */
    double mass_kg;                 /* Повна маса осередку (кг) */
    double volume_liters;           /* Повний об'єм осередку (літри) */
    double r_internal_dc_ohm;       /* Внутрішній опір постійному струму (Ом) */
} EnergyStorageCell;
