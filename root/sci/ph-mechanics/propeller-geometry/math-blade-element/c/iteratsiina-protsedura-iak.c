#include <math.h>

// Одна смужка лопаті на радіусі r: ітеративно узгодити елемент лопаті
// з теорією імпульсу й повернути внески в тягу (dT) і момент (dQ).
// V0 — швидкість польоту (м/с); omega — кутова швидкість (рад/с);
// r, dr, c — радіус, товщина смужки, хорда (м); beta — кут установки (рад);
// B — число лопатей; rho — густина повітря.
typedef struct { float dT, dQ; } Element;

// Коефіцієнти профілю як функції кута атаки (спрощена лінійна модель до зриву).
static float cl_of_alpha(float a_rad) {
    float cl = 2.0f * 3.14159265f * a_rad;   // тонке крило: C_L ≈ 2π·α
    if (cl >  1.4f) cl =  1.4f;               // груба межа зриву
    if (cl < -1.4f) cl = -1.4f;
    return cl;
}
static float cd_of_alpha(float a_rad) {
    return 0.02f + 0.05f * a_rad * a_rad;     // паразитний + індукований опір
}

Element blade_element(float V0, float omega, float r, float dr, float c,
                      float beta, int B, float rho) {
    float a = 0.0f, ap = 0.0f;                // початкові індукції
    float phi = 0.0f, W = 0.0f, Cn = 0.0f, Ct = 0.0f;
    float sigma = B * c / (2.0f * 3.14159265f * r);   // місцева щільність лопаті

    for (int it = 0; it < 100; ++it) {
        // 2) кут потоку з поточних індукцій
        float V_ax  = V0 * (1.0f + a);
        float V_tan = omega * r * (1.0f - ap);
        phi = atan2f(V_ax, V_tan);
        W   = sqrtf(V_ax * V_ax + V_tan * V_tan);

        // 3) кут атаки й коефіцієнти профілю
        float alpha = beta - phi;
        float Cl = cl_of_alpha(alpha);
        float Cd = cd_of_alpha(alpha);

        // 4) проєкції на вісь (нормальна) і на площину (тангенційна)
        Cn = Cl * cosf(phi) - Cd * sinf(phi);
        Ct = Cl * sinf(phi) + Cd * cosf(phi);

        // 5) нові індукції з рівнянь зшивання; f = a/(1+a) → a = f/(1−f)
        float s = sinf(phi);
        float f_ax  = sigma * Cn / (4.0f * s * s);
        float f_tan = sigma * Ct / (4.0f * s * cosf(phi));
        float a_new  = f_ax  / (1.0f - f_ax);
        float ap_new = f_tan / (1.0f + f_tan);

        // 6) перевірка збіжності
        if (fabsf(a_new - a) < 1e-5f && fabsf(ap_new - ap) < 1e-5f) {
            a = a_new; ap = ap_new; break;
        }
        a = a_new; ap = ap_new;
    }

    // сили смужки з усталеного трикутника швидкостей
    float q = 0.5f * rho * W * W;             // динамічний напір ½ρW²
    float dL = q * c * cl_of_alpha(beta - phi) * dr;
    float dD = q * c * cd_of_alpha(beta - phi) * dr;

    Element e;
    e.dT = B * (dL * cosf(phi) - dD * sinf(phi));        // тяга смужки (усі лопаті)
    e.dQ = B * (dL * sinf(phi) + dD * cosf(phi)) * r;    // момент смужки
    return e;
}
