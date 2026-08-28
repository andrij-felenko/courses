#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define MAX_VARS 32
#define MAX_ROWS 32
#define INF 1e18
#define EPS 1e-9

typedef enum {
    LIA_SAT,
    LIA_UNSAT,
    LIA_UNKNOWN
} LiaResult;

typedef struct {
    double low;
    double high;
    double val;
    bool is_integer;
} VarState;

typedef struct {
    int var_idx;
    double old_low;
    double old_high;
} TrailEntry;

typedef struct {
    int num_vars;
    int num_rows;
    double matrix[MAX_ROWS][MAX_VARS]; // matrix[row][col]
    int basic_vars[MAX_ROWS];
    int non_basic_vars[MAX_VARS];
    VarState vars[MAX_VARS + MAX_ROWS];
    
    TrailEntry trail[MAX_VARS * 8];
    int trail_size;
    int scope_markers[MAX_VARS * 4];
    int scope_depth;
} LiaSolver;

void lia_init(LiaSolver* s, int num_vars, int num_rows) {
    s->num_vars = num_vars;
    s->num_rows = num_rows;
    s->trail_size = 0;
    s->scope_depth = 0;
    
    for (int i = 0; i < num_vars; i++) {
        s->vars[i].low = -INF;
        s->vars[i].high = INF;
        s->vars[i].val = 0.0;
        s->vars[i].is_integer = true;
        s->non_basic_vars[i] = i;
    }
    for (int r = 0; r < num_rows; r++) {
        int b_var = num_vars + r;
        s->basic_vars[r] = b_var;
        s->vars[b_var].low = 0.0;
        s->vars[b_var].high = 0.0;
        s->vars[b_var].val = 0.0;
        s->vars[b_var].is_integer = false;
        for (int c = 0; c < num_vars; c++) {
            s->matrix[r][c] = 0.0;
        }
    }
}

void lia_push(LiaSolver* s) {
    s->scope_markers[s->scope_depth++] = s->trail_size;
}

void lia_pop(LiaSolver* s) {
    if (s->scope_depth == 0) return;
    int target_trail = s->scope_markers[--s->scope_depth];
    while (s->trail_size > target_trail) {
        TrailEntry e = s->trail[--s->trail_size];
        s->vars[e.var_idx].low = e.old_low;
        s->vars[e.var_idx].high = e.old_high;
    }
}

bool lia_set_bound(LiaSolver* s, int var_idx, double low, double high) {
    if (s->trail_size < MAX_VARS * 8) {
        s->trail[s->trail_size++] = (TrailEntry){
            .var_idx = var_idx,
            .old_low = s->vars[var_idx].low,
            .old_high = s->vars[var_idx].high
        };
    }
    if (low > s->vars[var_idx].low) s->vars[var_idx].low = low;
    if (high < s->vars[var_idx].high) s->vars[var_idx].high = high;
    return s->vars[var_idx].low <= s->vars[var_idx].high + EPS;
}

static void update_row_values(LiaSolver* s, int row) {
    double sum = 0.0;
    for (int c = 0; c < s->num_vars; c++) {
        int nb_var = s->non_basic_vars[c];
        sum += s->matrix[row][c] * s->vars[nb_var].val;
    }
    int b_var = s->basic_vars[row];
    s->vars[b_var].val = sum;
}

static void pivot(LiaSolver* s, int row, int col) {
    double a_ij = s->matrix[row][col];
    int b_var = s->basic_vars[row];
    int nb_var = s->non_basic_vars[col];
    
    // Обмін змінних у списках базису
    s->basic_vars[row] = nb_var;
    s->non_basic_vars[col] = b_var;
    
    // Перерахунок рядка шарніра
    s->matrix[row][col] = 1.0 / a_ij;
    for (int c = 0; c < s->num_vars; c++) {
        if (c != col) {
            s->matrix[row][c] /= -a_ij;
        }
    }
    
    // Перерахунок інших рядків табло
    for (int r = 0; r < s->num_rows; r++) {
        if (r != row) {
            double gamma = s->matrix[r][col];
            s->matrix[r][col] = 0.0;
            for (int c = 0; c < s->num_vars; c++) {
                s->matrix[r][c] += gamma * s->matrix[row][c];
            }
        }
    }
    
    // Оновлення обчислених значень
    for (int r = 0; r < s->num_rows; r++) {
        update_row_values(s, r);
    }
}

LiaResult lia_check_real_relaxation(LiaSolver* s) {
    int max_iter = 1000;
    while (max_iter-- > 0) {
        int viol_row = -1;
        bool is_below = false;
        
        for (int r = 0; r < s->num_rows; r++) {
            int b_var = s->basic_vars[r];
            if (s->vars[b_var].val < s->vars[b_var].low - EPS) {
                viol_row = r;
                is_below = true;
                break;
            }
            if (s->vars[b_var].val > s->vars[b_var].high + EPS) {
                viol_row = r;
                is_below = false;
                break;
            }
        }
        
        if (viol_row == -1) {
            return LIA_SAT; // Всі межі виконано в Q
        }
        
        // Пошук небазисної змінної за правилом Бленда
        int pivot_col = -1;
        for (int c = 0; c < s->num_vars; c++) {
            double coeff = s->matrix[viol_row][c];
            int nb_var = s->non_basic_vars[c];
            if (is_below) {
                if (coeff > EPS && s->vars[nb_var].val < s->vars[nb_var].high - EPS) {
                    pivot_col = c;
                    break;
                }
                if (coeff < -EPS && s->vars[nb_var].val > s->vars[nb_var].low + EPS) {
                    pivot_col = c;
                    break;
                }
            } else {
                if (coeff > EPS && s->vars[nb_var].val > s->vars[nb_var].low + EPS) {
                    pivot_col = c;
                    break;
                }
                if (coeff < -EPS && s->vars[nb_var].val < s->vars[nb_var].high - EPS) {
                    pivot_col = c;
                    break;
                }
            }
        }
        
        if (pivot_col == -1) {
            return LIA_UNSAT; // Сертифікат несумісності знайдено
        }
        
        pivot(s, viol_row, pivot_col);
    }
    return LIA_UNKNOWN;
}

static bool is_integer_value(double v) {
    return fabs(v - round(v)) < EPS;
}

LiaResult lia_solve_integer(LiaSolver* s) {
    LiaResult res = lia_check_real_relaxation(s);
    if (res != LIA_SAT) return res;
    
    // Пошук дробової змінної серед первинних цілих змінних
    int frac_var = -1;
    double frac_val = 0.0;
    for (int i = 0; i < s->num_vars; i++) {
        if (s->vars[i].is_integer && !is_integer_value(s->vars[i].val)) {
            frac_var = i;
            frac_val = s->vars[i].val;
            break;
        }
    }
    
    if (frac_var == -1) {
        return LIA_SAT; // Усі змінні цілі, знайдено розв'язок у Z^n
    }
    
    // Гілка 1: x_i <= floor(val)
    lia_push(s);
    if (lia_set_bound(s, frac_var, s->vars[frac_var].low, floor(frac_val))) {
        if (lia_solve_integer(s) == LIA_SAT) return LIA_SAT;
    }
    lia_pop(s);
    
    // Гілка 2: x_i >= ceil(val)
    lia_push(s);
    if (lia_set_bound(s, frac_var, ceil(frac_val), s->vars[frac_var].high)) {
        if (lia_solve_integer(s) == LIA_SAT) return LIA_SAT;
    }
    lia_pop(s);
    
    return LIA_UNSAT;
}

int main(void) {
    // Приклад: 2*x1 + x2 = 5, 0 <= x1 <= 2, 0 <= x2 <= 2, x1, x2 in Z
    LiaSolver solver;
    lia_init(&solver, 2, 1);
    
    // Рядок 0: 2*x1 + 1*x2 - s0 = 0, де s0 = 5
    solver.matrix[0][0] = 2.0;
    solver.matrix[0][1] = 1.0;
    solver.vars[2].low = 5.0;  // s0 = 5
    solver.vars[2].high = 5.0;
    
    lia_set_bound(&solver, 0, 0.0, 2.0); // 0 <= x1 <= 2
    lia_set_bound(&solver, 1, 0.0, 2.0); // 0 <= x2 <= 2
    
    LiaResult res = lia_solve_integer(&solver);
    if (res == LIA_SAT) {
        printf("LIA SAT: x1 = %.0f, x2 = %.0f\n", solver.vars[0].val, solver.vars[1].val);
    } else {
        printf("LIA UNSAT\n");
    }
    return 0;
}
