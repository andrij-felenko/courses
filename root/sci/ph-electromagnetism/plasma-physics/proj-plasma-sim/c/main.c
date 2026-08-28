#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Структура для представлення трьохвимірного вектора */
typedef struct {
    double x;
    double y;
    double z;
} Vector3D;

/* Структура для представлення зарядженої частинки у плазмі */
typedef struct {
    Vector3D pos;  /* Позиція частинки (м) */
    Vector3D vel;  /* Швидкість частинки (м/с) */
    double q;      /* Заряд частинки (Кл) */
    double m;      /* Маса частинки (кг) */
} Particle;

/* Допоміжні функції векторної алгебри */
static inline Vector3D vec_add(Vector3D a, Vector3D b) {
    return (Vector3D){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline Vector3D vec_sub(Vector3D a, Vector3D b) {
    return (Vector3D){a.x - b.x, a.y - b.y, a.z - b.z};
}

static inline Vector3D vec_scale(Vector3D a, double s) {
    return (Vector3D){a.x * s, a.y * s, a.z * s};
}

static inline Vector3D vec_cross(Vector3D a, Vector3D b) {
    return (Vector3D){
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

static inline double vec_dot(Vector3D a, Vector3D b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

/* Реалізація одного кроку алгоритму Бориса */
void boris_step(Particle *p, Vector3D E, Vector3D B, double dt) {
    double qm = p->q / p->m;
    
    /* 1. Перша половина електричного прискорення */
    Vector3D v_minus = vec_add(p->vel, vec_scale(E, qm * dt * 0.5));
    
    /* 2. Обертання у магнітному полі */
    Vector3D t = vec_scale(B, qm * dt * 0.5);
    double t_sq = vec_dot(t, t);
    Vector3D v_prime = vec_add(v_minus, vec_cross(v_minus, t));
    Vector3D s = vec_scale(t, 2.0 / (1.0 + t_sq));
    Vector3D v_plus = vec_add(v_minus, vec_cross(v_prime, s));
    
    /* 3. Друга половина електричного прискорення */
    p->vel = vec_add(v_plus, vec_scale(E, qm * dt * 0.5));
    
    /* 4. Оновлення координат частинки */
    p->pos = vec_add(p->pos, vec_scale(p->vel, dt));
}

int main(void) {
    /* Параметри полів: E_y = -100 В/м, B_z = 0.01 Тл */
    Vector3D E = {0.0, -100.0, 0.0};
    Vector3D B = {0.0, 0.0, 0.01};
    
    /* Створення додатного іона (протона) */
    Particle ion = {
        .pos = {0.0, 0.0, 0.0},
        .vel = {0.0, 1000.0, 0.0},
        .q = 1.60217663e-19,
        .m = 1.6726219e-27
    };
    
    double dt = 1.0e-9;  /* Крок за часом 1 наносекунда */
    int steps = 10000;   /* Загальна кількість кроків */
    
    Vector3D initial_pos = ion.pos;
    
    /* Головний цикл чисельного моделювання */
    for (int i = 0; i < steps; ++i) {
        boris_step(&ion, E, B, dt);
    }
    
    double total_time = steps * dt;
    double avg_v_drift_x = (ion.pos.x - initial_pos.x) / total_time;
    double theoretical_v_drift_x = (E.y * B.z - E.z * B.y) / (- B.z * B.z);

    printf("====================================================\n");
    printf("   Чисельне моделювання E x B дрейфу (Мова C)\n");
    printf("====================================================\n");
    printf("Кінцева позиція іона: (x = %.4f м, y = %.4f м)\n", ion.pos.x, ion.pos.y);
    printf("Обчислена середня швидкість дрейфу v_x:  %.2f м/с\n", avg_v_drift_x);
    printf("Теоретична швидкість E x B дрейфу:        %.2f м/с\n", theoretical_v_drift_x);
    printf("Відносна похибка обчислення:              %.4f %%\n",
           fabs(avg_v_drift_x - theoretical_v_drift_x) / theoretical_v_drift_x * 100.0);
    
    return 0;
}
