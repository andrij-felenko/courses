#include <stdio.h>
#include <stdbool.h>

/* Ступінь забруднення згідно з IEC 60664-1 */
typedef enum {
    POLLUTION_DEGREE_1 = 1, /* Герметичні корпуси або лаковані плати */
    POLLUTION_DEGREE_2 = 2, /* Побутова та офісна техніка */
    POLLUTION_DEGREE_3 = 3  /* Промислове обладнання з пилом */
} PollutionDegree;

/* Група матеріалу плати за Comparative Tracking Index */
typedef enum {
    MATERIAL_GROUP_I   = 1, /* CTI >= 600 */
    MATERIAL_GROUP_II  = 2, /* 400 <= CTI < 600 */
    MATERIAL_GROUP_IIIA = 3 /* 175 <= CTI < 400 (стандартний FR-4) */
} MaterialGroup;

/* Рівень ізоляції */
typedef enum {
    INSULATION_FUNCTIONAL,
    INSULATION_BASIC,
    INSULATION_REINFORCED
} InsulationType;

/* Розрахунок висотного коефіцієнта за стандартом IEC 60664-1 (Таблиця A.2) */
double calculate_altitude_factor(double altitude_m) {
    if (altitude_m <= 2000.0) return 1.00;
    if (altitude_m <= 3000.0) return 1.14;
    if (altitude_m <= 4000.0) return 1.29;
    if (altitude_m <= 5000.0) return 1.48;
    return 1.70; /* Екстремальні висоти > 5000 м */
}

/* Розрахунок мінімального повітряного зазору (Clearance) у мм */
double calculate_clearance(double v_rms, InsulationType ins_type, double altitude_m) {
    double base_clr = 0.0;
    
    /* Базові значення для категорії перенапруги II (OVC II) */
    if (v_rms <= 150.0) {
        base_clr = 1.0;
    } else if (v_rms <= 300.0) {
        base_clr = (ins_type == INSULATION_REINFORCED) ? 3.0 : 1.5;
    } else {
        base_clr = (ins_type == INSULATION_REINFORCED) ? 6.0 : 3.0;
    }
    
    if (ins_type == INSULATION_FUNCTIONAL) {
        base_clr = 0.5;
    }
    
    double k_alt = calculate_altitude_factor(altitude_m);
    return base_clr * k_alt;
}

/* Розрахунок мінімального шляху витоку (Creepage) у мм */
double calculate_creepage(double v_rms, InsulationType ins_type,
                          PollutionDegree pd, MaterialGroup mg) {
    double base_cr = 0.0;
    
    if (v_rms <= 250.0) {
        if (pd == POLLUTION_DEGREE_1) {
            base_cr = (ins_type == INSULATION_REINFORCED) ? 1.4 : 0.7;
        } else if (pd == POLLUTION_DEGREE_2) {
            switch (mg) {
                case MATERIAL_GROUP_I:
                    base_cr = (ins_type == INSULATION_REINFORCED) ? 3.6 : 1.8;
                    break;
                case MATERIAL_GROUP_II:
                    base_cr = (ins_type == INSULATION_REINFORCED) ? 4.4 : 2.2;
                    break;
                case MATERIAL_GROUP_IIIA:
                default:
                    base_cr = (ins_type == INSULATION_REINFORCED) ? 5.0 : 2.5;
                    break;
            }
        } else { /* PD 3 */
            base_cr = (ins_type == INSULATION_REINFORCED) ? 8.0 : 4.0;
        }
    } else {
        /* Напруга DC-шини 400 В */
        base_cr = (ins_type == INSULATION_REINFORCED) ? 8.0 : 4.0;
    }
    
    return base_cr;
}

int main(void) {
    double v_rms = 250.0;
    double altitude = 3500.0;
    InsulationType ins = INSULATION_REINFORCED;
    PollutionDegree pd = POLLUTION_DEGREE_2;
    MaterialGroup mg = MATERIAL_GROUP_IIIA; /* FR-4 */
    
    double clr = calculate_clearance(v_rms, ins, altitude);
    double crp = calculate_creepage(v_rms, ins, pd, mg);
    
    printf("=== Розрахунок зазорів безпеки друкованої плати (C) ===\n");
    printf("Робоча напруга мережі:        %.1f В RMS\n", v_rms);
    printf("Висота над рівнем моря:       %.0f м\n", altitude);
    printf("Ступінь забруднення:          PD %d\n", (int)pd);
    printf("Матеріал основи:              FR-4 (Група IIIa)\n");
    printf("Тип ізоляції:                 Посилена (Reinforced)\n");
    printf("------------------------------------------------------\n");
    printf("Мінімальний Clearance:        %.2f мм\n", clr);
    printf("Мінімальний Creepage:         %.2f мм\n", crp);
    
    return 0;
}
