#include <stdio.h>
#include <stdbool.h>

#define MAX_RAILS 8

typedef enum {
    REG_BUCK,
    REG_LDO,
    REG_ISOLATED_DCDC
} regulator_type_t;

typedef struct {
    const char *name;
    regulator_type_t type;
    float v_in;          /* Вхідна напруга, В */
    float v_out;         /* Вихідна напруга, В */
    float i_load_max;    /* Максимальний струм навантаження, А */
    float i_limit;       /* Паспортний ліміт струму регулятора, А */
    float efficiency;    /* ККД (0.0 .. 1.0) для DC-DC */
    float theta_ja;      /* Тепловий опір кристал-середовище, °C/Вт */
} power_rail_t;

typedef struct {
    float p_out_w;
    float p_loss_w;
    float t_junction_c;
    bool is_overcurrent;
    bool is_overheated;
} rail_status_t;

static rail_status_t validate_rail(const power_rail_t *rail, float t_ambient) {
    rail_status_t status = {0};
    
    status.p_out_w = rail->v_out * rail->i_load_max;
    status.is_overcurrent = (rail->i_load_max > rail->i_limit);

    if (rail->type == REG_LDO) {
        status.p_loss_w = (rail->v_in - rail->v_out) * rail->i_load_max;
    } else {
        if (rail->efficiency > 0.01f) {
            float p_in = status.p_out_w / rail->efficiency;
            status.p_loss_w = p_in - status.p_out_w;
        } else {
            status.p_loss_w = status.p_out_w * 0.2f;
        }
    }

    status.t_junction_c = t_ambient + (status.p_loss_w * rail->theta_ja);
    status.is_overheated = (status.t_junction_c > 125.0f);

    return status;
}

int main(void) {
    const float ambient_temp = 60.0f; /* Промислове середовище +60 °C */

    power_rail_t rails[MAX_RAILS] = {
        {"24V->5V Buck",    REG_BUCK,          24.0f, 5.0f, 2.50f, 3.00f, 0.91f, 35.0f},
        {"5V->3.3V Buck",   REG_BUCK,           5.0f, 3.3f, 1.50f, 2.00f, 0.94f, 45.0f},
        {"5V->1.2V Core",   REG_BUCK,           5.0f, 1.2f, 1.20f, 1.50f, 0.88f, 50.0f},
        {"5V->3.3V LDO",    REG_LDO,            5.0f, 3.3f, 0.15f, 0.30f, 0.66f, 62.0f},
        {"5V->5V_ISO DCDC", REG_ISOLATED_DCDC,  5.0f, 5.0f, 0.20f, 0.25f, 0.78f, 70.0f}
    };

    printf("=== Звіт валідації бюджету живлення блок-схеми (T_amb = %.1f C) ===\n", ambient_temp);
    for (size_t i = 0; i < 5; ++i) {
        rail_status_t st = validate_rail(&rails[i], ambient_temp);
        printf("[%s]\n", rails[i].name);
        printf("  P_out = %5.2f Вт | P_loss = %5.2f Вт | T_j = %5.1f °C", 
               st.p_out_w, st.p_loss_w, st.t_junction_c);
        
        if (st.is_overcurrent) printf(" -> [ПОМИЛКА: ПЕРЕВАНТАЖЕННЯ ЗА СТРУМОМ]");
        if (st.is_overheated)  printf(" -> [ПОМИЛКА: ТЕПЛОВИЙ ПЕРЕГРІВ]");
        if (!st.is_overcurrent && !st.is_overheated) printf(" -> [НОРМА]");
        printf("\n");
    }

    return 0;
}
