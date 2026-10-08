#include <stdbool.h>
#include <stdint.h>

typedef struct {
    bool gate_q1_p;
    bool gate_q2_n;
    bool gate_q3_p;
    bool gate_q4_n;
} hbridge_gates_t;

void hbridge_set_state(servo_dir_t dir, hbridge_gates_t *gates) {
    // Спочатку безпечно закриваємо всі ключі (Dead-time)
    gates->gate_q1_p = false;
    gates->gate_q2_n = false;
    gates->gate_q3_p = false;
    gates->gate_q4_n = false;

    if (dir == SERVO_DIR_CW) {
        gates->gate_q1_p = true; // Відкриваємо Q1 (P-channel)
        gates->gate_q4_n = true; // Відкриваємо Q4 (N-channel)
    } else if (dir == SERVO_DIR_CCW) {
        gates->gate_q3_p = true; // Відкриваємо Q3 (P-channel)
        gates->gate_q2_n = true; // Відкриваємо Q2 (N-channel)
    }
}
