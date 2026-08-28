#include <stdio.h>
#include <stdbool.h>
#include <math.h>

// Фізичні параметри ТЕГ модуля
typedef struct {
    int pairs_count;           // Кількість пар термопар (N)
    double seebeck_pair;       // Коефіцієнт Зеєбека пари (В/К)
    double r_internal;         // Внутрішній електричний опір (Ом)
    double theta_teg;          // Тепловий опір модуля (К/Вт)
    double theta_hot;          // Тепловий опір гарячого контакту (К/Вт)
    double theta_sink;         // Тепловий опір радіатора (К/Вт)
} TegModule;

// Параметри енергетичного накопичувача та навантаження
typedef struct {
    double capacitance;        // Ємність іоністора (Ф)
    double v_cap;              // Поточна напруга на іоністорі (В)
    double v_high;             // Верхній поріг увімкнення передачі (В)
    double v_low;              // Нижній поріг блокування UVLO (В)
    double i_leakage;          // Струм саморозряду іоністора (А)
    double i_sleep;            // Струм сну вузла (А)
    double i_active;           // Струм радіопередачі (А)
    double t_active;           // Тривалість передачі (с)
    double eta_boost;          // ККД DC-DC перетворювача (0..1)
    double v_cold_start;       // Поріг холодного старту перетворювача (В)
} HarvesterNode;

// Результат одного кроку симуляції
typedef struct {
    double time_s;
    double t_src;
    double v_teg_oc;
    double p_harvested_mw;
    double v_cap;
    bool tx_fired;
} SimStepResult;

void teg_init_default(TegModule *teg) {
    teg->pairs_count = 127;
    teg->seebeck_pair = 400e-6; // 400 мкВ/К
    teg->r_internal = 2.4;      // 2.4 Ом
    teg->theta_teg = 1.8;       // 1.8 К/Вт
    teg->theta_hot = 0.3;       // 0.3 К/Вт
    teg->theta_sink = 2.5;      // 2.5 К/Вт (радіатор)
}

void harvester_init_default(HarvesterNode *h) {
    h->capacitance = 0.47;      // 0.47 Ф (іоністор)
    h->v_cap = 2.0;             // Початкова напруга 2.0 В
    h->v_high = 3.3;            // Поріг активації передавача 3.3 В
    h->v_low = 2.2;             // Поріг UVLO 2.2 В
    h->i_leakage = 2.0e-6;      // 2 мкА витік
    h->i_sleep = 1.8e-6;        // 1.8 мкА сон
    h->i_active = 22.0e-3;      // 22 мА передача (LoRa / BLE)
    h->t_active = 0.025;        // 25 мс
    h->eta_boost = 0.78;        // 78% ККД
    h->v_cold_start = 0.040;    // 40 мВ мінімум для старту
}

SimStepResult harvester_step(const TegModule *teg, HarvesterNode *h, 
                             double t_src, double t_amb, double dt, double current_time) {
    SimStepResult res;
    res.time_s = current_time;
    res.t_src = t_src;
    res.tx_fired = false;

    // 1. Розрахунок теплового подільника
    double theta_tot = teg->theta_hot + teg->theta_teg + teg->theta_sink;
    double dt_sys = t_src - t_amb;
    double dt_teg = (dt_sys > 0.0) ? (dt_sys * (teg->theta_teg / theta_tot)) : 0.0;

    // 2. ЕРС ТЕГ
    double s_mod = teg->pairs_count * teg->seebeck_pair;
    double voc = s_mod * dt_teg;
    res.v_teg_oc = voc;

    // 3. Збирання потужності з точки MPPT
    double p_in = 0.0;
    if (voc >= h->v_cold_start) {
        p_in = (voc * voc) / (4.0 * teg->r_internal);
    }
    double p_boost = p_in * h->eta_boost;
    res.p_harvested_mw = p_boost * 1000.0;

    // 4. Поточна енергія накопичувача
    double e_cap = 0.5 * h->capacitance * h->v_cap * h->v_cap;

    // Надходження енергії за крок
    e_cap += p_boost * dt;

    // Втрати на сон і саморозряд
    double p_quiescent = h->v_cap * (h->i_sleep + h->i_leakage);
    e_cap -= p_quiescent * dt;

    // 5. Перевірка готовності до передачі
    if (h->v_cap >= h->v_high) {
        double e_tx = h->v_cap * h->i_active * h->t_active;
        if (e_cap >= e_tx) {
            e_cap -= e_tx;
            res.tx_fired = true;
        }
    }

    // Оновлення напруги іоністора
    if (e_cap < 0.0) e_cap = 0.0;
    h->v_cap = sqrt((2.0 * e_cap) / h->capacitance);
    res.v_cap = h->v_cap;

    return res;
}
