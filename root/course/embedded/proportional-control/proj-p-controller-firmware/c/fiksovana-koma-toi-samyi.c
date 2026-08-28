// p_controller_fixed.h — той самий регулятор у форматі Q16
#include <stdint.h>
#include <stdbool.h>

#define QBITS 16
#define QONE  (1L << QBITS)          // 1.0 у форматі Q16 = 65536

typedef struct {
    int32_t kp_q;       // Kp у Q16: kp_q = round(Kp * 65536)
    int32_t beta_q;     // beta у Q16 (0..QONE)
    int32_t u_min;      // межі виходу — у ЦІЛИХ одиницях виходу (не Q!)
    int32_t u_max;
    int32_t u_bias;     // поправка — теж у цілих одиницях виходу
    int32_t last_u;
    bool    saturated;
} p_ctrl_q_t;
