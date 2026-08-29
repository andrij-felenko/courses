#ifndef PIO_H
#define PIO_H

#include <stdbool.h>

/* Монітор розкачки: прибирає повільний тренд, міряє огинаючу амплітуду
   коливальної складової та їхню частоту за переходами через нуль.
   Смуга людського контуру — 0.5–2.5 Гц; вище лежать вібрації рами й
   помилки бортового D-терма, нижче — маневри пілота. */
typedef struct {
    float dt;
    float trend;     /* повільна складова */
    float hp;        /* коливальна складова */
    float amp;       /* огинаюча з витоком */
    float freq_hz;
    int   crossings;
    int   sign;      /* знак із гістерезисом — щоб шум не давав нулів */
    float win_t;
    float amp_first; /* амплітуда наприкінці першого вікна */
    float amp_last;
    bool  seeded;
} PioMonitor;

void  pio_init(PioMonitor *m, float dt);
void  pio_update(PioMonitor *m, float x);
float pio_hp(const PioMonitor *m);
float pio_amplitude(const PioMonitor *m);
float pio_frequency(const PioMonitor *m);
float pio_growth(const PioMonitor *m);
/* Ознака PIO: коливання в людській смузі з амплітудою понад поріг. */
bool  pio_active(const PioMonitor *m, float amp_threshold);

/* Взаємна кореляція стіка й гіроскопа на нульовому зсуві: близьке до -1
   означає строгу протифазу, тобто оператор підкачує енергію в коливання. */
typedef struct {
    float sxy, sxx, syy, leak;
} PioCorrelator;

void  pio_corr_init(PioCorrelator *c, float dt, float window_sec);
void  pio_corr_update(PioCorrelator *c, float a, float b);
float pio_correlation(const PioCorrelator *c);

/* Аналітичний бюджет фази: скільки градусів запасу з'їдає чиста затримка. */
float pio_phase_margin(float pm0_deg, float omega_c, float tau);
float pio_tau_critical(float pm0_deg, float omega_c);

#endif /* PIO_H */
