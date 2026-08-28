#include <stdio.h>
#include <math.h>
#include <complex.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Вектор Джонса для опису поляризації світлової хвилі */
typedef struct {
    double complex Ex;
    double complex Ey;
} JonesVector;

/* Матриця Джонса 2x2 для оптичного елемента */
typedef struct {
    double complex m00, m01;
    double complex m10, m11;
} JonesMatrix;

/* Множення матриці Джонса на вектор поляризації */
JonesVector apply_element(JonesMatrix M, JonesVector v) {
    JonesVector result;
    result.Ex = M.m00 * v.Ex + M.m01 * v.Ey;
    result.Ey = M.m10 * v.Ex + M.m11 * v.Ey;
    return result;
}

/* Обчислення інтенсивності (потужності) світлової хвилі */
double get_intensity(JonesVector v) {
    return cabs(v.Ex) * cabs(v.Ex) + cabs(v.Ey) * cabs(v.Ey);
}

/* Матриця лінійного поляризатора, повернутого на кут alpha (в радіанах) */
JonesMatrix make_polarizer(double alpha_rad) {
    double c = cos(alpha_rad);
    double s = sin(alpha_rad);
    JonesMatrix M;
    M.m00 = c * c;      M.m01 = c * s;
    M.m10 = c * s;      M.m11 = s * s;
    return M;
}

/* Матриця нереципрокного ротатора Фарадея для кута обертання theta (в радіанах).
   Важливо: ротатор Фарадея повертає вектор за годинниковою стрілкою
   відносно напрямку магнітного поля B, незалежно від напрямку хвилі! */
JonesMatrix make_faraday_rotator(double theta_rad, int is_forward) {
    /* При зворотному ході промінь іде проти вектора B, тому знак обертання
       відносно напрямку поширення хвилі протилежний */
    double sign = is_forward ? 1.0 : -1.0;
    double rot = sign * theta_rad;
    double c = cos(rot);
    double s = sin(rot);
    JonesMatrix M;
    M.m00 = c;   M.m01 = -s;
    M.m10 = s;   M.m11 = c;
    return M;
}

int main(void) {
    printf("=== Симуляція нереципрокного оптичного ізолятора Фарадея ===\n\n");

    /* Номінальні параметри */
    double target_rot_deg = 45.0;
    double target_rot_rad = target_rot_deg * M_PI / 180.0;
    
    /* 1. Початкове неполяризоване світло моделюємо як горизонтально поляризоване E0 */
    JonesVector E_in = { 1.0 + 0.0*I, 0.0 + 0.0*I };
    double I_in = get_intensity(E_in);

    /* Елементи ізолятора */
    JonesMatrix P1_input  = make_polarizer(0.0);                    /* Поляризатор 0 град */
    JonesMatrix FR_fwd    = make_faraday_rotator(target_rot_rad, 1); /* Фарадей +45 град */
    JonesMatrix P2_output = make_polarizer(45.0 * M_PI / 180.0);    /* Аналізатор 45 град */

    /* Прямий хід */
    JonesVector E1 = apply_element(P1_input, E_in);
    JonesVector E2 = apply_element(FR_fwd, E1);
    JonesVector E_out_fwd = apply_element(P2_output, E2);
    double I_fwd = get_intensity(E_out_fwd);

    double insertion_loss_db = -10.0 * log10(I_fwd / I_in);
    printf("[Прямий хід] Вхідна потужність: %.3f, Вихідна: %.3f\n", I_in, I_fwd);
    printf("[Прямий хід] Втрати на вставку (Insertion Loss): %.2f дБ\n\n", insertion_loss_db);

    /* Зворотний хід (відбите світло виходить з боку виходу під 45 град) */
    JonesVector E_back_start = { cos(45.0*M_PI/180.0), sin(45.0*M_PI/180.0) };
    double I_back_in = get_intensity(E_back_start);

    JonesMatrix FR_bwd = make_faraday_rotator(target_rot_rad, 0); /* Зворотній прохід крізь ротатор */
    
    JonesVector Eb1 = apply_element(P2_output, E_back_start);
    JonesVector Eb2 = apply_element(FR_bwd, Eb1);
    JonesVector E_out_bwd = apply_element(P1_input, Eb2);
    double I_bwd = get_intensity(E_out_bwd);

    /* Оскільки I_bwd близька до 0, додаємо захист від log(0) */
    double isolation_db = (I_bwd < 1e-12) ? 120.0 : -10.0 * log10(I_bwd / I_back_in);
    printf("[Зворотний хід] Відбита потужність: %.3f, Пропущена назад: %.6e\n", I_back_in, I_bwd);
    printf("[Зворотний хід] Рівень ізоляції (Isolation): %.2f дБ\n\n", isolation_db);

    /* Оцінка чутливості до флуктуацій магнітного поля */
    printf("--- Залежність ізоляції від помилки кута обертання (Δθ) ---\n");
    printf("Помилка (град) | Кут (град) | Пропускання назад | Ізоляція (дБ)\n");
    printf("-----------------------------------------------------------\n");
    
    double error_angles[] = { 0.0, 0.5, 1.0, 2.0, 5.0 };
    for (int i = 0; i < 5; i++) {
        double err = error_angles[i];
        double actual_rot = (45.0 - err) * M_PI / 180.0;
        JonesMatrix FR_err = make_faraday_rotator(actual_rot, 0);
        
        JonesVector Eb_err = apply_element(P1_input, apply_element(FR_err, Eb1));
        double I_err = get_intensity(Eb_err);
        double iso_err = -10.0 * log10(I_err / I_back_in);
        
        printf("%+12.1f | %10.1f | %17.6e | %11.2f\n", -err, 45.0 - err, I_err, iso_err);
    }

    return 0;
}
