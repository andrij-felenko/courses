/* mounting_clearance.c — Розрахунок зон заборони кріплення на C99 */
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define PI 3.14159265358979323846

typedef enum {
    SCREW_M2,
    SCREW_M2_5,
    SCREW_M3,
    SCREW_M4
} ScrewSize;

typedef struct {
    double drill_diameter;      /* Діаметр отвору в платі, мм */
    double head_diameter;       /* Діаметр головки гвинта за DIN, мм */
    double washer_diameter;     /* Діаметр збільшеної шайби DIN 9021, мм */
    double tool_envelope_dia;   /* Діаметр інструмента затяжки, мм */
    double copper_pullback;     /* Мінімальний відступ міді від шайби, мм */
} FastenerProfile;

FastenerProfile get_fastener_profile(ScrewSize size) {
    FastenerProfile prof;
    switch (size) {
        case SCREW_M2:
            prof.drill_diameter    = 2.2;
            prof.head_diameter     = 3.8;
            prof.washer_diameter   = 5.0;
            prof.tool_envelope_dia = 7.0;
            prof.copper_pullback   = 0.5;
            break;
        case SCREW_M2_5:
            prof.drill_diameter    = 2.7;
            prof.head_diameter     = 4.5;
            prof.washer_diameter   = 6.5;
            prof.tool_envelope_dia = 8.5;
            prof.copper_pullback   = 0.6;
            break;
        case SCREW_M3:
            prof.drill_diameter    = 3.2;
            prof.head_diameter     = 5.5;
            prof.washer_diameter   = 7.0;
            prof.tool_envelope_dia = 10.0;
            prof.copper_pullback   = 0.8;
            break;
        case SCREW_M4:
        default:
            prof.drill_diameter    = 4.3;
            prof.head_diameter     = 7.0;
            prof.washer_diameter   = 9.0;
            prof.tool_envelope_dia = 12.5;
            prof.copper_pullback   = 1.0;
            break;
    }
    return prof;
}

typedef struct {
    double cmp_keepout_radius;   /* Радіус зони заборони компонентів */
    double copper_keepout_radius;/* Радіус зони заборони міді на внутрішніх шарах */
    double tool_clearance_radius;/* Радіус вільного доступу інструмента */
} MountingKeepoutRadii;

MountingKeepoutRadii calculate_mounting_keepouts(ScrewSize size, bool use_large_washer) {
    FastenerProfile prof = get_fastener_profile(size);
    MountingKeepoutRadii res;
    
    double effective_mech_dia = use_large_washer ? prof.washer_diameter : prof.head_diameter;
    
    /* Запас безпеки на люфт та зміщення шайби: +0.3 мм на радіус */
    res.cmp_keepout_radius    = (effective_mech_dia / 2.0) + 0.3;
    res.copper_keepout_radius = (effective_mech_dia / 2.0) + prof.copper_pullback;
    res.tool_clearance_radius = prof.tool_envelope_dia / 2.0;
    
    return res;
}

int main(void) {
    MountingKeepoutRadii m3 = calculate_mounting_keepouts(SCREW_M3, true);
    printf("Кріплення M3 із шайбою DIN 125/9021:\n");
    printf(" - Радіус заборони компонентів (Component Keepout): %.2f мм\n", m3.cmp_keepout_radius);
    printf(" - Радіус відступу міді (Copper Pullback):          %.2f мм\n", m3.copper_keepout_radius);
    printf(" - Радіус конверта викрутки (Tool Envelope):        %.2f мм\n", m3.tool_clearance_radius);
    return 0;
}
