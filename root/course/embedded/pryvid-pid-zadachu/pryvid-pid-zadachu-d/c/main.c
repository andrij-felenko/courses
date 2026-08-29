#include <stdio.h>
#include <stdlib.h>

#include "motor.h"
#include "sizing.h"

typedef struct {
    MotorSpecs motor;
    Gearbox gear;
} Candidate;

/* Кандидати з полиці. Числа — типові паспортні: струм і опір фази NEMA 17
   ті самі, з якими рахували тепловиділення в тексті. */
static const Candidate CANDIDATES[] = {
    {
        {
            "N20 12В + планетарний 100:1", MOTOR_BDC,
            0.0092,   /* тривалий момент на валу мотора, Н·м */
            10000.0,  /* холостий хід */
            0.0,
            0.8, 1.5, 1.0e-7, 32.0, 12.0, 1.0,
            0.0       /* енкодера немає — положення привід не знає */
        },
        { 100.0, 0.60, 0.80 }
    },
    {
        {
            "37GB520 12В + планетарний 30:1", MOTOR_BDC,
            0.0215, 8000.0, 0.0,
            1.5, 1.0, 8.0e-6, 8.0, 12.0, 1.0,
            0.0
        },
        { 30.0, 0.70, 0.50 }
    },
    {
        {
            "NEMA 17 + TMC2209, 1/16 кроку", MOTOR_STEPPER,
            0.59,     /* момент утримання */
            1000.0,   /* вище цієї частоти кроків момент уже нікчемний */
            300.0,    /* злам кривої: далі індуктивність не встигає */
            1.5, 1.6, 5.4e-6, 6.0, 24.0,
            0.40,     /* драйвер зрізає струм у спокої до 40% */
            1.8 / 16.0
        },
        { 1.0, 1.0, 0.0 }   /* прямий привід: редуктора немає */
    },
    {
        {
            "GM4108 + FOC, енкодер 14 біт", MOTOR_BLDC,
            0.18, 2000.0, 800.0,
            2.5, 6.0, 3.0e-5, 8.0, 24.0, 1.0,
            360.0 / 16384.0
        },
        { 1.0, 1.0, 0.0 }
    },
    {
        {
            /* Паспорт шинного серво дано на ВИХІДНОМУ валу, тож зовнішнього
               редуктора немає, а k_t тут уже враховує внутрішній. */
            "STS3215, шинний сервопривід", MOTOR_SERVO,
            1.00, 50.0, 0.0,
            1.2, 3.0, 2.0e-6, 20.0, 12.0, 1.0,
            360.0 / 4096.0
        },
        { 1.0, 1.0, 0.25 }   /* люфт металевих шестерень */
    }
};

static const MotionTask TASKS[] = {
    {
        "поворотна вісь дозатора",
        0.35,      /* момент навантаження, Н·м */
        5.0e-4,    /* момент інерції, кг·м² */
        30.0,      /* оберти вихідного вала */
        0.10,      /* час розгону, с */
        0.30,      /* у русі 30% часу */
        true,      /* у паузі тримає позицію під навантаженням */
        0.50,      /* допуск позиціонування, градуси */
        25.0, 105.0, 12.0
    },
    {
        "привідне колесо мобільного робота",
        0.80, 2.0e-3, 120.0, 0.30, 0.80,
        false,     /* позицію не тримає: у паузі привід знеструмлений */
        0.0,       /* позиціонування не потрібне */
        40.0, 105.0, 30.0
    }
};

static void print_report(const Candidate *c, const SizingReport *r)
{
    char reasons[256];

    printf("  %s (%s)\n", c->motor.name, motor_family_name(c->motor.family));

    if ((r->fail & SZ_BAD_INPUT) != 0u) {
        printf("    ПАСПОРТ      %s\n\n",
               (r->input_problem != NULL) ? r->input_problem : "невідома вада");
        return;
    }

    printf("    вал мотора   %.0f об/хв · треба %.4f Н·м · є %.4f Н·м (запас %.2f при нормі %.2f)\n",
           r->motor_speed_rpm, r->peak_torque_nm, r->available_torque_nm,
           r->margin, r->required_margin);
    printf("    струм        пік %.2f А · пусковий %.2f А\n",
           r->peak_current_a, r->stall_current_a);
    printf("    тепло        рух %.2f Вт · пауза %.2f Вт · середнє %.2f Вт · редуктор %.2f Вт -> обмотка %.0f °C\n",
           r->copper_move_w, r->copper_hold_w, r->copper_average_w,
           r->gear_loss_w, r->winding_temp_c);
    printf("    живлення     %.1f Вт\n", r->electrical_power_w);
    if (r->output_resolution_deg >= 0.0) {
        printf("    позиція      дискрет із люфтом %.3f°\n", r->output_resolution_deg);
    } else {
        printf("    позиція      давача немає\n");
    }

    if (r->fail == 0u) {
        printf("    ВЕРДИКТ      підходить\n");
    } else {
        sizing_describe(r->fail, reasons, sizeof reasons);
        printf("    ВЕРДИКТ      не підходить: %s\n", reasons);
    }
    if (r->warn != 0u) {
        sizing_describe(r->warn, reasons, sizeof reasons);
        printf("    УВАГА        %s\n", reasons);
    }
    putchar('\n');
}

int main(void)
{
    const size_t candidate_count = sizeof CANDIDATES / sizeof CANDIDATES[0];
    const size_t task_count = sizeof TASKS / sizeof TASKS[0];
    size_t ti, ci;
    int unsolved = 0;

    for (ti = 0; ti < task_count; ++ti) {
        const MotionTask *task = &TASKS[ti];
        long best = -1;
        double best_margin = 0.0;

        printf("=== Задача: %s ===\n", task->label);
        printf("%.2f Н·м · %.0f об/хв за %.2f с · рух %.0f%% часу · допуск %.2f° · середовище %.0f °C\n\n",
               task->load_torque_nm, task->target_speed_rpm, task->accel_time_s,
               task->move_duty * 100.0, task->position_tolerance_deg,
               task->ambient_temp_c);

        for (ci = 0; ci < candidate_count; ++ci) {
            SizingReport report;
            bool fits = sizing_evaluate(&CANDIDATES[ci].motor, &CANDIDATES[ci].gear,
                                        task, &report);
            print_report(&CANDIDATES[ci], &report);
            if (fits && report.margin > best_margin) {
                best_margin = report.margin;
                best = (long)ci;
            }
        }

        if (best >= 0) {
            printf("  ВИБІР: %s — найбільший запас моменту (%.2f)\n\n",
                   CANDIDATES[best].motor.name, best_margin);
        } else {
            printf("  ВИБІР: жоден кандидат не проходить — вимоги треба переглядати\n\n");
            ++unsolved;
        }
    }

    return (unsolved == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}
