#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <time.h>

/* Конфігураційні параметри контролера автоскейлу */
typedef struct {
    int min_replicas;             /* Жорсткий мінімум реплік */
    int max_replicas;             /* Жорсткий максимум (захист бази даних) */
    double target_metric;         /* Цільове значення (наприклад, 70% CPU або 50 RPS) */
    double tolerance;             /* Зона нечутливості (наприклад, 0.10 = ±10%) */
    double ema_alpha;             /* Коефіцієнт експоненційного згладжування [0..1] */
    int scale_up_cooldown_sec;    /* Пауза між послідовними збільшеннями пулу */
    int scale_down_window_sec;    /* Вікно стабілізації перед зменшенням пулу */
    int max_scale_down_step;      /* Максимальна кількість реплік, що знімаються за 1 крок */
} AutoscalerConfig;

/* Поточний стан контролера */
typedef struct {
    int current_replicas;         /* Фактична кількість працюючих екземплярів */
    double smoothed_metric;       /* Поточне значення EMA */
    bool ema_initialized;         /* Прапорець першого запуску */
    time_t last_scale_up_time;    /* Час останнього масштабування вгору */
    time_t scale_down_candidate_time; /* Час, коли навантаження вперше впало нижче норми */
} AutoscalerState;

/* Результат кроку оцінки */
typedef struct {
    int new_replicas;             /* Нова рекомендована кількість реплік */
    bool action_taken;            /* Чи була виконана зміна розміру пулу */
    const char* reason;           /* Пояснення прийнятого рішення */
} AutoscalerDecision;

/* Ініціалізація стану за замовчуванням */
void autoscaler_init(AutoscalerState* state, int initial_replicas) {
    state->current_replicas = initial_replicas;
    state->smoothed_metric = 0.0;
    state->ema_initialized = false;
    state->last_scale_up_time = 0;
    state->scale_down_candidate_time = 0;
}

/* Обчислення одного кроку циклу автоскейлу */
AutoscalerDecision autoscaler_evaluate(const AutoscalerConfig* cfg,
                                      AutoscalerState* state,
                                      double raw_metric,
                                      time_t now) {
    AutoscalerDecision decision;
    decision.new_replicas = state->current_replicas;
    decision.action_taken = false;
    decision.reason = "Стан стабільний (у межах норми)";

    /* 1. Оновлення експоненційного середнього (EMA) */
    if (!state->ema_initialized) {
        state->smoothed_metric = raw_metric;
        state->ema_initialized = true;
    } else {
        state->smoothed_metric = cfg->ema_alpha * raw_metric + (1.0 - cfg->ema_alpha) * state->smoothed_metric;
    }

    /* 2. Перевірка відносного відхилення */
    double ratio = state->smoothed_metric / cfg->target_metric;
    double deviation = fabs(ratio - 1.0);

    /* Перевірка зони нечутливості (Deadband) */
    if (deviation <= cfg->tolerance) {
        state->scale_down_candidate_time = 0; /* Скидаємо таймер згортання */
        decision.reason = "Метрика всередині зони нечутливості (deadband)";
        return decision;
    }

    /* 3. Розрахунок бажаної кількості за формулою ceil(N * ratio) */
    int desired = (int)ceil((double)state->current_replicas * ratio);

    /* Застосування жорстких меж Guardrails */
    if (desired < cfg->min_replicas) desired = cfg->min_replicas;
    if (desired > cfg->max_replicas) desired = cfg->max_replicas;

    /* 4. Гілка збільшення потужностей (Scale-up) */
    if (desired > state->current_replicas) {
        state->scale_down_candidate_time = 0; /* Скасовуємо плани на скорочення */

        if (now - state->last_scale_up_time < cfg->scale_up_cooldown_sec) {
            decision.reason = "Scale-up заблоковано таймером охолодження (cooldown)";
            return decision;
        }

        decision.new_replicas = desired;
        decision.action_taken = true;
        decision.reason = "Виконано Scale-up (збільшення навантаження)";
        state->current_replicas = desired;
        state->last_scale_up_time = now;
        return decision;
    }

    /* 5. Гілка зменшення потужностей (Scale-down) */
    if (desired < state->current_replicas) {
        if (state->scale_down_candidate_time == 0) {
            /* Перший крок фіксації падіння навантаження */
            state->scale_down_candidate_time = now;
            decision.reason = "Фіксація спаду метрики: запущено вікно стабілізації";
            return decision;
        }

        /* Перевіряємо, чи минуло вікно стабілізації */
        if (now - state->scale_down_candidate_time < cfg->scale_down_window_sec) {
            decision.reason = "Очікування стабілізації перед Scale-down";
            return decision;
        }

        /* Обмеження кроку скорочення (Rate limit на видалення) */
        int allowed_drop = state->current_replicas - desired;
        if (allowed_drop > cfg->max_scale_down_step) {
            desired = state->current_replicas - cfg->max_scale_down_step;
        }

        decision.new_replicas = desired;
        decision.action_taken = true;
        decision.reason = "Виконано безпечний Scale-down після стабілізації";
        state->current_replicas = desired;
        state->scale_down_candidate_time = now; /* Скидаємо для наступного кроку */
        return decision;
    }

    return decision;
}

int main(void) {
    AutoscalerConfig cfg = {
        .min_replicas = 2,
        .max_replicas = 10,
        .target_metric = 70.0,         /* 70% цільове CPU */
        .tolerance = 0.10,            /* ±10% зона спокою [63%..77%] */
        .ema_alpha = 0.40,            /* Коефіцієнт фільтра */
        .scale_up_cooldown_sec = 15,  /* 15 секунд між scale-up */
        .scale_down_window_sec = 60,  /* 60 секунд стабілізації для тесту */
        .max_scale_down_step = 2      /* Не більше 2 екземплярів за раз */
    };

    AutoscalerState state;
    autoscaler_init(&state, 2);

    /* Імітація профілю навантаження: спокій -> стрибок -> спад */
    double load_profile[] = {
        68.0, 72.0, 95.0, 110.0, 85.0, 75.0, 40.0, 35.0, 30.0, 32.0, 30.0, 30.0
    };
    int steps = sizeof(load_profile) / sizeof(load_profile[0]);

    printf("=== Симуляція роботи контролера автоскейлу (C) ===\n");
    printf("%-5s | %-8s | %-8s | %-8s | %-40s\n", "Час", "Сирий CPU", "EMA CPU", "Репліки", "Рішення");
    printf("----------------------------------------------------------------------------------------\n");

    time_t virtual_time = 1000;
    for (int i = 0; i < steps; ++i) {
        double raw = load_profile[i];
        AutoscalerDecision d = autoscaler_evaluate(&cfg, &state, raw, virtual_time);

        printf("%4ds  | %7.1f%% | %7.1f%% | %8d | %s\n",
               (int)(virtual_time - 1000), raw, state.smoothed_metric, state.current_replicas, d.reason);

        virtual_time += 15; /* Крок 15 секунд */
    }

    return 0;
}
