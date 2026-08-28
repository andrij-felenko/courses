#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    PULSE_RECTANGULAR,
    PULSE_HALF_SINE,
    PULSE_TRIANGULAR,
    PULSE_EXPONENTIAL_RC
} PulseShape;

typedef enum {
    SPEED_VERY_FAST_FF,
    SPEED_FAST_F,
    SPEED_SLOW_BLOW_T
} FuseSpeed;

typedef enum {
    CIRCUIT_AC,
    CIRCUIT_DC
} CircuitType;

typedef struct {
    double current_rms;       /* Робочий струм навантаження, А */
    double voltage;           /* Робоча напруга кола, В */
    CircuitType circuit_type; /* Тип кола: AC або DC */
    double temp_ambient;      /* Температура середовища, °C */
    double fault_current_max; /* Максимальний струм к.з. джерела, А */
    
    /* Параметри пускового струму */
    PulseShape pulse_shape;
    double pulse_peak_current;/* Піковий струм імпульсу, А */
    double pulse_duration;    /* Тривалість імпульсу (або RC тау), с */
    int expected_cycles;      /* Очікувана кількість циклів ввімкнення */

    /* Граничний інтеграл захищуваного напівпровідника (0 якщо немає) */
    double semiconductor_i2t_limit;
} CircuitRequirements;

typedef struct {
    const char* part_number;
    double current_rating;     /* Номінальний струм, А */
    double voltage_rating_ac;  /* Номінальна напруга AC, В */
    double voltage_rating_dc;  /* Номінальна напруга DC, В */
    double breaking_capacity;  /* Відключна здатність, А */
    double i2t_melting;        /* Інтеграл плавлення, А²·с */
    double i2t_clearing;       /* Повний інтеграл відключення, А²·с */
    FuseSpeed speed_class;
} FuseModel;

typedef struct {
    bool is_valid;
    const FuseModel* selected_fuse;
    double calculated_inrush_i2t;
    double min_required_i2t_melting;
    double temp_derating_factor;
    const char* rejection_reason;
} SizingResult;

/* Розрахунок температурного дератингу для стандартного запобіжника */
static double calculate_temp_derating(double temp_celsius) {
    if (temp_celsius <= 25.0) {
        return 1.0;
    }
    /* Лінійне зниження струму ~0.35% на градус вище 25°C */
    double derating = 1.0 - (temp_celsius - 25.0) * 0.0035;
    return (derating > 0.4) ? derating : 0.4;
}

/* Визначення допустимої частки імпульсу залежно від кількості циклів */
static double calculate_pulse_factor(int cycles) {
    if (cycles <= 1) return 1.00;
    if (cycles <= 10) return 0.70;
    if (cycles <= 100) return 0.50;
    if (cycles <= 1000) return 0.40;
    if (cycles <= 10000) return 0.29;
    return 0.20; /* 100 000+ циклів */
}

/* Обчислення I²t пускового імпульсу за його формою */
static double calculate_inrush_i2t(PulseShape shape, double i_peak, double duration) {
    switch (shape) {
        case PULSE_RECTANGULAR:
            return i_peak * i_peak * duration;
        case PULSE_HALF_SINE:
            return 0.5 * i_peak * i_peak * duration;
        case PULSE_TRIANGULAR:
            return (1.0 / 3.0) * i_peak * i_peak * duration;
        case PULSE_EXPONENTIAL_RC:
            /* duration інтерпретується як стала часу tau = R*C */
            return 0.5 * i_peak * i_peak * duration;
        default:
            return i_peak * i_peak * duration;
    }
}

/* Головна функція підбору оптимального запобіжника */
SizingResult select_fuse(const CircuitRequirements* req, const FuseModel* catalog, size_t catalog_size) {
    SizingResult res;
    res.is_valid = false;
    res.selected_fuse = NULL;
    res.rejection_reason = "Не знайдено відповідного компонента в каталозі";

    res.temp_derating_factor = calculate_temp_derating(req->temp_ambient);
    res.calculated_inrush_i2t = calculate_inrush_i2t(req->pulse_shape, req->pulse_peak_current, req->pulse_duration);
    
    double pulse_factor = calculate_pulse_factor(req->expected_cycles);
    res.min_required_i2t_melting = res.calculated_inrush_i2t / pulse_factor;

    /* Коефіцієнт тривалого навантаження UL (0.75) */
    double min_current_rating = req->current_rms / (res.temp_derating_factor * 0.75);

    for (size_t i = 0; i < catalog_size; ++i) {
        const FuseModel* f = &catalog[i];

        /* 1. Перевірка тривалого номінального струму */
        if (f->current_rating < min_current_rating) {
            continue;
        }

        /* 2. Перевірка номінальної напруги */
        if (req->circuit_type == CIRCUIT_AC) {
            if (f->voltage_rating_ac < req->voltage) continue;
        } else {
            if (f->voltage_rating_dc < req->voltage) continue;
        }

        /* 3. Перевірка граничної відключної здатності */
        if (f->breaking_capacity < req->fault_current_max) {
            continue;
        }

        /* 4. Перевірка стійкості до пускового імпульсу */
        if (f->i2t_melting < res.min_required_i2t_melting) {
            continue;
        }

        /* 5. Перевірка координації з напівпровідником (якщо задано ліміт) */
        if (req->semiconductor_i2t_limit > 0.0) {
            double safe_semi_limit = 0.75 * req->semiconductor_i2t_limit;
            if (f->i2t_clearing > safe_semi_limit) {
                continue;
            }
        }

        /* Знайдено перший найменший підходящий номінал */
        res.is_valid = true;
        res.selected_fuse = f;
        res.rejection_reason = "Успішний підбір компонента";
        return res;
    }

    return res;
}

int main(void) {
    /* Тестовий каталог запобіжників */
    const FuseModel catalog[] = {
        {"FUSE-F-1A",   1.0, 250.0, 63.0,  50.0,    0.45,   1.2,   SPEED_FAST_F},
        {"FUSE-T-1.25A",1.25,250.0, 63.0,  50.0,    2.80,   7.5,   SPEED_SLOW_BLOW_T},
        {"FUSE-T-2A",   2.0, 250.0, 63.0,  1500.0,  9.50,   24.0,  SPEED_SLOW_BLOW_T},
        {"FUSE-FF-2A",  2.0, 250.0, 125.0, 10000.0, 0.85,   2.1,   SPEED_VERY_FAST_FF},
        {"FUSE-T-3.15A",3.15,250.0, 63.0,  1500.0,  22.0,   60.0,  SPEED_SLOW_BLOW_T}
    };
    size_t catalog_size = sizeof(catalog) / sizeof(catalog[0]);

    /* Вимоги до захисту імпульсного блоку живлення:
       Робочий струм 0.8 А, живлення 230 В AC, температура 45°C,
       пусковий струм заряду конденсатора 30 А (експонента, тау = 1.2 мс),
       ресурс 100 000 вмикань, очікуваний струм к.з. мережі 1000 А. */
    CircuitRequirements req = {
        .current_rms = 0.8,
        .voltage = 230.0,
        .circuit_type = CIRCUIT_AC,
        .temp_ambient = 45.0,
        .fault_current_max = 1000.0,
        .pulse_shape = PULSE_EXPONENTIAL_RC,
        .pulse_peak_current = 30.0,
        .pulse_duration = 0.0012,
        .expected_cycles = 100000,
        .semiconductor_i2t_limit = 0.0
    };

    SizingResult res = select_fuse(&req, catalog, catalog_size);

    if (res.is_valid) {
        printf("Обрано компонент: %s (Номінал: %.2f А)\n",
               res.selected_fuse->part_number, res.selected_fuse->current_rating);
        printf("Пусковий I²t: %.4f А²·с | Необхідний I²t плавлення: %.4f А²·с\n",
               res.calculated_inrush_i2t, res.min_required_i2t_melting);
        printf("Температурний коефіцієнт дератингу: %.3f\n", res.temp_derating_factor);
    } else {
        printf("Помилка підбору: %s\n", res.rejection_reason);
    }

    return 0;
}
