typedef enum {
    GFD_BC_PERIODIC = 0,    /* Періодичні граничні умови (для замкнених паралелей) */
    GFD_BC_CLAMPED  = 1,    /* Задані фіксовані значення на границях */
    GFD_BC_NEUMANN  = 2     /* Нульовий градієнт (∂q/∂n = 0) на границях */
} gfd_bc_type_t;

typedef struct {
    int use_pvu_units;      /* 1 — виводити в PVU (10^-6 м²·с⁻¹·К·кг⁻¹), 0 — у SI */
    int diff_order;         /* Порядок точності різницевої схеми: 2 або 4 */
    gfd_bc_type_t bc_x;     /* Тип граничних умов за віссю X */
    gfd_bc_type_t bc_y;     /* Тип граничних умов за віссю Y */
    gfd_bc_type_t bc_z;     /* Тип граничних умов за віссю Z */
} gfd_pv_options_t;
