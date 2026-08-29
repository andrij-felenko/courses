/* ==========================================================================
 *  mag_cal_solver.h — 9-параметричний розв'язувач Левенберга — Марквардта
 *  для моделі B_cal = W · (B_raw − V0) з фіксованим модулем поля Землі.
 * ========================================================================== */
#ifndef MAG_CAL_SOLVER_H
#define MAG_CAL_SOLVER_H

#include "mag_cal_collector.h"
#include "mag_cal_types.h"

typedef enum {
    MAG_CAL_SOLVE_OK = 0,
    MAG_CAL_SOLVE_LOW_COVERAGE,   /* заповнено менше 60 % секторів */
    MAG_CAL_SOLVE_FEW_POINTS,     /* точок менше за MAG_CAL_MIN_POINTS */
    MAG_CAL_SOLVE_SINGULAR,       /* нормальні рівняння вироджені навіть із λ */
    MAG_CAL_SOLVE_DIVERGED,       /* NaN або втеча параметрів */
    MAG_CAL_SOLVE_NO_CONVERGE,    /* вичерпано ліміт ітерацій без збіжності */
    MAG_CAL_SOLVE_POOR_FITNESS,   /* RMS > 3.0 мкТл */
    MAG_CAL_SOLVE_ILL_CONDITIONED /* cond(W) >= 2.5 */
} mag_cal_solve_status_t;

const char *mag_cal_solve_status_str(mag_cal_solve_status_t st);

/* Повна підгонка. out заповнюється завжди, коли повернено щось окрім
 * LOW_COVERAGE/FEW_POINTS: погані коефіцієнти теж треба показати оператору. */
mag_cal_solve_status_t mag_cal_run_solver(const mag_cal_collector_t *col,
                                          mag_cal_result_t *out);

/* Застосування моделі в реальному часі; некалібрований результат
 * повертає вимір як є, щоб контур керування не отримав нулів. */
vec3_t mag_cal_apply(vec3_t raw, const mag_cal_result_t *cal);

#endif /* MAG_CAL_SOLVER_H */
