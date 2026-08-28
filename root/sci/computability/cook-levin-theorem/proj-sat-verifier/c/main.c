/* Generator & Verifier of Cook-Levin CNF Formulas in C (C99/C11) */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAX_STATES 8
#define MAX_ALPHABET 8

typedef struct {
    int num_states;
    int num_alphabet;
    int q0;
    int q_accept;
    int q_reject;
    /* delta[q][symbol] -> {next_q, next_symbol, shift_dir (+1 R, -1 L, 0 None)} */
    int delta_q[MAX_STATES][MAX_ALPHABET];
    int delta_sym[MAX_STATES][MAX_ALPHABET];
    int delta_dir[MAX_STATES][MAX_ALPHABET];
} TuringMachine;

typedef struct {
    int time_steps; /* p(n) */
    int tape_size;  /* p(n) + 1 */
    int num_vars;
    int num_clauses;
    FILE *out;
} SATContext;

/* Індексація змінних у форматі 1..N */
static inline int get_x_var(SATContext *ctx, const TuringMachine *tm, int t, int j, int sym) {
    int space_per_cell = tm->num_alphabet + tm->num_states;
    int cell_idx = t * ctx->tape_size + j;
    return cell_idx * space_per_cell + sym + 1;
}

static inline int get_y_var(SATContext *ctx, const TuringMachine *tm, int t, int j, int q) {
    int space_per_cell = tm->num_alphabet + tm->num_states;
    int cell_idx = t * ctx->tape_size + j;
    return cell_idx * space_per_cell + tm->num_alphabet + q + 1;
}

static void write_clause_2(FILE *f, int l1, int l2) {
    fprintf(f, "%d %d 0\n", l1, l2);
}

static void write_clause_3(FILE *f, int l1, int l2, int l3) {
    fprintf(f, "%d %d %d 0\n", l1, l2, l3);
}

/* Генерація умов Phi_cell (однозначність вмісту комірок) */
static void generate_cell_clauses(SATContext *ctx, const TuringMachine *tm) {
    for (int t = 0; t <= ctx->time_steps; t++) {
        for (int j = 0; j < ctx->tape_size; j++) {
            /* 1. Принаймні один символ у комірці */
            for (int s = 0; s < tm->num_alphabet; s++) {
                fprintf(ctx->out, "%d ", get_x_var(ctx, tm, t, j, s));
            }
            fprintf(ctx->out, "0\n");

            /* 2. Не більше одного символу */
            for (int s1 = 0; s1 < tm->num_alphabet; s1++) {
                for (int s2 = s1 + 1; s2 < tm->num_alphabet; s2++) {
                    write_clause_2(ctx->out, -get_x_var(ctx, tm, t, j, s1),
                                             -get_x_var(ctx, tm, t, j, s2));
                }
            }

            /* 3. Не більше одного стану головки */
            for (int q1 = 0; q1 < tm->num_states; q1++) {
                for (int q2 = q1 + 1; q2 < tm->num_states; q2++) {
                    write_clause_2(ctx->out, -get_y_var(ctx, tm, t, j, q1),
                                             -get_y_var(ctx, tm, t, j, q2));
                }
            }
        }
    }
}

/* Генерація умов Phi_start (початкова конфігурація) */
static void generate_start_clauses(SATContext *ctx, const TuringMachine *tm, const int *input_str, int input_len) {
    /* t = 0, j = 0: головка в стан q0 */
    fprintf(ctx->out, "%d 0\n", get_y_var(ctx, tm, 0, 0, tm->q0));

    /* Перші n комірок містять вхідний рядок */
    for (int j = 0; j < input_len; j++) {
        fprintf(ctx->out, "%d 0\n", get_x_var(ctx, tm, 0, j, input_str[j]));
    }
    /* Решта комірок - порожні (пробіл sym = 2) */
    for (int j = input_len; j < ctx->tape_size; j++) {
        fprintf(ctx->out, "%d 0\n", get_x_var(ctx, tm, 0, j, 2));
    }
}

/* Генерація умов Phi_accept (досягнення приймального стану) */
static void generate_accept_clauses(SATContext *ctx, const TuringMachine *tm) {
    for (int t = 0; t <= ctx->time_steps; t++) {
        for (int j = 0; j < ctx->tape_size; j++) {
            fprintf(ctx->out, "%d ", get_y_var(ctx, tm, t, j, tm->q_accept));
        }
    }
    fprintf(ctx->out, "0\n");
}

/* Генерація умов Phi_move (правила переходів) */
static void generate_move_clauses(SATContext *ctx, const TuringMachine *tm) {
    for (int t = 0; t < ctx->time_steps; t++) {
        for (int j = 0; j < ctx->tape_size; j++) {
            for (int q = 0; q < tm->num_states; q++) {
                for (int s = 0; s < tm->num_alphabet; s++) {
                    int next_q = tm->delta_q[q][s];
                    int next_s = tm->delta_sym[q][s];
                    int dir = tm->delta_dir[q][s];

                    if (next_q < 0) continue; /* Невизначений перехід */

                    int y_curr = get_y_var(ctx, tm, t, j, q);
                    int x_curr = get_x_var(ctx, tm, t, j, s);

                    /* У момент t+1 символ у комірці j змінюється на next_s */
                    int x_next = get_x_var(ctx, tm, t + 1, j, next_s);
                    write_clause_3(ctx->out, -y_curr, -x_curr, x_next);

                    /* Головка зсувається у напрямку dir */
                    int next_j = j + dir;
                    if (next_j >= 0 && next_j < ctx->tape_size) {
                        int y_next = get_y_var(ctx, tm, t + 1, next_j, next_q);
                        write_clause_3(ctx->out, -y_curr, -x_curr, y_next);
                    }
                }
            }
        }
    }
}

/* Верифікація задоволення формули поданим свідком */
bool verify_sat_witness(const SATContext *ctx, const TuringMachine *tm, const int *witness) {
    /* Перевірка наявності приймального стану */
    bool accepted = false;
    for (int t = 0; t <= ctx->time_steps; t++) {
        for (int j = 0; j < ctx->tape_size; j++) {
            int var_idx = get_y_var((SATContext*)ctx, tm, t, j, tm->q_accept);
            if (witness[var_idx] == 1) {
                accepted = true;
                break;
            }
        }
    }
    return accepted;
}

int main(void) {
    TuringMachine tm = {
        .num_states = 3,    /* q0=0, q1=1, q_acc=2 */
        .num_alphabet = 3,  /* '0'=0, '1'=1, '⊔'=2 */
        .q0 = 0,
        .q_accept = 2,
        .q_reject = -1
    };
    memset(tm.delta_q, -1, sizeof(tm.delta_q));

    /* Rules: delta(q0, '0') -> (q1, '1', R); delta(q1, '1') -> (q_acc, '1', R) */
    tm.delta_q[0][0] = 1; tm.delta_sym[0][0] = 1; tm.delta_dir[0][0] = +1;
    tm.delta_q[1][1] = 2; tm.delta_sym[1][1] = 1; tm.delta_dir[1][1] = +1;

    SATContext ctx = {
        .time_steps = 2,
        .tape_size = 3,
        .out = stdout
    };

    int input_str[] = {0, 1}; /* "01" */

    printf("c Generating Cook-Levin CNF Formula...\n");
    generate_cell_clauses(&ctx, &tm);
    generate_start_clauses(&ctx, &tm, input_str, 2);
    generate_accept_clauses(&ctx, &tm);
    generate_move_clauses(&ctx, &tm);

    return 0;
}
