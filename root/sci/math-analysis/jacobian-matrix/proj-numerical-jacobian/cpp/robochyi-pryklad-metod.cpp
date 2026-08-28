#include <cstdio>

static const double XR = 1.9318516525781366;   // точний корінь — лише щоб
static const double YR = 0.5176380902050415;   // друкувати справжню похибку

static bool solve2(const Mat& J, const Vec& f0, Vec& d)
{
    const double det = J[0][0] * J[1][1] - J[0][1] * J[1][0];
    const double mag = std::abs(J[0][0] * J[1][1]) + std::abs(J[0][1] * J[1][0]);
    if (std::abs(det) < 1e-12 * mag) return false;   // майже вироджена
    d[0] = (-f0[0] * J[1][1] + J[0][1] * f0[1]) / det;
    d[1] = (-J[0][0] * f0[1] + J[1][0] * f0[0]) / det;
    return true;
}

int main()
{
    const Vec scale{1.0, 1.0};
    Vec x{3.0, 1.0}, d(2);
    for (int k = 0; k < 12; ++k) {
        const Vec f0 = F(x);                       // нев'язка — і вона ж вхід якобіана
        const double res = std::hypot(f0[0], f0[1]);
        std::printf("%2d  x = (%17.14f, %17.14f)   |F| = %.1e   |x-x*| = %.1e\n",
                    k, x[0], x[1], res, std::hypot(x[0] - XR, x[1] - YR));
        if (res < 1e-14) break;
        const Mat J = jacobianForward(F<double>, x, f0, scale);
        if (!solve2(J, f0, d)) { std::puts("якобіан майже вироджений"); break; }
        x[0] += d[0];
        x[1] += d[1];
    }
}
