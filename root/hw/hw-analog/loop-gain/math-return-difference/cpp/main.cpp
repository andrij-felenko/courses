// Усі чотири дари зворотного зв'язку з єдиного T = A·β.
// Вхід: голе A, зворотна частка β і голі параметри каскаду.
// Вихід: замкнене підсилення, вихідний/вхідний опір, фактор лінеаризації.
#include <cstdio>

void feedback_gains(float A, float beta,
                    float Ro_open, float Rd_open, float thd_open)
{
    const float T = A * beta;    // підсилення в контурі
    const float F = 1.0f + T;    // різниця повернення — ЄДИНИЙ важіль

    const float Gclosed = A / F;         // замкнене підсилення → прямує до 1/β
    const float Gideal  = 1.0f / beta;   // ідеал 1/β
    const float Rout    = Ro_open / F;   // вихідний опір ділиться на F
    const float Rin     = Rd_open * F;   // вхідний опір множиться на F
    const float thd     = thd_open / F;  // спотворення діляться на F

    std::printf("T = %.0f,  F = 1+T = %.0f\n", T, F);
    std::printf("підсилення: %.4f  (ідеал 1/β = %.4f, похибка %.4f%%)\n",
                Gclosed, Gideal, 100.0f * (Gideal - Gclosed) / Gideal);
    std::printf("вих. опір:  %.4g Ом  (з %.0f Ом, ÷%.0f)\n", Rout, Ro_open, F);
    std::printf("вх. опір:   %.4g Ом  (з %.0f Ом, ×%.0f)\n", Rin, Rd_open, F);
    std::printf("спотвор.:   %.4g %%  (з %.2f %%, ÷%.0f)\n",
                100.0f * thd, 100.0f * thd_open, F);
}

int main()
{
    // A = 100000, β = 0.1 (ціль ×10); голий каскад: Ro=75 Ом, Rd=1 МОм, THD=2%
    feedback_gains(100000.0f, 0.1f, 75.0f, 1.0e6f, 0.02f);
    return 0;
}
