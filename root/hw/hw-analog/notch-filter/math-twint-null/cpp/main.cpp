#include <complex>

using cplx = std::complex<float>;

// Модуль |H| симетричного twin-T на частоті f при настройці f0.
// Прямо з виведеної H(s) = ((sRC)²+1) / ((sRC)²+4 sRC +1), де sRC = j·(f/f0).
float twint_mag(float f_hz, float f0_hz)
{
    float x = f_hz / f0_hz;            // нормована частота f/f0
    cplx jx{0.0f, x};                 // sRC = j·x
    cplx s2 = jx * jx;                // (sRC)² = −x²
    cplx num = s2 + 1.0f;
    cplx den = s2 + 4.0f * jx + 1.0f;
    return std::abs(num / den);
}
// twint_mag(50, 50)   -> 0.000   (дно: нуль точно на f0)
// twint_mag(40, 50)   -> 0.112   (−19.0 дБ: сусід 40 Гц просідає у ~9 разів)
// twint_mag(60, 50)   -> 0.091   (−20.8 дБ: 60 Гц просідає навіть глибше за 40)
// twint_mag(62.5, 50) -> 0.112   (рівно як на 40 Гц: симетрія логарифмічна, x ↔ 1/x)
// twint_mag(25, 50)   -> 0.351   (−9.1 дБ: за октаву нижче яма ще добре чутна)
