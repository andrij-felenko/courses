#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    double mass;          /* маса пластини, кг */
    double sigma_0;       /* початкова електропровідність при 20°C, См/м */
    double alpha_temp;    /* температурний коефіцієнт опору, 1/K */
    double c_heat;        /* питома теплоємність, Дж/(кг·K) */
    double thickness;     /* товщина пластини, м */
    double length;        /* довжина пластини, м */
    double width;         /* ширина пластини, м */
    double B_field;       /* індукція поля, Тл */
    double field_length;  /* довжина зони поля, м */
    double c_geo;         /* геометричний фактор замикання вихрових струмів */
    double k_air;         /* коефіцієнт опору повітря, Н·с/м */
} PlateSystem;

typedef struct {
    double time;
    double position;
    double velocity;
    double temperature;   /* температура у Кельвінах або Цельсіях */
    double force;
    double power_dissipated;
} SimulationState;

/* Обчислення геометрії перекриття пластини та зони поля */
static double compute_active_area(const PlateSystem *sys, double pos) {
    double entry = pos;
    double exit_edge = pos - sys->length;
    
    double start_in = (entry < 0.0) ? 0.0 : ((entry > sys->field_length) ? sys->field_length : entry);
    double end_in = (exit_edge < 0.0) ? 0.0 : ((exit_edge > sys->field_length) ? sys->field_length : exit_edge);
    
    double active_len = start_in - end_in;
    if (active_len < 0.0) active_len = 0.0;
    
    return active_len * sys->width;
}

/* Крок симуляції методом Ейлера-Кромєра з тепловим зворотним зв'язком */
SimulationState step_simulation(const PlateSystem *sys, SimulationState state, double dt) {
    double active_area = compute_active_area(sys, state.position);
    
    /* Поточна провідність з урахуванням температури */
    double current_sigma = sys->sigma_0 / (1.0 + sys->alpha_temp * (state.temperature - 20.0));
    
    /* Сила гальмування Ленца */
    double f_eddy = sys->c_geo * current_sigma * sys->thickness * active_area * 
                    (sys->B_field * sys->B_field) * state.velocity;
    
    double f_air = sys->k_air * state.velocity * fabs(state.velocity);
    double total_f = -(f_eddy + f_air);
    
    double accel = total_f / sys->mass;
    
    /* Потужність нагріву та ріст температури */
    double power = f_eddy * state.velocity;
    double dT = (power * dt) / (sys->mass * sys->c_heat);
    
    SimulationState next_state;
    next_state.time = state.time + dt;
    next_state.velocity = state.velocity + accel * dt;
    if (next_state.velocity < 0.0) next_state.velocity = 0.0;
    
    next_state.position = state.position + next_state.velocity * dt;
    next_state.temperature = state.temperature + dT;
    next_state.force = total_f;
    next_state.power_dissipated = power;
    
    return next_state;
}

int main(void) {
    PlateSystem copper = {
        .mass = 0.5,            /* 500 грам */
        .sigma_0 = 5.8e7,       /* мідь при 20°C */
        .alpha_temp = 0.00393,
        .c_heat = 385.0,
        .thickness = 0.005,     /* 5 мм */
        .length = 0.15,         /* 15 см */
        .width = 0.10,          /* 10 см */
        .B_field = 0.8,         /* 0.8 Тесла */
        .field_length = 0.10,   /* зона поля 10 см */
        .c_geo = 0.25,
        .k_air = 0.01
    };

    SimulationState state = {
        .time = 0.0,
        .position = -0.05,      /* 5 см до входу у поле */
        .velocity = 5.0,        /* 5 м/с */
        .temperature = 20.0,    /* 20°C */
        .force = 0.0,
        .power_dissipated = 0.0
    };

    double dt = 0.0001; /* 100 мікросекунд */
    printf("Час(с)\tПоз(м)\tШвидк(м/с)\tТемп(C)\tСила(Н)\tПотужність(Вт)\n");

    for (int step = 0; step <= 2000; ++step) {
        if (step % 200 == 0) {
            printf("%.4f\t%.4f\t%.4f\t%.2f\t%.2f\t%.2f\n",
                   state.time, state.position, state.velocity, 
                   state.temperature, state.force, state.power_dissipated);
        }
        state = step_simulation(&copper, state, dt);
        if (state.velocity <= 0.001) break;
    }

    return 0;
}
