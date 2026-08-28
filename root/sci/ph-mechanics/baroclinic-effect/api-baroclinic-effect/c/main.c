typedef struct {
    size_t nx;                     /* Кількість вузлів по осі X (зональний напрямок) */
    size_t ny;                     /* Кількість вузлів по осі Y (меридіональний напрямок) */
    size_t nz;                     /* Кількість вузлів по осі Z (вертикальний напрямок) */
    double dx;                     /* Крок сітки по осі X (метри) */
    double dy;                     /* Крок сітки по осі Y (метри) */
    double dz;                     /* Крок сітки по осі Z (метри, для z-рівнів) */
    double latitude_deg;           /* Опорна географічна широта у градусах (-90..+90) */
    double coriolis_f0;            /* Параметр Коріоліса f0 (1/с), якщо 0 — рахується з latitude_deg */
    double gravity_g;              /* Прискорення вільного падіння (за замовчуванням 9.80665 м/с²) */
    baroclinic_coord_type_t coord; /* Тип вертикальної координати */
    baroclinic_bc_type_t bc;       /* Тип граничних умов */
    baroclinic_fd_order_t fd_order;/* Порядок скінченних різниць */
} baroclinic_grid_config_t;
