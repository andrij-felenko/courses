#include <cmath>
// ФНЧ Саллена–Кі, рівні резистори R1=R2=R; задаємо f0 і Q.
// З Q = 0.5*sqrt(C1/C2)  ->  C1/C2 = (2Q)^2
// З f0 = 1/(2*pi*R*sqrt(C1*C2)) -> sqrt(C1*C2) = 1/(2*pi*R*f0)

float R  = 11000.0f;          // Ом
float f0 = 1000.0f;           // Гц
float Q  = 0.70710678f;       // Баттерворт

float ratio   = (2.0f * Q) * (2.0f * Q);          // C1/C2 = 2.0
float geomean = 1.0f / (2.0f * (float)M_PI * R * f0); // √(C1·C2) ≈ 1.447e-8

float C2 = geomean / std::sqrt(ratio);   // ≈ 1.02e-8 Ф ≈ 10 нФ
float C1 = ratio  * C2;                  // ≈ 2.05e-8 Ф ≈ 20 нФ
